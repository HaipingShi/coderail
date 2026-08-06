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
CURRENT_TRUTH_MARKER = re.compile(
    r"<!--\s*coderail:current-truth\s+"
    r"task=(T-\d+)\s+"
    r"status=(active|in_progress|pending-closeout|finalized)\s*-->",
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


def _markdown_items(values: list[str], *, empty: str = "none") -> list[str]:
    return [f"- {value}" for value in values] if values else [f"- {empty}"]


def render_client_markdown(delivery: dict) -> str:
    """Render the stable client-facing order; technical facts are last."""
    recommended = delivery.get("recommended_next") or {}
    receipt = delivery.get("technical_receipt") or {}
    lines = [
        "# 客户交付摘要",
        "",
        "## 交付结果",
        "",
        f"- 任务状态：{delivery.get('task_status') or 'pending'}",
        f"- 客户结果：{delivery.get('customer_outcome') or 'not_assessed'}",
        "",
        "## 能力变化",
        "",
        *_markdown_items(delivery.get("capability_delta") or [], empty="not_assessed"),
        "",
        "## 项目整体状态",
        "",
        f"- 里程碑状态：{delivery.get('milestone_status') or 'not_assessed'}",
        f"- 产品状态：{delivery.get('product_status') or 'not_assessed'}",
        "",
        "## 未完成与风险",
        "",
        *_markdown_items(delivery.get("remaining_gaps") or [], empty="none"),
        "- 证据边界：",
        *[f"  - {value}" for value in (delivery.get("evidence_boundary") or ["not_assessed"])],
        "",
        "## 推荐下一任务",
        "",
        f"- ID：{recommended.get('id') or 'none'}",
        f"- 状态：{recommended.get('status') or 'none'}",
        f"- 原因：{recommended.get('reason') or 'not_assessed'}",
        "",
        "## 需要决策",
        "",
        *_markdown_items(delivery.get("decisions_required") or [], empty="none"),
        "",
        "## 技术附录",
        "",
        "- Commits:",
        *[f"  - {value}" for value in (receipt.get("commits") or ["none"])],
        "- Verification:",
        *[f"  - {value}" for value in (receipt.get("verification") or ["none"])],
        "- Safe files:",
        *[f"  - {value}" for value in (receipt.get("safe_files") or ["none"])],
        "",
    ]
    return "\n".join(lines)


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


def current_truth_projection_gaps(root: Path, finalized_task_ids: set[str]) -> list[str]:
    gaps = []
    for relative, markers in _marker_files(root).items():
        for task_id, status in markers:
            if task_id in finalized_task_ids and status != "finalized":
                gaps.append(
                    f"CURRENT_TRUTH_GAP file={relative} task={task_id} "
                    f"recorded={status} expected=finalized"
                )
    return gaps


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


def write_client_report(root: Path, task_id: str, stamp: str, markdown: str) -> str:
    reports = root / ".coderail" / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    safe_id = re.sub(r"[^A-Za-z0-9_-]", "_", task_id or "unknown")
    path = reports / f"delivery-{stamp or 'latest'}-{safe_id}.md"
    path.write_text(markdown.rstrip() + "\n", encoding="utf-8")
    return path.relative_to(root).as_posix()
