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

## CD-007 Owner-safe copy preflight

Status: accepted
Created at: 2026-08-08
Source: live T-061 closeout acceptance
Trace: T-062 executable Red

### Coordinate Contract Draft

G — Goal:
- A successful localized completion must communicate real product capability,
  not replace the entire result with a safe but uninformative fallback.

T — Task:
- Validate owner-facing product copy before verification or lifecycle mutation.
- Keep historical DELIVERIES rows append-only; do not rewrite T-061 evidence.

S — Scope:
- Allowed:
  - owner receipt validator, done preflight, executable Red, decision and harness docs
- Forbidden:
  - scope classifier, closeout transaction, Git, TRACE, task switch, downstream repositories

V — Verify:
- TDD mode: required
- Red check: unsafe localized copy completed and emitted the uninformative fallback.
- Green check: unsafe localized copy returns non-zero before verification or mutation.
- Unsafe English, identifiers, paths, or governance wording returns non-zero,
  leaves the task active, leaves Git HEAD unchanged, and appends no delivery fact.
- Valid Chinese product copy completes and renders a useful bounded receipt.

X — Stop:
- stop if preflight requires changing lifecycle, scope, Git, TRACE, or downstream files

P — Persist:
- TASKS: record T-062 Red/Green and completion
- DECISIONS: record the pre-closeout audience-input boundary
- TRACE: append normal task evidence only

Decision:
- proceed

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
## CD-004 Closeout Convergence

Status: accepted
Task: T-007 through T-009

### Coordinate Contract Draft

G — Goal:
- North Star: NS-001
- Outcome served: preserve the three-command product while making closeout facts and success authority converge

T — Task:
- Task ID: T-007 through T-009
- Exact task: characterize closeout behavior, unify repository facts, then make FINALIZED the only success state
- What this task must not become: a new public lifecycle or an excuse to weaken inspect

S — Scope:
- Allowed:
  - scripts/coderail.py
  - scripts/closeout_transaction.py
  - scripts/repository_state.py
  - scripts/finish_task.py
  - scripts/closeout_check.py
  - scripts/inspect_state.py
  - scripts/task_switch.py
  - tests/test_closeout.py
  - docs/CLOSEOUT_CONVERGENCE.md
- Forbidden:
  - new public commands or lifecycle states
  - automatic push
  - package or release changes

V — Verify:
- TDD mode required: preserve characterization before changing authority
- Red: expose duplicated facts or intermediate success through the existing closeout scenarios
- Green: repository facts are shared and only FINALIZED can render Done
- Refactor: keep public behavior stable while deleting duplicate internal classifiers
- Regression: `python tests/test_closeout.py`
- CI: `npm test`

X — Stop:
- stop if compatibility requires a new public command, task schema, security policy, or push behavior

P — Persist:
- CONTRACTS, DECISIONS, HARNESS_SPEC, TASKS, and TRACE

Decision: proceed

- Authorized outcome: preserve the three-command product while reducing closeout to one snapshot, classifier, and success authority.
- Specification: `docs/CLOSEOUT_CONVERGENCE.md`.
- Migration order: characterize first, unify facts second, unify authority third.
- Human gate: any public command, task schema, persistence, security, or push-policy change.
- Stop: do not add gates or weaken inspect to make migration tests pass.

## CD-005 Lifecycle Truth, Projection Debt, and Formulation Safety

Status: accepted
Task: T-060 (display id `GOV-LIFECYCLE-SSOT`)

### Coordinate Contract Draft

G — Goal:
- Preserve CodeRail's scope, verification, closeout, commit, and human-activation
  gates while preventing stale lifecycle prose from blocking product formulation.

T — Task:
- Separate control-plane truth, product truth, generated projections, and the
  append-only historical ledger.
- Give every diagnostic an explicit severity, category, blocking stage,
  evidence, and recommended action.
- Make ordinary `inspect` and `check` read-only and provide an explicit,
  previewable `sync-projections` write path.
- Keep formulation and recommendation read-only; only explicit lifecycle
  commands may register or activate a Coordinate.

S — Scope:
- Allowed: the T-060 task record is the exact file authority.
- Forbidden: package/release metadata, dependencies, automatic push, historical
  TRACE/PROGRESS rewriting, automatic Coordinate creation, and scope weakening.

V — Verify:
- TDD mode: required.
- Red A: a finalized task plus stale README/HANDOFF commit prose reports
  `projection_staleness` with `severity=warning`, `blocks=none`, and
  `blocks.formulation=false`; formulation/recommendation remains available and
  no GOV Coordinate is created.
- Red B: multiple live owners or an explicit lifecycle marker conflicting with
  live state reports `control_plane_conflict` and blocks activation/execution.
- Red C: ordinary `inspect`, `inspect --no-write`, `check`, Drive, and
  recommendation preserve a byte-for-byte target tree and do not change Git
  HEAD or active-task count.
- Red D: `sync-projections` previews by default and writes only after an explicit
  apply flag; the report identifies every changed generated projection.
- Green: focused suites and the structure suite pass, followed by `done`.

X — Stop:
- A fix would weaken forbidden scope, verification, protected-baseline, exact
  commit, or publication authorization.
- A migration would require rewriting old TRACELOG/PROGRESS records.
- A read-only command would need to create a Coordinate or modify lifecycle
  state.
- Product capability would need to be inferred from commit metadata when no
  Delivery Contract evidence exists.

P — Persist:
- CONTRACTS and DECISIONS record the authority and compatibility model.
- HARNESS_SPEC records the executable Red/Green matrix.
- README/references/diagrams describe the public behavior.
- TASKS and TRACE retain the ordinary CodeRail task evidence.

### Authority map

| Fact | Machine authority | Non-authoritative surfaces |
|---|---|---|
| active / paused / queued ownership | hot status markers in `TASKS.md` | README, HANDOFF prose, generated status |
| interrupted closeout | `.coderail/pending_close.json` while present | HANDOFF prose, generated status |
| finalized history | durable PROGRESS entry plus verify TRACE fact | old task/review/handoff prose |
| local commit | Git object and current ref | receipt prose and hashes copied into docs |
| pushed state | compared local and remote Git refs | README/HANDOFF statements |
| product capability and gap | explicit Delivery Contract/product evidence | commit title or lifecycle state |

### Diagnostic policy

| Condition | Severity | Category | Blocks |
|---|---|---|---|
| stale handwritten lifecycle prose | warning | projection_staleness | none |
| stale generated snapshot | warning | projection_staleness | none |
| multiple live owners or live/marker conflict | error | control_plane_conflict | activation |
| forbidden/outside task delta | error | scope_authorization | execution |
| failed verification or closeout transaction | error | closeout_integrity | closeout |
| materially unsupported safety-relevant product claim | error | product_evidence_conflict | delivery |

Decision: proceed

Notes:
- The repository owner's 2026-08-07 request explicitly accepted this design
  boundary and required executable Red before production changes.
- `inspect --write` may remain temporarily as an explicit deprecated compatibility
  path, but ordinary `inspect` changes to read-only immediately.
- Projection debt is batchable maintenance debt. It does not automatically
  recommend or register another GOV Coordinate.

## CD-006 Owner Communication and Agent Blackboard

Status: accepted
Task: T-061 (display id `OWNER-COMMS-001`)

### Coordinate Contract Draft

G — Goal:
- Make successful closeout directly decodable by the project owner without
  discarding the exact governance evidence required by agents.

T — Task:
- Introduce one normalized `CloseoutFacts` value after verification.
- Persist product delivery facts in an append-only tracked ledger before hot
  TASKS bodies are compacted.
- Render a localized, bounded Owner Receipt separately from the Agent
  Blackboard and the detailed Technical Report.
- Define Inspect and `CODERAIL_STATUS.md` as agent-facing projections; they must
  not infer verified capability from NORTH_STAR goal prose.

S — Scope:
- Allowed: the T-061 task record is the exact file authority.
- Forbidden: scope policy, `closeout_transaction`, repository/Git classification,
  task switching, TRACE authority, dependencies, release metadata, automatic
  activation, push, tag, release, and downstream A/B execution.

V — Verify:
- Red A: a `zh-CN` Owner Receipt rejects or omits unannotated English, task ids,
  paths, and governance vocabulary.
- Red B: Owner Receipt contains three to six owner-facing sentences.
- Red C: the same closeout keeps exact governance references available in the
  Agent Blackboard and Technical Report while hiding them from the owner view.
- Red D: product delivery facts survive TASKS compaction and a fresh clone.
- Red E: Inspect is explicitly agent-facing and never labels NORTH_STAR-only
  prose as verified product capability.
- Green: focused delivery/inspect/closeout/lifecycle/static suites and the full
  structure suite pass without changes to forbidden kernel files.

X — Stop:
- Localization would require inventing or machine-translating unauthored product
  claims.
- Blackboard would become lifecycle authority rather than a projection.
- Durable delivery facts would require rewriting valid TRACE/PROGRESS history.
- The implementation would change scope, Git, closeout-transaction, task-switch,
  or publication authority.

P — Persist:
- `docs/DELIVERIES.jsonl` stores append-only product delivery facts and technical
  receipt snapshots; it does not own task lifecycle.
- `docs/CODERAIL_STATUS.md` is the generated Agent Blackboard.
- `.coderail/reports/` keeps detailed local evidence.
- Owner Receipt is a localized projection over the same `CloseoutFacts`.

Decision: proceed

Notes:
- This is a product communication capability, not a recursive governance repair.
- The owner's 2026-08-08 direction authorizes Red/Green in the source repository
  but does not authorize downstream A/B, push, tag, or release.
- Compatibility may remain explicit during migration, but the default owner
  surface must not indefinitely retain the old seven-section report.
