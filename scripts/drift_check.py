#!/usr/bin/env python3
"""Simple static drift check for CodeRail docs."""
from __future__ import annotations

import argparse
import re
from pathlib import Path


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        return ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default=".")
    args = parser.parse_args()
    root = Path(args.target).resolve()

    north = read(root / "docs/NORTH_STAR.md")
    tasks = read(root / "docs/TASKS.md")
    handoff = read(root / "docs/HANDOFF.md")
    decisions = read(root / "docs/DECISIONS.md")

    issues = []
    if not north.strip():
        issues.append("Missing or empty docs/NORTH_STAR.md")
    if tasks and "North-Star Link" not in tasks:
        issues.append("TASKS.md does not contain North-Star Link")
    if handoff and len(handoff.splitlines()) > 120:
        issues.append("HANDOFF.md is over 120 lines and may be acting as a log")
    if decisions and "Current Bet" in decisions and "Current Bet" not in north:
        issues.append("DECISIONS.md may change current bet but NORTH_STAR does not mention it")

    orphan_tasks = []
    current = None
    has_link = False
    for line in tasks.splitlines():
        m = re.match(r"##\s+([A-Z]-\d+.*)", line)
        if m:
            if current and not has_link:
                orphan_tasks.append(current)
            current = m.group(1)
            has_link = False
        if "North-Star Link" in line:
            has_link = True
    if current and not has_link:
        orphan_tasks.append(current)
    if orphan_tasks:
        issues.append("Tasks missing North-Star Link: " + ", ".join(orphan_tasks[:10]))

    print("# Drift Check Report\n")
    print("Overall status: " + ("aligned" if not issues else "minor drift"))
    print("\n## Issues")
    if issues:
        for issue in issues:
            print(f"- {issue}")
    else:
        print("- none")
    print("\n## Required fixes before more coding")
    if issues:
        print("- Update NORTH_STAR, TASKS, HANDOFF, or DECISIONS so current work maps to a single outcome.")
    else:
        print("- none")
    return 0 if not issues else 1

if __name__ == "__main__":
    raise SystemExit(main())
