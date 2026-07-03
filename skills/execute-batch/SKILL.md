---
name: execute-batch
description: Execute an authorized task or batch continuously until done, blocked, failed, or drift is detected. Use after task-contract when coding is allowed.
---

# Execute Batch

Work continuously inside the authorized task boundary.

## Before editing

Confirm:

```text
Current task:
North-Star Link:
Allowed Files:
Forbidden Files:
Acceptance:
Harness:
Stop Triggers:
```

## Execution rhythm

- Plan fine-grained internal steps.
- Execute without asking the user at every safe step.
- Keep changes inside Allowed Files.
- Prefer the smallest reversible implementation.
- Run focused tests as soon as useful.
- Keep detailed command noise out of HANDOFF; use RUNLOG if necessary.

## Must pause

Pause and report when:

- A required file is forbidden or outside the contract.
- A new product assumption appears.
- A public API, schema, permission, security, privacy, payment, or migration change is needed.
- Harness fails twice and the root cause is unclear.
- The implementation no longer maps to the North Star.
- The task is becoming broader than `What this task must not become`.

## Output while working

Keep intermediate updates short. Use:

```text
Progress:
Risk:
Next:
```

Do not produce a full handoff unless a handoff trigger is met.
