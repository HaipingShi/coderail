#!/usr/bin/env python3
"""CodeRail Done Gate: verification-before-complete.

This script checks whether a task may be marked done. It does not run tests for
you; it verifies that verification evidence and persistence links are recorded.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
import coordinate_check  # noqa: E402


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        return ""


def find_task(root: Path, task_id: str | None):
    text = read(root / "docs" / "TASKS.md")
    tasks = list(coordinate_check.split_tasks(text))
    if task_id:
        for h, b, s in tasks:
            if h.split()[0] == task_id:
                return h, b, s
        return None
    for h, b, s in tasks:
        if s == "[~]":
            return h, b, s
    for h, b, s in tasks:
        if s == "[ ]" and "Example task" not in h and "Copy template" not in h:
            return h, b, s
    return None


def git_changed_files(root: Path) -> list[str]:
    try:
        out = subprocess.check_output(["git", "-C", str(root), "status", "--short"], text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return []
    files = []
    for line in out.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        files.append(path)
    return files


def split_patterns(value: str) -> list[str]:
    out = []
    for line in (value or "").splitlines():
        line = line.strip().lstrip("-* ").strip()
        if not line or line.lower() in {"none", "n/a"}:
            continue
        out.append(line)
    return out


def matches_any(path: str, patterns: list[str]) -> bool:
    normalized = path.replace("\\", "/").lstrip("./")
    for pat in patterns:
        p = pat.rstrip().replace("\\", "/").lstrip("./")
        if not p:
            continue
        if p.endswith("/**"):
            base = p[:-3].rstrip("/")
            if normalized == base or normalized.startswith(base + "/"):
                return True
        if fnmatch.fnmatch(normalized, p) or normalized == p:
            return True
    return False


def load_events(root: Path) -> list[dict]:
    log = root / "docs" / "TRACELOG.jsonl"
    events = []
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


def has_verify_trace(events: list[dict], task: str) -> bool:
    for ev in events:
        if ev.get("type") == "verify" and ev.get("task") == task:
            result = str(ev.get("harness_result", "")).lower()
            if result in {"passed", "manual"}:
                return True
    return False


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Run CodeRail done gate")
    ap.add_argument("--target", default=".")
    ap.add_argument("--task", help="Task id to check, e.g. T-001")
    ap.add_argument("--harness-result", choices=["passed", "failed", "manual", "skipped"], help="Fresh verification result to consider")
    ap.add_argument("--manual-acceptance", help="Manual acceptance evidence")
    ap.add_argument("--changed-files", help="Comma-separated changed files; defaults to git status")
    args = ap.parse_args(argv)
    root = Path(args.target).resolve()
    found = find_task(root, args.task)
    severe, warnings = [], []
    if not found:
        print("# Done Gate Report\n")
        print("Status: blocked\n")
        print("## Severe\n- task not found or no active task")
        return 1
    header, body, status = found
    task_id = header.split()[0]
    coord = coordinate_check.parse_coordinate(body)
    if coord is None:
        severe.append(f"{task_id}: missing CodeRail Coordinate")
    else:
        for key, label in [("g", "G"), ("t", "T"), ("s_allowed", "S allowed"), ("v", "V"), ("p", "P")]:
            if not coord.get(key):
                severe.append(f"{task_id}: {label} missing")
        if not coord.get("x"):
            warnings.append(f"{task_id}: X stop conditions empty")
        p = (coord.get("p") or "").upper()
        if "TASKS" not in p:
            severe.append(f"{task_id}: P must include TASKS")
        if "TRACE" not in p:
            severe.append(f"{task_id}: P must include TRACE")

        changed = []
        if args.changed_files:
            changed = [x.strip() for x in args.changed_files.split(",") if x.strip()]
        else:
            changed = git_changed_files(root)
        allowed = split_patterns(coord.get("s_allowed", ""))
        forbidden = split_patterns(coord.get("s_forbidden", ""))
        for f in changed:
            if forbidden and matches_any(f, forbidden):
                severe.append(f"{task_id}: changed forbidden file {f}")
            if allowed and not matches_any(f, allowed):
                warnings.append(f"{task_id}: changed file outside allowed scope: {f}")

    if args.harness_result == "failed":
        severe.append(f"{task_id}: fresh harness result is failed")
    verification_ok = args.harness_result in {"passed", "manual"} or bool(args.manual_acceptance)
    if args.harness_result == "skipped" and not args.manual_acceptance:
        severe.append(f"{task_id}: skipped harness requires explicit manual acceptance evidence")
    events = load_events(root)
    if not verification_ok and not has_verify_trace(events, task_id):
        severe.append(f"{task_id}: no passing verify trace or fresh harness/manual acceptance evidence")

    trace_index = root / "docs" / "TRACE_INDEX.md"
    tracelog = root / "docs" / "TRACELOG.jsonl"
    if tracelog.exists() and trace_index.exists() and tracelog.stat().st_mtime > trace_index.stat().st_mtime:
        warnings.append("TRACE_INDEX.md is stale; run scripts/trace_index.py")
    if not tracelog.exists():
        severe.append("docs/TRACELOG.jsonl missing")

    status_out = "pass" if not severe else "blocked"
    print("# Done Gate Report\n")
    print(f"Status: {status_out}")
    print(f"Task: {task_id}\n")
    print("## Severe")
    print("- none" if not severe else "\n".join(f"- {x}" for x in severe))
    print("\n## Warnings")
    print("- none" if not warnings else "\n".join(f"- {x}" for x in warnings))
    print("\n## Next")
    if severe:
        print("- Do not mark the task done. Fix severe items, record verification, sync P, and rerun done_gate.py.")
    else:
        print("- Completion is allowed. Update TASKS, write/confirm verify trace, regenerate TRACE_INDEX, then run Handoff Trigger Check.")
    return 1 if severe else 0


if __name__ == "__main__":
    raise SystemExit(main())
