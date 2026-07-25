# Tasks

## Status legend

- `[ ]` todo
- `[~]` doing
- `[!]` blocked
- `[p]` paused
- `[x]` done
- `[f]` failed
- `[r]` reopened

## T-019 Define Guided Convergence WP1 protocol fixtures

Status: [p]
Type: docs
Rail: light

### CodeRail Coordinate

G — Goal
- Make Guided Convergence readiness and knowledge-promotion rules testable before prompt implementation

T — Task
- Define Guided Convergence WP1 protocol fixtures

S — Scope
Allowed:
  - experiments/workflow-lab/fixtures/*.json
  - experiments/workflow-lab/fixtures/*.md
  - experiments/workflow-lab/tests/*.py
  - experiments/workflow-lab/tests/test_skill_contracts.py
  - experiments/workflow-lab/docs/GUIDED_CONVERGENCE_PLAN.md
  - experiments/workflow-lab/README.md
Forbidden:
  - scripts
  - skills
  - project-template
  - references

V — Verify
- Contract Draft and Draft Delta fixtures plus four route scenarios are validated by executable tests
- Run: `python -m unittest discover -s experiments/workflow-lab/tests -v` (must exit 0)

A — Acceptance
- [ ] Contract Draft fixture distinguishes FACT ASSUMPTION DECISION and UNKNOWN
- [ ] Draft Delta contains only changed item references
- [ ] Four initial scenarios encode expected route and at most one first question
- [ ] Readiness and glossary ADR promotion invariants are executable

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

Resume anchor: docs/TASKS.md#T-019

Next executable step: Continue in manual mode; no dependency-ready autonomous task is available to recommend.

Auto commit: disabled
Pause reason: dirty-fork
Resume command: coderail switch --to T-019
