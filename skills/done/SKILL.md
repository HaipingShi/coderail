---
name: done
description: Finish a task only after running the done gate, syncing P, writing trace, and deciding handoff level.
---

# done

Run the completion workflow. This skill wraps verification-before-complete.

## Required order

1. Run the task harness or record explicit manual acceptance.
2. Inspect `git diff` and confirm changes stay inside S.
3. Run `/coderail:done-gate` or `scripts/done_gate.py`.
4. Update `docs/TASKS.md` only after the gate passes.
5. Write change and verify trace events.
6. Regenerate `docs/TRACE_INDEX.md`.
7. Refresh `docs/CODERAIL_STATUS.md` with `/coderail:inspect` when resuming or handing off.
8. Run Handoff Trigger Check; update `docs/HANDOFF.md` only for H1/H2/H3.

## Rules

- Do not hide failed verification.
- Do not mark done when P is unsynced.
- Do not turn a failed gate into a narrative success.
