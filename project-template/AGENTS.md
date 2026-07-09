# CodeRail Runtime Entry

This repository uses CodeRail. Keep this file short; full schemas live in `references/`.

## Governance layers

- **L1 kernel**: CodeRail rules and entry files (`AGENTS.md`, `CLAUDE.md`), package files, plugin manifests, skills, scripts, references. Long-lived rails; do not modify unless the user explicitly asks to upgrade CodeRail.
- **L2 project state**: `docs/NORTH_STAR.md`, `docs/TASKS.md`, `docs/CONTRACTS.md`, `docs/BLUEPRINTS.md`, `docs/HANDOFF.md`, `docs/TRACELOG.jsonl`, `docs/HARNESS_SPEC.md`. Edit through CodeRail flow. `TRACELOG.jsonl` is append-only.
- **L3 implementation**: business code and tests. Edit only inside the current S field.

## K0 North-Star Kernel

Before implementation, read or create `docs/NORTH_STAR.md`.

Every task must name the outcome, intent level, current slice, invariant, non-goal, and drift signal.

If the request is L0-L3, do not jump to code. Produce an engineering judgment and a contract draft first.

## K1 CodeRail Coordinate

Every non-trivial task must choose a rail and have a matching Coordinate.

- **Full Rail**: code, schema, dependencies, data writes, runners, pipelines, external interfaces, migrations, or release work. Use full G/T/S/V/X/P, executable verification, trace, done gate, and closeout.
- **Light Rail**: theory, product positioning, design principles, philosophy boundaries, terminology, ADRs, and document drafts. Use a light coordinate: goal, boundary, persistence location, acceptance/trace or manual acceptance, and next step. Do not force an implementation/test loop when there is no code path.

- **G — Goal**: which North Star outcome this serves.
- **T — Task**: the exact task to complete.
- **S — Scope**: allowed and forbidden files/assets.
- **V — Verify**: harness, test, build, or manual acceptance.
- **X — Stop**: conditions that require stopping or escalating.
- **P — Persist**: project assets to update after the action.

If any field is missing, stop and run `/align`, `/contract-draft`, or `/task-contract`.

## TDD Gate

Use Red-Green-Refactor for bugs, regressions, parsers, validators, domain logic, APIs, shared utilities, and risky refactors. In `V`, set TDD mode to required, optional, or waived; required tasks need Red and Green evidence before done.

## Contract Draft Gate

For vague, high-risk, cross-module, or mid-session requirements, create a `Coordinate Contract Draft` before coding. Use `docs/CONTRACTS.md` or `/coderail:contract-draft`.

Do not code from vague intent. Do not silently fold a side request into the current task.

## Verification-before-complete

Before marking done, run `/coderail:done-gate` or `scripts/done_gate.py`.

No done without the rail-appropriate evidence:

1. V passed or explicit manual acceptance.
2. S respected.
3. P synced. Full Rail requires TASKS and TRACE; Light Rail requires TASKS plus trace, decision backlink, or explicit manual acceptance.
4. A verify trace event or fresh verification/manual evidence.
5. Handoff Trigger Check performed.

## Runtime State Inspect

Use `/coderail:inspect` or `scripts/inspect_state.py` before resuming, before handoff, after task jumps, or when the project feels hard to understand. It writes `docs/CODERAIL_STATUS.md`.

## Blueprint Gate

Use `docs/BLUEPRINTS.md` and `scripts/blueprint_check.py` when architecture, data, deployment, UI flow, or lifecycle complexity appears. Required diagrams must be current before high-complexity work is treated as done.

## K7 Trace Graph

Every meaningful action must be linkable:

1. source or intent
2. North Star or task
3. modified files/assets
4. verification evidence
5. persisted state

If an action cannot be linked, stop and run `/trace` or `/link`.

## Load order

Always read:

1. `docs/NORTH_STAR.md`
2. `docs/TASKS.md`
3. `docs/HARNESS_SPEC.md`
4. `git status`

Read when needed:

- `docs/CONTRACTS.md`: draft-gated or high-risk work.
- `docs/CODERAIL_STATUS.md`: resuming, inspecting, or handing off.
- `docs/BLUEPRINTS.md`: architecture, data, deployment, UI flow, or lifecycle complexity.
- `docs/HANDOFF.md`: new session, H2/H3 handoff, blocked task.
- `docs/TRACELOG.jsonl` / `docs/TRACE_INDEX.md`: history, trace gaps, why code exists.
- `docs/DECISIONS.md`, `docs/LESSONS.md`, `docs/ASSETS.md`: durable decisions, repeated failures, asset changes.

## Intent levels

- L0 Outcome
- L1 Product / Domain
- L2 Architecture
- L3 Technical Design
- L4 Task Plan
- L5 Implementation

Do not collapse L0-L3 requests into L5 patches before framing the judgment.

## Non-negotiable rules

- Do not mark done without the done gate.
- Do not modify forbidden files without approval and trace.
- Do not treat raw material or working notes as permanent assets.
- Do not hide failed tests or fake harness results.
- Prefer permissions/hooks/CI over prompt-only rules.

## Execution rhythm

Plan finely. Execute authorized batches until done, stage-complete, blocked, failed, or drift is detected. Fine-grained tasks are for traceability, not permission to stop after every low-risk internal step.

Pause only for decision-grade blockers: missing goal, forbidden scope, product/security/payment/privacy/API/schema/persistence changes, unclear repeated harness failure, or docs/code contradiction. Run non-decision gates yourself.

## Closeout

Before any substantial final response or stop:

1. State task result: done, stage-complete, blocked, failed, or deferred.
2. Run TDD Gate when required, CI Gate when available, and done gate only when marking done.
3. Inspect `git diff/status`; classify safe-to-stage, do-not-stage, ignored/generated.
4. Auto-commit exact task-scoped files when possible; never use `git add .` when unsafe.
5. Run Handoff Trigger Check: H0/H1/H2/H3; update HANDOFF only for H1/H2/H3.
6. State one Next Executable Step: a command or the next task card.
