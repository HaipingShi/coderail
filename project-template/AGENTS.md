# Agent Coding Runtime Entry

This repository uses CodeRail.

## K0 North-Star Kernel

Before any implementation, read or create `docs/NORTH_STAR.md`.

Every task must pass the North-Star Check:

1. What outcome does this serve?
2. What user intent level is this request?
3. What current slice does this belong to?
4. Which invariant must remain true?
5. What should this task not become?
6. What would indicate drift?

If `docs/NORTH_STAR.md` does not exist, create a provisional one before coding.
If the user request is L0-L3, do not implement directly. First produce an engineering judgment and a task contract.
If a task cannot be mapped to the North Star, stop and run alignment before editing code.

## Load order

Always read:

1. `docs/NORTH_STAR.md`
2. `docs/TASKS.md`
3. `docs/HARNESS_SPEC.md`
4. `git status`

Read when needed:

- `docs/HANDOFF.md`: new session, H2/H3 handoff, resumed work, blocked task.
- `docs/DECISIONS.md`: dependency, architecture, API, data model, security, build system changes.
- `docs/LESSONS.md`: repeated error, failed harness, related module failure.
- `docs/ASSETS.md`: raw material, generated documents, exported files, intermediate analysis.
- `docs/RUNLOG.md`: only when detailed execution history is needed.

## Intent levels

- L0 Outcome: final result or business/user outcome.
- L1 Product / Domain: user flows, domain objects, behavior boundaries.
- L2 Architecture: modules, state ownership, runtime boundaries, dependency direction.
- L3 Technical Design: API, schema, error model, directory structure, technical choices.
- L4 Task Plan: task ID, acceptance, allowed files, forbidden files, harness.
- L5 Implementation: code, tests, scripts, config, migrations.

Do not collapse L0-L3 requests into L5 patches before framing the engineering judgment.

## Non-negotiable rules

- Do not mark a task done without running the harness or recording manual acceptance.
- Do not modify forbidden files without a divergence note and user approval when risk is high.
- Do not treat raw material or working notes as permanent project assets.
- Do not perform broad refactors outside the task contract.
- Do not hide failed tests.
- Do not fake harness results.
- Prefer tool-native enforcement over prompt-only rules when available.

## Execution rhythm

Plan at fine granularity. Execute in an authorized batch until done, blocked, failed, or drift is detected. Do not ask for confirmation at every low-risk internal step.

Pause only when:

- The task cannot map to `docs/NORTH_STAR.md`.
- The task needs forbidden files.
- The task changes product goal, security, permissions, payment, privacy, destructive migration, public API, or data model.
- Harness fails twice and root cause is unclear.
- A new dependency or new persistent state is needed.
- Documentation and code disagree about the target behavior.

## Completion

1. Run task harness.
2. Run global smoke checks when relevant.
3. Inspect `git diff`.
4. Update `docs/TASKS.md`.
5. Update `docs/NORTH_STAR.md` if outcome, invariants, current slice, or decision debt changed.
6. Update `docs/DECISIONS.md` only for durable engineering decisions.
7. Update `docs/LESSONS.md` only for reusable failure lessons.
8. Update `docs/ASSETS.md` when asset state changes.
9. Run Handoff Trigger Check.
10. Update `docs/HANDOFF.md` only for H1/H2/H3.
