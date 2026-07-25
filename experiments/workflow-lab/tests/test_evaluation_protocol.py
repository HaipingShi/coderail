from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVALUATION = ROOT / "evaluation"
SCORER = ROOT / "scripts" / "score_evaluation.py"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_scorer() -> Any:
    spec = importlib.util.spec_from_file_location("score_evaluation", SCORER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load scorer: {SCORER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EvaluationProtocolTests(unittest.TestCase):
    def test_manifest_has_frozen_balanced_task_matrix(self) -> None:
        manifest = load_json(EVALUATION / "manifest.json")
        self.assertEqual(manifest["protocol_version"], "wp5-v1")
        self.assertEqual(len(manifest["tasks"]), 18)
        self.assertEqual(
            Counter(task["category"] for task in manifest["tasks"]),
            {
                "clear-local-reversible": 6,
                "ambiguous-cross-module": 6,
                "high-risk-persistent": 3,
                "domain-language-conflict": 3,
            },
        )
        self.assertTrue(
            {"novice", "expert"}.issubset(
                {task["user_profile"] for task in manifest["tasks"]}
            )
        )
        ids = [task["id"] for task in manifest["tasks"]]
        self.assertEqual(len(ids), len(set(ids)))
        for task in manifest["tasks"]:
            self.assertTrue(task["request"])
            self.assertTrue(task["repository_evidence"])
            self.assertTrue(task["scripted_answers"])
            self.assertIn(task["oracle"]["expected_route"], {"quick", "guided"})
            self.assertTrue(task["oracle"]["decisive_coordinates"])
            self.assertIn(
                task["oracle"]["ready_after_answers"],
                range(len(task["scripted_answers"]) + 1),
            )

    def test_workflows_share_output_contract_but_preserve_treatments(self) -> None:
        texts = {
            name: (EVALUATION / "workflows" / f"{name}.md").read_text(
                encoding="utf-8"
            )
            for name in ("A", "B", "C")
        }
        common = [
            "EVALUATION RESPONSE",
            "route:",
            "questions:",
            "contract:",
            "promotions:",
            "stop_after_contract",
        ]
        for name, text in texts.items():
            for marker in common:
                self.assertIn(marker, text, f"{name}: {marker}")
        self.assertIn("baseline CodeRail", texts["A"])
        self.assertIn("expert-oriented grilling", texts["B"])
        self.assertIn("immediate documentation", texts["B"])
        self.assertIn("Guided Convergence", texts["C"])
        self.assertIn("exactly one", texts["C"])
        self.assertNotEqual(texts["A"], texts["B"])
        self.assertNotEqual(texts["B"], texts["C"])

    def test_rubric_covers_planned_metrics_and_adoption_thresholds(self) -> None:
        rubric = load_json(EVALUATION / "rubric.json")
        expected_metrics = {
            "turns_before_readiness",
            "useful_questions",
            "user_visible_technical_choices",
            "unsupported_assumptions",
            "post_start_contract_corrections",
            "out_of_scope_edits",
            "first_pass_done",
            "reopened_or_post_close_defects",
            "promotion_reversals",
            "total_tokens",
            "human_interruptions",
            "quick_path_correct",
        }
        self.assertEqual(set(rubric["metrics"]), expected_metrics)
        thresholds = rubric["adoption_thresholds"]
        self.assertEqual(
            thresholds["unsupported_assumptions_or_corrections_reduction_pct"],
            25,
        )
        self.assertEqual(thresholds["clear_task_quick_path_accuracy_pct"], 90)
        self.assertEqual(thresholds["out_of_scope_or_closeout_regression"], 0)
        self.assertEqual(thresholds["clear_task_interruption_increase"], 0)
        self.assertTrue(thresholds["promotion_reversals_less_than_workflow_b"])

    def test_trial_schema_separates_model_output_from_observation(self) -> None:
        schema = load_json(EVALUATION / "trial-result.schema.json")
        required = set(schema["required"])
        self.assertTrue(
            {
                "protocol_version",
                "task_id",
                "workflow",
                "model",
                "response",
                "observation",
            }.issubset(required)
        )
        observation_required = set(
            schema["properties"]["observation"]["required"]
        )
        rubric = load_json(EVALUATION / "rubric.json")
        self.assertEqual(observation_required, set(rubric["metrics"]))

    def test_freeze_hashes_cover_every_pretrial_input(self) -> None:
        freeze = load_json(EVALUATION / "freeze.json")
        expected_paths = {
            "manifest.json",
            "rubric.json",
            "trial-result.schema.json",
            "workflows/A.md",
            "workflows/B.md",
            "workflows/C.md",
        }
        self.assertEqual(set(freeze["sha256"]), expected_paths)
        for relative, expected in freeze["sha256"].items():
            payload = (EVALUATION / relative).read_bytes()
            self.assertEqual(hashlib.sha256(payload).hexdigest(), expected, relative)
        results = EVALUATION / "results"
        self.assertFalse(results.exists() and any(results.rglob("*.json")))

    def test_scorer_aggregates_observations_without_model_self_scoring(self) -> None:
        scorer = load_scorer()
        records = []
        for workflow, unsupported, quick in [
            ("A", 4, False),
            ("B", 2, False),
            ("C", 1, True),
        ]:
            records.append(
                {
                    "protocol_version": "wp5-v1",
                    "task_id": "clear-01",
                    "workflow": workflow,
                    "model": {"name": "fixed-model", "reasoning_effort": "fixed"},
                    "response": {"raw_path": f"{workflow}/clear-01.md"},
                    "observation": {
                        "turns_before_readiness": 1,
                        "useful_questions": 0,
                        "user_visible_technical_choices": 0,
                        "unsupported_assumptions": unsupported,
                        "post_start_contract_corrections": 0,
                        "out_of_scope_edits": 0,
                        "first_pass_done": None,
                        "reopened_or_post_close_defects": None,
                        "promotion_reversals": 0,
                        "total_tokens": 100,
                        "human_interruptions": 0,
                        "quick_path_correct": quick,
                    },
                }
            )
        report = scorer.aggregate(records)
        self.assertEqual(report["workflows"]["C"]["unsupported_assumptions"], 1)
        self.assertEqual(report["workflows"]["A"]["unsupported_assumptions"], 4)
        self.assertEqual(report["workflows"]["C"]["quick_path_correct_pct"], 100.0)
        self.assertIsNone(report["workflows"]["C"]["first_pass_done_pct"])


if __name__ == "__main__":
    unittest.main()
