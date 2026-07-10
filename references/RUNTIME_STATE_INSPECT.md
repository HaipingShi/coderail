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
- Legacy Cutoff
- Active Coordinate
- Active Tasks
- Draft Contracts
- Verification Gaps
- Historical Verification Debt
- Trace Gaps
- Handoff State
- Recommended Next Action
- Auto Commit

## Relationship to doctor

`doctor.py` checks governance health.
`inspect_state.py` shows the current runtime state.

Doctor is for installation and compliance gaps.
Inspect is for daily continuation.

## Legacy cutoff for mature repositories

When CodeRail is adopted after a repository already has task history, configure
the first post-cutover task by document order:

```markdown
## Legacy Cutoff

- Enforcement starts at: T-178
```

Tasks before that anchor remain visible under `Historical Verification Debt`,
but their weak verification evidence does not make the current status blocked.
The anchor and every task after it remain enforced. A doing or blocked task
before the anchor is also treated as current. If the configured anchor is not
found, Inspect fails closed. Without this section, all tasks remain enforced for
backward compatibility.
