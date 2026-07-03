# Kernel Reference

## K0 North-Star Kernel

Every coding action must map to the current Outcome, Current Bet, Invariants, or Current Slice in `docs/NORTH_STAR.md`.

K0 is mandatory because users often begin with incomplete plans and develop through exploration. The agent must not only follow the local conversation. It must repeatedly look up at the persistent project direction.

## K1 Task Contract

Every task must have task ID, North-Star Link, acceptance, allowed files, forbidden files, and harness.

## K2 Execution Rhythm

Plan in fine-grained steps. Execute in longer authorized batches. Pause only at defined risk boundaries.

## K3 Harness Gate

No task is done until the harness passes or manual acceptance is explicitly recorded.

## K4 Tool-Native Enforcement

Use permissions, hooks, CI, branch protection, pre-commit, and review gates when possible. Prompt rules are fallback.

## K5 Handoff / Continuation

Handoff is event-triggered and short. It is not the history log.

## K6 Asset Boundary

Raw material, working notes, candidates, permanent project assets, generated artifacts, and release artifacts must remain distinct.
