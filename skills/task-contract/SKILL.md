---
name: task-contract
description: Convert a user request into a concrete task with a CodeRail Coordinate (G/T/S/V/X/P), dependencies, and acceptance. Use before implementation.
---

# Task Contract

Create a bounded task before editing code. The CodeRail Coordinate is the core
of the contract; it compresses Goal, Task, Scope, Verify, Stop, and Persist
into one block so they are not scattered across separate fields.

## Required inputs

- `docs/NORTH_STAR.md`
- `docs/TASKS.md`
- `docs/HARNESS_SPEC.md`
- current user request
- `git status`

## Contract format

Append or update a task in `docs/TASKS.md` using this shape:

```markdown
## T-XXX Short task title

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

Depends on:
- 

Blocks:
- 

Acceptance:
- [ ] 
- [ ] 
```

## Coordinate checks

Before finalizing the contract, verify every field:

- **G** maps to an Outcome / Current Bet / Invariant / Current Slice in `NORTH_STAR.md`.
- **T** is concrete enough to verify (not "optimize the system").
- **S** lists both Allowed and Forbidden (Forbidden stops scope creep).
- **V** is executable (harness) or explicit manual acceptance.
- **X** includes risk boundaries (forbidden files, API/schema change, new dependency, destructive migration, security/permissions/payment/privacy, harness failing twice).
- **P** includes TASKS and TRACE; add HANDOFF/DECISIONS/LESSONS/ASSETS only when relevant.

## Rules

- Use the smallest task that still produces a meaningful verified increment.
- Include `What this task must not become` inside G to stop scope creep.
- If no harness exists, create a harness task before implementation or define manual acceptance in V.
- Do not create more than one active task unless the user asks for a plan or execution batch.

## Trace

After creating or updating the task, write a `task` trace event with the
coordinate summary. Use `/trace` or `scripts/trace_event.py --type task`.
