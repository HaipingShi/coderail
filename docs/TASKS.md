# Tasks

## Status legend

- `[ ]` todo
- `[~]` doing
- `[!]` blocked
- `[p]` paused
- `[x]` done
- `[f]` failed
- `[r]` reopened

## T-024 Run frozen wp5-v1 comparative trials

Status: [~]
Type: docs
Rail: light

### CodeRail Coordinate

G — Goal
- Execute and report the frozen A/B/C contract-phase evaluation without changing its tasks, treatments, rubric, schema, or hashes

T — Task
- Run frozen wp5-v1 comparative trials

S — Scope
Allowed:
  - experiments/workflow-lab/evaluation/results/**
  - experiments/workflow-lab/scripts/run_evaluation.py
  - experiments/workflow-lab/tests/test_evaluation_results.py
  - experiments/workflow-lab/docs/WP5_EVALUATION_REPORT.md
  - experiments/workflow-lab/README.md
  - experiments/workflow-lab/docs/GUIDED_CONVERGENCE_PLAN.md
Forbidden:
  - scripts
  - project-template
  - skills
  - references
  - experiments/workflow-lab/skills
  - experiments/workflow-lab/evaluation/manifest.json
  - experiments/workflow-lab/evaluation/rubric.json
  - experiments/workflow-lab/evaluation/trial-result.schema.json
  - experiments/workflow-lab/evaluation/freeze.json
  - experiments/workflow-lab/evaluation/workflows

V — Verify
- all frozen contract-phase trials have raw outputs, independently derived observations, an aggregate report, and explicit limitations
- Run: `python -m unittest discover -s experiments/workflow-lab/tests -v` (must exit 0)

A — Acceptance
- [ ] all 54 workflow-task cells use the frozen model policy or failures are explicitly recorded
- [ ] pretrial hashes remain unchanged throughout execution
- [ ] aggregate metrics are computed from observation records rather than subject self-scoring
- [ ] report distinguishes contract-phase evidence from unmeasured implementation outcomes and makes no premature adoption claim

X — Stop
- Stop and ask if changes are needed outside the allowed files.

P — Persist
- TASKS, TRACE

Task result: blocked

Harness result: passed

Handoff level: H3

Handoff updated: no

Inspect status: refreshed

Drive decision: BLOCKED_DECISION

Resume anchor: docs/TASKS.md#T-024

Next executable step: Continue in manual mode; no dependency-ready autonomous task is available to recommend.

Auto commit: disabled
