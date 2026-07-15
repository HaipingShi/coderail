# Closeout Convergence

Status: accepted
Owner: CodeRail maintainers
Milestone: M-011 internal convergence
Tasks: T-007 through T-009

## Problem

The public workflow is deliberately small, but closeout facts are derived across
`coderail.py`, `finish_task.py`, `closeout_check.py`, `task_switch.py`, and
`inspect_state.py`. Repeated Git scans, ownership decisions, status writes, and
success checks make ordering defects likely even when each local check is sound.

## Outcome

CodeRail keeps `start`, `check`, and `done` unchanged while converging on one
repository snapshot, one ownership classifier, and one closeout transaction
authority.

```text
done success
= verification passed
+ ownership classified
+ safe paths committed
+ state and ledger persisted
+ final snapshot consistent
+ inspect projection non-blocked
```

## External Contract

- A successful `done` followed immediately by `inspect` is consistent.
- Task globs continue to own files created after activation.
- Safe tracked changes, new files, deletions, and renames are committed.
- Explicit baseline adoption remains content-free and auditable.
- Unchanged pre-task dirty files are not attributed to the task.
- Outside, forbidden, sensitive, generated, ephemeral, or ambiguous paths are
  excluded or block before success.
- Stage, commit, persistence, or post-commit consistency failure returns non-zero,
  suppresses `Done`, reports exact paths, and leaves a resumable task.
- No path uses `git add .` or automatically pushes.

## Canonical Snapshot

`RepositorySnapshot` is an immutable observation of one Git worktree instant.
Each `FileState` contains:

- normalized path and optional original path;
- porcelain status and tracked/untracked/ignored disposition;
- content fingerprint when required for baseline comparison;
- task ownership classification and its reason.

The classifier produces exactly one disposition per path:

```text
owned-safe | unchanged-baseline | outside | forbidden
sensitive | generated | ephemeral | ambiguous
```

Done, inspect, and task switching must consume this model rather than parse Git
status independently.

## Closeout State Machine

```text
CREATED -> VERIFIED -> SNAPSHOTTED -> CLASSIFIED -> STAGED
        -> COMMITTED -> PERSISTED -> RESCANNED -> FINALIZED
```

Failure results are explicit:

```text
BLOCKED_SCOPE | BLOCKED_SENSITIVE | STAGE_FAILED | COMMIT_FAILED
PERSIST_FAILED | POST_COMMIT_DIRTY | INSPECT_INCONSISTENT
```

Only `FINALIZED` may render `Done`. A failure after provisional closure uses a
compensating reopen; it never converts a failed transaction into a warning.

## Target Responsibilities

- `coderail.py`: CLI parsing, application-service call, compact rendering.
- `closeout_transaction.py`: the only closeout sequencing and success authority.
- `repository_state.py`: Git observation, fingerprints, scope and ownership.
- `finish_task.py`: advanced closeout application service pending a later
  responsibility-boundary review; it does not own repository-state adapters.
- `closeout_check.py`: read-only preflight/report adapter.
- `inspect_state.py`: read-only projection of the canonical snapshot.
- `task_switch.py`: ownership transfer and pause/resume metadata only.

## Migration

### T-007 Characterize

Freeze observable success and failure behavior in real temporary Git repositories.
No production closeout behavior changes.

### T-008 Unify facts

Introduce the canonical snapshot and classifier, then migrate readers one at a
time. Compatibility adapters may remain temporarily, but new parsing is forbidden.

### T-009 Unify authority

Move sequencing and final success into one transaction service. CLI and legacy
entry points become adapters, then duplicate state transitions are deleted.

### T-011 Delete repository-state adapters

Move every runtime caller to `RepositorySnapshot` and `FileState`, delete
legacy status projections, and restrict dictionary serialization to persisted
task metadata. This completes the temporary adapter allowance from T-008.

### T-012 Split characterization tests

Keep characterization behavior fixed while extracting shared Git fixtures and
responsibility-focused modules. Test discovery count and command entry points
are invariants during the move.

## Non-Goals

- No new user command, gate, server, database, plugin, or remote automation.
- No task-file schema migration unless characterization proves it unavoidable.
- No one-shot rewrite of closeout and task switching.
- No weakening of inspect, scope, sensitive-file, or forbidden-file rules.
- No requirement to collapse implementation and ledger commits during this slice.

## Measures

- one Git status parser;
- one ownership classifier;
- one closeout success authority;
- one task status transition API;
- zero `git add .` and zero automatic push paths;
- all characterization tests and full CI remain green;
- duplicate closeout decisions decrease; new framework code must earn deletion.

## Stop Conditions

- A migration changes an external behavior without an explicit failing test.
- A second snapshot or classifier becomes necessary.
- Done and inspect cannot consume the same facts without weakening either.
- A phase requires simultaneous rewrite of closeout and task switching.
- Net complexity grows without deleting an existing authority or decision path.
