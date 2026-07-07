#!/usr/bin/env python3
"""Governance doctor for CodeRail projects.

Integrates coordinate_check and trace_doctor and reports seven sections:
North Star, Coordinate, Task Contract, Harness, Handoff, Asset Boundary,
Trace Graph. Standard library only.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
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
    "docs/TRACELOG.jsonl",
    "docs/TRACE_INDEX.md",
]

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import coordinate_check  # noqa: E402
import trace_doctor  # noqa: E402

# blueprint_check is optional in spirit (non-blocking), but we import it
# unconditionally to surface the awareness section in every doctor run.
import blueprint_check  # noqa: E402


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
        out = subprocess.check_output(
            ["git", "-C", str(root), "status", "--short"],
            text=True, stderr=subprocess.DEVNULL,
        )
        return out.strip()
    except Exception:
        return "git status unavailable"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default=".")
    args = parser.parse_args(argv)
    root = Path(args.target).resolve()

    missing = [p for p in REQUIRED if not (root / p).exists()]

    # --- North Star ---
    ns_warnings = []
    ns = root / "docs/NORTH_STAR.md"
    if ns.exists() and line_count(ns) > 100:
        ns_warnings.append(f"docs/NORTH_STAR.md is {line_count(ns)} lines; target <= 100")
    if not ns.exists():
        ns_warnings.append("docs/NORTH_STAR.md missing")

    # --- Task Contract + Coordinate (via coordinate_check) ---
    coord_severe = []
    coord_warnings = []
    tasks_path = root / "docs/TASKS.md"
    if tasks_path.exists():
        text = tasks_path.read_text(encoding="utf-8", errors="ignore")
        for header, body, status in coordinate_check.split_tasks(text):
            s, w = coordinate_check.check_task(header, body, status)
            coord_severe.extend(s)
            coord_warnings.extend(w)
        if "CodeRail Coordinate" not in text:
            coord_warnings.append("TASKS.md has no CodeRail Coordinate block")
        if re.search(r"Status:\s*\[x\]", text) and "Harness result:" not in text:
            coord_warnings.append("A done task may be missing Harness result")
    else:
        coord_severe.append("docs/TASKS.md missing")

    # --- Harness ---
    harness_warnings = []
    harness_path = root / "docs/HARNESS_SPEC.md"
    if not harness_path.exists():
        harness_warnings.append("docs/HARNESS_SPEC.md missing")
    elif "Global Checks" not in read(harness_path):
        harness_warnings.append("HARNESS_SPEC.md has no Global Checks section")

    # --- Handoff ---
    handoff_warnings = []
    handoff = root / "docs/HANDOFF.md"
    if handoff.exists() and line_count(handoff) > 120:
        handoff_warnings.append(f"docs/HANDOFF.md is {line_count(handoff)} lines; target <= 120")
    if handoff.exists() and "Coordinate Summary" not in read(handoff):
        handoff_warnings.append("HANDOFF.md has no Coordinate Summary")

    # --- Asset Boundary ---
    asset_warnings = []
    assets_path = root / "docs/ASSETS.md"
    if not assets_path.exists():
        asset_warnings.append("docs/ASSETS.md missing (optional but recommended)")

    # --- Trace Graph (via trace_doctor) ---
    log_path = root / "docs/TRACELOG.jsonl"
    index_path = root / "docs/TRACE_INDEX.md"
    events = trace_doctor.load_events(log_path)
    trace_severe, trace_warnings = trace_doctor.check(events, index_path, log_path)

    agents = read(root / "AGENTS.md")
    agents_warnings = []
    if not agents:
        agents_warnings.append("AGENTS.md missing")
    elif "North-Star" not in agents and "NORTH_STAR" not in agents:
        agents_warnings.append("AGENTS.md does not mention North-Star Kernel")
    if agents and "CodeRail Coordinate" not in agents:
        agents_warnings.append("AGENTS.md does not mention CodeRail Coordinate")

    all_warnings = (
        ns_warnings + coord_warnings + harness_warnings + handoff_warnings
        + asset_warnings + trace_warnings + agents_warnings
    )
    severe = coord_severe + trace_severe

    status = "unhealthy" if (missing or severe) else ("usable with warnings" if all_warnings else "healthy")

    print("# Governance Doctor Report\n")
    print(f"Status: {status}\n")
    print("## Missing required files")
    if missing:
        for item in missing:
            print(f"- {item}")
    else:
        print("- none")

    def section(title, severe_items, warn_items):
        print(f"\n## {title}")
        shown = False
        if severe_items:
            for item in severe_items:
                print(f"- SEVERE: {item}")
            shown = True
        if warn_items:
            for item in warn_items:
                print(f"- {item}")
            shown = True
        if not shown:
            print("- ok")

    section("North Star", [], ns_warnings)
    section("Coordinate", coord_severe, coord_warnings)
    section("Task Contract", [], [])
    section("Harness", [], harness_warnings)
    section("Handoff", [], handoff_warnings)
    section("Asset Boundary", [], asset_warnings)
    section("Trace Graph", trace_severe, trace_warnings)
    section("Entry file (AGENTS.md)", [], agents_warnings)

    # Blueprint Awareness is educational, non-blocking, and multi-line — it does
    # NOT go through section() (which is severe/warning二元) and never affects
    # exit code or status. It only surfaces diagrams the project might benefit from.
    print("\n## Blueprint Awareness")
    print(blueprint_check.run_check(root))

    print("\n## Optional files present")
    for item in OPTIONAL:
        print(f"- {item}: {'yes' if (root / item).exists() else 'no'}")

    print("\n## Git status")
    gs = git_status(root)
    print(gs if gs else "clean")

    print("\n## Suggested fixes")
    suggestions = []
    if ns_warnings:
        suggestions.append("/align — realign NORTH_STAR.md")
    if coord_severe or coord_warnings:
        suggestions.append("/task-contract — fill missing CodeRail Coordinate fields")
    if trace_severe or trace_warnings:
        suggestions.append("/trace or /link — fix trace gaps and regenerate TRACE_INDEX.md")
        suggestions.append("python3 scripts/trace_index.py --target .")
    if any(warnings for warnings in [handoff_warnings]):
        suggestions.append("/handoff — refresh Coordinate Summary")
    if not suggestions:
        suggestions.append("none — project is healthy")
    for s in suggestions:
        print(f"- {s}")

    return 1 if status == "unhealthy" else 0


if __name__ == "__main__":
    raise SystemExit(main())
