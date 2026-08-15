---
name: closeout
description: End a work session cleanly: report what happened, commit safe files, and leave one clear next step for whoever resumes. Use when running `coderail done` or writing the Owner Receipt.
---

# closeout

Compatibility guidance for choosing the result passed to the single
`coderail done` completion authority.

## Action

```bash
python .coderail/coderail.py done --owner-locale zh-CN
```

For a verified partial boundary, use:

```bash
python .coderail/coderail.py done --result stage-complete --owner-locale zh-CN
```

## Owner channel

On success, return only the generated 3-6 sentence Owner Receipt. Match the
user's language. In Chinese, necessary English terms require a Chinese note;
task IDs, paths, lifecycle labels, commit receipts, and internal gate names do
not belong in this channel unless the owner asks.

Always choose `zh-CN` or `en` from the user's language preference. Never omit
the locale or recreate the retired fallback report.

## Agent channel

Use the Agent Blackboard and Technical Report for task result, exact checks,
safe files, Git receipt, handoff state, recovery anchor, and next executable
step. Do not make the blackboard a new lifecycle authority.

## Rules

- Do not include project-specific examples from another repository.
- Do not stop with only a narrative summary.
- Do not expand the Owner Receipt into the old seven-section technical packet.
- Do not run the legacy `finish` adapter as a second closeout path.
- Do not manually repeat persistence, staging, or commit work after `done`.
- If useful work is not verified, keep the task active and state the next
  validation step instead of manufacturing a checkpoint.
