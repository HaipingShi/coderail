---
name: align
description: Align a user request with docs/NORTH_STAR.md before coding. Use for vague goals, high-level decisions, multi-step features, refactors, drift, or any task that might be local-optimal but globally wrong.
---

# Align

Do not write code during this skill. Align intent, outcome, and task slice first.

## Read

1. `docs/NORTH_STAR.md` if present.
2. `docs/TASKS.md` if present.
3. `docs/HANDOFF.md` if resuming or blocked.
4. `git status`.

If `docs/NORTH_STAR.md` is missing, create a provisional North Star before implementation.

## Intent levels

- L0 Outcome: final result or user outcome.
- L1 Product / Domain: user flows, domain objects, business rules.
- L2 Architecture: module boundaries, state ownership, runtime boundaries.
- L3 Technical Design: API, schema, error model, directories, technical choices.
- L4 Task Plan: task ID, acceptance, allowed files, forbidden files, harness.
- L5 Implementation: code, tests, scripts, config, migrations.

If the request is L0-L3, do not collapse it into implementation. Produce an engineering judgment and task contract first.

## North-Star Check output

Return exactly this structure:

```markdown
## North-Star Check

Outcome:
- 

User intent level: L0 | L1 | L2 | L3 | L4 | L5

Current slice:
- 

This task serves:
- Outcome:
- Current Bet:
- Invariant:

What this task must not become:
- 

Drift risk: none | low | medium | high

Proceed / Reframe:
- proceed | reframe | update NORTH_STAR | ask user

Recommended engineering judgment:
- 

Next task contract candidate:
- Task ID:
- Allowed Files:
- Forbidden Files:
- Acceptance:
- Harness:
```

## Stop conditions

Stop and reframe if:

- The task cannot map to Outcome, Current Bet, Invariants, or Current Slice.
- The user goal is ambiguous at L0-L2.
- The request requires breaking an invariant.
- The request implies new product scope not recorded in the North Star.
- Documentation and code disagree about the target behavior.
