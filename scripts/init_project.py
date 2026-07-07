#!/usr/bin/env python3
"""Initialize CodeRail files in a repository.

This script copies project-template files without overwriting non-empty files
unless --force is provided. It has no network access and runs only local file IO.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "project-template"

LITE_FILES = [
    "AGENTS.md",
    "CLAUDE.md",
    "docs/NORTH_STAR.md",
    "docs/TASKS.md",
    "docs/HARNESS_SPEC.md",
    "docs/HANDOFF.md",
]

STANDARD_FILES = LITE_FILES + [
    "docs/ASSETS.md",
    "docs/DECISIONS.md",
    "docs/LESSONS.md",
    "docs/RUNLOG.md",
    "docs/TASK_GRAPH.md",
    "docs/METRICS.md",
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default=".", help="Repository root to initialize")
    parser.add_argument("--mode", choices=["lite", "standard"], default="standard")
    parser.add_argument("--force", action="store_true", help="Overwrite existing non-empty files")
    args = parser.parse_args()

    target = Path(args.target).resolve()
    if not target.exists():
        print(f"target does not exist: {target}", file=sys.stderr)
        return 2
    files = LITE_FILES if args.mode == "lite" else STANDARD_FILES
    for rel in files:
        print(copy_file(rel, target, args.force))
    print("\nNext: open docs/NORTH_STAR.md and fill Outcome, Current Bet, Invariants, and Current Slice.")
    print("Then: each task in docs/TASKS.md should carry a CodeRail Coordinate (G/T/S/V/X/P).")
    print("Trace: append events to docs/TRACELOG.jsonl via scripts/trace_event.py and regenerate docs/TRACE_INDEX.md.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
