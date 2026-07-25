# WP5 Comparative Evaluation Report

Status: preflight blocked; no subject trial observed
Protocol: `wp5-v1`
Date: 2026-07-25

## Preflight result

The frozen subject model was `gpt-5.6-terra` at medium reasoning. The installed
Codex CLI reached the service but received HTTP 400: that model requires a
newer Codex version. No A, B, or C subject trial was started and no task output
was observed.

A separate availability probe confirmed that `gpt-5.4` at medium reasoning can
run on the installed CLI. It was not used as an undeclared replacement.

## Protocol defect found

The contract-phase result schema requires an integer for
`promotion_reversals`, although reversal can be known only from later
follow-through evidence. Recording zero would confuse "not observed" with "no
reversal." The same experiment rules already require unobserved implementation
fields to remain null.

## Decision

Do not score `wp5-v1`. Create `wp5-v2` before subject execution:

1. pin the available `gpt-5.4` model at medium reasoning;
2. allow null for every metric that contract-only trials cannot observe;
3. retain the same 18 tasks, A/B/C treatments, oracles, and adoption
   thresholds;
4. freeze new hashes before the first subject output.

This is a pretrial protocol correction, not an unfavorable result and not
evidence for ADOPT, REVISE, or REJECT.

## v2 execution preflight

`wp5-v2` fixed the model and nullability defects, but its first subject request
was rejected before generation with `invalid_json_schema`. The service requires
an explicit JSON type alongside each constant constraint. No subject output was
returned; only the thread start and structured 400 error were recorded.

The frozen v2 schema was not transformed in place. A v3 freeze may add the
service-required types while preserving the same tasks, workflows, model,
rubric semantics, and execution design.

## v3 schema preflight

`wp5-v3` adds explicit JSON types beside constant constraints and changes no
task, workflow, model, oracle, rubric meaning, or batching rule. The service
accepted the frozen subject schema and returned a conforming dummy response.
One identical-input retry was used only because the first accepted response
could not be persisted to a missing local output directory.

No experiment task or hidden oracle was included in the schema preflight, and
subject batch count remains zero.

## v3 contract-phase results

`wp5-v3` completed all 12 subject batches and 4 workflow-masked judge batches:
54 workflow-task cells over the frozen 18-task matrix.

| Metric (sum unless marked) | A Baseline | B Expert grill | C Guided |
|---|---:|---:|---:|
| Trials | 18 | 18 | 18 |
| Turns before readiness | 16 | 17 | 16 |
| Useful questions | 16 | 17 | 16 |
| User-visible technical choices | 1 | 1 | 1 |
| Unsupported assumptions | 1 | 1 | 2 |
| Human interruptions | 16 | 17 | 16 |
| Route correctness | 100% | 100% | 100% |
| Allocated subject tokens | 73,397 | 75,868 | 76,618 |
| First-pass `done` | not observed | not observed | not observed |

Relative to A, B used 3.37% more subject tokens and C used 4.39% more. All
three workflows routed the six clear tasks correctly with zero clear-task
interruptions.

On the nine ambiguous or high-risk tasks, A and B had zero unsupported
assumptions while C had one. Therefore C did not achieve the required 25%
reduction; it moved in the wrong direction on the observed contract-phase
proxy.

## Material findings

- All three workflows asked a novice to decide an identity-provider mechanism
  in the login case. Guided wording did not remove that technical choice.
- A and C both declared the public Workspace contract ready before resolving
  the frozen migration answer.
- B proposed immediate Account documentation before code and scenario meaning
  had converged, demonstrating the expected premature-promotion risk.
- C treated refund audit design as outside the first slice even though the
  oracle forbade refunds without audit evidence.
- C matched A on turns and interruptions but consumed more tokens and retained
  one additional unsupported assumption.

## Evidence boundary

This was an offline contract-convergence simulation, not a live-human study.
Scripted answers were present in each batch prompt with instructions not to use
them before a matching question, so answer leakage cannot be excluded.

Tasks were batched by category. Per-task tokens are an equal allocation of the
batch total, not native per-task usage. The blind judge used the same model as
the subjects and did not receive workflow labels, although response style could
still reveal treatment.

The following remain null and unmeasured:

- post-start contract corrections;
- out-of-scope edits;
- first-pass CodeRail `done`;
- reopened or post-close defects;
- glossary or ADR reversals.

## Contract-phase verdict

The aggregate decision is `INSUFFICIENT_IMPLEMENTATION_EVIDENCE`. The run does
not authorize ADOPT. It also provides no contract-phase evidence that C
outperforms baseline A; current evidence favors a targeted revision before
paying for implementation follow-through.

The revision should:

1. keep audit and other forbidden-risk controls inside the reversible slice;
2. require every scripted decision dependency, including migration, before
   readiness;
3. translate provider feasibility into an agent investigation or outcome-level
   authorization instead of a novice architecture choice;
4. preserve the successful clear-task quick path.

Changing treatment C requires a new frozen protocol version and a full
contract-phase rerun. Alternatively, implementation follow-through can run
unchanged on v3, but null outcome gates still prevent an adoption decision.

## v4 revision and preflight

`wp5-v4` applies the targeted C revision while preserving A, B, all 18 task
packets and hidden oracles, the model, rubric semantics, batching, blinding,
and failure handling from v3. The new C readiness rules require:

1. audit and other controls necessary to make a risk boundary true remain
   inside the reversible slice and its verification;
2. every non-fallback decision dependency, including migration, resolves before
   readiness;
3. novice users authorize observable outcomes rather than providers or
   architecture labels;
4. clear local reversible tasks keep the zero-question quick path.

All v4 pretrial inputs are hash-frozen. A no-task schema request using
`gpt-5.4` at medium reasoning passed with zero task or oracle payloads and zero
subject batches started. This checkpoint proves protocol and service
compatibility only; it is not evidence that C improved.

## v4 contract-phase results

The v4 run completed 12 subject batches and four workflow-masked judge batches,
covering all 54 cells.

| Metric (sum unless marked) | A Baseline | B Expert grill | C Guided v4 |
|---|---:|---:|---:|
| Trials | 18 | 18 | 18 |
| Turns before readiness | 16 | 14 | 14 |
| Useful questions | 16 | 17 | 17 |
| User-visible technical choices | 1 | 1 | 1 |
| Unsupported assumptions | 3 | 1 | 0 |
| Human interruptions | 16 | 17 | 17 |
| Route correctness | 100% | 100% | 100% |
| Allocated subject tokens | 73,903 | 75,968 | 97,603 |
| First-pass `done` | not observed | not observed | not observed |

C used 32.07% more subject tokens than A and 28.48% more than B. Its
domain-language batches used 37,313 tokens versus A's 18,059, accounting for
most of the excess.

On the nine ambiguous and high-risk tasks targeted by the adoption threshold,
unsupported assumptions were A=0, B=0, and C=0. C therefore fixed its v3
high-risk failure but cannot demonstrate a 25% relative reduction against a
v4 baseline already at zero.

## v4 material findings

- C kept required refund auditability and approval gating inside the contract.
- C resolved both Workspace meaning and migration before readiness.
- C preserved the zero-question path on all six clear tasks.
- C still asked whether to reuse the existing identity provider. The blind
  judge counted that provider gate as a novice-facing technical choice.
- Overall unsupported assumptions improved to zero for C, but A changed from
  one in v3 to three in v4 despite unchanged treatment text. That baseline
  movement is evidence of single-run sampling variance, so the v3/v4 delta
  cannot be treated as a pure causal estimate.

The first execution attempt completed eight subject batches, then the local
runner decoded a UTF-8 event stream with the Windows GBK default and failed
after the next raw output had been persisted. The failure metadata and raw
output were retained. The runner now declares UTF-8 explicitly; the identical
input was retried and the eight complete raw/event pairs were reused. The final
metadata identifies reused and executed batches, and all frozen hashes remain
unchanged.

## v4 disposition

The treatment disposition is **REVISE**:

1. eliminate the remaining novice-facing provider choice;
2. reduce domain-language verbosity and token cost;
3. use repeated seeds or multiple samples before attributing score movement to
   the prompt revision.

The aggregate decision remains `INSUFFICIENT_IMPLEMENTATION_EVIDENCE`.
Implementation corrections, scope edits, CodeRail closeout, post-close defects,
and promotion reversals remain null. Nothing in v4 authorizes native
integration.

## v5 repaired freeze checkpoint

The `wp5-v5` pretrial inputs were reviewed and refrozen on 2026-07-26 before
any schema preflight or subject output. The repair makes seed provenance and
the `C5` treatment name machine-readable; it does not change task packets,
oracles, treatment text, rubric semantics, or model policy. This checkpoint
applies the three v4 disposition items only: the C-R1 provider-question
elimination, the C-R2 output-economy rule, and a multi-seed sampling plan for
attribution. The aggregate decision remains `INSUFFICIENT_IMPLEMENTATION_EVIDENCE`.

Version stamping follows the v3-to-v4 precedent for the rubric and
subject/judge output schemas. `manifest.json.trial_design` names primary
workflows `[A, B, C5]`, isolates `[C5p]` as a contingency, and records the
canonical category-to-seed plan for 180 primary trials.
`trial-result.schema.json` accepts `[A, B, C5, C5p]` and requires one of the
five frozen seed identifiers on every record. The 18 task packets, hidden
oracles, rubric content, judge prompt, and workflows A and B remain
byte-identical to v4. The C5 arm (`workflows/C.md`) is v4 C plus the
strengthened GC-R3 and the new GC-R5 output-economy rule. The C5p contingency
(`workflows/C5p.md`) is v4 C plus the strengthened GC-R3 only, retaining v4
verbosity; it is frozen here even though it may never run.

Key SHA-256 (`evaluation-v5/freeze.json`):

- `workflows/C.md` (C5): `9c751821a7b177920a77bcc8475dd3e6d6209b8b4ce19d120be51ea8b172a3eb`
- `workflows/C5p.md` (contingency): `97ddac2e734f2bb0b2c3a7f6b99175227d06e939cfcb3a1c4bf968b571dcbf65`
- `manifest.json`: `7329b61a3c146082565af26a00cd030e910105fd5b7cae1681eaf53154a25529`
- `trial-result.schema.json`: `13c562a19f82c37016143e7efadb40d906c6c61cb1b339b593406eaca35c63ff`
- `run-spec.md`: `2b703e2280ace7ab9a4ce9f2dc630a3d491900285c2868283fe1fc5c084c28bd`

Byte-identical to v4: `workflows/A.md` (`9fa02a6d...`), `workflows/B.md`
(`25092bcc...`), and `judge.md` (`6ee8385e...`).

Sampling plan: threshold subset (9 ambiguous and high-risk tasks) x 5 seeds,
domain-language-conflict (3 tasks) x 3 seeds, clear-local-reversible (6 tasks)
x 1 seed, for 180 trials across A, B, and C5. The domain-language subset is
sampled because it drove the v4 token excess; without it the token gate has no
measurement surface. Gate 4 is evaluated on pooled subject tokens per category
across that category's seeds, C5 versus A.

This repaired checkpoint records no subject output, no judge output, and no
schema preflight; `subject_batches_started` is 0 and
`schema_preflight_run_at_this_checkpoint` is false. The freeze is protocol
preparation only. It is not a trial, it constitutes no evidence that C5
improved, and it does not authorize ADOPT. The schema preflight with zero task
or oracle payloads remains paused until separately authorized.
