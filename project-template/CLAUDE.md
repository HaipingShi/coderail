# Claude Code Runtime Entry

Follow `AGENTS.md`. The key rule is the North-Star Kernel: before coding, confirm the task serves `docs/NORTH_STAR.md`.

## Default flow

Use these plugin skills when available:

- `/coderail:align` for vague, high-level, drifting, or multi-step work.
- `/coderail:task-contract` before implementation.
- `/coderail:execute-batch` to proceed through authorized tasks without unnecessary confirmation.
- `/coderail:done` before marking work complete.
- `/coderail:handoff` only when a handoff trigger is met.
- `/coderail:drift-check` when documents, tasks, code, or user intent appear misaligned.

## Required before coding

Output a North-Star Check:

```text
Outcome:
Intent level:
Current slice:
This task serves:
Invariant to preserve:
What this task must not become:
Drift risk:
Proceed / reframe:
```

If the request is L0-L3, make the engineering judgment and task contract before implementation.

## Completion gate

Never mark done until harness has run or manual acceptance has been explicitly recorded.
