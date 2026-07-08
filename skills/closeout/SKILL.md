---
name: closeout
description: Produce deterministic closeout with task result, auto-commit action, handoff check, resume anchor, and next executable step.
---

# closeout

Use at the end of any substantial task, batch boundary, blocked state, or handoff.

## Action

Run available CI/CD checks first:

```bash
python3 scripts/ci_gate.py --target .
```

Run when available:

```bash
python3 scripts/closeout_check.py --target . --task <TASK_ID> --task-result stage-complete --auto-commit
```

Use `--task-result done` only after Done Gate has passed.

## Required final packet

- Task result: done, stage-complete, blocked, failed, or deferred.
- Verification: harness/manual result and whether Done Gate passed when marking done.
- Persistence synced: TASKS, TRACE, and any P assets.
- Auto Commit action: committed, skipped, blocked, or failed; include safe-to-stage, do-not-stage, ignored/generated artifacts, and whether `git add .` is unsafe.
- Handoff Trigger Check: H0/H1/H2/H3 and whether HANDOFF was updated.
- Resume anchor: file, task, status, or inspect report a future agent can load.
- Next Executable Step: one command or one task card.

## Rules

- Do not include project-specific examples from another repository.
- Do not stop with only a narrative summary.
- Do not ask about commit mechanics when a safe task-scoped commit can be made automatically.
- Do not use broad staging when unrelated, ignored, generated, forbidden, or out-of-scope files exist.
- If useful work is stage-complete but not verified, keep the task active and make the next validation step explicit.
