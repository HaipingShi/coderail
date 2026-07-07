# CodeRail Coordinate Reference

The CodeRail Coordinate compresses the runtime state of an AI coding task into
six fields. It is not a theory chapter. It is the minimum coordinate every
non-trivial task must fill in before implementation.

It replaces several scattered rules (North-Star Link, Allowed/Forbidden Files,
Harness, Stop Triggers, Persisted Assets) with one block the agent fills in
once per task.

## Purpose

Before CodeRail, a task pulled rules from many places: the North-Star Link came
from `align`, the Allowed/Forbidden Files came from `task-contract`, the Harness
came from `HARNESS_SPEC`, the Stop Triggers came from the North Star, and the
Persisted Assets came from `done`. The agent read them once and then forgot. The
CodeRail Coordinate re-reads them into one shape the agent re-checks at every
gate.

## The six fields

- **G — Goal**: which North Star outcome this task serves.
- **T — Task**: the exact task to complete, with a clear boundary.
- **S — Scope**: files and assets allowed and forbidden.
- **V — Verify**: the harness, test, build, or manual acceptance that proves done.
- **X — Stop**: conditions that require stopping or escalating.
- **P — Persist**: which project assets must be updated after the action
  (`TASKS`, `HANDOFF`, `DECISIONS`, `LESSONS`, `ASSETS`, `TRACE`).

## Minimal coordinate template

```markdown
## CodeRail Coordinate

G — Goal:
- 

T — Task:
- 

S — Scope:
- Allowed:
- Forbidden:

V — Verify:
- 

X — Stop:
- 

P — Persist:
- TASKS:
- HANDOFF:
- DECISIONS:
- LESSONS:
- ASSETS:
- TRACE:
```

## How skills use it

- `align` drafts the coordinate after the North-Star Check. If G is unclear, it
  writes a provisional G and flags it for confirmation.
- `task-contract` finalizes G/T/S/V/X/P and writes the block into `TASKS.md`.
- `execute-batch` lists the coordinate before working and obeys S and X.
- `done` checks that G still holds, T is complete, S was obeyed, V passed, X was
  not triggered, and P was synced. It refuses done without V or with P unsynced.
- `handoff` copies only the current coordinate into the Coordinate Summary.
- `trace` embeds the coordinate summary (G/T/V/P) into trace events.
- `link` backfills missing coordinate edges (G→North Star, T→TASKS, S→files,
  V→evidence, P→docs).
- `drift-check` detects coordinate drift (G changed but TASKS unchanged, S
  expanded but X not triggered, V passed but P unsynced, etc.).
- `doctor` reports coordinate coverage, missing G/V/P, and scope violations.
- `coordinate_check.py` enforces the shape for every active/doing/done task.
- `asset-boundary` treats P as the asset-sink checklist.

## Example

User request: "I want to add CSV import to the project."

```markdown
## CodeRail Coordinate

G — Goal:
- Enable local data import for the current MVP.

T — Task:
- Add CSV parser and validation entry point.

S — Scope:
- Allowed:
  - src/import/**
  - tests/import/**
  - docs/TASKS.md
  - docs/HARNESS_SPEC.md
- Forbidden:
  - auth/**
  - database migrations
  - payment / permission logic

V — Verify:
- pytest tests/import
- or equivalent project harness

X — Stop:
- Need schema change
- Need new dependency
- Existing harness fails twice with unclear root cause
- User intent expands to a full data management system

P — Persist:
- TASKS: add/update T-XXX
- HARNESS_SPEC: add import test command
- HANDOFF: update only if H1/H2/H3 trigger
- DECISIONS: only if parser boundary or dependency decision is durable
- LESSONS: only if a reusable failure occurs
- ASSETS: only if a raw sample CSV becomes a test fixture
- TRACE: add task / change / verify events
```

## Anti-patterns

- **G written as "complete the task"** with no North Star mapping. G must name an
  Outcome, Current Bet, Invariant, or Current Slice.
- **T written as "optimize the system"** with no completion boundary. T must be
  concrete enough to verify.
- **S only lists allowed, never forbidden.** Forbidden is what stops scope creep.
- **V written as "looks fine"** with no harness and no manual acceptance. Without
  V, the task cannot be marked done.
- **X left empty.** An empty Stop field means the agent has no escalation path.
- **P only lists TASKS.** Most tasks should also carry TRACE; durable work also
  carries DECISIONS, LESSONS, or ASSETS.
- **User adds a mid-flight requirement and the agent implements it without
  updating G/T/X/P.** New intent must re-enter through `align`.

## Relationship to North Star

Every G must identify an Outcome, Current Bet, Invariant, or Current Slice from
`docs/NORTH_STAR.md`. If a task's G cannot identify one of those, the task is not
ready for implementation and must go back through `align`.

## Relationship to Trace Graph

Trace events of type `change`, `verify`, and `handoff` should embed a coordinate
summary so the trace graph can answer "which task, which goal, which verify,
which persist." See [`TRACE_GRAPH.md`](TRACE_GRAPH.md) for the embedded shape.
Old events are not required to carry a coordinate; new ones should.
