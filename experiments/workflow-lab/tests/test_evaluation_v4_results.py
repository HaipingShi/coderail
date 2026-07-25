from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V4 = ROOT / "evaluation-v4"
RESULTS = V4 / "results"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class EvaluationV4ResultTests(unittest.TestCase):
    def test_all_subject_and_judge_batches_completed(self) -> None:
        metadata = load_json(RESULTS / "run-metadata.json")
        self.assertEqual(metadata["protocol_version"], "wp5-v4")
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
        self.assertEqual(
            [batch["source"] for batch in metadata["subject_batches"]].count("resumed"),
            8,
        )

    def test_local_encoding_failure_is_preserved_without_losing_cells(self) -> None:
        failed = load_json(
            RESULTS / "attempts" / "run-metadata-encoding-failure.json"
        )
        self.assertIn("data must be str", failed["failure"])
        self.assertEqual(len(failed["subject_batches"]), 8)
        self.assertTrue(
            (
                RESULTS
                / "attempts"
                / "subject-C-ambiguous-cross-module-before-utf8-retry.json"
            ).is_file()
        )
        final = load_json(RESULTS / "run-metadata.json")
        self.assertNotIn("failure", final)

    def test_all_54_cells_are_exact_and_follow_through_stays_null(self) -> None:
        manifest = load_json(V4 / "manifest.json")
        expected = {
            (workflow, task["id"])
            for workflow in ("A", "B", "C")
            for task in manifest["tasks"]
        }
        records = [
            load_json(path)
            for path in sorted((RESULTS / "trials").glob("*.json"))
        ]
        self.assertEqual(len(records), 54)
        self.assertEqual(
            {(record["workflow"], record["task_id"]) for record in records},
            expected,
        )
        nullable = {
            "post_start_contract_corrections",
            "out_of_scope_edits",
            "first_pass_done",
            "reopened_or_post_close_defects",
            "promotion_reversals",
        }
        for record in records:
            self.assertEqual(record["protocol_version"], "wp5-v4")
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
        paths = sorted((RESULTS / "judge-inputs").glob("*.json"))
        self.assertEqual(len(paths), 4)
        for path in paths:
            payload = path.read_text(encoding="utf-8")
            self.assertNotIn('"workflow"', payload)
            self.assertTrue(
                all(item["opaque_id"] for item in json.loads(payload)["items"])
            )

    def test_aggregate_records_improvement_and_withholds_adoption(self) -> None:
        aggregate = load_json(RESULTS / "aggregate.json")
        self.assertEqual(
            {
                name: values["unsupported_assumptions"]
                for name, values in aggregate["workflows"].items()
            },
            {"A": 3, "B": 1, "C": 0},
        )
        self.assertEqual(
            {
                name: values["total_tokens"]
                for name, values in aggregate["workflows"].items()
            },
            {"A": 73903, "B": 75968, "C": 97603},
        )
        self.assertEqual(
            {
                name: values["quick_path_correct_pct"]
                for name, values in aggregate["workflows"].items()
            },
            {"A": 100.0, "B": 100.0, "C": 100.0},
        )
        self.assertTrue(
            all(
                values["first_pass_done_pct"] is None
                for values in aggregate["workflows"].values()
            )
        )
        self.assertFalse(aggregate["implementation_evidence_complete"])
        self.assertEqual(
            aggregate["decision"],
            "INSUFFICIENT_IMPLEMENTATION_EVIDENCE",
        )

    def test_revised_c_fixes_two_failures_but_keeps_novice_choice(self) -> None:
        refund = load_json(
            RESULTS / "judge-notes" / "C-risk-02-refund-authority.json"
        )
        workspace = load_json(
            RESULTS / "judge-notes" / "C-domain-02-workspace.json"
        )
        login = load_json(
            RESULTS / "trials" / "C-ambiguous-01-login-audience.json"
        )
        self.assertIn("auditability", " ".join(refund["notes"]))
        self.assertIn("both decisive answers", " ".join(workspace["notes"]))
        self.assertEqual(
            login["observation"]["user_visible_technical_choices"],
            1,
        )
        self.assertEqual(login["observation"]["unsupported_assumptions"], 0)

    def test_v4_pretrial_hashes_remain_unchanged(self) -> None:
        freeze = load_json(V4 / "freeze.json")
        for relative, expected in freeze["sha256"].items():
            actual = hashlib.sha256((V4 / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, relative)


if __name__ == "__main__":
    unittest.main()
