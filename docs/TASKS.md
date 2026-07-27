# Tasks

## Status legend

- `[ ]` todo
- `[~]` doing
- `[!]` blocked
- `[p]` paused
- `[x]` done
- `[f]` failed
- `[r]` reopened

## T-033 Run and adjudicate wp5-v4 A/B/C comparison

Status: [p]
Type: feature
Rail: full

### CodeRail Coordinate

G — Goal
- Measure whether the revised C improves contract-phase behavior under the frozen v4 protocol without overstating unobserved implementation outcomes

T — Task
- Run and adjudicate wp5-v4 A/B/C comparison

S — Scope
Allowed:
  - experiments/workflow-lab/evaluation-v4/results/**
  - experiments/workflow-lab/tests/test_evaluation_v4_results.py
  - experiments/workflow-lab/README.md
  - experiments/workflow-lab/docs/GUIDED_CONVERGENCE_PLAN.md
  - experiments/workflow-lab/docs/WP5_EVALUATION_REPORT.md
  - docs/HANDOFF.md
Forbidden:
  - src
  - tests
  - experiments/workflow-lab/evaluation-v4/freeze.json
  - experiments/workflow-lab/evaluation-v4/manifest.json
  - experiments/workflow-lab/evaluation-v4/rubric.json
  - experiments/workflow-lab/evaluation-v4/workflows

V — Verify
- All 54 v4 cells and four blind judge batches complete or failures are explicitly recorded, deterministic assertions verify evidence integrity, and the report compares v4 with v3 while withholding adoption
- Run: `python -m unittest discover -s experiments/workflow-lab/tests -v` (must exit 0)

A — Acceptance
- [ ] All 12 subject batches and four blind judge batches complete with the frozen model policy or failures are recorded
- [ ] Exactly 54 trial cells exist and judge inputs remain workflow-masked
- [ ] Frozen v4 hashes remain unchanged
- [ ] The report compares A/B/C and v3/v4 C on observed metrics
- [ ] Implementation fields remain null and no ADOPT decision is made

X — Stop
- Stop and ask if changes are needed outside the allowed files.

P — Persist
- TASKS, TRACE

Task result: done

Harness result: passed

Handoff level: H0

Handoff updated: no

Inspect status: refreshed

Drive decision: BLOCKED_DECISION

Resume anchor: docs/TASKS.md#T-033

Next executable step: Continue in manual mode; no dependency-ready autonomous task is available to recommend.

Auto commit: disabled
Pause reason: dirty-fork
Resume command: coderail switch --to T-033
