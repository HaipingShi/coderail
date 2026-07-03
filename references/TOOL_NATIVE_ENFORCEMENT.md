# Tool-Native Enforcement First

If a rule can be enforced by tools, do not leave it only in prompt text.

Examples:

- Forbidden files: permissions / deny rules.
- Harness gate: CI, hooks, pre-commit, task scripts.
- Done check: `/done` skill or task script.
- High-risk changes: plan/review mode and human approval.
- Branch isolation: worktree or sandbox.
- Repeated failures: regression test or CI gate.

This package ships no active hooks by default. Add hooks only after reviewing them.
