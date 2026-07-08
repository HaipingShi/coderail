---
name: handoff
description: Create an event-triggered handoff snapshot with Coordinate Summary and inspect status, not an execution log.
---

# handoff

Use only when H1/H2/H3 trigger fires.

## Before writing handoff

1. Run or read `/coderail:inspect` so the handoff reflects current state.
2. Confirm the active Coordinate G/T/S/V/X/P.
3. Confirm verification gaps are either resolved or explicitly marked blocked.
4. Write a handoff trace event if this is H1/H2/H3.

## Handoff content

Keep it short:

- Current North Star / slice
- Coordinate Summary
- Current task and next task
- Verification state
- Trace gaps / blockers
- Next recommended action

Do not paste full logs, full diffs, or TRACELOG contents.
