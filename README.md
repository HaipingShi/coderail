# CodeRail v0.2

A plugin-style workflow kit for AI coding agents. It keeps AI coding aligned with a project-level North Star, then routes work through task contracts, execution batches, harness gates, asset boundaries, drift checks, and short handoffs.

This package is intentionally not a long prompt. It is a compact kernel plus reusable skills and project templates.

## Core idea

Before implementation, the agent must look up from the local task and answer:

1. What outcome does this serve?
2. What intent level is the user asking at?
3. Which current slice does this belong to?
4. Which invariant must remain true?
5. What should this task not become?
6. What would indicate drift?

That is the North-Star Kernel. All other workflows hang from it.

## Kernel

- K0 North-Star Kernel: keep every task mapped to the current outcome, user intent, invariants, and execution slice.
- K1 Task Contract: task ID, goal, acceptance, allowed files, forbidden files, harness.
- K2 Execution Rhythm: fine-grained plan, long execution, pause only at risk boundaries.
- K3 Harness Gate: no done state without tests or explicit manual acceptance.
- K4 Tool-Native Enforcement: use permissions, hooks, CI, branch protection, and pre-commit where possible.
- K5 Handoff / Continuation: event-triggered handoff, not a verbose log after every micro-step.
- K6 Asset Boundary: classify raw material, working notes, candidate artifacts, permanent assets, generated artifacts, and releases.

## Included skills

Plugin skill commands are namespaced by the plugin when used in Claude Code, for example `/coderail:align`.

- `project-init`: create the repo docs and runtime entry files.
- `align`: run the North-Star alignment check before coding.
- `task-contract`: turn a user request into a task contract.
- `execute-batch`: execute authorized tasks continuously until done, blocked, or drift is detected.
- `done`: run the completion gate, harness, diff review, and state updates.
- `handoff`: produce H0-H3 handoff output with a context budget.
- `asset-boundary`: classify and promote project materials safely.
- `drift-check`: detect project goal drift and documentation rot.
- `harness-repair`: repair failing lint, typecheck, test, CI, or manual acceptance loops.
- `doctor`: inspect whether the governance kit is installed and healthy.

## Claude Code usage

Unzip this package and load it directly:

```bash
claude --plugin-dir ./coderail
```

Then initialize a repository:

```text
/coderail:project-init
```

For a high-level or vague request, start with:

```text
/coderail:align
```

For a concrete coding task:

```text
/coderail:task-contract
/coderail:execute-batch
/coderail:done
```

## Codex usage

This package includes a `.codex-plugin/plugin.json` manifest and `skills/` directory. For local repo testing, place the plugin under `plugins/coderail` and add a repo marketplace file at `.agents/plugins/marketplace.json`. See `examples/codex/marketplace.example.json`.

The same skill names are available through Codex plugin or skill invocation surfaces.

## Generic agent usage

For tools that do not support plugins, copy the project template into your repository:

```bash
python3 coderail/scripts/init_project.py --target /path/to/repo --mode standard
```

Then tell the agent to follow `AGENTS.md` and use the docs under `docs/`.

## No active hooks by default

This package does not run automatic hooks by default. It ships examples only. This avoids surprising command execution. Enable tool-native enforcement explicitly in your own environment after review.

## Minimal workflow

```text
/align
  ↓
/task-contract
  ↓
/execute-batch
  ↓
/done
  ↓
/handoff only if H1/H2/H3 triggers
```

## Boundary

This kit does not replace CI, code review, product management, security scanning, issue trackers, or developer judgment. It only constrains AI coding execution so local implementation stays connected to the project outcome and verification path.
