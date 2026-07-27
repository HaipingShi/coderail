# Tasks

## Status legend

- `[ ]` todo
- `[~]` doing
- `[!]` blocked
- `[p]` paused
- `[x]` done
- `[f]` failed
- `[r]` reopened

## T-030 Run frozen wp5-v3 contract trials

Status: [p]
Type: docs
Rail: light

### CodeRail Coordinate

G — Goal
- Execute the schema-preflighted 18-task A/B/C contract simulation with blind judging and report only observed evidence

T — Task
- Run frozen wp5-v3 contract trials

S — Scope
Allowed:
  - experiments/workflow-lab/evaluation-v3/results/**
  - experiments/workflow-lab/scripts/run_evaluation.py
  - experiments/workflow-lab/tests/test_evaluation_v3_results.py
  - experiments/workflow-lab/docs/WP5_EVALUATION_REPORT.md
  - experiments/workflow-lab/README.md
  - experiments/workflow-lab/docs/GUIDED_CONVERGENCE_PLAN.md
Forbidden:
  - scripts
  - project-template
  - skills
  - references
  - experiments/workflow-lab/skills
  - experiments/workflow-lab/evaluation
  - experiments/workflow-lab/evaluation-v2
  - experiments/workflow-lab/evaluation-v3/manifest.json
  - experiments/workflow-lab/evaluation-v3/rubric.json
  - experiments/workflow-lab/evaluation-v3/trial-result.schema.json
  - experiments/workflow-lab/evaluation-v3/model-output.schema.json
  - experiments/workflow-lab/evaluation-v3/judge-output.schema.json
  - experiments/workflow-lab/evaluation-v3/freeze.json
  - experiments/workflow-lab/evaluation-v3/workflows
  - experiments/workflow-lab/evaluation-v3/judge.md
  - experiments/workflow-lab/evaluation-v3/run-spec.md
  - experiments/workflow-lab/evaluation-v3/preflight

V — Verify
- 12 subject batches and 4 blind judge batches cover all 54 cells, aggregate contract metrics, and preserve null follow-through evidence
- Run: `python -m unittest discover -s experiments/workflow-lab/tests -v` (must exit 0)

A — Acceptance
- [ ] all 54 cells have frozen-policy raw output and observation records or explicit identical-input failures
- [ ] all v3 pretrial hashes remain unchanged
- [ ] workflow labels are masked from judge inputs and aggregate metrics come from judge or deterministic runner evidence
- [ ] report states contract-phase limitations and does not make an adoption decision from null implementation evidence

X — Stop
- Stop and ask if changes are needed outside the allowed files.

P — Persist
- TASKS, TRACE
Pause reason: dirty-fork
Resume command: coderail switch --to T-030

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

## T-036 all 54 cells have frozen-policy raw output and observation records or explicit identical-input failures

Status: [ ]
Type: feature
Rail: full

### CodeRail Coordinate

G — Goal
- Deferred from T-028: all 54 cells have frozen-policy raw output and observation records or explicit identical-input failures

T — Task
- all 54 cells have frozen-policy raw output and observation records or explicit identical-input failures

S — Scope
Allowed:
  - to be decided while working
Forbidden:
  - none

V — Verify
- Manually confirm the result works as intended.

X — Stop
- Stop and ask if changes are needed outside the allowed files.

P — Persist
- TASKS, TRACE

## T-037 workflow labels are masked from judge inputs and aggregate metrics come from judge or deterministic runner evidence

Status: [ ]
Type: feature
Rail: full

### CodeRail Coordinate

G — Goal
- Deferred from T-028: workflow labels are masked from judge inputs and aggregate metrics come from judge or deterministic runner evidence

T — Task
- workflow labels are masked from judge inputs and aggregate metrics come from judge or deterministic runner evidence

S — Scope
Allowed:
  - to be decided while working
Forbidden:
  - none

V — Verify
- Manually confirm the result works as intended.

X — Stop
- Stop and ask if changes are needed outside the allowed files.

P — Persist
- TASKS, TRACE
