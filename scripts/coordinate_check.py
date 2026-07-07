#!/usr/bin/env python3
"""Check that tasks in docs/TASKS.md carry a complete CodeRail Coordinate.

Standard library only. Parses each task block and verifies the G/T/S/V/X/P
fields. For done tasks, V must show a harness result or manual acceptance and
P must include at least TASKS and TRACE. Severe gaps exit non-zero.

See references/CODERAIL_COORDINATE.md.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TASK_HEADER = re.compile(r"^##\s+([A-Z]-\d+[^\n]*)", re.M)
DONE_MARKERS = ("[x]", "[f]", "[r]")


def split_tasks(text: str):
    """Yield (header, body, status) for each task block."""
    matches = list(TASK_HEADER.finditer(text))
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end]
        status = _extract_status(body)
        yield m.group(1).strip(), body, status


def _extract_status(body: str) -> str:
    m = re.search(r"Status:\s*(\[[ x~!fr]\])", body)
    if not m:
        return "unknown"
    return m.group(1)


def parse_coordinate(body: str) -> dict | None:
    """Parse the '### CodeRail Coordinate' block out of a task body.

    Line-based state machine: the field anchors are 'G — Goal:', 'T — Task:',
    'S — Scope:', 'V — Verify:', 'X — Stop:', 'P — Persist:'. Sub-labels inside
    S are 'Allowed:' and 'Forbidden:'. Bullet lines under a field are its value.
    """
    m = re.search(r"###\s+CodeRail Coordinate(.*?)(?=^###\s|^##\s|\Z)", body, re.S | re.M)
    if not m:
        return None
    block = m.group(1)

    coord = {"g": "", "t": "", "s_allowed": "", "s_forbidden": "", "v": "", "x": "", "p": ""}
    field = None  # one of g, t, s_allowed, s_forbidden, v, x, p, None
    field_label = re.compile(r"^([GTVXP])\s*[—\-:]\s*(Goal|Task|Scope|Verify|Stop|Persist):?\s*$")
    sub_label = re.compile(r"^[-*\s]*(Allowed|Forbidden):\s*$")

    for raw_line in block.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        fm = field_label.match(stripped)
        if fm:
            letter = fm.group(1)
            field = {"G": "g", "T": "t", "V": "v", "X": "x", "P": "p"}.get(letter)
            if letter == "S":
                field = "s_pending"  # S needs an inner Allowed/Forbidden
            continue
        sm = sub_label.match(stripped)
        if sm:
            kind = sm.group(1)
            field = "s_allowed" if kind == "Allowed" else "s_forbidden"
            continue
        # A new ### or ## inside the block ends parsing (shouldn't happen due to outer regex).
        if stripped.startswith("#"):
            field = None
            continue
        if field is None:
            continue
        value = stripped.lstrip("-* \t").rstrip()
        if not value:
            continue
        if field == "s_pending":
            # Lines directly under S but before an Allowed/Forbidden label: treat as allowed.
            field = "s_allowed"
        if coord[field]:
            coord[field] += "\n" + value
        else:
            coord[field] = value

    # Map a top-level 'S — Scope:' with no inner labels still counts as having content.
    return coord


def check_task(header: str, body: str, status: str) -> tuple:
    """Return (severe: list[str], warnings: list[str])."""
    severe = []
    warnings = []
    coord = parse_coordinate(body)
    tid = header.split()[0]

    if coord is None:
        # Coordinate block missing entirely.
        if status in {"[ ]", "[~]", "[!]", "[x]", "[f]", "[r]"}:
            severe.append(f"{tid}: no CodeRail Coordinate block")
        return severe, warnings

    if not coord.get("g"):
        severe.append(f"{tid}: G (Goal) missing")
    if not coord.get("t"):
        severe.append(f"{tid}: T (Task) missing")
    if not coord.get("s_allowed"):
        severe.append(f"{tid}: S allowed missing")
    if not coord.get("s_forbidden"):
        warnings.append(f"{tid}: S forbidden empty (write 'none' if truly nothing is forbidden)")
    if not coord.get("v"):
        severe.append(f"{tid}: V (Verify) missing")
    if not coord.get("x"):
        warnings.append(f"{tid}: X (Stop) empty")
    if not coord.get("p"):
        severe.append(f"{tid}: P (Persist) missing")

    # Done tasks need V evidence and P coverage.
    if status in DONE_MARKERS:
        if not coord.get("v"):
            severe.append(f"{tid}: done task missing V (harness or manual acceptance)")
        elif "harness" not in coord["v"].lower() and "manual" not in coord["v"].lower() and "pytest" not in coord["v"].lower() and "test" not in coord["v"].lower():
            warnings.append(f"{tid}: done task V has no clear harness or manual acceptance")
        p_upper = coord.get("p", "").upper()
        if "TASKS" not in p_upper:
            severe.append(f"{tid}: done task P missing TASKS")
        if "TRACE" not in p_upper:
            severe.append(f"{tid}: done task P missing TRACE")

    return severe, warnings


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Check CodeRail Coordinate coverage in TASKS.md")
    parser.add_argument("--target", default=".", help="Repository root containing docs/")
    args = parser.parse_args(argv)

    target = Path(args.target).resolve()
    tasks_path = target / "docs" / "TASKS.md"
    if not tasks_path.exists():
        print(f"error: {tasks_path} not found", file=sys.stderr)
        return 2

    text = tasks_path.read_text(encoding="utf-8", errors="ignore")
    tasks = list(split_tasks(text))

    severe = []
    warnings = []
    checked = 0
    for header, body, status in tasks:
        s, w = check_task(header, body, status)
        severe.extend(s)
        warnings.extend(w)
        checked += 1

    print("# Coordinate Check Report\n")
    status = "healthy" if not severe and not warnings else ("unhealthy" if severe else "usable with warnings")
    print(f"Status: {status}")
    print(f"Tasks checked: {checked}\n")

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
