---
name: link
description: Backfill missing edges between existing trace events in docs/TRACELOG.jsonl. Use to close orphan tasks/files/decisions/research and connect mid-session requirements to NORTH_STAR, TASKS, and HANDOFF.
---

# Link

Backfill missing relationships in the trace graph. This skill does not create
new business features and does not do broad rewrites. It only adds edges.

## When to use

- After `/trace` reports orphan events.
- When a mid-session requirement was implemented but never linked to a North Star or task.
- When `trace_doctor.py` reports verification gaps or missing coordinate edges.
- Before a PR or handoff, to tighten the chain.

## Read first

1. `docs/TRACELOG.jsonl` — the current events.
2. `docs/TRACE_INDEX.md` — Orphan Nodes and Verification Gaps sections.
3. `docs/NORTH_STAR.md`, `docs/TASKS.md`, `docs/HANDOFF.md`.

## Priority edges to backfill

In order, close the most damaging gaps first:

1. **G → NORTH_STAR** — a task whose Goal does not map to an Outcome / Current Bet / Invariant / Current Slice.
2. **T → TASKS** — a trace event with no task link.
3. **S → files/assets** — a change event with no `files` / `modifies`.
4. **V → evidence** — a `done` task or change with no `verify` event and no `validated_by`.
5. **P → docs** — a completed task whose `persist` named TASKS/DECISIONS/LESSONS/ASSETS but they were not updated.
6. **change → task** — change events that modified files but reference no task.
7. **verify → task** — verify events that reference no task.
8. **handoff → task** — handoff events that reference no task.
9. **decision → source** — decision events with no `source_ref` or `derived_from`.

## Output

```markdown
## Link Report

Events inspected: N
Edges added:
- TR-... implements T-XXX
- TR-... serves NS-XXX
- TR-... validated-by TR-...
- TR-... modifies src/foo.py

Still orphan:
- TR-... (reason)

Verification gaps closed:
- T-XXX now has verify TR-...

Next:
- /trace to record any new decision this link pass produced
- python3 scripts/trace_index.py --target .  (regenerate index)
- python3 scripts/trace_doctor.py --target .  (recheck)
```

## Rules

- Only add edges that are true. Do not invent task ids or file paths.
- If a task is genuinely orphan (no North Star mapping), flag it for `/align`
  rather than forcing a false link.
- If a done task has no verify event, do not fabricate one. Record a real
  `verify` event via `/trace` or mark the task `needs-verify`.
- Mid-session requirements: link them to NORTH_STAR / TASKS / HANDOFF. If they
  do not fit the current North Star, propose a backlog task instead of forcing
  the link.
- Keep the report short. Do not paste full events.
