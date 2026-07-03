---
name: harness-repair
description: Repair failing lint, typecheck, test, build, CI, migration dry-run, or manual acceptance loops without hiding failures. Use when the done gate fails.
---

# Harness Repair

Treat failing harness as signal, not noise.

## Procedure

1. Identify the exact failing command.
2. Capture a short failure summary, not a full log.
3. Classify failure:
   - implementation bug
   - wrong test
   - stale fixture
   - environment issue
   - missing dependency
   - task contract mismatch
   - North-Star mismatch
4. Fix the smallest root cause.
5. Re-run the focused command.
6. Re-run global checks if the fix touches shared code.
7. Update `docs/LESSONS.md` only if the lesson is reusable.
8. If failure repeats twice with unclear root cause, stop and report.

## Rules

- Do not weaken tests just to pass.
- Do not skip failing commands.
- Do not mark done with failed harness.
- Do not broaden scope without updating the task contract.
- If the harness itself is wrong, create or update a harness task and record the decision.

## Output

```markdown
## Harness Repair Report

Failing command:
Failure summary:
Failure class:
Root cause:
Fix applied:
Re-run result:
Global checks:
Lesson needed: yes | no
Task can proceed to done: yes | no
```
