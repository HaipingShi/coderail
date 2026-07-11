#!/usr/bin/env python3
"""Compute the next CodeRail Drive state from repo-local evidence.

This script is a deterministic policy evaluator. It does not execute an agent,
change project state, or grant authority.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import coordinate_check  # noqa: E402
import done_gate  # noqa: E402


NON_STOP_STATES = {"CONTINUE", "REPAIR", "ADVANCE"}
STOP_STATES = {"REVIEW_DIRECTION", "BLOCKED_DECISION", "COMPLETE", "EXHAUSTED"}
PRIORITY = {"p1": 0, "p2": 1, "p3": 2}
DECISION_PATH_PATTERNS = [
    re.compile(r"(^|/)(package\.json|pyproject\.toml|requirements[^/]*\.txt)$", re.I),
    re.compile(r"(^|/)([^/]*lock[^/]*)$", re.I),
    re.compile(r"(^|/)(schema|schemas|migrations?|permissions?)(/|\.|$)", re.I),
    re.compile(r"(^|/)\.codex/config\.toml$", re.I),
]


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        return ""


def section(text: str, header: str) -> str:
    match = re.search(
        rf"^##\s+{re.escape(header)}\s*$\n(.*?)(?=^##\s|\Z)",
        text,
        re.I | re.M | re.S,
    )
    return match.group(1) if match else ""


def field_value(text: str, label: str) -> str:
    match = re.search(rf"^[ \t]*-?[ \t]*{re.escape(label)}:[ \t]*(.*)$", text, re.I | re.M)
    return match.group(1).strip() if match else ""


def int_value(value: str, default: int) -> int:
    match = re.search(r"\d+", value or "")
    return int(match.group(0)) if match else default


def load_events(root: Path) -> list[dict]:
    rows = []
    for raw in read(root / "docs" / "TRACELOG.jsonl").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def parse_dependencies(body: str) -> list[str]:
    match = re.search(r"^Depends on:\s*\n(.*?)(?=^[A-Za-z][^\n]*:\s*$|^###\s|^##\s|\Z)", body, re.I | re.M | re.S)
    if not match:
        return []
    deps = []
    for raw in match.group(1).splitlines():
        value = raw.strip().lstrip("-* ").strip()
        if not value or value.lower() in {"none", "n/a", "-"}:
            continue
        task_id = re.match(r"[A-Z]-\d+", value)
        if task_id:
            deps.append(task_id.group(0))
    return deps


def parse_tasks(root: Path) -> list[dict]:
    tasks = []
    text = read(root / "docs" / "TASKS.md")
    for index, (header, body, status) in enumerate(coordinate_check.split_tasks(text)):
        task_id = header.split()[0]
        tasks.append(
            {
                "id": task_id,
                "header": header,
                "body": body,
                "status": status,
                "autonomy": coordinate_check.meta_value("Autonomy", body) or "human-gated",
                "priority": coordinate_check.meta_value("Priority", body) or "p3",
                "dependencies": parse_dependencies(body),
                "stage_complete": bool(re.search(r"^Task result:\s*stage-complete\s*$", body, re.I | re.M)),
                "index": index,
            }
        )
    return tasks


def ready_tasks(tasks: list[dict]) -> list[dict]:
    statuses = {task["id"]: task["status"] for task in tasks}
    ready = []
    for task in tasks:
        if task["status"] not in {"[ ]", "[r]"} or task["autonomy"] != "allowed":
            continue
        if all(statuses.get(dep) == "[x]" for dep in task["dependencies"]):
            ready.append(task)
    return sorted(ready, key=lambda task: (PRIORITY.get(task["priority"], 9), task["index"]))


def latest_harness(events: list[dict], task_id: str | None) -> str:
    for row in reversed(events):
        if row.get("type") != "verify":
            continue
        if task_id and row.get("task") not in {None, "", task_id}:
            continue
        result = str(row.get("harness_result") or "").strip().lower()
        if result:
            return result
    return ""


def unresolved_event_count(events: list[dict], task_id: str | None, statuses: set[str]) -> int:
    count = 0
    for row in reversed(events):
        if task_id and row.get("task") not in {None, "", task_id}:
            continue
        status = str(row.get("status") or "").strip().lower()
        harness_result = str(row.get("harness_result") or "").strip().lower()
        if harness_result in {"passed", "manual"} or status in {
            "progress", "advanced", "complete", "completed", "done",
        }:
            break
        if status in statuses:
            count += 1
    return count


def has_direction_signal(events: list[dict]) -> tuple[bool, str]:
    reopened: dict[str, int] = {}
    scope_pressure = 0
    for row in events:
        status = str(row.get("status") or "").strip().lower()
        task_id = str(row.get("task") or "project")
        if status == "reopened":
            reopened[task_id] = reopened.get(task_id, 0) + 1
        if status in {"scope-expanded", "scope_expanded"}:
            scope_pressure += 1
        if status in {"review-direction", "review_direction"} or row.get("source_kind") == "direction-review":
            return True, f"trace event {row.get('id', '(unknown)')} explicitly requests direction review"
    repeated = [task_id for task_id, count in reopened.items() if count >= 2]
    if repeated:
        return True, f"task {repeated[0]} was reopened at least twice"
    if scope_pressure >= 2:
        return True, "scope expansion was recorded at least twice"
    return False, ""


def split_files(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip().replace("\\", "/") for item in value.split(",") if item.strip()]


def git_changed_files(root: Path) -> list[str]:
    try:
        output = subprocess.check_output(
            ["git", "-C", str(root), "status", "--short", "--untracked-files=all"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return []
    files = []
    for raw in output.splitlines():
        if not raw.strip() or len(raw) < 4:
            continue
        path = raw[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        files.append(path.replace("\\", "/"))
    return files


def decision_file(files: list[str]) -> str:
    for path in files:
        if any(pattern.search(path) for pattern in DECISION_PATH_PATTERNS):
            return path
    return ""


def terminal_from_events(events: list[dict]) -> bool:
    for row in reversed(events):
        if row.get("type") != "verify" or str(row.get("harness_result") or "").lower() != "passed":
            continue
        status = str(row.get("status") or "").lower()
        if status in {"terminal", "complete"} or row.get("source_kind") == "terminal-evidence":
            return True
    return False


def report(
    decision: str,
    mode: str,
    reason: str,
    next_action: str,
    task: str | None = None,
    evidence=None,
    recommended_task: str | None = None,
    next_task_mode: str = "recommend",
) -> dict:
    return {
        "mode": mode,
        "decision": decision,
        "may_stop": decision in STOP_STATES,
        "task": task,
        "reason": reason,
        "next_action": next_action,
        "evidence": evidence or [],
        "recommended_task": recommended_task,
        "next_task_mode": next_task_mode,
    }


def evaluate(
    root: Path,
    *,
    harness_result: str = "",
    retry_count: int | None = None,
    no_progress_count: int | None = None,
    failure_known: bool = False,
    terminal_evidence: bool = False,
    changed_files: list[str] | None = None,
    decision_signals: list[str] | None = None,
    next_task_mode: str | None = None,
) -> dict:
    north_star = read(root / "docs" / "NORTH_STAR.md")
    contract = section(north_star, "Drive Contract")
    mode = (field_value(contract, "Mode") or "manual").split("|")[0].strip().lower()
    terminal_condition = field_value(contract, "Terminal condition")
    progress_signal = field_value(contract, "Progress signal")
    retry_budget = int_value(field_value(contract, "Retry budget"), 3)
    no_progress_limit = int_value(field_value(contract, "No-progress limit"), 2)
    configured_next_mode = (next_task_mode or field_value(contract, "Next-task mode") or "recommend").lower()
    if configured_next_mode not in {"recommend", "activate"}:
        configured_next_mode = "recommend"
    progress_harness = section(read(root / "docs" / "HARNESS_SPEC.md"), "Drive Progress Harness")
    harness_progress = field_value(progress_harness, "Progress signal")
    checkpoint_command = field_value(progress_harness, "Checkpoint command")
    terminal_harness = field_value(progress_harness, "Terminal evidence")
    events = load_events(root)
    tasks = parse_tasks(root)
    active_tasks = [task for task in tasks if task["status"] in {"[~]", "[!]"}]
    active = active_tasks[0] if active_tasks else None
    active_id = active["id"] if active else None
    ready = ready_tasks(tasks)
    terminal = terminal_evidence or terminal_from_events(events)
    retry = retry_count if retry_count is not None else unresolved_event_count(events, active_id, {"retry", "failed"})
    no_progress = no_progress_count if no_progress_count is not None else unresolved_event_count(events, active_id, {"no-progress", "no_progress"})
    harness = (harness_result or latest_harness(events, active_id)).strip().lower()
    files = git_changed_files(root) if changed_files is None else changed_files
    signals = [value for value in (decision_signals or []) if value]

    recommendation = ready[0] if ready else None
    if mode != "continuous":
        next_action = (
            f"Recommended next task: {recommendation['id']}. Activate it explicitly when ready."
            if recommendation
            else "Continue in manual mode; no dependency-ready autonomous task is available to recommend."
        )
        return report(
            "BLOCKED_DECISION", mode, "Drive Contract is not in continuous mode.", next_action,
            active_id,
            recommended_task=recommendation["id"] if recommendation else None,
            next_task_mode=configured_next_mode,
        )
    if not terminal_condition or not progress_signal:
        missing = "terminal condition" if not terminal_condition else "progress signal"
        return report(
            "BLOCKED_DECISION", mode, f"Continuous Drive is missing its {missing}.",
            f"Define the {missing} in docs/NORTH_STAR.md before continuing.", active_id,
        )
    if not harness_progress or not (checkpoint_command or terminal_harness):
        return report(
            "BLOCKED_DECISION", mode, "Continuous Drive has no configured progress harness.",
            "Define the progress signal and checkpoint command or terminal evidence in docs/HARNESS_SPEC.md.",
            active_id,
        )
    if len(active_tasks) > 1:
        ids = ", ".join(task["id"] for task in active_tasks)
        return report(
            "BLOCKED_DECISION", mode, f"Multiple active tasks make Drive ownership ambiguous: {ids}.",
            "Keep exactly one task active or record an explicit task-selection decision before continuing.",
            None,
            [f"active={ids}"],
        )
    risky_file = decision_file(files)
    if signals or risky_file:
        detail = signals[0] if signals else f"decision-grade file changed: {risky_file}"
        return report(
            "BLOCKED_DECISION", mode, detail,
            "Obtain explicit authority and update the Coordinate before continuing.", active_id,
            [detail],
        )
    scope_task = active or (ready[0] if ready else None)
    if scope_task:
        coordinate_severe, _ = coordinate_check.check_task(
            scope_task["header"], scope_task["body"], scope_task["status"]
        )
        if coordinate_severe:
            detail = coordinate_severe[0]
            return report(
                "BLOCKED_DECISION", mode, f"Selected task has an invalid Coordinate: {detail}",
                f"Repair {scope_task['id']} Coordinate before continuous execution.",
                scope_task["id"],
                coordinate_severe,
            )
    if files and not scope_task:
        return report(
            "BLOCKED_DECISION", mode, f"Changed files have no active or ready task owner: {files[0]}.",
            "Assign the changes to an authorized task Coordinate before continuing.", None, files,
        )
    if files and scope_task:
        coordinate = coordinate_check.parse_coordinate(scope_task["body"]) or {}
        allowed = done_gate.split_patterns(coordinate.get("s_allowed", ""))
        forbidden = done_gate.split_patterns(coordinate.get("s_forbidden", ""))
        forbidden_file = next((path for path in files if done_gate.matches_any(path, forbidden)), "")
        outside_file = next((path for path in files if allowed and not done_gate.matches_any(path, allowed)), "")
        if forbidden_file or outside_file:
            detail = (
                f"changed forbidden file: {forbidden_file}"
                if forbidden_file
                else f"changed file outside {scope_task['id']} S allowed: {outside_file}"
            )
            return report(
                "BLOCKED_DECISION", mode, detail,
                "Restore task ownership boundaries or obtain explicit scope authority before continuing.",
                scope_task["id"],
                [detail],
            )
    if active and active["autonomy"] != "allowed":
        return report(
            "BLOCKED_DECISION", mode, f"{active_id} is marked Autonomy: {active['autonomy']}.",
            f"Request the human gate for {active_id} or mark a separately authorized task autonomous.", active_id,
        )
    if active and active["status"] == "[!]":
        return report(
            "BLOCKED_DECISION", mode, f"{active_id} is explicitly blocked.",
            f"Resolve the recorded blocker for {active_id} before continuing.", active_id,
        )
    direction, direction_reason = has_direction_signal(events)
    if direction:
        return report(
            "REVIEW_DIRECTION", mode, direction_reason,
            "Run direction review and persist the accepted policy delta before more implementation.", active_id,
            [direction_reason],
        )
    if retry >= retry_budget or no_progress >= no_progress_limit:
        reason = (
            f"retry budget exhausted ({retry}/{retry_budget})"
            if retry >= retry_budget
            else f"no-progress limit reached ({no_progress}/{no_progress_limit})"
        )
        return report(
            "EXHAUSTED", mode, reason,
            "Persist failure evidence and request a decision or revised task contract.", active_id,
            [reason],
        )
    if active and harness in {"failed", "failure", "error"}:
        qualifier = "known in-scope failure" if failure_known else "first unresolved harness failure"
        return report(
            "REPAIR", mode, f"{active_id} has a {qualifier} with retry budget remaining.",
            f"Diagnose or repair {active_id} inside S, rerun its harness, then rerun drive_check.py.", active_id,
            [f"retry {retry}/{retry_budget}", f"harness={harness}"],
        )
    if active:
        if active["stage_complete"]:
            return report(
                "CONTINUE", mode, f"{active_id} is stage-complete but remains active until its acceptance is done.",
                f"Continue {active_id} with its remaining acceptance or validation step; do not activate another task yet.",
                active_id,
                [f"checkpoint={active_id}", f"retry {retry}/{retry_budget}", f"no-progress {no_progress}/{no_progress_limit}"],
            )
        return report(
            "CONTINUE", mode, f"{active_id} is active, autonomous, and inside its Drive budget.",
            f"Continue {active_id} inside S and run its next progress checkpoint.", active_id,
            [f"retry {retry}/{retry_budget}", f"no-progress {no_progress}/{no_progress_limit}"],
        )
    if ready:
        chosen = ready[0]
        verb = "Activate" if configured_next_mode == "activate" else "Recommend"
        return report(
            "ADVANCE", mode, f"{chosen['id']} is the highest-priority dependency-ready autonomous task.",
            f"{verb} {chosen['id']}; confirm its Coordinate and run its first progress checkpoint.", chosen["id"],
            [f"ready={chosen['id']}", f"priority={chosen['priority'].upper()}"],
            recommended_task=chosen["id"], next_task_mode=configured_next_mode,
        )
    if terminal:
        return report(
            "COMPLETE", mode, "Terminal evidence is present and no active or ready autonomous task remains.",
            "Run done/closeout checks and close the durable goal.", None,
            [f"terminal condition={terminal_condition}"],
        )
    gated = next((task for task in tasks if task["status"] in {"[ ]", "[r]"} and task["autonomy"] != "allowed"), None)
    reason = (
        f"{gated['id']} is ready only behind a human gate."
        if gated
        else "No active or ready autonomous task exists and terminal evidence is absent."
    )
    return report(
        "BLOCKED_DECISION", mode, reason,
        "Authorize a ready task or provide terminal evidence; do not invent backlog work.",
        gated["id"] if gated else None,
    )


def render_human(result: dict) -> str:
    lines = ["# CodeRail Drive Check", ""]
    lines.append(f"Mode: {result['mode']}")
    lines.append(f"Decision: {result['decision']}")
    lines.append(f"May stop: {'yes' if result['may_stop'] else 'no'}")
    lines.append(f"Task: {result['task'] or 'none'}")
    lines.append(f"Next-task mode: {result['next_task_mode']}")
    lines.append(f"Recommended task: {result['recommended_task'] or 'none'}")
    lines.append("")
    lines.append("## Reason")
    lines.append("")
    lines.append(f"- {result['reason']}")
    lines.append("")
    lines.append("## Next Executable Action")
    lines.append("")
    lines.append(f"- {result['next_action']}")
    lines.append("")
    lines.append("## Evidence")
    lines.append("")
    lines.extend(f"- {item}" for item in result["evidence"]) if result["evidence"] else lines.append("- none")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Compute the next CodeRail Drive decision")
    parser.add_argument("--target", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--harness-result", default="")
    parser.add_argument("--retry-count", type=int)
    parser.add_argument("--no-progress-count", type=int)
    parser.add_argument("--failure-known", action="store_true")
    parser.add_argument("--terminal-evidence", action="store_true")
    parser.add_argument(
        "--changed-files",
        help="Comma-separated task delta; defaults to all current git changes",
    )
    parser.add_argument("--decision-signal", action="append", default=[])
    parser.add_argument("--next-task-mode", choices=["recommend", "activate"])
    args = parser.parse_args(argv)
    root = Path(args.target).resolve()
    if not root.exists() or not (root / "docs" / "NORTH_STAR.md").exists():
        print(f"error: {root} is not a CodeRail project", file=sys.stderr)
        return 2
    result = evaluate(
        root,
        harness_result=args.harness_result,
        retry_count=args.retry_count,
        no_progress_count=args.no_progress_count,
        failure_known=args.failure_known,
        terminal_evidence=args.terminal_evidence,
        changed_files=None if args.changed_files is None else split_files(args.changed_files),
        decision_signals=args.decision_signal,
        next_task_mode=args.next_task_mode,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else render_human(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
