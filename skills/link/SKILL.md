---
name: link
description: Backfill missing trace relationships.
---

# link

Fix missing task -> north_star, change -> task/files, verify -> task, handoff -> task, decision -> source. Do not invent facts.

## Rules

- Keep output concise.
- Prefer G/T/S/V/X/P over duplicated fields.
- Do not write business code unless this skill explicitly covers execution.
- Do not hide failed verification.
