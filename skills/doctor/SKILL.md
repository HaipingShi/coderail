---
name: doctor
description: Inspect whether CodeRail is installed correctly and report health across North Star, Coordinate, Task Contract, Harness, Handoff, Asset Boundary, and Trace Graph. Use before adopting the kit or when workflow feels noisy.
---

# Doctor

Run a lightweight health check of the governance setup across seven sections.

## Checks

1. `AGENTS.md` exists and mentions North-Star Kernel and CodeRail Coordinate.
2. `docs/NORTH_STAR.md` exists and is under 100 lines.
3. **Coordinate**: tasks in `docs/TASKS.md` carry a complete CodeRail Coordinate (G/T/S/V/X/P); done tasks show V and P (TASKS + TRACE).
4. `docs/HARNESS_SPEC.md` exists and defines global checks.
5. `docs/HANDOFF.md` exists, is under 120 lines unless H3, and has a Coordinate Summary.
6. `docs/ASSETS.md` exists when raw material, generated docs, or release artifacts are used.
7. `docs/LESSONS.md` is not being used as a full log.
8. No task is marked done without a harness result.
9. **Trace Graph**: `docs/TRACELOG.jsonl` and `docs/TRACE_INDEX.md` are present; no change events without task/north_star; no verify events without harness_result; index is fresh.
10. `git status` has no unexpected changes.

## Coordinate health score

Report:

- coordinate coverage (share of tasks with a coordinate block)
- missing G
- missing V
- scope violations (forbidden files touched)
- missing P
- trace events without a coordinate

## Optional script

```bash
python3 scripts/doctor.py --target .
```

This integrates `coordinate_check.py` and `trace_doctor.py`.

## Output

```markdown
## Governance Doctor Report

Status: healthy | usable with warnings | unhealthy

### North Star
- 

### Coordinate
- coverage:
- missing G:
- missing V:
- scope violations:
- missing P:

### Task Contract
- 

### Harness
- 

### Handoff
- 

### Asset Boundary
- 

### Trace Graph
- 

Suggested fixes:
- /align
- /task-contract
- /trace
- /link
- /drift-check
```
