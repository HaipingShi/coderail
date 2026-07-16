# Stabilization Freeze

Status: active
Effective: 2026-07-16
Owner: CodeRail maintainers

## Policy

CodeRail is feature-frozen. A new implementation task is eligible only when it
addresses a defect reproduced against the current repository state. Ideas,
possible failure modes, architectural preferences, and unmeasured performance
concerns may be recorded, but they do not authorize code changes.

This is an intake rule, not a new runtime gate or command.

## Valid Defect Candidate

A candidate must contain all of the following evidence:

1. The exact commit or version, operating system, and invocation used.
2. Minimal deterministic reproduction steps, preferably in a temporary Git
   repository created by the test harness.
3. Expected behavior grounded in an existing invariant, contract, or accepted
   user workflow.
4. Actual exit code, state transition, Git status, and relevant output.
5. The smallest known affected path set and confirmation that the behavior is
   not explained by unsupported configuration.

Sensitive security evidence may remain private, but it must still be concrete
and reproducible by a maintainer. A report that cannot yet meet this standard
stays an observation, not an implementation task.

## Admission Sequence

```text
observation -> reproduced -> bug task -> failing regression -> minimal fix
            -> targeted tests -> complete suite -> done -> immediate inspect
```

- `observation`: preserve evidence; do not change production code.
- `reproduced`: confirm the current build violates an existing promise.
- `bug task`: create a numbered task with exact scope and stop conditions.
- `failing regression`: make the real scenario fail before implementing.
- `minimal fix`: change the root cause without adding adjacent capability.

If reproduction stops failing, ownership is ambiguous, or the expected result
requires a new product decision, stop. Reclassify the item as an observation or
proposal; do not smuggle it into a bug fix.

## Allowed Work

- P0/P1 correctness, data-integrity, ownership, staging, and lifecycle defects.
- Security defects supported by private or public reproducible evidence.
- Compatibility regressions against an already supported workflow.
- Test-harness corrections required to express a reproduced defect faithfully.
- Documentation corrections that remove a demonstrated contradiction.

Refactoring is allowed only inside an accepted bug task when it is the smallest
way to remove the reproduced root cause. It does not become a separate scope.

## Frozen Work

- New commands, gates, lifecycle states, integrations, services, or automation.
- New convenience behavior without a current failing workflow.
- Speculative hardening for a failure that has not been reproduced.
- General architecture cleanup, dependency churn, or schema migration.
- Performance work without a repeatable baseline and regression threshold.
- Release expansion, remote push, or hosted infrastructure changes.

## Required Closeout Evidence

Every admitted bug must record:

- the original reproduction and failing test;
- the passing targeted test using the same scenario;
- the complete-suite and CI result;
- the exact implementation and ledger commits;
- immediate post-`done` inspect status;
- any residual boundary that was deliberately not expanded.

Successful closeout does not reopen feature development. The freeze ends only
through an explicit North Star decision, not because the defect queue becomes
empty.

## Observation Ledger

During the freeze, review these measures without creating work merely to move
the numbers:

- observations awaiting reproduction;
- reproduced defects awaiting a numbered task;
- fixes that required scope expansion;
- regressions found after `done`;
- feature-freeze exceptions approved explicitly.

Current baseline: one reproduced context-growth observation, zero admitted bug
tasks, and zero approved exceptions. See
`docs/observations/context-growth-20260716.md`.
