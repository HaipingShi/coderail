# Changelog

All notable changes to CodeRail are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-07-03

The governance-first release. CodeRail now leads with the North-Star Kernel and
ships as installable plugins for Claude Code and Codex.

### Added
- **K0 North-Star Kernel** — every coding action must map to the current Outcome,
  Current Bet, Invariants, or Current Slice in `docs/NORTH_STAR.md`.
- **`docs/NORTH_STAR.md`** as the first-class, persistent direction anchor
  (target ≤ 100 lines).
- **`/align` skill** — intent-level check (L0–L5) before coding; produces a
  North-Star Check and a task-contract candidate.
- **`/drift-check` skill** — detects goal drift, orphan tasks, and documentation
  rot across `NORTH_STAR`, `TASKS`, `HANDOFF`, and `DECISIONS`.
- **Plugin manifests** for Claude Code (`.claude-plugin/`) and Codex
  (`.codex-plugin/`), with skills under `skills/`.
- **Project template** (`project-template/`) — `AGENTS.md`, `CLAUDE.md`, and the
  `docs/` set, plus `TASK_GRAPH.md` and `METRICS.md` for Standard mode.
- **Installer script** `scripts/init_project.py` with `--mode lite|standard`,
  copies templates without overwriting non-empty files.
- **`scripts/doctor.py`** — read-only governance health report.
- **`scripts/drift_check.py`** — static drift detection across docs.
- **Adoption Gate** (`references/ADOPTION_GATE.md`) — five criteria any new skill
  or workflow must pass to enter the default set.
- Four adoption tiers: **Lite, Standard, Team, Enterprise** (`references/MODES.md`).
- **Validation hierarchy** reference: executable harness > static acceptance >
  tool-native enforcement > human review > agent self-check (soft gate only).
- **`SECURITY.md`**, **`CONTRIBUTING.md`**, and **`CODE_OF_CONDUCT.md`**.

### Changed
- Converted the previous standalone document bundle into a plugin-compatible
  package with a clear `skills/` + `project-template/` + `references/` layout.
- Renamed the project to **CodeRail** (previously an internal codename).

### Removed
- All research-origin terminology from runtime files. The structure test
  (`tests/test_structure.py`) now enforces engineering-only language.

### Project metadata
- Rewritten `README.md` with explicit positioning, audience, and a comparison
  section covering Superpowers, spec-kit/Kiro, and BMAD.
- Public repository metadata (`package.json`, plugin manifests) point to
  [github.com/HaipingShi/coderail](https://github.com/HaipingShi/coderail).

### Notes
- Self-checks remain **soft gates only**. Harness, CI, permissions, hooks, and
  review remain the stronger validation layers (K3, K4).
- **No active hooks by default.** `examples/` contains sample hooks and
  permission configs that are default-off until you review and enable them.

## [0.1.0]

Initial document package.

### Added
- Task contracts (K1), execution rhythm (K2), harness gates (K3),
  tool-native enforcement (K4), handoff / continuation (K5), and asset
  boundary (K6).

[0.2.0]: https://github.com/HaipingShi/coderail/releases/tag/v0.2.0
[0.1.0]: https://github.com/HaipingShi/coderail/releases/tag/v0.1.0
