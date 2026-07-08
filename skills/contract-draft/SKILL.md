---
name: contract-draft
description: Create a Coordinate Contract Draft before implementation for vague, high-risk, cross-module, or mid-session requirements.
---

# Contract Draft

Do not write business code. Convert intent into a formal Coordinate Contract Draft.

## Read

- `docs/NORTH_STAR.md`
- `docs/TASKS.md`
- `docs/CONTRACTS.md` if present
- `docs/HARNESS_SPEC.md`
- `git status`

## Output

Write or propose a draft in `docs/CONTRACTS.md`:

```markdown
## CD-XXX Short title

Status: proposed
Created at:
Source:
Trace:

### Coordinate Contract Draft

G — Goal:
- North Star:
- Outcome served:
- Why now:

T — Task:
- Task ID:
- Exact task:
- What this task must not become:

S — Scope:
- Allowed:
  -
- Forbidden:
  -

V — Verify:
- TDD mode: required | optional | waived
- Red check:
- Green check:
- Refactor check:
- Regression check:
- CI check:
- Waiver reason:
- Harness:
  -
- Manual acceptance:
  -

X — Stop:
-

P — Persist:
- TASKS:
- HANDOFF:
- DECISIONS:
- LESSONS:
- ASSETS:
- TRACE:

Decision:
- proceed | revise | ask user | split task | backlog
```

## Rules

- If G cannot map to North Star, stop and ask or update `NORTH_STAR.md`.
- If V cannot be defined, create a harness task or manual acceptance before coding.
- If the request is a side branch, backlog it instead of folding it into the active task.
- After drafting, run or suggest `scripts/contract_check.py --target .`.
