# Governance Metrics

Track only lightweight, actionable metrics.

## Per-task metrics

| Date | Task | First-pass harness | Reopened | Forbidden file violation | Drift detected | Coordinate complete | Handoff level | Human interruption count |
|---|---|---:|---:|---:|---:|---|---|---:|
|  |  |  |  |  |  |  |  |  |

## Trace metrics

| Date | Orphan events | Done-without-verify | Trace coverage | Handoff trace-link coverage |
|---|---:|---:|---:|---:|
|  |  |  |  |  |

Suggested thresholds:

- First-pass harness rate should improve over time.
- Handoff H3 should be rare outside new-agent or blocked work.
- Drift detections should produce either a North-Star update or task deletion.
- Reopened tasks should produce a specific lesson only when the lesson is reusable.
- Orphan event count should trend toward zero; spikes indicate a `/link` pass is due.
- Done-without-verify should be zero; any non-zero value means a gate was skipped.
- Trace coverage (tasks with at least one trace event) should rise toward 100%.
- Handoff trace-link coverage (H1/H2/H3 handoffs with a handoff trace) should be high.

Trace metric definitions:

- **Orphan events** — trace events with no task, north star, or file link.
- **Done-without-verify** — done tasks whose trace log has no `verify` event.
- **Trace coverage** — share of tasks in `TASKS.md` that have at least one trace event.
- **Handoff trace-link coverage** — share of H1/H2/H3 handoffs that wrote a `handoff` trace event.
