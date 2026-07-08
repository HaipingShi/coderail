# CodeRail Kernel

CodeRail is a repo-local governance rail for AI coding agents.

## K0 North Star

Direction anchor. Every non-trivial action maps to `docs/NORTH_STAR.md`.

## K1 CodeRail Coordinate

Task coordinate. Every task compresses to G/T/S/V/X/P before implementation.

## K2 Task Contract

Executable task boundary. A task has ID, dependencies, acceptance, completion evidence, and a Coordinate.

## K3 Done Gate

Verification-before-complete. No done without passing V or explicit manual acceptance.

## K4 Tool-Native Enforcement

Use permissions, hooks, CI, tests, and scripts when possible. Prompt rules are fallback.

## K5 Handoff

Event-triggered snapshot, never a log dump. Handoff carries a Coordinate Summary and next action.

## K6 Asset Boundary

Raw material, working notes, candidates, permanent project assets, generated artifacts, and releases are different.

## K7 Trace Graph

No meaningful action without source, target, modified files/assets, validation evidence, and persistence link.

## Productization spine

v0.6 adds three runtime surfaces:

1. Coordinate Contract Draft — formal pre-implementation gate.
2. Runtime State Inspect — inspectable status from repo-local files.
3. Done Gate — verification-before-complete.
