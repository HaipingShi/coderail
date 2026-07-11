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

## Legacy Cutoff

- Enforcement starts at:

Leave this blank for a new project. When adopting CodeRail into a repository
with historical tasks, set it to the first post-cutover task ID as it appears in
`docs/TASKS.md`. Inspect keeps earlier verification gaps visible as historical
debt without treating them as current blockers.

## Drive Contract

- Mode: manual | continuous
- Next-task mode: recommend
- Terminal condition:
- Progress signal:
- Retry budget: 3
- No-progress limit: 2
- Human gates:

Continuous Drive is authorized only when the terminal condition and progress
signal are explicit. Goal persistence never expands scope or permissions.
`recommend` is the safe default; use `activate` only when the project explicitly
authorizes automatic activation of the next dependency-ready autonomous task.

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
