#!/usr/bin/env python3
"""Run CodeRail regression observations with ignored run artifacts.

The reusable harness lives in the repository. Each run writes snapshots,
command logs, and comparison reports under .coderail-runs/ by default so the
process output does not become source control state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tarfile
import time
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path


IGNORE_NAMES = {
    ".git",
    ".coderail-runs",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
    ".venv",
}


def run_cmd(cmd: list[str], cwd: Path) -> tuple[int, str, float]:
    started = time.monotonic()
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.returncode, result.stdout, time.monotonic() - started


def copy_current(source: Path, dest: Path) -> None:
    def ignore(_dir: str, names: list[str]) -> set[str]:
        return {name for name in names if name in IGNORE_NAMES or name.endswith((".pyc", ".log", ".tmp", ".bak"))}

    shutil.copytree(source, dest, ignore=ignore)


def archive_ref_binary(source: Path, ref: str, dest: Path) -> bool:
    if not (source / ".git").exists():
        return False
    result = subprocess.run(
        ["git", "-C", str(source), "archive", "--format=tar", ref],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        return False
    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=BytesIO(result.stdout), mode="r:") as tar:
        try:
            tar.extractall(dest, filter="data")
        except TypeError:
            tar.extractall(dest)
    return True


def command_plan(root: Path, include_npm_test: bool) -> list[tuple[str, list[str], Path]]:
    python = sys.executable
    scripts = root / "scripts"
    plan: list[tuple[str, list[str], Path]] = []
    if include_npm_test:
        npm = shutil.which("npm")
        if npm:
            plan.append(("npm test", [npm, "test"], root))
    if (scripts / "doctor.py").exists():
        plan.append(("doctor project-template", [python, str(scripts / "doctor.py"), "--target", "project-template"], root))
    if (scripts / "blueprint_check.py").exists():
        plan.append(("blueprint root", [python, str(scripts / "blueprint_check.py"), "--target", "."], root))
    if (scripts / "coordinate_check.py").exists():
        plan.append(("coordinate project-template", [python, str(scripts / "coordinate_check.py"), "--target", "project-template"], root))
    if (scripts / "contract_check.py").exists():
        plan.append(("contract project-template", [python, str(scripts / "contract_check.py"), "--target", "project-template"], root))
    if (scripts / "tdd_check.py").exists():
        plan.append(("tdd project-template", [python, str(scripts / "tdd_check.py"), "--target", "project-template"], root))
    return plan


def extract_signal(output: str) -> dict:
    tests = re.findall(r"(\d+)\s+tests passed", output)
    statuses = re.findall(r"^Status:\s*([^\n]+)", output, flags=re.M)
    severe = len(re.findall(r"\bSEVERE\b|must-fix blocker", output))
    warnings = len(re.findall(r"^\-\s+(?:warning:|optimization opportunity:)", output, flags=re.M))
    return {
        "tests_passed": int(tests[-1]) if tests else None,
        "statuses": statuses[:8],
        "severe_mentions": severe,
        "warning_mentions": warnings,
    }


def run_profile(label: str, root: Path, out_dir: Path, include_npm_test: bool) -> list[dict]:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, cmd, cwd in command_plan(root, include_npm_test):
        code, output, elapsed = run_cmd(cmd, cwd)
        log_name = re.sub(r"[^a-zA-Z0-9_.-]+", "_", name).strip("_") + ".log"
        (out_dir / log_name).write_text(output, encoding="utf-8")
        rows.append(
            {
                "name": name,
                "returncode": code,
                "elapsed_seconds": round(elapsed, 3),
                "stdout_sha256": hashlib.sha256(output.encode("utf-8", errors="replace")).hexdigest(),
                "signal": extract_signal(output),
                "log": str((out_dir / log_name).as_posix()),
            }
        )
    return rows


def compare(base: list[dict], current: list[dict]) -> list[dict]:
    by_name = {row["name"]: row for row in base}
    out = []
    for cur in current:
        prev = by_name.get(cur["name"])
        if not prev:
            out.append({"name": cur["name"], "change": "added", "current_returncode": cur["returncode"]})
            continue
        changed = []
        if prev["returncode"] != cur["returncode"]:
            changed.append(f"returncode {prev['returncode']} -> {cur['returncode']}")
        if prev["signal"] != cur["signal"]:
            changed.append("signal changed")
        if prev["stdout_sha256"] != cur["stdout_sha256"]:
            changed.append("output changed")
        out.append(
            {
                "name": cur["name"],
                "change": ", ".join(changed) if changed else "same",
                "baseline_returncode": prev["returncode"],
                "current_returncode": cur["returncode"],
                "baseline_signal": prev["signal"],
                "current_signal": cur["signal"],
            }
        )
    for name, prev in by_name.items():
        if not any(row["name"] == name for row in current):
            out.append({"name": name, "change": "removed", "baseline_returncode": prev["returncode"]})
    return out


def render_report(summary: dict) -> str:
    lines = ["# CodeRail Regression Observation", ""]
    lines.append(f"Generated at: {summary['generated_at']}")
    lines.append(f"Baseline: {summary['baseline_ref']}")
    lines.append(f"Run directory: {summary['run_dir']}")
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append(f"- Baseline failures: {summary['baseline_failures']}")
    lines.append(f"- Current failures: {summary['current_failures']}")
    lines.append(f"- Changed checks: {summary['changed_checks']}")
    lines.append("")
    lines.append("## Comparison")
    lines.append("")
    for row in summary["comparison"]:
        lines.append(f"- {row['name']}: {row['change']}")
    lines.append("")
    lines.append("## Artifact Policy")
    lines.append("")
    lines.append("- This report is a run artifact and should stay under a gitignored run directory.")
    lines.append("- Commit only reusable harness code, docs, templates, and package entries.")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Run CodeRail regression observation")
    ap.add_argument("--target", default=".")
    ap.add_argument("--baseline-ref", default="HEAD")
    ap.add_argument("--run-dir", help="Artifact directory; defaults to .coderail-runs/regression-observe/<timestamp>")
    ap.add_argument("--skip-npm-test", action="store_true")
    args = ap.parse_args(argv)

    root = Path(args.target).resolve()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = Path(args.run_dir).resolve() if args.run_dir else root / ".coderail-runs" / "regression-observe" / stamp
    baseline_dir = run_dir / "baseline"
    current_dir = run_dir / "current"
    logs_dir = run_dir / "logs"
    run_dir.mkdir(parents=True, exist_ok=True)

    baseline_available = archive_ref_binary(root, args.baseline_ref, baseline_dir)
    if not baseline_available:
        copy_current(root, baseline_dir)
    copy_current(root, current_dir)

    include_npm_test = not args.skip_npm_test
    baseline_rows = run_profile("baseline", baseline_dir, logs_dir / "baseline", include_npm_test)
    current_rows = run_profile("current", current_dir, logs_dir / "current", include_npm_test)
    comparison = compare(baseline_rows, current_rows)
    changed = [row for row in comparison if row["change"] != "same"]
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "target": str(root),
        "baseline_ref": args.baseline_ref if baseline_available else f"{args.baseline_ref} unavailable; copied current",
        "run_dir": str(run_dir),
        "baseline": baseline_rows,
        "current": current_rows,
        "comparison": comparison,
        "baseline_failures": sum(1 for row in baseline_rows if row["returncode"] != 0),
        "current_failures": sum(1 for row in current_rows if row["returncode"] != 0),
        "changed_checks": len(changed),
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    report = render_report(summary)
    (run_dir / "report.md").write_text(report, encoding="utf-8")
    print(report)
    return 1 if summary["current_failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
