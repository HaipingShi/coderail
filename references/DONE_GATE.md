# Done Gate

Done Gate is CodeRail's verification-before-complete rule.

A task cannot be marked done merely because the agent believes the implementation is finished. It must pass the done gate.

## Gate checks

A task may be completed only when:

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

## Gate result

`done_gate.py` returns:

- `pass` when completion is allowed.
- `blocked` when a required condition is missing.
- `warning` when completion is allowed but follow-up cleanup is recommended.

## Non-goals

Done Gate does not replace CI, code review, security review, or human product judgment. It is a repo-local completion gate for AI coding workflows.
