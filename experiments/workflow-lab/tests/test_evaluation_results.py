from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVALUATION = ROOT / "evaluation"


class EvaluationResultTests(unittest.TestCase):
    def test_wp5_v1_aborted_before_any_subject_trial(self) -> None:
        preflight = json.loads(
            (
                EVALUATION / "results" / "wp5-v1" / "preflight.jsonl"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(preflight["status"], "aborted-before-trials")
        self.assertEqual(preflight["subject_trials_started"], 0)
        self.assertEqual(preflight["observed_error"]["http_status"], 400)
        self.assertFalse(preflight["fallback_preflight"]["used_for_subject_trial"])
        trial_files = list(
            (EVALUATION / "results" / "wp5-v1").glob("trial-*.json")
        )
        self.assertEqual(trial_files, [])

    def test_wp5_v1_pretrial_hashes_remain_unchanged(self) -> None:
        freeze = json.loads(
            (EVALUATION / "freeze.json").read_text(encoding="utf-8")
        )
        for relative, expected in freeze["sha256"].items():
            actual = hashlib.sha256((EVALUATION / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, relative)


if __name__ == "__main__":
    unittest.main()
