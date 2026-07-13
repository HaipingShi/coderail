# CodeRail (this repository)

This is the CodeRail tool itself, and it is governed by its own rules.
The rules are in plain language; no special terminology is required.

## The three commands

```bash
python3 scripts/coderail.py start "what you want to do"   # begin a task
python3 scripts/coderail.py check                         # am I on track?
python3 scripts/coderail.py done                          # finish safely
```

Verification gates, history tracing, safe commits, and handoff notes all run
automatically behind these three commands.

## What lives where

- `scripts/` and `skills/` — the tool itself. Change only when the task is
  about improving CodeRail.
- `docs/` — this repo's own project state (goal, tasks, decisions, history).
  Update it through the commands above, not by hand-editing history files.
  `docs/TRACELOG.jsonl` is append-only.
- `project-template/` — what gets installed into user repositories. Keep it
  in plain language and keep `AGENTS.md` under 130 lines (tests enforce this).
- `references/` — deep documentation for power users. Optional reading.

## Before you write any code

1. Read `docs/NORTH_STAR.md` — the project goal.
2. Read `docs/TASKS.md` — what is in flight.
3. Run `git status`.
4. If there is no active task for what you are about to do, run `start`.

## While you work

- Only touch files the current task said it would touch. Need more? Say so
  and update the task first.
- Vague, big, or risky request? Write the plan in `docs/CONTRACTS.md` and get
  a yes before coding.
- Bug fixes and logic-heavy code: failing test first, then make it pass.
- Record important decisions in `docs/DECISIONS.md`.

## Before you say "done"

Run `python3 scripts/coderail.py done`. It verifies tests pass (or a manual
check was recorded), changes stayed in scope, docs are synced, then commits
only safe task-related files. If it says not finished, fix what it points
out — do not talk your way around it. Partial work: `done --result
stage-complete`.

## Honesty rules (non-negotiable)

- Do not claim tests passed if you did not run them.
- Do not mark a task done if the finish command failed.
- Do not quietly expand a task into unrelated files.
- Do not use `git add .`.

## Resuming

Read `docs/HANDOFF.md` and `docs/CODERAIL_STATUS.md`, or regenerate with
`python3 scripts/coderail.py inspect`.

## Advanced

Power users and long-running autonomous sessions can use the advanced
commands (`doctor`, `drive`, `inspect`, `trace`, `blueprint`, `finish`, ...).
Run `python3 scripts/coderail.py --help` to list them. Deep schemas live in
`references/`. The three everyday commands cover normal work.
