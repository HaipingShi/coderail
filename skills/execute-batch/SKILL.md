---
name: execute-batch
description: Execute authorized tasks continuously inside S and X.
---

# execute-batch

Use `references/LOOP_ENGINEERING.md` for the full loop rule.

Before work, list each task coordinate. Continue without low-risk interruptions. Stop only at done, stage-complete batch boundary, blocked, failed, X fires, S expands, V becomes impossible, or G changes.

## Rules

- Keep output concise.
- Prefer G/T/S/V/X/P over duplicated fields.
- Do not write business code unless this skill explicitly covers execution.
- Do not hide failed verification.
- Fine-grained tasks are for traceability; they should not fragment the execution loop into unnecessary user stops.
- If stopping at stage-complete, provide a closeout packet with auto-commit action and one next executable step.
