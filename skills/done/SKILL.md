---
name: done
description: Complete the current task only after the CodeRail Coordinate checks out, harness passes, diff is reviewed, TASKS/P assets are synced, and trace events are written. Use when the agent believes a task is finished.
---

# Done Gate

Never mark done without evidence. The CodeRail Coordinate is the checklist.

## Procedure

1. Re-read the current task and its CodeRail Coordinate in `docs/TASKS.md`.
2. Re-run the task harness (V) from `docs/HARNESS_SPEC.md` or the task itself.
3. Run global checks when relevant.
4. Inspect `git diff` and verify no unrelated files changed (S was obeyed).
5. Confirm the task still maps to `docs/NORTH_STAR.md` (G still holds).
6. Update the task completion fields:
   - Status: `[x]`
   - Completed at
   - Commit, if available
   - Harness result
   - Handoff level
   - Trace
7. Update `docs/DECISIONS.md` only for durable engineering decisions.
8. Update `docs/LESSONS.md` only for reusable failure lessons.
9. Update `docs/ASSETS.md` only if asset state changed.
10. Write trace events: `change` (files modified), `verify` (harness result), and `handoff` if H1/H2/H3.
11. Regenerate `docs/TRACE_INDEX.md`.
12. Run Handoff Trigger Check.
13. Update `docs/HANDOFF.md` only for H1/H2/H3.

## Coordinate gate

Before marking done, every field must check out:

- **G** still holds (the North Star mapping did not drift).
- **T** is complete.
- **S** was obeyed (no forbidden files touched).
- **V** ran and passed (or explicit manual acceptance).
- **X** was not triggered, or was already resolved.
- **P** was synced (at least TASKS and TRACE; plus DECISIONS/LESSONS/ASSETS/HANDOFF as declared).

If **V** did not run, do not mark done. If **P** is not synced, mark the task
`partial` or `needs-persist`, not `done`.

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
North-Star mapping (G):
Harness run (V):
Harness result:
Diff summary:
Files changed (S obeyed): yes | no
P synced (TASKS / TRACE / ...): yes | no
Trace events written: change | verify | handoff
Handoff level: H0 | H1 | H2 | H3
Next recommended action:
```

If harness failed, do not mark done. Use `harness-repair` instead.
