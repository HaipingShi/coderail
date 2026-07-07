---
name: harness-repair
description: Repair failing lint, typecheck, test, build, CI, migration dry-run, or manual acceptance loops without hiding failures. Binds failures to the CodeRail Coordinate V and P fields and writes trace events. Use when the done gate fails.
---

# Harness Repair

Treat failing harness as signal, not noise. Failures belong to the coordinate's
**V** field; reusable lessons belong to **P → LESSONS**; the repair result
belongs to **V** and to the trace log.

## Procedure

1. Identify the exact failing command (this is a V entry).
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
5. Re-run the focused command (V).
6. Re-run global checks if the fix touches shared code.
7. Update `docs/LESSONS.md` only if the lesson is reusable (P → LESSONS).
8. Write trace events:
   - `verify` with `harness_result: failed` for the original failure (command + summary + evidence location only).
   - `change` for the fix (files modified).
   - `verify` with `harness_result: passed` after the re-run.
   - `lesson` only if the failure is reusable.
9. If failure repeats twice with unclear root cause, stop and report (X trigger).

## Rules

- Do not weaken tests just to pass.
- Do not skip failing commands.
- Do not mark done with failed harness.
- Do not broaden scope (S) without updating the task contract.
- Do not record full test output in trace — only the command, result, summary,
  and where the evidence lives.
- If the harness itself is wrong, create or update a harness task and record
  the decision.

## Output

```markdown
## Harness Repair Report

Failing command (V):
Failure summary:
Failure class:
Root cause:
Fix applied (files in S):
Re-run result (V):
Global checks:
Lesson needed (P → LESSONS): yes | no
Trace events: verify(failed) | change | verify(passed) | lesson
Task can proceed to done: yes | no
```
