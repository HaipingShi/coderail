---
name: coderail-two-axis-review
description: "Review the active CodeRail task on two independent axes: repository standards and task-contract intent. Use before closeout, for work-in-progress review, or when implementation may be correct-looking but misaligned with scope or acceptance."
---

# CodeRail Two-Axis Review

Review one pinned task delta twice so code quality cannot mask incorrect intent,
and apparent spec compliance cannot mask repository violations.

## CodeRail boundary

- Treat the active CodeRail task as the review unit.
- Read `.coderail/tasks.json` only to locate the task activation baseline.
- Do not write `.coderail/tasks.json` or edit task state behind the CLI.
- Never stage or commit task changes.
- Create no review artifact unless its path is already inside task scope.
- Keep a requested read-only review read-only. If findings are accepted and
  fixed in the active task, finish through
  `python .coderail/coderail.py done`.
- Review supplements verification; it never replaces scope checks, registered
  commands, the canonical repository snapshot, or finalization.

## Pin the delta

1. Resolve the `[~]` task in `docs/TASKS.md` and its stored activation
   `baseline.head`. Treat generated status projections as potentially stale;
   report a disagreement, but do not replace the hot task's ownership fact.
2. Validate the baseline with `git rev-parse`.
3. Review the complete worktree delta from that point, including staged,
   unstaged, deleted, renamed, and untracked task-owned paths.
4. If no stored baseline exists, use `HEAD` only when all task work is known to
   be uncommitted. Otherwise stop and request an explicit fixed point.
5. Fail early if the fixed point is invalid or the task delta is empty.

Capture the fixed point once. Both axes must inspect the same delta.

## Axis 1: Standards

Read repository instructions and documented conventions, then report:

- concrete violations with file and tight line references;
- correctness, security, maintainability, or portability regressions;
- missing tests required by repository policy;
- advisory design smells only when they create real change risk.

Repository rules override generic heuristics. Do not report formatter or linter
findings that the registered tooling already provides.

## Axis 2: Contract

Use the active task's Goal, Task, Scope, Verify, Stop, acceptance items, and
North Star mapping as the specification. Report:

- acceptance behavior that is missing or partial;
- behavior added outside the accepted goal;
- paths outside S or conflicts with X;
- implementation that appears to satisfy an item but produces the wrong
  observable result;
- verification that cannot prove the claimed outcome.

Do not invent requirements from personal preference.

## Isolation and output

When the host supports independent agents and the user has permitted them, run
the two axes independently and give each the fixed delta plus only its own
sources. Otherwise review sequentially while keeping separate notes.

Present findings by severity under `Standards` and `Contract`. Do not blend,
average, or let one axis cancel the other. Fix accepted findings inside task
scope, rerun the affected checks, then review the changed delta again.

If review is a required acceptance item, pass its final verdict through the
existing CodeRail closeout inputs. Do not persist it by editing internal state.
