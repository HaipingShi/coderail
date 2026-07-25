# Handoff

Handoff Level: H3
Task: T-019
Reason: explicit dirty-fork waiver before switching to Ignore phantom Git modifications on Windows

## Coordinate Summary

- Current owner remains `T-019`.
- No implementation commit was created by the failed switch.
- No destination task was activated.

## Dirty Paths

- `.coderail/tasks.json` ( M)
- `docs/CODERAIL_STATUS.md` ( M)
- `docs/TASKS.md` ( M)
- `docs/TRACELOG.jsonl` ( M)
- `docs/TRACE_INDEX.md` ( M)
- `experiments/workflow-lab/README.md` ( M)
- `experiments/workflow-lab/docs/GUIDED_CONVERGENCE_PLAN.md` ( M)
- `experiments/workflow-lab/fixtures/contract-draft.md` (??)
- `experiments/workflow-lab/fixtures/draft-delta.md` (??)
- `experiments/workflow-lab/fixtures/promotion-cases.json` (??)
- `experiments/workflow-lab/fixtures/protocol.json` (??)
- `experiments/workflow-lab/fixtures/scenarios.json` (??)
- `experiments/workflow-lab/tests/test_guided_convergence_protocol.py` (??)

## Decision Required

- Continue current: `coderail switch --continue-current`
- Carry a fingerprinted dirty baseline: `coderail switch "new task" --dirty-fork`

## Auto Commit

- Action: not requested
- Automatic push: never

## Next Executable Step

- Choose exactly one command from Decision Required.
