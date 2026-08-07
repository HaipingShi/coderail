# Delivery Contract

Delivery is a customer-facing projection, not the internal closeout receipt.
The closeout receipt proves Git and verification facts. The optional Delivery
Contract supplies business facts that CodeRail cannot infer safely.

## Task declaration

Add this explicit block to a task when customer delivery language is needed:

```yaml
### Delivery Contract

delivery:
  task_status: pending
  milestone_status: in_progress
  product_status: not_assessed
  customer_outcome: The accepted capability is available to the customer.
  capability_delta:
    - Added the accepted capability.
  remaining_gaps:
    - Production rollout is not assessed.
  evidence_boundary:
    - Verified locally; no release claim.
  recommended_next:
    id: null
    status: none
    reason: No next task is declared.
  decisions_required: []
  technical_receipt:
    commits: []
    verification: []
    safe_files: []
```

The parser reads only this section and this fixed schema. Nearby project prose
is opaque. `technical_receipt` is populated from the successful closeout; input
values are placeholders and are never accepted as proof.

## Status rules

- CodeRail promotes `task_status` from `pending` to `finalized` only after the
  closeout transaction succeeds.
- Task finalization never promotes `milestone_status` or `product_status`.
  Those fields remain the explicit assessment supplied by the project.
- `planned` means recorded but not recommended, `recommended` means advice
  without authority, and `active` means already active through the normal task
  lifecycle. `none` requires a null id. Recommendation never registers or
  activates a task.
- Missing Delivery Contracts remain compatible. Customer outcome, milestone,
  and product status render as `not_assessed`; the tool does not invent them.

## Client Markdown

After a successful `done` or `done --resume`, CodeRail prints and stores a
customer report under `.coderail/reports/`. Its sections are stable and ordered:

1. 交付结果
2. 能力变化
3. 项目整体状态
4. 未完成与风险
5. 推荐下一任务
6. 需要决策
7. 技术附录

Commits, verification, and exact safe files appear only in the final technical
appendix. The internal `== Done ==` receipt remains separate.

## Current-truth projections

`docs/ASSETS.md` is the registry. Inspect reads only rows marked `Canonical:
yes`, excluding assets whose type is `append-only`. A registered current view
may declare an exact machine marker:

```html
<!-- coderail:current-truth task=T-123 status=active -->
```

Supported marker states are `active`, `in_progress`, `pending-closeout`, and
`finalized`. CodeRail rewrites only this marker, never surrounding prose. The
file must be inside the task's Allowed scope and outside Forbidden scope.

Canonical registration also makes bounded project-authored status assertions
part of the consistency gate. CodeRail binds an assertion only when the same
Markdown section has an exact `Task:` / `Coordinate:` id context, or when one
table/list row contains both the exact id and status. The registered display id
is an alias for its internal `T-nnn` Coordinate. Narrative mentions remain
opaque; for example, prose saying that a task fixed an old `active` incident is
not a current-state assertion.

For a finalized Coordinate, the following assertion values are stale:
`active`, `in_progress`, `pending-closeout`, `verified-commit-pending`, plain
pending commit/closeout variants, bare `pending` in an explicit status/closeout
field, `待提交`, and `待收口`. Inspect reports the exact file and line and blocks
current-truth consistency. CodeRail never guesses how to rewrite project prose:
only the marker is synchronized automatically.

On a pending exact commit the marker is `pending-closeout`; resume changes every
verified marker to `finalized` in the same exact recovery boundary. A newly
declared, out-of-snapshot, forbidden, or unwritable view leaves closeout in
`verified-commit-pending` and prints each file requiring repair. Inspect blocks
healthy status while a finalized task still has a stale marker. Historical
TRACELOG events are append-only evidence and are never treated as current
projection state.

The same fail-closed rule applies to a bounded stale prose assertion. Ordinary
`done` reopens the Coordinate before the exact closeout commit, and
`done --no-commit` refuses to freeze a snapshot that would require later prose
edits. `done --resume` keeps an already verified snapshot pending and returns
the exact repair location if a newly declared assertion appears. A docs-only
follow-up cannot finalize while leaving its own canonical closeout status stale,
so governance repair tasks do not recursively manufacture another apparently
healthy stale projection.

## Migration

No marker migration is required for old repositories. Add a Delivery Contract
only to new or reopened tasks that need a customer-facing assessment. Add
current-truth markers only to canonical views that should participate in
automatic closeout sync. Canonical files may keep human-authored prose, but any
explicit current status bound to a finalized Coordinate must be repaired before
Inspect can pass. Keep historical material in append-only or non-canonical
assets when it must preserve old lifecycle wording.
