#!/usr/bin/env python3
"""Initialize CodeRail files in a repository without overwriting non-empty files."""
from __future__ import annotations

import argparse
import json
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


def install_local_entry(target: Path, force: bool = False) -> None:
    local_dir = target / ".coderail"
    local_dir.mkdir(parents=True, exist_ok=True)
    entry = local_dir / "coderail.py"
    config_path = local_dir / "config.json"
    if force or not entry.exists():
        shutil.copy2(ROOT / "scripts" / "local_entry.py", entry)
        print("wrote .coderail/coderail.py")
    else:
        print("skipped existing .coderail/coderail.py")
    if force or not config_path.exists():
        config = {"coderail_home": str(ROOT)}
        config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        print("wrote .coderail/config.json")
    else:
        print("skipped existing .coderail/config.json")


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
    install_local_entry(target, args.force)
    print("\nNext:")
    print("1. Fill docs/NORTH_STAR.md.")
    print("2. Use docs/CONTRACTS.md for high-risk Coordinate Contract Drafts.")
    print("3. Create a task coordinate in docs/TASKS.md.")
    print("4. Use docs/BLUEPRINTS.md when architecture, data, deployment, or lifecycle complexity appears.")
    print("5. Run python .coderail/coderail.py inspect to refresh docs/CODERAIL_STATUS.md.")
    print("6. Run python .coderail/coderail.py tdd when correctness-sensitive work needs Red-Green-Refactor evidence.")
    print("7. Run python .coderail/coderail.py finish before every substantial stop.")
    print("8. For long-running work, configure the Drive Contract and run python .coderail/coderail.py drive at checkpoints.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
