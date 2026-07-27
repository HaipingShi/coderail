# WP6 Guided-Convergence Adoption Review

Date: 2026-07-27

Decision: REVISE

## Decision Scope

This decision applies to the proposed native adoption of the experimental
`coderail-frame` and `coderail-grill` workflow. The research signal is useful
enough to preserve and revise, but the current C5 treatment is not suitable for
native CodeRail integration.

The resulting dispositions are:

| Surface | Disposition |
|---|---|
| Isolated workflow-lab research pack | Preserve as a non-shipping prototype |
| C5 treatment | Revise under a new protocol |
| Native CodeRail skill pack | Withhold |
| Smart or automatic invocation hook | Do not build |
| CodeRail kernel, lifecycle, and task authority | Unchanged |
| Remaining v5 seeds and C5p | Do not run |

`REVISE` is not a partial adoption. Nothing from this experiment is installed
as a native skill, made automatic, or placed on CodeRail's correctness path.

## Evidence

The decision uses the frozen v4 and v5 results rather than the fluency of the
workflow prose.

### Useful signal

- In v4, C recorded zero unsupported assumptions across 18 trials and retained
  100% clear-task quick-path correctness.
- In v5, C5 again retained 100% quick-path correctness on the clear arm.
- The framing and grilling split remained testable without changing CodeRail
  task ownership, lifecycle states, or canonical persistence.
- Seed-major execution, blind judging, frozen hashes, and explicit early-stop
  records made a negative result observable instead of silently rationalizing
  it away.

### Blocking evidence

- In v4, C used 32.07% more subject tokens than A and still exposed one
  provider-related technical choice to a novice.
- The v4 acceptance-targeted ambiguous and risky subset had a zero baseline,
  so the registered relative-improvement claim could not be established.
- In v5, blind judging found two user-visible technical choices in s2:
  `ambiguous-03-csv-import-mapping` exposed a preview-workflow mechanism and
  `ambiguous-06-offline-mode` exposed a cache-based implementation path.
- The registered provider gate therefore stopped v5 after 90 trials, 21
  subject batches, and seven judge batches. Seeds s3-s5 and C5p were not run.
- On the completed v5 prefix, unsupported assumptions were worse for C5 than A
  (0.5 versus 0.1667 on the threshold metric). C5/A token ratios were 1.0756,
  1.0713, 1.0509, and 0.9857 across the four task categories.
- C5 used 1.2667 turns per trial versus 0.9333 for matched v4 C. Interruptions
  improved slightly (1.0333 versus 1.1333), but this does not override the
  provider-gate failure.
- Implementation and follow-through observations remain null. There is no
  evidence for closeout behavior, long-lived project drift, or native runtime
  operation.

The clear-task result and bounded token ratios are promising, but they cannot
compensate for a failed novice boundary or missing implementation evidence.

## Novice Boundary

The next treatment must ask a novice to authorize observable outcomes, not to
select providers, caches, schemas, architecture, or workflow mechanisms.

Examples:

| Avoid asking | Ask instead |
|---|---|
| Which CSV preview workflow should be used? | Must imported rows be previewable and reversible before they are committed? |
| Should offline mode use a local cache? | Which previously opened information must remain available without a connection? |
| Should the existing identity provider be reused? | Must existing accounts keep working without another sign-in? |

The agent must investigate repository facts and choose reversible technical
mechanisms internally. It may surface a mechanism only when the user owns a
real tradeoff that cannot be resolved from evidence. In that case it asks one
question, recommends an outcome, explains the consequence in novice language,
and records the unresolved boundary without promoting an assumption.

## Revision Contract

Any continuation must be a new frozen protocol, not a mutation or continuation
of `wp5-v5`. A revised treatment must:

1. preserve the clear-task bypass and one-question-at-a-time interaction;
2. keep provider and implementation choices inside agent investigation;
3. retain evidence-linked Contract Draft and Draft Delta outputs;
4. preserve CodeRail as the only task and lifecycle authority;
5. keep invocation explicit and optional during research;
6. evaluate all five registered gates with seed-major blind judging;
7. collect real contract, implementation, verification, and closeout evidence
   before reconsidering native adoption.

The next protocol may advance beyond an initial provider gate only after the
revised treatment records zero novice-facing technical choices. Native
integration remains unavailable until the complete evidence package passes;
partial subject-response evidence cannot authorize it.

## Rejected Integration Paths

- No smart hook or automatic intent classifier.
- No new CodeRail command, lifecycle state, hard gate, or canonical store.
- No direct writes to `.coderail/tasks.json`.
- No copying the experimental skills into the shipping skill surface.
- No execution of v5 s3-s5 or C5p.
- No demographic or identity proxy for estimating user expertise.

## Closeout

The grill-me and grill-with-docs study is absorbed as a tested design lesson,
not as shipping machinery: explore what the repository can answer, ask one
high-value question when a material decision remains, recommend an
outcome-level default, and persist the result through CodeRail's existing
contract authority. WP0-WP6 are complete. Further work requires a separately
authorized protocol with new frozen inputs.
