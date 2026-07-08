---
name: doctor
description: Run CodeRail health checks, including contracts, coordinates, done gate readiness, inspect state, trace, and blueprint awareness.
---

# doctor

Run:

```bash
python3 scripts/doctor.py --target .
```

Doctor checks installation and governance health. It is not the same as `/inspect`, which shows current runtime state.

## Readout

Summarize:

- North Star health
- Contract Draft health
- Coordinate coverage
- Harness / done gate readiness
- Handoff state
- Asset Boundary
- Trace Graph
- Runtime inspect status
- Suggested next fixes

Keep the final answer concise.
