---
name: drift-check
description: Check for North Star, Coordinate, task, trace, and handoff drift.
---

# drift-check

Look for tasks without G, scope expansion without X, done without V/P, handoff direction not in NORTH_STAR, and trace orphans.

## Rules

- Keep output concise.
- Prefer G/T/S/V/X/P over duplicated fields.
- Do not write business code unless this skill explicitly covers execution.
- Do not hide failed verification.
