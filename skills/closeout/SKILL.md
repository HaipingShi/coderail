---
name: closeout
description: End a work session cleanly: report what happened, commit safe files, and leave one clear next step for whoever resumes.
---

# closeout

Compatibility guidance for choosing the result passed to the single
`coderail done` completion authority.

## Action

```bash
python .coderail/coderail.py done
```

For a verified partial boundary, use:

```bash
python .coderail/coderail.py done --result stage-complete
```

## Required final packet

- Task result: done, stage-complete, blocked, failed, or deferred.
- Verification: harness/manual result and whether Done Gate passed when marking done.
- Persistence synced: TASKS, TRACE, and any P assets.
- Auto Commit action: committed, skipped, blocked, or failed; include exact staged files, safe-to-stage, do-not-stage, ignored/generated artifacts, and whether `git add .` is unsafe.
- Handoff Trigger Check: H0/H1/H2/H3 and whether HANDOFF was updated.
- Resume anchor: file, task, status, or inspect report a future agent can load.
- Next Executable Step: one command or one task card.

## Rules

- Do not include project-specific examples from another repository.
- Do not stop with only a narrative summary.
- Do not run the legacy `finish` adapter as a second closeout path.
- Do not manually repeat persistence, staging, or commit work after `done`.
- If useful work is not verified, keep the task active and state the next
  validation step instead of manufacturing a checkpoint.
