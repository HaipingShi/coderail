---
name: task-contract
description: Convert a user request into a concrete task contract with North-Star Link, allowed files, acceptance, harness, and stop triggers. Use before implementation.
---

# Task Contract

Create a bounded task before editing code.

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

### North-Star Link

Outcome served:
- 

Current Bet served:
- 

Invariant preserved:
- 

Why now:
- 

What this task must not become:
- 

Drift risk: low | medium | high

### Task Contract

Depends on:
- 

Blocks:
- 

Allowed Files:
- 

Forbidden Files:
- 

Acceptance:
- [ ] 
- [ ] 

Harness:
- [ ] 

### Stop Triggers

- forbidden files required
- public API or schema change
- new dependency required
- destructive migration
- security, permissions, payment, privacy impact
- harness fails twice with unclear root cause
- task no longer maps to North Star
```

## Rules

- Use the smallest task that still produces a meaningful verified increment.
- Include `What this task must not become` to stop uncontrolled scope expansion.
- If no harness exists, create a harness task before implementation or define manual acceptance.
- Do not create more than one active task unless the user asks for a plan or execution batch.
