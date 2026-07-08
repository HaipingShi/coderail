# Runtime State Inspect

Runtime State Inspect is CodeRail's repo-local status surface.
It answers: where is the project now, what is active, what is blocked, and what is safe to do next?

It deliberately avoids MCP runtime, web preview, graph database, or background execution. The source of truth remains the repository files:

- `docs/NORTH_STAR.md`
- `docs/TASKS.md`
- `docs/CONTRACTS.md`
- `docs/TRACELOG.jsonl`
- `docs/TRACE_INDEX.md`
- `docs/HANDOFF.md`
- `docs/DECISIONS.md`
- `docs/LESSONS.md`
- `docs/ASSETS.md`

## Inspect output

`inspect_state.py` writes or prints a compact status panel:

- Current North Star
- Active Coordinate
- Active Tasks
- Draft Contracts
- Verification Gaps
- Trace Gaps
- Handoff State
- Recommended Next Action

## Relationship to doctor

`doctor.py` checks governance health.
`inspect_state.py` shows the current runtime state.

Doctor is for installation and compliance gaps.
Inspect is for daily continuation.
