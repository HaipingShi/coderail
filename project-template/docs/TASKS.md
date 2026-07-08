# Tasks

## Status legend

- `[ ]` todo
- `[~]` doing
- `[!]` blocked
- `[x]` done
- `[f]` failed
- `[r]` reopened

## Task Template

Copy this block and rename the heading to `\## T-001 Short task title` when creating a real task.

```markdown
\## T-001 Short task title

Status: [ ]
Type: feature | bug | refactor | docs | harness | chore
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

Done gate: pass | blocked | warning
Completed at:
Commit:
Harness result:
Manual acceptance:
Handoff level: H0 | H1 | H2 | H3
Trace:
Inspect status:
Notes:
```
