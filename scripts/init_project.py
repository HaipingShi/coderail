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


def home_version() -> str:
    version_file = ROOT / "VERSION"
    if version_file.exists():
        return version_file.read_text(encoding="utf-8").strip().splitlines()[0].strip()
    return "0.0.0"


def render_shim() -> str:
    text = (ROOT / "scripts" / "local_entry.py").read_text(encoding="utf-8")
    return text.replace('SHIM_VERSION = "0.0.0-dev"', f'SHIM_VERSION = "{home_version()}"', 1)


def shim_version_of(path: Path) -> str:
    try:
        import re
        m = re.search(r'SHIM_VERSION\s*=\s*"([^"]+)"', path.read_text(encoding="utf-8"))
        return m.group(1) if m else "unknown"
    except OSError:
        return "unknown"


def install_local_entry(target: Path, force: bool = False) -> None:
    local_dir = target / ".coderail"
    local_dir.mkdir(parents=True, exist_ok=True)
    entry = local_dir / "coderail.py"
    config_path = local_dir / "config.json"

    # FN-002: the shim is versioned and updates on its own schedule.
    # An outdated shim is refreshed even without --force, so "new docs + old
    # entry" mixes can no longer happen.
    version = home_version()
    if not entry.exists():
        entry.write_text(render_shim(), encoding="utf-8")
        print(f"wrote .coderail/coderail.py (shim v{version})")
    elif shim_version_of(entry) != version:
        old = shim_version_of(entry)
        entry.write_text(render_shim(), encoding="utf-8")
        print(f"updated .coderail/coderail.py (shim {old} -> v{version})")
    else:
        print("shim .coderail/coderail.py is current")

    # FN-002: config.json holds machine-local state and is NEVER silently
    # overwritten - not even by --force. Delete it by hand to reset.
    if not config_path.exists():
        config = {"coderail_home": str(ROOT)}
        config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        print("wrote .coderail/config.json")
    else:
        print("kept existing .coderail/config.json (never overwritten; edit or delete by hand)")
    # Local working state (spin counter, done reports) must stay out of git.
    gitignore = target / ".gitignore"
    ignore_lines = [".coderail/spin.json", ".coderail/reports/"]
    existing = gitignore.read_text(encoding="utf-8", errors="ignore") if gitignore.exists() else ""
    missing = [l for l in ignore_lines if l not in existing]
    if missing:
        with gitignore.open("a", encoding="utf-8") as fh:
            if existing and not existing.endswith("\n"):
                fh.write("\n")
            fh.write("\n".join(missing) + "\n")
        print(f"updated .gitignore ({', '.join(missing)})")


def prefill_blueprints(target: Path) -> None:
    """FN-006: seed BLUEPRINTS.md from detected code signals instead of
    defaulting everything to not-applicable and contradicting doctor."""
    index = target / "docs" / "BLUEPRINTS.md"
    if not index.exists():
        return
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        import blueprint_check
        result = blueprint_check.check_project(target)
    except Exception:
        return
    finally:
        if str(ROOT / "scripts") in sys.path:
            sys.path.remove(str(ROOT / "scripts"))
    needed = set(result.get("required", []))
    if not needed:
        return
    import re
    text = index.read_text(encoding="utf-8")
    changed = 0
    for did in needed:
        row_re = re.compile(rf"^(\|\s*{did}\s*\|[^|]*\|)\s*not-applicable\s*(\|)", re.M)
        text, n = row_re.subn(rf"\g<1> planned \g<2>", text, count=1)
        changed += n
    if changed:
        index.write_text(text, encoding="utf-8")
        print(f"prefilled docs/BLUEPRINTS.md from code signals: {', '.join(sorted(needed))} -> planned")


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
    prefill_blueprints(target)
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
