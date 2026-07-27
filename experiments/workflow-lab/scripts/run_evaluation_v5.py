from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterator


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "evaluation-v5"
PREFLIGHT = PROTOCOL / "preflight"
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
    for line in stream.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "thread.started":
            thread_id = event.get("thread_id")
        if event.get("type") == "turn.completed":
            usage = event.get("usage", {})
    return {"thread_id": thread_id, "usage": usage}


def run_codex(
    *,
    prompt: str,
    schema: Path,
    output_path: Path,
    event_path: Path,
    stderr_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
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


def schema_preflight() -> int:
    output_path = PREFLIGHT / "schema-output.json"
    event_path = PREFLIGHT / "schema-events.jsonl"
    stderr_path = PREFLIGHT / "schema-stderr.log"
    record_path = PREFLIGHT / "schema-compatibility.json"
    if any(
        path.exists()
        for path in (output_path, event_path, stderr_path, record_path)
    ):
        raise RuntimeError("Refusing to overwrite existing schema preflight")

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
    args = parser.parse_args()

    if args.schema_preflight:
        return schema_preflight()
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
        "No action selected. Subject execution is intentionally unavailable "
        "until the schema preflight checkpoint is closed."
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
