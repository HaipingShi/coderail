#!/usr/bin/env python3
"""Evidence-aware trace graph helpers and novice-readable queries."""
from __future__ import annotations

import json
import re
import secrets
import subprocess
from datetime import datetime, timezone
from pathlib import Path


EDGE_KEYS = (
    "serves",
    "derived_from",
    "implements",
    "implemented_by",
    "modifies",
    "validated_by",
    "validates",
    "depends_on",
    "supersedes",
    "blocks",
    "relates_to",
    "follows",
)
FORMAL_EDGE_CLASSES = {"fact", "decision"}
CANDIDATE_STATUSES = {"proposed", "promoted", "rejected"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def make_id(prefix: str = "TR") -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"{prefix}-{stamp}-{secrets.token_hex(2)}"


def trace_path(root: Path) -> Path:
    return root / "docs" / "TRACELOG.jsonl"


def candidate_path(root: Path) -> Path:
    return root / "docs" / "TRACE_CANDIDATES.jsonl"


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            row = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_events(root: Path) -> list[dict]:
    return load_jsonl(trace_path(root))


def git_fact_events(root: Path) -> list[dict]:
    """Synthesize immutable fact edges from CodeRail trailers and Git diffs."""
    result = subprocess.run(
        ["git", "-C", str(root), "log", "--format=%H%x1f%cI%x1f%B%x1e"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode:
        return []
    events: list[dict] = []
    for record in result.stdout.split("\x1e"):
        record = record.strip()
        if not record:
            continue
        parts = record.split("\x1f", 2)
        if len(parts) != 3:
            continue
        commit, committed_at, body = parts
        task_match = re.search(r"^CodeRail-Task:\s*(T-\d+)\s*$", body, re.M | re.I)
        if not task_match:
            continue
        task_id = task_match.group(1).upper()
        verify_match = re.search(r"^CodeRail-Verified-By:\s*(.+?)\s*$", body, re.M | re.I)
        verify_ids = (
            [item.strip() for item in verify_match.group(1).split(",") if item.strip()]
            if verify_match else []
        )
        files_result = subprocess.run(
            ["git", "-C", str(root), "show", "--pretty=", "--name-only", "-z", commit],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        files = sorted(
            {
                value.decode(errors="replace").replace("\\", "/")
                for value in (files_result.stdout or b"").split(b"\0")
                if value
            }
        )
        event = {
            "id": f"GIT-{commit[:12]}",
            "ts": committed_at,
            "type": "change",
            "subject": commit,
            "edge_class": "fact",
            "summary": body.splitlines()[0] if body.splitlines() else commit[:12],
            "task": task_id,
            "status": "done",
            "source_kind": "git",
            "source_ref": commit,
            "commit": commit,
            "files": files,
            "implements": [task_id],
            "modifies": files,
            "basis": [f"git:{commit}"],
            "coordinate": {"task": task_id, "persist": ["TASKS", "TRACE"]},
        }
        if verify_ids:
            event["validated_by"] = verify_ids
        events.append(event)
    return events


def load_graph_events(root: Path) -> list[dict]:
    return load_events(root) + git_fact_events(root)


def append_event(root: Path, event: dict) -> dict:
    append_jsonl(trace_path(root), event)
    return event


def north_star(root: Path) -> tuple[str, str]:
    """Return a durable reference and the plain-language outcome."""
    path = root / "docs" / "NORTH_STAR.md"
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        return "", ""
    match = re.search(r"^ID:\s*(NS-\d+)\s*$", text, re.M | re.I)
    ref = match.group(1).upper() if match else "docs/NORTH_STAR.md#Outcome"
    section = re.search(r"^##\s+Outcome\s*$\n(.*?)(?=^##\s|\Z)", text, re.M | re.S | re.I)
    outcome = ""
    if section:
        for line in section.group(1).splitlines():
            clean = line.strip().lstrip("-* ").strip()
            if clean:
                outcome = clean
                break
    return ref, outcome


def task_event(
    root: Path,
    task_id: str,
    summary: str,
    status: str,
    *,
    follows: str = "",
) -> dict:
    ns_ref, _ = north_star(root)
    event = {
        "id": make_id(),
        "ts": now_iso(),
        "type": "task",
        "subject": task_id,
        "edge_class": "fact",
        "summary": summary,
        "task": task_id,
        "north_star": ns_ref,
        "status": status,
        "source_kind": "lifecycle",
        "source_ref": f"docs/TASKS.md#{task_id}",
        "basis": ["repository:docs/TASKS.md"],
        "coordinate": {"task": task_id, "persist": ["TASKS", "TRACE"]},
    }
    if ns_ref:
        event["serves"] = [ns_ref]
    if follows:
        event["follows"] = [follows]
    return event


def latest_verify_ids(events: list[dict], task_id: str) -> list[str]:
    return [
        str(event["id"])
        for event in events
        if event.get("type") == "verify"
        and event.get("task") == task_id
        and str(event.get("harness_result", "")).lower() in {"passed", "manual"}
        and event.get("id")
    ][-10:]


def edges(events: list[dict]) -> list[dict]:
    result: list[dict] = []
    for event in events:
        source = event.get("subject") or event.get("id")
        edge_class = event.get("edge_class") or "legacy"
        for predicate in EDGE_KEYS:
            values = event.get(predicate) or []
            if isinstance(values, str):
                values = [values]
            for target in values:
                result.append(
                    {
                        "event": event.get("id"),
                        "source": str(source),
                        "predicate": predicate,
                        "target": str(target),
                        "edge_class": edge_class,
                        "basis": event.get("basis") or [],
                    }
                )
    return result


def task_details(root: Path, task_id: str) -> dict:
    title = task_id
    goal = ""
    tasks = root / "docs" / "TASKS.md"
    if tasks.exists():
        text = tasks.read_text(encoding="utf-8", errors="ignore")
        block_match = re.search(
            rf"^##\s+{re.escape(task_id)}\s+([^\n]*)\n(.*?)(?=^##\s|\Z)",
            text,
            re.M | re.S,
        )
        if block_match:
            title = block_match.group(1).strip() or task_id
            goal_match = re.search(
                r"^G\s+[^\n]*\n(.*?)(?=^T\s+[^\n]*\n|\Z)",
                block_match.group(2),
                re.M | re.S,
            )
            if goal_match:
                for line in goal_match.group(1).splitlines():
                    clean = line.strip().lstrip("-* ").strip()
                    if clean:
                        goal = clean
                        break
    if title == task_id:
        progress = root / "docs" / "PROGRESS.md"
        if progress.exists():
            for line in progress.read_text(encoding="utf-8", errors="ignore").splitlines():
                if line.startswith("## ") and task_id in line:
                    title_match = re.match(r"##\s+\d{4}-\d{2}-\d{2}\s+-\s+(.*?)\s+\(", line)
                    if title_match:
                        title = title_match.group(1)
                        break
    return {"id": task_id, "title": title, "goal": goal}


def formal_candidates(root: Path) -> dict[str, dict]:
    folded: dict[str, dict] = {}
    for row in load_jsonl(candidate_path(root)):
        candidate_id = str(row.get("id", ""))
        if not candidate_id:
            continue
        if candidate_id not in folded:
            folded[candidate_id] = dict(row)
        else:
            folded[candidate_id].update(row)
    return folded


def append_candidate(
    root: Path,
    source: str,
    relation: str,
    target: str,
    reason: str,
    proposed_by: str,
) -> dict:
    row = {
        "id": make_id("CAND"),
        "ts": now_iso(),
        "status": "proposed",
        "source": source,
        "relation": relation,
        "target": target,
        "reason": reason,
        "proposed_by": proposed_by,
    }
    append_jsonl(candidate_path(root), row)
    return row


def resolve_candidate(
    root: Path,
    candidate_id: str,
    status: str,
    *,
    evidence: list[str] | None = None,
    confirmed_by: str = "",
    reason: str = "",
) -> dict:
    if status not in CANDIDATE_STATUSES - {"proposed"}:
        raise ValueError(f"invalid candidate resolution {status!r}")
    current = formal_candidates(root).get(candidate_id)
    if not current:
        raise ValueError(f"candidate {candidate_id} does not exist")
    if current.get("status") != "proposed":
        raise ValueError(f"candidate {candidate_id} is already {current.get('status')}")
    if status == "promoted" and not (evidence or confirmed_by):
        raise ValueError("promotion requires --evidence or --confirmed-by")
    row = {
        "id": candidate_id,
        "ts": now_iso(),
        "status": status,
        "evidence": evidence or [],
        "confirmed_by": confirmed_by,
        "resolution_reason": reason,
    }
    append_jsonl(candidate_path(root), row)
    return {**current, **row}


def _event_task_files(events: list[dict], task_id: str) -> tuple[list[str], list[str], list[str]]:
    files: set[str] = set()
    commits: set[str] = set()
    verifies: set[str] = set()
    for event in events:
        if event.get("task") != task_id:
            continue
        files.update(event.get("modifies") or event.get("files") or [])
        if event.get("commit"):
            commits.add(str(event["commit"]))
        if event.get("type") == "verify" and event.get("id"):
            result = str(event.get("harness_result", "")).lower()
            if result in {"passed", "manual"}:
                verifies.add(str(event["id"]))
        verifies.update(event.get("validated_by") or [])
    return sorted(files), sorted(commits), sorted(verifies)


def render_task_query(root: Path, task_id: str, *, heading: str = "Why") -> str:
    events = load_graph_events(root)
    detail = task_details(root, task_id)
    ns_ref, outcome = north_star(root)
    files, commits, verifies = _event_task_files(events, task_id)
    graph_edges = edges(events)
    serves = sorted(
        {edge["target"] for edge in graph_edges
         if edge["source"] == task_id and edge["predicate"] == "serves"}
        | {
            str(event["north_star"]) for event in events
            if event.get("task") == task_id and event.get("north_star")
        }
    )
    depends = sorted(
        {edge["target"] for edge in graph_edges
         if edge["source"] == task_id and edge["predicate"] == "depends_on"}
    )
    blocked_by = sorted(
        {edge["source"] for edge in graph_edges
         if edge["target"] == task_id and edge["predicate"] == "blocks"}
    )
    decisions = [
        event for event in events
        if event.get("task") == task_id and event.get("edge_class") == "decision"
    ]
    candidates = [
        item for item in formal_candidates(root).values()
        if item.get("status") == "proposed"
        and (item.get("source") == task_id or item.get("target") == task_id)
    ]
    lines = [f"# {heading}: {task_id}", "", f"Task: {detail['title']}"]
    if detail["goal"]:
        lines.append(f"Direct goal: {detail['goal']}")
    if serves:
        served_labels = [outcome if ref == ns_ref and outcome else ref for ref in serves]
        lines.append(f"Serves: {', '.join(served_labels)}")
    else:
        lines.append("Serves: no formal North Star link recorded")
    lines += [
        f"Modified: {len(files)} file(s)" + (f" ({', '.join(files[:8])}{'...' if len(files) > 8 else ''})" if files else ""),
        f"Implementation commits: {len(commits)}" + (f" ({', '.join(c[:12] for c in commits)})" if commits else ""),
        f"Verification evidence: {len(verifies)} item(s)",
        f"Depends on: {', '.join(depends) if depends else 'none'}",
        f"Blocked by: {', '.join(blocked_by) if blocked_by else 'none'}",
        f"Important decisions: {len(decisions)}",
    ]
    if candidates:
        lines.append(
            f"Unconfirmed candidates: {len(candidates)} "
            "(kept outside the formal graph)"
        )
    return "\n".join(lines)


def render_impact(root: Path, path: str) -> str:
    normalized = path.replace("\\", "/")
    events = load_graph_events(root)
    matches = [
        event for event in events
        if normalized in (event.get("modifies") or [])
        or normalized in (event.get("files") or [])
    ]
    tasks = sorted({str(event["task"]) for event in matches if event.get("task")})
    commits = sorted({str(event["commit"]) for event in matches if event.get("commit")})
    verify_ids = sorted(
        {str(value) for event in matches for value in (event.get("validated_by") or [])}
    )
    lines = [
        f"# Impact: {normalized}",
        "",
        f"Modified by {len(tasks)} task(s): {', '.join(tasks) if tasks else 'no formal record'}.",
        f"Implementation commits: {len(commits)}" + (f" ({', '.join(c[:12] for c in commits)})" if commits else "") + ".",
        f"Linked verification: {len(verify_ids)} item(s).",
    ]
    proposed = [
        item for item in formal_candidates(root).values()
        if item.get("status") == "proposed"
        and (item.get("source") == normalized or item.get("target") == normalized)
    ]
    if proposed:
        lines.append(
            f"{len(proposed)} unconfirmed candidate relationship(s) are excluded "
            "from these conclusions."
        )
    return "\n".join(lines)
