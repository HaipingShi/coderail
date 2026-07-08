# CodeRail v0.6.0 Optimization Notes

This package upgrades the current GitHub version into a more productized CodeRail without turning it into a workflow runtime.

## Added

- `Coordinate Contract Draft`: formal pre-implementation gate for vague, high-risk, cross-module, or mid-session requirements.
- `Runtime State Inspect`: repo-local state surface generated from existing CodeRail docs and trace files.
- `Done Gate`: verification-before-complete script and skill.

## New commands

```bash
python3 scripts/contract_check.py --target .
python3 scripts/inspect_state.py --target . --write
python3 scripts/done_gate.py --target . --task T-001 --harness-result passed
```

## Boundary

No MCP runtime, no web preview, no graph database, no task orchestrator. CodeRail remains a repo-local governance rail.
