from __future__ import annotations

import hashlib
import json
import unittest
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
V3 = ROOT / "evaluation-v3"
V4 = ROOT / "evaluation-v4"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def with_protocol(payload: Any, protocol: str) -> Any:
    normalized = deepcopy(payload)
    normalized["protocol_version"] = protocol
    return normalized


class EvaluationV4ProtocolTests(unittest.TestCase):
    def test_v4_changes_only_c_and_versioned_execution_metadata(self) -> None:
        v3_manifest = load_json(V3 / "manifest.json")
        v4_manifest = load_json(V4 / "manifest.json")
        self.assertEqual(v4_manifest["protocol_version"], "wp5-v4")
        self.assertEqual(v4_manifest["tasks"], v3_manifest["tasks"])
        self.assertEqual(v4_manifest["trial_design"], v3_manifest["trial_design"])

        self.assertEqual(
            (V4 / "workflows" / "A.md").read_bytes(),
            (V3 / "workflows" / "A.md").read_bytes(),
        )
        self.assertEqual(
            (V4 / "workflows" / "B.md").read_bytes(),
            (V3 / "workflows" / "B.md").read_bytes(),
        )
        self.assertNotEqual(
            (V4 / "workflows" / "C.md").read_bytes(),
            (V3 / "workflows" / "C.md").read_bytes(),
        )
        self.assertEqual(
            (V4 / "judge.md").read_bytes(),
            (V3 / "judge.md").read_bytes(),
        )

        v3_rubric = load_json(V3 / "rubric.json")
        v4_rubric = load_json(V4 / "rubric.json")
        self.assertEqual(
            with_protocol(v4_rubric, "wp5-v3"),
            v3_rubric,
        )

    def test_v4_c_closes_the_three_observed_failure_modes(self) -> None:
        workflow = (V4 / "workflows" / "C.md").read_text(encoding="utf-8")
        compact = " ".join(workflow.split())
        self.assertIn("GC-R1 Risk-control closure", workflow)
        self.assertIn("approval and audit evidence", compact)
        self.assertIn("placed outside scope", compact)

        self.assertIn("GC-R2 Decision-dependency closure", workflow)
        self.assertIn("every non-fallback scripted-answer trigger", compact)
        self.assertIn("dependency such as migration", compact)

        self.assertIn("GC-R3 Novice outcome ownership", workflow)
        self.assertIn("do not ask for a provider", compact)
        self.assertIn("investigation or stop condition", compact)

    def test_v4_c_preserves_clear_task_quick_path(self) -> None:
        workflow = (V4 / "workflows" / "C.md").read_text(encoding="utf-8")
        self.assertIn("GC-R4 Quick-path preservation", workflow)
        self.assertIn("remains quick", workflow)
        self.assertIn("fallback-only scripted answer is not a dependency", workflow)

        manifest = load_json(V4 / "manifest.json")
        clear_tasks = [
            task for task in manifest["tasks"]
            if task["category"] == "clear-local-reversible"
        ]
        self.assertEqual(len(clear_tasks), 6)
        self.assertTrue(
            all(task["oracle"]["expected_route"] == "quick" for task in clear_tasks)
        )

    def test_v4_schema_contracts_differ_only_by_protocol_const(self) -> None:
        for filename in (
            "model-output.schema.json",
            "judge-output.schema.json",
            "trial-result.schema.json",
        ):
            v3 = load_json(V3 / filename)
            v4 = load_json(V4 / filename)
            self.assertEqual(
                v4["properties"]["protocol_version"]["const"],
                "wp5-v4",
            )
            v4["properties"]["protocol_version"]["const"] = "wp5-v3"
            self.assertEqual(v4, v3, filename)

    def test_v4_hashes_remain_frozen(self) -> None:
        freeze = load_json(V4 / "freeze.json")
        self.assertEqual(freeze["protocol_version"], "wp5-v4")
        self.assertEqual(freeze["supersedes_for_execution"], "wp5-v3")
        for relative, expected in freeze["sha256"].items():
            actual = hashlib.sha256((V4 / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, relative)
        self.assertNotIn("results", freeze["sha256"])

    def test_v4_schema_preflight_passes_before_subject_batches(self) -> None:
        preflight = load_json(V4 / "preflight" / "schema-compatibility.json")
        self.assertEqual(preflight["protocol_version"], "wp5-v4")
        self.assertEqual(preflight["status"], "passed")
        self.assertEqual(preflight["model"], "gpt-5.4")
        self.assertEqual(preflight["reasoning_effort"], "medium")
        self.assertEqual(preflight["subject_batches_started"], 0)
        self.assertEqual(preflight["task_or_oracle_payloads_sent"], 0)


if __name__ == "__main__":
    unittest.main()
