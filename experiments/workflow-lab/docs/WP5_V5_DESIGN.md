# WP5 V5 Experiment Design

Status: design draft; no pretrial input frozen; no subject trial started
Protocol: `wp5-v5` (planned)
Supersedes for execution: `wp5-v4`
Date: 2026-07-25

## 1. Purpose

The v4 disposition was REVISE with three required changes:

1. eliminate the remaining novice-facing provider choice;
2. reduce domain-language verbosity and token cost;
3. use repeated seeds or multiple samples before attributing score movement to
   the prompt revision.

`wp5-v5` applies exactly these three changes and nothing else. It is a
contract-phase protocol revision, not an implementation-phase experiment. The
aggregate decision remains `INSUFFICIENT_IMPLEMENTATION_EVIDENCE` regardless of
v5 outcome; v5 only decides whether treatment C earns the implementation-phase
follow-through experiment or returns to revision.

## 2. Changes from v4

Two separable revisions to workflow C. A, B, all 18 task packets, hidden
oracles, rubric semantics, model, batching, blinding, and failure handling are
carried over unchanged.

### 2.1 C-R1: provider-question elimination

v4 finding: C still asked whether to reuse the existing identity provider in
the login case, and the blind judge counted that gate as a novice-facing
technical choice (`user_visible_technical_choices = 1`).

Revision: strengthen GC-R3 with an explicit enumeration rule. For a novice
profile, reuse-or-replace of an existing provider, library, storage engine,
protocol, or architecture component is an agent investigation outcome, never a
user-facing question. The agent must either resolve it from repository
evidence or record an investigation/stop condition. The only permitted
user-facing content is the observable outcome or boundary the user can own.

### 2.2 C-R2: domain-language output compression

v4 finding: C used 97,603 subject tokens, 32.07% more than A; the
domain-language-conflict batches used 37,313 tokens versus A's 18,059,
accounting for most of the excess.

Revision: add an output-economy rule to workflow C. Typed contract items must
use the shortest domain-accurate phrasing; lens labels and rationale appear
once per item, not per turn; repeated restatement of resolved FACT/DECISION
items in later turns is prohibited. The response contract shape (G/T/S/V/X/P,
promotions, ready flag) is unchanged so the frozen output schema still
applies.

### 2.3 Separability and attribution

The two revisions target nearly disjoint metrics: C-R1 moves the binary
rubric item `user_visible_technical_choices`; C-R2 moves `total_tokens`. A
single combined arm `C5` is therefore the primary design, with pre-registered
metric-level attribution.

Contingency: if `C5` regresses on any assumption, turn, or interruption
metric relative to v4 C, attribution is ambiguous. In that case only, a
disentangling arm `C5p` (C-R1 only, v4 verbosity retained) is frozen and run
on the threshold subset before any conclusion is drawn. `C5p` is not run
otherwise.

## 3. Multi-seed sampling plan

v4 showed material single-run variance: baseline A moved from 1 to 3
unsupported assumptions across v3/v4 with unchanged treatment text. Single
samples cannot support causal attribution, so v5 repeats sampling.

- **Threshold subset (primary):** the 9 ambiguous and high-risk tasks used by
  the adoption threshold are run with **5 independent seeds** per workflow
  (A, B, C5). Seed identifiers: `coderail-wp5-v5-s1` through
  `coderail-wp5-v5-s5`, used for task-order shuffling and recorded in the
  manifest.
- **Domain-language subset (token-economy measurement):** the 3
  domain-language-conflict tasks are run with **3 seeds** (s1-s3) per
  workflow. This category drove the v4 token excess (C 37,313 versus A
  18,059), so it is the primary measurement surface for C-R2 and gate 4.
  Without it the token gate would have no denominator.
- **Clear-task subset (verification only):** the 6 clear/local/reversible
  tasks are run with **1 seed** (s1) per workflow. The quick path held at
  100% across v3 and v4 for all workflows; this arm guards against a C-R2
  regression on GC-R4, it is not a variance-estimation arm.
- **Judge:** workflow-masked judging as in v4, one judge batch per category
  per seed. The judge receives no workflow labels and no seed identifiers.

Estimated subject volume: 5 x 3 x 9 + 3 x 3 x 3 + 1 x 3 x 6 = 180 trials,
versus 54 in v4. Per-trial token cost for C5 is expected to drop under C-R2;
A and B per-trial costs should match v4 within sampling noise. Gate 4 is
evaluated on pooled subject tokens per category across that category's seeds
(C5 versus A), with batch-allocation labeling as in v4.

## 4. The baseline-floor problem

The adoption threshold requires a >= 25% relative reduction in unsupported
assumptions or post-start contract corrections on ambiguous/risky tasks
versus baseline. In v4 the threshold subset counts were A=0, B=0, C=0, and
contract corrections are unobservable in contract-phase trials. If the pooled
baseline mean across 5 seeds is 0, a relative reduction is structurally
undefined.

This is pre-registered handling, not a post-hoc rule:

- **If pooled A > 0:** compute the relative reduction of C5 versus A with a
  bootstrap confidence interval over seeds (10,000 resamples, seed-level
  cluster). The 25% gate is evaluated on the point estimate; the interval is
  reported to show whether sampling noise alone explains the gap.
- **If pooled A = 0:** the 25% relative-reduction gate is declared
  **untestable at contract phase**. C5 must then satisfy the absolute gate in
  section 5 to earn the implementation-phase experiment, where post-start
  contract corrections become observable and the threshold regains a
  denominator.

## 5. Pre-registered decision rules

All gates are evaluated on frozen v5 aggregates before any v6 or
implementation-phase planning.

**C5 earns the implementation-phase experiment only if ALL hold:**

1. `user_visible_technical_choices` = 0 across all seeds (C-R1 effective);
2. threshold-subset unsupported assumptions: C5 <= A on pooled means, and the
   25% relative gate passes whenever it is testable under section 4;
3. quick-path correctness = 100% on the clear-task arm (GC-R4 preserved);
4. C5 pooled subject tokens per category across that category's seeds <=
   +15% versus A pooled the same way (C-R2 effective; v4 was +32.07%);
5. no regression versus v4 C on turns before readiness or human
   interruptions.

**Stopping rules:**

- If the provider gate persists in any seed (gate 1 fails), stop. GC-R3
  wording is rejected as written; do not run further seeds or the C5p
  contingency.
- If C5 assumptions on the threshold subset exceed A's pooled mean, run the
  C5p contingency (section 2.3) before concluding.
- If gates 1-3 pass but gate 4 fails, disposition is REVISE scoped to output
  economy only; the provider revision is retained as validated.
- Implementation-phase follow-through remains gated on v5 plus the still-null
  follow-through metrics (contract corrections, out-of-scope edits,
  first-pass `done`, post-close defects, promotion reversals).

## 6. Execution policy (carried from v4)

- Model: `gpt-5.4`, medium reasoning, availability-preflighted.
- Schema preflight with zero task or oracle payloads before the first subject
  batch.
- Sandbox read-only, approval never, ephemeral, user config and rules
  ignored, web search off.
- Subject never receives oracles; scripted answers withheld until a matching
  question; adjudicator blind to workflow.
- Batch by category; per-task tokens are equal allocations of batch totals
  and are labeled as such.
- The runner declares UTF-8 explicitly (v4 fix retained); raw output is
  persisted before decoding; completed raw/event pairs are reused on retry
  and identified in run metadata.
- All pretrial inputs are hash-frozen in `evaluation-v5/freeze.json` before
  the first subject output, including the C5p contingency text even though it
  may never run. Freezing the contingency prevents mid-run authoring under
  outcome knowledge.
- Version stamping follows the v3-to-v4 precedent: `manifest.json` and all
  schema files are re-stamped to `wp5-v5` in their `protocol_version`/`const`
  fields, so their hashes differ from v4 by exactly those strings.
  `trial-result.schema.json` additionally widens its workflow enum from
  ["A", "B", "C"] to ["A", "B", "C5", "C5p"] so v5 trial records validate;
  no other schema semantics change. Task packets, oracles, rubric content,
  judge prompt, and workflows A/B remain byte-identical to v4.

## 7. Metrics and nullability

Identical to v4. Contract-phase trials cannot observe post-start contract
corrections, out-of-scope edits, first-pass `done`, reopened defects, or
glossary/ADR reversals; these remain null and are not imputed as zero.

## 8. Out of scope

- No implementation-phase execution, CodeRail closeout, or live-human study.
- No change to A, B, task packets, oracles, rubric semantics, or judge
  prompt.
- No native integration. Nothing in v5 can authorize ADOPT; at best it
  authorizes proposing the implementation-phase experiment.
