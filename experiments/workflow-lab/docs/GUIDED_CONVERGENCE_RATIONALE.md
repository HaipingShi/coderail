# Guided Convergence: Design Rationale

Status: proposed experiment
Date: 2026-07-25
Applies to: `coderail-workflow-lab`
Does not authorize: changes to the CodeRail kernel, commands, hooks, lifecycle,
or required governance context

## 1. Why This Record Exists

This document records the reasoning behind adapting Matt Pocock's
`grill-with-docs` and `domain-modeling` ideas for CodeRail. It is an iteration
baseline, not a claim that the design is already validated.

The important correction is that a workflow designed by and for an expert
programmer carries an implicit operator-capability assumption. An expert can
reject a fluent but weak recommendation, recognize a missing technical
dimension, distinguish a stable domain term from a temporary label, and decide
when further interviewing has negative value. A novice using vibe coding often
cannot.

CodeRail must therefore absorb the information-gathering discipline without
delegating technical truth or convergence judgment to a user who may not be
equipped to evaluate it.

## 2. Source Baseline

- Upstream repository: `https://github.com/mattpocock/skills`
- Analyzed commit: `ed37663cc5fbef691ddfecd080dff42f7e7e350d`
- Local research clone: `G:\codeRail\research-mattpocock-skills`
- Relevant upstream skills:
  - `skills/engineering/grill-with-docs/SKILL.md`
  - `skills/engineering/grilling/SKILL.md`
  - `skills/engineering/domain-modeling/SKILL.md`

At the analyzed commit, `grill-with-docs` is deliberately thin: it runs a
user-invoked grilling session while applying domain modeling. The substantive
behavior is distributed across two disciplines:

1. Resolve a decision tree one question at a time, include a recommended
   answer, and investigate facts that the codebase can answer.
2. Challenge vocabulary, test concrete scenarios, cross-reference claims with
   code, persist resolved terms, and record only sparse decision-grade ADRs.

The useful unit is not the short wrapper. It is the composition of active
questioning, semantic refinement, evidence, and selective persistence.

## 3. Information-Theoretic Interpretation

Let:

```text
Theta = the user's actual desired outcome and acceptable design
C     = current conversation, repository facts, and prior decisions
```

Grilling attempts to choose a question whose answer removes high-impact
candidate interpretations:

```text
H(Theta | C, answer) < H(Theta | C)
```

The skill does not compute entropy or information gain. Those are explanatory
models, not runtime scoring requirements.

The practical sequence is:

```text
surface hidden dimensions
-> collect discriminating evidence
-> prune incompatible interpretations
-> compile the surviving intent into an executable contract
```

This can increase front-loaded conversation tokens while reducing later
rework. It is useful only when the expected downstream cost of a wrong
interpretation is greater than the interview cost.

## 4. Semantic Addressing

A user cannot reliably ask about a decision dimension they do not know exists.
The agent must use its domain priors to discover candidate lenses such as
security, persistence, accessibility, concurrency, migration, or failure
recovery.

This makes the agent an intent compiler:

```text
natural-language intent
-> candidate domain frame
-> relevant blind spot
-> one answerable question
-> contract delta
```

The domain frame is a hypothesis generator, not a source of truth. Model
knowledge can be stale, incomplete, or inappropriate for the repository.
Repository evidence, focused experiments, primary documentation, and actual
acceptance behavior remain authoritative for technical claims.

## 5. The Expert-Novice Capability Gap

| Judgment | Expert operator | Novice vibe coder | CodeRail adaptation |
|---|---|---|---|
| Detect fuzzy terminology | Often recognizes it directly | May accept polished vocabulary | Agent proposes terms as hypotheses |
| Evaluate a recommendation | Can challenge architecture and trade-offs | May treat fluency as correctness | Explain impact, evidence, uncertainty, and reversibility |
| Discover unknown unknowns | Has a developed domain checklist | Does not know which questions to ask | Activate domain lenses silently |
| Select technical options | Can compare implementation consequences | May choose by familiarity or wording | Ask about observable outcomes, not jargon |
| Know when to stop | Can judge residual risk | May stop too early or interview forever | Use explicit readiness and stop rules |
| Persist domain knowledge | Can distinguish stable language from scratch ideas | May canonize a guess | Use a promotion ladder |

The failure mode is not merely a bad answer. It is a bad answer becoming
canonical project language and steering later sessions.

## 6. Product Thesis

The CodeRail adaptation is **Guided Convergence**:

> Help a user reach the next bounded, verifiable, and reversible implementation
> slice without requiring the user to act as the technical reviewer.

This differs from pursuing a complete shared domain model before action.
Completeness is neither achievable nor necessary for many tasks. The target is
sufficient readiness for the next safe slice, followed by learning from
execution.

```text
intent
-> capability-aware guidance
-> silent domain framing
-> repository and source evidence
-> one high-impact question
-> proposed contract delta
-> readiness for a reversible slice
-> execute and verify
-> promote only stable knowledge
```

## 7. Authority Model

Authority is intentionally asymmetric:

| Concern | Primary authority |
|---|---|
| Desired outcome, priorities, experience, and acceptance | User |
| Repository structure and current behavior | Repository evidence |
| Technical defaults and candidate solutions | Agent proposal |
| Correctness of technical claims | Tests, tools, experiments, and primary sources |
| Task lifecycle, ownership, verification record, and commit | CodeRail kernel |
| High-impact irreversible trade-offs | Explicit user confirmation after evidence |

The user is not asked to certify technical correctness merely because a
question was presented as a choice.

## 8. Epistemic States

Every material draft item must have one state:

```text
FACT
  Supported by repository evidence, a tool result, or an authoritative source.

ASSUMPTION
  A provisional belief used to keep work moving. It includes a confidence
  note and a falsification or review trigger.

DECISION
  An explicitly accepted choice with its owner and material trade-off.

UNKNOWN
  Not resolved. It is either blocking or deliberately deferred.
```

Fluent wording must not erase these distinctions. A contract with labeled
uncertainty is more honest than a complete-looking contract made of guesses.

## 9. Persistence Promotion Ladder

Information should move through progressively more durable stores:

```text
conversation observation
-> proposed contract item
-> verified task constraint or accepted decision
-> stable domain term
-> ADR, only for a consequential trade-off
```

Promotion rules:

- A proposed item does not mutate canonical task state.
- An assumption must not become a glossary definition solely because the user
  accepted the agent's recommendation.
- A glossary term requires consistent meaning in concrete scenarios and no
  unresolved contradiction with code or existing project language.
- An ADR requires all upstream tests: hard to reverse, surprising without
  context, and the result of a real trade-off.
- For novice-safe operation, an ADR also requires an evidence link and an
  explicit decision owner.
- Implementation details stay out of the glossary.

CodeRail's existing records remain canonical. The experiment must not create a
second issue tracker, task store, or lifecycle.

## 10. Question Contract

The agent asks exactly one question at a time only when the answer can change
the current task, verification, stop condition, or persistence decision.

A novice-safe question contains:

```text
Question:
  A result or behavior the user can evaluate.

Recommendation:
  The current default.

Reason:
  Why it fits the known goal and repository.

Impact:
  What becomes easier, harder, included, or excluded.

Evidence:
  Repository, experiment, or source support. Otherwise label it an assumption.

Uncertainty:
  What could make the recommendation wrong.

Reversibility:
  Whether the choice can be changed cheaply after the next slice.
```

Technical jargon should be translated into observable consequences. Do not ask
a novice to choose between architecture labels when a prototype, code search,
or focused test can answer the underlying question more reliably.

Recommendations create anchoring pressure. The interface must allow the user
to say "I do not know", request alternatives, or delegate a reversible
technical default without that response being treated as informed approval.

## 11. Convergence Contract

The session converges when the next slice is safe enough to execute, not when
all possible questions are answered.

The G/T/S/V/X/P draft is ready when:

- **G - Goal:** the observable outcome and its North Star relationship are
  explicit.
- **T - Task:** one bounded vertical slice can demonstrate progress.
- **S - Scope:** allowed and forbidden surfaces prevent material drift.
- **V - Verify:** executable checks and user-visible acceptance are known.
- **X - Stop:** blocking unknowns, escalation triggers, and assumption
  falsifiers are explicit.
- **P - Persist:** the existing CodeRail records that must remain honest are
  identified.

Additional readiness rules:

- No unresolved unknown blocks the slice.
- High-risk assumptions are verified or represented by an X trigger.
- Deferred unknowns are named rather than silently discarded.
- The slice is reversible at a cost appropriate to its risk.
- Another question is asked only if its expected decision value exceeds its
  interruption cost.

Readiness is a qualitative, inspectable judgment. The experiment must not
invent fake entropy, confidence, or readiness percentages.

## 12. Routing Boundary

Not every request should be grilled.

### Quick path

Use direct contract drafting when the request is clear, local, low-risk,
reversible, and has an obvious verification command.

### Guided path

Use Guided Convergence when one or more apply:

- the user states uncertainty or asks for design help;
- the work is cross-module or persistent;
- business behavior or acceptance is ambiguous;
- security, privacy, payment, migration, destructive data change, or public
  API behavior is involved;
- a key term has conflicting meanings;
- the agent detects a high-impact unknown that repository evidence cannot
  resolve.

Routing is advisory during the experiment. It must not be an LLM-powered hook,
must not mutate state, and must not add a kernel gate.

## 13. What Is Accepted, Modified, and Rejected

### Accepted

- One decision at a time.
- Investigate repository facts instead of asking the user.
- Attach a recommendation and trade-off to questions.
- Challenge ambiguous domain language with concrete scenarios.
- Cross-reference claims with code.
- Persist stable vocabulary and sparse decision-grade ADRs.
- Use user-invoked orchestration and model-invoked reasoning primitives.

### Modified

- "Write terms as they crystallize" becomes staged promotion after evidence.
- "Relentless interview" becomes value-bounded interviewing with a quick path.
- Shared understanding becomes an explicit typed draft, not an implicit
  conversational feeling.
- Domain framing remains internal by default; the novice sees only the most
  relevant consequence.
- Completion means readiness for the next reversible slice, not exhaustive
  domain closure.

### Rejected

- Treating model priors as current facts.
- Asking users to arbitrate technical choices they cannot reasonably evaluate.
- Numeric pseudo-information-gain scoring.
- Persisting every answer as canonical documentation.
- Automatic workflow selection through a smart hook.
- Any competing task, issue, commit, or lifecycle authority.

## 14. Failure Signals

The design must be reconsidered if experiments show:

- longer conversations without fewer contract corrections or reopened tasks;
- novices approving recommendations they cannot explain in outcome terms;
- glossary or ADR churn caused by premature persistence;
- simple tasks repeatedly entering the guided path;
- the agent hiding consequential assumptions behind confident wording;
- G/T/S/V/X/P becoming ceremonial text rather than executable constraints;
- a second source of truth or pressure to add an LLM-dependent kernel gate.

## 15. Open Questions

- What observable signals best distinguish a novice needing guidance from an
  expert preferring terse technical choices without profiling the person?
- Which task classes gain enough from interviewing to justify the added turns?
- How many draft deltas can remain readable before the draft needs compaction?
- What evidence threshold is sufficient to promote a term to stable glossary
  language?
- Can readiness be evaluated consistently from qualitative rules without
  becoming another hard lifecycle state?
- Does showing uncertainty improve correction rates, or merely increase user
  fatigue?

These are evaluation questions. They are not authorization to change the
CodeRail kernel.
