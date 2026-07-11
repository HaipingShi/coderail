#!/usr/bin/env python3
"""Inspect CodeRail runtime state and write docs/CODERAIL_STATUS.md.

This is a repo-local state surface. It reads CodeRail's markdown/jsonl files and
summarizes what is active, blocked, unverified, or unsafe to continue.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from datetime import datetime, timezone
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
import coordinate_check  # noqa: E402
import trace_doctor  # noqa: E402
import contract_check  # noqa: E402
import drive_check  # noqa: E402


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        return ""


def first_section_value(text: str, header: str) -> str:
    m = re.search(rf"^##\s+{re.escape(header)}\s*\n(.*?)(?=^##\s|\Z)", text, re.S | re.M | re.I)
    if not m:
        return ""
    lines = [ln.strip("- ") for ln in m.group(1).splitlines() if ln.strip() and not ln.strip().startswith(">")]
    return lines[0] if lines else ""


def git_status(root: Path) -> str:
    try:
        out = subprocess.check_output(["git", "-C", str(root), "status", "--short"], text=True, stderr=subprocess.DEVNULL)
        return out.strip()
    except Exception:
        return "git status unavailable"


def load_events(root: Path) -> list[dict]:
    events = []
    log = root / "docs" / "TRACELOG.jsonl"
    if not log.exists():
        return events
    for raw in log.read_text(encoding="utf-8", errors="ignore").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            events.append(json.loads(raw))
        except json.JSONDecodeError:
            pass
    return events


def task_statuses(root: Path):
    text = read(root / "docs" / "TASKS.md")
    rows = []
    for header, body, status in coordinate_check.split_tasks(text):
        if "Example task" in header or "Copy template" in header:
            continue
        coord = coordinate_check.parse_coordinate(body) or {}
        rows.append({"id": header.split()[0], "header": header, "body": body, "status": status, "coord": coord})
    return rows


def draft_statuses(root: Path):
    text = read(root / "docs" / "CONTRACTS.md")
    rows = []
    for header, body, status in contract_check.split_drafts(text):
        if "Example draft" in header:
            continue
        rows.append({"id": header.split()[0], "header": header, "status": status})
    return rows


def legacy_cutoff(ns: str, tasks: list[dict]) -> tuple[str, list[dict], list[dict], str]:
    block = drive_check.section(ns, "Legacy Cutoff")
    enforcement_task = drive_check.field_value(block, "Enforcement starts at")
    if not enforcement_task:
        return "", tasks, [], ""

    anchor = next((index for index, task in enumerate(tasks) if task["id"] == enforcement_task), None)
    if anchor is None:
        issue = f"legacy cutoff configured enforcement task {enforcement_task} was not found"
        return enforcement_task, tasks, [], issue

    before = tasks[:anchor]
    post_cutover = tasks[anchor:]
    active_before_cutoff = [task for task in before if task["status"] in {"[~]", "[!]"}]
    historical = [task for task in before if task["status"] not in {"[~]", "[!]"}]
    return enforcement_task, active_before_cutoff + post_cutover, historical, ""


def weak_verification_gaps(tasks: list[dict]) -> list[str]:
    gaps = []
    for task in tasks:
        verification = (task["coord"].get("v") or "").lower()
        if task["status"] == "[x]" and not any(
            marker in verification for marker in ["passed", "manual", "pytest", "test", "harness"]
        ):
            gaps.append(f"{task['id']}: done task has weak V evidence")
    return gaps


def render(root: Path) -> tuple[str, str]:
    docs = root / "docs"
    ns = read(docs / "NORTH_STAR.md")
    outcome = first_section_value(ns, "Outcome") or "(unknown)"
    current_slice = first_section_value(ns, "Current Slice") or "(unknown)"
    tasks = task_statuses(root)
    enforcement_task, enforced_tasks, historical_tasks, cutoff_issue = legacy_cutoff(ns, tasks)
    drafts = draft_statuses(root)
    active_drafts = [d for d in drafts if d["status"] in drive_check.ACTIVE_DRAFT_STATUSES]
    active = [t for t in tasks if t["status"] in {"[~]", "[ ]", "[!]"}]
    events = load_events(root)
    trace_severe, trace_warn = trace_doctor.check(events, docs / "TRACE_INDEX.md", docs / "TRACELOG.jsonl")
    drive = drive_check.evaluate(root)

    verification_gaps = weak_verification_gaps(enforced_tasks)
    historical_verification_debt = weak_verification_gaps(historical_tasks)
    if cutoff_issue:
        verification_gaps.insert(0, cutoff_issue)
    for item in trace_severe:
        if "verify" in item or "harness" in item:
            verification_gaps.append(item)

    trace_gaps = trace_warn + [x for x in trace_severe if x not in verification_gaps]
    handoff = read(docs / "HANDOFF.md")
    hm = re.search(r"Handoff Level:\s*([^\n]+)", handoff)
    handoff_level = hm.group(1).strip() if hm else "unknown"
    handoff_needs = "yes" if "needs" in handoff.lower() else "no"

    drive_blocked = drive["mode"] == "continuous" and drive["decision"] in {"BLOCKED_DECISION", "EXHAUSTED"}
    drive_warning = drive["mode"] == "continuous" and drive["decision"] == "REVIEW_DIRECTION"
    status = (
        "blocked"
        if verification_gaps or trace_severe or drive_blocked
        else ("warning" if trace_gaps or not outcome or active or drive_warning else "healthy")
    )

    lines = []
    lines.append("# CodeRail Status")
    lines.append("")
    lines.append("> Generated by `python .coderail/coderail.py inspect`. Prefer regenerating this file instead of editing it by hand.")
    lines.append("")
    lines.append(f"Generated at: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    lines.append(f"Status: {status}")
    lines.append("")
    lines.append("## Current North Star")
    lines.append("")
    lines.append(f"- Outcome: {outcome}")
    lines.append(f"- Current Slice: {current_slice}")
    lines.append("")
    lines.append("## Legacy Cutoff")
    lines.append("")
    if enforcement_task:
        lines.append(f"- Enforcement starts at: {enforcement_task}")
        lines.append(f"- Status: {'invalid' if cutoff_issue else 'active'}")
        lines.append(f"- Historical tasks excluded from current verification status: {len(historical_tasks)}")
    else:
        lines.append("- Enforcement starts at: none (all tasks enforced)")
        lines.append("- Status: disabled")
        lines.append("- Historical tasks excluded from current verification status: 0")
    lines.append("")
    lines.append("## Active Coordinate")
    lines.append("")
    if active:
        t = active[0]
        coord = t["coord"]
        explicit_rail = coordinate_check.explicit_rail(t["body"])
        rail = coordinate_check.rail_type(t["header"], t["body"], None, None)
        task_kind = coordinate_check.task_type(t["body"]) or "(unspecified)"
        lines.append(f"- Task: {t['header']} ({t['status']})")
        lines.append(f"- Rail: {rail}")
        lines.append(f"- Rail source: {'explicit' if explicit_rail else 'inferred; add Rail: full | light'}")
        lines.append(f"- Type: {task_kind}")
        lines.append(f"- G: {coord.get('g','(missing)') or '(missing)'}")
        lines.append(f"- T: {coord.get('t','(missing)') or '(missing)'}")
        lines.append(f"- S allowed: {coord.get('s_allowed','(missing)') or '(missing)'}")
        lines.append(f"- S forbidden: {coord.get('s_forbidden','(missing)') or '(missing)'}")
        lines.append(f"- V: {coord.get('v','(missing)') or '(missing)'}")
        lines.append(f"- X: {coord.get('x','(missing)') or '(missing)'}")
        lines.append(f"- P: {coord.get('p','(missing)') or '(missing)'}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Active Tasks")
    lines.append("")
    if active:
        for t in active:
            lines.append(f"- {t['header']} — {t['status']}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Draft Contracts")
    lines.append("")
    if drafts:
        for d in drafts:
            lines.append(f"- {d['header']} — {d['status']}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Verification Gaps")
    lines.append("")
    lines.append("- none" if not verification_gaps else "\n".join(f"- {x}" for x in verification_gaps))
    lines.append("")
    lines.append("## Historical Verification Debt")
    lines.append("")
    if not historical_verification_debt:
        lines.append("- none")
    else:
        lines.extend(f"- {item}" for item in historical_verification_debt[:20])
        if len(historical_verification_debt) > 20:
            lines.append(f"- ... {len(historical_verification_debt) - 20} more")
    lines.append("")
    lines.append("## Trace Gaps")
    lines.append("")
    lines.append("- none" if not trace_gaps else "\n".join(f"- {x}" for x in trace_gaps[:20]))
    lines.append("")
    lines.append("## Drive Decision")
    lines.append("")
    lines.append(f"- Mode: {drive['mode']}")
    lines.append(f"- Decision: {drive['decision']}")
    lines.append(f"- Task: {drive['task'] or 'none'}")
    lines.append(f"- Reason: {drive['reason']}")
    lines.append(f"- Next action: {drive['next_action']}")
    lines.append("")
    lines.append("## Execution Decision")
    lines.append("")
    lines.append(f"- Mode: {drive['mode']}")
    lines.append(f"- Decision: {drive['decision']}")
    lines.append(f"- Task: {drive['task'] or 'none'}")
    lines.append(f"- Reason: {drive['reason']}")
    lines.append(f"- Next action: {drive['next_action']}")
    lines.append("")
    recommendation = drive["recommendation"]
    lines.append("## Recommendation Decision")
    lines.append("")
    lines.append(f"- Status: {recommendation['status']}")
    lines.append(f"- Reason: {recommendation['reason']}")
    lines.append(f"- Next action: {recommendation['next_action']}")
    lines.append(
        "- Requires human approval for execution: "
        + ("yes" if recommendation["requires_human_for_execution"] else "no")
    )
    lines.append("- Evidence:")
    if recommendation["evidence"]:
        lines.extend(f"  - {item}" for item in recommendation["evidence"])
    else:
        lines.append("  - none")
    lines.append("")
    lines.append("## Handoff")
    lines.append("")
    lines.append(f"- Level: {handoff_level}")
    lines.append(f"- Needs update: {handoff_needs}")
    lines.append("")
    lines.append("## Recommended Next Action")
    lines.append("")
    if verification_gaps:
        lines.append("- Run `/coderail:done-gate` and fix verification gaps before marking done.")
    elif drive["mode"] == "continuous" and drive["decision"] in drive_check.NON_STOP_STATES:
        lines.append(f"- Drive {drive['decision']}: {drive['next_action']}")
    elif recommendation["status"] != "NO_RECOMMENDATION":
        lines.append(f"- Recommendation {recommendation['status']}: {recommendation['next_action']}")
    elif drive["mode"] == "continuous":
        lines.append(f"- Drive {drive['decision']}: {drive['next_action']}")
    elif active:
        lines.append("- Continue the active task inside S and stop if X triggers.")
    elif active_drafts:
        lines.append("- Accept, revise, reject, or backlog the active contract draft before coding.")
    else:
        lines.append("- Run `/coderail:align` or `/coderail:contract-draft` for the next request.")
    lines.append("")
    lines.append("## Auto Commit")
    lines.append("")
    gs = git_status(root)
    if gs == "git status unavailable":
        lines.append("- Worktree: unknown")
        lines.append("- Git status unavailable; inspect the worktree before auto-commit.")
    elif gs:
        lines.append("- Worktree: dirty")
        lines.append("- Avoid `git add .` until changed files are matched to the active task S.")
        lines.append("- Run `python .coderail/coderail.py finish --task <ID> --task-result <result>` before stopping.")
    else:
        lines.append("- Worktree: clean")
        lines.append("- No commit boundary needed unless new work is started.")
    lines.append("")
    lines.append("## Git Status")
    lines.append("")
    lines.append("```text")
    lines.append(gs or "clean")
    lines.append("```")
    lines.append("")
    return status, "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Inspect CodeRail runtime state")
    ap.add_argument("--target", default=".")
    ap.add_argument("--write", action="store_true", help="Write docs/CODERAIL_STATUS.md")
    ap.add_argument("--no-write", action="store_true", help="Print only; do not write")
    args = ap.parse_args(argv)
    root = Path(args.target).resolve()
    status, text = render(root)
    if args.write or not args.no_write:
        docs = root / "docs"
        docs.mkdir(parents=True, exist_ok=True)
        (docs / "CODERAIL_STATUS.md").write_text(text + "\n", encoding="utf-8")
    print(text)
    return 1 if status == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
