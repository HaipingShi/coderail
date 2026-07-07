# Tasks

## Status legend

- `[ ]` todo
- `[~]` doing
- `[!]` blocked
- `[x]` done
- `[f]` failed
- `[r]` reopened

## T-001 Example task

Status: [ ]
Type: feature | bug | refactor | docs | harness | chore
Priority: P1 | P2 | P3
Owner:
Branch:

### CodeRail Coordinate

> The coordinate compresses Goal, Task, Scope, Verify, Stop, and Persist into
> one block. It replaces the old separate North-Star Link / Allowed Files /
> Forbidden Files / Harness / Stop Triggers / Persisted Assets fields. See
> `references/CODERAIL_COORDINATE.md`.

G — Goal:
- North Star:
- Outcome served:

T — Task:
- 

S — Scope:
- Allowed:
  - 
- Forbidden:
  - 

V — Verify:
- Harness:
  - 
- Manual acceptance:
  - 

X — Stop:
- 
- 

P — Persist:
- TASKS:
- HANDOFF:
- DECISIONS:
- LESSONS:
- ASSETS:
- TRACE:

### Task Contract

> Dependency, acceptance, and completion only. Scope/verify/stop live above in
> the CodeRail Coordinate so they are not duplicated.

Depends on:
- 

Blocks:
- 

Acceptance:
- [ ] 
- [ ] 

### Critical Check

- [ ] The task maps to `docs/NORTH_STAR.md` through its G field.
- [ ] The request level was not collapsed incorrectly into implementation.
- [ ] Changes stayed inside S (Allowed) and respected S (Forbidden).
- [ ] No raw material or working note was treated as a permanent asset.
- [ ] New dependency, API, schema, or persistent state was recorded.
- [ ] V can verify the change, or manual acceptance is explicit.
- [ ] P was synced (at least TASKS and TRACE).

### Completion

Completed at:
Commit:
Harness result:
Handoff level: H0 | H1 | H2 | H3
Trace:
Notes:
