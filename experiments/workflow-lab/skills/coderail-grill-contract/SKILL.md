---
name: coderail-grill-contract
description: Orchestrate repository framing, quick-path bypass, one-question guided convergence, typed Contract Drafts, and Draft Deltas into a confirmed CodeRail G/T/S/V/X/P contract. Use explicitly before implementation when a new request needs task boundaries or user-owned decisions.
---

# CodeRail Grill Contract

Converge on the next bounded, verifiable, reversible slice without making a
clear request endure an interview.

## CodeRail boundary

- Read `AGENTS.md`, `docs/NORTH_STAR.md`, `docs/TASKS.md`, relevant decisions,
  and `git status` before asking repository facts.
- Look up facts in the repository. Ask the user only for decisions, priorities,
  risk authority, or information unavailable from evidence.
- Treat drafts and deltas as conversation artifacts, not canonical task state.
- Do not write `.coderail/tasks.json` or edit task state behind the CLI.
- Never stage or commit task changes.
- Do not change business code during contract convergence.
- Any later implementation finishes through
  `python .coderail/coderail.py done`.

## Dispatch and frame

1. If a deterministic red reproduction already exists, route to
   `coderail-diagnose` and stop contract grilling. Do not reopen settled
   product scope merely because a bug needs diagnosis.
2. Otherwise invoke `$coderail-frame` internally with the request, repository
   evidence, and current draft if one exists.
3. Consume its `quick` or `guided` result. Do not expose candidate-lens
   brainstorming or an exhaustive expert checklist to the user.
4. Build or update one live Contract Draft. Do not create a PRD, issue, local
   ticket, alternate handoff, glossary, or ADR as a second source of truth.

## Type the draft

Use exactly one epistemic state for every material item:

- `FACT`: cite observable evidence. A user answer alone is not a fact.
- `ASSUMPTION`: name its owner, falsifier, and risk. Link every high-risk
  assumption to an `X` stop item.
- `DECISION`: name the person or authority that accepted the choice.
- `UNKNOWN`: mark exactly one of blocking or deferred.

Never silently promote an answer from `ASSUMPTION` to `FACT` or `DECISION`.
Record it as `DECISION` only when the user actually accepts a choice; otherwise
retain its prior state and expose the remaining uncertainty.

Render the full draft in this order:

```text
CONTRACT DRAFT

G - Goal
  [G.1][DECISION][owner=user] <outcome>

T - Task
  [T.1][ASSUMPTION][owner=agent][risk=low][falsifier=<condition>] <slice>

S - Scope
  [S.1][FACT][evidence=<repository or command>] <boundary>

V - Verify
  [V.1][FACT][evidence=<command>] <observable acceptance>

X - Stop
  [X.1][UNKNOWN][blocking=false][deferred=true] <stop or deferral>

P - Persist
  [P.1][FACT][evidence=<existing CodeRail records>] <persistence boundary>

READINESS
  ready: yes | no
  blocking: <item ids | none>
  deferred: <item ids | none>
  slice-reversible: yes | no
  next-question-reason: <reason | none>
```

## Quick path

When frame returns `quick`, produce the typed Contract Draft without asking a
user-facing question. Recheck that all six coordinates exist, verification is
executable or explicitly manual, no blocking `UNKNOWN` remains, and the slice
is reversible at a cost appropriate to its risk.

If any check fails, change to the guided path instead of declaring readiness.
If all checks pass, show the draft and request explicit user confirmation.
Quick path bypasses the interview, never confirmation or CodeRail activation.

## Guided path

When frame returns `guided`, show the current draft only when it helps the user
understand the decision, then ask exactly one outcome-level question and wait.
Use this complete shape:

```text
focus: <one boundary>
question: <one plain-language choice>
recommendation: <the safest reversible default>
reason: <why this is the highest-impact unknown>
impact: <which outcome or G/T/S/V/X/P boundary changes>
evidence: <what repository or external evidence was checked>
uncertainty: <what the evidence cannot decide>
reversibility: <cost of changing or inability to undo>
```

Keep technical wording terse for users who already use it accurately.
Otherwise translate choices into observable outcomes. Never ask a novice to
select unexplained architecture labels.

Treat "I do not know" as a valid answer. Use a reversible technical default
only when the user has authorized that class of trade-off. Record the default
as an agent-owned `ASSUMPTION` with a falsifier and risk, not as the user's
decision. If the choice is high-risk, irreversible, or outside the user's
authority, keep the `UNKNOWN` blocking and ask one authorization or escalation
question next.

## Draft Delta

After every answer or newly discovered fact, update the live draft and emit a
Draft Delta. Only changed item references and readiness changes may appear;
omit unchanged coordinates.

```text
DRAFT DELTA after answer <id>

CHANGED
  [add][<item id>][<state>] <new item>
  [replace][<item id>][<old state> -> <new state>] <replacement>
  [remove][<item id>][<old state>] <removed item>

READINESS CHANGED
  ready: <before> -> <after>
  blocking: <before> -> <after>
  next-question-reason: <new reason | none>

UNCHANGED
  omitted by contract
```

Re-run the readiness rules after the delta. Ask another question only when one
blocking unknown remains and its answer can change a coordinate, evidence
need, stop condition, or persistence decision.

## Reversible-slice readiness

Stop interviewing at reversible-slice readiness, not at exhaustive certainty.
Readiness requires:

- every `G`, `T`, `S`, `V`, `X`, and `P` coordinate has a typed item;
- no blocking `UNKNOWN` remains and every other `UNKNOWN` is deferred;
- every `FACT` cites evidence;
- every `ASSUMPTION` has an owner and falsifier;
- every high-risk `ASSUMPTION` links to an `X` stop item;
- every `DECISION` names its owner;
- `V` contains executable or explicit manual verification;
- the proposed slice is reversible at a cost appropriate to its risk.

Do not use numeric confidence, entropy, readiness, or information-gain scores.

## Delay promotion

Conversation may propose a glossary or ADR candidate, but do not promote it
during grilling merely because the wording sounds useful.

- Promote a glossary candidate only when it is scenario-consistent,
  code-consistent, contradiction-resolved, and supported by evidence.
- Promote an ADR candidate only when it is hard to reverse, surprising without
  context, represents a real trade-off, has evidence, and names the decision
  owner.

Keep failed candidates conversational or explicitly deferred. If a candidate
passes later, persist it only through the repository's existing optional
decision or terminology location; never create required parallel context.

## Confirmation and activation

Once readiness is true, present the final typed draft and ask for explicit user
confirmation. Do not activate from silence, an inferred preference, or frame's
recommendation.

After confirmation, translate only the accepted contract through the public
interface:

```bash
python .coderail/coderail.py start "<task>" \
  --goal "<goal>" \
  --files "<allowed path or glob>" \
  --avoid "<forbidden paths>" \
  --verify "<command>" \
  --tests "<promised test path>" \
  --accept "<acceptance item>"
```

Use repeatable flags as needed. If an accepted `X` or `P` condition cannot be
represented honestly through the public workflow, keep the contract as a
proposal and stop instead of writing internal state directly.
