from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "WP6_ADOPTION_REVIEW.md"
PLAN = ROOT / "docs" / "GUIDED_CONVERGENCE_PLAN.md"
REPORT = ROOT / "docs" / "WP5_EVALUATION_REPORT.md"
README = ROOT / "README.md"
AGGREGATE = ROOT / "evaluation-v5" / "results" / "aggregate.json"
RUN_STATE = ROOT / "evaluation-v5" / "results" / "run-state.json"


class WP6AdoptionReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.review = REVIEW.read_text(encoding="utf-8")

    def test_review_makes_one_scoped_decision(self) -> None:
        decisions = re.findall(
            r"^Decision: (ADOPT|REVISE|REJECT)$",
            self.review,
            flags=re.MULTILINE,
        )
        self.assertEqual(decisions, ["REVISE"])
        self.assertIn("C5 treatment | Revise under a new protocol", self.review)
        self.assertIn("Native CodeRail skill pack | Withhold", self.review)
        self.assertIn("Smart or automatic invocation hook | Do not build", self.review)
        self.assertIn("`REVISE` is not a partial adoption", self.review)

    def test_review_matches_registered_v5_stop(self) -> None:
        aggregate = json.loads(AGGREGATE.read_text(encoding="utf-8"))
        run_state = json.loads(RUN_STATE.read_text(encoding="utf-8"))

        self.assertEqual(aggregate["completed_primary_trials"], 90)
        self.assertEqual(len(run_state["subject_batches"]), 21)
        self.assertEqual(len(run_state["judge_batches"]), 7)
        self.assertEqual(
            aggregate["treatment_disposition"],
            "REVISE_PROVIDER_GATE",
        )
        self.assertEqual(
            run_state["early_stop"]["observed_user_visible_technical_choices"],
            2,
        )
        for evidence in (
            "90 trials",
            "21\n  subject batches",
            "seven judge batches",
            "0.5 versus 0.1667",
            "1.0756",
            "1.2667 turns per trial",
            "Implementation and follow-through observations remain null",
        ):
            self.assertIn(evidence, self.review)

    def test_revision_requires_outcomes_and_a_new_protocol(self) -> None:
        self.assertIn(
            "authorize observable outcomes",
            self.review,
        )
        self.assertRegex(
            self.review,
            r"new frozen protocol,\s+not a mutation or continuation\s+of `wp5-v5`",
        )
        self.assertIn("No smart hook or automatic intent classifier", self.review)
        self.assertIn("No execution of v5 s3-s5 or C5p", self.review)
        self.assertIn("CodeRail as the only task and lifecycle authority", self.review)

    def test_public_documents_agree_on_wp6_closeout(self) -> None:
        for path in (PLAN, REPORT, README):
            text = path.read_text(encoding="utf-8")
            self.assertIn("WP6", text, path.name)
            self.assertIn("REVISE", text, path.name)
            self.assertIn("WP6_ADOPTION_REVIEW.md", text, path.name)
            self.assertNotIn("WP6 decision pending", text, path.name)


if __name__ == "__main__":
    unittest.main()
