from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "evaluation-v3"
RESULTS = PROTOCOL / "results"
WORKFLOWS = ("A", "B", "C")
MODEL = "gpt-5.4"
REASONING = "medium"
SEED = "coderail-wp5-v3"
POWERSHELL = r"C:\Program Files\PowerShell\7\pwsh.exe"
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


def verify_freeze() -> None:
    freeze = read_json(PROTOCOL / "freeze.json")
    for relative, expected in freeze["sha256"].items():
        actual = hashlib.sha256((PROTOCOL / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError(f"Frozen input changed: {relative}")


def codex_version() -> str:
    result = subprocess.run(
        [POWERSHELL, "-NoLogo", "-NoProfile", "-Command", "codex -V"],
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


def run_codex(
    *,
    prompt: str,
    schema: Path,
    output_path: Path,
    event_path: Path,
    stderr_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="coderail-wp5-v3-") as temp:
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
            capture_output=True,
        )

    event_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path.parent.mkdir(parents=True, exist_ok=True)
    event_path.write_text(result.stdout, encoding="utf-8")
    stderr_path.write_text(result.stderr, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError(
            f"Codex failed ({result.returncode}); see {stderr_path}"
        )

    thread_id = None
    usage: dict[str, Any] = {}
    for line in result.stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "thread.started":
            thread_id = event.get("thread_id")
        if event.get("type") == "turn.completed":
            usage = event.get("usage", {})

    return read_json(output_path), {
        "thread_id": thread_id,
        "usage": usage,
        "total_tokens": int(usage.get("input_tokens", 0))
        + int(usage.get("output_tokens", 0)),
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
schema, with protocol_version wp5-v3 and exactly one response per task.

TASK PACKETS
{json.dumps(packets, indent=2, ensure_ascii=True)}
""".strip()


def judge_prompt(
    judge_text: str,
    items: list[dict[str, Any]],
) -> str:
    return f"""
{judge_text}

Judge every opaque item independently. The workflow label is intentionally
absent. Use the supplied hidden oracle only for adjudication. Return exactly
one observation per opaque id and JSON matching the supplied schema.

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


def aggregate(records: list[dict[str, Any]]) -> dict[str, Any]:
    count_metrics = (
        "turns_before_readiness",
        "useful_questions",
        "user_visible_technical_choices",
        "unsupported_assumptions",
        "total_tokens",
        "human_interruptions",
    )
    workflows: dict[str, Any] = {}
    for workflow in WORKFLOWS:
        selected = [record for record in records if record["workflow"] == workflow]
        summary: dict[str, Any] = {"trials": len(selected)}
        for metric in count_metrics:
            summary[metric] = sum(
                record["observation"][metric] for record in selected
            )
        summary["quick_path_correct_pct"] = percentage(
            [record["observation"]["quick_path_correct"] for record in selected]
        )
        summary["first_pass_done_pct"] = percentage(
            [
                record["observation"]["first_pass_done"]
                for record in selected
                if record["observation"]["first_pass_done"] is not None
            ]
        )
        workflows[workflow] = summary
    return {
        "protocol_version": "wp5-v3",
        "workflows": workflows,
        "implementation_evidence_complete": False,
        "decision": "INSUFFICIENT_IMPLEMENTATION_EVIDENCE",
    }


def main() -> int:
    global RESULTS
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--results",
        type=Path,
        default=RESULTS,
        help="Result directory; defaults to evaluation-v3/results.",
    )
    args = parser.parse_args()
    RESULTS = args.results.resolve()

    if RESULTS.exists() and any(RESULTS.rglob("*")):
        raise RuntimeError(f"Refusing to overwrite existing results: {RESULTS}")

    verify_freeze()
    manifest = read_json(PROTOCOL / "manifest.json")
    tasks = manifest["tasks"]
    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for task in tasks:
        by_category[task["category"]].append(task)

    metadata: dict[str, Any] = {
        "protocol_version": "wp5-v3",
        "model": MODEL,
        "reasoning_effort": REASONING,
        "codex_version": codex_version(),
        "token_allocation": "batch total divided across task cells",
        "subject_batches": [],
        "judge_batches": [],
    }
    subject_responses: dict[tuple[str, str], dict[str, Any]] = {}
    subject_tokens: dict[tuple[str, str], int] = {}
    subject_paths: dict[tuple[str, str], tuple[str, str | None]] = {}

    try:
        for workflow in WORKFLOWS:
            workflow_text = (
                PROTOCOL / "workflows" / f"{workflow}.md"
            ).read_text(encoding="utf-8")
            for category, category_tasks in sorted(by_category.items()):
                ordered = list(category_tasks)
                random.Random(f"{SEED}:{workflow}:{category}").shuffle(ordered)
                stem = f"subject-{workflow}-{category}"
                raw_path = RESULTS / "raw" / f"{stem}.json"
                output, event = run_codex(
                    prompt=subject_prompt(workflow_text, workflow, ordered),
                    schema=PROTOCOL / "model-output.schema.json",
                    output_path=raw_path,
                    event_path=RESULTS / "events" / f"{stem}.jsonl",
                    stderr_path=RESULTS / "logs" / f"{stem}.stderr.log",
                )
                expected = {task["id"] for task in ordered}
                actual = {response["task_id"] for response in output["responses"]}
                if actual != expected or len(output["responses"]) != len(expected):
                    raise RuntimeError(f"Subject batch mismatch: {stem}")
                token_map = allocate_tokens(
                    event["total_tokens"], [task["id"] for task in ordered]
                )
                for response in output["responses"]:
                    key = (workflow, response["task_id"])
                    subject_responses[key] = response
                    subject_tokens[key] = token_map[response["task_id"]]
                    subject_paths[key] = (
                        raw_path.relative_to(PROTOCOL).as_posix(),
                        event["thread_id"],
                    )
                metadata["subject_batches"].append(
                    {
                        "workflow": workflow,
                        "category": category,
                        "status": "completed",
                        "tasks": [task["id"] for task in ordered],
                        "thread_id": event["thread_id"],
                        "usage": event["usage"],
                    }
                )

        opaque_map: dict[str, tuple[str, str]] = {}
        judge_observations: dict[str, dict[str, Any]] = {}
        judge_text = (PROTOCOL / "judge.md").read_text(encoding="utf-8")
        for category, category_tasks in sorted(by_category.items()):
            items = []
            for task in category_tasks:
                for workflow in WORKFLOWS:
                    opaque_id = hashlib.sha256(
                        f"{SEED}:{category}:{task['id']}:{workflow}".encode()
                    ).hexdigest()[:16]
                    opaque_map[opaque_id] = (workflow, task["id"])
                    items.append(
                        {
                            "opaque_id": opaque_id,
                            "user_profile": task["user_profile"],
                            "request": task["request"],
                            "repository_evidence": task["repository_evidence"],
                            "scripted_answers": task["scripted_answers"],
                            "oracle": task["oracle"],
                            "subject_response": subject_responses[
                                (workflow, task["id"])
                            ],
                        }
                    )
            random.Random(f"{SEED}:judge:{category}").shuffle(items)
            write_json(RESULTS / "judge-inputs" / f"{category}.json", {"items": items})
            stem = f"judge-{category}"
            output, event = run_codex(
                prompt=judge_prompt(judge_text, items),
                schema=PROTOCOL / "judge-output.schema.json",
                output_path=RESULTS / "raw" / f"{stem}.json",
                event_path=RESULTS / "events" / f"{stem}.jsonl",
                stderr_path=RESULTS / "logs" / f"{stem}.stderr.log",
            )
            expected = {item["opaque_id"] for item in items}
            actual = {
                observation["opaque_id"]
                for observation in output["observations"]
            }
            if actual != expected or len(output["observations"]) != len(expected):
                raise RuntimeError(f"Judge batch mismatch: {stem}")
            for observation in output["observations"]:
                judge_observations[observation["opaque_id"]] = observation
            metadata["judge_batches"].append(
                {
                    "category": category,
                    "status": "completed",
                    "items": len(items),
                    "thread_id": event["thread_id"],
                    "usage": event["usage"],
                }
            )

        write_json(
            RESULTS / "opaque-map.json",
            {
                opaque_id: {"workflow": key[0], "task_id": key[1]}
                for opaque_id, key in opaque_map.items()
            },
        )

        records = []
        task_by_id = {task["id"]: task for task in tasks}
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
                "protocol_version": "wp5-v3",
                "task_id": task_id,
                "workflow": workflow,
                "model": {
                    "name": MODEL,
                    "reasoning_effort": REASONING,
                    "cli_version": metadata["codex_version"],
                },
                "response": {
                    "raw_path": raw_path,
                    "session_id": thread_id,
                },
                "observation": observation,
                "judge_notes": judged["notes"],
            }
            records.append(record)
            write_json(
                RESULTS / "trials" / f"{workflow}-{task_id}.json",
                record,
            )

        write_json(RESULTS / "aggregate.json", aggregate(records))
        write_json(RESULTS / "run-metadata.json", metadata)
        verify_freeze()
    except Exception as error:
        metadata["failure"] = str(error)
        write_json(RESULTS / "run-metadata.json", metadata)
        raise

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
