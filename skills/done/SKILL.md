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
2. Run `python .coderail/coderail.py done --owner-locale zh-CN` for a Chinese
   user; use `--owner-locale en` for English.
3. If it fails, repair the named issue and rerun only when the task remains open.
4. If it succeeds, report its result without manually repeating TASKS, TRACE,
   Inspect, staging, or commit steps.

## Two projections

The successful localized command prints the Owner Receipt: 3-6 sentences about
new capability, evidence boundary, remaining gap, next step, and owner decision.
Do not add task IDs, paths, governance jargon, or unannotated English to it.

Lifecycle state, exact verification, paths, and Git receipts stay in
`docs/CODERAIL_STATUS.md` (Agent Blackboard) and `.coderail/reports/`
(Technical Report). `docs/DELIVERIES.jsonl` stores append-only product delivery
facts but never becomes lifecycle authority.

## Rules

- Do not hide failed verification.
- Do not turn a failed gate into a narrative success.
- Do not create a second completion sequence after `coderail done` succeeds.
- Do not paste the Agent Blackboard or Technical Report into the Owner Receipt.
- Do not edit generated closeout state merely to make the report look cleaner.
