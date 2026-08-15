---
name: domain-modeling
description: Build and sharpen the project's domain language. Use when discussing project terminology, writing or editing CONTEXT.md, or recording or editing an ADR in docs/DECISIONS.md.
---

# Domain Modeling

Actively build the project's domain model as you design: challenge terms,
invent edge-case scenarios, and write the glossary and decisions down the
moment they crystallise. Merely reading CONTEXT.md for vocabulary is a habit
any skill can do; this skill is for changing the model, not just consuming it.

## File structure

- `CONTEXT.md` at the repo root — the glossary. Create it lazily when the
  first term is resolved.
- `docs/DECISIONS.md` — the existing ADR log (`ADR-NNN`, Status / Date /
  Task). Do not create a second decision store such as `docs/adr/`.
- Multi-context repos only: a root `CONTEXT-MAP.md` points to each context's
  own `CONTEXT.md`.

## During the session

- **Challenge against the glossary.** When the user uses a term that
  conflicts with CONTEXT.md, call it out immediately and ask which meaning is
  right.
- **Sharpen fuzzy language.** When the user uses vague or overloaded terms,
  propose one precise canonical term.
- **Discuss concrete scenarios.** Stress-test domain relationships with
  specific edge-case scenarios that force precise boundaries between concepts.
- **Cross-reference with code.** When the user states how something works,
  check whether the code agrees; surface contradictions.
- **Update CONTEXT.md inline.** When a term is resolved, update the glossary
  right there — do not batch. CONTEXT.md is a glossary only: no
  implementation details, no specs, no scratch notes.

## Glossary format

```md
# {Context Name}

{One or two sentences: what this context is and why it exists.}

## Language

**Order**:
{One or two sentences defining what the term IS.}
_Avoid_: Purchase, transaction
```

## Offering ADRs

Offer a new `ADR-NNN` entry in docs/DECISIONS.md only when all three hold:

1. **Hard to reverse** — changing your mind later has meaningful cost.
2. **Surprising without context** — a future reader will wonder why.
3. **A real trade-off** — genuine alternatives existed and one was chosen.

If any is missing, skip the ADR. Numbering continues from the highest
existing ADR number; keep the established Status / Date / Task header.

## Rules

- Be opinionated: when several words name one concept, pick the best and list
  the rest under `_Avoid_`.
- Only include terms specific to this project's domain; general programming
  concepts never belong in CONTEXT.md.
- Record glossary and ADR updates through `trace` so each change stays
  attributable to a task and a reason.
