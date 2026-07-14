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
