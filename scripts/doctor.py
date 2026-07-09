#!/usr/bin/env python3
"""Governance doctor for CodeRail projects."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import coordinate_check  # noqa: E402
import trace_doctor  # noqa: E402
import contract_check  # noqa: E402
import blueprint_check  # noqa: E402
import inspect_state  # noqa: E402
import tdd_check  # noqa: E402

REQUIRED = [
    "AGENTS.md",
    "docs/NORTH_STAR.md",
    "docs/TASKS.md",
    "docs/HARNESS_SPEC.md",
    "docs/HANDOFF.md",
]
OPTIONAL = [
    "docs/CONTRACTS.md",
    "docs/CODERAIL_STATUS.md",
    "docs/BLUEPRINTS.md",
    "docs/ASSETS.md",
    "docs/DECISIONS.md",
    "docs/LESSONS.md",
    "docs/RUNLOG.md",
    "docs/TRACELOG.jsonl",
    "docs/TRACE_INDEX.md",
]


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        return ""


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return {}


def line_count(path: Path) -> int:
    text = read(path)
    return len(text.splitlines()) if text else 0


def is_historical_status(status: str) -> bool:
    return status in {"[x]", "[f]"}


def git_status(root: Path) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(root), "status", "--short"], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "git status unavailable"


def run_coordinate(root: Path):
    tasks_path = root / "docs" / "TASKS.md"
    severe, warnings, historical = [], [], []
    if not tasks_path.exists():
        return ["docs/TASKS.md missing"], [], []
    text = read(tasks_path)
    for header, body, status in coordinate_check.split_tasks(text):
        if "Example task" in header or "Task Template" in header:
            continue
        s, w = coordinate_check.check_task(header, body, status)
        if is_historical_status(status):
            historical.extend([f"Coordinate: {x}" for x in s + w])
        else:
            severe.extend(s)
            warnings.extend(w)
    return severe, warnings, historical


def run_contracts(root: Path):
    path = root / "docs" / "CONTRACTS.md"
    if not path.exists():
        return [], ["docs/CONTRACTS.md missing (optional unless draft-gated work is active)"]
    severe, warnings = [], []
    for header, body, status in contract_check.split_drafts(read(path)):
        if "Example" in header or "Short title" in header:
            continue
        s, w = contract_check.check_draft(header, body, status)
        severe.extend(s)
        warnings.extend(w)
    return severe, warnings


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Run CodeRail governance doctor")
    ap.add_argument("--target", default=".")
    args = ap.parse_args(argv)
    root = Path(args.target).resolve()
    docs = root / "docs"

    missing = [p for p in REQUIRED if not (root / p).exists()]

    ns_warn = []
    if not (docs / "NORTH_STAR.md").exists():
        ns_warn.append("docs/NORTH_STAR.md missing")
    elif line_count(docs / "NORTH_STAR.md") > 100:
        ns_warn.append(f"docs/NORTH_STAR.md is {line_count(docs / 'NORTH_STAR.md')} lines; target <= 100")

    contract_severe, contract_warn = run_contracts(root)
    coord_severe, coord_warn, historical_debt = run_coordinate(root)
    tdd_severe, tdd_warn = [], []
    if (docs / "TASKS.md").exists():
        for header, body, status in coordinate_check.split_tasks(read(docs / "TASKS.md")):
            if "Example task" in header or "Task Template" in header:
                continue
            s, w = tdd_check.check_task(header, body, status)
            if is_historical_status(status):
                historical_debt.extend([f"TDD Gate: {x}" for x in s + w])
            else:
                tdd_severe.extend(s)
                tdd_warn.extend(w)

    harness_warn = []
    if not (docs / "HARNESS_SPEC.md").exists():
        harness_warn.append("docs/HARNESS_SPEC.md missing")
    elif "Global Checks" not in read(docs / "HARNESS_SPEC.md"):
        harness_warn.append("HARNESS_SPEC.md has no Global Checks section")

    handoff_warn = []
    friction = []
    if (docs / "HANDOFF.md").exists():
        handoff_text = read(docs / "HANDOFF.md")
        if line_count(docs / "HANDOFF.md") > 120:
            friction.append("handoff too long: docs/HANDOFF.md should stay <= 120 lines; move history to TRACE_INDEX, RUNLOG, or archive")
        if "Coordinate Summary" not in handoff_text:
            handoff_warn.append("HANDOFF.md has no Coordinate Summary")
        if "Next Executable Step" not in handoff_text:
            handoff_warn.append("HANDOFF.md has no Next Executable Step")
        if "Auto Commit" not in handoff_text:
            handoff_warn.append("HANDOFF.md has no Auto Commit section")

    tasks_lines = line_count(docs / "TASKS.md")
    if tasks_lines > 1200:
        friction.append(f"TASKS too long: docs/TASKS.md is {tasks_lines} lines; compact closed chains and move detail to RUNLOG/TRACE/archive")
    elif tasks_lines > 600:
        friction.append(f"TASKS growth: docs/TASKS.md is {tasks_lines} lines; consider compact summaries for closed subtasks")

    if (docs / "TASKS.md").exists():
        for header, body, status in coordinate_check.split_tasks(read(docs / "TASKS.md")):
            if status not in {"[ ]", "[~]", "[!]"}:
                continue
            task_kind = coordinate_check.task_type(body)
            rail = coordinate_check.meta_value("Rail", body)
            inferred = coordinate_check.rail_type(header, body)
            if task_kind in coordinate_check.LIGHT_TYPES and inferred == "full":
                friction.append(f"{header.split()[0]}: docs/design-like task is running on Full Rail; consider Rail: light")
            if task_kind in coordinate_check.LIGHT_TYPES and not rail:
                friction.append(f"{header.split()[0]}: docs/design-like task has no explicit Rail; add Rail: light to avoid over-governance")

    asset_warn = []
    if not (docs / "ASSETS.md").exists():
        asset_warn.append("docs/ASSETS.md missing (optional but recommended)")

    events = trace_doctor.load_events(docs / "TRACELOG.jsonl")
    trace_severe, trace_warn = trace_doctor.check(events, docs / "TRACE_INDEX.md", docs / "TRACELOG.jsonl")
    trace_info = []
    trace_warn_filtered = []
    for item in trace_warn:
        if "TRACELOG.jsonl is empty" in item:
            trace_info.append(item)
        else:
            trace_warn_filtered.append(item)
    trace_warn = trace_warn_filtered

    inspect_warn = []
    if not (docs / "CODERAIL_STATUS.md").exists():
        inspect_warn.append("docs/CODERAIL_STATUS.md missing; run scripts/inspect_state.py")
    else:
        status_text = read(docs / "CODERAIL_STATUS.md")
        if "Generated by `scripts/inspect_state.py`" not in status_text:
            inspect_warn.append("CODERAIL_STATUS.md does not look generated")

    entry_warn = []
    agents = read(root / "AGENTS.md")
    if not agents:
        entry_warn.append("AGENTS.md missing")
    else:
        for phrase in ["CodeRail Coordinate", "done gate", "Coordinate Contract Draft", "Runtime State Inspect", "TDD Gate", "Closeout"]:
            if phrase not in agents:
                entry_warn.append(f"AGENTS.md does not mention {phrase}")

    blueprint = blueprint_check.check_project(root)
    blueprint_severe = blueprint["severe"]
    blueprint_warn = blueprint["warnings"]
    blueprint_info = blueprint["info"]

    ci_warn = []
    package = read_json(root / "package.json")
    scripts = package.get("scripts", {}) if isinstance(package.get("scripts", {}), dict) else {}
    if scripts and any(name in scripts for name in ["test", "build", "lint", "typecheck"]) and "ci" not in scripts:
        ci_warn.append("package.json has check scripts but no ci script")
    workflows = root / ".github" / "workflows"
    if workflows.exists() and not list(workflows.glob("*.yml")) and not list(workflows.glob("*.yaml")):
        ci_warn.append(".github/workflows exists but has no workflow files")

    severe = contract_severe + coord_severe + tdd_severe + trace_severe + blueprint_severe
    warnings = ns_warn + contract_warn + coord_warn + tdd_warn + harness_warn + handoff_warn + asset_warn + trace_warn + inspect_warn + entry_warn + blueprint_warn + ci_warn
    if len(warnings) > 12:
        friction.append(f"done/doctor warning noise: {len(warnings)} warnings; classify current blockers separately from historical debt")
    if historical_debt and not (missing or severe):
        friction.append("historical debt present but separated from current blockers")
    status = "unhealthy" if (missing or severe) else ("usable with warnings" if warnings else "healthy")

    print("# Governance Doctor Report\n")
    print(f"Status: {status}\n")
    print("## Missing required files")
    print("- none" if not missing else "\n".join(f"- {x}" for x in missing))

    def section(title, sev, warn, info=None):
        print(f"\n## {title}")
        shown = False
        for x in sev:
            print(f"- SEVERE: {x}")
            shown = True
        for x in warn:
            print(f"- {x}")
            shown = True
        for x in info or []:
            print(f"- info: {x}")
            shown = True
        if not shown:
            print("- ok")

    section("North Star", [], ns_warn)
    section("Contract Drafts", contract_severe, contract_warn)
    section("Coordinate", coord_severe, coord_warn)
    section("TDD Gate", tdd_severe, tdd_warn)
    section("Harness / Done Gate", [], harness_warn)
    section("Handoff", [], handoff_warn)
    section("Asset Boundary", [], asset_warn)
    section("Trace Graph", trace_severe, trace_warn, trace_info)
    section("Runtime State Inspect", [], inspect_warn)
    section("Entry file", [], entry_warn)

    section("Blueprint Gate", blueprint_severe, blueprint_warn, blueprint_info)
    section("CI Gate", [], ci_warn)

    print("\n## Governance Friction")
    print("- Goal: reduce high-production/high-entanglement friction without weakening scope, verification, trace, or done gates.")
    if not friction:
        print("- none")
    else:
        for item in friction:
            print(f"- optimization opportunity: {item}")

    print("\n## Historical Debt")
    if not historical_debt:
        print("- none")
    else:
        for item in historical_debt[:30]:
            print(f"- historical debt: {item}")
        if len(historical_debt) > 30:
            print(f"- ... {len(historical_debt) - 30} more")

    print("\n## Current Blocker Classification")
    if missing or severe:
        for item in missing:
            print(f"- must-fix blocker: missing required file {item}")
        for item in severe:
            print(f"- must-fix blocker: {item}")
    else:
        print("- none")
    if warnings:
        for item in warnings[:30]:
            print(f"- warning: {item}")
        if len(warnings) > 30:
            print(f"- ... {len(warnings) - 30} more warnings")
    if friction:
        for item in friction[:20]:
            print(f"- optimization opportunity: {item}")

    print("\n## Optional files present")
    for item in OPTIONAL:
        print(f"- {item}: {'yes' if (root / item).exists() else 'no'}")

    print("\n## Git status")
    print(git_status(root) or "clean")

    print("\n## Suggested fixes")
    fixes = []
    if ns_warn:
        fixes.append("/align — realign NORTH_STAR.md")
    if contract_severe or contract_warn:
        fixes.append("/contract-draft — fix or accept/reject draft contracts")
    if coord_severe or coord_warn:
        fixes.append("/task-contract — fill missing coordinate fields")
    if tdd_severe or tdd_warn:
        fixes.append("/tdd-gate — record Red-Green-Refactor evidence or an explicit waiver")
    if trace_severe or trace_warn:
        fixes.append("/trace or /link — fix trace gaps; then run trace_index.py")
    if inspect_warn:
        fixes.append("/inspect — refresh CODERAIL_STATUS.md")
    if handoff_warn:
        fixes.append("/handoff — refresh Coordinate Summary")
    if blueprint_severe or blueprint_warn:
        fixes.append("/blueprint — update docs/BLUEPRINTS.md and required architecture diagrams")
    if ci_warn:
        fixes.append("/ci-gate — add or run a repo-local CI script for non-decision checks")
    if friction:
        fixes.append("/handoff or TASKS compact — reduce governance friction without relaxing current blockers")
    if not fixes:
        fixes.append("none — project is healthy")
    for item in fixes:
        print(f"- {item}")

    return 1 if status == "unhealthy" else 0


if __name__ == "__main__":
    raise SystemExit(main())
