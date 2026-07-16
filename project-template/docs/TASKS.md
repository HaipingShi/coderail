# Tasks

## Status legend

- `[ ]` todo
- `[~]` doing
- `[!]` blocked
- `[p]` paused (non-active; resume explicitly with `coderail switch --to <ID>`)
- `[x]` done (transient until the closeout ledger commits)
- `[f]` failed (transient until the closeout ledger commits)
- `[r]` reopened

Task result at closeout may be `done`, `stage-complete`, `blocked`, `failed`, or `deferred`. `stage-complete` stays `[~]` unless Task Switch Gate commits it and transitions the source to `[p]`.
Generated task coordinates declare `Rail: full | light` and
`Autonomy: allowed | human-gated` explicitly.

## Compact summary policy

TASKS is the hot ownership view and persists only active, queued, paused,
blocked, or reopened work. `coderail start` writes the full coordinate, so no
copyable task body lives here while idle. After a successful closeout ledger
commit, completed bodies leave TASKS; `docs/PROGRESS.md` plus
`docs/TRACELOG.jsonl` are the repository-tracked completed-history authority.
Done reports and `.coderail/tasks.json` are supplemental recovery detail only.
