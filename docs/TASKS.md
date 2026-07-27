# Tasks

## Status legend

- `[ ]` todo
- `[~]` doing
- `[!]` blocked
- `[p]` paused
- `[x]` done
- `[f]` failed
- `[r]` reopened

## T-042 Issue WP6 guided-convergence adoption review

Status: [p]
Display id: T-042
Type: docs
Rail: light

### CodeRail Coordinate

G — Goal
- Convert the frozen v3-v5 evidence into a final CodeRail adoption decision that protects novice users and preserves kernel authority

T — Task
- Issue WP6 guided-convergence adoption review

S — Scope
Allowed:
  - experiments/workflow-lab/docs/WP6_ADOPTION_REVIEW.md
  - experiments/workflow-lab/docs/GUIDED_CONVERGENCE_PLAN.md
  - experiments/workflow-lab/docs/WP5_EVALUATION_REPORT.md
  - experiments/workflow-lab/README.md
  - experiments/workflow-lab/tests/test_wp6_adoption_review.py
Forbidden:
  - src/**
  - tests/**
  - coderail/**
  - experiments/workflow-lab/evaluation-v5/**
  - experiments/workflow-lab/skills/**
  - package.json
  - package-lock.json

V — Verify
- One evidence-linked REVISE decision explicitly withholds native integration and hooks while preserving a bounded future research path
- Run: `python -m unittest discover -s experiments/workflow-lab/tests -v` (must exit 0)

A — Acceptance
- [ ] The review makes exactly one top-level ADOPT, REVISE, or REJECT decision and distinguishes treatment disposition from native integration
- [ ] The decision cites v4 and v5 evidence, including the s2 provider-gate stop, unsupported assumptions, clear quick path, token economy, and missing implementation evidence
- [ ] No smart hook, kernel change, native skill installation, later v5 seed, or C5p execution is authorized
- [ ] A future revision must use a new frozen protocol and novice-facing questions must request outcomes rather than mechanisms
- [ ] The plan, report, README, and executable consistency test agree on the final decision
- [ ] All workflow-lab tests pass

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

Resume anchor: docs/TASKS.md#T-042

Next executable step: Continue in manual mode; no dependency-ready autonomous task is available to recommend.

Auto commit: disabled
Pause reason: dirty-fork
Resume command: coderail switch --to T-042
