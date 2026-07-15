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
