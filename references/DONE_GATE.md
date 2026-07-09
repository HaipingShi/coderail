# Done Gate

Done Gate is CodeRail's verification-before-complete rule.

A task cannot be marked done merely because the agent believes the implementation is finished. It must pass the done gate.

Done Gate is not Closeout Gate. Passing Done Gate allows `done`; it does not by itself justify stopping without auto-commit action, handoff trigger check, and a next executable step.

## Gate checks

A Full Rail task may be completed only when:

1. It has a CodeRail Coordinate.
2. G still maps to the North Star.
3. T is completed.
4. S was respected.
5. V has a passing harness result or explicit manual acceptance.
6. X is not triggered, or the triggered stop condition is resolved and recorded.
7. P is synced: TASKS and TRACE are mandatory; HANDOFF, DECISIONS, LESSONS, ASSETS are updated when relevant.
8. There is a verify trace event for the task.
9. `docs/TRACE_INDEX.md` is current.
10. Handoff Trigger Check has been performed.

A Light Rail task may use lighter completion evidence for docs-only or
design-only work:

1. It still needs a Coordinate with goal, task, scope boundary, verify/manual
   acceptance, stop conditions, and persistence.
2. S must be respected and forbidden files still block completion.
3. P must include TASKS and a durable backlink: TRACE, DECISIONS, RUNLOG,
   HANDOFF, or explicit manual acceptance recorded in the task.
4. Verification may be a review, decision acceptance, trace event, or explicit
   manual acceptance. Do not pretend an executable harness ran.
5. Historical warnings from old closed tasks are historical debt, not current
   blockers for the active task.

## Gate result

`done_gate.py` returns:

- `pass` when completion is allowed.
- `blocked` when a required condition is missing.
- `warning` when completion is allowed but follow-up cleanup is recommended.

Diagnostic output should distinguish:

- `must-fix blocker`: missing current evidence, scope violation, failed verify, or forbidden changes.
- `warning`: current cleanup that does not invalidate completion.
- `historical debt`: old closed-task debt that should not block the current task by default.
- `optimization opportunity`: friction signals such as long handoff, long TASKS, or docs/design tasks over-constrained by Full Rail.

## Non-goals

Done Gate does not replace CI, code review, security review, or human product judgment. It is a repo-local completion gate for AI coding workflows.

Done Gate also does not replace closeout. Use `references/CLOSEOUT_GATE.md` or `scripts/closeout_check.py` before stopping after substantial work.
