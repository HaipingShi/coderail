#!/usr/bin/env python3
"""Governance doctor for CodeRail projects."""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

REQUIRED = [
    "AGENTS.md",
    "docs/NORTH_STAR.md",
    "docs/TASKS.md",
    "docs/HARNESS_SPEC.md",
    "docs/HANDOFF.md",
]
OPTIONAL = [
    "docs/ASSETS.md",
    "docs/DECISIONS.md",
    "docs/LESSONS.md",
    "docs/RUNLOG.md",
]


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        return ""


def line_count(path: Path) -> int:
    text = read(path)
    return 0 if not text else len(text.splitlines())


def git_status(root: Path) -> str:
    try:
        out = subprocess.check_output(["git", "-C", str(root), "status", "--short"], text=True, stderr=subprocess.DEVNULL)
        return out.strip()
    except Exception:
        return "git status unavailable"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default=".")
    args = parser.parse_args()
    root = Path(args.target).resolve()

    missing = [p for p in REQUIRED if not (root / p).exists()]
    warnings = []

    ns = root / "docs/NORTH_STAR.md"
    if ns.exists() and line_count(ns) > 100:
        warnings.append(f"docs/NORTH_STAR.md is {line_count(ns)} lines; target <= 100")
    handoff = root / "docs/HANDOFF.md"
    if handoff.exists() and line_count(handoff) > 120:
        warnings.append(f"docs/HANDOFF.md is {line_count(handoff)} lines; target <= 120")

    tasks_text = read(root / "docs/TASKS.md")
    if tasks_text:
        task_headers = re.findall(r"^##\s+([A-Z]-\d+[^\n]*)", tasks_text, flags=re.M)
        if task_headers and "North-Star Link" not in tasks_text:
            warnings.append("TASKS.md has task headers but no North-Star Link sections")
        if task_headers and "Harness:" not in tasks_text:
            warnings.append("TASKS.md has task headers but no Harness sections")
        if re.search(r"Status:\s*\[x\]", tasks_text) and "Harness result:" not in tasks_text:
            warnings.append("A done task may be missing Harness result")

    agents = read(root / "AGENTS.md")
    if agents and "North-Star" not in agents and "NORTH_STAR" not in agents:
        warnings.append("AGENTS.md does not mention North-Star Kernel")

    status = "healthy"
    if missing:
        status = "unhealthy"
    elif warnings:
        status = "usable with warnings"

    print("# Governance Doctor Report\n")
    print(f"Status: {status}\n")
    print("## Missing required files")
    if missing:
        for item in missing:
            print(f"- {item}")
    else:
        print("- none")
    print("\n## Warnings")
    if warnings:
        for item in warnings:
            print(f"- {item}")
    else:
        print("- none")
    print("\n## Optional files present")
    for item in OPTIONAL:
        print(f"- {item}: {'yes' if (root / item).exists() else 'no'}")
    print("\n## Git status")
    gs = git_status(root)
    print(gs if gs else "clean")
    return 0 if status != "unhealthy" else 1

if __name__ == "__main__":
    raise SystemExit(main())
