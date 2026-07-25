# CodeRail Workflow Lab

An isolated, non-shipping experiment for evaluating selected ideas from Matt
Pocock's agent skills against CodeRail's deterministic task and closeout model.

The experiment is versioned in the CodeRail repository on a feature branch so
its evolution can be reviewed and reverted normally. It is isolated under
`experiments/workflow-lab` and adds no CodeRail command, hook, lifecycle state,
required context file, or issue tracker. Removing this directory removes the
experiment; merging it does not imply enabling or shipping its skills.

## Design records

- `docs/GUIDED_CONVERGENCE_RATIONALE.md` records the reasoning for adapting
  expert-oriented grilling and domain modeling to novice vibe-coding users.
- `docs/GUIDED_CONVERGENCE_PLAN.md` defines the staged implementation,
  evaluation thresholds, and stop conditions for the next lab iteration.

The design calls the adaptation **Guided Convergence**. Its target is readiness
for the next bounded, verifiable, reversible slice, not an exhaustive interview
or immediate promotion of conversational answers into canonical documentation.

## Skills

- `coderail-frame`: model-invoked, read-only framing primitive that investigates
  repository evidence, chooses quick or guided routing, and surfaces at most
  one high-impact unknown.
- `coderail-diagnose`: require a red-capable reproduction before bug theory.
- `coderail-tdd-quality`: improve test seams and reject weak tests while
  retaining CodeRail's full evidence contract.
- `coderail-two-axis-review`: review standards and task intent independently.
- `coderail-grill-contract`: explicitly invoked orchestrator that consumes the
  frame result, bypasses interviews for quick work, and converges guided work
  through typed drafts and change-only deltas.

The framing, diagnosis, TDD-quality, and two-axis-review skills are
model-invoked. Contract grilling is user-invoked because it changes the
interaction flow and waits for explicit decisions.

## Invariants

- CodeRail remains the only task-state authority.
- Skills never stage or commit.
- Skills never create a competing spec, ticket, handoff, or issue store.
- All implementation still closes through `coderail done`.
- No skill installs or calls a hook.

## Validation

```powershell
python -m pip install --target .test-deps -r requirements-dev.txt
python -m unittest discover -s tests -v
```

The test suite runs the standard Codex skill validator for every skill. The
validation dependency is isolated in `.test-deps` and is not a runtime
dependency of the skills.

## Guided Convergence protocol

WP1 freezes the protocol before changing prompts:

- `fixtures/protocol.json` defines the closed vocabularies and invariants.
- `fixtures/contract-draft.md` is the deterministic full-draft fixture.
- `fixtures/draft-delta.md` demonstrates change-only reporting.
- `fixtures/scenarios.json` fixes the first four quick/guided route cases.
- `fixtures/promotion-cases.json` covers glossary and ADR promotion.

`tests/test_guided_convergence_protocol.py` derives readiness and promotion
eligibility from the fixture data. A fixture cannot declare itself ready or
promotion-eligible unless the executable invariants agree.

WP2 implements `coderail-frame` against that frozen protocol. WP3 composes it
into `coderail-grill-contract`, adds the quick-path bypass, treats "I do not
know" as valid, emits a change-only Draft Delta after each answer, and stops at
reversible-slice readiness. The orchestrator remains user-invoked and requires
explicit confirmation before calling the public CodeRail lifecycle.

The scenario matrix now contains all eight planned cases: two quick contracts,
five guided contracts, and one reproduced regression routed to diagnosis. The
tests derive readiness, question shape, promotion eligibility, workflow
routing, and invocation policy from the fixtures.

## Evaluation

WP5 freezes its pretrial inputs under `evaluation/` before recording results:

- `manifest.json`: 18 balanced task packets and hidden scoring oracles.
- `workflows/A.md`: baseline CodeRail contract drafting.
- `workflows/B.md`: expert grilling with immediate documentation.
- `workflows/C.md`: Guided Convergence.
- `rubric.json` and `trial-result.schema.json`: blind observation rules.
- `freeze.json`: SHA-256 hashes and fixed model execution settings.
- `scripts/score_evaluation.py`: deterministic aggregation that never accepts
  model self-scoring as observation.

Contract-phase and implementation-phase evidence remain distinct. A contract
trial may measure route, questions, assumptions, interruptions, and tokens, but
unobserved implementation fields remain `null` and cannot authorize adoption.

The `wp5-v1` availability preflight stopped before any subject trial:
`gpt-5.6-terra` requires a newer local Codex version, and the frozen schema also
made `promotion_reversals` non-nullable despite being unobservable in a
contract-only trial. Both findings are recorded under
`evaluation/results/wp5-v1`; no silent model substitution or false zero was
accepted. A corrected `wp5-v2` must be frozen before execution.

`evaluation-v2/` is that corrected freeze. It preserves all 18 task packets,
A/B/C treatments, oracles, and thresholds; pins the preflight-confirmed
`gpt-5.4` medium configuration; makes every unobservable follow-through metric
nullable; and freezes separate subject, blind-judge, and execution contracts.

Its first structured-output request was rejected before subject generation
because the service requires an explicit JSON type alongside a constant schema
constraint. The v2 hashes remain intact and subject output count is zero.

`evaluation-v3/` adds only those service-required explicit types, re-freezes
the same experiment semantics, and passes a no-task schema compatibility
preflight before any subject batch.

The v3 contract-phase run completed all 54 cells. Clear-task routing was 100%
for A, B, and C, but C produced two unsupported assumptions versus one each for
A and B, used 4.39% more subject tokens than A, and did not reduce
interruptions. Implementation and post-close fields remain null, so the result
does not authorize adoption. See `docs/WP5_EVALUATION_REPORT.md`.

`evaluation-v4/` is the targeted revision checkpoint. It keeps A, B, all task
packets and hidden oracles, the model, rubric semantics, batching, and blinding
unchanged. Only C now makes risk-control closure, complete decision-dependency
closure, novice outcome ownership, and clear-task quick-path preservation
explicit. Its no-task schema preflight passed before any subject batch.

The v4 run completed all 54 cells. C recorded zero unsupported assumptions
versus A=3 and B=1, and retained 100% clear-task routing. It also used 32.07%
more subject tokens than A and still exposed one provider-related technical
choice to a novice. On the acceptance-targeted ambiguous/risky subset, all
three workflows were already at zero unsupported assumptions, so the required
25% relative reduction cannot be established from this run. The treatment
therefore remains REVISE, not ADOPT, and implementation evidence is still
absent.

Do not copy the experiment into CodeRail until measured results justify ending
the stabilization freeze for a native optional pack.

## Initial forward-test result

- The two-axis review independently found all seeded standards and contract
  failures without changing the fixture. Its wording was tightened so
  read-only review does not imply closeout and `[~]` in hot `TASKS` remains the
  ownership fact when generated status is stale.
- Diagnosis produced a real failing regression before the fix and passed the
  focused suite afterward. Closeout exposed two useful integration details:
  acceptance verdicts must be supplied explicitly, and generated test
  artifacts must stay outside task ownership. The skill now handles both.
- The diagnosis fixture also reproduced a CodeRail-generated trailing-blank
  `diff --check` failure after an earlier failed closeout. The skill correctly
  stops and reports that kernel-owned failure rather than editing governance
  state or claiming success.
