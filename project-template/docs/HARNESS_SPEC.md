# Harness Spec

## Global Checks

Replace these with project-specific commands.

```bash
# Examples:
pnpm lint
pnpm typecheck
pnpm test
pytest
```

## Task Checks

### T-001 Example task

```bash
# task-specific command here
```

Pass criteria:

- 

## Manual Acceptance

Use this only when automatic verification is not enough.

- Steps:
- Expected result:
- Evidence:
- Accepted by:
- Date:

## Validation hierarchy

1. Executable harness: tests, lint, typecheck, build, migration dry-run.
2. Static acceptance: schema diff, API contract, snapshot, golden file, allowed files.
3. Tool-native enforcement: permissions, hooks, CI, branch protection, pre-commit.
4. Human review: high-risk product, security, permissions, payment, privacy, destructive migration.
5. Agent critical check: soft gate only; never enough to mark done.
