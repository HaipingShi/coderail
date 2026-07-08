# North Star

Status: provisional
Last reviewed:
Owner:

## Outcome

- 

## Current Bet

- 

## Invariants

- 

## Current Slice

- Milestone:
- Execution Batch:
- Active Task:

## Non-Goals

- 

## Known Unknowns

- 

## Decision Debt

- 

## Coordinate Rule

Every active task must map to this North Star through its G field. If G cannot identify an Outcome, Current Bet, Invariant, or Current Slice, the task is not ready for implementation.

## Stop Triggers

- A task cannot map to the North Star.
- A code change has no task or trace link.
- Handoff introduces a new direction but this file is unchanged.
- A done task lacks verify trace.
- User intent changes the Outcome, Current Bet, or Invariants.

## Drift Signals

- A task has T/S/V but no meaningful G.
- The user request changes G but TASKS or NORTH_STAR is not updated.
- S expands repeatedly without X triggering.
- V passes but P is not synced.
- A high-risk request has no Coordinate Contract Draft.
- A completed task fails the done gate.
- `CODERAIL_STATUS.md` reports blocked state before handoff.
