# Coordinate Contract Drafts

Use this file for proposed or accepted Coordinate Contract Drafts before they become active tasks in `docs/TASKS.md`.

Copy this block and rename the heading to `## CD-001 Short title` when creating a real draft.

```markdown
\## CD-001 Short title

Status: proposed
Created at:
Source: user | agent | handoff | trace | issue
Trace:

### Coordinate Contract Draft

G — Goal:
- North Star:
- Outcome served:
- Why now:

T — Task:
- Task ID:
- Exact task:
- What this task must not become:

S — Scope:
- Allowed:
  -
- Forbidden:
  - none

V — Verify:
- TDD mode: required | optional | waived
- Red check:
- Green check:
- Refactor check:
- Regression check:
- CI check:
- Waiver reason:
- Harness:
  -
- Manual acceptance:
  -

X — Stop:
- forbidden files needed
- harness fails twice with unclear root cause

P — Persist:
- TASKS:
- HANDOFF:
- DECISIONS:
- LESSONS:
- ASSETS:
- TRACE:

Decision:
- proceed | revise | ask user | split task | backlog

Notes:
-
```

## CD-002 Doctor marker compatibility

Status: accepted
Created at: 2026-07-12
Source: user
Trace: pending T-002 verification trace

### Coordinate Contract Draft

G — Goal:
- North Star: keep CodeRail executable and diagnosable across launcher migrations
- Outcome served: Doctor reports current generated Inspect state without false warnings
- Why now: downstream timeBuilderEngin sync must start from a healthy source release

T — Task:
- Task ID: T-002
- Exact task: accept both the legacy inspect script marker and the repo-local launcher marker in Doctor
- What this task must not become: a broader Doctor refactor or target-project sync implementation

S — Scope:
- Allowed:
  - scripts/doctor.py
  - tests/test_structure.py
  - docs/NORTH_STAR.md
  - docs/TASKS.md
  - docs/CONTRACTS.md
  - docs/TRACELOG.jsonl
  - docs/TRACE_INDEX.md
  - docs/CODERAIL_STATUS.md
  - docs/HANDOFF.md
- Forbidden:
  - package.json
  - lockfiles
  - timeBuilderEngin files

V — Verify:
- TDD mode: required
- Red check: new and legacy marker compatibility test fails before implementation
- Green check: both markers pass and unrelated text remains rejected
- Refactor check: marker parsing stays localized in Doctor
- Regression check: npm test
- CI check: npm run ci
- Harness:
  - python scripts/doctor.py --target project-template
  - python scripts/drift_check.py --target project-template

X — Stop:
- compatibility requires changing Inspect output contract
- validation reveals unrelated source drift

P — Persist:
- TASKS: T-002 completion
- HANDOFF: H0 unless sync becomes blocked
- DECISIONS: none
- LESSONS: none
- ASSETS: none
- TRACE: T-002 verify event

Decision: proceed

Notes:
- Downstream sync remains a separate target-repository boundary.

## CD-003 Task Switch Gate

Status: accepted
Created at: 2026-07-14
Source: user
Trace: user authorization on 2026-07-15; pending T-003 implementation trace

### Coordinate Contract Draft

G — Goal:
- North Star: make CodeRail executable and resumable without dangling or ambiguous task ownership
- Outcome served: every task switch leaves exactly one owner for current worktree changes and never creates multiple active tasks by force
- Why now: `stage-complete` intentionally keeps a task active, while `start --force` can bypass that ownership boundary instead of completing a formal switch

T — Task:
- Task ID: T-003
- Exact task: add one Task Switch Gate shared by `start`, `next --go`, and an explicit `switch` flow; introduce `[p] paused` as a non-active resumable state and persist dirty-baseline ownership evidence
- What this task must not become: a hosted scheduler, automatic branch manager, automatic push workflow, or rewrite of Done/Drive semantics unrelated to switching

S — Scope:
- Allowed:
  - scripts/coderail.py
  - scripts/task_switch.py
  - scripts/closeout_check.py
  - scripts/coordinate_check.py
  - scripts/done_gate.py
  - scripts/doctor.py
  - scripts/finish_task.py
  - scripts/drive_check.py
  - scripts/inspect_state.py
  - tests/test_structure.py
  - README.md
  - project-template/AGENTS.md
  - project-template/docs/TASKS.md
  - project-template/docs/HANDOFF.md
  - project-template/docs/CODERAIL_STATUS.md
  - references/CLOSEOUT_GATE.md
  - docs/NORTH_STAR.md
  - docs/TASKS.md
  - docs/CONTRACTS.md
  - docs/DECISIONS.md
  - docs/HANDOFF.md
  - docs/HARNESS_SPEC.md
  - docs/PROGRESS.md
  - docs/CODERAIL_STATUS.md
  - docs/TRACELOG.jsonl
  - docs/TRACE_INDEX.md
  - .coderail/tasks.json
- Forbidden:
  - package.json
  - package-lock.json
  - automatic `git push`
  - implicit commit of files not owned by the closing task
  - more than one `[~]` or `[!]` task after a successful gate transition

V — Verify:
- TDD mode: required
- Red check: lifecycle tests prove current `start --force` permits ambiguous ownership and current `stage-complete` cannot transition to a non-active resumable state
- Green check: all switch-matrix tests pass with exactly one active owner or an explicit stopped state
- Refactor check: state classification, fingerprinting, and transition decisions live in one switch module used by all three entry paths
- Regression check: `python3 tests/test_structure.py`
- CI check: `npm test` and `npm run ci`
- Harness:
  - accepted current task runs `done`, creates its safe commit, then starts the requested task
  - verified checkpoint creates a `stage-complete` commit, marks the original task `[p]`, records its resume anchor, then starts the requested task
  - uncommittable current work writes H3 and refuses to activate another task until the user chooses `continue-current` or explicit `dirty-fork`
  - closed-task uncommitted ownership blocks ordinary `start` and `next --go`, prints exact paths, and requires repair commit or explicit dirty-fork waiver
  - unrelated dirty files present before task start are stored as normalized path, porcelain state, and SHA-256 fingerprint; unchanged baseline files are excluded from new-task attribution
  - a dirty-fork waiver records the carried baseline and switch trace but still leaves at most one active task
  - `--force` cannot create multiple active tasks
  - no switch or closeout path runs `git push`
- Manual acceptance:
  - CLI wording makes the safe next action explicit without requiring users to understand internal state files

X — Stop:
- an implementation would need to commit unrelated baseline files
- fingerprinting would persist file contents or secrets instead of hashes and paths
- a transition can leave multiple active tasks
- a failed switch cannot provide a deterministic recovery command
- compatibility requires changing package or lock files

P — Persist:
- TASKS: add and complete T-003; add `[p] paused` to the status legend
- HANDOFF: record H3 only for the uncommittable/dirty-fork decision boundary
- DECISIONS: record the single-active invariant, pause semantics, monotonic switch transaction, and push separation
- LESSONS: record only if implementation exposes a reusable failure pattern
- ASSETS: none
- TRACE: append contract, switch, verify, pause/resume, and closeout links

### Switch decision matrix

1. Current task accepted: run `done --result done`; require safe auto-commit to be committed or a truthful no-change result; then start the requested task.
2. Current task has a verified checkpoint: run `done --result stage-complete`; require checkpoint commit; transition the original task to `[p]` with `stage-complete` as its pause reason; then start the requested task.
3. Current work is not safely committable: do not commit implementation and do not activate another task; write H3 and require `continue-current` or explicit `dirty-fork`.
4. A closed task still owns uncommitted paths: block ordinary `start` and `next --go`, print exact repair paths; only explicit `dirty-fork` may carry them as the next task's baseline.
5. Unrelated changes already exist before a task starts: record path, porcelain state, and SHA-256 fingerprint; do not force a commit and do not attribute an unchanged baseline path to the new task.
6. Auto-commit is never auto-push. Push remains a separate user-authorized action.

### State and transaction semantics

- `[~]` and `[!]` remain active ownership states; `[p]` is paused, non-active, and resumable only by an explicit switch/resume action.
- `deferred` remains a task result or pause reason, not a second paused status.
- `--force` may not bypass the single-active invariant. An explicit dirty-fork waiver carries a fingerprinted baseline; it does not authorize broad staging.
- The switch transaction is monotonic: preflight, close/checkpoint when safe, persist pause/handoff/trace, snapshot the incoming baseline, activate the destination. A later failure never rolls back a successful commit; it stops with zero active destinations and a deterministic recovery command.
- Baseline metadata lives in `.coderail/tasks.json`; it stores hashes and Git states, never file contents.

Decision: proceed

Notes:
- Accepted public shape: `coderail switch "new task"` for an automatic safe switch, plus explicit `--continue-current` and `--dirty-fork` decisions when the gate stops.
