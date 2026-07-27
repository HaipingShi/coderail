# Tasks

## Status legend

- `[ ]` todo
- `[~]` doing
- `[!]` blocked
- `[p]` paused
- `[x]` done
- `[f]` failed
- `[r]` reopened

## T-038 Preflight wp5-v5 schema and execution runner

Status: [p]
Type: feature
Rail: full

### CodeRail Coordinate

G — Goal
- Prove the refrozen v5 schema is service-compatible with zero task or oracle payloads and prepare a seed-aware runner without starting subject trials

T — Task
- Preflight wp5-v5 schema and execution runner

S — Scope
Allowed:
  - experiments/workflow-lab/evaluation-v5/preflight/**
  - experiments/workflow-lab/scripts/run_evaluation_v5.py
  - experiments/workflow-lab/tests/test_evaluation_v5_preflight.py
  - experiments/workflow-lab/README.md
  - experiments/workflow-lab/docs/WP5_EVALUATION_REPORT.md
  - experiments/workflow-lab/docs/WP5_V5_DESIGN.md
  - docs/HANDOFF.md
Forbidden:
  - src
  - tests
  - experiments/workflow-lab/evaluation-v5/freeze.json
  - experiments/workflow-lab/evaluation-v5/manifest.json
  - experiments/workflow-lab/evaluation-v5/rubric.json
  - experiments/workflow-lab/evaluation-v5/workflows

V — Verify
- A zero-task gpt-5.4 schema request passes, preflight metadata proves no task or oracle payload was sent, frozen hashes remain unchanged, and no subject or judge result exists
- Run: `python -m unittest discover -s experiments/workflow-lab/tests -v` (must exit 0)

A — Acceptance
- [ ] The runner reads primary workflows, contingency workflows, canonical seeds, and sampling plan from manifest.json
- [ ] The service accepts model-output.schema.json for protocol wp5-v5
- [ ] Preflight sends zero task and oracle payloads and starts zero subject batches
- [ ] All v5 frozen hashes remain unchanged
- [ ] No v5 results directory or trial output is created

X — Stop
- Stop and ask if changes are needed outside the allowed files.

P — Persist
- TASKS, TRACE

Task result: stage-complete

Harness result: passed

Handoff level: H1

Handoff updated: no

Inspect status: refreshed

Drive decision: BLOCKED_DECISION

Resume anchor: docs/TASKS.md#T-038

Next executable step: Continue in manual mode; no dependency-ready autonomous task is available to recommend.

Auto commit: disabled
