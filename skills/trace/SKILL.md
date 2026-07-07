---
name: trace
description: Record a key development action as a trace event in docs/TRACELOG.jsonl. Use at task completion, when a new requirement appears, on task jumps, when research or a PoC ends, and before handoff.
---

# Trace

No action without a trace link. Every meaningful action records its source,
target, modification, validation, and persistence location.

This skill does not write business code. It writes a trace event draft and
appends it to `docs/TRACELOG.jsonl`.

## When to trace

Produce a trace event when any of these happens:

- A task is completed (`done`).
- A user adds a new requirement mid-session.
- A task jumps to a different goal, task, or scope.
- Research or a PoC ends (with `accepted`, `rejected`, or `superseded` status).
- A decision is recorded.
- A handoff is written (H1/H2/H3).
- A harness failure is repaired.
- An asset is promoted (A0/A1/A2 → A3/A4/A5) or rejected.

Do not trace trivial micro-edits that need no audit trail.

## Read first

1. `docs/NORTH_STAR.md` — to fill the G field and the `north_star` / `serves` links.
2. `docs/TASKS.md` — to fill the T field and the `implements` link.
3. `docs/HANDOFF.md` — if resuming or handing off.
4. The current task's CodeRail Coordinate (G/T/S/V/X/P).
5. `git status` / `git diff --stat` — for the `files` / `modifies` links.

## Event types

`intent` · `align` · `task` · `decision` · `research` · `attempt` · `change` ·
`verify` · `handoff` · `lesson`. See [`references/TRACE_GRAPH.md`](../../references/TRACE_GRAPH.md)
for the full schema and edge types.

## Output: Trace Event Draft

Return a draft using exactly this shape, then append it:

```markdown
## Trace Event Draft

type: change | verify | task | decision | research | attempt | handoff | lesson | intent | align
summary: (1-3 lines, no full logs or diffs)
task: T-XXX
north_star: NS-XXX
status: open | accepted | rejected | superseded | blocked | done
source_kind: user | agent | ci | external
source_ref: (chat id, file, url)
files: (comma-separated)
serves: NS-XXX
implements: T-XXX
modifies: (files/assets)
validated_by: (verify id or task)
coordinate:
  goal: (G)
  task: (T)
  verify: (V)
  persist: TASKS, TRACE, ...
```

## Rules

- Keep `summary` to 1-3 lines. Never paste full logs, full diffs, or transcripts.
- A `change` event must carry at least one of task, north_star, or files.
- A `verify` event must carry `harness_result` (`passed` / `failed` / `manual`).
- Embed the coordinate summary (G/T/V/P) on new change/verify/handoff events.
- Do not treat a research draft as an accepted decision. Use `research` with
  status `open`, and only flip to `accepted` after the decision is recorded.

## Append

If the plugin scripts are available, append the event and regenerate the index:

```bash
python3 scripts/trace_event.py --target . \
  --type change --summary "..." \
  --task T-XXX --north-star NS-XXX \
  --files src/foo.py \
  --implements T-XXX --modifies src/foo.py \
  --goal "..." --coordinate-task "..." --verify "pytest" --persist "TASKS,TRACE"

python3 scripts/trace_index.py --target .
```

If the script is unavailable, append one JSON line per event to
`docs/TRACELOG.jsonl` by hand, matching the schema in
[`references/TRACE_GRAPH.md`](../../references/TRACE_GRAPH.md). Then regenerate
the index when possible.
