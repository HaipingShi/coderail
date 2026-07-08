#!/usr/bin/env python3
"""Initialize CodeRail files in a repository without overwriting non-empty files."""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "project-template"

LITE = [
    "AGENTS.md",
    "CLAUDE.md",
    "docs/NORTH_STAR.md",
    "docs/TASKS.md",
    "docs/HARNESS_SPEC.md",
    "docs/HANDOFF.md",
    "docs/CODERAIL_STATUS.md",
]

STANDARD = LITE + [
    "docs/ASSETS.md",
    "docs/DECISIONS.md",
    "docs/LESSONS.md",
    "docs/RUNLOG.md",
    "docs/TASK_GRAPH.md",
    "docs/METRICS.md",
    "docs/CONTRACTS.md",
    "docs/BLUEPRINTS.md",
    "docs/TRACELOG.jsonl",
    "docs/TRACE_INDEX.md",
]


def copy_file(rel: str, target: Path, force: bool) -> str:
    src = TEMPLATE / rel
    dst = target / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and dst.read_text(encoding="utf-8", errors="ignore").strip() and not force:
        return f"skipped existing {rel}"
    shutil.copy2(src, dst)
    return f"wrote {rel}"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default=".")
    parser.add_argument("--mode", choices=["lite", "standard"], default="standard")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    target = Path(args.target).resolve()
    if not target.exists():
        print(f"target does not exist: {target}", file=sys.stderr)
        return 2
    for rel in (LITE if args.mode == "lite" else STANDARD):
        print(copy_file(rel, target, args.force))
    print("\nNext:")
    print("1. Fill docs/NORTH_STAR.md.")
    print("2. Use docs/CONTRACTS.md for high-risk Coordinate Contract Drafts.")
    print("3. Create a task coordinate in docs/TASKS.md.")
    print("4. Use docs/BLUEPRINTS.md when architecture, data, deployment, or lifecycle complexity appears.")
    print("5. Run scripts/inspect_state.py --target <repo> to refresh docs/CODERAIL_STATUS.md.")
    print("6. Run scripts/done_gate.py before marking work done.")
    print("7. Run scripts/ci_gate.py and scripts/closeout_check.py --auto-commit before stopping after substantial work.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
