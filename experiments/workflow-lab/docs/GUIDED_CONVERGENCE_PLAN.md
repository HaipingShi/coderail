# Guided Convergence Experiment Plan

Status: proposed
Date: 2026-07-25
Depends on: `docs/GUIDED_CONVERGENCE_RATIONALE.md`
Target: `experiments/workflow-lab` on a feature branch only

## 1. Objective

Determine whether a novice-safe adaptation of grilling and domain modeling
improves CodeRail contract quality and reduces downstream correction cost
without adding kernel state, commands, hooks, required context, or a competing
source of truth.

The experiment tests this claim:

> Capability-aware framing, typed uncertainty, one high-impact question at a
> time, and delayed knowledge promotion will outperform both immediate
> implementation and expert-oriented relentless grilling on ambiguous or
> risky tasks, while a quick path avoids taxing clear tasks.

## 2. Fixed Constraints

- The CodeRail `main` branch remains under its stabilization freeze.
- Work occurs in `experiments/workflow-lab` on
  `feature/guided-convergence`.
- Skills may propose G/T/S/V/X/P but never write CodeRail internal state.
- Only the existing CodeRail CLI may activate or close a task.
- Skills never stage, commit, push, or install hooks.
- No LLM-dependent gate is added.
- No glossary, ADR, PRD, ticket store, or handoff becomes required context.
- Upstream-derived wording retains the existing pinned attribution and license.

## 3. Deliverables

The experiment should produce:

1. A model-invoked `coderail-frame` reasoning primitive.
2. A revised user-invoked `coderail-grill-contract`.
3. A compact live draft format using FACT, ASSUMPTION, DECISION, and UNKNOWN.
4. Quick-path and guided-path routing guidance.
5. Persistence promotion rules for glossary terms and ADR candidates.
6. Characterization tests for invocation, side effects, draft shape, and
   convergence behavior.
7. A scenario evaluation report comparing three workflows.
8. A final adopt, revise, or reject decision.

## 4. Work Packages

### WP0 - Freeze the design baseline

Actions:

- Add the rationale and this plan to the isolated in-repository lab.
- Link both from the lab README.
- Record the upstream commit and relevant source files.
- Preserve the current skill as the behavioral baseline in Git history or a
  fixture before rewriting it.

Acceptance:

- The rationale separates source facts, interpretations, and proposals.
- The plan contains explicit stop conditions.
- The main CodeRail worktree has no changes.

### WP1 - Define the draft protocol before prompts

Status: implemented in fixtures; pending comparative prompt work

Actions:

- Define a deterministic text fixture for a Contract Draft.
- Require each material item to carry one epistemic state.
- Define a Draft Delta that reports only what changed after an answer.
- Define readiness checks for G/T/S/V/X/P and blocking unknowns.
- Define promotion records for proposed glossary terms and ADR candidates.

Proposed draft shape:

```text
CONTRACT DRAFT

G - Goal
  [DECISION user] ...

T - Task
  [ASSUMPTION agent; falsify when ...] ...

S - Scope
  [FACT repo:path] ...

V - Verify
  [FACT command] ...

X - Stop
  [UNKNOWN blocking] ...

P - Persist
  [DECISION user] ...

READINESS
  ready: no
  blocking: X.1
  next-question-reason: answer changes task boundary
```

Acceptance:

- A reader can distinguish evidence, guesses, accepted choices, and deferrals.
- Readiness never uses a numeric confidence or entropy score.
- The format introduces no canonical store outside existing CodeRail records.

WP1 result:

- `fixtures/protocol.json` defines the protocol vocabulary and rules.
- `fixtures/contract-draft.md` and `fixtures/draft-delta.md` freeze the text
  forms.
- `fixtures/scenarios.json` encodes the first four routing cases.
- `fixtures/promotion-cases.json` encodes positive and negative glossary and
  ADR promotion cases.
- `tests/test_guided_convergence_protocol.py` derives readiness and promotion
  outcomes instead of trusting fixture declarations.

### WP2 - Add the internal framing primitive

Status: implemented and contract-tested

Actions:

- Create `skills/coderail-frame/SKILL.md`.
- Make it model-invoked.
- Have it identify candidate domains and rank only high-impact blind spots.
- Require repository investigation before questions.
- Require primary-source or experimental verification for unstable or
  high-risk technical claims.
- Prohibit dumping an exhaustive expert checklist on the user.
- Produce a proposed question or "quick path is sufficient"; do not mutate
  files or task state.

Acceptance:

- The skill passes the standard validator.
- It preserves every CodeRail authority marker used by the lab tests.
- It returns no user-facing question when repository evidence already resolves
  the issue.
- Its output labels domain lenses as candidates, never facts.

WP2 result:

- `skills/coderail-frame/SKILL.md` implements a read-only, model-invoked
  framing primitive.
- It investigates repository evidence before routing, removes resolved lenses,
  and emits either `user-facing question: none` or one complete question.
- It labels every domain lens `[CANDIDATE]`, types material claims with the WP1
  epistemic vocabulary, and avoids numeric proxy scores.
- Unstable or high-risk technical claims require primary-source evidence or a
  focused experiment before they can be treated as facts.
- `tests/test_skill_contracts.py` derives the required routes, states,
  coordinates, question fields, and initial focus cases from the frozen
  fixtures.

### WP3 - Rewrite the grilling orchestrator

Status: implemented and contract-tested

Actions:

- Compose `coderail-frame` into `coderail-grill-contract`.
- Add an explicit quick-path bypass.
- Ask exactly one outcome-level question at a time.
- Include recommendation, reason, impact, evidence, uncertainty, and
  reversibility.
- Accept "I do not know" as a valid answer and select a reversible technical
  default when authorized.
- Emit a Draft Delta after each answer.
- Stop at reversible-slice readiness.
- Delay glossary and ADR promotion until their evidence rules pass.

Acceptance:

- A simple bounded change reaches a draft without an interview.
- A risky ambiguous change cannot become ready while a blocking unknown is
  hidden.
- A novice is not asked to select unexplained architecture labels.
- No answer is silently promoted from ASSUMPTION to FACT or DECISION.
- Activation still requires explicit user confirmation and the public
  `coderail start` interface.

WP3 result:

- `coderail-grill-contract` invokes `$coderail-frame` as its internal framing
  step and routes reproduced regressions to `coderail-diagnose`.
- Quick results produce a typed draft without an interview; guided results
  expose exactly one complete outcome-level question.
- "I do not know" preserves epistemic honesty and permits only an authorized,
  reversible, agent-owned assumption.
- Every answer produces a change-only Draft Delta before readiness is
  recomputed.
- Readiness stops at a reversible slice, promotion remains delayed, and task
  activation still requires explicit confirmation through public `start`.

### WP4 - Add contract and scenario tests

Status: minimum matrix and static contracts implemented

Actions:

- Extend `tests/test_skill_contracts.py` for the new skill and invariants.
- Add static contract tests for required and forbidden wording.
- Add scenario fixtures with expected route, question focus, draft state, and
  readiness outcome.
- Test that the orchestration skill remains user-invoked and the framing
  primitive remains model-invoked.

Minimum scenario matrix:

| Scenario | User profile | Expected route |
|---|---|---|
| Rename a local button with an existing test | novice | quick |
| Add login with unclear audience and persistence | novice | guided |
| Add local-only file processing | novice | guided, privacy boundary first |
| Select a database for a throwaway prototype | novice | guided, reversible default |
| Change a public API with migration impact | expert | guided, terse technical form |
| Fix a reproduced regression | either | diagnosis, not grilling |
| Add a report export with clear acceptance | expert | quick |
| Resolve conflicting "account" meanings | either | guided, domain term proposed |

Acceptance:

- Static tests pass for every skill.
- Every fixture has one expected first question at most.
- At least one scenario rejects premature readiness.
- At least one scenario rejects premature glossary promotion.
- At least one scenario demonstrates an explicit deferred UNKNOWN.

WP4 result:

- `fixtures/scenarios.json` now covers all eight minimum cases.
- Contract scenarios contain at most one first question; reproduced regression
  has no contract route or draft and explicitly selects diagnosis.
- The suite derives typed-item validity, readiness, question shape, delayed
  promotion, and workflow routing from the fixtures.
- Static skill tests preserve model invocation for frame, explicit invocation
  for grilling, and CodeRail's no-side-effect authority boundary.

### WP5 - Run comparative evaluation

Status: wp5-v3 contract phase complete; implementation evidence pending

Compare:

```text
A: baseline CodeRail contract drafting
B: expert-oriented grilling with immediate documentation
C: Guided Convergence
```

Run at least 18 tasks:

- 6 clear, local, reversible tasks;
- 6 ambiguous product or cross-module tasks;
- 3 high-risk or persistent decisions;
- 3 domain-language conflicts.

Include both novice-style inputs and expert-style inputs. Keep repository
fixtures and model settings stable enough for a meaningful comparison.

Measure:

- turns before executable contract readiness;
- number of questions whose answers change G/T/S/V/X/P;
- user-visible technical choices requiring clarification;
- unsupported assumptions at activation;
- contract corrections after implementation begins;
- out-of-scope edits;
- first-pass `done` success;
- reopened tasks or post-close defects;
- glossary and ADR reversals;
- total interaction tokens;
- user interruption count;
- simple-task quick-path accuracy.

Interpretation:

- More front-loaded turns are acceptable only when they reduce later
  corrections or risk.
- A question is low-value if its answer changes no contract coordinate,
  evidence need, stop condition, or persistence decision.
- Documentation volume is not a success metric.

Acceptance threshold for a native-pack proposal:

- Guided Convergence reduces unsupported assumptions or post-start contract
  corrections by at least 25% on ambiguous/risky tasks versus baseline.
- At least 90% of clear tasks take the quick path.
- It creates no increase in out-of-scope edits or CodeRail closeout failures.
- It causes fewer premature glossary/ADR reversals than expert-oriented
  immediate documentation.
- Median human interruptions do not increase for clear tasks.

These thresholds authorize a proposal, not automatic integration.

WP5 frozen baseline:

- `evaluation/manifest.json` contains 18 tasks: 6 clear/local/reversible,
  6 ambiguous/cross-module, 3 high-risk/persistent, and 3 domain-language
  conflicts.
- `evaluation/workflows/A.md`, `B.md`, and `C.md` isolate the three treatments
  behind one response contract.
- `evaluation/rubric.json` defines independent observation rules for every
  planned metric and preserves the original adoption thresholds.
- `evaluation/trial-result.schema.json` separates raw model response references
  from adjudicated observations; missing implementation evidence stays null.
- `evaluation/freeze.json` pins all pretrial content hashes and the model,
  reasoning, sandbox, configuration, ordering, and blinding policy.
- `scripts/score_evaluation.py` aggregates only adjudicated result fields.

No trial result existed when the hashes were frozen. Any later edit to a
pretrial input creates a new protocol version instead of silently changing
`wp5-v1`.

WP5 preflight:

- The installed Codex CLI cannot run the frozen `gpt-5.6-terra` model; the
  service returned HTTP 400 before a subject response.
- `gpt-5.4` at medium reasoning passed a separate availability probe but was
  not substituted into `wp5-v1`.
- Preflight review found that `promotion_reversals` must allow null in
  contract-only trials, just like unobserved implementation fields.
- `evaluation/results/wp5-v1/preflight.jsonl` records both facts. Subject trial
  count remains zero and all frozen hashes remain intact.

WP5 v2 correction:

- `evaluation-v2/` preserves the v1 task packets, A/B/C workflow text, hidden
  oracles, and adoption thresholds.
- It pins the preflight-confirmed `gpt-5.4` model at medium reasoning.
- It allows null for every follow-through metric unavailable to a contract-only
  trial, including promotion reversals.
- It freezes subject output, blind judge, batching, failure, and blinding
  contracts before any v2 subject output exists.

WP5 v2 execution preflight:

- The first subject request reached `gpt-5.4` but structured-output validation
  returned HTTP 400 before generation.
- The service requires an explicit JSON type on properties constrained by a
  constant; the frozen v2 schema omitted it.
- No subject output was observed. The error event and zero-output record live
  under `evaluation-v2/results/`.
- A v3 protocol may add only the service-compatibility types, then re-freeze
  before retrying.

WP5 v3 correction:

- The 18 tasks, workflows, model, rubric semantics, blinding, and batching are
  unchanged from v2.
- Constant-constrained schema properties now also declare their JSON type.
- The frozen subject schema passed a `gpt-5.4` structured-output preflight.
- The first preflight generated a valid response but could not persist it
  because the local output directory did not exist; one identical-input retry,
  allowed by the run specification, persisted the result.
- At the v3 freeze and schema-preflight checkpoint, subject batch count was
  zero.

WP5 v3 contract-phase result:

- 12 subject and 4 blind-judge batches completed all 54 workflow-task cells.
- A/B/C all achieved 100% route correctness and zero clear-task
  interruptions.
- Aggregate unsupported assumptions were A=1, B=1, C=2.
- C matched A's turns and interruptions but used 4.39% more subject tokens.
- On ambiguous and high-risk tasks, C had one unsupported assumption while A
  and B had none, so the 25% reduction threshold did not pass.
- Implementation, closeout, post-close, and promotion-reversal evidence
  remains null. The only valid decision is
  `INSUFFICIENT_IMPLEMENTATION_EVIDENCE`, not ADOPT.

### WP6 - Review adoption

Produce one decision:

```text
ADOPT
  Evidence supports an optional native skill pack after the freeze is lifted.

REVISE
  The signal is promising but one or more boundaries need another lab cycle.

REJECT
  The process cost, anchoring risk, or documentation churn outweighs benefit.
```

An ADOPT recommendation must specify:

- exact skills and invocation policy;
- measured task classes where they apply;
- unchanged kernel and lifecycle boundaries;
- optional context-loading behavior;
- attribution;
- removal and rollback procedure;
- characterization tests required in the native pack.

## 5. Implementation Order

Execute in this order:

```text
WP0 rationale and plan
-> WP1 draft protocol
-> WP4 fixture skeletons
-> WP2 framing primitive
-> WP3 grilling rewrite
-> WP4 complete tests
-> WP5 evaluation
-> WP6 adoption review
```

Fixtures precede prompt implementation so the experiment does not merely
declare its own output successful.

## 6. Stop Conditions

Stop implementation and return to design if:

- the experiment needs a new CodeRail command, lifecycle state, or hard gate;
- it needs direct writes to `.coderail/tasks.json`;
- a smart hook is required for correctness;
- user expertise must be inferred from demographic or identity proxies;
- recommendations cannot expose their evidence and reversibility;
- the draft becomes a second canonical task store;
- simple tasks cannot bypass the interview reliably;
- tests can validate only the presence of prose, not observable scenario
  behavior;
- promotion rules still permit an unverified assumption to become canonical;
- evaluation benefit is anecdotal rather than measurable.

## 7. Immediate Next Slice

The next implementation slice is WP5 evaluation preparation and execution:

1. Freeze prompts and scoring rubrics for workflows A, B, and C.
2. Create the 18-task evaluation manifest from the required task classes.
3. Run blind, reproducible trials with stable repository fixtures and model
   settings.
4. Record turns, useful questions, unsupported assumptions, corrections,
   scope, closeout, tokens, and interruption counts.
5. Compare results against the adoption thresholds before making any native
   integration proposal.

This slice remains inside the isolated lab on a feature branch. It does not
require ending CodeRail's stabilization freeze or changing the shipping
runtime.
