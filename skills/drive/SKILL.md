---
name: drive
description: For long-running autonomous work: at each checkpoint, decide deterministically whether to continue, repair, advance, or stop.
---

# Drive

Read `references/DRIVE_LOOP.md`, then read `AGENTS.md`, `docs/NORTH_STAR.md`,
`docs/TASKS.md`, `docs/HARNESS_SPEC.md`, and `docs/CODERAIL_STATUS.md`.

## Loop

1. Work only on the active task or a dependency-ready task marked `Autonomy: allowed`.
2. Stay inside G and S; Goal persistence does not grant new authority.
3. Run the declared progress/task harness at each meaningful checkpoint.
4. Run `python .coderail/coderail.py drive` with fresh harness, retry,
   no-progress, changed-file, and decision signals when applicable. The command
   reads current Git changes by default. In a pre-existing dirty multi-agent
   worktree, pass the exact task delta with `--changed-files`; never use that
   override to hide an out-of-scope change.
5. Follow exactly one returned state:
   - `CONTINUE`: execute the named next action.
   - `REPAIR`: repair or diagnose inside S and rerun the harness.
   - `ADVANCE`: activate the named ready task and start its first checkpoint.
   - `REVIEW_DIRECTION`: run direction review before implementation continues.
   - `BLOCKED_DECISION`: request only the named missing authority.
   - `COMPLETE`: run done and closeout checks, then finish the durable goal.
   - `EXHAUSTED`: persist failure evidence and stop for revised authority.

Do not return control merely because a low-risk step or stage-complete checkpoint
finished. Under Continuous Drive, only review or terminal states may stop.

## Evidence

- Keep progress updates compact: checkpoint, evidence, decision, next action.
- Persist durable state in project docs and TRACE, not chat memory.
- Never claim progress without a fresh harness or explicit manual evidence.
- Never invent a terminal condition, progress signal, task, or permission.
