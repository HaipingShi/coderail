#!/usr/bin/env python3
"""Repo-local CodeRail launcher installed by init_project.py."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


COMMANDS = {
    "blueprint": "blueprint_check.py",
    "ci": "ci_gate.py",
    "closeout": "closeout_check.py",
    "coordinate": "coordinate_check.py",
    "doctor": "doctor.py",
    "done": "done_gate.py",
    "drive": "drive_check.py",
    "finish": "finish_task.py",
    "finish-task": "finish_task.py",
    "hook": "hook_guard.py",
    "inspect": "inspect_state.py",
    "tdd": "tdd_check.py",
    "trace-index": "trace_index.py",
}


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in {"-h", "--help"}:
        print("Usage: python .coderail/coderail.py <command> [args]")
        print("Commands: " + ", ".join(sorted(COMMANDS)))
        return 0

    command = args.pop(0)
    script_name = COMMANDS.get(command)
    if not script_name:
        print(f"Unknown CodeRail command: {command}", file=sys.stderr)
        return 2

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

    script = home / "scripts" / script_name
    if not script.exists():
        print(f"CodeRail script is unavailable: {script}", file=sys.stderr)
        return 2

    if "--target" not in args:
        args.extend(["--target", str(project)])
    return subprocess.call([sys.executable, str(script), *args], cwd=str(project))


if __name__ == "__main__":
    raise SystemExit(main())
