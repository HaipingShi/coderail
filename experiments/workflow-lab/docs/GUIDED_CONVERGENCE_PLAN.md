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

### WP2 - Add the internal framing primitive

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

### WP3 - Rewrite the grilling orchestrator

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

### WP4 - Add contract and scenario tests

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

### WP5 - Run comparative evaluation

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

The next implementation slice is WP1 plus the WP4 fixture skeleton:

1. Add the Contract Draft and Draft Delta fixtures.
2. Encode quick/guided route expectations for the first four scenarios.
3. Encode readiness and promotion invariants.
4. Run the existing lab suite unchanged.
5. Only then change or add skill prompts.

This slice is documentation and test-fixture work inside the isolated lab on a
feature branch. It does not require ending CodeRail's stabilization freeze or
changing the shipping runtime.
