---
name: done-gate
description: The final verification before marking a task done: evidence exists, changes stayed in the agreed files, docs are synced.
---

# Done Gate

This is an advanced, read-only diagnostic gate. It answers whether completion
is currently allowed; it does not close the task or replace `coderail done`.

## Action

Run:

```bash
python .coderail/coderail.py done-gate --task <TASK_ID> --harness-result passed
```

Tasks should declare `Rail: full` or `Rail: light` in TASKS. Use `--rail-type light --task-type docs|design` only as an intentional override for docs-only or design-only tasks that have not been updated yet. Use `--manual-acceptance` only when automatic harness is impossible and acceptance is explicit. Do not claim a skipped harness passed.

## Gate checks

- G still maps to North Star.
- T is complete.
- S was respected.
- V passed or manual acceptance was recorded.
- X is not triggered, or the trigger was resolved and recorded.
- P is synced, at least TASKS and TRACE.
- A verify trace exists or fresh verification evidence is supplied.
- TRACE_INDEX is current or will be regenerated before handoff.

For Light Rail, TASKS plus trace, decision backlink, or explicit manual acceptance is enough. Historical debt from old closed tasks should be labeled historical instead of blocking the current task.

## Structured Persist assertions

When P must prove a machine-owned surface exists, add a strict JSON assertion:

```text
P — Persist
- TASKS
- TRACE
- Persist-Assert: {"path":"docs/HANDOFF.md","contains":["<!-- coderail:continuation:start -->"]}
```

Paths must be repository-relative. `contains` is an optional list of exact
machine markers or serialized values; it is never a prose or semantic query.
Missing files, missing literals, unsafe paths, or invalid JSON block completion
as `PERSIST_GAP`. Do not add an assertion for ordinary project prose.

## Rules

- Failed verification blocks done.
- Missing P blocks done.
- Scope violation blocks done.
- Handoff is not always required, but Handoff Trigger Check is always required.
- Passing Done Gate is not enough to stop; final closeout must still state auto-commit action and a next executable step.
- A passing final `done` already authorizes one exact task-scoped local commit.
  Do not ask the user for separate commit approval unless they explicitly asked
  to review before committing; push, tag, or release remain separate decisions.
- Do not update TASKS, TRACE, status, or Git from this diagnostic; run
  `python .coderail/coderail.py done` for the completion transaction.
