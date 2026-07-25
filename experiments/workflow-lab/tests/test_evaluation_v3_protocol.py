from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V2 = ROOT / "evaluation-v2"
V3 = ROOT / "evaluation-v3"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class EvaluationV3ProtocolTests(unittest.TestCase):
    def test_v3_preserves_v2_experiment_semantics(self) -> None:
        v2_manifest = load_json(V2 / "manifest.json")
        v3_manifest = load_json(V3 / "manifest.json")
        self.assertEqual(v3_manifest["tasks"], v2_manifest["tasks"])
        self.assertEqual(v3_manifest["trial_design"], v2_manifest["trial_design"])
        for name in ("A.md", "B.md", "C.md"):
            self.assertEqual(
                (V3 / "workflows" / name).read_bytes(),
                (V2 / "workflows" / name).read_bytes(),
            )
        self.assertEqual(
            load_json(V3 / "rubric.json")["metrics"],
            load_json(V2 / "rubric.json")["metrics"],
        )

    def test_v3_adds_types_to_constant_constraints(self) -> None:
        subject = load_json(V3 / "model-output.schema.json")
        judge = load_json(V3 / "judge-output.schema.json")
        trial = load_json(V3 / "trial-result.schema.json")
        self.assertEqual(subject["properties"]["protocol_version"]["type"], "string")
        self.assertEqual(
            subject["properties"]["responses"]["items"]["properties"][
                "stop_after_contract"
            ]["type"],
            "boolean",
        )
        self.assertEqual(judge["properties"]["protocol_version"]["type"], "string")
        self.assertEqual(trial["properties"]["protocol_version"]["type"], "string")

    def test_v3_hashes_remain_frozen(self) -> None:
        freeze = load_json(V3 / "freeze.json")
        for relative, expected in freeze["sha256"].items():
            actual = hashlib.sha256((V3 / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, relative)
        self.assertNotIn("results", freeze["sha256"])

    def test_v3_schema_preflight_passes_before_subject_batches(self) -> None:
        preflight = load_json(V3 / "preflight" / "schema-compatibility.json")
        self.assertEqual(preflight["status"], "passed")
        self.assertEqual(preflight["model"], "gpt-5.4")
        self.assertEqual(preflight["subject_batches_started"], 0)
        trials = V3 / "results" / "trials"
        self.assertFalse(trials.exists() and any(trials.iterdir()))


if __name__ == "__main__":
    unittest.main()
