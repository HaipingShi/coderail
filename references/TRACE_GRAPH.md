# Evidence-Aware Trace Graph

K7 rule: no meaningful action without a trace link.

CodeRail uses a small relationship graph, not a graph database. It has three
strictly separated evidence classes:

| Class | Meaning | Authority |
|---|---|---|
| `fact` | Directly proven by repository state, a lifecycle transition, Git, or a verification result. | May be registered automatically. |
| `decision` | An important relationship deliberately accepted by an operator, user, or cited project decision. | Must be registered explicitly with evidence or confirmation. |
| `candidate` | A model or person suspects a relationship but cannot yet prove it. | No execution authority; excluded from the formal graph. |

## Sources Of Truth

- `docs/TRACELOG.jsonl`: append-only lifecycle, verification, and decision events.
- Git commit trailers and diffs: immutable commit, task, verification, and file facts.
- `.coderail/tasks.json`: current task dependency state.
- `docs/TRACE_CANDIDATES.jsonl`: append-only candidate proposals and resolutions.
- `docs/TRACE_INDEX.md`: generated human index; never the canonical source.

Git facts use trailers in the same exact task-scoped commit:

```text
CodeRail-Task: T-046
CodeRail-Verified-By: TR-...
```

The commit diff proves which files changed. Queries join the trailers, diff,
and verification events into formal edges. This preserves the single-snapshot
closeout invariant; CodeRail does not create a second commit merely to record
the first commit's hash.

## Automatic Fact Edges

`start`, activation through `switch`/`next`, verification, and `done` produce
only relationships available from deterministic state:

```text
task --serves--> north star
verify event --validates--> task
commit --implements--> task
commit --modifies--> file
commit --validated_by--> verify event
activation --follows--> previous task     # temporal order only
```

An allowed scope is not a `modifies` fact. A planned test is not a
`validated_by` fact. Those edges appear only after Git or the harness proves
them.

## Explicit Decision Edges

Important semantic relationships are registered deliberately:

```bash
coderail link T-046 depends_on T-045 \
  --reason "uses the accepted introduction contract" \
  --evidence "docs/CODERAIL_FOR_VIBE_CODERS_ZH.md"
```

`--confirmed-by` may replace `--evidence` when the relationship is a genuine
product or governance choice. A decision edge without either is refused.

Supported task relations:

- `depends_on`: this task requires the target task;
- `blocks`: the target cannot proceed until this task completes;
- `supersedes`: this task deliberately replaces the target.

CodeRail rejects self references, missing task references, and dependency
cycles. Dependency readiness is checked before `start`, `switch --to`, or
`next --go` activates work.

## Candidate Boundary

Uncertain model suggestions do not enter `TRACELOG`:

```bash
coderail candidate add T-046 depends_on T-045 \
  --reason "the model suspects an unstated dependency"
coderail candidate list
```

Promotion requires evidence or explicit confirmation:

```bash
coderail candidate promote CAND-... --evidence "docs/DECISIONS.md#..."
coderail candidate reject CAND-... --reason "repository evidence contradicts it"
```

Candidate history remains append-only after promotion or rejection. Promotion
creates a separate formal `decision` event containing its basis.

## Ordinary-Language Queries

```bash
coderail why T-046
coderail impact docs/BLUEPRINTS.md
coderail graph T-046
```

Queries report the task's goal, North Star contribution, modified files,
implementation commits, verification evidence, dependencies, blockers,
accepted decisions, and a separately labelled candidate count. They do not
dump raw adjacency data or count candidates as facts.

## Formal Edge Types

`serves`, `derived_from`, `implements`, `implemented_by`, `modifies`,
`validated_by`, `validates`, `depends_on`, `supersedes`, `blocks`,
`relates_to`, and `follows`.

Do not store full chat logs, full terminal logs, full Git diffs, secrets, or
large artifacts in trace events. Store compact references to durable evidence.
