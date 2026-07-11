---
name: done
description: Finish or close out a task only after done gate, P sync, trace, auto-commit action, and deterministic next step.
---

# done

Run the completion workflow. This skill wraps verification-before-complete and closeout state.

## Required order

1. Run TDD Gate when required.
2. Run the task harness or record explicit manual acceptance.
3. Inspect `git diff` and confirm changes stay inside S.
4. Run `/coderail:done-gate` or `python .coderail/coderail.py done`.
5. Update `docs/TASKS.md` only after the gate passes.
6. Write change and verify trace events.
7. Regenerate `docs/TRACE_INDEX.md`.
8. Refresh `docs/CODERAIL_STATUS.md` with `/coderail:inspect` when resuming or handing off.
9. Run Handoff Trigger Check; update `docs/HANDOFF.md` only for H1/H2/H3.
10. Run CI Gate when available.
11. Inspect `git status`/`git diff` and auto-commit safe task-scoped files when possible.
12. End with one Next Executable Step.

## Closeout packet

Every substantial final response must include:

- Task result: done, stage-complete, blocked, failed, or deferred.
- TDD state when required: Red, Green, Refactor, regression, and CI evidence.
- Verification and persistence state.
- Auto Commit action: committed, skipped, blocked, or failed; include safe-to-stage, do-not-stage, ignored/generated artifacts, and whether `git add .` is unsafe.
- Handoff Trigger Check and whether HANDOFF was updated.
- Resume anchor.
- Next Executable Step: one command or one task card.

## Rules

- Do not hide failed verification.
- Do not mark done when P is unsynced.
- Do not turn a failed gate into a narrative success.
- Do not stop after stage-complete work without a resume anchor and next executable step.
