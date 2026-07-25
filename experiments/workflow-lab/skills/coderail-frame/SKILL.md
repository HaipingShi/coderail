---
name: coderail-frame
description: Investigate repository evidence, detect candidate domain boundaries, and choose a quick path or one high-impact novice-safe question before drafting a CodeRail contract. Use internally for new, ambiguous, risky, persistent, or cross-module requests whose task boundary is not yet established.
---

# CodeRail Frame

Frame the next bounded slice before contract drafting. Reduce decision
uncertainty without making the user answer questions the repository can answer.

## CodeRail boundary

- Read `AGENTS.md`, `docs/NORTH_STAR.md`, `docs/TASKS.md`, relevant decisions,
  and `git status` before framing the request.
- Treat this skill as a read-only reasoning primitive. Do not create a task,
  edit files, implement, or persist the frame.
- Do not write `.coderail/tasks.json` or edit task state behind the CLI.
- Never stage or commit task changes.
- Any later implementation finishes through
  `python .coderail/coderail.py done`.

## Frame

1. Extract the requested outcome and the repository facts already supplied.
2. Generate at most three domain lenses that could materially change `G`,
   `T`, `S`, `V`, `X`, or `P`. Label each as `[CANDIDATE]`. A candidate lens is
   never a fact about the product or user.
3. Investigate the repository before asking anything. Inspect instructions,
   code, tests, configuration, decisions, and history relevant to each lens.
4. Type every material claim:
   - `FACT`: cite repository, command, request, primary-source, or experiment
     evidence.
   - `ASSUMPTION`: name the owner, falsifier, and risk. Point high-risk
     assumptions to a proposed `X` stop condition.
   - `DECISION`: name the decision owner.
   - `UNKNOWN`: mark it exactly one of blocking or deferred.
5. Remove lenses that repository evidence resolves. When repository evidence
   resolves the issue, emit `user-facing question: none`; do not ask the user
   to confirm discovered facts.
6. Rank the remaining blind spots by whether an answer changes a contract
   coordinate, prevents irreversible harm, or determines verification. Do not
   use numeric confidence, entropy, readiness, or information-gain scoring.
7. Select the `quick` or `guided` route.

## Route

Choose `quick` only when the requested outcome is clear, local, low-risk,
reversible, bounded by repository evidence, and backed by executable or
explicit manual verification. Quick means no interview is useful; it does not
claim that a CodeRail task is already active or ready to close.

Choose `guided` when one unresolved answer could change a coordinate or when
security, privacy, identity, persistence, migration, public API, payment, or
other hard-to-reverse behavior is material.

For guided work, surface exactly one highest-impact unknown. Translate it into
an outcome-level choice. Do not dump an exhaustive expert checklist or ask a
novice to choose unexplained architecture labels. Accept that the user may not
know; recommend the cheapest reversible default when their authority permits.

Use fixture-consistent focus names when applicable:

- `audience-boundary`: who receives distinct identity, authority, or data.
- `privacy-boundary`: which original or derived data may cross a device or
  trust boundary.
- `durability-boundary`: what must survive, be shared, or be migrated.

These are candidate lenses, not a complete taxonomy.

## Evidence

Use repository evidence for stable local claims. For unstable or high-risk
technical claims, verify against a primary source or a focused experiment
before presenting the claim as `FACT`. Otherwise keep it as `ASSUMPTION` or
`UNKNOWN` and expose what would falsify or resolve it.

Never infer expertise from identity or demographics. Adapt wording only to the
user's demonstrated language and the decision they actually own.

## Output

Return exactly one of these internal results. This is a proposal for the later
contract orchestrator, not a user-facing specification or canonical record.

Quick:

```text
FRAME RESULT
route: quick
candidate lenses: [CANDIDATE] <lens> | none
evidence: <typed evidence summary>
resolved by repository: <what no longer needs a question>
affected coordinates: <G/T/S/V/X/P>
user-facing question: none
```

Guided:

```text
FRAME RESULT
route: guided
candidate lenses: [CANDIDATE] <at most three>
evidence: <typed evidence summary>
highest-impact unknown: <one blocking UNKNOWN>
affected coordinates: <G/T/S/V/X/P>
question:
  focus: <outcome boundary>
  question: <one plain-language question>
  recommendation: <one reversible default>
  reason: <why this unknown is highest impact>
  impact: <what changes with the answer>
  evidence: <what was inspected>
  uncertainty: <what remains unknown>
  reversibility: <cost or irreversible consequence>
```

Do not emit a Draft, Draft Delta, glossary entry, ADR, task mutation, or
implementation. Those belong to later orchestration and CodeRail's public
lifecycle.
