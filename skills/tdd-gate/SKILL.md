---
name: tdd-gate
description: Enforce Red-Green-Refactor evidence for bugs, regressions, parsers, domain logic, APIs, and shared utilities.
---

# tdd-gate

Use before implementation for correctness-sensitive tasks and before done for any task where TDD mode is `required`.

## Action

Run:

```bash
python3 scripts/tdd_check.py --target .
```

## Required evidence

- TDD mode: required, optional, or waived.
- Red check: the failing check captured before implementation.
- Green check: the passing check after the minimal implementation.
- Refactor check: checks still pass after cleanup.
- Regression check: stable check for the bug or failure mode when relevant.
- CI check: CI Gate or equivalent repository checks.

## Rules

- Required by default for bug fixes, regressions, parsers, validators, domain logic, public APIs, shared utilities, and risky behavior-preserving refactors.
- Optional or waived for docs-only, scaffolding, release metadata, visual polish, and exploratory spikes.
- Do not treat tests written after implementation as Red evidence unless the failure was reproduced before the fix.
- If TDD is waived, record the reason in `V -- Verify`.

