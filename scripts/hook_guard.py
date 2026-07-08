#!/usr/bin/env python3
"""Hook guard for long-running CodeRail projects.

This script is intentionally conservative and portable. It can be called from
agent/tool hooks to remind, protect CodeRail governance files, or run periodic
health checks such as Blueprint Gate and Doctor.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

PROTECTED_PATTERNS = [
    "AGENTS.md",
    "CLAUDE.md",
    ".codex-plugin/**",
    ".claude-plugin/**",
    "skills/**",
    "references/**",
    "project-template/AGENTS.md",
    "project-template/CLAUDE.md",
]

STATE_PATTERNS = [
    "docs/NORTH_STAR.md",
    "docs/TASKS.md",
    "docs/CONTRACTS.md",
    "docs/BLUEPRINTS.md",
    "docs/HANDOFF.md",
    "docs/HARNESS_SPEC.md",
    "docs/CODERAIL_STATUS.md",
]


def normalize(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def matches(path: str, pattern: str) -> bool:
    path = normalize(path)
    pattern = normalize(pattern)
    if pattern.endswith("/**"):
        base = pattern[:-3].rstrip("/")
        return path == base or path.startswith(base + "/")
    return path == pattern


def extract_paths(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"path", "file_path", "filePath", "filename"} and isinstance(item, str):
                found.append(item)
            found.extend(extract_paths(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(extract_paths(item))
    elif isinstance(value, str):
        found.extend(re.findall(r"[\w./\\-]+\.(?:md|json|py|ts|tsx|js|jsx|yml|yaml|toml)", value))
    return sorted(set(normalize(p) for p in found))


def paths_from_stdin() -> list[str]:
    raw = sys.stdin.read()
    if not raw.strip():
        return []
    try:
        return extract_paths(json.loads(raw))
    except json.JSONDecodeError:
        return extract_paths(raw)


def run_script(script: str, target: Path) -> int:
    cmd = [sys.executable, str(ROOT / "scripts" / script), "--target", str(target)]
    return subprocess.call(cmd)


def pre_edit(target: Path) -> int:
    paths = paths_from_stdin()
    if not paths:
        return 0
    protected = [p for p in paths if any(matches(p, pat) for pat in PROTECTED_PATTERNS)]
    state = [p for p in paths if any(matches(p, pat) for pat in STATE_PATTERNS)]

    if state:
        print("[CodeRail] Governance state edit detected. Keep it tied to G/T/S/V/X/P and trace.")

    if protected and os.environ.get("CODERAIL_ALLOW_GOVERNANCE_EDIT") != "1":
        print("[CodeRail] Protected governance/kernel files should not be edited casually:")
        for path in protected:
            print(f"- {path}")
        print("Set CODERAIL_ALLOW_GOVERNANCE_EDIT=1 only for an explicit CodeRail upgrade.")
        return 1
    return 0


def prompt() -> int:
    print("[CodeRail] Load AGENTS.md. Treat CodeRail rules as long-lived project rails, not ordinary task notes.")
    print("[CodeRail] For bugs/regressions/parsers/domain logic/APIs/shared utilities, run TDD Gate.")
    print("[CodeRail] For architecture/data/deployment/UI/lifecycle complexity, keep docs/BLUEPRINTS.md current.")
    print("[CodeRail] Before stopping, include Closeout State, Auto Commit action, Handoff Trigger Check, and Next Executable Step.")
    return 0


def stop(target: Path, soft: bool) -> int:
    print("[CodeRail] Stop reminder: do not end substantial work without closeout state and auto-commit action.")
    print("[CodeRail] Running Blueprint Gate...")
    bp = run_script("blueprint_check.py", target)
    print("[CodeRail] Running Doctor...")
    dr = run_script("doctor.py", target)
    status = 1 if bp or dr else 0
    if status and soft:
        print("[CodeRail] Hook found issues, but soft mode will not block.")
        return 0
    return status


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Run CodeRail hook guard")
    ap.add_argument("--stage", choices=["prompt", "pre-edit", "blueprint", "doctor", "stop"], required=True)
    ap.add_argument("--target", default=".")
    ap.add_argument("--soft", action="store_true", help="Report issues without blocking")
    args = ap.parse_args(argv)
    target = Path(args.target).resolve()

    if args.stage == "prompt":
        return prompt()
    if args.stage == "pre-edit":
        return pre_edit(target)
    if args.stage == "blueprint":
        return run_script("blueprint_check.py", target)
    if args.stage == "doctor":
        return run_script("doctor.py", target)
    if args.stage == "stop":
        return stop(target, args.soft)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
