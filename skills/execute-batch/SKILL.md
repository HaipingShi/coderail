---
name: execute-batch
description: Execute an authorized task or batch continuously until done, blocked, failed, or drift is detected. Use after task-contract when coding is allowed. Obeys the CodeRail Coordinate (G/T/S/V/X/P).
---

# Execute Batch

Work continuously inside the authorized task boundary. The CodeRail Coordinate
defines that boundary.

## Before editing

List the CodeRail Coordinate for each task in the batch:

```text
G — Goal:
T — Task:
S — Allowed / Forbidden:
V — Verify:
X — Stop:
P — Persist:
```

If multiple tasks in the batch do not share a G, they may not belong in the same
batch — flag this rather than silently mixing goals.

## Execution rhythm

- Plan fine-grained internal steps.
- Execute without asking the user at every safe step.
- Keep changes inside S (Allowed); respect S (Forbidden).
- Prefer the smallest reversible implementation.
- Run focused tests (V) as soon as useful.
- Keep detailed command noise out of HANDOFF; use RUNLOG if necessary.

## Task transitions

If work must jump to a different task mid-batch:

1. Do not switch silently. First write a trace `intent` or `task` transition event.
2. Confirm the new task has its own coordinate.
3. If the new task changes G or S, treat it as triggering X for the current task.

## Must pause (X triggers)

Pause and report when:

- A required file is forbidden or outside S.
- A new product assumption appears.
- A public API, schema, permission, security, privacy, payment, or migration change is needed.
- Harness (V) fails twice and the root cause is unclear.
- The implementation no longer maps to G (the North Star).
- The task is becoming broader than `What this task must not become`.
- G changes but `TASKS.md` / `NORTH_STAR.md` is not updated.
- S is being expanded but X was not revisited.

When X triggers, write a trace event recording the stop and the reason.

## Output while working

Keep intermediate updates short. Use:

```text
Progress:
Risk:
Next:
```

Do not produce a full handoff unless a handoff trigger is met. Do not interrupt
the user for low-risk internal steps — X is the pause boundary, not every step.
