# CodeRail Kernel

CodeRail is a repo-local governance rail for AI coding agents.

## K0 North Star

Direction anchor. Every non-trivial action maps to `docs/NORTH_STAR.md`.

## K1 CodeRail Coordinate

Task coordinate. Every task compresses to G/T/S/V/X/P before implementation.
Use Full Rail for code, data, runner, schema, dependency, release, and external
interface work. Use Light Rail for theory, positioning, principles, philosophy,
terminology, ADRs, and document drafts.

## K2 Task Contract

Executable task boundary. A task has ID, dependencies, acceptance, completion evidence, and a Coordinate.

## K3 TDD Gate

Correctness-sensitive work records Red-Green-Refactor evidence or an explicit waiver.

## K4 Done Gate

Verification-before-complete. No done without passing V or explicit manual acceptance.
For Light Rail, review/decision/manual acceptance can be valid evidence; fake
test claims and out-of-scope edits still block completion.

## K5 Tool-Native Enforcement

Use permissions, hooks, CI, tests, and scripts when possible. Prompt rules are fallback.

## K6 Handoff

Event-triggered snapshot, never a log dump. Handoff carries a Coordinate Summary and next action.

## K7 Asset Boundary

Raw material, working notes, candidates, permanent project assets, generated artifacts, and releases are different.

## K8 Trace Graph

No meaningful action without source, target, modified files/assets, validation evidence, and persistence link.

## K9 Blueprint Gate

Complex systems need current architecture, data, deployment, UI flow, and lifecycle diagrams.

## K10 Auto Commit / Closeout Gate

An agent may stop only after naming task result, auto-commit action, handoff trigger check, resume anchor, and one next executable step.

## K11 CI Gate

Run available non-decision CI checks before stopping or handing off.

## Productization spine

v0.6 adds three runtime surfaces:

1. Coordinate Contract Draft — formal pre-implementation gate.
2. Runtime State Inspect — inspectable status from repo-local files.
3. Done Gate — verification-before-complete.

v0.7 adds Blueprint Gate. v0.7.1 adds Closeout Gate for deterministic resume state. v0.7.2 makes safe task-scoped commits automatic and adds CI Gate. v0.7.3 adds TDD Gate.
