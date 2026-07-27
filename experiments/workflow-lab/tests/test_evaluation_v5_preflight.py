from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
V5 = ROOT / "evaluation-v5"
RUNNER_PATH = ROOT / "scripts" / "run_evaluation_v5.py"
PREFLIGHT = V5 / "preflight"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_runner() -> Any:
    spec = importlib.util.spec_from_file_location(
        "run_evaluation_v5",
        RUNNER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load the v5 runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EvaluationV5RunnerTests(unittest.TestCase):
    def test_plan_is_manifest_derived_and_seed_aware(self) -> None:
        runner = load_runner()
        plan = runner.load_execution_plan()
        manifest = load_json(V5 / "manifest.json")
        design = manifest["trial_design"]

        self.assertEqual(
            plan["primary_workflows"],
            tuple(design["workflows"]),
        )
        self.assertEqual(
            plan["contingency_workflows"],
            tuple(design["contingency_workflows"]),
        )
        self.assertEqual(plan["seeds"], tuple(design["task_order_seeds"]))
        self.assertEqual(
            plan["sampling_plan"],
            {
                category: tuple(seeds)
                for category, seeds in design["sampling_plan"].items()
            },
        )
        self.assertEqual(
            plan["expected_primary_trials"],
            design["expected_primary_trials"],
        )
        self.assertEqual(plan["workflow_files"]["C5"].name, "C.md")
        self.assertEqual(plan["workflow_files"]["C5p"].name, "C5p.md")

    def test_primary_batch_plan_covers_180_cells_in_42_batches(self) -> None:
        runner = load_runner()
        batches = list(runner.iter_primary_batches(
            runner.load_execution_plan()
        ))

        self.assertEqual(len(batches), 42)
        self.assertEqual(
            sum(len(batch["task_ids"]) for batch in batches),
            180,
        )
        self.assertEqual(
            {batch["workflow"] for batch in batches},
            {"A", "B", "C5"},
        )
        self.assertNotIn(
            "C5p",
            {batch["workflow"] for batch in batches},
        )
        self.assertTrue(
            all(batch["seed"].startswith("coderail-wp5-v5-s")
                for batch in batches)
        )

    def test_frozen_hashes_still_match(self) -> None:
        freeze = load_json(V5 / "freeze.json")
        for relative, expected in freeze["sha256"].items():
            actual = hashlib.sha256((V5 / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, relative)


@unittest.skipUnless(PREFLIGHT.exists(), "v5 preflight has not run yet")
class EvaluationV5PreflightArtifactTests(unittest.TestCase):
    def test_service_accepted_schema_without_evaluation_payloads(self) -> None:
        record = load_json(PREFLIGHT / "schema-compatibility.json")
        output = load_json(PREFLIGHT / "schema-output.json")

        self.assertEqual(record["protocol_version"], "wp5-v5")
        self.assertEqual(record["status"], "passed")
        self.assertEqual(record["request_kind"], "schema-compatibility-only")
        self.assertEqual(record["subject_batches_started"], 0)
        self.assertEqual(record["judge_batches_started"], 0)
        self.assertEqual(record["task_payloads_sent"], 0)
        self.assertEqual(record["oracle_payloads_sent"], 0)
        self.assertEqual(record["task_or_oracle_payloads_sent"], 0)
        self.assertTrue(record["frozen_hashes_unchanged"])
        self.assertEqual(record["planned_primary_trials"], 180)
        self.assertTrue(record["thread_id"])
        self.assertIn(record["transport_attempts"], (1, 2))

        self.assertEqual(output["protocol_version"], "wp5-v5")
        self.assertEqual(len(output["responses"]), 1)
        self.assertEqual(
            output["responses"][0]["task_id"],
            "__schema_preflight__",
        )

    def test_preflight_created_no_results_or_trials(self) -> None:
        self.assertFalse((V5 / "results").exists())
        self.assertFalse((V5 / "results" / "trials").exists())

    def test_transport_retry_is_identical_and_precedes_output(self) -> None:
        record = load_json(PREFLIGHT / "schema-compatibility.json")
        failure_path = PREFLIGHT / "schema-transport-failure.json"
        if record["transport_attempts"] == 1:
            self.assertFalse(failure_path.exists())
            return

        failure = load_json(failure_path)
        self.assertEqual(failure["attempt"], 1)
        self.assertEqual(
            failure["status"],
            "transport-failed-before-output",
        )
        self.assertEqual(
            failure["retry_policy"],
            "one identical-input transport retry",
        )
        self.assertEqual(failure["subject_batches_started"], 0)
        self.assertEqual(failure["judge_batches_started"], 0)
        self.assertEqual(failure["task_or_oracle_payloads_sent"], 0)
        self.assertTrue((PREFLIGHT / failure["events"]).is_file())
        self.assertTrue((PREFLIGHT / failure["stderr"]).is_file())


if __name__ == "__main__":
    unittest.main()
