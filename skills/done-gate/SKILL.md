---
name: done-gate
description: Enforce verification-before-complete: check V, S, P, trace, and handoff trigger before marking a task done.
---

# Done Gate

Do not mark a task done until this gate passes.

## Action

Run:

```bash
python3 scripts/done_gate.py --target . --task <TASK_ID> --harness-result passed
```

Use `--manual-acceptance` only when automatic harness is impossible and acceptance is explicit.

## Gate checks

- G still maps to North Star.
- T is complete.
- S was respected.
- V passed or manual acceptance was recorded.
- X is not triggered, or the trigger was resolved and recorded.
- P is synced, at least TASKS and TRACE.
- A verify trace exists or fresh verification evidence is supplied.
- TRACE_INDEX is current or will be regenerated before handoff.

## Rules

- Failed verification blocks done.
- Missing P blocks done.
- Scope violation blocks done.
- Handoff is not always required, but Handoff Trigger Check is always required.
- Passing Done Gate is not enough to stop; final closeout must still state auto-commit action and a next executable step.
