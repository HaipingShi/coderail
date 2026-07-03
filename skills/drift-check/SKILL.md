---
name: drift-check
description: Detect North-Star drift, documentation rot, task/code mismatch, and asset confusion. Use after several tasks, before PRs, after handoff, or when the user says the work is drifting.
---

# Drift Check

Check whether the project is still moving toward the North Star.

## Read

- `docs/NORTH_STAR.md`
- `docs/TASKS.md`
- `docs/HANDOFF.md`
- `docs/DECISIONS.md`
- `docs/ASSETS.md`
- `git status`
- recent diff or commits when available

## Checks

1. Do recent tasks map to Outcome, Current Bet, Invariants, or Current Slice?
2. Does `HANDOFF.md` mention a new direction not in `NORTH_STAR.md`?
3. Does `TASKS.md` contain orphan tasks with no North-Star Link?
4. Did code introduce capability, public API, schema, dependency, or state not recorded in docs?
5. Did `DECISIONS.md` change the Current Bet without updating `NORTH_STAR.md`?
6. Does the harness still verify the actual Outcome?
7. Are raw materials or working notes being treated as permanent assets?
8. Is `HANDOFF.md` too long or acting as a log?

## Output

```markdown
## Drift Check Report

Overall status: aligned | minor drift | major drift | blocked

North-Star mismatches:
- 

Task/document mismatches:
- 

Code/document mismatches:
- 

Asset-boundary issues:
- 

Handoff/context issues:
- 

Required fixes before more coding:
- 

Safe next task:
- 
```

Do not write code as part of drift-check unless the user explicitly asks to repair the docs after the report.
