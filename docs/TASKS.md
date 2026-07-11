# Tasks

## Status legend

- `[ ]` todo
- `[~]` doing
- `[!]` blocked
- `[x]` done
- `[f]` failed
- `[r]` reopened

## T-001 Self-bootstrap CodeRail execution boundary

Status: [~]
Type: feature
Rail: full
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

Task result: stage-complete
Done gate: warning
Completed at:
Commit:
Harness result: passed
Handoff level: H1
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
