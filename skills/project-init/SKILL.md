---
name: project-init
description: Initialize a repository for CodeRail, including the CodeRail Coordinate template and Trace Graph files. Use when a project lacks NORTH_STAR.md, TASKS.md, HARNESS_SPEC.md, TRACELOG.jsonl, or runtime entry files.
---

# Project Init

Create or update the minimum governance files for the current repository.

## Goal

Install the North-Star Kernel, the CodeRail Coordinate, and the Trace Graph
supporting files without adding unnecessary ceremony.

## Procedure

1. Inspect the repository root.
2. If `AGENTS.md` is missing, create it from the project template.
3. If `CLAUDE.md` is missing and the user uses Claude Code, create it from the project template.
4. Create `docs/` if missing.
5. Create these files if missing:
   - `docs/NORTH_STAR.md`
   - `docs/TASKS.md` (with the CodeRail Coordinate block)
   - `docs/HARNESS_SPEC.md`
   - `docs/HANDOFF.md` (with the Coordinate Summary)
   - `docs/ASSETS.md`
   - `docs/DECISIONS.md`
   - `docs/LESSONS.md`
   - `docs/RUNLOG.md`
   - `docs/TRACELOG.jsonl` (empty append-only log)
   - `docs/TRACE_INDEX.md` (generated index)
6. Do not overwrite non-empty user files without explicit approval.
7. If the user gave only a vague project idea, create `docs/NORTH_STAR.md` with `Status: provisional`.
8. Generate the first task as `T-001` only after the North Star has at least Outcome, Current Bet, Invariants, and Current Slice. The task must carry a CodeRail Coordinate (G/T/S/V/X/P).

## Optional script

If you can access the plugin directory, run:

```bash
python3 scripts/init_project.py --target . --mode standard
```

If the script is unavailable, manually create files using the templates under `project-template/`.

## Output

Return:

```text
Initialized files:
Skipped existing files:
Provisional North Star:
First suggested task (with CodeRail Coordinate):
Next command:
```
