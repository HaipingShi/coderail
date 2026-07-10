# CodeRail Drive Loop Design

Status: accepted for D1-D4 implementation
Owner: CodeRail
Date: 2026-07-10

## 1. Purpose

CodeRail Drive Loop adds goal-preserving initiative to the existing governance
rail. While the current North Star remains valid and work stays inside an
authorized Coordinate, the agent should continue through safe, verifiable work
instead of stopping for non-decision choices.

The design combines four layers without collapsing them:

```text
Codex Goal          keeps a durable objective active across turns
Codex harness       runs model -> tool -> observation iterations
CodeRail Drive      chooses continue, repair, advance, review, block, or finish
Direction Review    changes task, architecture, or strategy when evidence demands it
```

Drive is not goal generation. It is a deterministic default-to-continue policy
inside an existing goal, scope, verification contract, and stop boundary.

## 2. North Star

Outcome:
- An authorized long-running coding goal can make continuous, auditable progress
  without asking the user to resolve routine engineering choices.

Invariants:
- Drive never changes the North Star, expands S, or grants itself permissions.
- Drive does not execute a model or become a hosted workflow runtime.
- Every non-terminal decision names evidence and one next executable action.
- Human attention is reserved for decision-grade blockers.
- Repeated activity without measurable progress terminates as `EXHAUSTED`.

Non-goals:
- autonomous product strategy or self-generated goals;
- background daemon, scheduler, task server, or multi-agent orchestrator;
- automatic schema, dependency, public API, persistence, release, security,
  privacy, payment, or permission decisions;
- storing full chats, terminal logs, or generated run artifacts as project truth.

## 3. Control Model

```text
Goal / terminal condition
        |
        v
Select active or ready task
        |
        v
Execute -> observe harness -> classify evidence
        |                         |
        +-----------<-------------+
                    |
        Drive Decision + next action
```

The inner harness loop corrects implementation actions. Drive operates one level
above it: it decides whether the current task should continue, repair, advance,
or leave the execution loop. Direction Review remains the strategy-level outer
loop.

## 4. Drive Contract

`docs/NORTH_STAR.md` owns the durable Drive Contract:

```markdown
## Drive Contract

- Mode: manual | continuous
- Terminal condition:
- Progress signal:
- Retry budget: 3
- No-progress limit: 2
- Human gates:
```

`manual` is the backward-compatible default. Continuous Drive is available only
when the contract has a terminal condition and progress signal.

Each task adds:

```markdown
Autonomy: allowed | human-gated
```

Only an active task or a dependency-ready task with `Autonomy: allowed` may be
selected automatically.

## 5. Decision States

| State | Meaning | May stop a continuous goal? |
|---|---|---|
| `CONTINUE` | Current task is valid and still has an executable step. | no |
| `REPAIR` | Harness failed with a known, in-scope recovery path. | no |
| `ADVANCE` | Current checkpoint is complete and another task is ready. | no |
| `REVIEW_DIRECTION` | Evidence suggests repeated task, architecture, or strategy pressure. | yes, for review |
| `BLOCKED_DECISION` | Existing authority is insufficient for a decision-grade change. | yes |
| `COMPLETE` | The terminal condition is evidenced and no active/ready work remains. | yes |
| `EXHAUSTED` | Retry or no-progress budget is consumed. | yes |

`stage-complete` is a checkpoint rather than a stop. Because the task remains
`[~]`, Drive continues that task toward acceptance and does not activate a
second task. `ADVANCE` becomes valid only after the current task leaves active
state.

## 6. Decision Precedence

The deterministic evaluator applies this order:

1. `BLOCKED_DECISION` for explicit human-gated work, missing authority, forbidden
   scope, or high-risk change signals.
2. `REVIEW_DIRECTION` for repeated reopening, repeated scope expansion, or
   explicit direction-review trace evidence.
3. `EXHAUSTED` when retry/no-progress limits are reached.
4. `REPAIR` when the harness failed and a retry remains.
5. `CONTINUE` when an active autonomous task remains in progress, including a
   stage-complete task whose acceptance is not done.
6. `ADVANCE` when no active task remains and a ready autonomous task exists.
7. `COMPLETE` when the terminal condition is explicitly evidenced.
8. Otherwise `BLOCKED_DECISION`, because guessing a missing task or terminal
   condition would create new authority.

## 7. Decision-Grade Boundary

Routine actions that Drive may continue:
- tests, lint, type checks, builds, formatting, and deterministic generators;
- known-root-cause repair inside S;
- selecting the smallest reversible implementation matching repository patterns;
- syncing trace/status, exact task-scoped commit, and advancing to a ready task.

Decision-grade actions that must stop:
- changing G, S, North Star, terminal condition, or permissions;
- dependency, public API, schema, persistence, migration, release, security,
  privacy, payment, or external-side-effect decisions;
- conflicting project truth;
- repeated failure without a clear root cause;
- product-semantic choices between non-equivalent options.

## 8. Evidence and Data Lifecycle

Durable inputs:
- `docs/NORTH_STAR.md`: outcome, Drive Contract, terminal condition;
- `docs/TASKS.md`: status, dependency, priority, autonomy, Coordinate;
- `docs/HARNESS_SPEC.md`: progress and terminal harnesses;
- `docs/TRACELOG.jsonl`: attempts, verification, decisions, reopenings;
- `docs/DECISIONS.md`: accepted policy decisions.

Derived state:
- `docs/CODERAIL_STATUS.md`: current Drive Decision and next action;
- stdout/JSON from `scripts/drive_check.py`.

Run artifacts:
- `.coderail-runs/drive-observe/<timestamp>/` for D4 scenario output;
- never staged or treated as project truth.

## 9. D1-D4 Delivery Plan

### D1 - Drive Contract

Rail: light

Deliver:
- this design;
- `references/DRIVE_LOOP.md` runtime contract;
- Drive fields in North Star, task, harness, status, and metrics templates;
- blueprint links for the state and sequence diagrams.

Acceptance:
- default mode is manual;
- continuous mode requires terminal/progress evidence;
- stop and decision boundaries are explicit;
- no runtime or dependency is added.

### D2 - Deterministic Drive Decision

Rail: full

Deliver:
- `scripts/drive_check.py` with human and JSON output;
- scenario tests for all seven states and precedence;
- optional Drive section in `inspect_state.py`;
- doctor/init integration.

Acceptance:
- the same repository state always returns the same decision;
- every non-terminal state has one next executable action;
- ambiguous authority returns `BLOCKED_DECISION`;
- changed files are checked against the selected task's S;
- passing progress resets inferred retry and no-progress budgets;
- existing projects remain valid in manual mode.

### D3 - Codex Goal Bridge

Rail: full

Deliver:
- concise `skills/drive/SKILL.md`;
- a Goal Bridge prompt in the runtime reference and README;
- execution rule: run `drive_check`, then continue for `CONTINUE`, `REPAIR`, or
  `ADVANCE`; stop only on terminal/review states.

Acceptance:
- the skill does not claim to start or control the Codex runtime;
- the skill uses repository state rather than chat memory;
- the Goal prompt names objective, terminal condition, read-first assets,
  checkpoints, verification, and pause conditions.

### D4 - A/B Observation

Rail: full

Deliver:
- `scripts/drive_observe.py` with isolated fixtures;
- baseline policy versus Drive decision comparison;
- ignored JSON/Markdown reports containing decisions and metrics.

Metrics:
- unnecessary stops;
- autonomous task transitions;
- useful non-terminal decisions;
- unsafe decision crossings (must remain zero);
- no-progress termination coverage;
- decision agreement with scenario expectations.

Acceptance:
- run artifacts remain ignored;
- all scenarios are deterministic and offline;
- the report distinguishes safety from forward progress;
- D4 does not claim that fixtures prove real-world model performance.

## 10. Goal Bridge Contract

Codex Goal is the scheduling layer, not the source of project authority. A valid
Goal Bridge must instruct Codex to:

1. read North Star, TASKS, HARNESS_SPEC, and current status;
2. execute only autonomous tasks inside S;
3. run the task/progress harness at checkpoints;
4. run `drive_check.py` after each checkpoint;
5. continue immediately for `CONTINUE`, `REPAIR`, and `ADVANCE`;
6. invoke direction review for `REVIEW_DIRECTION`;
7. stop for `BLOCKED_DECISION`, `COMPLETE`, or `EXHAUSTED`;
8. never interpret persistence of the Goal as permission expansion.

## 11. Verification Strategy

Red:
- tests reference missing Drive templates and script;
- state scenarios fail before the evaluator exists.

Green:
- all Drive states and precedence rules pass;
- existing 23-test baseline remains green.

Regression:
- doctor, blueprint, coordinate, contract, TDD, init, inspect, and regression
  observation remain compatible;
- `git diff --check` passes;
- no package, lock, version, or manifest change is required for D1-D4.

## 12. Sources

- OpenAI, Follow a goal: https://learn.chatgpt.com/use-cases/follow-goals
- OpenAI, Unrolling the Codex agent loop: https://openai.com/index/unrolling-the-codex-agent-loop/
- OpenAI, Harness engineering: https://openai.com/index/harness-engineering/

## 13. D5 - Legacy Cutoff for Runtime State Inspect

Mature repositories may contain closed tasks that predate CodeRail and lack its
verification vocabulary. D5 adds an explicit document-order anchor in
`docs/NORTH_STAR.md`:

```markdown
## Legacy Cutoff

- Enforcement starts at: T-178
```

`inspect_state.py` keeps weak-V gaps before the anchor visible as historical
verification debt, but only the anchor and later tasks contribute closed-task
verification gaps to current status. Any doing/blocked task before the anchor
also remains in the current enforcement scope. A missing
anchor fails closed. No configured cutoff preserves the pre-D5 all-task
behavior. The cutoff changes classification only; it does not rewrite history,
grant autonomy, or weaken post-cutover verification.
