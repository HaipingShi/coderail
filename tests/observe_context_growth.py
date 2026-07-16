#!/usr/bin/env python3
"""Measure CodeRail context growth in a disposable standard project."""
from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_CONTEXT = (
    "AGENTS.md",
    "docs/NORTH_STAR.md",
    "docs/TASKS.md",
    "docs/HANDOFF.md",
    "docs/CODERAIL_STATUS.md",
)
TASK_BLOCK = re.compile(r"^##\s+T-\d+\b.*?(?=^##\s+T-\d+\b|\Z)", re.M | re.S)
STATUS = re.compile(r"^Status:\s*(\[[^]]+\])", re.M)


def task_state_bytes(text: str) -> dict[str, int]:
    sizes = {name: 0 for name in ("active", "queued", "paused", "closed", "unknown")}
    for match in TASK_BLOCK.finditer(text):
        block = match.group(0)
        status_match = STATUS.search(block)
        status = status_match.group(1) if status_match else ""
        size = len(block.encode("utf-8"))
        if status in {"[~]", "[!]", "[r]"}:
            sizes["active"] += size
        elif status == "[ ]":
            sizes["queued"] += size
        elif status == "[p]":
            sizes["paused"] += size
        elif status in {"[x]", "[f]"}:
            sizes["closed"] += size
        else:
            sizes["unknown"] += size
    sizes["hot"] = sizes["active"] + sizes["queued"]
    sizes["historical"] = sizes["closed"]
    return sizes


def latency_summary(values: list[float]) -> dict[str, float | int]:
    if not values:
        return {"count": 0, "median_ms": 0.0, "p95_ms": 0.0}
    ordered = sorted(values)
    p95_index = max(0, math.ceil(len(ordered) * 0.95) - 1)
    return {
        "count": len(ordered),
        "median_ms": round(float(statistics.median(ordered)), 3),
        "p95_ms": round(float(ordered[p95_index]), 3),
    }


def linear_slope(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    xs = list(range(len(values)))
    x_mean = statistics.mean(xs)
    y_mean = statistics.mean(values)
    denominator = sum((x - x_mean) ** 2 for x in xs)
    if not denominator:
        return 0.0
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, values))
    return round(numerator / denominator, 3)


def context_snapshot(root: Path) -> dict:
    file_bytes = {}
    for relative in REQUIRED_CONTEXT:
        path = root / relative
        file_bytes[relative] = path.stat().st_size if path.exists() else 0
    tasks_path = root / "docs" / "TASKS.md"
    tasks = tasks_path.read_text(encoding="utf-8", errors="replace")
    states = task_state_bytes(tasks)
    required_bytes = sum(file_bytes.values())
    tasks_bytes = file_bytes["docs/TASKS.md"]
    task_overhead = max(0, tasks_bytes - sum(
        states[name] for name in ("active", "queued", "paused", "closed", "unknown")
    ))
    non_tasks = required_bytes - tasks_bytes
    return {
        "required_read_bytes": required_bytes,
        "estimated_tokens": math.ceil(required_bytes / 4),
        "logical_hot_bytes": non_tasks + task_overhead + states["hot"],
        "tasks_bytes": tasks_bytes,
        "tasks_lines": len(tasks.splitlines()),
        "task_overhead_bytes": task_overhead,
        "task_state_bytes": states,
        "file_bytes": file_bytes,
    }


def run_timed(command: list[str], *, cwd: Path | None = None) -> tuple[float, subprocess.CompletedProcess]:
    started = time.perf_counter()
    result = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    elapsed_ms = (time.perf_counter() - started) * 1000
    return round(elapsed_ms, 3), result


def require_ok(result: subprocess.CompletedProcess, label: str) -> None:
    if result.returncode:
        raise RuntimeError(f"{label} failed ({result.returncode}):\n{result.stdout}")


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    require_ok(result, f"git {' '.join(args)}")
    return result.stdout.strip()


def initialize_standard_project(root: Path) -> None:
    git(root, "init", "-q")
    git(root, "config", "user.email", "observation@coderail.test")
    git(root, "config", "user.name", "CodeRail Observation")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "init_project.py"), "--target", str(root)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        encoding="utf-8", errors="replace",
    )
    require_ok(result, "standard project initialization")
    (root / "docs" / "NORTH_STAR.md").write_text(
        "# North Star\n\n## Outcome\n\n- Measure CodeRail without changing production.\n",
        encoding="utf-8",
    )
    (root / "src").mkdir()
    (root / "src" / "state.txt").write_text("cycle 0\n", encoding="utf-8")
    (root / "README.md").write_text("# Synthetic CodeRail project\n", encoding="utf-8")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "synthetic baseline")


def command_runner(target: Path):
    def run(*args: str) -> tuple[float, subprocess.CompletedProcess]:
        return run_timed([
            sys.executable, str(ROOT / "scripts" / "coderail.py"),
            *args, "--target", str(target),
        ])
    return run


def startup_observation(runs: int) -> dict:
    python_times = []
    coderail_times = []
    for _ in range(runs):
        elapsed, result = run_timed([sys.executable, "-c", "pass"])
        require_ok(result, "python startup")
        python_times.append(elapsed)
        elapsed, result = run_timed([
            sys.executable, str(ROOT / "scripts" / "coderail.py"), "--help"
        ])
        require_ok(result, "coderail help startup")
        coderail_times.append(elapsed)
    python_summary = latency_summary(python_times)
    coderail_summary = latency_summary(coderail_times)
    return {
        "python_process": python_summary,
        "coderail_help": coderail_summary,
        "eager_import_proxy_median_ms": round(
            float(coderail_summary["median_ms"]) - float(python_summary["median_ms"]), 3
        ),
    }


def run_experiment(task_count: int, startup_runs: int) -> dict:
    verify = f'"{sys.executable}" -c "pass"'
    with tempfile.TemporaryDirectory(prefix="coderail-context-") as td:
        target = Path(td)
        initialize_standard_project(target)
        cr = command_runner(target)
        initial = context_snapshot(target)
        cycles = []
        command_times = {"start": [], "check": [], "done": []}

        for number in range(1, task_count + 1):
            elapsed, result = cr(
                "start", f"Synthetic context observation {number:02d}",
                "--files", "src/**", "--verify", verify,
            )
            require_ok(result, f"cycle {number} start")
            command_times["start"].append(elapsed)
            after_start = context_snapshot(target)

            (target / "src" / "state.txt").write_text(
                f"cycle {number}\n", encoding="utf-8"
            )
            elapsed, result = cr("check")
            require_ok(result, f"cycle {number} check")
            command_times["check"].append(elapsed)

            elapsed, result = cr(
                "done", "--next", f"run synthetic cycle {number + 1:02d}"
            )
            require_ok(result, f"cycle {number} done")
            if "== Done:" not in result.stdout:
                raise RuntimeError(f"cycle {number} returned zero without Done:\n{result.stdout}")
            command_times["done"].append(elapsed)

            _, inspect = cr("inspect", "--no-write")
            require_ok(inspect, f"cycle {number} inspect")
            if "Status: healthy" not in inspect.stdout:
                raise RuntimeError(f"cycle {number} inspect was not healthy:\n{inspect.stdout}")
            if "Closed-task uncommitted ownership: none" not in inspect.stdout:
                raise RuntimeError(f"cycle {number} left closed ownership:\n{inspect.stdout}")
            dirty = git(target, "status", "--porcelain")
            if dirty:
                raise RuntimeError(f"cycle {number} left a dirty worktree:\n{dirty}")

            cycles.append({
                "task": number,
                "after_start": after_start,
                "after_done": context_snapshot(target),
                "elapsed_ms": {name: command_times[name][-1] for name in command_times},
            })

        done_snapshots = [initial, *(cycle["after_done"] for cycle in cycles)]
        tasks_values = [snapshot["tasks_bytes"] for snapshot in done_snapshots]
        required_values = [snapshot["required_read_bytes"] for snapshot in done_snapshots]
        closed_values = [
            snapshot["task_state_bytes"]["closed"] for snapshot in done_snapshots
        ]
        latency = {
            name: latency_summary(values) for name, values in command_times.items()
        }
        startup = startup_observation(startup_runs)
        final = done_snapshots[-1]
        return {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "candidate": {
                "commit": git(ROOT, "rev-parse", "HEAD"),
                "python": sys.version.split()[0],
                "platform": sys.platform,
            },
            "experiment": {
                "task_count": task_count,
                "project": "disposable standard CodeRail template with one stable source file",
                "scope": "src/**",
                "verify": "current Python interpreter exits zero",
            },
            "initial": initial,
            "final": final,
            "cycles": cycles,
            "growth": {
                "tasks_bytes_total_delta": tasks_values[-1] - tasks_values[0],
                "tasks_bytes_per_closed_task": linear_slope(tasks_values),
                "required_read_bytes_total_delta": required_values[-1] - required_values[0],
                "required_read_bytes_per_closed_task": linear_slope(required_values),
                "closed_history_bytes_per_task": linear_slope(closed_values),
            },
            "latency": latency,
            "startup": startup,
            "thresholds": {
                "estimated_tokens_limit": 3000,
                "final_estimated_tokens": final["estimated_tokens"],
                "within_token_limit": final["estimated_tokens"] <= 3000,
                "closed_history_growth_is_zero": linear_slope(closed_values) == 0,
            },
        }


def print_summary(report: dict) -> None:
    growth = report["growth"]
    final = report["final"]
    print("# CodeRail Synthetic Context Observation")
    print(f"Tasks: {report['experiment']['task_count']}")
    print(f"Final required context: {final['required_read_bytes']} bytes")
    print(f"Estimated tokens: {final['estimated_tokens']}")
    print(f"TASKS growth/task: {growth['tasks_bytes_per_closed_task']} bytes")
    print(f"Closed history growth/task: {growth['closed_history_bytes_per_task']} bytes")
    for command in ("start", "check", "done"):
        item = report["latency"][command]
        print(f"{command}: median {item['median_ms']} ms; P95 {item['p95_ms']} ms")
    print(
        "Eager-import proxy median: "
        f"{report['startup']['eager_import_proxy_median_ms']} ms"
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks", type=int, default=10)
    parser.add_argument("--startup-runs", type=int, default=10)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.tasks < 1 or args.startup_runs < 1:
        parser.error("--tasks and --startup-runs must be positive")
    report = run_experiment(args.tasks, args.startup_runs)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    print_summary(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
