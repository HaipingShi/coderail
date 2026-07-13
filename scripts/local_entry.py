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
    "Hint: the recorded coderail_home path is machine-specific. On a different\n"
    "machine (CI, cloud sandbox, teammate laptop), override it per run:\n"
    "    CODERAIL_HOME=/path/to/coderail python .coderail/coderail.py <command>\n"
    "or update .coderail/config.json to this machine's CodeRail checkout."
)


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    local_dir = Path(__file__).resolve().parent
    project = local_dir.parent
    config_path = local_dir / "config.json"
    configured_home = None
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        configured_home = config.get("coderail_home")
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    home_value = os.environ.get("CODERAIL_HOME") or configured_home
    if not home_value:
        print("CodeRail home is not configured (.coderail/config.json has no", file=sys.stderr)
        print("coderail_home and CODERAIL_HOME is not set).", file=sys.stderr)
        print(HOME_HINT, file=sys.stderr)
        return 2

    home = Path(home_value).expanduser().resolve()
    entry = home / "scripts" / "coderail.py"
    if not entry.exists():
        print(f"CodeRail entry is unavailable: {entry}", file=sys.stderr)
        print(HOME_HINT, file=sys.stderr)
        return 2

    if args and "--target" not in args and args[0] not in {"-h", "--help"}:
        args.extend(["--target", str(project)])
    return subprocess.call([sys.executable, str(entry), *args], cwd=str(project))


if __name__ == "__main__":
    raise SystemExit(main())
