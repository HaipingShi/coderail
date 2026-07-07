# Kernel Reference

The CodeRail Kernel is eight invariants. K0 anchors direction; K1 compresses a
task's runtime state into one coordinate; K2-K6 bound, verify, and continue the
work; K7 indexes it so the next agent can follow.

## K0 North-Star Kernel

Every coding action must map to the current Outcome, Current Bet, Invariants, or
Current Slice in `docs/NORTH_STAR.md`.

K0 is mandatory because users often begin with incomplete plans and develop
through exploration. The agent must not only follow the local conversation. It
must repeatedly look up at the persistent project direction.

## K1 CodeRail Coordinate

Every non-trivial task must carry a CodeRail Coordinate before implementation:
**G**oal, **T**ask, **S**cope, **V**erify, **X** (Stop), **P**ersist.

The coordinate compresses the previously scattered North-Star Link, Allowed/
Forbidden Files, Harness, Stop Triggers, and Persisted Assets into one block the
agent re-checks at every gate. Full text: [`CODERAIL_COORDINATE.md`](CODERAIL_COORDINATE.md).

## K2 Task Contract

Every task must have a task ID, North-Star Link, acceptance, dependencies, and
completion record. Allowed/forbidden files, harness, and stop triggers live
inside the CodeRail Coordinate (S/V/X) to avoid duplication.

## K3 Harness Gate

No task is done until the harness passes or manual acceptance is explicitly
recorded.

## K4 Tool-Native Enforcement

Use permissions, hooks, CI, branch protection, pre-commit, and review gates when
possible. Prompt rules are fallback.

## K5 Handoff / Continuation

Handoff is event-triggered and short. It carries a Coordinate Summary, not a
history log.

## K6 Asset Boundary

Raw material, working notes, candidates, permanent project assets, generated
artifacts, and release artifacts must remain distinct.

## K7 Trace Graph Kernel

No action without a trace link. Every meaningful development action records its
source, target, modification, validation, and persistence location in
`docs/TRACELOG.jsonl`. Full text: [`TRACE_GRAPH.md`](TRACE_GRAPH.md).

## Renumbering note (v0.4.0)

Before v0.4.0 the kernel was K0–K6 with "K1 Task Contract" and "K2 Execution
Rhythm" as separate rows. In v0.4.0 the Task Contract moved to K2 and the
Execution Rhythm was absorbed into the CodeRail Coordinate (G/T/X) and the
`execute-batch` skill. K7 Trace Graph was added.
