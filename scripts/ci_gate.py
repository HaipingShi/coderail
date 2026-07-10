#!/usr/bin/env python3
"""CodeRail CI Gate: run non-decision checks without stopping for permission."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def run(label: str, cmd: list[str], cwd: Path) -> int:
    print(f"\n## {label}")
    print(" ".join(cmd))
    result = subprocess.run(cmd, cwd=str(cwd))
    if result.returncode:
        print(f"{label}: failed ({result.returncode})")
    else:
        print(f"{label}: passed")
    return result.returncode


def has_git_repo(root: Path) -> bool:
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip().lower() == "true"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Run CodeRail CI gate")
    ap.add_argument("--target", default=".")
    ap.add_argument("--skip-npm-test", action="store_true")
    args = ap.parse_args(argv)
    root = Path(args.target).resolve()
    scripts = root / "scripts"
    failures = 0

    package = read_json(root / "package.json")
    has_test = bool(package.get("scripts", {}).get("test"))
    if has_test and not args.skip_npm_test:
        npm = shutil.which("npm")
        if npm:
            failures += bool(run("npm test", [npm, "test"], root))
        else:
            print("\n## npm test\nnpm unavailable; skipped")

    python = sys.executable
    if (scripts / "doctor.py").exists():
        doctor_target = root / "project-template" if (root / "project-template").exists() else root
        failures += bool(run("CodeRail doctor", [python, str(scripts / "doctor.py"), "--target", str(doctor_target)], root))

    if (scripts / "blueprint_check.py").exists():
        failures += bool(run("Blueprint gate", [python, str(scripts / "blueprint_check.py"), "--target", str(root)], root))

    if (scripts / "contract_check.py").exists():
        contract_target = root / "project-template" if (root / "project-template").exists() else root
        failures += bool(run("Contract check", [python, str(scripts / "contract_check.py"), "--target", str(contract_target)], root))

    if (scripts / "tdd_check.py").exists():
        tdd_target = root / "project-template" if (root / "project-template").exists() else root
        failures += bool(run("TDD gate", [python, str(scripts / "tdd_check.py"), "--target", str(tdd_target)], root))

    if (scripts / "drive_check.py").exists():
        drive_target = root / "project-template" if (root / "project-template").exists() else root
        failures += bool(run("Drive check", [python, str(scripts / "drive_check.py"), "--target", str(drive_target)], root))

    if has_git_repo(root):
        failures += bool(run("Whitespace diff check", ["git", "-C", str(root), "diff", "--check"], root))

    print("\n# CI Gate Report")
    print("Status: passed" if not failures else "Status: failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
