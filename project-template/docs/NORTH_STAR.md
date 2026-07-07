# North Star

Status: provisional
Last reviewed:
Owner:

## 1. Outcome

The most important current project result:

- 

## 2. User / Operator Intent

The capability, efficiency, or result the user actually wants:

- 

## 3. Current Bet

The current engineering approach for this phase:

- 

## 4. Non-Goals

Explicitly out of scope for the current phase:

- 

## 5. Invariants

Constraints every task must preserve:

- 
- 
- 

## 6. Current Slice

- Milestone:
- Execution Batch:
- Active Task:

## 6b. Coordinate Rule

Every active task must map to this North Star through its **G** field.

If a task's G field cannot identify an Outcome, Current Bet, Invariant, or
Current Slice, the task is not ready for implementation. Send it back to
`/align`.

## 7. Known Unknowns

Unclear points that do not block current work:

- 

## 8. Decision Debt

Open judgments that must be revisited:

- 

## 9. Stop Triggers

Stop local implementation and realign if:

- The user goal changes.
- A new task cannot map to Outcome, Current Bet, Invariants, or Current Slice.
- A task needs to change Non-Goals.
- A task must break an Invariant.
- Harness fails twice and root cause is unclear.
- Documents and code disagree about target behavior.
- A task adds an unrecorded product assumption.
- The agent wants a broad refactor but cannot explain which Outcome it serves.
- A task cannot be mapped to a North Star (no G).
- A code change has no task link (no T in the CodeRail Coordinate).
- A handoff introduces a new direction but this file is not updated.
- A done task has no verify trace.

## 10. Drift Signals

Likely drift:

- The last three tasks do not share a common Outcome.
- HANDOFF mentions a new direction but this file is unchanged.
- TASKS contains work that cannot be mapped to Outcome or Current Slice.
- Code adds a capability that TASKS and this file do not mention.
- The user repeatedly says the work is not what they meant.
- A task has T/S/V but no meaningful G.
- A user request changes G but TASKS.md / this file is not updated.
- A task repeatedly changes S without updating X.
- A completed task has V but no P.
