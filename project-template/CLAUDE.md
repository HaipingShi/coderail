# Claude Code Runtime Entry

Follow `AGENTS.md`. The key rules are the North-Star Kernel (K0), the CodeRail
Coordinate (K1), and the Trace Graph (K7): before coding, confirm the task
serves `docs/NORTH_STAR.md`, fill a CodeRail Coordinate (G/T/S/V/X/P), and make
every meaningful action linkable in `docs/TRACELOG.jsonl`.

## Default flow

Use these plugin skills when available:

- `/coderail:align` for vague, high-level, drifting, or multi-step work.
- `/coderail:task-contract` before implementation.
- `/coderail:execute-batch` to proceed through authorized tasks without unnecessary confirmation.
- `/coderail:done` before marking work complete.
- `/coderail:trace` to record key actions; `/coderail:link` to backfill missing edges.
- `/coderail:handoff` only when a handoff trigger is met.
- `/coderail:drift-check` when documents, tasks, code, or user intent appear misaligned.

## Required before coding

Output a North-Star Check and a CodeRail Coordinate:

```text
Outcome:
Intent level:
Current slice:
This task serves:
Invariant to preserve:
What this task must not become:
Drift risk:
Proceed / reframe:

G — Goal:
T — Task:
S — Scope (allowed / forbidden):
V — Verify:
X — Stop:
P — Persist:
```

If the request is L0-L3, make the engineering judgment and task contract before implementation.

## Completion gate

Never mark done until harness has run or manual acceptance has been explicitly
recorded, the CodeRail Coordinate checks out (G/T/V/X/P satisfied), and the
change/verify trace events are written.
