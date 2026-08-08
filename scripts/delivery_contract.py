#!/usr/bin/env python3
"""Structured customer delivery and declared current-truth projections.

The parser accepts only the explicit ``### Delivery Contract`` block. Project
prose remains opaque. Current-truth synchronization likewise edits only exact
machine markers registered through canonical, non-append-only assets.
"""
from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path


DELIVERY_FIELDS = {
    "task_status",
    "milestone_status",
    "product_status",
    "customer_outcome",
    "capability_delta",
    "remaining_gaps",
    "evidence_boundary",
    "recommended_next",
    "decisions_required",
    "technical_receipt",
}
LIST_FIELDS = {
    "capability_delta",
    "remaining_gaps",
    "evidence_boundary",
    "decisions_required",
}
RECOMMENDED_FIELDS = {"id", "status", "reason"}
RECEIPT_FIELDS = {"commits", "verification", "safe_files"}
TASK_STATUSES = {"finalized", "pending"}
ASSESSMENT_STATUSES = {"completed", "in_progress", "not_assessed"}
NEXT_STATUSES = {"planned", "recommended", "active", "none"}
STANDARD_PROSE_PROJECTIONS = (
    "README.md",
    "README.zh-CN.md",
    "docs/HANDOFF.md",
    "docs/NORTH_STAR.md",
)
CURRENT_TRUTH_MARKER = re.compile(
    r"<!--\s*coderail:current-truth\s+"
    r"task=(T-\d+)\s+"
    r"status=(active|in_progress|pending-closeout|finalized)\s*-->",
    re.I,
)
STALE_CURRENT_STATUS = re.compile(
    r"(?<![A-Za-z0-9_])"
    r"(verified-commit-pending|pending-closeout|in_progress|in[ -]progress|"
    r"active|pending[ -]closeout|closeout[ -]pending|pending[ -]commit|"
    r"commit[ -]pending|waiting[ -]for[ -](?:commit|push|commit/push)|"
    r"awaiting[ -](?:commit|push|commit/push)|pending|"
    r"等待[ ]*(?:commit|push|commit/push|提交|推送|提交/推送)|待提交|待推送|待收口)"
    r"(?![A-Za-z0-9_])",
    re.I,
)
CURRENT_STATUS_FIELD = re.compile(
    r"^[ ]{0,3}(?:[-*][ ]+)?(?:\*\*)?"
    r"(?:(?:(?:task|coordinate|current)[ _-]*)?(?:status|state)|"
    r"(?:closeout|commit)(?:[ _-]*(?:status|state))?|"
    r"(?:任务|坐标|当前|收口|提交)?状态|收口|提交)"
    r"(?:\*\*)?[ ]*[:：](?:\*\*)?[ ]*(.*)$",
    re.I,
)
CURRENT_ID_FIELD = re.compile(
    r"^[ ]{0,3}(?:[-*][ ]+)?(?:\*\*)?"
    r"(?:task|coordinate|任务|坐标)(?:[ _-]*id)?"
    r"(?:\*\*)?[ ]*[:：](?:\*\*)?",
    re.I,
)


def _legacy_contract() -> dict:
    return {
        "task_status": "pending",
        "milestone_status": "not_assessed",
        "product_status": "not_assessed",
        "customer_outcome": "not_assessed",
        "capability_delta": [],
        "remaining_gaps": [],
        "evidence_boundary": [],
        "recommended_next": {
            "id": None,
            "status": "none",
            "reason": "not_assessed",
        },
        "decisions_required": [],
        "technical_receipt": {
            "commits": [],
            "verification": [],
            "safe_files": [],
        },
    }


def _delivery_section(text: str) -> str:
    match = re.search(
        r"^###\s+Delivery Contract\s*$\n(.*?)(?=^###\s|^##\s|\Z)",
        text or "",
        re.I | re.M | re.S,
    )
    if not match:
        return ""
    body = match.group(1).strip()
    fence = re.fullmatch(r"```(?:ya?ml)?\s*\n(.*?)\n```", body, re.I | re.S)
    return fence.group(1).strip() if fence else body


def _scalar(raw: str):
    value = raw.strip()
    if value == "null":
        return None
    if value == "[]":
        return []
    if value.startswith(('"', "'")):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value[1:-1] if len(value) >= 2 and value[-1] == value[0] else value
    return value


def _parse_restricted_yaml(body: str) -> tuple[dict, list[str]]:
    lines = [line.rstrip() for line in body.splitlines() if line.strip()]
    if not lines or lines[0].strip() != "delivery:":
        return {}, ["Delivery Contract must start with delivery:"]
    data: dict = {}
    parent = ""
    nested_parent = ""
    issues: list[str] = []
    for line in lines[1:]:
        root_field = re.fullmatch(r"  ([a-z_]+):(?:\s*(.*))?", line)
        nested_field = re.fullmatch(r"    ([a-z_]+):(?:\s*(.*))?", line)
        root_item = re.fullmatch(r"    -(?:\s+(.*))?", line)
        nested_item = re.fullmatch(r"      -(?:\s+(.*))?", line)
        if root_field:
            key, raw = root_field.groups()
            parent = key
            nested_parent = ""
            if key not in DELIVERY_FIELDS:
                issues.append(f"unknown Delivery Contract field: {key}")
                continue
            if key in LIST_FIELDS:
                data[key] = [] if not raw else _scalar(raw)
            elif key in {"recommended_next", "technical_receipt"}:
                data[key] = {}
                if raw:
                    issues.append(f"{key} must use nested fields")
            else:
                data[key] = _scalar(raw or "")
            continue
        if root_item and parent in LIST_FIELDS:
            item = (root_item.group(1) or "").strip()
            if not item:
                issues.append(f"{parent} entries must be non-empty strings")
            else:
                data.setdefault(parent, []).append(_scalar(item))
            continue
        if nested_field and parent in {"recommended_next", "technical_receipt"}:
            key, raw = nested_field.groups()
            nested_parent = key
            allowed = RECOMMENDED_FIELDS if parent == "recommended_next" else RECEIPT_FIELDS
            if key not in allowed:
                issues.append(f"unknown {parent} field: {key}")
            else:
                value = _scalar(raw or "")
                if parent == "technical_receipt" and not raw:
                    value = []
                data.setdefault(parent, {})[key] = value
            continue
        if nested_item and parent == "technical_receipt" and nested_parent in RECEIPT_FIELDS:
            item = (nested_item.group(1) or "").strip()
            if not item:
                issues.append(f"technical_receipt.{nested_parent} entries must be non-empty strings")
            else:
                data.setdefault(parent, {}).setdefault(nested_parent, []).append(_scalar(item))
            continue
        issues.append(f"unsupported Delivery Contract syntax: {line.strip()}")
    return data, issues


def _validate(contract: dict) -> list[str]:
    issues = []
    missing = DELIVERY_FIELDS - set(contract)
    if missing:
        issues.append("missing Delivery Contract fields: " + ", ".join(sorted(missing)))
    if contract.get("task_status") not in TASK_STATUSES:
        issues.append("task_status must be finalized or pending")
    for field in ("milestone_status", "product_status"):
        if contract.get(field) not in ASSESSMENT_STATUSES:
            issues.append(f"{field} must be completed, in_progress, or not_assessed")
    if not isinstance(contract.get("customer_outcome"), str):
        issues.append("customer_outcome must be a string")
    for field in LIST_FIELDS:
        value = contract.get(field)
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            issues.append(f"{field} must be a string list")
    recommended = contract.get("recommended_next")
    if not isinstance(recommended, dict) or set(recommended) != RECOMMENDED_FIELDS:
        issues.append("recommended_next must contain exactly id, status, and reason")
    else:
        status = recommended.get("status")
        candidate = recommended.get("id")
        if status not in NEXT_STATUSES:
            issues.append("recommended_next.status must be planned, recommended, active, or none")
        if status == "none" and candidate is not None:
            issues.append("recommended_next.id must be null when status is none")
        if status != "none" and (not isinstance(candidate, str) or not candidate.strip()):
            issues.append("recommended_next.id must be a non-empty string unless status is none")
        if not isinstance(recommended.get("reason"), str):
            issues.append("recommended_next.reason must be a string")
    receipt = contract.get("technical_receipt")
    if not isinstance(receipt, dict) or set(receipt) != RECEIPT_FIELDS:
        issues.append("technical_receipt must contain exactly commits, verification, and safe_files")
    elif any(
        not isinstance(receipt.get(field), list)
        or any(not isinstance(item, str) for item in receipt.get(field, []))
        for field in RECEIPT_FIELDS
    ):
        issues.append("technical_receipt fields must be string lists")
    return issues


def parse_delivery_contract(task_body: str) -> tuple[dict, list[str]]:
    """Parse the optional explicit contract; missing means not_assessed."""
    body = _delivery_section(task_body)
    if not body:
        return _legacy_contract(), []
    contract, issues = _parse_restricted_yaml(body)
    issues.extend(_validate(contract))
    return contract, list(dict.fromkeys(issues))


def finalized_delivery(
    contract: dict,
    *,
    commits: list[str],
    verification: list[str],
    safe_files: list[str],
) -> dict:
    """Promote only the task fact; broader completion stays explicit."""
    delivery = deepcopy(contract or _legacy_contract())
    delivery["task_status"] = "finalized"
    delivery["technical_receipt"] = {
        "commits": list(commits),
        "verification": list(verification),
        "safe_files": list(safe_files),
    }
    return delivery


def canonical_current_truth_files(root: Path) -> list[str]:
    """Read exact canonical paths from ASSETS; append-only history is excluded."""
    registry = root / "docs" / "ASSETS.md"
    try:
        text = registry.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    files = []
    for raw in text.splitlines():
        if not raw.lstrip().startswith("|"):
            continue
        cells = [cell.strip().strip("`") for cell in raw.strip().strip("|").split("|")]
        if len(cells) < 4 or cells[0].lower() in {"asset", "---"}:
            continue
        path, asset_type, canonical = cells[:3]
        if canonical.lower() != "yes" or "append-only" in asset_type.lower():
            continue
        candidate = Path(path)
        if candidate.is_absolute() or ".." in candidate.parts:
            continue
        if path == "docs/TRACELOG.jsonl":
            continue
        files.append(candidate.as_posix())
    return list(dict.fromkeys(files))


def _marker_files(root: Path, task_id: str | None = None) -> dict[str, list[tuple[str, str]]]:
    found = {}
    for relative in canonical_current_truth_files(root):
        path = root / relative
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        markers = [
            (match.group(1), match.group(2).lower())
            for match in CURRENT_TRUTH_MARKER.finditer(text)
            if task_id is None or match.group(1) == task_id
        ]
        if markers:
            found[relative] = markers
    return found


def prose_projection_files(root: Path) -> list[str]:
    """Return current prose surfaces; historical task/review archives stay out."""
    candidates = canonical_current_truth_files(root) + [
        relative for relative in STANDARD_PROSE_PROJECTIONS
        if (root / relative).is_file()
    ]
    return list(dict.fromkeys(candidates))


def _finalized_aliases(root: Path, finalized_task_ids: set[str]) -> dict[str, str]:
    """Map exact internal/display ids to the finalized internal Coordinate."""
    aliases = {task_id: task_id for task_id in finalized_task_ids}
    try:
        metadata = json.loads((root / ".coderail" / "tasks.json").read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError, UnicodeError):
        metadata = {}
    for task_id in finalized_task_ids:
        display_id = (metadata.get(task_id) or {}).get("display_id")
        if isinstance(display_id, str) and display_id.strip():
            aliases[display_id.strip()] = task_id
    return aliases


def _aliases_in_line(line: str, aliases: dict[str, str]) -> list[tuple[str, str]]:
    found = []
    for alias, task_id in aliases.items():
        if re.search(
            rf"(?<![A-Za-z0-9_-]){re.escape(alias)}(?![A-Za-z0-9_-])",
            line,
            re.I,
        ):
            found.append((alias, task_id))
    return found


def _exact_stale_status(value: str):
    candidate = value.strip().strip("`*_ ").rstrip(".!。；;").strip()
    return STALE_CURRENT_STATUS.fullmatch(candidate)


def _row_stale_status(
    line: str, inline_aliases: list[tuple[str, str]]
):
    stripped = line.strip()
    if stripped.startswith("|"):
        for cell in stripped.strip("|").split("|"):
            stale = _exact_stale_status(cell)
            if stale:
                return stale
        return None
    if not stripped.startswith(("-", "*")):
        return None
    for alias, _task_id in inline_aliases:
        match = re.search(
            rf"(?<![A-Za-z0-9_-]){re.escape(alias)}(?![A-Za-z0-9_-])",
            line,
            re.I,
        )
        if not match:
            continue
        remainder = line[match.end():].strip()
        remainder = re.sub(r"^(?:[:：|]|—|–|->)[ ]*", "", remainder)
        stale = _exact_stale_status(remainder)
        if stale:
            return stale
    return None


def _prose_projection_gaps(root: Path, finalized_task_ids: set[str]) -> list[str]:
    """Find exact current-status assertions that CodeRail cannot safely rewrite.

    Canonical prose stays project-owned. We therefore inspect only explicit
    status fields, task/coordinate contexts, and table/list rows that carry the
    exact internal or display id. Narrative mentions remain opaque.
    """
    aliases = _finalized_aliases(root, finalized_task_ids)
    if not aliases:
        return []
    gaps = []
    for relative in prose_projection_files(root):
        path = root / relative
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (FileNotFoundError, OSError, UnicodeError):
            continue
        context_stack: list[tuple[int, list[tuple[str, str]] | None]] = [(0, None)]
        for line_number, line in enumerate(lines, 1):
            if CURRENT_TRUTH_MARKER.search(line):
                continue
            inline_aliases = _aliases_in_line(line, aliases)
            heading = re.match(r"^[ ]{0,3}(#{1,6})[ ]+", line)
            if heading:
                level = len(heading.group(1))
                while context_stack and context_stack[-1][0] >= level:
                    context_stack.pop()
                context_stack.append((level, inline_aliases or None))
            elif CURRENT_ID_FIELD.search(line):
                level, _context = context_stack[-1]
                context_stack[-1] = (level, inline_aliases)

            section_context = []
            for _level, context in reversed(context_stack):
                if context is not None:
                    section_context = context
                    break

            status_field = CURRENT_STATUS_FIELD.search(line)
            row_stale = _row_stale_status(line, inline_aliases)
            stale = (
                _exact_stale_status(status_field.group(1))
                if status_field else row_stale
            )
            if not stale:
                continue
            row_assertion = bool(inline_aliases and (row_stale or status_field))
            bound = inline_aliases if row_assertion else (section_context if status_field else [])
            for alias, task_id in bound:
                alias_detail = f" alias={alias}" if alias.lower() != task_id.lower() else ""
                gaps.append(
                    f"CURRENT_TRUTH_PROSE_GAP file={relative} line={line_number} "
                    f"task={task_id}{alias_detail} recorded={stale.group(1)} "
                    "expected=finalized"
                )
    return list(dict.fromkeys(gaps))


def _diagnostic(
    *,
    severity: str,
    category: str,
    blocks: str,
    evidence: str,
    recommended_action: str,
) -> dict[str, str]:
    return {
        "severity": severity,
        "category": category,
        "blocks": blocks,
        "evidence": evidence,
        "recommended_action": recommended_action,
    }


def current_truth_diagnostics(
    root: Path,
    finalized_task_ids: set[str],
    *,
    lifecycle_statuses: dict[str, str] | None = None,
) -> list[dict[str, str]]:
    """Classify lifecycle marker conflicts separately from prose staleness.

    Exact CodeRail markers participate in the live control plane. Bounded prose
    assertions are human-owned projections: useful debt signals, but never a
    lifecycle authority or formulation gate.
    """
    diagnostics = []
    expected_statuses = {
        task_id: "finalized" for task_id in finalized_task_ids
    }
    expected_statuses.update(lifecycle_statuses or {})
    aliases = _finalized_aliases(root, set(expected_statuses))
    for relative, markers in _marker_files(root).items():
        for task_id, status in markers:
            internal_id = aliases.get(task_id)
            expected = expected_statuses.get(internal_id or "")
            equivalent = (
                status in {"active", "in_progress"}
                if expected == "active" else status == expected
            )
            if not expected or equivalent:
                continue
            evidence = (
                f"CURRENT_TRUTH_GAP file={relative} task={task_id} "
                f"recorded={status} expected={expected}"
            )
            diagnostics.append(_diagnostic(
                severity="error",
                category="control_plane_conflict",
                blocks="activation",
                evidence=evidence,
                recommended_action=(
                    "Reconcile the exact machine marker with live lifecycle state "
                    "before activation; do not infer authority from surrounding prose."
                ),
            ))
    for evidence in _prose_projection_gaps(root, finalized_task_ids):
        diagnostics.append(_diagnostic(
            severity="warning",
            category="projection_staleness",
            blocks="none",
            evidence=evidence,
            recommended_action=(
                "Keep formulation available and batch lifecycle-neutral prose cleanup "
                "as maintenance debt; do not create a GOV Coordinate solely for this warning."
            ),
        ))
    unique = []
    seen = set()
    for diagnostic in diagnostics:
        key = tuple(diagnostic.items())
        if key not in seen:
            seen.add(key)
            unique.append(diagnostic)
    return unique


def current_truth_projection_gaps(root: Path, finalized_task_ids: set[str]) -> list[str]:
    """Compatibility view containing only authority conflicts that block."""
    return [
        diagnostic["evidence"]
        for diagnostic in current_truth_diagnostics(root, finalized_task_ids)
        if diagnostic["blocks"] != "none"
    ]


def projection_scope_issues(
    root: Path,
    task_id: str,
    *,
    allowed: list[str],
    forbidden: list[str],
) -> tuple[list[str], list[str]]:
    """Return declared projection paths and exact scope blockers."""
    from repository_state import matches_any

    paths = sorted(_marker_files(root, task_id))
    issues = []
    for path in paths:
        if forbidden and matches_any(path, forbidden):
            issues.append(f"CURRENT_TRUTH_SCOPE file={path} reason=forbidden")
        elif allowed and not matches_any(path, allowed):
            issues.append(f"CURRENT_TRUTH_SCOPE file={path} reason=outside_allowed")
        elif not allowed:
            issues.append(f"CURRENT_TRUTH_SCOPE file={path} reason=no_allowed_scope")
    return paths, issues


def synchronize_current_truth(
    root: Path,
    task_id: str,
    status: str,
    *,
    authorized_paths: set[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Update only exact markers, rolling back all files on a write failure."""
    if status not in {"pending-closeout", "finalized"}:
        return [], [f"unsupported projection status: {status}"]
    marker_files = _marker_files(root, task_id)
    paths = sorted(marker_files)
    if authorized_paths is not None:
        missing = [path for path in paths if path not in authorized_paths]
        if missing:
            return [], [
                f"CURRENT_TRUTH_PROJECTION_PENDING file={path} reason=not_in_verified_safe_files"
                for path in missing
            ]
    originals = {}
    updates = {}
    for relative in paths:
        path = root / relative
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            return [], [f"CURRENT_TRUTH_PROJECTION_PENDING file={relative} reason={type(exc).__name__}"]

        def replace(match: re.Match) -> str:
            if match.group(1) != task_id:
                return match.group(0)
            return f"<!-- coderail:current-truth task={task_id} status={status} -->"

        updated = CURRENT_TRUTH_MARKER.sub(replace, text)
        if updated != text:
            originals[relative] = text
            updates[relative] = updated
    written = []
    try:
        for relative, updated in updates.items():
            (root / relative).write_text(updated, encoding="utf-8")
            written.append(relative)
    except OSError as exc:
        for relative in written:
            try:
                (root / relative).write_text(originals[relative], encoding="utf-8")
            except OSError:
                pass
        return [], [
            f"CURRENT_TRUTH_PROJECTION_PENDING file={relative} reason={type(exc).__name__}"
        ]
    return written, []


def write_technical_report(root: Path, task_id: str, stamp: str, markdown: str) -> str:
    reports = root / ".coderail" / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    safe_id = re.sub(r"[^A-Za-z0-9_-]", "_", task_id or "unknown")
    path = reports / f"delivery-{stamp or 'latest'}-{safe_id}.md"
    path.write_text(markdown.rstrip() + "\n", encoding="utf-8")
    return path.relative_to(root).as_posix()


def write_client_report(root: Path, task_id: str, stamp: str, markdown: str) -> str:
    """Compatibility alias; new code should name this the Technical Report."""
    return write_technical_report(root, task_id, stamp, markdown)
