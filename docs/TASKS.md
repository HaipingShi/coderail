# Tasks

## Status legend

- `[ ]` todo
- `[~]` doing
- `[!]` blocked
- `[p]` paused
- `[x]` done
- `[f]` failed
- `[r]` reopened

## T-001 Self-bootstrap CodeRail execution boundary

Status: [x]
Type: feature
Rail: full
Priority: P1
Autonomy: allowed
Owner: Codex
Branch: main
Priority: P1
Autonomy: allowed
Owner: CodeRail maintainers
Branch: main

### CodeRail Coordinate

G — Goal:
- North Star: make CodeRail executable and resumable from a target repository
- Outcome served: reliable finish, persistence, and next-task behavior

T — Task:
- Install CodeRail governance into this repository and verify the local launcher, finish command, stop hook, safe state commit, and Drive recommendation behavior.

S — Scope:
- Allowed:
  - README.md
  - AGENTS.md
  - CLAUDE.md
  - .coderail/**
  - docs/**
  - examples/**
  - project-template/**
  - references/CLOSEOUT_GATE.md
  - scripts/**
  - skills/**
- Forbidden:
  - .git/**
  - project implementation outside the CodeRail runtime and governance files

V — Verify:
- TDD mode: optional
- Harness:
  - python -m pytest -q
  - npm test
  - python .coderail/coderail.py inspect --write
  - python .coderail/coderail.py finish --task T-001 --task-result stage-complete

X — Stop:
- verification failure with unclear root cause
- change required outside the allowed CodeRail scope
- git identity unavailable for the task-scoped commit

P — Persist:
- TASKS
- HANDOFF
- TRACE
- Inspect status
- Closeout commit

### Task Contract

Depends on:
- none

Blocks:
- none

Acceptance:
- [ ] target repositories receive `.coderail/coderail.py` and `.coderail/config.json`
- [ ] one finish command runs the stop boundary and reports the next action
- [ ] current repository has a persisted closeout state and task-scoped commit

### Completion

Task result: done
Done gate: warning
Completed at:
Commit:
Harness result: passed
Handoff level: H0
Handoff updated: no
Trace:
Inspect status: refreshed
Resume anchor: docs/TASKS.md#T-001
Next executable step: Continue in manual mode; no dependency-ready autonomous task is available to recommend.
Auto commit: requested
- Action: committed | skipped | blocked | failed
- Commit:
- Exact files staged:
- Safe to stage:
- Do not stage:
- Ignored/generated artifacts:
- Avoid git add .: yes | no
Notes:

Drive decision: BLOCKED_DECISION

## T-002 Doctor generated-marker compatibility

Status: [x]
Type: bug
Rail: full
Priority: P1
Autonomy: allowed
Owner: Codex
Branch: main

### CodeRail Coordinate

G — Goal:
- North Star: keep CodeRail executable and diagnosable across launcher migrations
- Outcome served: remove the false Doctor warning before production-project sync

T — Task:
- Accept both `scripts/inspect_state.py` and `.coderail/coderail.py inspect` generated-status markers without weakening invalid-status detection.

S — Scope:
- Allowed:
  - scripts/doctor.py
  - tests/test_structure.py
  - docs/NORTH_STAR.md
  - docs/TASKS.md
  - docs/CONTRACTS.md
  - docs/TRACELOG.jsonl
  - docs/TRACE_INDEX.md
  - docs/CODERAIL_STATUS.md
  - docs/HANDOFF.md
- Forbidden:
  - package.json
  - lockfiles
  - project-template behavior changes outside marker compatibility
  - /Users/geesh/projects/timeBuilderEngin/**

V — Verify:
- TDD mode: required
- Red check: `AttributeError: module 'scripts.doctor' has no attribute 'is_generated_status'`
- Green check: marker unit test passed for legacy, repo-local, and invalid text
- Refactor check: marker compatibility is localized to `is_generated_status`
- Regression check: `npm test` passed (63 tests)
- CI check: `npm run ci` passed
- Harness:
  - python scripts/doctor.py --target project-template
  - python scripts/drift_check.py --target project-template

X — Stop:
- Inspect output contract must change
- unrelated failing harness has unclear root cause

P — Persist:
- TASKS
- HANDOFF
- TRACE
- Inspect status
- Closeout commit

### Task Contract

Depends on:
- T-001

Blocks:
- downstream timeBuilderEngin CodeRail sync

Acceptance:
- [x] legacy generated marker remains accepted
- [x] repo-local launcher generated marker is accepted
- [x] unrelated status text still produces the Doctor warning
- [x] source test and CI gates pass

### Completion

Task result: done
Done gate: pending
Completed at:
Commit:
Harness result: passed
Handoff level: H0
Handoff updated: no
Trace:
Inspect status: refreshed
Resume anchor: docs/TASKS.md#T-002
Next executable step: Continue in manual mode; no dependency-ready autonomous task is available to recommend.
Auto commit: requested

Drive decision: BLOCKED_DECISION

## T-003 Task Switch Gate

Status: [x]
Display id: T-003
Type: feature
Rail: full

### CodeRail Coordinate

G — Goal
- Make task switches preserve single ownership, safe commits, resumable pause state, and truthful dirty baselines.

T — Task
- Task Switch Gate

S — Scope
Allowed:
  - scripts/coderail.py
  - scripts/task_switch.py
  - scripts/closeout_check.py
  - scripts/coordinate_check.py
  - scripts/done_gate.py
  - scripts/doctor.py
  - scripts/finish_task.py
  - scripts/drive_check.py
  - scripts/inspect_state.py
  - tests/test_structure.py
  - README.md
  - project-template/AGENTS.md
  - project-template/docs/TASKS.md
  - project-template/docs/HANDOFF.md
  - project-template/docs/CODERAIL_STATUS.md
  - references/CLOSEOUT_GATE.md
  - docs/NORTH_STAR.md
  - docs/TASKS.md
  - docs/CONTRACTS.md
  - docs/DECISIONS.md
  - docs/HANDOFF.md
  - docs/HARNESS_SPEC.md
  - docs/PROGRESS.md
  - docs/CODERAIL_STATUS.md
  - docs/TRACELOG.jsonl
  - docs/TRACE_INDEX.md
  - .coderail/tasks.json
Forbidden:
  - package.json
  - package-lock.json

V — Verify
- All switch-matrix lifecycle tests, regression tests, CI, and CodeRail done gate pass without multiple active tasks or automatic push.
- TDD mode: required
- Red check: `start --force` created T-002 while T-001 remained `[~]`; lifecycle assertion failed with two active owners.
- Green check: ten switch/baseline lifecycle tests plus a static no-push guard passed in isolated Git repositories.
- Refactor check: activation preflight, SHA-256 snapshots, pause/resume, closed ownership, and H3 recovery are centralized in `scripts/task_switch.py`.
- Regression check: `python3 tests/test_structure.py` passed (88 tests) after runtime integration and root-cause repair.
- CI check: `npm test` and `npm run ci` passed; Doctor, Blueprint, Contract, TDD, Drive, and whitespace gates passed inside CI.
- Run: `python3 tests/test_structure.py` (must exit 0)
- Run: `npm test` (must exit 0)
- Run: `npm run ci` (must exit 0)

A — Acceptance
- [x] accepted current task closes and commits before the destination starts
- [x] verified checkpoint commits then pauses the source before the destination starts
- [x] uncommittable work writes H3 and requires continue-current or dirty-fork
- [x] closed-task dirty ownership blocks ordinary start and next --go
- [x] pre-existing unrelated changes are fingerprinted and excluded from new-task attribution
- [x] dirty-fork preserves one active task and records the carried baseline
- [x] no switch or closeout path runs git push

X — Stop
- Stop if a switch can create multiple active tasks, commit unchanged baseline files, persist file contents, or require automatic push.
- Stop if compatibility requires package or lockfile changes.

P — Persist
- TASKS, CONTRACTS, DECISIONS, HANDOFF, HARNESS_SPEC, TRACE, Inspect status, closeout commits

Task result: done

Harness result: passed

Handoff level: H0

Handoff updated: no

Inspect status: refreshed

Drive decision: BLOCKED_DECISION

Resume anchor: docs/TASKS.md#T-003

Next executable step: Continue in manual mode; no dependency-ready autonomous task is available to recommend.

Auto commit: requested

## T-004 Prepare v0.9.0 release

Status: [x]
Display id: T-004
Type: release
Rail: full
Priority: P1
Autonomy: allowed
Owner: Codex
Branch: main

### CodeRail Coordinate

G — Goal
- Publish a coherent local v0.9.0 release candidate for Task Switch Gate without creating remote state.

T — Task
- Prepare v0.9.0 release

S — Scope
Allowed:
  - VERSION
  - package.json
  - README.md
  - .claude-plugin/plugin.json
  - .codex-plugin/plugin.json
  - CHANGELOG.md
  - docs/NORTH_STAR.md
  - docs/TASKS.md
  - docs/HARNESS_SPEC.md
  - docs/CODERAIL_STATUS.md
  - docs/TRACELOG.jsonl
  - docs/TRACE_INDEX.md
  - docs/PROGRESS.md
  - .coderail/tasks.json
Forbidden:
  - package-lock.json
  - node_modules/**
  - .git/**

V — Verify
- All version surfaces read 0.9.0, v0.9.0 changelog is complete, install smoke and full CI pass, release diff is committed locally, and no tag or push occurs.
- Run: `python3 tests/test_structure.py` (must exit 0)
- Run: `npm test` (must exit 0)
- Run: `npm run ci` (must exit 0)
- Run: `mkdir -p /tmp/coderail-v090-smoke && python3 scripts/init_project.py --target /tmp/coderail-v090-smoke --mode standard --force && rg -q '^SHIM_VERSION = "0\.9\.0"$' /tmp/coderail-v090-smoke/.coderail/coderail.py` (must exit 0)

A — Acceptance
- [ ] VERSION, package metadata, plugin manifests, and README badge agree on 0.9.0
- [ ] v0.9.0 changelog covers Task Switch Gate, closeout ledger integrity, and FN-029
- [ ] fresh install smoke reports shim v0.9.0
- [ ] full regression and CI pass
- [ ] release review finds no package or lockfile drift
- [ ] no tag and no push are created

X — Stop
- Stop and ask if changes are needed outside the allowed files.
- Do not create a release tag or modify remote state without separate authorization.
- Do not create or modify dependency lockfiles.

P — Persist
- TASKS, TRACE, PROGRESS, local task-scoped commit

Task result: done

Harness result: passed

Handoff level: H0

Handoff updated: no

Inspect status: refreshed

Drive decision: BLOCKED_DECISION

Resume anchor: docs/TASKS.md#T-004

Next executable step: Continue in manual mode; no dependency-ready autonomous task is available to recommend.

Auto commit: requested

## T-005 Safe ownership for new files and baseline adoption

Status: [x]
Display id: T-005
Type: bug
Rail: full

### CodeRail Coordinate

G — Goal
- Make done truthfully close task-owned new and baseline files without leaving inspect blocked

T — Task
- Safe ownership for new files and baseline adoption

S — Scope
Allowed:
  - scripts/__pycache__/blueprint_check.cpython-313.pyc
  - scripts/__pycache__/closeout_check.cpython-313.pyc
  - scripts/__pycache__/contract_check.cpython-313.pyc
  - scripts/__pycache__/coordinate_check.cpython-313.pyc
  - scripts/__pycache__/done_gate.cpython-313.pyc
  - scripts/__pycache__/drive_check.cpython-313.pyc
  - scripts/__pycache__/finish_task.cpython-313.pyc
  - scripts/__pycache__/hook_guard.cpython-313.pyc
  - scripts/__pycache__/init_project.cpython-313.pyc
  - scripts/__pycache__/inspect_state.cpython-313.pyc
  - scripts/__pycache__/local_entry.cpython-313.pyc
  - scripts/__pycache__/task_switch.cpython-313.pyc
  - scripts/__pycache__/tdd_check.cpython-313.pyc
  - scripts/__pycache__/trace_doctor.cpython-313.pyc
  - scripts/__pycache__/trace_index.cpython-313.pyc
  - scripts/blueprint_check.py
  - scripts/ci_gate.py
  - scripts/closeout_check.py
  - scripts/coderail.py
  - scripts/contract_check.py
  - scripts/coordinate_check.py
  - scripts/doctor.py
  - scripts/done_gate.py
  - scripts/drift_check.py
  - scripts/drive_check.py
  - scripts/drive_observe.py
  - scripts/finish_task.py
  - scripts/hook_guard.py
  - scripts/init_project.py
  - scripts/inspect_state.py
  - scripts/local_entry.py
  - scripts/regression_observe.py
  - scripts/run_python.js
  - scripts/task_switch.py
  - scripts/tdd_check.py
  - scripts/trace_doctor.py
  - scripts/trace_event.py
  - scripts/trace_index.py
  - tests/__pycache__/test_structure.cpython-313-pytest-8.4.1.pyc
  - tests/__pycache__/test_structure.cpython-313.pyc
  - tests/test_structure.py
  - docs/ASSETS.md
  - docs/BLUEPRINTS.md
  - docs/CODERAIL_STATUS.md
  - docs/CONTRACTS.md
  - docs/DECISIONS.md
  - docs/DRIVE_LOOP_DESIGN.md
  - docs/HANDOFF.md
  - docs/HARNESS_SPEC.md
  - docs/LESSONS.md
  - docs/METRICS.md
  - docs/NORTH_STAR.md
  - docs/PROGRESS.md
  - docs/REGRESSION_OBSERVE.md
  - docs/RELEASE_CHECKLIST.md
  - docs/RUNLOG.md
  - docs/TASKS.md
  - docs/TASK_GRAPH.md
  - docs/TRACELOG.jsonl
  - docs/TRACE_INDEX.md
  - references/ADOPTION_GATE.md
  - references/BLUEPRINT_STANDARD.md
  - references/CLOSEOUT_GATE.md
  - references/CODERAIL_COORDINATE.md
  - references/CONTRACT_DRAFT.md
  - references/CONVERGENT_CODING.md
  - references/DONE_GATE.md
  - references/DRIVE_LOOP.md
  - references/EXAMPLES.md
  - references/KERNEL.md
  - references/LOOP_ENGINEERING.md
  - references/MODES.md
  - references/RUNTIME_STATE_INSPECT.md
  - references/TDD_GATE.md
  - references/TOOL_NATIVE_ENFORCEMENT.md
  - references/TRACE_GRAPH.md
  - references/VALIDATION_HIERARCHY.md
  - project-template/AGENTS.md
  - project-template/CLAUDE.md
  - project-template/docs/ASSETS.md
  - project-template/docs/BLUEPRINTS.md
  - project-template/docs/CODERAIL_STATUS.md
  - project-template/docs/CONTRACTS.md
  - project-template/docs/DECISIONS.md
  - project-template/docs/HANDOFF.md
  - project-template/docs/HARNESS_SPEC.md
  - project-template/docs/LESSONS.md
  - project-template/docs/METRICS.md
  - project-template/docs/NORTH_STAR.md
  - project-template/docs/RUNLOG.md
  - project-template/docs/TASKS.md
  - project-template/docs/TASK_GRAPH.md
  - project-template/docs/TRACELOG.jsonl
  - project-template/docs/TRACE_INDEX.md
  - .coderail/coderail.py
  - .coderail/config.json
  - .coderail/tasks.json
Forbidden:
  - .git/**
  - node_modules/**
  - package-lock.json

V — Verify
- New glob files and auditable baseline adoption are safely committed or precisely blocked before closure, and post-done inspect is healthy
- Run: `python tests/test_structure.py` (must exit 0)
- Run: `npm test` (must exit 0)
- Run: `npm run ci` (must exit 0)

A — Acceptance
- [ ] lib/** owns new matching files created after start
- [ ] baseline adoption records fingerprints and excludes unsafe files
- [ ] done blocks ambiguous or forbidden files before closure
- [ ] done followed by inspect has no closed-task ownership

X — Stop
- Stop and ask if changes are needed outside the allowed files.

P — Persist
- TASKS, TRACE

Task result: done

Harness result: passed

Handoff level: H0

Handoff updated: no

Inspect status: refreshed

Drive decision: BLOCKED_DECISION

Resume anchor: docs/TASKS.md#T-005

Next executable step: Continue in manual mode; no dependency-ready autonomous task is available to recommend.

Auto commit: requested

## T-006 Atomic closeout success and post-commit inspect

Status: [x]
Display id: T-006
Type: bug
Rail: full

### CodeRail Coordinate

G — Goal
- Make successful done an atomic boundary whose post-commit Git state and inspect result agree

T — Task
- Atomic closeout success and post-commit inspect

S — Scope
Allowed:
  - scripts/**
  - scripts/__pycache__/blueprint_check.cpython-313.pyc
  - scripts/__pycache__/closeout_check.cpython-313.pyc
  - scripts/__pycache__/contract_check.cpython-313.pyc
  - scripts/__pycache__/coordinate_check.cpython-313.pyc
  - scripts/__pycache__/doctor.cpython-313.pyc
  - scripts/__pycache__/done_gate.cpython-313.pyc
  - scripts/__pycache__/drive_check.cpython-313.pyc
  - scripts/__pycache__/finish_task.cpython-313.pyc
  - scripts/__pycache__/hook_guard.cpython-313.pyc
  - scripts/__pycache__/init_project.cpython-313.pyc
  - scripts/__pycache__/inspect_state.cpython-313.pyc
  - scripts/__pycache__/local_entry.cpython-313.pyc
  - scripts/__pycache__/task_switch.cpython-313.pyc
  - scripts/__pycache__/tdd_check.cpython-313.pyc
  - scripts/__pycache__/trace_doctor.cpython-313.pyc
  - scripts/__pycache__/trace_index.cpython-313.pyc
  - scripts/blueprint_check.py
  - scripts/ci_gate.py
  - scripts/closeout_check.py
  - scripts/coderail.py
  - scripts/contract_check.py
  - scripts/coordinate_check.py
  - scripts/doctor.py
  - scripts/done_gate.py
  - scripts/drift_check.py
  - scripts/drive_check.py
  - scripts/drive_observe.py
  - scripts/finish_task.py
  - scripts/hook_guard.py
  - scripts/init_project.py
  - scripts/inspect_state.py
  - scripts/local_entry.py
  - scripts/regression_observe.py
  - scripts/run_python.js
  - scripts/task_switch.py
  - scripts/tdd_check.py
  - scripts/trace_doctor.py
  - scripts/trace_event.py
  - scripts/trace_index.py
  - tests/**
  - tests/__pycache__/test_structure.cpython-313-pytest-8.4.1.pyc
  - tests/__pycache__/test_structure.cpython-313.pyc
  - tests/test_structure.py
  - docs/**
  - docs/ASSETS.md
  - docs/BLUEPRINTS.md
  - docs/CODERAIL_STATUS.md
  - docs/CONTRACTS.md
  - docs/DECISIONS.md
  - docs/DRIVE_LOOP_DESIGN.md
  - docs/HANDOFF.md
  - docs/HARNESS_SPEC.md
  - docs/LESSONS.md
  - docs/METRICS.md
  - docs/NORTH_STAR.md
  - docs/PROGRESS.md
  - docs/REGRESSION_OBSERVE.md
  - docs/RELEASE_CHECKLIST.md
  - docs/RUNLOG.md
  - docs/TASKS.md
  - docs/TASK_GRAPH.md
  - docs/TRACELOG.jsonl
  - docs/TRACE_INDEX.md
  - references/**
  - references/ADOPTION_GATE.md
  - references/BLUEPRINT_STANDARD.md
  - references/CLOSEOUT_GATE.md
  - references/CODERAIL_COORDINATE.md
  - references/CONTRACT_DRAFT.md
  - references/CONVERGENT_CODING.md
  - references/DONE_GATE.md
  - references/DRIVE_LOOP.md
  - references/EXAMPLES.md
  - references/KERNEL.md
  - references/LOOP_ENGINEERING.md
  - references/MODES.md
  - references/RUNTIME_STATE_INSPECT.md
  - references/TDD_GATE.md
  - references/TOOL_NATIVE_ENFORCEMENT.md
  - references/TRACE_GRAPH.md
  - references/VALIDATION_HIERARCHY.md
  - .coderail/**
  - .coderail/coderail.py
  - .coderail/config.json
  - .coderail/reports/done-20260715-073852-T-005.md
  - .coderail/spin.json
  - .coderail/tasks.json
  - .gitignore
Forbidden:
  - .git/**
  - node_modules/**
  - dist/**
  - build/**
  - package-lock.json

V — Verify
- Done returns success only after final persistence commit and post-commit inspect prove no task-owned residue
- Run: `python tests/test_structure.py` (must exit 0)
- Run: `npm test` (must exit 0)
- Run: `npm run ci` (must exit 0)

A — Acceptance
- [ ] tracked modifications, new glob files, deletions and renames close cleanly
- [ ] unborn baseline adoption closes cleanly without ledger-only commits
- [ ] outside, sensitive, generated and ambiguous paths never cause false success
- [ ] post-commit rescan and inspect inconsistency force done failure
- [ ] no implementation or test uses git add .

X — Stop
- Stop and ask if changes are needed outside the allowed files.

P — Persist
- TASKS, TRACE

Task result: done

Harness result: passed

Handoff level: H0

Handoff updated: no

Inspect status: refreshed

Drive decision: BLOCKED_DECISION

Resume anchor: docs/TASKS.md#T-006

Next executable step: Continue in manual mode; no dependency-ready autonomous task is available to recommend.

Auto commit: requested

## T-007 Closeout characterization harness and convergence specification

Status: [x]
Display id: T-007
Type: refactor
Rail: full

### CodeRail Coordinate

G — Goal
- Freeze the verified closeout contract before migrating internal authority

T — Task
- Closeout characterization harness and convergence specification

S — Scope
Allowed:
  - tests/**
  - tests/__pycache__/test_structure.cpython-313-pytest-8.4.1.pyc
  - tests/__pycache__/test_structure.cpython-313.pyc
  - tests/test_structure.py
  - docs/**
  - docs/ASSETS.md
  - docs/BLUEPRINTS.md
  - docs/CODERAIL_STATUS.md
  - docs/CONTRACTS.md
  - docs/DECISIONS.md
  - docs/DRIVE_LOOP_DESIGN.md
  - docs/HANDOFF.md
  - docs/HARNESS_SPEC.md
  - docs/LESSONS.md
  - docs/METRICS.md
  - docs/NORTH_STAR.md
  - docs/PROGRESS.md
  - docs/REGRESSION_OBSERVE.md
  - docs/RELEASE_CHECKLIST.md
  - docs/RUNLOG.md
  - docs/TASKS.md
  - docs/TASK_GRAPH.md
  - docs/TRACELOG.jsonl
  - docs/TRACE_INDEX.md
  - references/**
  - references/ADOPTION_GATE.md
  - references/BLUEPRINT_STANDARD.md
  - references/CLOSEOUT_GATE.md
  - references/CODERAIL_COORDINATE.md
  - references/CONTRACT_DRAFT.md
  - references/CONVERGENT_CODING.md
  - references/DONE_GATE.md
  - references/DRIVE_LOOP.md
  - references/EXAMPLES.md
  - references/KERNEL.md
  - references/LOOP_ENGINEERING.md
  - references/MODES.md
  - references/RUNTIME_STATE_INSPECT.md
  - references/TDD_GATE.md
  - references/TOOL_NATIVE_ENFORCEMENT.md
  - references/TRACE_GRAPH.md
  - references/VALIDATION_HIERARCHY.md
  - .coderail/**
  - .coderail/coderail.py
  - .coderail/config.json
  - .coderail/reports/done-20260715-073852-T-005.md
  - .coderail/reports/done-20260715-080654-T-006.md
  - .coderail/spin.json
  - .coderail/tasks.json
Forbidden:
  - .git/**
  - package.json
  - node_modules/**

V — Verify
- The convergence specification is accepted, T-008/T-009 are queued, and black-box tests cover every closeout success and failure contract
- Run: `python tests/test_structure.py` (must exit 0)
- Run: `npm test` (must exit 0)
- Run: `npm run ci` (must exit 0)

A — Acceptance
- [ ] spec defines invariants, non-goals, state model and migration boundaries
- [ ] characterization matrix covers tracked, glob, adoption, outside, sensitive, generated, rename/delete and post-commit mutation
- [ ] T-008 and T-009 have explicit dependency, scope, verification and stop contracts

X — Stop
- Stop and ask if changes are needed outside the allowed files.

P — Persist
- TASKS, TRACE


Task result: done

Harness result: passed

Handoff level: H0

Handoff updated: no

Inspect status: refreshed

Drive decision: BLOCKED_DECISION

Resume anchor: docs/TASKS.md#T-007

Next executable step: Continue in manual mode; no dependency-ready autonomous task is available to recommend.

Auto commit: requested
## T-008 Canonical repository snapshot and ownership classifier

Status: [x]
Type: refactor
Rail: full
Priority: P1

### CodeRail Coordinate

G — Goal
- Give done, inspect, and task switching one immutable observation and one path classification vocabulary.

T — Task
- Introduce `repository_state.py` and migrate Git status parsing, fingerprints, baseline comparison, and closeout classification without changing external behavior.

S — Scope
Allowed:
  - scripts/repository_state.py
  - scripts/task_switch.py
  - scripts/closeout_check.py
  - scripts/inspect_state.py
  - scripts/done_gate.py
  - tests/**
  - docs/**
  - references/**
  - .coderail/**
Forbidden:
  - package.json
  - project-template/**
  - public command changes
  - automatic push

V — Verify
- Run all closeout characterization tests, `python tests/test_structure.py`, `npm test`, and `npm run ci`.

A — Acceptance
- [ ] one canonical Git status parser and immutable snapshot model
- [ ] one ownership classifier used by closeout and inspect ownership projection
- [ ] unchanged baseline, rename, ignored, sensitive, generated, and ephemeral semantics preserved
- [ ] duplicate readers removed rather than wrapped indefinitely

X — Stop
- Stop if migration requires a task-file schema change, weakens inspect, or changes characterized behavior.

P — Persist
- TASKS, DECISIONS, HARNESS, TRACE, closeout commits

Depends on:
- T-007


Task result: done

Harness result: passed

Handoff level: H0

Handoff updated: no

Inspect status: refreshed

Drive decision: BLOCKED_DECISION

Resume anchor: docs/TASKS.md#T-008

Next executable step: Continue in manual mode; no dependency-ready autonomous task is available to recommend.

Auto commit: requested
## T-009 Single closeout transaction authority

Status: [ ]
Type: refactor
Rail: full
Priority: P1

### CodeRail Coordinate

G — Goal
- Make one transaction service the only authority that can declare closeout success.

T — Task
- Introduce a closeout transaction state machine, move sequencing and final consistency into it, and reduce CLI/finish/check modules to adapters.

S — Scope
Allowed:
  - scripts/closeout_transaction.py
  - scripts/repository_state.py
  - scripts/coderail.py
  - scripts/finish_task.py
  - scripts/closeout_check.py
  - scripts/inspect_state.py
  - scripts/task_switch.py
  - tests/**
  - docs/**
  - references/**
  - .coderail/**
Forbidden:
  - package.json
  - project-template/**
  - new gates or public commands
  - automatic push

V — Verify
- Run the full characterization matrix, failure-injection tests, `python tests/test_structure.py`, `npm test`, `npm run ci`, and a real temporary `start -> change -> done -> inspect` flow.

A — Acceptance
- [ ] only FINALIZED can render Done or return success
- [ ] stage, commit, persistence, rescan, or inspect failure returns an explicit transaction failure
- [ ] provisional closure is compensatingly reopened on late failure
- [ ] duplicate closeout sequencing and success judgments are deleted
- [ ] immediate inspect agrees with every successful done

X — Stop
- Stop if a second success authority remains, recovery becomes less deterministic, or compatibility requires weakening a characterization test.

P — Persist
- TASKS, DECISIONS, HARNESS, TRACE, closeout commits

Depends on:
- T-008
