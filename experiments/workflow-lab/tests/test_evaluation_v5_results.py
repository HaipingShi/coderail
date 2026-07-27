from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
V5 = ROOT / "evaluation-v5"
RESULTS = V5 / "results"
RUNNER_PATH = ROOT / "scripts" / "run_evaluation_v5.py"
NULL_METRICS = (
    "post_start_contract_corrections",
    "out_of_scope_edits",
    "first_pass_done",
    "reopened_or_post_close_defects",
    "promotion_reversals",
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_runner() -> Any:
    spec = importlib.util.spec_from_file_location(
        "run_evaluation_v5_results",
        RUNNER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load the v5 runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def synthetic_records() -> list[dict[str, Any]]:
    runner = load_runner()
    plan = runner.load_execution_plan()
    tasks = {
        task["id"]: task for task in plan["manifest"]["tasks"]
    }
    records = []
    for batch in runner.iter_primary_batches(plan):
        for task_id in batch["task_ids"]:
            workflow = batch["workflow"]
            records.append(
                {
                    "protocol_version": "wp5-v5",
                    "task_id": task_id,
                    "workflow": workflow,
                    "seed": batch["seed"],
                    "model": {
                        "name": "gpt-5.4",
                        "reasoning_effort": "medium",
                        "cli_version": None,
                    },
                    "response": {
                        "raw_path": "synthetic",
                        "session_id": None,
                    },
                    "observation": {
                        "turns_before_readiness": 0,
                        "useful_questions": 0,
                        "user_visible_technical_choices": 0,
                        "unsupported_assumptions": 0,
                        "post_start_contract_corrections": None,
                        "out_of_scope_edits": None,
                        "first_pass_done": None,
                        "reopened_or_post_close_defects": None,
                        "promotion_reversals": None,
                        "total_tokens": 110 if workflow == "C5" else 100,
                        "human_interruptions": 0,
                        "quick_path_correct": (
                            tasks[task_id]["oracle"]["expected_route"] != "quick"
                            or True
                        ),
                    },
                }
            )
    return records


class EvaluationV5RunnerResultContractTests(unittest.TestCase):
    def test_subject_prompt_excludes_hidden_oracle(self) -> None:
        runner = load_runner()
        task = runner.load_execution_plan()["manifest"]["tasks"][0]
        prompt = runner.subject_prompt(
            "workflow",
            "A",
            [task],
        )

        self.assertNotIn('"oracle"', prompt)
        self.assertIn('"repository_evidence"', prompt)
        self.assertIn('"scripted_answers"', prompt)

    def test_seed_transition_requires_manifest_order_and_honors_stop(self) -> None:
        runner = load_runner()
        plan = runner.load_execution_plan()
        state = runner.initial_run_state(plan)

        runner.validate_seed_transition(
            state,
            plan,
            "coderail-wp5-v5-s1",
            resume=False,
        )
        with self.assertRaisesRegex(RuntimeError, "Expected next seed"):
            runner.validate_seed_transition(
                state,
                plan,
                "coderail-wp5-v5-s2",
                resume=False,
            )

        state["early_stop"] = {"gate": "provider-question-elimination"}
        with self.assertRaisesRegex(RuntimeError, "provider gate"):
            runner.validate_seed_transition(
                state,
                plan,
                "coderail-wp5-v5-s1",
                resume=False,
            )

    def test_synthetic_complete_run_evaluates_all_five_gates(self) -> None:
        runner = load_runner()
        plan = runner.load_execution_plan()
        state = runner.initial_run_state(plan)
        state["completed_seeds"] = list(plan["seeds"])
        aggregate = runner.aggregate_results(synthetic_records(), state)

        self.assertEqual(aggregate["completed_primary_trials"], 180)
        self.assertEqual(len(aggregate["gates"]), 5)
        self.assertEqual(
            aggregate["gates"]["threshold-assumptions"][
                "relative_reduction"
            ]["status"],
            "untestable-baseline-floor",
        )
        self.assertEqual(
            aggregate["gates"]["category-pooled-token-economy"]["status"],
            "passed",
        )
        self.assertEqual(
            aggregate["treatment_disposition"],
            "EARN_IMPLEMENTATION_FOLLOW_THROUGH",
        )
        self.assertFalse(aggregate["implementation_evidence_complete"])
        self.assertEqual(
            aggregate["decision"],
            "INSUFFICIENT_IMPLEMENTATION_EVIDENCE",
        )

    def test_provider_failure_forces_revise_disposition(self) -> None:
        runner = load_runner()
        plan = runner.load_execution_plan()
        records = synthetic_records()
        c5 = next(record for record in records if record["workflow"] == "C5")
        c5["observation"]["user_visible_technical_choices"] = 1
        state = runner.initial_run_state(plan)
        state["completed_seeds"] = ["coderail-wp5-v5-s1"]
        state["early_stop"] = {
            "gate": "provider-question-elimination",
            "seed": "coderail-wp5-v5-s1",
        }

        aggregate = runner.aggregate_results(records, state)
        self.assertEqual(
            aggregate["gates"]["provider-question-elimination"]["status"],
            "failed",
        )
        self.assertEqual(
            aggregate["treatment_disposition"],
            "REVISE_PROVIDER_GATE",
        )


@unittest.skipUnless(
    (RESULTS / "run-state.json").exists(),
    "v5 primary execution has not started",
)
class EvaluationV5ResultArtifactTests(unittest.TestCase):
    def test_completed_seeds_are_a_prefix_and_batches_are_exact(self) -> None:
        runner = load_runner()
        plan = runner.load_execution_plan()
        state = load_json(RESULTS / "run-state.json")
        completed = state["completed_seeds"]

        self.assertEqual(completed, list(plan["seeds"][:len(completed)]))
        for seed in completed:
            categories = runner.expected_seed_categories(plan, seed)
            subjects = [
                batch
                for batch in state["subject_batches"]
                if batch["seed"] == seed
            ]
            judges = [
                batch
                for batch in state["judge_batches"]
                if batch["seed"] == seed
            ]
            self.assertEqual(
                len(subjects),
                len(categories) * len(plan["primary_workflows"]),
            )
            self.assertEqual(len(judges), len(categories))

    def test_judge_inputs_mask_seed_and_workflow(self) -> None:
        for path in (RESULTS / "judge-inputs").glob("*.json"):
            payload = load_json(path)
            for item in payload["items"]:
                self.assertNotIn("workflow", item)
                self.assertNotIn("seed", item)
                self.assertEqual(
                    set(item),
                    {
                        "opaque_id",
                        "user_profile",
                        "request",
                        "repository_evidence",
                        "scripted_answers",
                        "oracle",
                        "subject_response",
                    },
                )

    def test_trial_records_are_seeded_and_follow_through_is_null(self) -> None:
        runner = load_runner()
        plan = runner.load_execution_plan()
        state = load_json(RESULTS / "run-state.json")
        trials = [
            load_json(path)
            for path in (RESULTS / "trials").glob("*.json")
        ]
        self.assertTrue(trials)
        self.assertEqual(
            {record["seed"] for record in trials},
            set(state["completed_seeds"]),
        )
        expected_cells = {
            (batch["seed"], batch["workflow"], task_id)
            for batch in runner.iter_primary_batches(plan)
            if batch["seed"] in state["completed_seeds"]
            for task_id in batch["task_ids"]
        }
        actual_cells = {
            (record["seed"], record["workflow"], record["task_id"])
            for record in trials
        }
        self.assertEqual(actual_cells, expected_cells)
        self.assertEqual(len(trials), len(expected_cells))
        for record in trials:
            self.assertEqual(record["protocol_version"], "wp5-v5")
            self.assertIn(record["workflow"], ("A", "B", "C5"))
            for metric in NULL_METRICS:
                self.assertIsNone(record["observation"][metric])

    def test_aggregate_withholds_adoption_and_covers_five_gates(self) -> None:
        aggregate = load_json(RESULTS / "aggregate.json")
        self.assertEqual(len(aggregate["gates"]), 5)
        self.assertFalse(aggregate["implementation_evidence_complete"])
        self.assertEqual(
            aggregate["decision"],
            "INSUFFICIENT_IMPLEMENTATION_EVIDENCE",
        )
        self.assertNotEqual(aggregate["treatment_disposition"], "ADOPT")

    def test_provider_failure_stops_later_seeds_and_c5p(self) -> None:
        state = load_json(RESULTS / "run-state.json")
        aggregate = load_json(RESULTS / "aggregate.json")
        if state["early_stop"] is None:
            self.skipTest("provider gate has not failed")

        stop = state["early_stop"]
        self.assertEqual(stop["gate"], "provider-question-elimination")
        self.assertEqual(stop["seed"], state["completed_seeds"][-1])
        self.assertGreater(
            stop["observed_user_visible_technical_choices"],
            0,
        )
        self.assertEqual(stop["rule"], "do not run further seeds or C5p")
        self.assertEqual(
            aggregate["treatment_disposition"],
            "REVISE_PROVIDER_GATE",
        )
        self.assertEqual(
            aggregate["gates"]["provider-question-elimination"]["status"],
            "failed",
        )

        later_seeds = set(state["planned_seeds"]) - set(
            state["completed_seeds"]
        )
        trials = [
            load_json(path)
            for path in (RESULTS / "trials").glob("*.json")
        ]
        self.assertFalse(
            any(record["seed"] in later_seeds for record in trials)
        )
        self.assertFalse(
            any(record["workflow"] == "C5p" for record in trials)
        )

    def test_frozen_hashes_remain_unchanged(self) -> None:
        freeze = load_json(V5 / "freeze.json")
        for relative, expected in freeze["sha256"].items():
            actual = hashlib.sha256((V5 / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, relative)


if __name__ == "__main__":
    unittest.main()
