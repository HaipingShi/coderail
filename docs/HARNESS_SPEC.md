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

### T-004 v0.9.0 release candidate

```bash
python3 tests/test_structure.py
npm test
npm run ci
mkdir -p /tmp/coderail-v090-smoke && python3 scripts/init_project.py --target /tmp/coderail-v090-smoke --mode standard --force && rg -q '^SHIM_VERSION = "0\.9\.0"$' /tmp/coderail-v090-smoke/.coderail/coderail.py
```

Release review requirements:

- `VERSION`, package metadata, both plugin manifests, and the README badge agree on `0.9.0`
- a fresh installed `.coderail/coderail.py` reports `SHIM_VERSION = "0.9.0"`
- the changelog covers Task Switch Gate, closeout ledger integrity, and FN-029
- no package lockfile, release tag, or remote state is created

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

### T-005 ownership and baseline adoption

The lifecycle harness creates isolated repositories and proves: a file created under `lib/**` after start is committed; an unborn repository can explicitly adopt allowed files using fingerprint-only evidence; `.env` blocks done; ignored dependencies and unchanged build output are not staged; post-done inspect is healthy; and closeout contains no `git add .` path.

### T-006 atomic closeout

Isolated real Git repositories cover tracked modifications, glob-created files, unborn baseline adoption, outside and sensitive paths, deletion, rename, and post-commit mutation. Every successful done is followed immediately by inspect and a clean ownership assertion. A post-commit hook that mutates a task file must force a non-zero result, suppress the `Done` label, list the path, and reopen the task.

### T-008 canonical repository state

Unit characterization proves snapshots are immutable, rename origins survive porcelain parsing, and classification uses the accepted vocabulary. The complete lifecycle matrix then proves the shared parser/classifier preserves all T-007 behavior.

### T-009 closeout transaction authority

State-machine tests prove every phase before `FINALIZED` is unsuccessful and failure results retain exact paths. Existing hook-based failure injection proves commit and post-commit mutation cannot render Done. Real temporary repositories must finish with `inspect: consistent`, `Status: healthy`, and no closed ownership.
