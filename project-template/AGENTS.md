# CodeRail Runtime Entry

This repository uses CodeRail. Keep this file short; full schemas live in `references/`.

## Governance layers

- **L1 kernel**: CodeRail rules and entry files (`AGENTS.md`, `CLAUDE.md`), package files, plugin manifests, skills, scripts, references. Long-lived rails; do not modify unless the user explicitly asks to upgrade CodeRail.
- **L2 project state**: `docs/NORTH_STAR.md`, `docs/TASKS.md`, `docs/CONTRACTS.md`, `docs/BLUEPRINTS.md`, `docs/HANDOFF.md`, `docs/TRACELOG.jsonl`, `docs/HARNESS_SPEC.md`. Edit through CodeRail flow. `TRACELOG.jsonl` is append-only.
- **L3 implementation**: business code and tests. Edit only inside the current S field.

## K0 North-Star Kernel

Before implementation, read or create `docs/NORTH_STAR.md`.

Every task must answer:

1. What outcome does this serve?
2. What user intent level is this request?
3. What current slice does this belong to?
4. Which invariant must remain true?
5. What should this task not become?
6. What would indicate drift?

If the request is L0-L3, do not jump to code. Produce an engineering judgment and a contract draft first.

## K1 CodeRail Coordinate

Every non-trivial task must have a CodeRail Coordinate:

- **G — Goal**: which North Star outcome this serves.
- **T — Task**: the exact task to complete.
- **S — Scope**: allowed and forbidden files/assets.
- **V — Verify**: harness, test, build, or manual acceptance.
- **X — Stop**: conditions that require stopping or escalating.
- **P — Persist**: project assets to update after the action.

If any field is missing, stop and run `/align`, `/contract-draft`, or `/task-contract`.

## Contract Draft Gate

For vague, high-risk, cross-module, or mid-session requirements, create a `Coordinate Contract Draft` before coding. Use `docs/CONTRACTS.md` or `/coderail:contract-draft`.

Do not code from vague intent. Do not silently fold a side request into the current task.

## Verification-before-complete

Before marking done, run `/coderail:done-gate` or `scripts/done_gate.py`.

No done without:

1. V passed or explicit manual acceptance.
2. S respected.
3. P synced, at least TASKS and TRACE.
4. A verify trace event or fresh verification evidence.
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

Plan finely. Execute authorized batches until done, blocked, failed, or drift is detected. Do not ask for confirmation at every low-risk internal step.

Pause when the task cannot map to North Star, needs forbidden scope, changes product/security/payment/privacy/API/schema/persistence, harness fails twice without root cause, or docs and code disagree.

## Completion

1. Run V.
2. Inspect `git diff`.
3. Run done gate.
4. Update TASKS and required P assets.
5. Write change/verify trace events.
6. Regenerate TRACE_INDEX.
7. Inspect state if resuming or handing off.
8. Update HANDOFF only for H1/H2/H3.
