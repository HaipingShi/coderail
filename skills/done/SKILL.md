---
name: done
description: Finish a task the safe way: verify it, keep changes in scope, sync the docs, commit safe files, and state the next step. Run this instead of declaring done from memory.
---

# done

`coderail done` is the single completion authority. Run it once; it owns
verification, scope classification, task state, trace, progress, final Inspect,
and the exact task-scoped commit.

## Required order

1. Confirm the implementation and its declared verification are ready.
2. Run `python .coderail/coderail.py done`.
3. If it fails, repair the named issue and rerun only when the task remains open.
4. If it succeeds, report its result without manually repeating TASKS, TRACE,
   Inspect, staging, or commit steps.

## Closeout packet

Translate the command result into plain language: what changed, how it was
verified, whether it committed, and the one next step or decision.

## Rules

- Do not hide failed verification.
- Do not turn a failed gate into a narrative success.
- Do not create a second completion sequence after `coderail done` succeeds.
- Do not edit generated closeout state merely to make the report look cleaner.
