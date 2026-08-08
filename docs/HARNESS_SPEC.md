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

## T-018 Scope contradiction and recoverable closeout

```bash
python3 tests/test_closeout.py
python3 tests/test_lifecycle.py
python3 tests/test_task_switch.py
python3 tests/test_structure.py
npm run ci
git diff --check
```

Required matrix:

- contradictory Allowed child + Forbidden parent -> start/switch rejected before state writes
- legacy contradictory task -> closeout rejected before status transition with exact rules/path
- narrowed production Forbidden -> declared test path closes normally
- commit/index-lock failure -> `verified-commit-pending`, evidence and exact safe files retained
- explicit `--no-commit` -> one classified snapshot, no `POST_COMMIT_DIRTY`
- manual exact commit or permission recovery -> `done --resume` reaches `FINALIZED`
- unrelated dirty baseline -> never staged, committed, or rewritten
- repeated resume -> no duplicate commit, PROGRESS entry, or verify trace
- existing auto-commit, Task Switch Gate, manual Drive, sensitive-file, and no-push tests remain green

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

### T-017 Markdown-formatted scope paths

The parser contract proves that plain patterns are unchanged, an exact pair of
Markdown inline-code delimiters is presentation only, and annotated or
malformed values are not silently rewritten. Real temporary repositories prove
that an inline-code-formatted allowed glob commits a newly created matching
file and finishes with healthy inspect, while an equivalently formatted
forbidden path still blocks done and remains untracked.

TDD evidence:

- Red: `test_scope_patterns_treat_exact_inline_code_as_presentation_only`
  failed because `` `lib/**` `` retained its backticks.
- Red lifecycle: done classified `lib/new-file.ts` outside the formatted
  allowed glob and refused closeout.
- Green: all 31 static tests and all 16 closeout tests passed.

```bash
python tests/test_static.py
python tests/test_closeout.py
```

### T-047 self-governance decay regression

The regression harness keeps CodeRail's own repository subject to the same
contracts it installs elsewhere. It proves that dot-prefixed scope roots keep
their names, `doctor` is not mistaken for the documentation word `doc`, and
the checked-in `.coderail` launcher exactly matches the current stamped local
entry shim.

Health and completion assertions cover the user-facing convergence:

- `coderail check` must fail and include Doctor's severe finding when Doctor is
  unhealthy.
- automatic `coderail done` must fold a clean post-commit Inspect projection
  into the closeout commit rather than commit a dirty pre-commit snapshot.
- `done` is the single completion authority; `done-gate` is diagnostic and
  `closeout` is compatibility guidance, not a second write sequence.
- persisted Inspect output identifies itself as a point-in-time snapshot.

TDD evidence begins with failures for dot-directory normalization, stale
post-close status, and the missing snapshot marker. The smallest production
changes are exercised by the existing responsibility suites; the locked core
inventory remains 122 tests.

The root-repository repair also removes `closed_pending` records from T-042
through T-046. T-047 captured an empty baseline at a later clean HEAD, which is
repository evidence that those path-only records described already committed
work rather than current residue. This is a one-time state repair, not a rule
that active work may ignore real closed-task residue.

```bash
python tests/test_static.py
python tests/test_closeout.py
python tests/test_inspect.py
python scripts/doctor.py --target .
python .coderail/coderail.py check
python scripts/trace_doctor.py --target .
npm.cmd test
```

### T-059 current-authority closeout projection consistency

The delivery/Inspect harness registers canonical current-authority fixtures and
proves that a finalized Coordinate cannot retain an explicit project-authored
current status of `active`, `in_progress`, `pending-closeout`,
`verified-commit-pending`, bare status/closeout `pending`, `待提交`, or `待收口`.

Required matrix:

- an exact Task/Coordinate context plus a stale status field blocks Inspect;
- table/list assertions bind both internal ids and registered display ids;
- diagnostics include canonical file, line, task, alias when used, recorded
  state, and expected `finalized` state;
- narrative incident prose and append-only TRACE activation history stay out of
  current-truth consistency;
- ordinary `done` reopens before commit and suppresses `Done`;
- `done --no-commit` rejects stale prose before freezing its exact snapshot;
- `done --resume` preserves `verified-commit-pending` until prose is repaired;
- exact machine markers still synchronize to `finalized` without rewriting
  surrounding project prose.

```bash
python3 tests/test_delivery.py
python3 tests/test_inspect.py
python3 tests/test_closeout.py
python3 tests/test_structure.py
```

### T-060 lifecycle authority and formulation safety

This harness supersedes T-059 only where T-059 treated human-owned prose as a
closeout authority. Exact machine markers remain fail-closed.

Required matrix:

- finalized live state plus README/HANDOFF `waiting for commit/push` produces a
  `projection_staleness` warning, `blocks=none`, and
  `blocks.formulation=false`;
- the same warning leaves product recommendation/formulation available and does
  not add a TASKS or TRACE entry, especially not a recursive GOV Coordinate;
- a conflicting exact lifecycle marker and multiple active tasks produce
  `control_plane_conflict` with activation blocked;
- `inspect`, `inspect --no-write`, `check`, Drive, and recommendation preserve
  worktree bytes, Git HEAD, task count, TRACE bytes, and Git-index bytes/mtime;
- `sync-projections` previews with zero writes and writes only after `--apply`;
- recommendation-only Drive returns `RECOMMEND` with no execution authority,
  while explicit activation mode alone may return `ADVANCE`;
- append-only TRACELOG/PROGRESS lifecycle wording never enters current truth;
- owner output precedes governance detail and never invents product capability
  from commits or task finalization.
- the locked core inventory contains 162 unique tests after the T-060 Red
  matrix; duplicate discovery remains forbidden.

```bash
python3 tests/test_delivery.py
python3 tests/test_inspect.py
python3 tests/test_drive.py
python3 tests/test_static.py
python3 tests/test_structure.py
git diff --check
```

### T-063 explicit owner language and legacy-output retirement

The downstream Chinese A/B has satisfied the v0.10 migration exit condition.
The retirement harness keeps the audience boundary strict without changing the
closeout kernel.

Required behavior:

- a closeout without an explicit owner locale exits before verification,
  lifecycle mutation, delivery-ledger append, or Git mutation;
- source-closing `switch` requires the same locale, while no-active activation,
  `--continue-current`, and `--dirty-fork` remain available without it;
- the legacy seven-section renderer is absent;
- explicit Chinese and English closeout retain the bounded Owner Receipt and
  the complete Agent Blackboard/Technical Report facts;
- the locked core remains 162 unique tests and the complete suite contains 171
  unique tests exactly once.

```bash
python3 tests/test_owner_comms.py
python3 tests/test_task_switch.py
python3 tests/test_static.py
python3 tests/test_structure.py
git diff --check
```

### T-062 owner-safe copy preflight

The live T-061 self-closeout showed that a leak-free fallback can still fail the
owner communication outcome by hiding real capability. The regression fixture
uses otherwise valid Delivery Contract structure with owner-unsafe product copy.

Required behavior:

- localized `done` returns non-zero before verification or lifecycle mutation;
- console text stays bounded and does not expose task IDs or paths;
- the active marker, Git HEAD, and DELIVERIES ledger remain unchanged;
- the existing valid Chinese fixture still produces a useful Owner Receipt;
- the complete-suite inventory contains 170 unique tests exactly once.

```bash
python3 tests/test_owner_comms.py
python3 tests/test_lifecycle.py
python3 tests/test_structure.py
git diff --check
```

### T-061 owner communication and durable delivery facts

The owner communication harness is presentation-layer Red/Green. It must not
alter scope classification, the closeout transaction, Git staging, task switch,
or TRACE authority.

Required matrix:

- `done --owner-locale zh-CN` success emits three-to-six Chinese sentences and
  no unannotated English, task/product ID, path, or governance jargon;
- necessary bilingual terms remain allowed only as an annotated parenthetical;
- unlocalized Delivery Contract text fails safe to a bounded Chinese notice
  instead of leaking English claims;
- the same `CloseoutFacts` renders a Technical Report containing task reference,
  exact verification, paths, commits, and safe files;
- Inspect identifies itself as the Agent Blackboard, references the durable
  delivery fact, and never renders NORTH_STAR as verified product capability;
- `owner-summary` preserves every project byte and lifecycle record;
- `DELIVERIES.jsonl` retains product facts after TASKS compaction and a fresh
  Git clone;
- legacy closeout output remains compatible only for calls without an explicit
  owner locale during the downstream A/B window.
- the locked complete-suite inventory contains 169 unique tests, including the
  seven owner communication tests exactly once.

```bash
python3 tests/test_owner_comms.py
python3 tests/test_delivery.py
python3 tests/test_inspect.py
python3 tests/test_closeout.py
python3 tests/test_static.py
python3 tests/test_lifecycle.py
python3 tests/test_structure.py
git diff --check
```
