#!/usr/bin/env python3
"""Repo-local CodeRail launcher installed by init_project.py.

Forwards every command to the CodeRail home's single entry point:

    python .coderail/coderail.py start "what you want to do"
    python .coderail/coderail.py check
    python .coderail/coderail.py done
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    local_dir = Path(__file__).resolve().parent
    project = local_dir.parent
    config_path = local_dir / "config.json"
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        configured_home = config.get("coderail_home")
        home_value = os.environ.get("CODERAIL_HOME") or configured_home
        if not home_value:
            raise KeyError("coderail_home")
        home = Path(home_value).expanduser().resolve()
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as exc:
        print(f"Invalid CodeRail local config: {exc}", file=sys.stderr)
        return 2

    entry = home / "scripts" / "coderail.py"
    if not entry.exists():
        print(f"CodeRail entry is unavailable: {entry}", file=sys.stderr)
        return 2

    if args and "--target" not in args and args[0] not in {"-h", "--help"}:
        args.extend(["--target", str(project)])
    return subprocess.call([sys.executable, str(entry), *args], cwd=str(project))


if __name__ == "__main__":
    raise SystemExit(main())
