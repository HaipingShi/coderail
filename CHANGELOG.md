# Changelog

## Unreleased

Reporting integrity: closes the second round of field findings (FN-013..FN-018). The theme: what the tool reports must be exactly what happened — right task, real evidence, no noise.

### Progress journal integrity (FN-017)

- Fixed cross-contamination: each PROGRESS.md entry now carries its own task's title and evidence. `done` always passes the resolved task id through the whole gate chain, and cross-checks which task's status actually flipped in TASKS.md before reporting.
- "Checked by" always carries real evidence: verify exit codes, an explicit `manual check: ...`, or an honest `unverified - no verify commands registered`. Boilerplate can no longer appear as evidence.
- Per-item acceptance results land in the journal (`Acceptance [done]: ...` / `Acceptance [deferred]: ...`), so partial delivery is visible at a glance.

### Quiet close, full evidence on disk (FN-018)

- `done` now prints a compact summary (verdict, verify count, acceptance tally, warnings, commit status) of at most ~10 lines. The full gate output plus verify command output tails are persisted to `.coderail/reports/done-<stamp>-<task>.md` (gitignored).
- `done --verbose` restores the full console dump, with a clarifying note when the inspect section says "blocked" for project-level reasons unrelated to the passing task closure.
- Failure output is unchanged: when the gate fails, the details are the point and are printed in full.

### Business id leads (FN-014)

- Everywhere a task is shown — start, check, done summary, PROGRESS.md, commit messages — the user's id comes first: `T-186 (internal T-001)` and `chore(T-186/T-001): ...`.

### Acceptance input, unambiguous form (FN-016 follow-up)

- `--accept-status` now also takes numbered form: `--accept-status "1=done" --accept-status "2=deferred"` (any order, repeatable), removing order-mistake risk on long checklists. Positional `"done,deferred"` still works.

### Version single source of truth (FN-015 blind spot)

- README badge is now covered by the version-consistency test; a hand-copied shim (placeholder version) falls back to reading VERSION from the CodeRail home, and doctor explains it instead of raising a false mismatch.

### Tests

- Four new end-to-end lifecycle tests: journal cross-contamination, verify evidence propagation, acceptance ledger + deferred queueing, and summary-with-report-on-disk (67 total).

## v0.8.1

Trust hardening: closes the field-negative findings from the first real-world run (FN-001..FN-012). The theme: every promise the tool makes is now machine-checked, and every claim it reports is backed by evidence.

### done actually verifies (FN-010)

- `start --verify "cmd"` registers shell commands; `done` RUNS them and refuses to close the task on any non-zero exit, printing the failing command and output tail.
- All verify commands passing auto-fills harness evidence; "Checked by" in PROGRESS.md now records real exit codes (`` `npm test` exit 0 ``) instead of boilerplate.
- Closing without any machine check is allowed but permanently marked `UNVERIFIED` in the progress journal, with a warning at close time.

### One task identity everywhere (FN-011)

- `start --id T-186` (or a `T-186 ...` title prefix) binds the user's business id; `check`, `done`, PROGRESS.md, and the auto-commit message all show `T-00x (T-186)` consistently.

### Acceptance ledger (FN-012)

- `start --accept "item"` (repeatable) registers acceptance items; `done` refuses to close until each is explicitly marked `done` or `deferred` via `--accept-status`.
- Deferred items are automatically registered as queued follow-up tasks and listed in the progress entry — silent scope-shrink is no longer possible.

### TDD promise check (FN-009)

- `start --tests "file"` registers promised test files; `done` warns loudly when a promised test file never appears in the diff, and records the warning in PROGRESS.md.

### Install/upgrade single source of truth (FN-005, FN-002, FN-008)

- The shim (`.coderail/coderail.py`) is now versioned; `init` refreshes an outdated shim automatically and NEVER overwrites `config.json` (machine-local state).
- Shim errors now include actionable recovery: the `CODERAIL_HOME` override and the config path to fix.
- `doctor` checks shim version against the CodeRail home version and verifies `coderail_home` reachability.

### doctor checks concepts, not keywords (FN-007)

- A managed marker (`<!-- coderail:gates ... -->`) written by init certifies gate coverage; without it, each gate concept passes if ANY synonym appears — plain-language AGENTS.md files no longer produce false warnings.

### Blueprint truthfulness (FN-006, FN-008b)

- `init` prefills `docs/BLUEPRINTS.md` from detected code signals instead of defaulting everything to `not-applicable` and contradicting doctor one command later.
- `blueprint --scaffold` stubs now embed the project's detected layers and top-level directories, so agents replace placeholders with facts.

### Spin detection noise (FN-003)

- File churn now counts only pure modifications (`git log --name-status -M -C`); renames, copies, adds, and deletes no longer trigger false "never settles" warnings.

## v0.8.0

Convergent Coding.

The release that gives CodeRail its formal positioning — **spec is the output, not the input** — and rebuilds the outward interface around three plain commands so vibe coders and agents need zero terminology.

### Single entry point and plain-language interface

- Added `scripts/coderail.py`: `start` (begin a task), `check` (am I on track?), `done` (finish safely), `next` (pick up the next queued task). The 21 legacy scripts remain as advanced internals.
- `start` auto-generates the task coordinate and auto-infers the rail level; users never choose Full/Light Rail.
- Rewrote root and template `AGENTS.md` in plain language; internal jargon (K-invariants, L-levels, G/T/S/V/X/P) removed from the outward interface.
- Translated all 20 skill descriptions to natural language.
- Condensed `README.md` from 649 to under 100 lines with a 60-second quickstart first.

### Task chain: automatic handoff

- `done` recommends the next queued task after a successful close; `coderail next --go` activates it (deterministic: first queued task in file order).
- `check` shows queue state.

### Spinning-in-place detection (second-order feedback)

- Deterministic counters — failed `done` attempts, trace retries, file churn across recent commits, blocked tasks — trigger a plain-language `== Step back ==` notice in `check`/`done`.
- Escalation ladder: action → design (3 failures) → intent (5 failures, quoting the North Star). Counter state lives in `.coderail/spin.json` (git-ignored).

### Plain-language reporting

- Added `docs/PROGRESS.md`: three short lines per finished task, newest first — the one file a non-technical owner reads.
- After every successful `done`, a report scaffold forces the agent to answer three plain questions (what changed / how verified / what's next) with no jargon, no file paths, no tool names.

### Blueprint gap detection and scaffolding

- `check` and `done` surface missing/stale diagrams (4 layers, 11 classes) detected from real code signals (frontend, backend, schema, Dockerfile, CI config).
- Added `coderail blueprint --scaffold`: creates Mermaid stubs under `docs/blueprints/` and updates `docs/BLUEPRINTS.md` index rows to `planned`.
- Convergent rule codified: diagrams are ratified from what was built, never drawn ahead of the code.

### Positioning

- Added `references/CONVERGENT_CODING.md`: the explore → ratify → converge loop, what it borrows from SDD/TDD/DDD/cybernetics, and five testable design commitments (bilingual).
- Template `AGENTS.md` anchors the principle for agents: never demand an upfront spec; never violate ratified constraints.

### Rail layering and friction reduction (previously unreleased)

- Separated Execution Decision from read-only Recommendation Decision so manual Drive can block implementation without suppressing North Star continuation audit.
- Added the optional Recommendation Contract, nested JSON recommendation output, active-draft status filtering, Inspect dual-channel output, and contradiction checks in Drift Check.
- Added Full Rail / Light Rail language for task type governance, with explicit `Rail: full | light` required for current task contracts and done checks, and `--rail-type` as an intentional override.
- Let docs-only and design-only done checks use explicit manual acceptance without requiring fake engineering harness evidence.
- Classified old closed-task findings as historical debt in Doctor instead of current blockers.
- Added governance friction signals for long HANDOFF, long TASKS, warning noise, and docs/design tasks over-constrained by Full Rail.
- Slimmed HANDOFF and TASKS templates toward coordinate summary, recent slice, recovery commands, compact summaries, and trace back-links.
- Added a regression observation harness whose reusable script/docs are committed while run artifacts stay under `.coderail-runs/`.

### Verification

- All 63 structure tests pass (`npm test`, `npm run ci`).
- End-to-end tested in fresh repos: init → start → check → done auto-commit, `next --go` handoff, spin escalation at 3 and 5 failures, PROGRESS.md journaling, blueprint scaffold on a frontend + backend + SQL + Docker project.

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
