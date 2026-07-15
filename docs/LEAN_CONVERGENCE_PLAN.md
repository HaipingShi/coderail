# Lean Implementation Convergence

Status: active
Date: 2026-07-15
Milestone: M-012

## Intent

Keep the public rail small while reducing the internal cost of proving that it
is correct. Feature work is frozen for this milestone. Only two changes are in
scope: remove repository-state compatibility adapters and split the test
monolith without changing behavior.

Characterization tests are the migration boundary. They first freeze every
currently correct lifecycle result, then authority moves in small steps. A
step is accepted only when targeted tests, the complete suite, CI, and a real
`start -> done -> inspect` repository agree.

## Baseline

Recorded before T-011:

- closeout runtime modules: 3,258 lines;
- `tests/test_structure.py`: 1,910 lines and 103 tests;
- Git porcelain parsers: one;
- repository-state compatibility adapters: three runtime definitions plus
  four runtime call sites;
- closeout success authorities: one (`FINALIZED`).

## T-011 Remove Compatibility Adapters

1. Add a failing structural test that rejects legacy status projections.
2. Make closeout, ledger persistence, and task switching consume
   `RepositorySnapshot` and `FileState` directly.
3. Serialize dictionaries only where `.coderail/tasks.json` is written.
4. Delete `git_status_entries`, `as_legacy_entries`, and the duplicate
   closeout classifier adapter.
5. Require touched closeout runtime code to be net-negative.

Exit measures:

- zero runtime compatibility adapters and zero runtime call sites;
- one porcelain parser and one ownership classifier;
- no characterized behavior change;
- closeout runtime modules below 3,258 lines.

## T-012 Split The Test Monolith

1. Add a test-inventory guard before moving tests.
2. Extract shared temporary-Git setup and command runners into one support
   module with no test discovery side effects.
3. Group tests by responsibility: structure, lifecycle, closeout, inspect, and
   task switch.
4. Keep one deterministic suite entry point so `npm test` and `npm run ci`
   retain their command contract.
5. Prohibit test duplication: test names must be unique and the discovered
   count may not decrease during migration.

Exit measures:

- no test module exceeds 650 lines;
- all 104 tests present after T-011 remain discoverable exactly once;
- targeted groups can run independently;
- the existing complete-suite and CI commands remain green.

## Observation Cadence

At each task boundary record adapter definitions and call sites, runtime and
test lines by module, discovered test count and duplicate names, targeted and
complete-suite results, CI, and immediate post-done inspect state.

## Stop Conditions

- A characterization test must be weakened to make a migration pass.
- A second state parser, classifier, or success authority appears.
- A public command or task metadata schema must change.
- Runtime or test structure grows without deleting an existing duplication.
- The real repository cannot complete `done -> inspect` consistently.

## Non-Goals

- New commands, gates, lifecycle states, services, or remote automation.
- Changes to scope, sensitive-file, forbidden-file, or inspect policy.
- Combining the implementation and ledger commits.
- Automatic push.
