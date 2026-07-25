from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V2 = ROOT / "evaluation-v2"
RESULTS = V2 / "results"


class EvaluationV2ResultTests(unittest.TestCase):
    def test_v2_aborted_before_subject_output(self) -> None:
        metadata = json.loads(
            (RESULTS / "run-metadata.json").read_text(encoding="utf-8")
        )
        self.assertEqual(metadata["protocol_version"], "wp5-v2")
        self.assertEqual(metadata["subject_batches"], [])
        self.assertEqual(metadata["judge_batches"], [])
        self.assertIn("subject-A-ambiguous-cross-module", metadata["failure"])
        self.assertEqual(list((RESULTS / "raw").glob("*.json")), [])

        events = (
            RESULTS
            / "events"
            / "subject-A-ambiguous-cross-module.jsonl"
        ).read_text(encoding="utf-8")
        self.assertIn("invalid_json_schema", events)
        self.assertIn("schema must have a 'type' key", events)

    def test_v2_pretrial_hashes_remain_unchanged(self) -> None:
        freeze = json.loads((V2 / "freeze.json").read_text(encoding="utf-8"))
        for relative, expected in freeze["sha256"].items():
            actual = hashlib.sha256((V2 / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, relative)


if __name__ == "__main__":
    unittest.main()
