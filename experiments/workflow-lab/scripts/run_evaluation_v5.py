from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import subprocess
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterator


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "evaluation-v5"
PREFLIGHT = PROTOCOL / "preflight"
RESULTS = PROTOCOL / "results"
V4_RESULTS = ROOT / "evaluation-v4" / "results"
PROTOCOL_VERSION = "wp5-v5"
MODEL = "gpt-5.4"
REASONING = "medium"
POWERSHELL = r"C:\Program Files\PowerShell\7\pwsh.exe"
WORKFLOW_FILES = {
    "A": "A.md",
    "B": "B.md",
    "C5": "C.md",
    "C5p": "C5p.md",
}
NULL_METRICS = (
    "post_start_contract_corrections",
    "out_of_scope_edits",
    "first_pass_done",
    "reopened_or_post_close_defects",
    "promotion_reversals",
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def verify_freeze() -> dict[str, str]:
    freeze = read_json(PROTOCOL / "freeze.json")
    hashes: dict[str, str] = {}
    for relative, expected in freeze["sha256"].items():
        actual = hashlib.sha256((PROTOCOL / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError(f"Frozen input changed: {relative}")
        hashes[relative] = actual
    return hashes


def codex_version() -> str | None:
    try:
        result = subprocess.run(
            [POWERSHELL, "-NoLogo", "-NoProfile", "-Command", "codex -V"],
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def load_execution_plan() -> dict[str, Any]:
    manifest = read_json(PROTOCOL / "manifest.json")
    if manifest.get("protocol_version") != PROTOCOL_VERSION:
        raise RuntimeError("Manifest protocol version is not wp5-v5")

    design = manifest["trial_design"]
    primary = tuple(design["workflows"])
    contingency = tuple(design["contingency_workflows"])
    seeds = tuple(design["task_order_seeds"])
    sampling = {
        category: tuple(category_seeds)
        for category, category_seeds in design["sampling_plan"].items()
    }
    task_counts = Counter(task["category"] for task in manifest["tasks"])

    if set(primary + contingency) != set(WORKFLOW_FILES):
        raise RuntimeError("Manifest workflows do not match the v5 workflow map")
    if set(sampling) != set(task_counts):
        raise RuntimeError("Sampling plan does not cover every task category")
    for category, category_seeds in sampling.items():
        if not category_seeds or not set(category_seeds).issubset(seeds):
            raise RuntimeError(f"Invalid seed plan for category: {category}")

    expected_trials = len(primary) * sum(
        task_counts[category] * len(category_seeds)
        for category, category_seeds in sampling.items()
    )
    if expected_trials != design["expected_primary_trials"]:
        raise RuntimeError("Manifest expected_primary_trials is inconsistent")

    workflow_files = {
        workflow: PROTOCOL / "workflows" / WORKFLOW_FILES[workflow]
        for workflow in primary + contingency
    }
    if any(not path.is_file() for path in workflow_files.values()):
        raise RuntimeError("A declared workflow file is missing")

    return {
        "manifest": manifest,
        "primary_workflows": primary,
        "contingency_workflows": contingency,
        "seeds": seeds,
        "sampling_plan": sampling,
        "workflow_files": workflow_files,
        "expected_primary_trials": expected_trials,
    }


def iter_primary_batches(
    plan: dict[str, Any],
) -> Iterator[dict[str, Any]]:
    tasks = plan["manifest"]["tasks"]
    by_category: dict[str, list[dict[str, Any]]] = {
        category: [
            task for task in tasks if task["category"] == category
        ]
        for category in plan["sampling_plan"]
    }
    for seed in plan["seeds"]:
        for category, category_seeds in plan["sampling_plan"].items():
            if seed not in category_seeds:
                continue
            for workflow in plan["primary_workflows"]:
                ordered = list(by_category[category])
                random.Random(f"{seed}:{workflow}:{category}").shuffle(ordered)
                yield {
                    "seed": seed,
                    "workflow": workflow,
                    "category": category,
                    "task_ids": tuple(task["id"] for task in ordered),
                }


def parse_event_stream(stream: str) -> dict[str, Any]:
    thread_id = None
    usage: dict[str, Any] = {}
    completed = False
    failed = False
    for line in stream.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "thread.started":
            thread_id = event.get("thread_id")
        if event.get("type") == "turn.completed":
            completed = True
            usage = event.get("usage", {})
        if event.get("type") == "turn.failed":
            failed = True
    return {
        "thread_id": thread_id,
        "usage": usage,
        "total_tokens": int(usage.get("input_tokens", 0))
        + int(usage.get("output_tokens", 0)),
        "completed": completed,
        "failed": failed,
    }


def subject_prompt(
    workflow_text: str,
    workflow: str,
    tasks: list[dict[str, Any]],
) -> str:
    packets = []
    for task in tasks:
        packets.append(
            {
                "task_id": task["id"],
                "user_profile": task["user_profile"],
                "request": task["request"],
                "repository_evidence": task["repository_evidence"],
                "scripted_answers": [
                    {
                        "index": index,
                        "when": answer["when"],
                        "answer": answer["answer"],
                    }
                    for index, answer in enumerate(task["scripted_answers"])
                ],
            }
        )
    return f"""
You are a subject in a frozen contract-workflow evaluation.

Treatment label: {workflow}

{workflow_text}

Evaluate every task packet independently. This is an offline conversation
simulation. Initially use only request and repository evidence. Treat each
scripted answer as unavailable until you first record a materially matching
question in a turn; then record its index as scripted_answer_index. Never
consume a fallback-only answer on a quick path.

For a quick task, include one ready turn with question null. For guided work,
record one question per turn and consume answers in order only when relevant.
Stop once the contract is ready. Do not implement, score yourself, inspect the
filesystem, or discuss the experiment. Return JSON matching the supplied
schema, with protocol_version wp5-v5 and exactly one response per task.

TASK PACKETS
{json.dumps(packets, indent=2, ensure_ascii=True)}
""".strip()


def judge_prompt(judge_text: str, items: list[dict[str, Any]]) -> str:
    return f"""
{judge_text}

Judge every opaque item independently. Workflow and seed labels are
intentionally absent. Use the supplied hidden oracle only for adjudication.
Return exactly one observation per opaque id and JSON matching the supplied
schema.

OPAQUE ITEMS
{json.dumps({"items": items}, indent=2, ensure_ascii=True)}
""".strip()


def allocate_tokens(total: int, task_ids: list[str]) -> dict[str, int]:
    base, remainder = divmod(total, len(task_ids))
    return {
        task_id: base + (1 if index < remainder else 0)
        for index, task_id in enumerate(task_ids)
    }


def percentage(values: list[bool]) -> float | None:
    if not values:
        return None
    return round(sum(values) * 100 / len(values), 2)


def batch_paths(stem: str) -> tuple[Path, Path, Path]:
    return (
        RESULTS / "raw" / f"{stem}.json",
        RESULTS / "events" / f"{stem}.jsonl",
        RESULTS / "logs" / f"{stem}.stderr.log",
    )


def run_or_reuse_batch(
    *,
    stem: str,
    prompt: str,
    schema: Path,
    resume: bool,
) -> tuple[dict[str, Any], dict[str, Any], str]:
    raw_path, event_path, stderr_path = batch_paths(stem)
    if raw_path.exists() and event_path.exists():
        if not resume:
            raise RuntimeError(
                f"Completed batch exists; rerun with --resume: {stem}"
            )
        output = read_json(raw_path)
        event = parse_event_stream(event_path.read_text(encoding="utf-8"))
        if not event["completed"] or event["failed"]:
            raise RuntimeError(f"Existing batch did not complete cleanly: {stem}")
        return output, event, "reused"

    if any(path.exists() for path in (raw_path, event_path, stderr_path)):
        if not resume:
            raise RuntimeError(
                f"Partial batch exists; rerun with --resume: {stem}"
            )
        if raw_path.exists():
            raise RuntimeError(f"Raw output lacks its event stream: {stem}")
        if not event_path.exists() or not stderr_path.exists():
            raise RuntimeError(f"Incomplete failure evidence: {stem}")
        stream = event_path.read_text(encoding="utf-8")
        if '"type":"turn.failed"' not in stream:
            raise RuntimeError(f"Partial batch is not transport-retryable: {stem}")
        failure_dir = RESULTS / "failures"
        failure_dir.mkdir(parents=True, exist_ok=True)
        failed_events = failure_dir / f"{stem}-attempt-1.events.jsonl"
        failed_stderr = failure_dir / f"{stem}-attempt-1.stderr.log"
        failed_record = failure_dir / f"{stem}-attempt-1.json"
        if any(
            path.exists()
            for path in (failed_events, failed_stderr, failed_record)
        ):
            raise RuntimeError(f"Transport retry already consumed: {stem}")
        event = parse_event_stream(stream)
        event_path.replace(failed_events)
        stderr_path.replace(failed_stderr)
        write_json(
            failed_record,
            {
                "protocol_version": PROTOCOL_VERSION,
                "status": "transport-failed-before-output",
                "batch": stem,
                "attempt": 1,
                "retry_policy": "one identical-input transport retry",
                "thread_id": event["thread_id"],
                "events": failed_events.relative_to(RESULTS).as_posix(),
                "stderr": failed_stderr.relative_to(RESULTS).as_posix(),
            },
        )

    output, event = run_codex(
        prompt=prompt,
        schema=schema,
        output_path=raw_path,
        event_path=event_path,
        stderr_path=stderr_path,
    )
    if not event["completed"] or event["failed"]:
        raise RuntimeError(f"Batch returned without a clean completion: {stem}")
    return output, event, "executed"


def run_codex(
    *,
    prompt: str,
    schema: Path,
    output_path: Path,
    event_path: Path,
    stderr_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    if environment.get("CODERAIL_V5_DIRECT_NETWORK") == "1":
        for name in (
            "HTTP_PROXY",
            "HTTPS_PROXY",
            "ALL_PROXY",
            "http_proxy",
            "https_proxy",
            "all_proxy",
        ):
            environment.pop(name, None)
    with tempfile.TemporaryDirectory(prefix="coderail-wp5-v5-") as temp:
        codex_args = [
            "-a",
            "never",
            "exec",
            "--ephemeral",
            "--ignore-user-config",
            "--ignore-rules",
            "-m",
            MODEL,
            "-c",
            f'model_reasoning_effort="{REASONING}"',
            "-s",
            "read-only",
            "--skip-git-repo-check",
            "-C",
            temp,
            "--output-schema",
            str(schema.resolve()),
            "--json",
            "-o",
            str(output_path.resolve()),
            "-",
        ]
        powershell_command = "& codex " + " ".join(
            "'" + argument.replace("'", "''") + "'" for argument in codex_args
        )
        result = subprocess.run(
            [
                POWERSHELL,
                "-NoLogo",
                "-NoProfile",
                "-Command",
                powershell_command,
            ],
            input=prompt,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            env=environment,
        )

    event_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path.parent.mkdir(parents=True, exist_ok=True)
    event_path.write_text(result.stdout, encoding="utf-8")
    stderr_path.write_text(result.stderr, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError(
            f"Codex failed ({result.returncode}); see {stderr_path}"
        )
    return read_json(output_path), parse_event_stream(result.stdout)


def prepare_schema_preflight_retry(
    *,
    output_path: Path,
    event_path: Path,
    stderr_path: Path,
    record_path: Path,
) -> int:
    failed_record = PREFLIGHT / "schema-transport-failure.json"
    failed_events = PREFLIGHT / "schema-attempt-1-events.jsonl"
    failed_stderr = PREFLIGHT / "schema-attempt-1-stderr.log"

    if output_path.exists() or record_path.exists():
        raise RuntimeError("Refusing to overwrite completed schema preflight")
    if failed_record.exists():
        if event_path.exists() or stderr_path.exists():
            raise RuntimeError("A second schema preflight attempt already exists")
        return 2
    if not event_path.exists() and not stderr_path.exists():
        return 1
    if not event_path.exists() or not stderr_path.exists():
        raise RuntimeError("Incomplete schema preflight failure evidence")

    stream = event_path.read_text(encoding="utf-8")
    if '"type":"turn.failed"' not in stream or '"type":"turn.completed"' in stream:
        raise RuntimeError("Existing preflight is not a retryable transport failure")
    event = parse_event_stream(stream)
    event_path.replace(failed_events)
    stderr_path.replace(failed_stderr)
    write_json(
        failed_record,
        {
            "protocol_version": PROTOCOL_VERSION,
            "status": "transport-failed-before-output",
            "attempt": 1,
            "retry_policy": "one identical-input transport retry",
            "subject_batches_started": 0,
            "judge_batches_started": 0,
            "task_or_oracle_payloads_sent": 0,
            "thread_id": event["thread_id"],
            "events": failed_events.name,
            "stderr": failed_stderr.name,
        },
    )
    return 2


def schema_preflight() -> int:
    output_path = PREFLIGHT / "schema-output.json"
    event_path = PREFLIGHT / "schema-events.jsonl"
    stderr_path = PREFLIGHT / "schema-stderr.log"
    record_path = PREFLIGHT / "schema-compatibility.json"
    attempt = prepare_schema_preflight_retry(
        output_path=output_path,
        event_path=event_path,
        stderr_path=stderr_path,
        record_path=record_path,
    )

    hashes_before = verify_freeze()
    plan = load_execution_plan()
    prompt = """
This is a JSON-schema compatibility preflight. No evaluation task, hidden
oracle, workflow treatment, repository evidence, scripted answer, or user data
is present. Return exactly one response with protocol_version wp5-v5, task_id
__schema_preflight__, route quick, one turn whose question and
scripted_answer_index are null and whose draft_ready is true, a ready contract
whose G/T/S/V/X/P strings are "preflight", no promotions, and
stop_after_contract true.
""".strip()
    output, event = run_codex(
        prompt=prompt,
        schema=PROTOCOL / "model-output.schema.json",
        output_path=output_path,
        event_path=event_path,
        stderr_path=stderr_path,
    )
    responses = output.get("responses", [])
    if (
        output.get("protocol_version") != PROTOCOL_VERSION
        or len(responses) != 1
        or responses[0].get("task_id") != "__schema_preflight__"
    ):
        raise RuntimeError("Schema preflight returned an unexpected payload")

    hashes_after = verify_freeze()
    write_json(
        record_path,
        {
            "protocol_version": PROTOCOL_VERSION,
            "status": "passed",
            "model": MODEL,
            "reasoning_effort": REASONING,
            "schema": "model-output.schema.json",
            "request_kind": "schema-compatibility-only",
            "transport_attempts": attempt,
            "network_route": (
                "direct-via-host-tun"
                if os.environ.get("CODERAIL_V5_DIRECT_NETWORK") == "1"
                else "inherited"
            ),
            "subject_batches_started": 0,
            "judge_batches_started": 0,
            "task_payloads_sent": 0,
            "oracle_payloads_sent": 0,
            "task_or_oracle_payloads_sent": 0,
            "planned_primary_workflows": list(plan["primary_workflows"]),
            "planned_contingency_workflows": list(
                plan["contingency_workflows"]
            ),
            "planned_seeds": list(plan["seeds"]),
            "planned_primary_trials": plan["expected_primary_trials"],
            "frozen_hashes_unchanged": hashes_before == hashes_after,
            "thread_id": event["thread_id"],
            "usage": event["usage"],
        },
    )
    verify_freeze()
    return 0


def load_trial_records() -> list[dict[str, Any]]:
    trial_dir = RESULTS / "trials"
    if not trial_dir.exists():
        return []
    return [
        read_json(path)
        for path in sorted(trial_dir.glob("*.json"))
    ]


def metric_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    count_metrics = (
        "turns_before_readiness",
        "useful_questions",
        "user_visible_technical_choices",
        "unsupported_assumptions",
        "total_tokens",
        "human_interruptions",
    )
    summary: dict[str, Any] = {"trials": len(records)}
    for metric in count_metrics:
        values = [record["observation"][metric] for record in records]
        summary[metric] = sum(values)
        summary[f"{metric}_per_trial"] = (
            round(sum(values) / len(values), 4) if values else None
        )
    summary["quick_path_correct_pct"] = percentage(
        [record["observation"]["quick_path_correct"] for record in records]
    )
    return summary


def bootstrap_relative_assumption_reduction(
    records: list[dict[str, Any]],
    seeds: tuple[str, ...],
) -> dict[str, Any]:
    threshold = {"ambiguous-cross-module", "high-risk-persistent"}
    task_category = {
        task["id"]: task["category"]
        for task in load_execution_plan()["manifest"]["tasks"]
    }
    seed_means: dict[str, dict[str, float]] = {}
    for seed in seeds:
        seed_means[seed] = {}
        for workflow in ("A", "C5"):
            selected = [
                record
                for record in records
                if record["seed"] == seed
                and record["workflow"] == workflow
                and task_category[record["task_id"]] in threshold
            ]
            if selected:
                seed_means[seed][workflow] = sum(
                    record["observation"]["unsupported_assumptions"]
                    for record in selected
                ) / len(selected)

    complete_seeds = [
        seed
        for seed in seeds
        if set(seed_means[seed]) == {"A", "C5"}
    ]
    if not complete_seeds:
        return {
            "status": "pending",
            "complete_seeds": 0,
            "point_estimate_pct": None,
            "bootstrap_ci95_pct": None,
        }

    pooled_a = sum(seed_means[seed]["A"] for seed in complete_seeds)
    pooled_c = sum(seed_means[seed]["C5"] for seed in complete_seeds)
    if pooled_a == 0:
        return {
            "status": "untestable-baseline-floor",
            "complete_seeds": len(complete_seeds),
            "point_estimate_pct": None,
            "bootstrap_ci95_pct": None,
        }

    point = (pooled_a - pooled_c) * 100 / pooled_a
    randomizer = random.Random("coderail-wp5-v5-bootstrap")
    estimates = []
    for _ in range(10_000):
        sample = [
            randomizer.choice(complete_seeds)
            for _ in range(len(complete_seeds))
        ]
        sample_a = sum(seed_means[seed]["A"] for seed in sample)
        sample_c = sum(seed_means[seed]["C5"] for seed in sample)
        if sample_a:
            estimates.append((sample_a - sample_c) * 100 / sample_a)
    estimates.sort()
    interval = None
    if estimates:
        low = estimates[int(0.025 * (len(estimates) - 1))]
        high = estimates[int(0.975 * (len(estimates) - 1))]
        interval = [round(low, 2), round(high, 2)]
    return {
        "status": "testable",
        "complete_seeds": len(complete_seeds),
        "point_estimate_pct": round(point, 2),
        "bootstrap_ci95_pct": interval,
    }


def matched_v4_c_summary(
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    v4_by_task = {
        record["task_id"]: record
        for path in (V4_RESULTS / "trials").glob("C-*.json")
        for record in [read_json(path)]
    }
    selected = [
        v4_by_task[record["task_id"]]
        for record in records
        if record["workflow"] == "C5"
    ]
    return metric_summary(selected)


def aggregate_results(
    records: list[dict[str, Any]],
    state: dict[str, Any],
) -> dict[str, Any]:
    plan = load_execution_plan()
    task_category = {
        task["id"]: task["category"]
        for task in plan["manifest"]["tasks"]
    }
    workflows = {
        workflow: metric_summary(
            [record for record in records if record["workflow"] == workflow]
        )
        for workflow in plan["primary_workflows"]
    }
    categories: dict[str, dict[str, Any]] = {}
    for category in plan["sampling_plan"]:
        categories[category] = {
            workflow: metric_summary(
                [
                    record
                    for record in records
                    if record["workflow"] == workflow
                    and task_category[record["task_id"]] == category
                ]
            )
            for workflow in plan["primary_workflows"]
        }

    complete = len(records) == plan["expected_primary_trials"]
    c5_records = [
        record for record in records if record["workflow"] == "C5"
    ]
    provider_choices = sum(
        record["observation"]["user_visible_technical_choices"]
        for record in c5_records
    )
    gate1 = {
        "name": "provider-question-elimination",
        "value": provider_choices,
        "threshold": 0,
        "status": (
            "failed"
            if provider_choices
            else "passed" if complete else "passed-so-far"
        ),
    }

    threshold_records = [
        record
        for record in records
        if task_category[record["task_id"]]
        in {"ambiguous-cross-module", "high-risk-persistent"}
    ]
    threshold_means: dict[str, float | None] = {}
    for workflow in ("A", "C5"):
        selected = [
            record
            for record in threshold_records
            if record["workflow"] == workflow
        ]
        threshold_means[workflow] = (
            sum(
                record["observation"]["unsupported_assumptions"]
                for record in selected
            ) / len(selected)
            if selected
            else None
        )
    relative = bootstrap_relative_assumption_reduction(
        records,
        plan["seeds"],
    )
    absolute_pass = (
        threshold_means["A"] is not None
        and threshold_means["C5"] is not None
        and threshold_means["C5"] <= threshold_means["A"]
    )
    relative_pass = (
        relative["status"] == "untestable-baseline-floor"
        or (
            relative["status"] == "testable"
            and relative["point_estimate_pct"] >= 25
        )
    )
    gate2 = {
        "name": "threshold-assumptions",
        "pooled_mean": threshold_means,
        "absolute_c5_lte_a": absolute_pass,
        "relative_reduction": relative,
        "status": (
            "passed"
            if complete and absolute_pass and relative_pass
            else "failed"
            if complete
            else "pending"
        ),
    }

    clear = categories["clear-local-reversible"]["C5"]
    gate3_pass = clear["quick_path_correct_pct"] == 100
    gate3 = {
        "name": "clear-quick-path",
        "value_pct": clear["quick_path_correct_pct"],
        "threshold_pct": 100,
        "status": "passed" if gate3_pass else "failed",
    }

    token_ratios: dict[str, float | None] = {}
    for category, summaries in categories.items():
        a_tokens = summaries["A"]["total_tokens"]
        c_tokens = summaries["C5"]["total_tokens"]
        token_ratios[category] = (
            round(c_tokens / a_tokens, 4) if a_tokens else None
        )
    gate4_pass = complete and all(
        ratio is not None and ratio <= 1.15
        for ratio in token_ratios.values()
    )
    gate4 = {
        "name": "category-pooled-token-economy",
        "c5_to_a_ratios": token_ratios,
        "threshold_ratio": 1.15,
        "status": "passed" if gate4_pass else "failed" if complete else "pending",
    }

    matched_v4 = matched_v4_c_summary(records)
    c5_summary = metric_summary(c5_records)
    turns_pass = (
        c5_summary["turns_before_readiness_per_trial"] is not None
        and matched_v4["turns_before_readiness_per_trial"] is not None
        and c5_summary["turns_before_readiness_per_trial"]
        <= matched_v4["turns_before_readiness_per_trial"]
    )
    interruptions_pass = (
        c5_summary["human_interruptions_per_trial"] is not None
        and matched_v4["human_interruptions_per_trial"] is not None
        and c5_summary["human_interruptions_per_trial"]
        <= matched_v4["human_interruptions_per_trial"]
    )
    gate5 = {
        "name": "no-turn-or-interruption-regression",
        "c5": {
            "turns_per_trial": c5_summary[
                "turns_before_readiness_per_trial"
            ],
            "interruptions_per_trial": c5_summary[
                "human_interruptions_per_trial"
            ],
        },
        "matched_v4_c": {
            "turns_per_trial": matched_v4[
                "turns_before_readiness_per_trial"
            ],
            "interruptions_per_trial": matched_v4[
                "human_interruptions_per_trial"
            ],
        },
        "status": (
            "passed"
            if complete and turns_pass and interruptions_pass
            else "failed"
            if complete
            else "pending"
        ),
    }
    gates = [gate1, gate2, gate3, gate4, gate5]

    if state.get("early_stop"):
        disposition = "REVISE_PROVIDER_GATE"
    elif not complete:
        disposition = "IN_PROGRESS"
    elif all(gate["status"] == "passed" for gate in gates):
        disposition = "EARN_IMPLEMENTATION_FOLLOW_THROUGH"
    elif (
        threshold_means["A"] is not None
        and threshold_means["C5"] is not None
        and threshold_means["C5"] > threshold_means["A"]
    ):
        disposition = "RUN_C5P_CONTINGENCY"
    elif (
        all(gate["status"] == "passed" for gate in gates[:3])
        and gate4["status"] == "failed"
    ):
        disposition = "REVISE_OUTPUT_ECONOMY"
    else:
        disposition = "REVISE"

    return {
        "protocol_version": PROTOCOL_VERSION,
        "planned_primary_trials": plan["expected_primary_trials"],
        "completed_primary_trials": len(records),
        "completed_seeds": state.get("completed_seeds", []),
        "workflows": workflows,
        "categories": categories,
        "gates": {gate["name"]: gate for gate in gates},
        "treatment_disposition": disposition,
        "implementation_evidence_complete": False,
        "decision": "INSUFFICIENT_IMPLEMENTATION_EVIDENCE",
    }


def initial_run_state(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "protocol_version": PROTOCOL_VERSION,
        "model": MODEL,
        "reasoning_effort": REASONING,
        "cli_version": codex_version(),
        "planned_seeds": list(plan["seeds"]),
        "planned_primary_trials": plan["expected_primary_trials"],
        "completed_seeds": [],
        "active_seed": None,
        "seed_status": {},
        "early_stop": None,
        "subject_batches": [],
        "judge_batches": [],
    }


def load_run_state(plan: dict[str, Any]) -> dict[str, Any]:
    path = RESULTS / "run-state.json"
    if not path.exists():
        return initial_run_state(plan)
    state = read_json(path)
    if (
        state.get("protocol_version") != PROTOCOL_VERSION
        or state.get("planned_seeds") != list(plan["seeds"])
        or state.get("planned_primary_trials") != plan["expected_primary_trials"]
    ):
        raise RuntimeError("Existing run state does not match the frozen plan")
    return state


def expected_seed_categories(
    plan: dict[str, Any],
    seed: str,
) -> list[str]:
    return [
        category
        for category, seeds in plan["sampling_plan"].items()
        if seed in seeds
    ]


def validate_seed_transition(
    state: dict[str, Any],
    plan: dict[str, Any],
    seed: str,
    *,
    resume: bool,
) -> None:
    if state.get("early_stop"):
        raise RuntimeError("The frozen provider gate already stopped execution")
    completed = state["completed_seeds"]
    if len(completed) >= len(plan["seeds"]):
        raise RuntimeError("All frozen seeds are already complete")
    next_seed = plan["seeds"][len(completed)]
    if seed != next_seed:
        raise RuntimeError(f"Expected next seed {next_seed}, not {seed}")
    if state.get("active_seed") not in (None, seed):
        raise RuntimeError(f"Another seed is active: {state['active_seed']}")
    if state.get("active_seed") == seed and not resume:
        raise RuntimeError("Seed is partially active; rerun with --resume")


def run_seed(seed: str, *, resume: bool) -> int:
    verify_freeze()
    preflight = read_json(PREFLIGHT / "schema-compatibility.json")
    if (
        preflight.get("status") != "passed"
        or preflight.get("task_or_oracle_payloads_sent") != 0
    ):
        raise RuntimeError("The zero-task schema preflight is not complete")

    plan = load_execution_plan()
    if seed not in plan["seeds"]:
        raise RuntimeError(f"Unknown frozen seed: {seed}")
    state = load_run_state(plan)
    validate_seed_transition(state, plan, seed, resume=resume)

    state["active_seed"] = seed
    state["seed_status"][seed] = "running"
    if state.get("failure"):
        state.setdefault("failure_history", []).append(state.pop("failure"))
    write_json(RESULTS / "run-state.json", state)

    manifest = plan["manifest"]
    task_by_id = {task["id"]: task for task in manifest["tasks"]}
    categories = expected_seed_categories(plan, seed)
    by_category = {
        category: [
            task
            for task in manifest["tasks"]
            if task["category"] == category
        ]
        for category in categories
    }
    subject_responses: dict[tuple[str, str], dict[str, Any]] = {}
    subject_tokens: dict[tuple[str, str], int] = {}
    subject_paths: dict[tuple[str, str], tuple[str, str | None]] = {}

    try:
        for category in categories:
            for workflow in plan["primary_workflows"]:
                ordered = list(by_category[category])
                random.Random(f"{seed}:{workflow}:{category}").shuffle(ordered)
                stem = f"subject-{seed}-{workflow}-{category}"
                workflow_text = plan["workflow_files"][workflow].read_text(
                    encoding="utf-8"
                )
                output, event, source = run_or_reuse_batch(
                    stem=stem,
                    prompt=subject_prompt(workflow_text, workflow, ordered),
                    schema=PROTOCOL / "model-output.schema.json",
                    resume=resume,
                )
                expected = {task["id"] for task in ordered}
                responses = output.get("responses", [])
                actual = {response["task_id"] for response in responses}
                if (
                    output.get("protocol_version") != PROTOCOL_VERSION
                    or actual != expected
                    or len(responses) != len(expected)
                ):
                    raise RuntimeError(f"Subject batch mismatch: {stem}")
                token_map = allocate_tokens(
                    event["total_tokens"],
                    [task["id"] for task in ordered],
                )
                raw_path = batch_paths(stem)[0]
                for response in responses:
                    key = (workflow, response["task_id"])
                    subject_responses[key] = response
                    subject_tokens[key] = token_map[response["task_id"]]
                    subject_paths[key] = (
                        raw_path.relative_to(PROTOCOL).as_posix(),
                        event["thread_id"],
                    )
                if not any(
                    batch["seed"] == seed
                    and batch["workflow"] == workflow
                    and batch["category"] == category
                    for batch in state["subject_batches"]
                ):
                    state["subject_batches"].append(
                        {
                            "seed": seed,
                            "workflow": workflow,
                            "category": category,
                            "status": "completed",
                            "tasks": [task["id"] for task in ordered],
                            "thread_id": event["thread_id"],
                            "usage": event["usage"],
                            "source": source,
                        }
                    )
                    write_json(RESULTS / "run-state.json", state)

        judge_text = (PROTOCOL / "judge.md").read_text(encoding="utf-8")
        opaque_map: dict[str, tuple[str, str]] = {}
        judge_observations: dict[str, dict[str, Any]] = {}
        for category in categories:
            items = []
            for task in by_category[category]:
                for workflow in plan["primary_workflows"]:
                    opaque_id = hashlib.sha256(
                        f"{seed}:{category}:{task['id']}:{workflow}".encode()
                    ).hexdigest()[:16]
                    opaque_map[opaque_id] = (workflow, task["id"])
                    items.append(
                        {
                            "opaque_id": opaque_id,
                            "user_profile": task["user_profile"],
                            "request": task["request"],
                            "repository_evidence": task[
                                "repository_evidence"
                            ],
                            "scripted_answers": task["scripted_answers"],
                            "oracle": task["oracle"],
                            "subject_response": subject_responses[
                                (workflow, task["id"])
                            ],
                        }
                    )
            random.Random(f"{seed}:judge:{category}").shuffle(items)
            judge_input = RESULTS / "judge-inputs" / f"{seed}-{category}.json"
            payload = {"items": items}
            if judge_input.exists():
                if read_json(judge_input) != payload:
                    raise RuntimeError(f"Judge input changed: {judge_input}")
            else:
                write_json(judge_input, payload)

            stem = f"judge-{seed}-{category}"
            output, event, source = run_or_reuse_batch(
                stem=stem,
                prompt=judge_prompt(judge_text, items),
                schema=PROTOCOL / "judge-output.schema.json",
                resume=resume,
            )
            observations = output.get("observations", [])
            expected = {item["opaque_id"] for item in items}
            actual = {
                observation["opaque_id"] for observation in observations
            }
            if actual != expected or len(observations) != len(expected):
                raise RuntimeError(f"Judge batch mismatch: {stem}")
            for observation in observations:
                judge_observations[observation["opaque_id"]] = observation
            if not any(
                batch["seed"] == seed and batch["category"] == category
                for batch in state["judge_batches"]
            ):
                state["judge_batches"].append(
                    {
                        "seed": seed,
                        "category": category,
                        "status": "completed",
                        "items": len(items),
                        "thread_id": event["thread_id"],
                        "usage": event["usage"],
                        "source": source,
                    }
                )
                write_json(RESULTS / "run-state.json", state)

        write_json(
            RESULTS / "opaque-maps" / f"{seed}.json",
            {
                opaque_id: {
                    "workflow": workflow,
                    "seed": seed,
                    "task_id": task_id,
                }
                for opaque_id, (workflow, task_id) in opaque_map.items()
            },
        )

        for opaque_id, (workflow, task_id) in opaque_map.items():
            judged = judge_observations[opaque_id]
            response = subject_responses[(workflow, task_id)]
            oracle = task_by_id[task_id]["oracle"]
            has_question = any(turn["question"] for turn in response["turns"])
            quick_correct = response["route"] == oracle["expected_route"]
            if oracle["expected_route"] == "quick":
                quick_correct = quick_correct and not has_question
            observation = {
                "turns_before_readiness": judged["turns_before_readiness"],
                "useful_questions": judged["useful_questions"],
                "user_visible_technical_choices": judged[
                    "user_visible_technical_choices"
                ],
                "unsupported_assumptions": judged["unsupported_assumptions"],
                "post_start_contract_corrections": None,
                "out_of_scope_edits": None,
                "first_pass_done": None,
                "reopened_or_post_close_defects": None,
                "promotion_reversals": None,
                "total_tokens": subject_tokens[(workflow, task_id)],
                "human_interruptions": judged["human_interruptions"],
                "quick_path_correct": quick_correct,
            }
            raw_path, thread_id = subject_paths[(workflow, task_id)]
            record = {
                "protocol_version": PROTOCOL_VERSION,
                "task_id": task_id,
                "workflow": workflow,
                "seed": seed,
                "model": {
                    "name": MODEL,
                    "reasoning_effort": REASONING,
                    "cli_version": state["cli_version"],
                },
                "response": {
                    "raw_path": raw_path,
                    "session_id": thread_id,
                },
                "observation": observation,
            }
            write_json(
                RESULTS / "trials" / f"{seed}-{workflow}-{task_id}.json",
                record,
            )
            write_json(
                RESULTS
                / "judge-notes"
                / f"{seed}-{workflow}-{task_id}.json",
                {
                    "protocol_version": PROTOCOL_VERSION,
                    "task_id": task_id,
                    "workflow": workflow,
                    "seed": seed,
                    "notes": judged["notes"],
                },
            )

        seed_records = [
            record
            for record in load_trial_records()
            if record["seed"] == seed
        ]
        expected_cells = len(plan["primary_workflows"]) * sum(
            len(by_category[category]) for category in categories
        )
        if len(seed_records) != expected_cells:
            raise RuntimeError(
                f"Seed {seed} has {len(seed_records)} of {expected_cells} cells"
            )
        provider_choices = sum(
            record["observation"]["user_visible_technical_choices"]
            for record in seed_records
            if record["workflow"] == "C5"
        )
        state["active_seed"] = None
        state["completed_seeds"].append(seed)
        state["seed_status"][seed] = (
            "provider-gate-failed" if provider_choices else "completed"
        )
        if provider_choices:
            state["early_stop"] = {
                "gate": "provider-question-elimination",
                "seed": seed,
                "observed_user_visible_technical_choices": provider_choices,
                "rule": "do not run further seeds or C5p",
            }
        write_json(RESULTS / "run-state.json", state)
        write_json(
            RESULTS / "aggregate.json",
            aggregate_results(load_trial_records(), state),
        )
        verify_freeze()
    except Exception as error:
        state["seed_status"][seed] = "failed"
        state["failure"] = {"seed": seed, "message": str(error)}
        write_json(RESULTS / "run-state.json", state)
        raise
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--schema-preflight",
        action="store_true",
        help="Validate the frozen subject schema without task or oracle data.",
    )
    parser.add_argument(
        "--print-plan",
        action="store_true",
        help="Print the manifest-derived primary execution plan.",
    )
    parser.add_argument(
        "--run-seed",
        choices=tuple(
            f"coderail-wp5-v5-s{index}" for index in range(1, 6)
        ),
        help="Run one frozen seed, including its blind-judge batches.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Reuse completed batches after a recorded local failure.",
    )
    args = parser.parse_args()

    if args.schema_preflight:
        return schema_preflight()
    if args.run_seed:
        return run_seed(args.run_seed, resume=args.resume)
    if args.print_plan:
        plan = load_execution_plan()
        batches = list(iter_primary_batches(plan))
        print(
            json.dumps(
                {
                    "protocol_version": PROTOCOL_VERSION,
                    "primary_workflows": plan["primary_workflows"],
                    "contingency_workflows": plan[
                        "contingency_workflows"
                    ],
                    "seeds": plan["seeds"],
                    "sampling_plan": plan["sampling_plan"],
                    "subject_batches": len(batches),
                    "primary_trials": sum(
                        len(batch["task_ids"]) for batch in batches
                    ),
                },
                indent=2,
            )
        )
        return 0
    parser.error(
        "No action selected. Use --run-seed to execute the next frozen seed."
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
