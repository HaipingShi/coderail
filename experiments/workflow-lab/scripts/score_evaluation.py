from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


COUNT_METRICS = (
    "turns_before_readiness",
    "useful_questions",
    "user_visible_technical_choices",
    "unsupported_assumptions",
    "post_start_contract_corrections",
    "out_of_scope_edits",
    "reopened_or_post_close_defects",
    "promotion_reversals",
    "total_tokens",
    "human_interruptions",
)


def percentage(values: list[bool]) -> float | None:
    if not values:
        return None
    return round(sum(values) * 100 / len(values), 2)


def aggregate(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[record["workflow"]].append(record)

    workflows: dict[str, dict[str, Any]] = {}
    for workflow in ("A", "B", "C"):
        trials = grouped.get(workflow, [])
        summary: dict[str, Any] = {"trials": len(trials)}
        for metric in COUNT_METRICS:
            values = [
                record["observation"][metric]
                for record in trials
                if record["observation"][metric] is not None
            ]
            summary[metric] = sum(values) if values else None
        summary["first_pass_done_pct"] = percentage(
            [
                record["observation"]["first_pass_done"]
                for record in trials
                if record["observation"]["first_pass_done"] is not None
            ]
        )
        summary["quick_path_correct_pct"] = percentage(
            [record["observation"]["quick_path_correct"] for record in trials]
        )
        workflows[workflow] = summary

    return {
        "protocol_version": "wp5-v1",
        "workflows": workflows,
        "implementation_evidence_complete": all(
            workflow["first_pass_done_pct"] is not None
            for workflow in workflows.values()
            if workflow["trials"]
        ),
    }


def load_records(paths: list[Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in paths:
        candidates = sorted(path.rglob("*.json")) if path.is_dir() else [path]
        for candidate in candidates:
            payload = json.loads(candidate.read_text(encoding="utf-8"))
            if isinstance(payload, list):
                records.extend(payload)
            else:
                records.append(payload)
    return records


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Aggregate independently observed Guided Convergence trials."
    )
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = aggregate(load_records(args.paths))
    rendered = json.dumps(report, indent=2, ensure_ascii=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
