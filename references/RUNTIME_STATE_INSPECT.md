# Runtime State Inspect

Runtime State Inspect is CodeRail's repo-local status surface.
It answers: where is the project now, what is active, what is blocked, and what is safe to do next?

It deliberately avoids MCP runtime, web preview, graph database, or background execution. Lifecycle facts use one machine authority per fact:

- hot `TASKS.md` markers own active, queued, paused, blocked, and reopened work;
- `.coderail/pending_close.json` owns an interrupted verified closeout;
- PROGRESS plus verify TRACE facts own finalized history;
- local and remote Git refs own commit and pushed state;
- tracked DELIVERIES facts preserve verified product delivery claims.

`HANDOFF.md`, `CODERAIL_STATUS.md`, README prose, task/review prose, and
current-truth prose are projections. They do not overrule those authorities.
TRACELOG and PROGRESS are historical ledgers: old `active` or pending wording is
preserved and is never reclassified as current state.

## Inspect output

`inspect_state.py` prints the Agent Blackboard. It does not write by default and
is not intended as owner-facing product copy:

- Current North Star
- Latest Delivery Fact reference (never the product wording)
- Legacy Cutoff
- Active Coordinate
- Active Tasks
- Draft Contracts
- Verification Gaps
- Historical Verification Debt
- Trace Gaps
- Execution Decision
- Recommendation Decision and evidence
- Handoff State
- Recommended Next Action
- Auto Commit

The separate owner surface reads the latest durable Delivery fact and performs
no writes:

```bash
python .coderail/coderail.py owner-summary --locale zh-CN
```

It does not include active task state, report paths, task IDs, exact commands,
commits, or safe-file lists. Inspect does not infer product capability from
NORTH_STAR goals, recommendations, Git history, or task finalization.

Every normalized diagnostic contains:

```text
severity: info | warning | error
category: stable machine category
blocks: none | formulation | activation | execution | closeout | delivery
evidence: exact repository observation
recommended_action: bounded recovery or maintenance action
```

The output also renders a blocking matrix. Handwritten lifecycle drift is a
`projection_staleness` warning with `blocks=none`; a conflicting exact machine
marker is a `control_plane_conflict` that blocks activation. Formulation remains
available in both cases and never activates work.

## Read and write commands

```bash
python .coderail/coderail.py inspect                   # read-only
python .coderail/coderail.py inspect --no-write        # compatibility spelling, read-only
python .coderail/coderail.py check                     # read-only gate report
python .coderail/coderail.py sync-projections          # preview, read-only
python .coderail/coderail.py sync-projections --apply  # explicit generated writes
```

`inspect --write` remains a deprecated explicit compatibility path during the
migration window and points callers to `sync-projections --apply`. Ordinary
`inspect` no longer inherits the old implicit-write behavior.

## Relationship to doctor

`doctor.py` checks governance health.
`inspect_state.py` shows the current runtime state.

Doctor is for installation and compliance gaps.
Inspect is for agent continuation. `owner-summary` is for owner communication.

Inspect keeps execution permission separate from recommendation autonomy. A
manual or human-gated execution result may therefore coexist with a read-only
continuation recommendation. Only pending draft statuses are described as
active; accepted, completed, rejected, and backlogged drafts remain visible but
do not block continuation audit.

## Legacy cutoff for mature repositories

When CodeRail is adopted after a repository already has task history, configure
the first post-cutover task by document order:

```markdown
## Legacy Cutoff

- Enforcement starts at: T-178
```

Tasks before that anchor remain visible under `Historical Verification Debt`,
but their weak verification evidence does not make the current status blocked.
The anchor and every task after it remain enforced. A doing or blocked task
before the anchor is also treated as current. If the configured anchor is not
found, Inspect fails closed. Without this section, all tasks remain enforced for
backward compatibility.
