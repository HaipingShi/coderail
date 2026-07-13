---
name: harness-repair
description: When the test/check setup itself is broken, fix it without weakening what it verifies.
---

# harness-repair

Classify failure, fix minimal root cause inside S, rerun V, and record verify/change/lesson trace events as needed.

## Rules

- Keep output concise.
- Prefer G/T/S/V/X/P over duplicated fields.
- Do not write business code unless this skill explicitly covers execution.
- Do not hide failed verification.
