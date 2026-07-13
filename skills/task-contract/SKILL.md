---
name: task-contract
description: Turn a request into a concrete task: goal, exact files allowed, how to verify, when to stop.
---

# task-contract

Use the Coordinate Draft Gate. Append or update TASKS.md with G/T/S/V/X/P, dependencies, acceptance, and completion fields. Write a task trace event.

For correctness-sensitive work, set `TDD mode` in V before implementation.

## Rules

- Keep output concise.
- Prefer G/T/S/V/X/P over duplicated fields.
- Do not write business code unless this skill explicitly covers execution.
- Do not hide failed verification.


## v0.6 Productization gate

For vague, high-risk, cross-module, or mid-session requirements, use `/coderail:contract-draft` before implementation. The draft can be accepted into a task contract or backlogged.
