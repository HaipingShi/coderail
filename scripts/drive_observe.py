#!/usr/bin/env python3
"""Run isolated A/B observations for the CodeRail Drive policy.

The baseline returns control after every checkpoint. The Drive profile uses the
deterministic evaluator. This harness measures policy behavior, not model quality.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import drive_check  # noqa: E402


def task(task_id="T-001", status="[~]", autonomy="allowed", priority="P1", result="") -> str:
    completion = f"\n### Completion\n\nTask result: {result}\n" if result else ""
    return f"""## {task_id} Observation task

Status: {status}
Type: feature
Rail: full
Priority: {priority}
Autonomy: {autonomy}

### CodeRail Coordinate

G — Goal:
- North Star: NS-OBSERVE

T — Task:
- Advance the observation fixture

S — Scope:
- Allowed:
  - src/**
- Forbidden:
  - schema/**

V — Verify:
- Harness:
  - deterministic fixture

X — Stop:
- decision-grade change required

P — Persist:
- TASKS
- TRACE

### Task Contract

Depends on:
- none

Acceptance:
- [ ] fixture expectation
{completion}"""


def write_fixture(root: Path, tasks: str, events=None) -> None:
    docs = root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "NORTH_STAR.md").write_text("""# North Star

## Outcome

- measure Drive behavior

## Current Slice

- Milestone: M-OBSERVE

## Drive Contract

- Mode: continuous
- Terminal condition: all observation tasks pass
- Progress signal: matched scenario decisions
- Retry budget: 3
- No-progress limit: 2
- Human gates: decision-grade changes
""", encoding="utf-8")
    (docs / "TASKS.md").write_text("# Tasks\n\n" + tasks, encoding="utf-8")
    (docs / "HARNESS_SPEC.md").write_text("""# Harness Spec

## Drive Progress Harness

- Progress signal: matched scenario decisions
- Terminal evidence: all observation tasks passed
""", encoding="utf-8")
    (docs / "TRACELOG.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in (events or [])), encoding="utf-8"
    )


def scenarios() -> list[dict]:
    return [
        {"name": "continue_active", "expected": "CONTINUE", "tasks": task()},
        {
            "name": "repair_known_failure",
            "expected": "REPAIR",
            "tasks": task(),
            "kwargs": {"harness_result": "failed", "retry_count": 1, "failure_known": True},
        },
        {
            "name": "advance_after_task_done",
            "expected": "ADVANCE",
            "tasks": task(status="[x]", result="done") + "\n" + task("T-002", "[ ]"),
        },
        {
            "name": "continue_stage_complete",
            "expected": "CONTINUE",
            "tasks": task(result="stage-complete") + "\n" + task("T-002", "[ ]"),
        },
        {
            "name": "block_human_gate",
            "expected": "BLOCKED_DECISION",
            "tasks": task(autonomy="human-gated"),
        },
        {
            "name": "review_repeated_reopen",
            "expected": "REVIEW_DIRECTION",
            "tasks": task(),
            "events": [
                {"id": "TR-1", "type": "task", "task": "T-001", "status": "reopened"},
                {"id": "TR-2", "type": "task", "task": "T-001", "status": "reopened"},
            ],
        },
        {
            "name": "exhaust_retry_budget",
            "expected": "EXHAUSTED",
            "tasks": task(),
            "kwargs": {"harness_result": "failed", "retry_count": 3, "failure_known": True},
        },
        {
            "name": "exhaust_no_progress_budget",
            "expected": "EXHAUSTED",
            "tasks": task(),
            "kwargs": {"no_progress_count": 2},
        },
        {
            "name": "complete_terminal",
            "expected": "COMPLETE",
            "tasks": task(status="[x]"),
            "kwargs": {"terminal_evidence": True},
        },
        {
            "name": "block_schema_change",
            "expected": "BLOCKED_DECISION",
            "tasks": task(),
            "kwargs": {"changed_files": ["prisma/schema.prisma"]},
        },
    ]


def run_scenarios(run_dir: Path) -> list[dict]:
    rows = []
    for item in scenarios():
        fixture = run_dir / "fixtures" / item["name"]
        write_fixture(fixture, item["tasks"], item.get("events"))
        kwargs = {"changed_files": [], **item.get("kwargs", {})}
        result = drive_check.evaluate(fixture, **kwargs)
        expected = item["expected"]
        expected_non_stop = expected in drive_check.NON_STOP_STATES
        rows.append(
            {
                "name": item["name"],
                "expected": expected,
                "baseline_decision": "STOP",
                "drive_decision": result["decision"],
                "agreement": result["decision"] == expected,
                "baseline_unnecessary_stop": expected_non_stop,
                "drive_unnecessary_stop": expected_non_stop and result["decision"] in drive_check.STOP_STATES,
                "unsafe_crossing": not expected_non_stop and result["decision"] in drive_check.NON_STOP_STATES,
                "next_action": result["next_action"],
            }
        )
    return rows


def summarize(target: Path, run_dir: Path, rows: list[dict]) -> dict:
    total = len(rows)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "target": str(target),
        "run_dir": str(run_dir),
        "scenario_count": total,
        "scenario_agreement": sum(row["agreement"] for row in rows) / total if total else 0,
        "baseline_unnecessary_stops": sum(row["baseline_unnecessary_stop"] for row in rows),
        "drive_unnecessary_stops": sum(row["drive_unnecessary_stop"] for row in rows),
        "autonomous_task_transitions": sum(row["drive_decision"] == "ADVANCE" for row in rows),
        "useful_non_terminal_decisions": sum(row["drive_decision"] in drive_check.NON_STOP_STATES for row in rows),
        "unsafe_decision_crossings": sum(row["unsafe_crossing"] for row in rows),
        "scenarios": rows,
    }


def render(summary: dict) -> str:
    lines = ["# CodeRail Drive A/B Observation", ""]
    lines.append(f"Generated at: {summary['generated_at']}")
    lines.append(f"Run directory: {summary['run_dir']}")
    lines.append("")
    lines.append("## Metrics")
    lines.append("")
    lines.append(f"- Scenario agreement: {summary['scenario_agreement']:.0%}")
    lines.append(f"- Baseline unnecessary stops: {summary['baseline_unnecessary_stops']}")
    lines.append(f"- Drive unnecessary stops: {summary['drive_unnecessary_stops']}")
    lines.append(f"- Autonomous task transitions: {summary['autonomous_task_transitions']}")
    lines.append(f"- Useful non-terminal decisions: {summary['useful_non_terminal_decisions']}")
    lines.append(f"- Unsafe decision crossings: {summary['unsafe_decision_crossings']}")
    lines.append("")
    lines.append("## Scenarios")
    lines.append("")
    for row in summary["scenarios"]:
        marker = "pass" if row["agreement"] else "mismatch"
        lines.append(
            f"- {row['name']}: baseline={row['baseline_decision']}, "
            f"drive={row['drive_decision']}, expected={row['expected']} ({marker})"
        )
    lines.append("")
    lines.append("## Interpretation Boundary")
    lines.append("")
    lines.append("- This offline fixture harness validates deterministic policy behavior.")
    lines.append("- It does not prove real-world model quality, product correctness, or strategy quality.")
    lines.append("- Run artifacts must remain ignored; commit only the reusable harness and contracts.")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Observe baseline versus CodeRail Drive decisions")
    parser.add_argument("--target", default=".")
    parser.add_argument("--run-dir")
    args = parser.parse_args(argv)
    target = Path(args.target).resolve()
    if not target.exists():
        print(f"target does not exist: {target}", file=sys.stderr)
        return 2
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = Path(args.run_dir).resolve() if args.run_dir else target / ".coderail-runs" / "drive-observe" / stamp
    run_dir.mkdir(parents=True, exist_ok=True)
    rows = run_scenarios(run_dir)
    summary = summarize(target, run_dir, rows)
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    report = render(summary)
    (run_dir / "report.md").write_text(report, encoding="utf-8")
    print(report)
    return 1 if summary["scenario_agreement"] < 1 or summary["unsafe_decision_crossings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
