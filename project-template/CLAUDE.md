# CodeRail Runtime Entry

Follow `AGENTS.md` first. Keep this file short.

Treat CodeRail rules as long-lived project rails. Do not rewrite `AGENTS.md`, `CLAUDE.md`, or CodeRail governance files unless the user explicitly asks for a CodeRail upgrade.

Before coding, confirm a CodeRail Coordinate: G Goal, T Task, S Scope, V Verify, X Stop, P Persist.

For vague or risky work, create a Coordinate Contract Draft before implementation. Use `/coderail:contract-draft` or `docs/CONTRACTS.md`.

Before marking done, run the done gate. V must pass, S must be respected, P must be synced, and TRACE must record the action.

Use TDD Gate for bugs, regressions, parsers, validators, domain logic, APIs, shared utilities, and risky refactors. Required TDD needs Red and Green evidence before done.

Use `/coderail:inspect` before resuming or handing off. Use `/coderail:handoff` only on H1/H2/H3 triggers.

Before stopping after substantial work, produce a closeout packet: task result, auto-commit action, Handoff Trigger Check, resume anchor, and one next executable step. If safe task-scoped files can be committed, commit them instead of asking. If the task is stage-complete but not done, keep it active.

When architecture, data, deployment, UI flow, or lifecycle complexity appears, run Blueprint Gate and keep `docs/BLUEPRINTS.md` current.
