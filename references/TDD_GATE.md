# TDD Gate

TDD Gate is CodeRail's test-first implementation loop.

CodeRail already requires verification before completion. TDD Gate strengthens
that rule for work where correctness is best protected by a failing check before
implementation.

## Loop

```text
Red -> Green -> Refactor -> CI Gate -> Done Gate
```

## Default policy

TDD is required by default for:

- bug fixes and regressions;
- parsers, validators, and data transforms;
- domain logic and shared utilities;
- public API or contract changes;
- risky refactors with observable behavior.

TDD is optional or may be waived for:

- docs-only work;
- scaffolding with no behavior yet;
- release metadata;
- visual polish without stable assertions;
- exploratory spikes.

Waivers must be explicit and include a reason.

## Coordinate fields

Inside `V -- Verify`, record:

```text
TDD mode: required | optional | waived
Red check:
Green check:
Refactor check:
Regression check:
CI check:
Waiver reason:
```

## Evidence

- Red check: the new/changed test, harness, or fixture fails for the intended
  reason before implementation.
- Green check: the minimal implementation makes that check pass.
- Refactor check: cleanup did not change behavior; the same checks still pass.
- Regression check: a bug or failure mode has a stable check that would fail if
  the bug returns.
- CI check: repository-level checks passed through CI Gate or an equivalent
  command.

## Stop rule

Do not stop at "implemented" when TDD is required and Red or Green evidence is
missing. Either add the evidence, mark a decision-grade blocker, or explicitly
waive TDD with a reason.

