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
    # Local working state (e.g. the spinning-in-place counter) must stay out of git.
    gitignore = target / ".gitignore"
    ignore_line = ".coderail/spin.json"
    existing = gitignore.read_text(encoding="utf-8", errors="ignore") if gitignore.exists() else ""
    if ignore_line not in existing:
        with gitignore.open("a", encoding="utf-8") as fh:
            if existing and not existing.endswith("\n"):
                fh.write("\n")
            fh.write(ignore_line + "\n")
        print("updated .gitignore (.coderail/spin.json)")


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
    print("\nCodeRail is ready. Three commands cover everyday work:")
    print()
    print('  python .coderail/coderail.py start "what you want to do"   # begin a task')
    print("  python .coderail/coderail.py check                         # am I on track?")
    print("  python .coderail/coderail.py done                          # finish safely")
    print()
    print("First step: write one paragraph about what you are building in docs/NORTH_STAR.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
