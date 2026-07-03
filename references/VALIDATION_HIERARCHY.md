# Validation Hierarchy

Agent self-checks are useful only as soft gates. Completion evidence should follow this hierarchy.

1. Executable harness: tests, lint, typecheck, build, migration dry-run.
2. Static acceptance: schema diff, API contract, snapshot, golden file, allowed files.
3. Tool-native enforcement: permissions, hooks, CI, branch protection, pre-commit.
4. Human review: product goal, security, permissions, payment, privacy, destructive migration, public API.
5. Agent critical check: intent exposure and drift discovery only.

Rules:

- Never mark done from an agent self-check alone.
- Never hide failed tests.
- When hard enforcement exists, use it instead of relying on instructions.
