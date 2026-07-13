#!/usr/bin/env python3
"""Repo-local CodeRail launcher installed by init_project.py.

Forwards every command to the CodeRail home's single entry point:

    python .coderail/coderail.py start "what you want to do"
    python .coderail/coderail.py check
    python .coderail/coderail.py done

If this machine keeps CodeRail somewhere else (CI, cloud sandbox, another
laptop), point at it without editing any file:

    CODERAIL_HOME=/path/to/coderail python .coderail/coderail.py check
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

# Replaced with the CodeRail home version at install time (see init_project.py).
# If this file was copied by hand (so the placeholder survives), effective_version()
# falls back to reading VERSION from the CodeRail home - manual copies stay honest.
SHIM_VERSION = "0.0.0-dev"


def effective_version(home: "Path | None" = None) -> str:
    if SHIM_VERSION != "0.0.0-dev":
        return SHIM_VERSION
    if home is not None:
        version_file = home / "VERSION"
        try:
            return version_file.read_text(encoding="utf-8").strip().splitlines()[0].strip()
        except (OSError, IndexError):
            pass
    return SHIM_VERSION

HOME_HINT = (
    "Hint: the recorded coderail_home path is machine-specific. Fix it once for\n"
    "this machine with a gitignored local override (checked before config.json):\n"
    '    echo \'{"coderail_home": "/path/to/coderail"}\' > .coderail/config.local.json\n'
    "or per run:  CODERAIL_HOME=/path/to/coderail python .coderail/coderail.py <cmd>\n"
    "config.json also accepts a list of candidate paths, probed in order (FN-022)."
)


def home_candidates(local_dir: Path) -> list[str]:
    """Resolution order (FN-022): CODERAIL_HOME env > config.local.json
    (gitignored, machine-local) > config.json. Each source may hold a single
    path or a list of candidate paths, probed in order."""
    candidates: list[str] = []
    env = os.environ.get("CODERAIL_HOME")
    if env:
        candidates.append(env)
    for name in ("config.local.json", "config.json"):
        try:
            value = json.loads((local_dir / name).read_text(encoding="utf-8")).get("coderail_home")
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            continue
        if isinstance(value, str):
            candidates.append(value)
        elif isinstance(value, list):
            candidates.extend(v for v in value if isinstance(v, str))
    return candidates


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    local_dir = Path(__file__).resolve().parent
    project = local_dir.parent

    candidates = home_candidates(local_dir)
    if not candidates:
        print("CodeRail home is not configured (.coderail/config.json has no", file=sys.stderr)
        print("coderail_home and CODERAIL_HOME is not set).", file=sys.stderr)
        print(HOME_HINT, file=sys.stderr)
        return 2

    entry = home = None
    for cand in candidates:
        h = Path(cand).expanduser().resolve()
        e = h / "scripts" / "coderail.py"
        if e.exists():
            home, entry = h, e
            break
    if entry is None:
        print("CodeRail entry is unavailable. Probed candidate path(s):", file=sys.stderr)
        for cand in candidates:
            print(f"  - {Path(cand).expanduser()}", file=sys.stderr)
        print(HOME_HINT, file=sys.stderr)
        return 2

    if args and "--target" not in args and args[0] not in {"-h", "--help"}:
        args.extend(["--target", str(project)])
    return subprocess.call([sys.executable, str(entry), *args], cwd=str(project))


if __name__ == "__main__":
    raise SystemExit(main())
