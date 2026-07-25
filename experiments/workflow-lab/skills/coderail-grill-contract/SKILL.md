---
name: coderail-grill-contract
description: Interview the user one decision at a time and convert vague, risky, or cross-module work into a confirmed CodeRail G/T/S/V/X/P contract. Use explicitly before implementation when requirements or authority are not yet settled.
---

# CodeRail Grill Contract

Clarify decision-grade uncertainty without turning ordinary work into a
specification ceremony.

## CodeRail boundary

- Read `AGENTS.md`, `docs/NORTH_STAR.md`, `docs/TASKS.md`, relevant decisions,
  and `git status` before asking repository facts.
- Look up facts in the repository. Ask the user for decisions and authority.
- Do not write `.coderail/tasks.json` or edit task state behind the CLI.
- Never stage or commit task changes.
- Do not change business code during the interview.
- Any later implementation finishes through
  `python .coderail/coderail.py done`.

## Interview

1. State the unresolved decision tree in one sentence.
2. Resolve dependencies between decisions before asking downstream questions.
3. Ask exactly one question at a time and wait for the answer.
4. Give a recommended answer and its main trade-off with every question.
5. Test important answers against concrete edge cases and the current code.
6. Distinguish facts, preferences, and irreversible decisions.
7. Stop expanding when the request is safe enough for one bounded task.

Do not implement or create the task until the user confirms the shared
understanding.

## Contract draft

Produce a concise draft:

```text
G - Goal: outcome and North Star relationship
T - Task: one bounded, demonstrable slice
S - Scope: allowed paths and explicit forbidden paths
V - Verify: commands, promised tests, and acceptance items
X - Stop: decisions or scope changes that halt execution
P - Persist: existing CodeRail records that must remain honest
```

Prefer a vertical slice. Do not create a separate PRD, issue tracker, local
ticket store, or handoff file.

## Confirmation and activation

Ask the user to confirm the draft. After confirmation, translate it through the
public interface:

```bash
python .coderail/coderail.py start "<task>" \
  --goal "<goal>" \
  --files "<allowed path or glob>" \
  --avoid "<forbidden paths>" \
  --verify "<command>" \
  --tests "<promised test path>" \
  --accept "<acceptance item>"
```

Use repeatable flags as needed. If a required X or P condition cannot be
represented safely through the current public workflow, keep the contract as a
proposal and stop rather than writing internal state directly.
