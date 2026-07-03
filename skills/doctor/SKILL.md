---
name: doctor
description: Inspect whether CodeRail is installed correctly and whether docs are becoming too stale or too heavy. Use before adopting the kit or when workflow feels noisy.
---

# Doctor

Run a lightweight health check of the governance setup.

## Checks

1. `AGENTS.md` exists and mentions North-Star Kernel.
2. `docs/NORTH_STAR.md` exists and is under 100 lines.
3. `docs/TASKS.md` exists and tasks have North-Star Link, Allowed Files, Acceptance, and Harness.
4. `docs/HARNESS_SPEC.md` exists and defines global checks.
5. `docs/HANDOFF.md` exists and is under 120 lines unless H3.
6. `docs/ASSETS.md` exists when raw material, generated docs, or release artifacts are used.
7. `docs/LESSONS.md` is not being used as a full log.
8. No task is marked done without harness result.
9. `git status` has no unexpected changes.

## Optional script

If you can access this package locally:

```bash
python3 scripts/doctor.py --target .
```

## Output

```markdown
## Governance Doctor Report

Status: healthy | usable with warnings | unhealthy

Missing files:
- 

Oversized files:
- 

Task contract issues:
- 

Harness issues:
- 

Handoff issues:
- 

North-Star issues:
- 

Recommended next fixes:
1. 
2. 
3. 
```
