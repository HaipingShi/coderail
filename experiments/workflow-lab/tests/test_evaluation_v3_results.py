from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V3 = ROOT / "evaluation-v3"
RESULTS = V3 / "results"


class EvaluationV3ResultTests(unittest.TestCase):
    def test_all_subject_and_judge_batches_completed(self) -> None:
        metadata = json.loads(
            (RESULTS / "run-metadata.json").read_text(encoding="utf-8")
        )
        self.assertEqual(metadata["protocol_version"], "wp5-v3")
        self.assertEqual(metadata["model"], "gpt-5.4")
        self.assertEqual(metadata["reasoning_effort"], "medium")
        self.assertEqual(len(metadata["subject_batches"]), 12)
        self.assertEqual(len(metadata["judge_batches"]), 4)
        self.assertTrue(
            all(batch["status"] == "completed" for batch in metadata["subject_batches"])
        )
        self.assertTrue(
            all(batch["status"] == "completed" for batch in metadata["judge_batches"])
        )

    def test_all_54_cells_have_trial_records(self) -> None:
        manifest = json.loads((V3 / "manifest.json").read_text(encoding="utf-8"))
        expected = {
            (workflow, task["id"])
            for workflow in ("A", "B", "C")
            for task in manifest["tasks"]
        }
        records = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted((RESULTS / "trials").glob("*.json"))
        ]
        self.assertEqual(
            {(record["workflow"], record["task_id"]) for record in records},
            expected,
        )
        self.assertEqual(len(records), 54)
        nullable = {
            "post_start_contract_corrections",
            "out_of_scope_edits",
            "first_pass_done",
            "reopened_or_post_close_defects",
            "promotion_reversals",
        }
        for record in records:
            self.assertEqual(record["protocol_version"], "wp5-v3")
            self.assertEqual(
                set(record),
                {
                    "protocol_version",
                    "task_id",
                    "workflow",
                    "model",
                    "response",
                    "observation",
                },
            )
            for metric in nullable:
                self.assertIsNone(record["observation"][metric])

    def test_judge_inputs_mask_workflow_labels(self) -> None:
        judge_inputs = sorted((RESULTS / "judge-inputs").glob("*.json"))
        self.assertEqual(len(judge_inputs), 4)
        for path in judge_inputs:
            payload = path.read_text(encoding="utf-8")
            self.assertNotIn('"workflow"', payload)
            parsed = json.loads(payload)
            self.assertTrue(all(item["opaque_id"] for item in parsed["items"]))

    def test_aggregate_withholds_adoption(self) -> None:
        aggregate = json.loads(
            (RESULTS / "aggregate.json").read_text(encoding="utf-8")
        )
        self.assertEqual(set(aggregate["workflows"]), {"A", "B", "C"})
        for workflow in aggregate["workflows"].values():
            self.assertEqual(workflow["trials"], 18)
            self.assertIsNone(workflow["first_pass_done_pct"])
        self.assertEqual(
            {
                name: values["unsupported_assumptions"]
                for name, values in aggregate["workflows"].items()
            },
            {"A": 1, "B": 1, "C": 2},
        )
        self.assertEqual(
            {
                name: values["quick_path_correct_pct"]
                for name, values in aggregate["workflows"].items()
            },
            {"A": 100.0, "B": 100.0, "C": 100.0},
        )
        self.assertFalse(aggregate["implementation_evidence_complete"])
        self.assertEqual(
            aggregate["decision"],
            "INSUFFICIENT_IMPLEMENTATION_EVIDENCE",
        )

    def test_v3_pretrial_hashes_remain_unchanged(self) -> None:
        freeze = json.loads((V3 / "freeze.json").read_text(encoding="utf-8"))
        for relative, expected in freeze["sha256"].items():
            actual = hashlib.sha256((V3 / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, relative)


if __name__ == "__main__":
    unittest.main()
