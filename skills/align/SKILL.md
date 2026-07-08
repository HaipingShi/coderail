---
name: align
description: Align a user request with NORTH_STAR before coding and draft G/T/S/V/X/P.
---

# align

Do not write code. Read NORTH_STAR, TASKS, HANDOFF when relevant, and git status. Output North-Star Check plus Coordinate Draft. If G is vague or high-risk, stop for confirmation or create a proposed intent trace.

## Rules

- Keep output concise.
- Prefer G/T/S/V/X/P over duplicated fields.
- Do not write business code unless this skill explicitly covers execution.
- Do not hide failed verification.


## v0.6 Productization gate

For vague, high-risk, cross-module, or mid-session requirements, use `/coderail:contract-draft` before implementation. The draft can be accepted into a task contract or backlogged.
