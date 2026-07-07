---
name: drift-check
description: Detect North-Star drift, CodeRail Coordinate drift, Trace Graph gaps, documentation rot, task/code mismatch, and asset confusion. Use after several tasks, before PRs, after handoff, or when the user says the work is drifting.
---

# Drift Check

Check whether the project is still moving toward the North Star, whether the
CodeRail Coordinate still holds, and whether the trace graph has gaps.

## Read

- `docs/NORTH_STAR.md`
- `docs/TASKS.md`
- `docs/HANDOFF.md`
- `docs/DECISIONS.md`
- `docs/ASSETS.md`
- `docs/TRACELOG.jsonl` / `docs/TRACE_INDEX.md`
- `git status`
- recent diff or commits when available

## Coordinate Drift checks

1. Do recent tasks share, or cleanly switch, their G field?
2. Is there a task whose T changed but whose G did not (suspicious)?
3. Is there a task whose S was expanded but whose X was not revisited?
4. Is there a task whose V passed but whose P was not updated?
5. Does `HANDOFF.md`'s current task disagree with `TASKS.md`'s T?
6. Are there trace `change` events with no G/T link?

## North-Star checks

1. Do recent tasks map to Outcome, Current Bet, Invariants, or Current Slice?
2. Does `HANDOFF.md` mention a new direction not in `NORTH_STAR.md`?
3. Does `TASKS.md` contain orphan tasks with no G mapping?
4. Did code introduce capability, public API, schema, dependency, or state not recorded in docs?
5. Did `DECISIONS.md` change the Current Bet without updating `NORTH_STAR.md`?
6. Does the harness still verify the actual Outcome?

## Trace Graph checks

1. Are there recent tasks that cannot map to a North Star?
2. Are there orphan `change` events (no task/north_star/file)?
3. Are there done tasks missing a `verify` trace event?
4. Does `git diff` include product assumptions not registered anywhere?
5. Does `TRACELOG.jsonl` have orphan changes?
6. Is `TRACE_INDEX.md` stale relative to `TRACELOG.jsonl`?

## Asset checks

1. Are raw materials or working notes being treated as permanent assets?
2. Is `HANDOFF.md` too long or acting as a log?

## Optional script

```bash
python3 scripts/drift_check.py --target .
```

## Output

```markdown
## Drift Check Report

Overall status: aligned | minor drift | major drift | blocked

North-Star mismatches:
- 

Coordinate drift:
- 

Trace Graph gaps:
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

Do not write code as part of drift-check unless the user explicitly asks to
repair the docs after the report. Run `/link` to close trace gaps instead.
