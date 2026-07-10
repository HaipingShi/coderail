# Harness Spec

## Global Checks

```bash
# replace with project checks
python3 -m pytest
```

## Task Checks

### T-001

```bash
# task-specific check
```

## Drive Progress Harness

- Progress signal:
- How to measure:
- Improvement direction: increase | decrease | boolean
- Checkpoint command:
- Terminal evidence:

Continuous Drive requires a measurable progress signal. Activity without
progress consumes the no-progress budget in `docs/NORTH_STAR.md`.

## TDD Evidence

For correctness-sensitive work, record the Red check, Green check, Refactor check, Regression check, and CI check in the task's `V -- Verify` section.

## Rule

No task is done until V passes or manual acceptance is recorded.
