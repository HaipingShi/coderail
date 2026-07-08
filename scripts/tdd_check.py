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
    "refactor",
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


def likely_required(header: str, body: str) -> bool:
    blob = f"{header}\n{task_type(body)}\n{body}".lower()
    if any(hint in blob for hint in REQUIRED_HINTS):
        return True
    if any(hint in blob for hint in WAIVABLE_HINTS):
        return False
    return False


def has_evidence(label: str, verify_text: str) -> bool:
    value = value_after(label, verify_text)
    return bool(value and value.lower() not in {"none", "n/a", "todo", "pending"})


def check_task(header: str, body: str, status: str) -> tuple[list[str], list[str]]:
    severe, warnings = [], []
    tid = header.split()[0]
    coord = coordinate_check.parse_coordinate(body) or {}
    verify = coord.get("v", "")
    if not verify:
        return severe, warnings

    mode = value_after("TDD mode", verify).lower()
    required_by_hint = likely_required(header, body)
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

    severe, warnings = [], []
    checked = 0
    for header, body, status in coordinate_check.split_tasks(text):
        if "Example task" in header or "Task Template" in header:
            continue
        s, w = check_task(header, body, status)
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

