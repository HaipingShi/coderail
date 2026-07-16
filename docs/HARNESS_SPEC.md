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

### T-011 repository-state adapter removal

The structural harness rejects `git_status_entries`, `as_legacy_entries`, and
runtime calls through task-switch status projections. Lifecycle
characterization still covers tracked changes, glob-created files, baseline
adoption, ignored and sensitive paths, delete/rename, commit failure, and
post-commit mutation. Touched closeout runtime lines must decrease from the
3,258-line pre-task baseline.

```bash
python tests/test_structure.py
npm run ci
```

### T-012 responsibility-focused characterization suite

The suite retains 104 unique test definitions. Every responsibility module is
independently executable and stays below 650 lines; `test_structure.py` is a
thin complete-suite aggregator. The split must not change `npm test` or
`npm run ci`.

TDD evidence:

- Red: the inventory guard failed with `responsibility test modules are incomplete`.
- Green: independent groups passed with counts `28/29/7/11/15/14`.
- Full discovery: `python -m pytest -q` passed all 104 tests exactly once.

```bash
python tests/test_static.py
python tests/test_drive.py
python tests/test_inspect.py
python tests/test_task_switch.py
python tests/test_lifecycle.py
python tests/test_closeout.py
python tests/test_structure.py
npm run ci
```

### T-013 stabilization freeze policy

This documentation-only task verifies that the existing static harness remains
green and `coderail check` accepts the active coordinate. It adds no runtime
gate. Future bug tasks must place their exact reproduction in the relevant
responsibility module before changing production code.

```bash
python tests/test_static.py
python scripts/coderail.py check
```

### T-014 synthetic context-growth observation

The harness installs the standard template into a disposable Git repository,
keeps the project file count constant, and completes sequential real lifecycle
commands. It records required-read bytes, estimated tokens, task-state bytes,
growth slopes, command latency, and a fresh-process eager-import proxy. Every
done must be followed by healthy inspect, no closed ownership, and a clean
worktree.

TDD evidence:

- Red: observer contract failed with `ModuleNotFoundError: observe_context_growth`.
- Green: task-state classification and median/P95 contract passed.
- Targeted: three-cycle smoke observation completed successfully.
- Full: the split complete-suite entry point passed all 105 tests.

```bash
python tests/observe_context_growth.py --tasks 10 --startup-runs 20 \
  --output docs/observations/context-growth-20260716.json
```

### T-015 bounded hot-context contract

The measurement contract is characterized independently: required reads are
exactly AGENTS, NORTH_STAR, TASKS, HANDOFF, and CODERAIL_STATUS; token estimate
is `ceil(UTF-8 bytes / 4)`; the limit is 3,000 tokens. With
`--assert-thresholds`, the observer returns non-zero if the limit fails, if
either required-read bytes or TASKS bytes changes after closes 2 through 10,
if internal task IDs are not unique and strictly increasing, or if PROGRESS
and TRACE do not each contain all ten task IDs.

Lifecycle characterization additionally proves that a successful ledger
removes the closed body, a rejected ledger commit restores it and retains the
pending snapshot, and `progress --repair` later commits and compacts it.
Inspect characterization rebuilds compacted history and preserves legacy
cutoff and historical verification debt. Existing checkpoint, dirty-fork, and
paused-resume tests protect hot ownership behavior.

TDD evidence:

- Red: static characterization failed because the fixed estimator constants
  did not exist; lifecycle characterization then failed because `[x]` bodies
  still accumulated in TASKS.
- Green targeted: 79 lifecycle/static/inspect/switch/closeout tests passed.
- Synthetic: ten sequential tasks ended at 10,330 required bytes / 2,583
  estimated tokens; closes 2 through 10 were byte-stable and all ten IDs were
  present in both PROGRESS and TRACE.

```bash
python tests/observe_context_growth.py --tasks 10 --startup-runs 10 --assert-thresholds
python tests/test_static.py
python tests/test_lifecycle.py
python tests/test_inspect.py
python tests/test_task_switch.py
python tests/test_closeout.py
```
