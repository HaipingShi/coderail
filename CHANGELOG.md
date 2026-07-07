# Changelog

All notable changes to CodeRail are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.2] - 2026-07-07

The governance protection + hooks release. Adds an explicit layering rule so
agents do not rewrite CodeRail's own governance files, and ships an opt-in hooks
example set for periodic drift correction.

### Added — Governance Layering
- **Governance Layering section** in `AGENTS.md`: L1 governance core (do not
  modify), L2 project assets (controlled edits via governance flow), L3 business
  code (free within Coordinate scope). Tells agents which files they may edit.
- **Claude Code `permissions.deny` example** expanded in
  `examples/claude/settings.example.json` to block edits to L1 paths
  (`references/`, `skills/`, `scripts/`, manifests, `AGENTS.md`,
  `docs/TRACELOG.jsonl`). Opt-in; not enabled by default.
- **`references/HOOKS.md`** — guide on what to protect with deny rules, what to
  wire as hooks vs pre-commit, and what must NOT be wired as a gate.

### Added — Periodic correction hooks (all opt-in)
- **`examples/hooks.example.json`** rewritten as a multi-scenario set:
  - `PostToolUse` (Write\|Edit): soft reminder to write a trace event.
  - `Stop`: short `doctor.py` summary at turn end so drift does not accumulate.
  - `pre_commit_examples`: hard gates for `coordinate_check.py` and
    `drift_check.py` (block commits missing G/V/P or with detected drift).

### Design rules enforced
- **`blueprint_check.py` is explicitly excluded** from all blocking hooks. It is
  an educational reminder layer; blocking on missing diagrams would misfire on
  every new project and violate its non-judgmental design.
- **CodeRail ships no active hooks by default.** All hook/deny examples are
  opt-in, user-reviewed. This stance is unchanged from v0.2.0.

### Changed
- `CLAUDE.md` runtime entry adds a one-line pointer to the Governance Layering
  rule (kept short).

## [0.4.1] - 2026-07-07

The Blueprint Awareness release. Adds a non-blocking educational layer that
surfaces the technical diagrams a project usually benefits from — turning
"unknown unknowns" into "at least heard of".

### Added — Blueprint Awareness
- **`references/BLUEPRINT_STANDARD.md`** — concise encyclopedia of the 11
  standard technical diagrams across 4 layers (interaction / architecture /
  data / deployment). Each entry: what pain it solves, the symptom of its
  absence, a minimal mermaid example, and when it's not needed.
- **`scripts/blueprint_check.py`** — scans project signals (UI? DB? multiple
  modules? HTTP API? stateful entities? Dockerfile? CI?), infers which diagrams
  are relevant for this project type, and surfaces them with inline
  explanations. Adaptive: a TTS model is not told it needs an ER diagram; a
  single-page gradio app is not told it needs User Flow.
- **`/blueprint` skill** — surfaces the relevant diagrams; never blocks,
  never judges compliance, only teaches that the diagrams exist.
- **`tests/test_blueprint.py`** — 17 tests covering signal detection,
  relevance mapping, and false-positive guards (transformer "transition" must
  not trigger a business state machine; "Link to" in a gradio file must not
  trigger multi-page UI).

### Changed
- **`scripts/doctor.py`** — adds a `## Blueprint Awareness` section to the
  report. Educational and non-blocking: never reports severe, never changes
  the exit code, never affects the health status.

### Notes
- This layer is **not** a kernel row (K0–K7 unchanged). It is a doctor section
  + a reference + an optional skill.
- It does **not** check whether diagrams were drawn. It only surfaces which
  diagrams the project type typically benefits from — so developers learn the
  names of structural concepts before the project rots in the middle stage.
- BIM analogy: vibe coding is like building by hand; a complex project without
  blueprints accumulates structural debt that becomes unfixable and un-auditable.
  This layer tells you "this kind of building usually has these diagrams —
  have you heard of them?"

## [0.4.0] - 2026-07-06

The Coordinate + Trace release. CodeRail gains a task coordinate compression layer
and a lightweight trace graph so every meaningful action is linkable to a source,
a target, validation, and persistence.

### Added — K1 CodeRail Coordinate
- **K1 CodeRail Coordinate** — every non-trivial task is compressed into six
  fields before implementation: **G**oal, **T**ask, **S**cope, **V**erify,
  **X** (Stop), **P**ersist. See [`references/CODERAIL_COORDINATE.md`](references/CODERAIL_COORDINATE.md).
- **`scripts/coordinate_check.py`** — verifies that active/doing/done tasks in
  `docs/TASKS.md` carry a complete coordinate (G/T/S allowed/S forbidden/V/X/P);
  done tasks must show V (harness or manual acceptance) and P (TASKS + TRACE).
- **CodeRail Coordinate block** in `docs/TASKS.md` ahead of the Task Contract.
- **Coordinate Summary** in `docs/HANDOFF.md` for resuming agents.
- **Coordinate Rule + drift signals** in `docs/NORTH_STAR.md`.
- CodeRail Coordinate short rule in `AGENTS.md` / `CLAUDE.md` (kept short;
  full text lives in references).

### Added — K7 Trace Graph Kernel
- **K7 Trace Graph Kernel** — *no action without a trace link.* Each meaningful
  development action records its source, target, modification, validation, and
  persistence location. See [`references/TRACE_GRAPH.md`](references/TRACE_GRAPH.md).
- **`docs/TRACELOG.jsonl`** — append-only, machine-readable event log (no comments
  in JSONL; explanations live in `TRACE_INDEX.md` and `references/TRACE_GRAPH.md`).
- **`docs/TRACE_INDEX.md`** — human-readable index, regenerated by script.
- **`scripts/trace_event.py`** — appends a typed event to `docs/TRACELOG.jsonl`
  with an auto-generated id (`TR-YYYYMMDD-HHMMSS-XXXX`), ISO timestamp, edges,
  and an optional embedded coordinate.
- **`scripts/trace_index.py`** — generates `docs/TRACE_INDEX.md` with sections:
  Current Active Chain, Recent Events, By Task, By File, By North Star, Orphan
  Nodes, Verification Gaps.
- **`scripts/trace_doctor.py`** — checks trace health (change without task,
  verify without harness_result, orphan events, stale index, etc.).
- **`/trace` skill** — produce a trace event draft at task completion, new
  requirements, task jumps, end of research, end of PoC, and before handoff.
- **`/link` skill** — backfill missing edges between existing trace events.

### Changed
- **Kernel renumbered to K0–K7.** The previous K1 Task Contract is now K2;
  the previous K2 Execution Rhythm is absorbed into the CodeRail Coordinate
  (G/T/X) and the `execute-batch` skill and is no longer a kernel row.
  Updated [`references/KERNEL.md`](references/KERNEL.md), README, and docs.
- **Task Contract** in `docs/TASKS.md` now holds only dependency, acceptance,
  and completion fields. Allowed/Forbidden Files, Harness, and Stop Triggers
  moved into the CodeRail Coordinate (S/V/X) to remove repeated wording.
- **`scripts/init_project.py`** now ships `docs/TRACELOG.jsonl` and
  `docs/TRACE_INDEX.md` in Standard mode.
- **`scripts/doctor.py`** integrates `coordinate_check.py` and `trace_doctor.py`
  and reports seven sections: North Star, Coordinate, Task Contract, Harness,
  Handoff, Asset Boundary, Trace Graph.
- **`scripts/drift_check.py`** adds Coordinate Drift and Trace Graph checks.
- All existing skills (`align`, `task-contract`, `execute-batch`, `done`,
  `handoff`, `drift-check`, `doctor`, `asset-boundary`, `harness-repair`,
  `project-init`) now read and emit the CodeRail Coordinate and trace events.

### Notes
- Old trace events are not required to carry a coordinate; new change/verify/
  handoff events should. `trace_doctor.py` warns rather than fails on legacy rows.
- The trace layer is intentionally small. It is not a graph database, project
  management system, or knowledge base. See the "what it is not" section of
  [`references/TRACE_GRAPH.md`](references/TRACE_GRAPH.md).

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

[0.4.2]: https://github.com/HaipingShi/coderail/releases/tag/v0.4.2
[0.4.1]: https://github.com/HaipingShi/coderail/releases/tag/v0.4.1
[0.4.0]: https://github.com/HaipingShi/coderail/releases/tag/v0.4.0
[0.2.0]: https://github.com/HaipingShi/coderail/releases/tag/v0.2.0
[0.1.0]: https://github.com/HaipingShi/coderail/releases/tag/v0.1.0
