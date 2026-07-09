---
name: doctor
description: Run CodeRail health checks, including contracts, coordinates, TDD, done/closeout readiness, inspect state, trace, and blueprint awareness.
---

# doctor

Run:

```bash
python3 scripts/doctor.py --target .
```

Doctor checks installation and governance health. It is not the same as `/inspect`, which shows current runtime state.

## Readout

Summarize:

- Must-fix blockers
- Warnings
- Historical debt
- Optimization opportunities
- North Star health
- Contract Draft health
- Coordinate coverage
- TDD Gate health
- Harness / done gate readiness
- Closeout / handoff readiness
- CI Gate readiness
- Handoff state
- Asset Boundary
- Trace Graph
- Runtime inspect status
- Suggested next fixes

Treat "high production but high entanglement" as a governance friction signal:
long HANDOFF, long TASKS, noisy warnings, docs-only work on Full Rail, and
historical debt mixed into current blockers.

Keep the final answer concise.
