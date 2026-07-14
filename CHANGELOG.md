# Changelog

## Unreleased

No unreleased changes.

## v0.9.0

Task Switch Gate: CodeRail now treats switching work as an explicit lifecycle transition instead of allowing a second active task to emerge through `--force`. This minor release also hardens closeout ownership and includes the cross-platform scope-path fix from FN-029.

### Safe task switching

- Added the paused task state (`[p]`) and first-class `switch` flows for accepted work, verified checkpoints, unsafe dirty work, and paused-task resume.
- Accepted work closes through the normal done boundary before the destination task starts. A verified checkpoint is committed as `stage-complete`, then the source task is paused before activation moves to the destination.
- Unsafe work is not committed automatically. CodeRail writes an H3 handoff and requires an explicit choice between continuing the current task and carrying the dirty baseline into a fork.
- A closed task that still owns dirty paths blocks ordinary `start`, `next --go`, and switching. Carrying those paths requires an explicit waiver.
- Pre-existing unrelated changes are recorded as a path, Git status, and SHA-256 baseline. Unchanged baseline paths are not attributed to the new task.
- Automatic commit remains local-only. No CodeRail start, switch, next, or done path performs `git push`.

### Closeout ledger integrity

- A successful closeout persists the task-scoped source commit first, then records the exact resulting commit in the closeout ledger with a dedicated metadata commit.
- Closed dirty ownership is audited before activation, preventing an already-finished task from silently lending uncommitted changes to later work.
- Pausing and resuming preserve a single active owner and restore the original task ownership instead of relying on `--force` to manufacture multiple active tasks.

### Cross-platform scope paths (FN-029)

Caught by the Windows CI matrix that Linux-only local runs had been missing.

- `--files` glob expansion wrote OS-native separators into `docs/TASKS.md` — backslashes on Windows. Because the committed scope block is matched against `git` output (always forward-slash) by the drive-check scope gate, Windows-declared scopes silently failed to match their own changed files, and the committed artifact was not portable across machines.
- The pattern is now normalized to forward-slash BEFORE globbing (so a Windows-style `src\dir\*.ts` still expands) and every stored path uses `Path.as_posix()`. The done-report backlinks written into `TASKS.md`/`PROGRESS.md` are normalized the same way.
- The FN-021 regression test now feeds a backslash-style pattern and asserts the committed Allowed-scope block contains no backslash, so the contract is enforced even on Linux-only runs (76 total).

### Verification

- Version consistency covers `VERSION`, package metadata, both plugin manifests, and the README badge; installed launchers are stamped from the same source.
- The release candidate is gated by the full Python regression suite, npm test and CI entrypoints, and a fresh standard-mode install smoke.

## v0.8.4

Close-before-report ordering fix: closes the fourth round of field findings (FN-027/FN-028) and corrects the root-cause analysis of FN-023. The theme: the closeout ledger runs from a snapshot taken before anything mutates, and every verdict printed matches what actually happened on disk.

### Root cause correction (FN-027, supersedes the FN-023 analysis)

- The v0.8.2 FN-023 fix targeted the wrong branch: it assumed warning paths skipped the ledger, but the fourth field run (T-191, zero warnings) proved the real defect is ordering - `done` decided success purely by the gate's return code, and the gate can return failure AFTER the task was already closed and committed (its late stages query "the current active task", which by then no longer exists). The old rc-only branch then skipped the whole ledger and printed a misleading "run done again".
- `done` now decides by facts, not return codes: after the gate runs, it checks whether the task actually flipped to `[x]` in TASKS.md. A closed-and-committed task gets its full ledger (journal entry, on-disk report, deferred queueing) even when the gate reports failure, with an explicit `GATE INCONSISTENCY` note instead of silence.
- The "run done again" hint is only printed when the task is genuinely still open; a failure on an already-closed task points to `coderail progress --repair` instead.
- `finish_task`'s Finish Task Report matches reality: when checks fail after the task was marked done and committed, it reports `done (WITH ERRORS)` with an explicit do-not-rerun note, never a bare "blocked".
- Built-in fuse: `done` ends by running the same audit as `coderail progress` and hard-fails with `LEDGER ERROR` if the journal entry it just claimed to write is not actually on disk.

### Closeout snapshot (FN-028)

- Before any state-mutating step, `done` persists the full closeout context to `.coderail/pending_close.json` (gitignored): task id, display id, title, `--next` text, acceptance items and verdicts, manual-acceptance note, verify results. No ledger step depends on "the current active task" any more.
- The snapshot is deleted only after the ledger is fully written. If a close is interrupted mid-ledger, `progress --repair` reads the surviving snapshot and restores the REAL `--next` text, per-item acceptance verdicts, and verify evidence into the retroactive entry - not default copy.

### Tests

- Lessons applied from FN-023's failed fix: the three new regression tests are end-to-end against the real `done` flow, no mocked report layer. They assert (a) two consecutive closes each leave all four artifacts at once (journal entry with verbatim `--next`, on-disk report with a non-blocked Done Gate, closed TASKS entry, task commit) plus a clean audit; (b) a sabotaged journal keeps the snapshot and `--repair` restores the original parameters verbatim; (c) the rerun hint only appears for genuinely open tasks (76 total).

## v0.8.3

Ledger integrity and gate coherence: closes the third round of field findings (FN-020..FN-024) from the timebuild run. The theme: closing a task and recording that close are one transaction, and both ends of a task's life apply the same rules.

### Transactional closeout (FN-023)

- Fixed a silent ledger regression: in continuous mode (gate exit 3) `done` closed the task and committed but skipped the PROGRESS entry and the on-disk report entirely. Both exit paths of a successful close now run the same ledger steps.
- Each ledger step (report file, journal entry, deferred queueing) is individually guarded: any failure prints an explicit `LEDGER ERROR` naming the failed step and the remedy, and `done` exits non-zero instead of reporting success.
- New `coderail progress` audits the ledger (every closed task must have a journal entry); `coderail progress --repair` backfills honest retroactive entries — marked as repairs, referencing surviving reports and registered verify commands — for historical gaps like T-190.

### TDD gate coherence (FN-024)

- The TDD heuristic now respects an explicitly declared `Type:` — `refactor` (and docs/chore/release/etc.) tasks no longer get "likely needs TDD mode" at done after being waved through at start. `tdd_required()` in tdd_check.py is the single source of the verdict for start, check, and done.
- Tasks that promised test files at start (`--tests`) are no longer nagged by the heuristic; the diff check (FN-009) already covers them. The bare keyword "refactor" was removed from the hint list — the explicit type is the signal.

### Scope declaration ergonomics (FN-021)

- `--files` is now repeatable and accepts globs: `--files "src/director/director*.ts" --files "docs/x.md,README.md"`. Globs expand against the repo at start (deduplicated, unmatched patterns kept literally for files created later), so the done scope check sees real paths.

### Portable home resolution (FN-022)

- The shim resolves the CodeRail home in order: `CODERAIL_HOME` env > gitignored `.coderail/config.local.json` > `config.json`; each source may hold a single path or a list of candidates probed in order. Cloud sandboxes set the local override once instead of exporting per shell; failures list every probed path.

### Closeout copy (FN-020)

- `done --next "..."` writes the real next step into the journal's Next field (default text only when omitted); the "Now tell the user" template truncates long verify evidence at 70 chars, pointing to the on-disk report for the full text.

### Tests

- Six new end-to-end tests: warning-laden done still writes the ledger, sabotaged journal fails loudly and repairs cleanly, refactor/feature TDD-hint contrast, glob expansion, candidate-home probing, and `--next` injection (73 total).

## v0.8.2

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
