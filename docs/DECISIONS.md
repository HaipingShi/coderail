# Decisions

Record durable engineering decisions.

## ADR-003 Task switching is an ownership transaction

Status: accepted
Date: 2026-07-15
Task: T-003

- `[~]` and `[!]` are active ownership states; `[p]` is paused, non-active, and explicitly resumable.
- `start`, `next --go`, and `switch` share one activation preflight. `--force` cannot bypass the single-active invariant.
- A safe switch closes or checkpoints and commits the source before activation. An unsafe switch writes H3 and requires `continue-current` or `dirty-fork`.
- Pre-existing dirty state is stored as normalized path, Git porcelain status, and SHA-256; contents are never persisted.
- Switch transactions are monotonic: successful commits are not rolled back after a later failure.
- Auto-commit never grants auto-push authority.

## ADR-004 Scope patterns survive activation and closeout is two-phase

Status: accepted
Date: 2026-07-15
Task: T-005

- `--files` stores normalized glob intent as well as matches present at activation, so later matching files have the same owner.
- A successful `done` requires a path-safety preflight before the task status changes; the final closeout stages only its audited explicit path list.
- `--adopt-baseline` is explicit and valid only before the first commit. It records path, porcelain status, SHA-256, and disposition without file contents.
- Sensitive paths block closure. Unchanged non-adopted baseline and ignored local artifacts remain unstaged; generated paths are never automatically adopted merely because they exist.

## ADR-005 Done is an atomic completion boundary

Status: accepted
Date: 2026-07-15
Task: T-006

CodeRail 的 done 是原子化完成边界。成功返回意味着验证、范围判断、安全提交、状态持久化和提交后 inspect 一致性全部成立。

- The word `Done` is emitted only after the closeout commit, ledger commit, final Git rescan, and inspect-equivalent evaluation succeed.
- A failure after `[x]` is written compensates by reopening the task as `[!]`; a post-commit mutation also clears closed ownership for that now-active task and reports exact residual paths.
- This strengthens done/finish/closeout. Inspect keeps the same blocking rules and is not taught to hide residue.

## ADR-006 Repository state is an immutable shared fact

Status: accepted
Date: 2026-07-15
Task: T-008

- `repository_state.py` owns the only porcelain parser, path matcher, file fingerprint implementation, immutable snapshot, and ownership vocabulary.
- Closeout consumes the canonical classifier. Done, inspect, and task switching retain compatibility adapters only at their public/internal call boundaries.
- Ignored files are classified before forbidden patterns so local generated artifacts cannot become blockers merely because a task forbids their parent source directory.
- Compatibility projections may translate the canonical dataclasses to legacy dictionaries, but may not re-parse Git or invent a second classification.

## ADR-007 FINALIZED is the only closeout success state

Status: accepted
Date: 2026-07-15
Task: T-009

- `closeout_transaction.py` defines ordered phases and explicit failure codes; no intermediate phase has a truthy success result.
- `coderail done` advances the transaction around the existing compatibility gates, ledger persistence, final repository rescan, and inspect-equivalent evaluation.
- The user-facing `Done` label is guarded by `transaction.success`, which is possible only after `FINALIZED`.
- Queued tasks hydrate registered `Run:` verification and acceptance clauses from their task contract when activation metadata does not contain them, preventing a verified queued closeout from being journaled as unverified.

## ADR-008 Canonical state has no runtime compatibility projection

Status: accepted
Date: 2026-07-15
Task: T-011

- Runtime closeout, ledger, and task-switch code consumes `RepositorySnapshot`
  and `FileState` directly.
- Dictionary conversion is permitted only at the `.coderail/tasks.json`
  persistence boundary; it is not a second repository-state API.
- `git_status_entries`, `as_legacy_entries`, and the duplicate closeout
  classifier are deleted rather than deprecated.
- Characterization behavior is the compatibility contract. Internal legacy
  shapes are not preserved when they have no external caller.

## ADR-009 Characterization tests are grouped by responsibility

Status: accepted
Date: 2026-07-15
Task: T-012

- `test_structure.py` remains the stable complete-suite entry point but owns no
  lifecycle tests itself.
- Static, Drive, inspect, task-switch, lifecycle, and closeout tests are
  independently runnable modules backed by one side-effect-free support file.
- Suite inventory is a checked invariant: 104 unique test definitions, no
  duplicates, and no responsibility module above 650 lines.
- `npm test` and `npm run ci` keep their existing commands; no package or
  production code changes are required for the split.

## ADR-010 Feature work is frozen until a defect is reproduced

Status: accepted
Date: 2026-07-16
Task: T-013

- Only defects reproduced against the current repository state may authorize
  implementation work.
- Expected behavior must already follow from an invariant, contract, or
  supported workflow; a desired new behavior is a proposal, not a bug.
- Each admitted defect begins with a failing characterization or regression
  using the real scenario, followed by the smallest root-cause fix.
- The freeze is an intake policy, not a CLI gate. Ending it requires an
  explicit North Star decision.

## ADR-011 TASKS is the hot ownership view, not completed-history storage

Status: accepted
Date: 2026-07-16
Task: T-015

- `docs/TASKS.md` persists only active, queued, paused, blocked, or reopened
  work. A completed body is transient until its ledger commit succeeds.
- `docs/PROGRESS.md` plus a verify fact in `docs/TRACELOG.jsonl` are the
  repository-tracked authority for compacted completed history. Reports and
  `.coderail/tasks.json` are supplemental recovery detail, never the sole
  authority.
- Compaction happens after PROGRESS and TRACE exist and inside the ledger
  commit. If that commit fails, the full closed body and pending snapshot are
  restored so `progress --repair` can retry the durable boundary.
- Task numbering scans hot TASKS, PROGRESS, TRACE, and metadata. Removing
  completed bodies can therefore never reuse an internal task ID.
- Inspect reconstructs compacted completed rows from the same PROGRESS and
  TRACE facts; legacy cutoff and verification-debt evaluation do not depend on
  closed bodies remaining hot.
