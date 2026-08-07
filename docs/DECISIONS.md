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

## ADR-012 Scope contradictions and commit-pending are explicit states

Status: accepted
Date: 2026-07-17
Task: T-018

- Scope normalization happens before `start` or `switch` writes task state and
  again before closeout changes task status. Any concrete path matching both
  Allowed and Forbidden is `SCOPE_CONTRADICTION`; diagnostics name the path and
  both rules. Allowed never overrides Forbidden, and no implicit exception
  syntax exists.
- The facade prepares implementation plus TASKS, PROGRESS, TRACE, STATUS, and
  metadata as one classified closeout snapshot before attempting its exact Git
  commit. This refines ADR-011: compaction may be prepared in the worktree, but
  it becomes durable only with that snapshot commit.
- `COMMIT_PENDING` preserves successful verification without claiming success.
  The snapshot records task id, evidence, exact safe files and fingerprints,
  full state-file classification, expected message, pre-commit HEAD, mode,
  failure detail, and resume command.
- `done --no-commit` selects manual commit mode from the beginning.
  `done --resume` either retries exact staging/commit after permission recovery
  or verifies that a manual commit contains every safe file. It never stages an
  unrelated dirty path and is idempotent after finalization.
- Only `FINALIZED` renders `Done`. Commit permission failure is recoverable
  pending state, not `[!]`; scope, sensitive-file, manual Drive, and no-push
  invariants remain unchanged.

## ADR-013 Freeze-period command additions were an undocumented exception

Status: accepted
Date: 2026-07-28
Task: T-047

- ADR-010 froze feature work on 2026-07-16 until a reproduced defect or an
  explicit North Star decision authorized implementation.
- The later public inspection commands, including graph-oriented navigation
  added during T-046, were merged without a repository-tracked freeze
  exception. User direction existed in the development conversation, but the
  required decision was not persisted before implementation. This is a
  governance process violation, not evidence that the freeze silently ended.
- The already merged behavior remains in place. Removing it during T-047 would
  be a new product decision and could create a regression; this repair neither
  expands those commands nor treats them as precedent for more feature work.
- During the freeze, only a reproduced defect with an existing invariant may
  enter implementation. Any proposed exception must be recorded in the North
  Star or Decisions before code changes begin, with its scope and stop
  conditions.
- T-047 is admitted only for reproduced self-governance defects: stale local
  entrypoint, contradictory health signals, stale status projection, duplicate
  completion guidance, dot-directory scope corruption, and rail
  misclassification.

## ADR-014 Code length does not authorize kernel refactoring

Status: accepted
Date: 2026-07-28
Task: T-048

- 代码长度本身不授权重构；只有可重复的维护伤害才能触发内核治理。
- `scripts/coderail.py` 的行数、函数数和集中度只作为观察信号。任何 PREPARE
  或 GOVERN 决定必须引用已复现缺陷、跨职责共同变更、冲突状态权威、局部测试
  缺口或可复查的回归成本。
- stabilization freeze 和 ADR-010 保持有效；T-048 只建立被动观察基线，不
  授权生产代码移动、抽取、重命名或重构。

## ADR-015 Freeze-period public-surface cleanup is a bounded exception

Status: accepted
Date: 2026-07-28
Task: T-049

- The repository owner explicitly authorized removal of machine-specific
  configuration, stale handoff state, and the completed Workflow Lab workspace
  from the maintained `main` branch.
- The final Workflow Lab tree must remain available through the immutable
  `archive-workflow-lab-final-20260728` tag before its removal from `main`.
- This exception covers only repository hygiene and public-surface reduction.
  It does not authorize changes to the production kernel, tests, templates,
  skills, references, package metadata, CI, commands, hooks, or telemetry.
- The archive result remains `REVISE`; moving the experiment out of `main`
  neither promotes it to product behavior nor erases its recorded evidence.
- The exception ends when T-049 is closed. Any state-ledger compaction must be
  designed and governed as a separate task before implementation.

## ADR-016 Current blueprints must point to renderable implementation maps

Status: accepted
Date: 2026-07-28
Task: T-051

- A Blueprint entry marked `current` must point to a diagram or executable flow
  that shows the claimed relationships; a directory list or prose-only section
  is not enough for architecture, component, sequence, state, or data-flow
  coverage.
- T-051 is a bounded documentation-maintenance exception during stabilization:
  it records the existing kernel, lifecycle, closeout transaction, and state
  authorities without changing their behavior.
- The permitted surface is README, the repository Blueprint index, the diagram
  document, and this decision. Production scripts, tests, templates, skills,
  references, packages, CI, commands, hooks, and telemetry remain unchanged.
- Diagram detail must stop at facts that can be traced to current files and
  commands. Proposed architecture belongs in a separate design task and cannot
  be labeled `current`.

## ADR-017 Continuation truth is a structured projection, not project prose

Status: accepted
Date: 2026-08-05
Task: T-054

- CodeRail owns one explicitly delimited continuation block in `HANDOFF.md`.
  Inspect and closeout parse only that block; project-authored handoff prose is
  preserved and is never interpreted through keywords such as `needs`.
- The projection records handoff level, last closed task, closeout state,
  recommendation status, candidate direction, human gate, and next executable
  step. Missing legacy blocks produce a warning and migrate only on a
  write-authorized Inspect or verified closeout.
- A mission and slice that remain active while no open Coordinate owns the
  available continuation produces `REQUEST_DIRECTION`, not
  `NO_RECOMMENDATION`. Candidate directions remain evidence for the owner;
  CodeRail does not select, activate, or execute one automatically.
- Closeout advances the projection through `pending-closeout`,
  `verified-commit-pending`, and `finalized`. Resume is idempotent, exact-file
  staging remains mandatory, manual Drive remains the execution authority, and
  automatic push remains forbidden.

## ADR-018 Verified local commit is the no-prompt completion default

Status: accepted
Date: 2026-08-05
Task: T-056

- Successful `coderail done` is authorization for one exact task-scoped local
  commit after verification, scope, sensitive-file, and persistence gates pass.
  An agent does not ask a non-technical user to re-decide that mechanical step.
- `done --no-commit` is an explicit review-first exception, not the ordinary
  default. Failed gates, unsafe or ambiguous ownership, and commit permission
  failures remain blocking or recoverable pending states.
- Product direction, destructive changes, push, tag, release, and any scope or
  permission expansion remain separate human decisions. Local commit authority
  never implies publication authority.

## ADR-019 Persist assertions are explicit JSON, exact, and read-only

Status: accepted
Date: 2026-08-05
Task: T-055

- A task may add `Persist-Assert: {JSON}` inside P to require a repository-local
  UTF-8 file and optional exact literals before Done Gate passes. Failures use
  the concrete `PERSIST_GAP` code and reason.
- The first protocol version supports only `path` and `contains`. It does not
  interpret Markdown, product language, semantic freshness, or arbitrary query
  expressions, and it never rewrites the asserted surface.
- The contract is optional and backward compatible. Broader schemas, adapters,
  public CLI flags, and automatic project-document synchronization require a
  separately authorized task.

## ADR-020 v0.10.0 remains explicitly pre-1.0

Status: accepted
Date: 2026-08-06
Task: T-057

- The post-v0.9.0 changes ship as v0.10.0, not v1.0.0. The release represents
  substantial new capability while CodeRail remains in a rapid-evolution phase
  with a deliberately weaker compatibility promise than a stable major line.
- The everyday `start`, `check`, and `done` entry points remain compatible for
  this release. Advanced commands, generated governance documents, and internal
  `.coderail` state formats may still evolve before 1.0.
- T-057 changes only release metadata and documentation. The repository owner
  separately authorized the v0.10.0 tag, push, and GitHub Release; no product
  behavior, dependency, or automatic-publication policy changes are included.

## ADR-021 Customer delivery is an explicit projection over closeout facts

Status: accepted
Date: 2026-08-06
Task: T-058

- Internal closeout receipts prove commits, verification, exact safe files, and
  transaction state. They are not customer outcome claims. An optional strict
  Delivery Contract supplies outcome, capability, gap, assessment, recommendation,
  and decision facts; missing contracts remain `not_assessed`.
- Finalized proves only Task Done. Milestone and Product completion require
  explicit assessments. Planned, recommended, active, and none remain distinct;
  recommendations are read-only and never grant registration, activation, or
  implementation authority.
- Current authority files are registered through `docs/ASSETS.md`. CodeRail
  reads and rewrites only explicit `coderail:current-truth` markers, excludes
  append-only TRACE history, and blocks Inspect health when a finalized task has
  a stale marker.
- Resume may finalize only the declared, verified projection set. A missing,
  out-of-snapshot, forbidden, or unwritable projection preserves
  `verified-commit-pending` and reports exact repair files. Exact staging,
  single-active ownership, manual Drive, and no-automatic-push remain unchanged.

## ADR-022 Canonical current authority fails closed on stale Coordinate prose

Status: accepted
Date: 2026-08-07
Task: T-059

- `docs/ASSETS.md` registration is the current-authority boundary. In canonical,
  non-append-only files, an explicit status assertion bound to the exact internal
  task id or its registered display id participates in current-truth consistency
  even when the project author did not add a machine marker.
- CodeRail recognizes only bounded assertion shapes: a status field inside an
  exact Task/Coordinate context, or a table/list row carrying both the exact id
  and status. Narrative mentions remain opaque. Append-only TRACE history remains
  evidence and is never reclassified as current state.
- The stale finalized states are `active`, `in_progress`, `pending-closeout`,
  `verified-commit-pending`, bare `pending` in an explicit status/closeout field,
  their plain-language pending commit/closeout forms, `待提交`, and `待收口`.
  Inspect reports the exact canonical file, line, task, alias when applicable,
  recorded state, and expected `finalized` state.
- Only explicit `coderail:current-truth` markers are machine-rewritten. Project
  prose remains human-owned: ordinary `done` reopens before its exact commit,
  `done --no-commit` refuses to freeze stale prose into its exact snapshot, and
  `done --resume` preserves `verified-commit-pending` when a new assertion
  appears, until every stale current-authority assertion is repaired. No path
  may report consistency pass or `Done` while such residue exists.

## ADR-023 Lifecycle authority is separate from prose and generated projections

Status: accepted
Date: 2026-08-07
Task: T-060
Supersedes: ADR-022 prose-blocking policy; preserves its exact-marker policy

- One machine authority owns each lifecycle fact: hot TASKS markers own current
  task ownership, `pending_close.json` owns interrupted verified closeout, the
  PROGRESS plus verify-TRACE pair owns finalized history, and Git refs own
  commit/push facts. HANDOFF, CODERAIL_STATUS, README, and task/review prose are
  projections and cannot overrule those sources.
- Exact `coderail:current-truth` marker conflicts remain
  `control_plane_conflict` errors that block activation. Bounded handwritten
  lifecycle assertions are now `projection_staleness` warnings with
  `blocks=none`; they never block formulation, closeout, or recommendation and
  never cause an automatic follow-up GOV Coordinate.
- Every normalized diagnostic exposes severity, category, blocking stage,
  evidence, and recommended action. Severity is not a proxy for a global stop;
  the explicit blocking stage is the decision authority.
- Ordinary `inspect`, `inspect --no-write`, `check`, Drive, and recommendation
  are read-only, including the Git index. Generated HANDOFF/STATUS updates use
  explicit `sync-projections` preview/apply. `inspect --write` is a deprecated
  explicit compatibility path, not the default.
- Recommendation-only Drive returns `RECOMMEND` with
  `execution_authorized=false`; `ADVANCE` is reserved for an explicitly
  configured activation mode. Formulation and recommendation never register or
  activate a task.
- Owner-facing status leads with explicit product capability, limitation, next
  gap, active task, and human gates. Missing Delivery Contract evidence stays
  `not_assessed`; technical lifecycle receipts remain in the appendix.
