from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = {
    "coderail-frame": True,
    "coderail-diagnose": True,
    "coderail-tdd-quality": True,
    "coderail-two-axis-review": True,
    "coderail-grill-contract": False,
}
VALIDATOR = (
    Path.home()
    / ".codex"
    / "skills"
    / ".system"
    / "skill-creator"
    / "scripts"
    / "quick_validate.py"
)


def skill_text(name: str) -> str:
    return (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")


def frontmatter(text: str) -> list[str]:
    parts = text.split("---", 2)
    if len(parts) != 3:
        return []
    return [line.strip() for line in parts[1].splitlines() if line.strip()]


class SkillContractTests(unittest.TestCase):
    def test_all_skills_pass_standard_validator(self) -> None:
        self.assertTrue(VALIDATOR.exists(), VALIDATOR)
        env = os.environ.copy()
        validation_deps = ROOT / ".test-deps"
        if validation_deps.exists():
            existing = env.get("PYTHONPATH")
            env["PYTHONPATH"] = str(validation_deps) + (
                os.pathsep + existing if existing else ""
            )
        for name in SKILLS:
            result = subprocess.run(
                [sys.executable, str(VALIDATOR), str(ROOT / "skills" / name)],
                text=True,
                capture_output=True,
                env=env,
            )
            self.assertEqual(result.returncode, 0, f"{name}: {result.stdout}{result.stderr}")

    def test_frontmatter_is_minimal_and_complete(self) -> None:
        for name in SKILLS:
            lines = frontmatter(skill_text(name))
            self.assertEqual(len(lines), 2, f"{name}: {lines}")
            self.assertEqual(lines[0], f"name: {name}")
            self.assertTrue(lines[1].startswith("description: "))
            self.assertGreater(len(lines[1]), 80)

    def test_invocation_policy_matches_role(self) -> None:
        for name, implicit in SKILLS.items():
            metadata = (
                ROOT / "skills" / name / "agents" / "openai.yaml"
            ).read_text(encoding="utf-8")
            if implicit:
                self.assertNotIn("allow_implicit_invocation: false", metadata, name)
            else:
                self.assertIn("allow_implicit_invocation: false", metadata, name)

    def test_every_skill_preserves_coderail_authority(self) -> None:
        required = [
            "## CodeRail boundary",
            "Do not write `.coderail/tasks.json`",
            "Never stage or commit task changes.",
            "python .coderail/coderail.py done",
        ]
        for name in SKILLS:
            text = skill_text(name)
            for marker in required:
                self.assertIn(marker, text, f"{name}: missing {marker}")

    def test_pack_contains_no_hook_or_direct_git_authority(self) -> None:
        forbidden = [
            "PreToolUse",
            "PostToolUse",
            "SessionStart",
            "git add .",
            "git commit",
            "git push",
        ]
        for path in (ROOT / "skills").rglob("*"):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            for marker in forbidden:
                self.assertNotIn(marker, text, f"{path}: contains {marker}")

    def test_no_skill_ships_executable_side_effects(self) -> None:
        for name in SKILLS:
            self.assertFalse((ROOT / "skills" / name / "scripts").exists(), name)

    def test_forward_test_fixes_remain_in_contract(self) -> None:
        diagnose = skill_text("coderail-diagnose")
        review = skill_text("coderail-two-axis-review")
        self.assertIn('--accept-status "1=done"', diagnose)
        self.assertIn("generated test artifacts", diagnose)
        self.assertIn("Keep a requested read-only review read-only", review)
        self.assertIn("`[~]` task in `docs/TASKS.md`", review)

    def test_frame_skill_implements_frozen_protocol(self) -> None:
        frame = skill_text("coderail-frame")
        protocol = json.loads(
            (ROOT / "fixtures" / "protocol.json").read_text(encoding="utf-8")
        )
        scenarios = json.loads(
            (ROOT / "fixtures" / "scenarios.json").read_text(encoding="utf-8")
        )

        for route in protocol["routes"]:
            self.assertIn(f"`{route}`", frame)
        for state in protocol["epistemic_states"]:
            self.assertIn(f"`{state}`", frame)
        for coordinate in protocol["coordinates"]:
            self.assertIn(f"`{coordinate}`", frame)

        question_fields = {
            field
            for scenario in scenarios
            if scenario["first_question"] is not None
            for field in scenario["first_question"]
        }
        for field in question_fields:
            self.assertIn(f"{field}:", frame)

        expected_focuses = {
            scenario["first_question"]["focus"]
            for scenario in scenarios
            if scenario["first_question"] is not None
        }
        for focus in expected_focuses:
            self.assertIn(focus, frame)

        self.assertIn("candidate lens", frame.lower())
        self.assertIn("never a fact", frame.lower())
        self.assertIn("repository evidence resolves", frame.lower())
        self.assertIn("user-facing question: none", frame.lower())
        self.assertIn("exactly one", frame.lower())
        self.assertIn("primary source", frame.lower())
        self.assertIn("exhaustive expert checklist", frame.lower())

        for forbidden in protocol["readiness"]["forbidden_fields"]:
            self.assertNotIn(forbidden, frame)

    def test_attribution_pins_an_upstream_commit(self) -> None:
        notice = (ROOT / "NOTICE.md").read_text(encoding="utf-8")
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("ed37663cc5fbef691ddfecd080dff42f7e7e350d", notice)
        self.assertIn("https://github.com/mattpocock/skills", notice)
        self.assertIn("Copyright (c) 2026 Matt Pocock", license_text)

    def test_templates_are_fully_resolved(self) -> None:
        for path in ROOT.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".yaml"}:
                self.assertNotIn("[TODO", path.read_text(encoding="utf-8"), str(path))


if __name__ == "__main__":
    unittest.main()
