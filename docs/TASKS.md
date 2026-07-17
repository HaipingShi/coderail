# Tasks

## Status legend

- `[ ]` todo
- `[~]` doing
- `[!]` blocked
- `[p]` paused
- `[x]` done
- `[f]` failed
- `[r]` reopened

## T-017 Accept Markdown code-formatted scope paths

Status: [x]
Display id: T-017
Type: bug
Rail: full

### CodeRail Coordinate

G — Goal
- Treat exact Markdown inline-code wrappers around allowed and forbidden path patterns as presentation syntax, while preserving scope and safety semantics.

T — Task
- Accept Markdown code-formatted scope paths

S — Scope
Allowed:
  - scripts/done_gate.py
  - tests/test_static.py
  - tests/test_closeout.py
  - docs/TASKS.md
  - docs/PROGRESS.md
  - docs/TRACELOG.jsonl
  - docs/TRACE_INDEX.md
  - docs/CODERAIL_STATUS.md
  - docs/LESSONS.md
  - docs/HARNESS_SPEC.md
  - .coderail/**
  - .coderail/coderail.py
  - .coderail/config.json
  - .coderail/reports/done-20260715-073852-T-005.md
  - .coderail/reports/done-20260715-080654-T-006.md
  - .coderail/reports/done-20260715-085402-T-007.md
  - .coderail/reports/done-20260715-090436-T-008.md
  - .coderail/reports/done-20260715-091212-T-009.md
  - .coderail/reports/done-20260715-092227-T-010.md
  - .coderail/reports/done-20260715-102434-T-011.md
  - .coderail/reports/done-20260715-104159-T-012.md
  - .coderail/reports/done-20260716-063430-T-013.md
  - .coderail/reports/done-20260716-070558-T-014.md
  - .coderail/reports/done-20260716-084948-T-015.md
  - .coderail/reports/done-20260716-090441-T-016.md
  - .coderail/spin.json
  - .coderail/tasks.json
Forbidden:
  - scripts/inspect_state.py
  - scripts/repository_state.py

V — Verify
- Plain and exact inline-code-formatted scope paths classify identically; forbidden and sensitive paths remain blocked; targeted and full tests pass.
- Run: `python tests/test_static.py` (must exit 0)
- Run: `python tests/test_closeout.py` (must exit 0)
- Run: `python tests/test_structure.py` (must exit 0)
- Run: `npm run ci` (must exit 0)

A — Acceptance
- [ ] Inline-code allowed paths are accepted as their plain path equivalents
- [ ] Inline-code forbidden paths retain blocking behavior
- [ ] Plain path behavior remains compatible

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

Resume anchor: docs/TASKS.md#T-017

Next executable step: Continue in manual mode; no dependency-ready autonomous task is available to recommend.

Auto commit: requested
