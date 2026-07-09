# Changelog

## Unreleased

Rail layering and friction reduction.

- Added Full Rail / Light Rail language for task type governance.
- Made explicit `Rail: full | light` required for current task contracts and done checks, with `--rail-type` as an intentional override.
- Let docs-only and design-only done checks use explicit manual acceptance without requiring fake engineering harness evidence.
- Classified old closed-task findings as historical debt in Doctor instead of current blockers.
- Added governance friction signals for long HANDOFF, long TASKS, warning noise, and docs/design tasks over-constrained by Full Rail.
- Slimmed HANDOFF and TASKS templates toward coordinate summary, recent slice, recovery commands, compact summaries, and trace back-links.
- Verified with `npm test`, `npm run ci`, Doctor, Blueprint Gate, Coordinate Check, and Contract Check.

## v0.7.3

TDD Gate.

- Added `references/TDD_GATE.md`, `skills/tdd-gate`, and `scripts/tdd_check.py`.
- Added TDD mode, Red check, Green check, Refactor check, Regression check, CI check, and Waiver reason fields to task and contract templates.
- Integrated TDD Gate into Doctor and CI Gate so correctness-sensitive tasks surface missing Red-Green-Refactor evidence.
- Documented default TDD policy for bugs, regressions, parsers, validators, domain logic, APIs, shared utilities, and risky refactors.
- Verified with `npm run ci`.

## v0.7.2

Auto-commit and CI Gate hardening.

- Changed closeout from commit recommendation to automatic task-scoped commit action when safe.
- Added `--auto-commit` support to `scripts/closeout_check.py`, staging only safe files derived from the task scope and never relying on broad staging.
- Added `scripts/ci_gate.py` and `npm run ci` to run non-decision checks without asking the user first.
- Hardened GitHub Actions with `workflow_dispatch`, read-only permissions, concurrency, timeout, and the shared CI Gate.
- Updated runtime entries, templates, skills, and docs to stop only for decision-grade blockers while executing CI, validation, inspect, trace, and safe auto-commit directly.
- Verified with `npm test` and `npm run ci`.

## v0.7.1

Closeout, loop continuity, and commit-boundary hardening.

- Added Closeout Gate reference and `/closeout` skill to prevent substantial work from ending with only a narrative summary.
- Added `scripts/closeout_check.py` to classify safe-to-stage files, do-not-stage files, ignored/generated artifacts, and `git add .` risk.
- Updated runtime entries, task and handoff templates, done/execute-batch/handoff skills, inspect state, and doctor checks to require Next Executable Step and Commit Readiness.
- Documented `stage-complete` as a first-class task result so partial progress can remain resumable without being mislabeled done.

## v0.7.0

Architecture Blueprint Layer.

- Upgraded Blueprint Awareness into Blueprint Gate with `scripts/blueprint_check.py`.
- Added `docs/BLUEPRINTS.md` and `project-template/docs/BLUEPRINTS.md` to track 4 classes and 11 core technical drawings.
- Expanded `references/BLUEPRINT_STANDARD.md` with diagram classes, lifecycle statuses, detection policy, and tooling guidance.
- Upgraded `skills/blueprint` from a non-blocking reminder into a blueprint coverage skill.
- Integrated Blueprint Gate into `doctor.py` so high-complexity projects can produce warnings or severe findings.
- Updated project initialization to copy `docs/BLUEPRINTS.md` in standard mode.
- Added `scripts/hook_guard.py` plus example hooks for prompt reminders, protected governance-file edits, and periodic doctor/blueprint checks.
- Added regression coverage for blueprint detection, lifecycle validation, and project-template install flow.

## v0.6.1

GitHub polish, install docs, and done gate hardening.

- Hardened `scripts/done_gate.py`: `skipped` harness results now require explicit manual acceptance, and scope matching is path-segment aware.
- Added `scripts/run_python.js` so npm scripts find a real Python interpreter instead of accepting broken `python3` shims.
- Fixed Windows UTF-8 test reads and added regression coverage for done gate scope matching and skipped verification.
- Reworked `README.md` with bilingual English/Chinese docs, richer icons, 5W2H, user/agent guidance, clone-first install prompts, and npm Git URL clarification.
- Added GitHub project hygiene: CI workflow, issue templates, PR template, release notes config, and release checklist.
- Expanded `CONTRIBUTING.md` and `SECURITY.md`; completed the MIT license text for better GitHub license detection.

## v0.6.0

Productization spine.

- Added Coordinate Contract Drafts: `skills/contract-draft`, `docs/CONTRACTS.md`, `references/CONTRACT_DRAFT.md`, and `scripts/contract_check.py`.
- Added Runtime State Inspect: `skills/inspect`, `docs/CODERAIL_STATUS.md`, `references/RUNTIME_STATE_INSPECT.md`, and `scripts/inspect_state.py`.
- Added Verification-before-complete: `skills/done-gate`, `references/DONE_GATE.md`, and `scripts/done_gate.py`.
- Updated `/done`, `/handoff`, `/doctor`, `AGENTS.md`, and `CLAUDE.md` to use contract draft, inspect, and done gate.
- Updated `init_project.py` to copy `CONTRACTS.md` and `CODERAIL_STATUS.md`.
- Updated tests to cover v0.6 scripts and entry files.

## v0.5.0

- Optimized current GitHub package.
- Fixed trace edge CLI handling and `--from-file` behavior.
- Tightened coordinate, trace, and doctor checks.
- Kept entry files short and schemas in references.
