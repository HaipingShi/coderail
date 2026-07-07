#!/usr/bin/env python3
"""End-to-end test for the CodeRail plugin (v0.4).

Verifies the full K0-K7 stack against a real demo repo with real code and a
real pytest harness:

  K0 North-Star Kernel
  K1 CodeRail Coordinate (G/T/S/V/X/P)
  K2 Task Contract
  K3 Harness Gate
  K4 Tool-Native Enforcement (out of scope here)
  K5 Handoff (out of scope here)
  K6 Asset Boundary (out of scope here)
  K7 Trace Graph Kernel

Pipeline (all steps run for real against the filesystem):
  1. (Re)create a clean demo repo at ./demo-app
  2. Add a tiny real module + pytest (the "governed" code)
  3. Install CodeRail via scripts/init_project.py --mode standard
  4. Fill NORTH_STAR.md and TASKS.md as a user would, using the CodeRail
     Coordinate format (align -> task-contract)
  5. Assert all governance files exist, including TRACELOG.jsonl + TRACE_INDEX.md
  6. Run doctor.py -> exit 0, Coordinate + Trace Graph sections present
     (status is "usable with warnings" because the trace log is still empty)
  7. trace_event: append a task event (with coordinate) -> TRACELOG.jsonl grows
  8. trace_event: append a change event (modifies src/calc.py)
  9. trace_event: append a verify event (harness_result passed)
 10. trace_index: regenerate TRACE_INDEX.md -> contains By Task, ### T-001,
     and the coordinate summary (G=/T=/V=/P=)
 11. trace_doctor -> expect healthy, exit 0, no severe findings
 12. Run drift_check.py -> expect aligned, exit 0 (done task now has verify trace)
 13. coordinate_check -> T-001 passes (done task has V and P), exit 0
 14. Run the demo's own pytest -> expect pass (harness baseline)
 15. Run doctor.py -> expect healthy now that the trace log is populated
 16. NEGATIVE: append a task with a missing G field -> coordinate_check AND
     drift_check must both catch it (proves the coordinate gate governs)
 17. Restore clean TASKS.md and final recheck (doctor + drift + coord + trace_doctor)

Exit code 0 iff every assertion held.
"""
from __future__ import annotations

import atexit
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Force the parent process's own stdout/stderr to UTF-8 too. On a Chinese
# Windows console the default can be cp936/GBK, which crashes on the em-dash
# ('—') and '≠' characters this script prints. PYTHONUTF8 in the env only
# affects child processes; this reconfigures our own streams.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

HERE = Path(__file__).resolve().parent
# Script lives in <coderail>/e2e/, so the plugin root is one level up.
CODERAIL = HERE.parent
# DEMO is assigned in main() to a temp dir so the test never pollutes the
# coderail git repo. Module-level placeholder keeps helpers referencing DEMO.
DEMO = None

CALC = '''"""Tiny module under governance."""


def add(a: int, b: int) -> int:
    return a + b


def divide(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("division by zero")
    return a / b
'''

TEST_CALC = '''from src.calc import add, divide

import pytest


def test_add():
    assert add(2, 3) == 5


def test_divide():
    assert divide(10, 2) == 5.0


def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(1, 0)
'''

PYTEST_INI = """[pytest]
pythonpath = .
"""

NORTH_STAR = """# North Star

Status: active
Last reviewed: 2026-07-06
Owner: e2e

## 1. Outcome

- Ship a correct calculator module with a green test suite.

## 2. User / Operator Intent

- Callers can add and divide integers safely.

## 3. Current Bet

- Pure-Python stdlib module, no dependencies.

## 4. Non-Goals

- No GUI, no persistence, no async.

## 5. Invariants

- divide() raises ValueError on zero denominator.
- Public API stays limited to add() and divide().

## 6. Current Slice

Milestone: M0 core calc
Execution Batch: B-001
Active Task: T-001

## 6b. Coordinate Rule

Every active task must map to this North Star through its G field.

## 7. Known Unknowns

- Whether floats will be needed later.

## 8. Decision Debt

- none

## 9. Stop Triggers

- A new dependency is introduced.
- A task cannot be mapped to a North Star (no G).
- A code change has no task link.

## 10. Drift Signals

- TASKS contains work not tied to the calc outcome.
- A task has T/S/V but no meaningful G.
"""

# v0.4 task format: CodeRail Coordinate (G/T/S/V/X/P) is the core.
# T-001 is [x] done, so V must have harness and P must include TASKS + TRACE.
TASKS = """# Tasks

## Status legend

- `[ ]` todo
- `[~]` doing
- `[!]` blocked
- `[x]` done
- `[f]` failed
- `[r]` reopened

## T-001 Implement calc.add and calc.divide

Status: [x]
Type: feature
Priority: P1
Owner: e2e
Branch: main

### CodeRail Coordinate

G — Goal:
- North Star: NS-001
- Outcome served: Ship a correct calculator module with a green test suite.

T — Task:
- Implement add() and divide() with a zero-denominator guard.

S — Scope:
- Allowed:
  - src/calc.py
  - tests/test_calc.py
- Forbidden:
  - docs/**

V — Verify:
- Harness:
  - python -m pytest -q
- Manual acceptance:
  - none needed

X — Stop:
- A new dependency is introduced.
- A broader math library is requested.

P — Persist:
- TASKS: T-001
- HANDOFF: H0 only
- DECISIONS: none
- LESSONS: none
- ASSETS: none
- TRACE: task, change, verify

### Task Contract

Depends on:
- none

Blocks:
- later UI work

Acceptance:
- [x] add() returns the sum
- [x] divide() returns the quotient
- [x] divide() raises ValueError on zero

### Critical Check

- [x] The task maps to `docs/NORTH_STAR.md` through its G field.
- [x] The request level was not collapsed incorrectly into implementation.
- [x] Changes stayed inside S (Allowed) and respected S (Forbidden).
- [x] No raw material or working note was treated as a permanent asset.
- [x] New dependency, API, schema, or persistent state was recorded.
- [x] V can verify the change, or manual acceptance is explicit.
- [x] P was synced (at least TASKS and TRACE).

### Completion

Completed at: 2026-07-06
Commit: HEAD
Harness result: 3 passed
Handoff level: H0
Trace: TR-e2e-task, TR-e2e-change, TR-e2e-verify
Notes: baseline module done
"""

# A task with a missing G field, used for the negative test in step 9.
ORPHAN_TASK = """
## T-002 Sneaky refactor with no goal

Status: [ ]
Type: refactor

### CodeRail Coordinate

G — Goal:
- 

T — Task:
- Refactor everything for no stated reason.

S — Scope:
- Allowed:
  - src/**
- Forbidden:
  - none

V — Verify:
- python -m pytest -q

X — Stop:
- none

P — Persist:
- TASKS
"""


def run(cmd: list[str], cwd: Path, *, check: bool = True) -> subprocess.CompletedProcess:
    # Force UTF-8 on BOTH sides: encoding= tells the parent how to decode the
    # captured stdout/stderr (Windows defaults to cp936/GBK and crashes on em-dash,
    # '≠', etc.); PYTHONUTF8=1 makes the child Python print UTF-8 too.
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True,
                          encoding="utf-8", errors="replace",
                          env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"})


def step(n: int, msg: str) -> None:
    print(f"\n[{n}] {msg}")


def assert_true(cond: bool, msg: str) -> None:
    print(f"    {'PASS' if cond else 'FAIL'}: {msg}")
    if not cond:
        print("\n*** E2E TEST FAILED ***")
        sys.exit(1)


def trace_event(args: list[str]) -> subprocess.CompletedProcess:
    """Run trace_event.py against the demo repo."""
    return run([sys.executable, str(CODERAIL / "scripts/trace_event.py"),
                "--target", str(DEMO)] + args, cwd=DEMO)


def main() -> int:
    global DEMO
    # Use a temp dir so the demo never pollutes the coderail git repo.
    DEMO = Path(tempfile.mkdtemp(prefix="coderail-e2e-"))
    atexit.register(lambda: shutil.rmtree(DEMO, ignore_errors=True))

    # 1. clean demo repo
    step(1, f"(Re)create clean demo at {DEMO}")
    (DEMO / "src").mkdir(parents=True)
    (DEMO / "tests").mkdir(parents=True)
    run(["git", "init", "-b", "main"], cwd=DEMO, check=False)
    assert_true(DEMO.exists(), "demo-app created")

    # 2. real module + tests
    step(2, "Write governed code (src/calc.py, tests/test_calc.py)")
    (DEMO / "src/calc.py").write_text(CALC, encoding="utf-8")
    (DEMO / "tests/test_calc.py").write_text(TEST_CALC, encoding="utf-8")
    (DEMO / "pytest.ini").write_text(PYTEST_INI, encoding="utf-8")

    # 3. install plugin
    step(3, "Install CodeRail via init_project.py --mode standard")
    r = run([sys.executable, str(CODERAIL / "scripts/init_project.py"),
             "--target", str(DEMO), "--mode", "standard"], cwd=HERE)
    print("    " + r.stdout.replace("\n", "\n    ").rstrip())
    assert_true(r.returncode == 0, "init_project exit 0")
    assert_true((DEMO / "AGENTS.md").exists(), "AGENTS.md written")
    assert_true((DEMO / "CLAUDE.md").exists(), "CLAUDE.md written")

    # 4. user fills NORTH_STAR + TASKS (CodeRail Coordinate format)
    step(4, "Fill NORTH_STAR.md and TASKS.md (align -> task-contract, v0.4 format)")
    (DEMO / "docs/NORTH_STAR.md").write_text(NORTH_STAR, encoding="utf-8")
    (DEMO / "docs/TASKS.md").write_text(TASKS, encoding="utf-8")

    # 5. all required files present (incl. v0.4 trace files)
    step(5, "Assert required governance files exist (incl. TRACELOG.jsonl, TRACE_INDEX.md)")
    required = ["AGENTS.md", "docs/NORTH_STAR.md", "docs/TASKS.md",
                "docs/HARNESS_SPEC.md", "docs/HANDOFF.md", "docs/ASSETS.md",
                "docs/DECISIONS.md", "docs/LESSONS.md", "docs/RUNLOG.md",
                "docs/TRACELOG.jsonl", "docs/TRACE_INDEX.md"]
    for rel in required:
        assert_true((DEMO / rel).exists(), f"{rel} exists")

    # 6. doctor -> exit 0, 7 sections present (Coordinate + Trace Graph).
    # At this point TRACELOG.jsonl is still empty, so status is "usable with
    # warnings" rather than "healthy" — that is correct, not a failure.
    step(6, "Run doctor.py -> expect exit 0, Coordinate + Trace Graph sections present")
    r = run([sys.executable, str(CODERAIL / "scripts/doctor.py"),
             "--target", str(DEMO)], cwd=DEMO)
    print("    " + r.stdout.replace("\n", "\n    ").rstrip())
    assert_true(r.returncode == 0, "doctor exit 0")
    assert_true("Status:" in r.stdout, "doctor reports a status")
    assert_true("unhealthy" not in r.stdout, "doctor not unhealthy")
    assert_true("## Coordinate" in r.stdout, "doctor has Coordinate section")
    assert_true("## Trace Graph" in r.stdout, "doctor has Trace Graph section")
    assert_true("- none" in r.stdout.split("## Missing required files")[1]
                .split("##")[0], "no missing required files")

    # --- Record the work in the trace graph BEFORE auditing it. ---
    # The drift_check "done task without verify trace" rule only makes sense
    # once the trace log exists, so we populate the trace first.

    # 7. trace_event: task event with coordinate
    step(7, "trace_event: append task event with CodeRail Coordinate")
    r = trace_event(["--type", "task", "--summary", "Implement calc.add and calc.divide",
                     "--task", "T-001", "--north-star", "NS-001", "--serves", "NS-001",
                     "--goal", "Ship a correct calculator module with a green test suite.",
                     "--coordinate-task", "Implement add() and divide() with a zero-denominator guard.",
                     "--scope-allowed", "src/calc.py,tests/test_calc.py",
                     "--scope-forbidden", "docs/**",
                     "--verify", "python -m pytest -q",
                     "--stop", "A new dependency is introduced.",
                     "--persist", "TASKS,TRACE"])
    print("    " + r.stdout.replace("\n", "\n    ").rstrip())
    assert_true(r.returncode == 0, "trace_event task exit 0")
    log_text = (DEMO / "docs/TRACELOG.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert_true(len(log_text) >= 1, "TRACELOG.jsonl has at least one event")
    last = json.loads(log_text[-1])
    assert_true(last["type"] == "task", "last event is a task event")
    assert_true("coordinate" in last and "goal" in last["coordinate"],
                "task event carries a coordinate with goal")

    # 8. trace_event: change event (modifies src/calc.py)
    step(8, "trace_event: append change event (modifies src/calc.py)")
    r = trace_event(["--type", "change", "--summary", "Implement add and divide",
                     "--task", "T-001", "--north-star", "NS-001",
                     "--files", "src/calc.py", "--implements", "T-001",
                     "--modifies", "src/calc.py",
                     "--goal", "Ship a correct calculator module with a green test suite.",
                     "--verify", "python -m pytest -q", "--persist", "TASKS,TRACE"])
    print("    " + r.stdout.replace("\n", "\n    ").rstrip())
    assert_true(r.returncode == 0, "trace_event change exit 0")

    # 9. trace_event: verify event (harness_result passed)
    step(9, "trace_event: append verify event (harness_result passed)")
    r = trace_event(["--type", "verify", "--summary", "pytest 3 passed",
                     "--task", "T-001", "--north-star", "NS-001",
                     "--harness-command", "python -m pytest -q", "--harness-result", "passed",
                     "--validated-by", "T-001",
                     "--goal", "Ship a correct calculator module with a green test suite.",
                     "--verify", "python -m pytest -q", "--persist", "TASKS,TRACE"])
    print("    " + r.stdout.replace("\n", "\n    ").rstrip())
    assert_true(r.returncode == 0, "trace_event verify exit 0")

    # 10. trace_index: regenerate and check sections + coordinate summary
    step(10, "trace_index: regenerate TRACE_INDEX.md and verify sections + coordinate summary")
    r = run([sys.executable, str(CODERAIL / "scripts/trace_index.py"),
             "--target", str(DEMO)], cwd=DEMO)
    print("    " + r.stdout.replace("\n", "\n    ").rstrip())
    assert_true(r.returncode == 0, "trace_index exit 0")
    index_text = (DEMO / "docs/TRACE_INDEX.md").read_text(encoding="utf-8")
    assert_true("## By Task" in index_text, "index has By Task section")
    assert_true("### T-001" in index_text, "index groups events under T-001")
    assert_true("`src/calc.py`" in index_text, "index lists src/calc.py under By File")
    assert_true("NS-001" in index_text, "index references the North Star")
    assert_true("G=" in index_text and "P=" in index_text,
                "index renders coordinate summary (G=/P=)")

    # 11. trace_doctor -> healthy, no severe (trace log now populated)
    step(11, "trace_doctor -> expect healthy / exit 0 / no severe")
    r = run([sys.executable, str(CODERAIL / "scripts/trace_doctor.py"),
             "--target", str(DEMO)], cwd=DEMO)
    print("    " + r.stdout.replace("\n", "\n    ").rstrip())
    assert_true(r.returncode == 0, "trace_doctor exit 0")
    assert_true("Status: healthy" in r.stdout, "trace_doctor reports healthy")
    severe_section = r.stdout.split("## Severe")[1].split("##")[0]
    assert_true("- none" in severe_section, "trace_doctor reports no severe findings")

    # --- Now audit the fully-recorded state. ---

    # 12. drift_check -> aligned (done task T-001 now has a verify trace event)
    step(12, "Run drift_check.py -> expect aligned / exit 0")
    r = run([sys.executable, str(CODERAIL / "scripts/drift_check.py"),
             "--target", str(DEMO)], cwd=DEMO)
    print("    " + r.stdout.replace("\n", "\n    ").rstrip())
    assert_true(r.returncode == 0, "drift_check exit 0")
    assert_true("aligned" in r.stdout, "drift_check reports aligned")

    # 13. coordinate_check -> T-001 passes (done task with V + P)
    step(13, "coordinate_check -> T-001 passes (done task has V and P)")
    r = run([sys.executable, str(CODERAIL / "scripts/coordinate_check.py"),
             "--target", str(DEMO)], cwd=DEMO)
    print("    " + r.stdout.replace("\n", "\n    ").rstrip())
    assert_true(r.returncode == 0, "coordinate_check exit 0 (T-001 fully valid)")
    assert_true("Status: healthy" in r.stdout, "coordinate_check reports healthy")

    # 14. demo's own pytest (harness baseline — CodeRail does not break the project)
    step(14, "Run demo's own pytest (harness baseline)")
    r = run([sys.executable, "-m", "pytest", "-q"], cwd=DEMO)
    print("    " + r.stdout.replace("\n", "\n    ").rstrip())
    assert_true(r.returncode == 0, "demo pytest passes")
    assert_true("3 passed" in r.stdout, "3 tests passed")

    # 15. doctor -> now healthy (trace populated, coordinate valid)
    step(15, "Run doctor.py -> expect healthy / exit 0")
    r = run([sys.executable, str(CODERAIL / "scripts/doctor.py"),
             "--target", str(DEMO)], cwd=DEMO)
    print("    " + r.stdout.replace("\n", "\n    ").rstrip())
    assert_true(r.returncode == 0, "doctor exit 0")
    assert_true("Status: healthy" in r.stdout, "doctor reports healthy (trace populated)")

    # 16. NEGATIVE: append a task with no G field -> coordinate_check + drift_check catch it
    step(16, "NEGATIVE: append task with missing G -> coordinate_check + drift_check must fail")
    with open(DEMO / "docs/TASKS.md", "a", encoding="utf-8") as f:
        f.write(ORPHAN_TASK)
    r = run([sys.executable, str(CODERAIL / "scripts/coordinate_check.py"),
             "--target", str(DEMO)], cwd=DEMO)
    print("    [coordinate_check]\n    " + r.stdout.replace("\n", "\n    ").rstrip())
    assert_true(r.returncode == 1, "coordinate_check exit 1 (missing G detected)")
    assert_true("T-002" in r.stdout and "G (Goal) missing" in r.stdout,
                "coordinate_check names T-002 missing G")
    r = run([sys.executable, str(CODERAIL / "scripts/drift_check.py"),
             "--target", str(DEMO)], cwd=DEMO)
    print("    [drift_check]\n    " + r.stdout.replace("\n", "\n    ").rstrip())
    assert_true(r.returncode == 1, "drift_check exit 1 (drift detected)")
    assert_true("T-002" in r.stdout, "drift_check names T-002")

    # 17. restore clean TASKS.md and final recheck
    step(17, "Restore clean TASKS.md and final recheck")
    (DEMO / "docs/TASKS.md").write_text(TASKS, encoding="utf-8")
    for label, script in [("doctor", "doctor.py"), ("drift_check", "drift_check.py"),
                          ("coordinate_check", "coordinate_check.py"),
                          ("trace_doctor", "trace_doctor.py")]:
        r = run([sys.executable, str(CODERAIL / "scripts" / script),
                 "--target", str(DEMO)], cwd=DEMO)
        assert_true(r.returncode == 0, f"final {label} exit 0 after restore")

    print("\n========================================")
    print("ALL E2E CHECKS PASSED (v0.4)")
    print("========================================")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
