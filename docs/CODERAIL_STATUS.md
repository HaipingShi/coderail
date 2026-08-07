# CodeRail Status

> Generated projection. `inspect` reads live state without rewriting this file.
> Preview with `coderail sync-projections`; write only with explicit `--apply`.

Generated at: 2026-08-07T15:49:43+00:00
Status: blocked

## Owner Product View

- Current verified capability: read-only status and planning distinguish control-plane authority, product evidence, generated projections, and historical ledgers.
- Current known limitation: downstream repositories need compatible, explicit projection synchronization without rewriting historical documents.
- Next smallest product gap: downstream repositories need compatible, explicit projection synchronization without rewriting historical documents.
- Active task: none
- Human authorization required: explicit owner approval is required before activation or execution

## Current North Star

- Outcome: Make CodeRail a reliable repo-local governance rail that agents can execute, verify, close out, and resume without dangling state.
- Current Slice: Milestone: M-014 lifecycle truth and owner communication

## Legacy Cutoff

- Enforcement starts at: T-001
- Status: active
- Historical tasks excluded from current verification status: 0

## Active Coordinate

- none

## Active Tasks

- none

## Paused Tasks

- none

## Task Switch Gate

- Active owners: 0
- Single-active invariant: pass
- Closed-task uncommitted ownership: none
- Automatic push: never

## Closeout Pending

- State: verified-commit-pending
- Task: T-060
- Safe files: 33
- Activation blocked until finalized: yes
- Resume: `coderail done --resume`

## Draft Contracts

- CD-002 Doctor marker compatibility — accepted
- CD-003 Task Switch Gate — accepted
- CD-004 Closeout Convergence — accepted
- CD-005 Lifecycle Truth, Projection Debt, and Formulation Safety — accepted

## Verification Gaps

- none

## Historical Verification Debt

- none

## Trace Gaps

- none

## Current Truth Projection Consistency

- pass

## Structured Diagnostics

- severity=error category=closeout_integrity blocks=activation evidence=T-060 is verified-commit-pending recommended_action=Resume the exact pending closeout before activating another task.

### Blocking Matrix

- formulation: false
- activation: true
- execution: false
- closeout: false
- delivery: false

## Drive Decision

- Mode: manual
- Decision: BLOCKED_DECISION
- Task: none
- Reason: Drive Contract is not in continuous mode.
- Next action: Continue in manual mode; no dependency-ready autonomous task is available to recommend.

## Execution Decision

- Mode: manual
- Decision: BLOCKED_DECISION
- Task: none
- Reason: Drive Contract is not in continuous mode.
- Next action: Continue in manual mode; no dependency-ready autonomous task is available to recommend.

## Recommendation Decision

- Status: NO_RECOMMENDATION
- Reason: No Recommendation Contract is configured; legacy execution behavior is preserved.
- Next action: Continue using explicit human direction or the existing Drive Contract.
- Requires human approval for execution: yes
- Evidence:
  - none

## Handoff

- Level: H0
- Needs update: no
- Last closed task: T-060
- Closeout state: verified-commit-pending

## Recommended Next Action

- Resume the verified closeout with `coderail done --resume`; do not rerun verification or use `git add .`.

## Technical Appendix

- Lifecycle receipts, marker details, safe-file counts, and Git state follow.

## Auto Commit

- Worktree: dirty
- Avoid `git add .` until changed files are matched to the active task S.
- Run `python .coderail/coderail.py finish --task <ID> --task-result <result>` before stopping.

## Git Status

```text
 M .coderail/tasks.json
 M README.md
 M README.zh-CN.md
 M docs/CODERAIL_DIAGRAMS.md
 M docs/CODERAIL_STATUS.md
 M docs/CONTRACTS.md
 M docs/DECISIONS.md
 M docs/DRIVE_LOOP_DESIGN.md
 M docs/HANDOFF.md
 M docs/HARNESS_SPEC.md
 M docs/NORTH_STAR.md
 M docs/PROGRESS.md
 M docs/TRACELOG.jsonl
 M docs/TRACE_INDEX.md
 M project-template/AGENTS.md
 M project-template/docs/CODERAIL_STATUS.md
 M project-template/docs/HANDOFF.md
 M references/DELIVERY_CONTRACT.md
 M references/DRIVE_LOOP.md
 M references/RUNTIME_STATE_INSPECT.md
 M scripts/coderail.py
 M scripts/delivery_contract.py
 M scripts/doctor.py
 M scripts/drive_check.py
 M scripts/drive_observe.py
 M scripts/inspect_state.py
 M scripts/repository_state.py
 M scripts/task_switch.py
 M tests/test_closeout.py
 M tests/test_delivery.py
 M tests/test_drive.py
 M tests/test_inspect.py
 M tests/test_static.py
```

