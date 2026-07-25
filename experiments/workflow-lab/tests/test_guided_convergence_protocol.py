from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"
COORDINATES = ("G", "T", "S", "V", "X", "P")
STATES = {"FACT", "ASSUMPTION", "DECISION", "UNKNOWN"}


def load_json(name: str) -> Any:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def all_items(draft: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for coordinate in COORDINATES for item in draft[coordinate]]


def derive_ready(draft: dict[str, Any]) -> bool:
    if any(not draft.get(coordinate) for coordinate in COORDINATES):
        return False

    items = all_items(draft)
    ids = {item["id"] for item in items}
    for item in items:
        state = item["state"]
        if state == "FACT" and not item.get("evidence"):
            return False
        if state == "ASSUMPTION":
            if not item.get("owner") or not item.get("falsifier"):
                return False
            if item.get("risk") == "high" and item.get("x_trigger") not in ids:
                return False
        if state == "DECISION" and not item.get("owner"):
            return False
        if state == "UNKNOWN":
            if item.get("blocking") == item.get("deferred"):
                return False
            if item.get("blocking"):
                return False

    verification = draft["V"]
    if not any(
        item.get("verification_kind") in {"executable", "manual"}
        for item in verification
    ):
        return False
    return bool(draft["readiness"]["slice_reversible"])


def derive_promotion(case: dict[str, Any], protocol: dict[str, Any]) -> bool:
    required = protocol["promotion"][f"{case['kind']}_required"]
    return all(bool(case.get(field)) for field in required)


class GuidedConvergenceProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.protocol = load_json("protocol.json")
        cls.scenarios = load_json("scenarios.json")
        cls.promotion_cases = load_json("promotion-cases.json")

    def test_protocol_uses_closed_vocabulary(self) -> None:
        self.assertEqual(
            self.protocol["epistemic_states"],
            ["FACT", "ASSUMPTION", "DECISION", "UNKNOWN"],
        )
        self.assertEqual(self.protocol["coordinates"], list(COORDINATES))
        self.assertEqual(self.protocol["routes"], ["quick", "guided"])
        self.assertEqual(
            set(self.protocol["item_requirements"]),
            STATES,
        )

    def test_contract_draft_golden_is_typed_and_ordered(self) -> None:
        text = (FIXTURES / "contract-draft.md").read_text(encoding="utf-8")
        positions = [text.index(f"\n{coordinate} - ") for coordinate in COORDINATES]
        self.assertEqual(positions, sorted(positions))
        for state in STATES:
            self.assertRegex(text, rf"\[[A-Z]\.\d+\]\[{state}\]")
        self.assertIn("\nREADINESS\n", text)
        self.assertNotRegex(text.lower(), r"(confidence|entropy|readiness)[_-]?score")

    def test_draft_delta_contains_only_changed_item_references(self) -> None:
        text = (FIXTURES / "draft-delta.md").read_text(encoding="utf-8")
        changed, readiness = text.split("\nREADINESS CHANGED\n", 1)
        changed_lines = [
            line.strip()
            for line in changed.splitlines()
            if line.strip().startswith("[")
        ]
        references = []
        for line in changed_lines:
            match = re.match(r"\[(add|replace|remove)\]\[([GTSVXP]\.\d+)\]", line)
            self.assertIsNotNone(match, line)
            references.append(match.group(2))
        self.assertEqual(references, ["G.2", "T.1", "X.1", "X.2"])
        self.assertEqual(len(references), len(set(references)))
        for coordinate in COORDINATES:
            self.assertNotIn(f"{coordinate} - ", changed)
        self.assertIn("UNCHANGED\n  omitted by contract", readiness)

    def test_scenarios_cover_minimum_matrix_and_question_shape(self) -> None:
        self.assertEqual(
            [scenario["id"] for scenario in self.scenarios],
            [
                "rename-local-button",
                "login-unclear-audience",
                "local-only-file-processing",
                "database-for-throwaway-prototype",
                "public-api-migration",
                "reproduced-regression",
                "report-export-clear-acceptance",
                "conflicting-account-meanings",
            ],
        )
        self.assertEqual(
            [
                (scenario["workflow"], scenario["route"])
                for scenario in self.scenarios
            ],
            [
                ("contract", "quick"),
                ("contract", "guided"),
                ("contract", "guided"),
                ("contract", "guided"),
                ("contract", "guided"),
                ("diagnosis", None),
                ("contract", "quick"),
                ("contract", "guided"),
            ],
        )
        for scenario in self.scenarios:
            if scenario["workflow"] == "diagnosis":
                self.assertIsNone(scenario["route"])
                self.assertIsNone(scenario["first_question"])
                self.assertIsNone(scenario["draft"])
                self.assertEqual(scenario["skill"], "coderail-diagnose")
                continue

            self.assertIn(scenario["route"], self.protocol["routes"])
            question = scenario["first_question"]
            if scenario["route"] == "quick":
                self.assertIsNone(question)
                continue
            self.assertIsInstance(question, dict)
            self.assertEqual(
                set(question),
                {
                    "focus",
                    "question",
                    "recommendation",
                    "reason",
                    "impact",
                    "evidence",
                    "uncertainty",
                    "reversibility",
                },
            )
            self.assertTrue(all(question.values()))

    def test_material_items_obey_epistemic_state_requirements(self) -> None:
        requirements = self.protocol["item_requirements"]
        for scenario in self.scenarios:
            if scenario["draft"] is None:
                continue
            seen_ids: set[str] = set()
            for item in all_items(scenario["draft"]):
                self.assertIn(item["state"], STATES, scenario["id"])
                self.assertNotIn(item["id"], seen_ids, scenario["id"])
                seen_ids.add(item["id"])
                for field in requirements[item["state"]]:
                    self.assertIn(field, item, f"{scenario['id']}:{item['id']}")
                if item["state"] == "UNKNOWN":
                    self.assertNotEqual(
                        item["blocking"],
                        item["deferred"],
                        f"{scenario['id']}:{item['id']}",
                    )

    def test_readiness_is_derived_from_invariants(self) -> None:
        results = []
        for scenario in self.scenarios:
            draft = scenario["draft"]
            if draft is None:
                continue
            derived = derive_ready(draft)
            self.assertEqual(derived, draft["readiness"]["ready"], scenario["id"])
            blocking = sorted(
                item["id"]
                for item in all_items(draft)
                if item["state"] == "UNKNOWN" and item["blocking"]
            )
            deferred = sorted(
                item["id"]
                for item in all_items(draft)
                if item["state"] == "UNKNOWN" and item["deferred"]
            )
            self.assertEqual(blocking, sorted(draft["readiness"]["blocking"]))
            self.assertEqual(deferred, sorted(draft["readiness"]["deferred"]))
            results.append(derived)
        self.assertEqual(results, [True, False, False, False, False, True, False])

    def test_high_risk_assumptions_point_to_stop_items(self) -> None:
        for scenario in self.scenarios:
            draft = scenario["draft"]
            if draft is None:
                continue
            stop_ids = {item["id"] for item in draft["X"]}
            for item in all_items(draft):
                if item["state"] == "ASSUMPTION" and item["risk"] == "high":
                    self.assertIn(item.get("x_trigger"), stop_ids, scenario["id"])

    def test_promotion_requires_evidence_and_all_kind_specific_fields(self) -> None:
        outcomes = {}
        for case in self.promotion_cases:
            derived = derive_promotion(case, self.protocol)
            self.assertEqual(derived, case["eligible"], case["id"])
            outcomes[case["id"]] = derived
        self.assertFalse(outcomes["glossary-premature-user-acceptance"])
        self.assertTrue(outcomes["glossary-stable-term"])
        self.assertFalse(outcomes["adr-missing-evidence"])
        self.assertTrue(outcomes["adr-decision-grade"])

    def test_scenarios_include_deferred_unknown_and_rejected_promotions(self) -> None:
        self.assertTrue(
            any(
                item["state"] == "UNKNOWN" and item["deferred"]
                for scenario in self.scenarios
                if scenario["draft"] is not None
                for item in all_items(scenario["draft"])
            )
        )
        candidates = [
            candidate
            for scenario in self.scenarios
            for candidate in scenario["promotion_candidates"]
        ]
        self.assertTrue(any(not candidate["eligible"] for candidate in candidates))
        for candidate in candidates:
            self.assertEqual(
                derive_promotion(candidate, self.protocol),
                candidate["eligible"],
            )

    def test_protocol_contains_no_numeric_pseudo_scores(self) -> None:
        serialized = json.dumps(
            {
                "protocol": self.protocol,
                "scenarios": self.scenarios,
                "promotion": self.promotion_cases,
            }
        ).lower()
        for field in self.protocol["readiness"]["forbidden_fields"]:
            self.assertNotIn(f'"{field}":', serialized)


if __name__ == "__main__":
    unittest.main()
