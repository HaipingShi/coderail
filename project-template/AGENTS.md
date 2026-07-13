# CodeRail

This project uses CodeRail to keep AI-assisted work on track. The rules below
are written in plain language. You do not need to learn any special terminology.

## The three commands

There is one entry point with three everyday commands:

```bash
python .coderail/coderail.py start "what you want to do"   # begin a task
python .coderail/coderail.py check                         # am I on track?
python .coderail/coderail.py done                          # finish safely
```

Everything else (verification gates, history tracing, safe commits, handoff
notes) happens automatically behind these three commands.

## Before you write any code

1. Read `docs/NORTH_STAR.md` — the project goal in one page. If it is empty,
   ask the user what they are building and write it down first.
2. Read `docs/TASKS.md` — what is in flight right now.
3. Run `git status` — know what is already changed.
4. If there is no active task for what you are about to do, run `start`.

## While you work

- Only touch files the current task said it would touch. If you need to go
  outside that list, say so and update the task — do not do it silently.
- If the request is vague, big, or risky (payments, auth, data deletion,
  schema changes), write down what you plan to do in `docs/CONTRACTS.md` and
  get a yes before coding.
- For bug fixes and logic-heavy code, write a failing test first, then make
  it pass. Record that in the task.
- Record important decisions in `docs/DECISIONS.md` (one line is enough:
  what you decided and why).

## Before you say "done"

Never declare a task finished from memory. Run:

```bash
python .coderail/coderail.py done
```

It verifies, in order: tests/checks pass (or you explicitly recorded a manual
check), changes stayed inside the task's file list, the docs are updated, and
then it commits only the safe, task-related files. If it says the task is not
finished, fix what it points out — do not talk your way around it.

If you finished part of the work but not all of it, use
`done --result stage-complete` so the next session knows where to pick up.

## Honesty rules (non-negotiable)

- Do not claim tests passed if you did not run them.
- Do not mark a task done if the finish command failed.
- Do not quietly expand a task into unrelated files.
- Do not use `git add .` — the finish command stages only safe files.

## When you come back to a project

If you are resuming after a break, a crash, or someone else's session, read
`docs/HANDOFF.md` and `docs/CODERAIL_STATUS.md` first, or regenerate the
status with `python .coderail/coderail.py inspect`.

## Advanced

Power users and long-running autonomous sessions can use the advanced
commands (`doctor`, `drive`, `inspect`, `trace`, `blueprint`, `finish`, ...).
Run `python .coderail/coderail.py --help` to list them. They are optional;
the three everyday commands cover normal work.
