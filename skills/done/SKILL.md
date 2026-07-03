---
name: done
description: Complete the current task only after harness, diff review, task update, and handoff trigger check. Use when the agent believes a task is finished.
---

# Done Gate

Never mark done without evidence.

## Procedure

1. Re-read the current task in `docs/TASKS.md`.
2. Re-run the task harness from `docs/HARNESS_SPEC.md` or the task itself.
3. Run global checks when relevant.
4. Inspect `git diff` and verify no unrelated files changed.
5. Confirm the task still maps to `docs/NORTH_STAR.md`.
6. Update the task completion fields:
   - Status: `[x]`
   - Completed at
   - Commit, if available
   - Harness result
   - Handoff level
7. Update `docs/DECISIONS.md` only for durable engineering decisions.
8. Update `docs/LESSONS.md` only for reusable failure lessons.
9. Update `docs/ASSETS.md` only if asset state changed.
10. Run Handoff Trigger Check.
11. Update `docs/HANDOFF.md` only for H1/H2/H3.

## Validation hierarchy

1. Executable harness: strongest.
2. Static acceptance: strong when explicit.
3. Tool-native enforcement: strong when configured.
4. Human review: required for high-risk changes.
5. Agent critical check: soft gate only.

## Completion report

Return:

```markdown
## Completion Report

Task:
Status:
North-Star mapping:
Harness run:
Harness result:
Diff summary:
Files changed:
Decisions updated: yes | no
Lessons updated: yes | no
Assets updated: yes | no
Handoff level: H0 | H1 | H2 | H3
Next recommended action:
```

If harness failed, do not mark done. Use `harness-repair` instead.
