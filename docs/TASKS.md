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

## T-016 Migrate legacy closed history out of hot TASKS

Status: [x]
Type: bug
Rail: full

### CodeRail Coordinate

G — Goal
- Complete T-015 migration so TASKS contains only open work while legacy T-001 and T-002 remain auditable in PROGRESS plus TRACE

T — Task
- Migrate legacy closed history out of hot TASKS

S — Scope
Allowed:
  - docs/TASKS.md
  - docs/PROGRESS.md
  - docs/TRACELOG.jsonl
  - docs/TRACE_INDEX.md
  - docs/CODERAIL_STATUS.md
  - docs/METRICS.md
  - tests/test_closeout.py
  - .coderail/tasks.json
  - .coderail/pending_close.json
Forbidden:
  - none

V — Verify
- Manually confirm the result works as intended.
- Run: `python scripts/coderail.py check` (must exit 0)
- Run: `python tests/test_closeout.py` (must exit 0)
- Run: `python tests/test_structure.py` (must exit 0)

A — Acceptance
- [ ] legacy T-001 and T-002 receive honest retroactive PROGRESS authority
- [ ] successful closeout compacts every closed body from TASKS
- [ ] immediate inspect is healthy and hot context is at most 3000 estimated tokens

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

Resume anchor: docs/TASKS.md#T-016

Next executable step: Continue in manual mode; no dependency-ready autonomous task is available to recommend.

Auto commit: requested
