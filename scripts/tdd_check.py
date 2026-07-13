#!/usr/bin/env python3
"""CodeRail TDD Gate: check Red-Green-Refactor evidence."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import coordinate_check  # noqa: E402

REQUIRED_HINTS = {
    "bug",
    "fix",
    "regression",
    "parser",
    "parse",
    "validator",
    "validation",
    "transform",
    "domain",
    "logic",
    "api",
    "contract",
    "shared",
    "utility",
}
WAIVABLE_HINTS = {
    "docs",
    "documentation",
    "chore",
    "scaffold",
    "release",
    "metadata",
    "visual",
    "polish",
    "spike",
}


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        return ""


def value_after(label: str, text: str) -> str:
    m = re.search(rf"^\s*-?\s*{re.escape(label)}\s*:\s*(.*)$", text, re.I | re.M)
    return (m.group(1) or "").strip() if m else ""


def task_type(body: str) -> str:
    m = re.search(r"^Type:\s*([^\n]+)", body, re.I | re.M)
    return m.group(1).strip().lower() if m else ""


# FN-024: an explicit, declared Type always beats keyword sniffing.
# refactor = behaviour preserved, existing verify commands are the safety
# net; forcing "write a failing test first" there is a category error.
NON_TDD_TYPES = {"refactor", "docs", "documentation", "chore", "scaffold",
                 "release", "metadata", "visual", "polish", "spike"}


def tdd_required(header: str, body: str, has_declared_tests: bool = False) -> bool:
    """Single source of truth for the TDD-needed decision. Used by every
    caller (start, check, done all run this module), so the verdict cannot
    differ between the two ends of a task's life (FN-024)."""
    declared = task_type(body)
    if declared in NON_TDD_TYPES:
        return False
    if has_declared_tests:
        return False  # tests were promised at start; FN-009 checks the diff
    blob = f"{header}\n{declared}\n{body}".lower()
    if any(hint in blob for hint in REQUIRED_HINTS):
        return True
    return False


def has_evidence(label: str, verify_text: str) -> bool:
    value = value_after(label, verify_text)
    return bool(value and value.lower() not in {"none", "n/a", "todo", "pending"})


def check_task(header: str, body: str, status: str,
               declared_tests: set[str] | None = None) -> tuple[list[str], list[str]]:
    severe, warnings = [], []
    tid = header.split()[0]
    coord = coordinate_check.parse_coordinate(body) or {}
    verify = coord.get("v", "")
    if not verify:
        return severe, warnings

    mode = value_after("TDD mode", verify).lower()
    required_by_hint = tdd_required(
        header, body, has_declared_tests=tid in (declared_tests or set()))
    if required_by_hint and not mode:
        warnings.append(f"{tid}: likely needs TDD mode because task appears correctness-sensitive")
        return severe, warnings
    if mode and mode not in {"required", "optional", "waived"}:
        warnings.append(f"{tid}: TDD mode should be required, optional, or waived")
    if required_by_hint and mode == "waived" and not has_evidence("Waiver reason", verify):
        warnings.append(f"{tid}: TDD waived for correctness-sensitive task without waiver reason")
    if mode == "required":
        missing = [label for label in ["Red check", "Green check"] if not has_evidence(label, verify)]
        if status == "[x]" and missing:
            severe.append(f"{tid}: done task with TDD required missing {', '.join(missing)}")
        elif missing:
            warnings.append(f"{tid}: TDD required missing {', '.join(missing)}")
        if status == "[x]" and not has_evidence("CI check", verify):
            warnings.append(f"{tid}: done task with TDD required should record CI check")
    return severe, warnings


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Run CodeRail TDD gate")
    ap.add_argument("--target", default=".")
    args = ap.parse_args(argv)
    root = Path(args.target).resolve()
    tasks = root / "docs" / "TASKS.md"
    text = read(tasks)
    if not text:
        print(f"error: {tasks} not found", file=sys.stderr)
        return 2

    # FN-024: tasks that promised test files at start (--tests) are already
    # covered by the diff check in done; do not nag them here.
    declared_tests: set[str] = set()
    try:
        import json
        meta = json.loads((root / ".coderail" / "tasks.json").read_text(encoding="utf-8"))
        declared_tests = {tid for tid, m in meta.items() if m.get("tests")}
    except (FileNotFoundError, ValueError, OSError):
        pass

    severe, warnings = [], []
    checked = 0
    for header, body, status in coordinate_check.split_tasks(text):
        if "Example task" in header or "Task Template" in header:
            continue
        s, w = check_task(header, body, status, declared_tests)
        severe.extend(s)
        warnings.extend(w)
        checked += 1

    status = "healthy" if not severe and not warnings else ("unhealthy" if severe else "usable with warnings")
    print("# TDD Gate Report\n")
    print(f"Status: {status}")
    print(f"Tasks checked: {checked}\n")
    print("## Severe")
    print("- none" if not severe else "\n".join(f"- {x}" for x in severe))
    print("\n## Warnings")
    print("- none" if not warnings else "\n".join(f"- {x}" for x in warnings))
    return 1 if severe else 0


if __name__ == "__main__":
    raise SystemExit(main())

