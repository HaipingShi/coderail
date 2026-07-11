# Closeout Gate

Closeout Gate is CodeRail's stop-with-state rule.

Done Gate answers whether a task may be marked done. Closeout Gate answers
whether an agent may stop without leaving the project suspended. When a safe
task-scoped commit can be created, the agent should create it instead of merely
recommending it.

## Required closeout packet

Every substantial final response or execution stop must include:

```text
Closeout State:
- Task result: done | stage-complete | blocked | failed | deferred
- Active Task ID:
- Verification:
- Persistence synced:
- Handoff Trigger Check:
- HANDOFF updated:
- Resume anchor:
- Next executable step:

Auto Commit:
- Eligible:
- Action: committed | skipped | blocked | failed
- Commit:
- Exact files staged:
- Safe to stage:
- Do not stage:
- Ignored/generated artifacts:
- Avoid git add .:
```

## Task result meanings

- `done`: V passed, P synced, trace exists, and Done Gate allows completion.
- `stage-complete`: useful work landed, but acceptance is incomplete or another
  validation step remains. Keep the task active unless a maintainer decides
  otherwise.
- `blocked`: X fired or a required decision/dependency is missing.
- `failed`: the attempted path is known not to work and should not be resumed as
  is.
- `deferred`: work is intentionally paused in favor of another task or batch.

## Next executable step

The next step must be operational, not aspirational.

Good:

```text
Run `python scripts/closeout_check.py --target . --task T-012`.
Create task T-013 for the data inventory runner with S limited to docs/** and tools/**.
```

Bad:

```text
Continue later.
Work on the next task.
Improve the implementation.
```

## Auto commit

Before stopping, classify the worktree and auto-commit safe task-scoped files
when all conditions hold:

1. the task result is `done` or `stage-complete`; for `blocked`, `failed`, or
   `deferred`, the unified `finish` command may commit persistence files only;
2. V/Done Gate requirements are satisfied when claiming `done`;
3. no forbidden file changes are present;
4. safe-to-stage files can be derived from S;
5. git commit is available and identity is configured.

The agent should not stop to ask about commit mechanics when the commit is
task-scoped and reversible.

Classify:

1. files safe to stage for the current task;
2. files that must not be staged;
3. ignored or generated artifacts;
4. whether `git add .` is unsafe;
5. auto-commit action and resulting commit id when created.

If unrelated, ignored, generated, or out-of-scope files are present, do not use
broad staging. Stage only safe task-scoped files and leave unrelated work alone.
CodeRail persistence files (`TASKS`, trace/index, inspect status, and handoff)
may be included by the unified `finish` command even when implementation S is
narrow; unrelated project files remain outside the commit.

If no safe commit can be made, record `blocked`, `failed`, or `skipped` with the
next executable step.

For task-sliced commits, prefer one commit per coherent task or
stage-complete checkpoint. The closeout packet must name exact staged files and
whether `git add .` is forbidden for the current worktree. If work is not done,
the resume anchor must point to the active task, current file, failing command,
or next task card.

## Handoff trigger check

Handoff is event-triggered, but the check is mandatory.

- H0: no `HANDOFF.md` update, but final response must name the resume anchor.
- H1: small delta; update handoff if the next session needs the state.
- H2: rolling snapshot; rewrite `HANDOFF.md` as current state.
- H3: full handoff; use for blocked, risky, cross-session, or new-agent work.

If the task is not done but has useful stage-complete output, write a resume
anchor and next executable step even when HANDOFF remains H0.
