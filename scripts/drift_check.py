#!/usr/bin/env python3
"""Lightweight drift check."""
from __future__ import annotations

import argparse
import re
from pathlib import Path


def read(path):
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


def recommendation_issues(north_star: str) -> list[str]:
    contract = section(north_star, "Recommendation Contract")
    if not contract:
        return []

    issues = []
    mode = field_value(contract, "Mode").lower()
    mission = field_value(contract, "Mission Status").lower()
    current_slice = field_value(contract, "Current Slice Status").lower()
    next_candidate = field_value(contract, "Next Candidate")
    active_task = field_value(section(north_star, "Current Slice"), "Active Task")

    required = {
        "Mode": mode,
        "Mission Status": mission,
        "Current Slice Status": current_slice,
        "Next Candidate": next_candidate,
        "Human Gate": field_value(contract, "Human Gate"),
    }
    for label, value in required.items():
        if not value:
            issues.append(f"Recommendation Contract lacks {label}")

    if mission == "complete" and next_candidate.lower() != "none":
        issues.append("Mission complete requires Next Candidate: none")
    if current_slice == "active" and active_task.lower() in {"", "none"}:
        issues.append("Current Slice active requires a non-empty Active Task")
    if mission == "active" and current_slice == "complete" and mode == "auto-draft" and not next_candidate:
        issues.append("auto-draft continuation requires Next Candidate")
    return issues


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default=".")
    args = parser.parse_args(argv)
    root = Path(args.target).resolve()
    docs = root / "docs"
    issues = []
    north_star = read(docs / "NORTH_STAR.md")
    tasks = read(docs / "TASKS.md")
    handoff = read(docs / "HANDOFF.md")
    if "Outcome" not in north_star or "Current Slice" not in north_star:
        issues.append("NORTH_STAR.md lacks Outcome or Current Slice")
    if "CodeRail Coordinate" not in tasks:
        issues.append("TASKS.md lacks CodeRail Coordinate")
    if "Status: [x]" in tasks and "Harness result:" not in tasks:
        issues.append("done task may lack harness result")
    if handoff and "Coordinate Summary" not in handoff:
        issues.append("HANDOFF.md lacks Coordinate Summary")
    issues.extend(recommendation_issues(north_star))
    print("# Drift Check Report\n")
    print("Status: " + ("aligned" if not issues else "minor drift"))
    print("\n## Findings")
    print("- none" if not issues else "\n".join(f"- {item}" for item in issues))
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
