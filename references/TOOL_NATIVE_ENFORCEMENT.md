# Tool-Native Enforcement

Use permissions, hooks, CI, pre-commit, and branch protection when available. Prompt rules are fallback.

CodeRail provides `scripts/hook_guard.py` and example hook configs under `examples/`.

Suggested stages:

- prompt start: remind the agent to load CodeRail and treat governance files as long-lived rails
- pre edit: block casual edits to `AGENTS.md`, `CLAUDE.md`, skills, scripts, and references
- stop: run Blueprint Gate and Doctor periodically, preferably in soft mode until the project is fully aligned
