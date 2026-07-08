---
name: inspect
description: Inspect CodeRail runtime state before resuming, handing off, or when the project feels hard to understand.
---

# Inspect

Use this skill to show the current project state, not to write business code.

## Read

- `docs/NORTH_STAR.md`
- `docs/TASKS.md`
- `docs/CONTRACTS.md`
- `docs/TRACELOG.jsonl`
- `docs/TRACE_INDEX.md`
- `docs/HANDOFF.md`
- `git status`

## Action

Run:

```bash
python3 scripts/inspect_state.py --target . --write
```

or, if scripts are not available, manually produce the same sections:

- Current North Star
- Active Coordinate
- Active Tasks
- Draft Contracts
- Verification Gaps
- Trace Gaps
- Handoff State
- Recommended Next Action
- Auto Commit

## Rules

- `docs/CODERAIL_STATUS.md` is a generated status surface.
- Do not treat inspect output as a new source of truth; it summarizes existing project files.
- If inspect finds verification gaps, run `/coderail:done-gate` before marking done.
- If inspect finds orphan tasks or trace gaps, run `/coderail:link` or `/coderail:trace`.
