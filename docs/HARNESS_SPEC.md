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

### T-003 Task Switch Gate

```bash
python3 tests/test_structure.py
npm test
npm run ci
python3 scripts/coderail.py check
```

Required lifecycle matrix:

- accepted source -> done commit -> destination active
- verified checkpoint -> stage-complete commit -> source `[p]` -> destination active
- unsafe source -> H3 -> continue-current or dirty-fork only
- closed dirty owner -> ordinary activation blocked with exact paths
- pre-existing dirty path -> path/status/SHA-256 baseline -> unchanged path excluded
- dirty-fork and paused resume -> exactly one active owner, original ownership restored
- no CodeRail path runs `git push`

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
