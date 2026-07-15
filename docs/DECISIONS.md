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
