#!/usr/bin/env python3
"""Static drift check for CodeRail docs.

Checks North-Star alignment, Coordinate drift, and Trace Graph health.
Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import coordinate_check  # noqa: E402 — reuse the authoritative coordinate parser

TASK_HEADER = re.compile(r"^##\s+([A-Z]-\d+[^\n]*)", re.M)


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        return ""


def load_trace(path: Path) -> list:
    if not path.exists():
        return []
    events = []
    with path.open("r", encoding="utf-8") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            try:
                events.append(json.loads(raw))
            except json.JSONDecodeError:
                continue
    return events


def _tasks_with_coordinate(tasks_text: str):
    """Yield (task_id, has_coord_block, has_g, has_v, status).

    Reuses coordinate_check.parse_coordinate so drift detection and the
    coordinate gate agree on what counts as a present G/V field.
    """
    for header, body, status in coordinate_check.split_tasks(tasks_text):
        tid = header.split()[0]
        coord = coordinate_check.parse_coordinate(body)
        if coord is None:
            yield tid, False, False, False, status
            continue
        has_g = bool(coord.get("g"))
        has_v = bool(coord.get("v"))
        yield tid, True, has_g, has_v, status


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default=".")
    args = parser.parse_args(argv)
    root = Path(args.target).resolve()

    north = read(root / "docs/NORTH_STAR.md")
    tasks = read(root / "docs/TASKS.md")
    handoff = read(root / "docs/HANDOFF.md")
    decisions = read(root / "docs/DECISIONS.md")
    events = load_trace(root / "docs/TRACELOG.jsonl")

    issues = []

    # North-Star alignment.
    if not north.strip():
        issues.append("Missing or empty docs/NORTH_STAR.md")
    if handoff and len(handoff.splitlines()) > 120:
        issues.append("HANDOFF.md is over 120 lines and may be acting as a log")
    if decisions and "Current Bet" in decisions and "Current Bet" not in north:
        issues.append("DECISIONS.md may change current bet but NORTH_STAR does not mention it")
    if handoff and north and "Current slice" in handoff:
        # Crude: handoff references work not in north star's outcome section.
        if "Outcome:" in handoff and handoff.split("Outcome:", 1)[1].split("\n", 1)[0].strip() and "## 1. Outcome" in north:
            handoff_outcome = handoff.split("Outcome:", 1)[1].split("\n", 1)[0].strip()
            if handoff_outcome and handoff_outcome not in north:
                issues.append("HANDOFF.md references an outcome not recorded in NORTH_STAR.md (possible drift)")

    # Coordinate + task alignment.
    orphan_tasks = []
    tasks_without_g = []
    done_without_v = []
    for tid, has_coord, has_g, has_v, status in _tasks_with_coordinate(tasks):
        if not has_coord or not has_g:
            orphan_tasks.append(tid)
            tasks_without_g.append(tid)
        if status in {"[x]", "[f]", "[r]"} and not has_v:
            done_without_v.append(tid)
    if orphan_tasks:
        issues.append("Tasks without a North-Star-mapped G field: " + ", ".join(orphan_tasks[:10]))
    if done_without_v:
        issues.append("Done tasks without a V (verify) field: " + ", ".join(done_without_v[:10]))

    # Trace Graph checks.
    change_without_task_ns = [e.get("id", "?") for e in events
                              if e.get("type") == "change"
                              and not (e.get("task") or e.get("north_star"))]
    if change_without_task_ns:
        issues.append("Trace change events without task/north_star link: " + ", ".join(change_without_task_ns[:10]))

    done_tasks = {tid for tid, _, _, _, status in _tasks_with_coordinate(tasks) if status in {"[x]"}}
    verified_tasks = {e.get("task") for e in events if e.get("type") == "verify" and e.get("task")}
    done_without_verify_trace = sorted(done_tasks - verified_tasks)
    if done_without_verify_trace:
        issues.append("Done tasks without a verify trace event: " + ", ".join(done_without_verify_trace[:10]))

    orphan_events = [e.get("id", "?") for e in events
                     if e.get("type") in {"change", "verify", "decision", "lesson"}
                     and not (e.get("task") or e.get("north_star") or e.get("files"))]
    if orphan_events:
        issues.append("Orphan trace events (no task/north_star/file): " + ", ".join(orphan_events[:10]))

    print("# Drift Check Report\n")
    overall = "aligned" if not issues else ("major drift" if len(issues) >= 4 else "minor drift")
    print(f"Overall status: {overall}")
    print("\n## Issues")
    if issues:
        for issue in issues:
            print(f"- {issue}")
    else:
        print("- none")
    print("\n## Required fixes before more coding")
    if issues:
        print("- Update NORTH_STAR, TASKS Coordinate, HANDOFF, DECISIONS, or TRACE so current work maps to one outcome with V and P.")
        print("- Run /align, /task-contract, /trace, or /link to close the gaps.")
    else:
        print("- none")
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
