from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "evaluation"
V2 = ROOT / "evaluation-v2"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


class EvaluationV2ProtocolTests(unittest.TestCase):
    def test_v2_preserves_tasks_and_workflow_treatments(self) -> None:
        v1_manifest = load_json(V1 / "manifest.json")
        v2_manifest = load_json(V2 / "manifest.json")
        self.assertEqual(v2_manifest["protocol_version"], "wp5-v2")
        self.assertEqual(v2_manifest["tasks"], v1_manifest["tasks"])
        self.assertEqual(v2_manifest["trial_design"], v1_manifest["trial_design"])
        for workflow in ("A.md", "B.md", "C.md"):
            self.assertEqual(
                (V2 / "workflows" / workflow).read_bytes(),
                (V1 / "workflows" / workflow).read_bytes(),
            )

    def test_v2_pins_available_model_and_offline_execution_limits(self) -> None:
        freeze = load_json(V2 / "freeze.json")
        policy = freeze["execution_policy"]
        self.assertEqual(policy["model"], "gpt-5.4")
        self.assertEqual(policy["reasoning_effort"], "medium")
        self.assertTrue(policy["availability_preflight_passed"])
        run_spec = (V2 / "run-spec.md").read_text(encoding="utf-8")
        self.assertIn("12 subject batches", run_spec)
        self.assertIn("contract-phase simulation", run_spec)
        self.assertIn("not a live-human or implementation trial", run_spec)

    def test_v2_nullable_follow_through_metrics_cannot_imply_zero(self) -> None:
        rubric = load_json(V2 / "rubric.json")
        schema = load_json(V2 / "trial-result.schema.json")
        nullable = {
            "post_start_contract_corrections",
            "out_of_scope_edits",
            "first_pass_done",
            "reopened_or_post_close_defects",
            "promotion_reversals",
        }
        for metric in nullable:
            metric_type = rubric["metrics"][metric]["type"]
            self.assertIn("null", metric_type)
            schema_type = schema["properties"]["observation"]["properties"][metric][
                "type"
            ]
            self.assertIn("null", schema_type)
        self.assertIn(
            "Null implementation fields cannot authorize ADOPT",
            rubric["decision_rule"],
        )

    def test_v2_separates_subject_and_blind_judge_outputs(self) -> None:
        subject = load_json(V2 / "model-output.schema.json")
        judge = load_json(V2 / "judge-output.schema.json")
        self.assertIn("responses", subject["required"])
        self.assertNotIn("observation", subject["properties"])
        self.assertIn("observations", judge["required"])
        judge_item = judge["properties"]["observations"]["items"]
        self.assertIn("opaque_id", judge_item["required"])
        self.assertNotIn("workflow", judge_item["properties"])
        judge_prompt = (V2 / "judge.md").read_text(encoding="utf-8")
        self.assertIn("do not receive the workflow label", judge_prompt)

    def test_v2_freeze_hashes_cover_all_pretrial_inputs(self) -> None:
        freeze = load_json(V2 / "freeze.json")
        expected = {
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
        }
        self.assertEqual(set(freeze["sha256"]), expected)
        for relative, digest in freeze["sha256"].items():
            actual = hashlib.sha256((V2 / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, digest, relative)
        self.assertNotIn("results", freeze["sha256"])


if __name__ == "__main__":
    unittest.main()
