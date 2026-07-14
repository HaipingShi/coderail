# North Star

Status: current
Last reviewed: 2026-07-15
Owner: CodeRail maintainers

## Outcome

- Make CodeRail a reliable repo-local governance rail that agents can execute, verify, close out, and resume without dangling state.

## Current Bet

- A single local launcher and finish boundary will improve rule recall, persistence, safe commits, and next-task continuity more than adding more prompt text.

## Invariants

- Governance decisions remain inspectable in repository files.
- Task scope, verification evidence, and persistence links are explicit.
- Failed or blocked work never masquerades as done.

## Current Slice

- Milestone: M-010 v0.9.0 release readiness
- Execution Batch: align release metadata, notes, install output, and regression evidence
- Active Task: T-004

## Non-Goals

- CodeRail is not a hosted CI service, issue tracker, scheduler, or model runtime.

## Known Unknowns

- Which agent hosts will enforce a hard stop hook without a soft override.

## Decision Debt

- None for this slice.

## Legacy Cutoff

- Enforcement starts at: T-001

## Drive Contract

- Mode: manual
- Next-task mode: recommend
- Terminal condition: all changes in the current slice are verified and committed
- Progress signal: tests pass and closeout state is persisted
- Retry budget: 3
- No-progress limit: 2
- Human gates: changes to public APIs, security, privacy, payment, persistence, or release policy

Continuous Drive is opt-in. `recommend` is the safe default; use `activate` only
when automatic activation of the next dependency-ready task is explicitly authorized.

## Coordinate Rule

Every active task must map to this North Star through its G field.

## Stop Triggers

- A task cannot map to the North Star.
- A code change has no task or trace link.
- Verification fails or a required decision is missing.
- A done task lacks a verify trace or closeout commit.
