# CodeRail

**Draft before coding. Verify before done. Inspect before handoff.**

CodeRail is a lightweight governance rail for AI coding agents. It keeps long-running coding work aligned through a small repo-local kernel: North Star, CodeRail Coordinate, Coordinate Contract Drafts, task contracts, verification-before-complete, runtime state inspect, short handoffs, asset boundaries, and trace links.

Version: **v0.6.0**

## What v0.6 adds

v0.6 productizes CodeRail without turning it into a loop runtime:

1. **Formal contract draft** — `/coderail:contract-draft` and `docs/CONTRACTS.md` create a visible pre-implementation `Coordinate Contract Draft` for vague, high-risk, cross-module, or mid-session requirements.
2. **Runtime state inspect** — `/coderail:inspect` and `scripts/inspect_state.py` generate `docs/CODERAIL_STATUS.md`, a compact state surface for resuming, debugging drift, or preparing handoff.
3. **Verification-before-complete** — `/coderail:done-gate` and `scripts/done_gate.py` block completion until V passes, S is respected, P is synced, and trace evidence exists.

## Closed loop

```text
North Star
→ Coordinate Contract Draft
→ Task Contract
→ Execute Batch
→ Done Gate
→ Trace
→ Inspect
→ Handoff
```

## Kernel

| | Invariant | Plain meaning |
|---|---|---|
| K0 | North Star | Every action maps to Outcome / Current Bet / Invariants / Current Slice |
| K1 | CodeRail Coordinate | Every non-trivial task compresses to G/T/S/V/X/P before implementation |
| K2 | Task Contract | A task has ID, dependencies, acceptance, and completion evidence |
| K3 | Done Gate | No done without passing verification or explicit manual acceptance |
| K4 | Tool-Native Enforcement | Prefer permissions/hooks/CI over prompt-only rules |
| K5 | Handoff | Event-triggered snapshot with Coordinate Summary, never a log dump |
| K6 | Asset Boundary | Raw material, working notes, candidates, permanent assets, generated artifacts, and releases are different |
| K7 | Trace Graph | No meaningful action without source, target, modification, validation, and persistence links |

## Quick start

```bash
python3 scripts/init_project.py --target /path/to/your/repo --mode standard
python3 scripts/doctor.py --target /path/to/your/repo
```

For Claude Code:

```bash
claude --plugin-dir ./coderail
```

For Codex, register this repository as a plugin source or copy it under your plugin directory. The Codex manifest is `.codex-plugin/plugin.json`.

## Normal session

```text
/coderail:align           # align request to North Star
/coderail:contract-draft  # draft formal G/T/S/V/X/P gate when work is vague or risky
/coderail:task-contract   # accept/finalize task contract in TASKS.md
/coderail:execute-batch   # work inside S until done, blocked, failed, or X fires
/coderail:done-gate       # verify-before-complete
/coderail:done            # sync P, trace, status, and optional handoff
/coderail:inspect         # refresh CODERAIL_STATUS.md
/coderail:handoff         # only when H1/H2/H3 trigger fires
```

## Core files copied into a project

```text
AGENTS.md
CLAUDE.md
docs/NORTH_STAR.md
docs/TASKS.md
docs/CONTRACTS.md
docs/HARNESS_SPEC.md
docs/HANDOFF.md
docs/CODERAIL_STATUS.md
docs/TRACELOG.jsonl
docs/TRACE_INDEX.md
docs/DECISIONS.md
docs/LESSONS.md
docs/ASSETS.md
```

## Scripts

```bash
python3 scripts/contract_check.py --target .
python3 scripts/coordinate_check.py --target .
python3 scripts/done_gate.py --target . --task T-001 --harness-result passed
python3 scripts/trace_event.py --target . --type verify --task T-001 --harness-result passed --summary "tests passed"
python3 scripts/trace_index.py --target .
python3 scripts/inspect_state.py --target . --write
python3 scripts/doctor.py --target .
```

## Boundary

CodeRail is not a CI system, issue tracker, graph database, multi-agent orchestrator, web preview, or workflow runtime. It is a repo-local governance rail for AI coding execution.

It borrows three productization patterns without copying a loop engine:

- Formal draft before implementation.
- Inspectable runtime state from repo-local files.
- Verification-before-complete.

## Layout

```text
.claude-plugin/      Claude Code manifest
.codex-plugin/       Codex manifest
skills/              self-contained SKILL.md files
project-template/    files copied into target repositories
scripts/             local validators, done gate, inspect, trace tools
references/          full schemas and design notes
examples/            optional hooks and marketplace examples
tests/               structure and script smoke tests
```
