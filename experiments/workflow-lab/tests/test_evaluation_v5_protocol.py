from __future__ import annotations

import hashlib
import json
import unittest
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
V4 = ROOT / "evaluation-v4"
V5 = ROOT / "evaluation-v5"
DESIGN = ROOT / "docs" / "WP5_V5_DESIGN.md"
PRIMARY_WORKFLOWS = ("A", "B", "C5")
CONTINGENCY_WORKFLOWS = ("C5p",)
SEEDS = tuple(f"coderail-wp5-v5-s{index}" for index in range(1, 6))


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


class EvaluationV5ProtocolTests(unittest.TestCase):
    def test_v5_manifest_names_primary_and_contingency_workflows(self) -> None:
        manifest = load_json(V5 / "manifest.json")
        trial_design = manifest["trial_design"]

        self.assertEqual(manifest["protocol_version"], "wp5-v5")
        self.assertEqual(trial_design["workflows"], list(PRIMARY_WORKFLOWS))
        self.assertEqual(
            trial_design["contingency_workflows"],
            list(CONTINGENCY_WORKFLOWS),
        )
        self.assertEqual(trial_design["task_order_seeds"], list(SEEDS))
        self.assertEqual(
            manifest["tasks"],
            load_json(V4 / "manifest.json")["tasks"],
        )

    def test_v5_trial_records_require_a_frozen_seed(self) -> None:
        manifest = load_json(V5 / "manifest.json")
        schema = load_json(V5 / "trial-result.schema.json")

        self.assertFalse(schema["additionalProperties"])
        self.assertIn("seed", schema["required"])
        self.assertEqual(schema["properties"]["seed"], {"enum": list(SEEDS)})
        self.assertEqual(
            schema["properties"]["seed"]["enum"],
            manifest["trial_design"]["task_order_seeds"],
        )
        self.assertEqual(
            schema["properties"]["workflow"]["enum"],
            [*PRIMARY_WORKFLOWS, *CONTINGENCY_WORKFLOWS],
        )

    def test_v5_sampling_plan_covers_180_primary_trials(self) -> None:
        manifest = load_json(V5 / "manifest.json")
        trial_design = manifest["trial_design"]
        sampling_plan = trial_design["sampling_plan"]
        freeze_policy = load_json(V5 / "freeze.json")["execution_policy"]
        task_counts = Counter(task["category"] for task in manifest["tasks"])

        self.assertEqual(set(sampling_plan), set(task_counts))
        self.assertEqual(
            sampling_plan,
            {
                "ambiguous-cross-module": list(SEEDS),
                "high-risk-persistent": list(SEEDS),
                "domain-language-conflict": list(SEEDS[:3]),
                "clear-local-reversible": list(SEEDS[:1]),
            },
        )
        primary_trials = len(PRIMARY_WORKFLOWS) * sum(
            task_counts[category] * len(seeds)
            for category, seeds in sampling_plan.items()
        )
        self.assertEqual(primary_trials, 180)
        self.assertEqual(trial_design["expected_primary_trials"], primary_trials)
        self.assertEqual(
            freeze_policy["task_order_seeds"],
            trial_design["task_order_seeds"],
        )
        self.assertEqual(freeze_policy["estimated_trials"], primary_trials)
        for subset in freeze_policy["sampling_plan"].values():
            self.assertEqual(
                subset["task_count"],
                sum(task_counts[category] for category in subset["categories"]),
            )
            for category in subset["categories"]:
                self.assertEqual(sampling_plan[category], subset["seeds"])

    def test_v5_changes_only_registered_protocol_contracts(self) -> None:
        for relative in ("workflows/A.md", "workflows/B.md", "judge.md"):
            self.assertEqual(
                (V5 / relative).read_bytes(),
                (V4 / relative).read_bytes(),
                relative,
            )

        v4_rubric = load_json(V4 / "rubric.json")
        v5_rubric = load_json(V5 / "rubric.json")
        v5_rubric["protocol_version"] = "wp5-v4"
        self.assertEqual(v5_rubric, v4_rubric)

        for filename in ("model-output.schema.json", "judge-output.schema.json"):
            v4_schema = load_json(V4 / filename)
            v5_schema = load_json(V5 / filename)
            v5_schema["properties"]["protocol_version"]["const"] = "wp5-v4"
            self.assertEqual(v5_schema, v4_schema, filename)

        v4_trial = load_json(V4 / "trial-result.schema.json")
        v5_trial = deepcopy(load_json(V5 / "trial-result.schema.json"))
        v5_trial["properties"]["protocol_version"]["const"] = "wp5-v4"
        v5_trial["properties"]["workflow"]["enum"] = ["A", "B", "C"]
        v5_trial["required"].remove("seed")
        del v5_trial["properties"]["seed"]
        self.assertEqual(v5_trial, v4_trial)

    def test_v5_freeze_covers_inputs_and_registered_execution_prefix(self) -> None:
        freeze = load_json(V5 / "freeze.json")
        expected_paths = {
            "manifest.json",
            "rubric.json",
            "trial-result.schema.json",
            "model-output.schema.json",
            "judge-output.schema.json",
            "judge.md",
            "run-spec.md",
            "workflows/A.md",
            "workflows/B.md",
            "workflows/C.md",
            "workflows/C5p.md",
        }

        self.assertEqual(set(freeze["sha256"]), expected_paths)
        for relative, expected in freeze["sha256"].items():
            actual = hashlib.sha256((V5 / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, relative)

        policy = freeze["execution_policy"]
        self.assertFalse(policy["schema_preflight_run_at_this_checkpoint"])
        self.assertEqual(policy["subject_batches_started"], 0)

        preflight = load_json(V5 / "preflight" / "schema-compatibility.json")
        self.assertEqual(preflight["status"], "passed")
        self.assertEqual(preflight["subject_batches_started"], 0)
        self.assertEqual(preflight["judge_batches_started"], 0)
        self.assertEqual(preflight["task_or_oracle_payloads_sent"], 0)

        run_state = load_json(V5 / "results" / "run-state.json")
        aggregate = load_json(V5 / "results" / "aggregate.json")
        completed_seeds = list(SEEDS[:2])

        self.assertEqual(run_state["completed_seeds"], completed_seeds)
        self.assertEqual(
            run_state["seed_status"],
            {
                SEEDS[0]: "completed",
                SEEDS[1]: "provider-gate-failed",
            },
        )
        self.assertEqual(len(run_state["subject_batches"]), 21)
        self.assertEqual(len(run_state["judge_batches"]), 7)
        self.assertTrue(
            all(
                batch["seed"] in completed_seeds
                for batch in (
                    run_state["subject_batches"] + run_state["judge_batches"]
                )
            ),
        )
        self.assertNotIn(
            CONTINGENCY_WORKFLOWS[0],
            {batch["workflow"] for batch in run_state["subject_batches"]},
        )

        early_stop = run_state["early_stop"]
        self.assertEqual(early_stop["gate"], "provider-question-elimination")
        self.assertEqual(early_stop["seed"], SEEDS[1])
        self.assertEqual(early_stop["observed_user_visible_technical_choices"], 2)
        self.assertEqual(aggregate["completed_primary_trials"], 90)
        self.assertEqual(aggregate["completed_seeds"], completed_seeds)
        self.assertEqual(
            aggregate["treatment_disposition"],
            "REVISE_PROVIDER_GATE",
        )
        self.assertFalse(aggregate["implementation_evidence_complete"])
        self.assertEqual(
            aggregate["decision"],
            "INSUFFICIENT_IMPLEMENTATION_EVIDENCE",
        )

    def test_v5_frozen_documents_match_the_machine_contract(self) -> None:
        design = DESIGN.read_text(encoding="utf-8")
        run_spec = (V5 / "run-spec.md").read_text(encoding="utf-8")

        self.assertIn(
            "Status: stopped after s2 by the pre-registered provider gate",
            design,
        )
        self.assertIn("Protocol: `wp5-v5`", design)
        self.assertIn("A, B, and C5", run_spec)
        self.assertIn("required in every trial record", run_spec)


if __name__ == "__main__":
    unittest.main()
