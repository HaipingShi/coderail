#!/usr/bin/env python3
"""Check trace health for a CodeRail project.

Standard library only. Returns non-zero exit code for severe problems; returns
zero with warnings otherwise. See references/TRACE_GRAPH.md for the rules.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SEVERE_PREFIX = "SEVERE"


def load_events(log_path: Path) -> list:
    if not log_path.exists():
        return []
    events = []
    with log_path.open("r", encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                events.append(json.loads(raw))
            except json.JSONDecodeError as exc:
                print(f"warning: invalid JSON on line {lineno}: {exc}", file=sys.stderr)
    return events


def check(events: list, index_path: Path, log_path: Path) -> tuple:
    """Return (severe: list[str], warnings: list[str])."""
    severe = []
    warnings = []

    if not events:
        warnings.append("TRACELOG.jsonl is empty — no trace events yet.")
        return severe, warnings

    # Map task -> statuses and task -> verify events for cross checks.
    task_status = {}
    task_verify = {}
    for ev in events:
        t = ev.get("task")
        if t:
            if ev.get("status"):
                task_status[t] = ev["status"]
            if ev.get("type") == "verify":
                task_verify.setdefault(t, []).append(ev)

    change_without_task_ns = []
    change_without_modifies = []
    verify_without_result = []
    task_without_ns = []
    open_research = []
    handoff_without_task = []
    orphans = []

    for ev in events:
        etype = ev.get("type")
        eid = ev.get("id", "?")

        if etype == "change":
            if not (ev.get("task") or ev.get("north_star")):
                change_without_task_ns.append(eid)
            if not (ev.get("modifies") or ev.get("files")):
                change_without_modifies.append(eid)
            if not (ev.get("task") or ev.get("north_star") or ev.get("files")):
                orphans.append(eid)

        if etype == "verify" and not ev.get("harness_result"):
            verify_without_result.append(eid)

        if etype == "task":
            if ev.get("task") and not ev.get("north_star"):
                task_without_ns.append(ev.get("task"))

        if etype in {"research", "attempt"}:
            status = ev.get("status")
            if status not in {"accepted", "rejected", "superseded", "done"}:
                open_research.append((eid, etype, status or "open"))

        if etype == "handoff" and not ev.get("task"):
            handoff_without_task.append(eid)

        if etype in {"change", "verify", "decision", "lesson"}:
            if not (ev.get("task") or ev.get("north_star") or ev.get("files")):
                if eid not in orphans:
                    orphans.append(eid)

    # New change/verify/handoff events should carry a coordinate.
    coord_missing = []
    for ev in events:
        if ev.get("type") in {"change", "verify", "handoff"} and not ev.get("coordinate"):
            coord_missing.append(ev.get("id", "?"))

    # Index freshness: regenerate if log mtime newer than index.
    index_stale = False
    if index_path.exists() and log_path.exists():
        if log_path.stat().st_mtime > index_path.stat().st_mtime:
            index_stale = True
    elif events and not index_path.exists():
        index_stale = True

    severe.extend(f"SEVERE: change {x} has no task or north_star" for x in change_without_task_ns)
    severe.extend(f"SEVERE: verify {x} has no harness_result" for x in verify_without_result)

    if change_without_modifies:
        warnings.append("change events without modifies/files: " + ", ".join(change_without_modifies))
    if task_without_ns:
        warnings.append("task events that cannot map to a north star: " + ", ".join(task_without_ns))
    if open_research:
        items = [f"{eid}({t}:{s})" for eid, t, s in open_research]
        warnings.append("research/attempt events with no terminal status: " + ", ".join(items))
    if handoff_without_task:
        warnings.append("handoff events with no task link: " + ", ".join(handoff_without_task))
    if orphans:
        warnings.append("orphan events (no task/north_star/file): " + ", ".join(orphans))
    if coord_missing:
        warnings.append("change/verify/handoff events without a coordinate (recommended): " + ", ".join(coord_missing))
    if index_stale:
        warnings.append("TRACE_INDEX.md is stale — rerun scripts/trace_index.py")

    return severe, warnings


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Check trace health")
    parser.add_argument("--target", default=".", help="Repository root containing docs/")
    args = parser.parse_args(argv)

    target = Path(args.target).resolve()
    docs = target / "docs"
    log_path = docs / "TRACELOG.jsonl"
    index_path = docs / "TRACE_INDEX.md"

    events = load_events(log_path)
    severe, warnings = check(events, index_path, log_path)

    print("# Trace Doctor Report\n")
    status = "healthy" if not severe and not warnings else ("unhealthy" if severe else "usable with warnings")
    print(f"Status: {status}")
    print(f"Events: {len(events)}\n")

    print("## Severe")
    if severe:
        for item in severe:
            print(f"- {item}")
    else:
        print("- none")
    print("\n## Warnings")
    if warnings:
        for item in warnings:
            print(f"- {item}")
    else:
        print("- none")

    return 1 if severe else 0


if __name__ == "__main__":
    raise SystemExit(main())
