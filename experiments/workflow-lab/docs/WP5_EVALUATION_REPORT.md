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
