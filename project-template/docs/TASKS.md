# Tasks

## Status legend

- `[ ]` todo
- `[~]` doing
- `[!]` blocked
- `[x]` done
- `[f]` failed
- `[r]` reopened

Task result at closeout may be `done`, `stage-complete`, `blocked`, `failed`, or `deferred`. `stage-complete` usually keeps Status as `[~]`.

## Task Template

Copy this block and rename the heading to `\## T-001 Short task title` when creating a real task.

```markdown
\## T-001 Short task title

Status: [ ]
Type: feature | bug | refactor | docs | harness | chore
Rail: full | light
Priority: P1 | P2 | P3
Owner:
Branch:

### CodeRail Coordinate

G — Goal:
- North Star:
- Outcome served:

T — Task:
- 

S — Scope:
- Allowed:
  - 
- Forbidden:
  - none

V — Verify:
- TDD mode: required | optional | waived
- Red check:
- Green check:
- Refactor check:
- Regression check:
- CI check:
- Waiver reason:
- Harness:
  - 
- Manual acceptance:
  - 

X — Stop:
- forbidden files needed
- harness fails twice with unclear root cause

P — Persist:
- TASKS:
- HANDOFF:
- DECISIONS:
- LESSONS:
- ASSETS:
- TRACE:

### Task Contract

Depends on:
- 

Blocks:
- 

Acceptance:
- [ ] 
- [ ] 

### Critical Check

- [ ] G maps to `docs/NORTH_STAR.md`.
- [ ] Changes stayed inside S.
- [ ] V can verify the change or manual acceptance is explicit.
- [ ] P was synced, at least TASKS and TRACE.

### Completion

Task result: done | stage-complete | blocked | failed | deferred
Done gate: pass | blocked | warning
Completed at:
Commit:
Harness result:
Manual acceptance:
Handoff level: H0 | H1 | H2 | H3
Handoff updated: yes | no
Trace:
Inspect status:
Resume anchor:
Next executable step:
Auto commit:
- Eligible: yes | no
- Action: committed | skipped | blocked | failed
- Commit:
- Exact files staged:
- Safe to stage:
- Do not stage:
- Ignored/generated artifacts:
- Avoid git add .: yes | no
Notes:
```

## Compact summary policy

When a completed chain becomes long, keep only status, key result, completion
evidence, and trace backlink in TASKS. Move detailed logs, failed attempts,
terminal output, and long rationale to TRACE_INDEX, RUNLOG, DECISIONS, or an
archive. TASKS should stay fast to scan during recovery.
