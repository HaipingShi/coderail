---
name: ci-gate
description: Run available non-decision CI/CD checks before stopping, handing off, or auto-committing a completed task.
---

# ci-gate

Use before closeout when a repository has tests, build scripts, CodeRail scripts, or CI workflow files. It includes TDD Gate when available.

## Action

Run:

```bash
python3 scripts/ci_gate.py --target .
```

or:

```bash
npm run ci
```

## Rules

- Run CI/CD checks directly instead of asking the user to run them.
- Stop only when the failure needs a decision, forbidden scope, unavailable dependency, or repeated unclear root cause.
- If CI fails with a clear local fix inside S, fix it and rerun.
- Record failure state in closeout only after the agent has exhausted non-decision fixes.
