# Drive Loop

Drive Loop gives an agent goal-preserving initiative inside an authorized
CodeRail Coordinate. It computes whether work should continue, repair, advance,
leave the execution loop for review, block for a decision, or finish.

It is not a model runtime, scheduler, or source of new authority. Codex Goal may
keep a run active across turns; CodeRail Drive decides the safe next project
state from repository evidence.

## Required contract

Continuous Drive requires `docs/NORTH_STAR.md` to contain:

```markdown
## Drive Contract

- Mode: continuous
- Terminal condition: <verifiable project end state>
- Progress signal: <measurable movement>
- Retry budget: 3
- No-progress limit: 2
- Human gates: <decision checkpoints or none>
```

Tasks eligible for automatic selection must contain:

```markdown
Autonomy: allowed
```

Missing terminal or progress evidence makes continuous execution a
`BLOCKED_DECISION`; Drive must not invent it.

## Decisions

| Decision | Required agent behavior |
|---|---|
| `CONTINUE` | Execute the named next action inside the active task. |
| `REPAIR` | Apply the known in-scope repair and rerun the harness. |
| `ADVANCE` | Activate the named ready task and start its first checkpoint. |
| `REVIEW_DIRECTION` | Run direction review before more implementation. |
| `BLOCKED_DECISION` | Ask only for the named decision-grade authority. |
| `COMPLETE` | Close out because terminal evidence is present. |
| `EXHAUSTED` | Close out with failure evidence and the consumed budget. |

Only the final four states may return control in Continuous Drive. A Direction
Review may produce a new authorized contract; it does not silently resume under
changed assumptions.

## Precedence

Apply the first matching rule:

1. explicit human gate, forbidden scope, or decision-grade change -> `BLOCKED_DECISION`;
2. repeated reopen/scope pressure or explicit review signal -> `REVIEW_DIRECTION`;
3. consumed retry/no-progress budget -> `EXHAUSTED`;
4. failed harness with retry remaining -> `REPAIR`;
5. active autonomous task -> `CONTINUE`;
6. ready autonomous task -> `ADVANCE`;
7. terminal evidence with no active/ready work -> `COMPLETE`;
8. otherwise -> `BLOCKED_DECISION`.

Decision-grade changes include Goal, S, dependency, public API, schema,
persistence, migration, release, security, privacy, payment, permissions, and
irreversible external side effects.

## Evidence lifecycle

- Durable truth: NORTH_STAR, TASKS, HARNESS_SPEC, TRACELOG, DECISIONS.
- Derived state: CODERAIL_STATUS and `drive_check.py` output.
- Run artifacts: `.coderail-runs/drive-observe/`; never stage them.

Do not save full chat logs or terminal logs in project truth. Persist user
corrections as concise intent/decision trace events when they must affect future
Drive decisions.

## Commands

Human report:

```bash
python3 scripts/drive_check.py --target .
```

Machine-readable report:

```bash
python3 scripts/drive_check.py --target . --json
```

Runtime evidence may be supplied for one checkpoint:

```bash
python3 scripts/drive_check.py --target . \
  --harness-result failed \
  --retry-count 1 \
  --no-progress-count 0 \
  --failure-known
```

By default the evaluator checks every current Git change against the selected
task's S. In a pre-existing dirty multi-agent worktree, pass an exact
comma-separated task delta with `--changed-files`; unrelated or forbidden files
must remain excluded from the task and visible in the closeout classification.
Passing verification or an explicit progress event resets the inferred retry
and no-progress counters for the next checkpoint.

## Codex Goal Bridge

Use this shape when Codex Goal is available:

```text
/goal Advance the current CodeRail North Star slice until its terminal condition is verified.

Read AGENTS.md, docs/NORTH_STAR.md, docs/TASKS.md,
docs/HARNESS_SPEC.md, and docs/CODERAIL_STATUS.md first.
Work only on tasks marked Autonomy: allowed and only inside S.
At each checkpoint run the progress/task harness, then drive_check.py.
Continue immediately for CONTINUE, REPAIR, and ADVANCE.
Run direction review for REVIEW_DIRECTION.
Stop only for BLOCKED_DECISION, COMPLETE, or EXHAUSTED.
Goal persistence never grants permission to change G, S, schema, dependencies,
public APIs, persistence, security/privacy/payment policy, or external state.
```

For the full design, see `docs/DRIVE_LOOP_DESIGN.md` in the CodeRail source
repository.
