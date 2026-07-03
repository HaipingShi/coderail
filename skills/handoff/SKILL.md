---
name: handoff
description: Generate an H0-H3 handoff decision and update docs/HANDOFF.md only when needed. Use when switching agents, ending a batch, blocked, failing, or resuming long work.
---

# Handoff

Handoff is a current-state snapshot, not an execution log.

## Handoff levels

- H0 No update: same agent, same batch, low-risk task, harness passed, no new decision.
- H1 Delta: normal task done; write 5-10 lines only if helpful.
- H2 Rolling snapshot: execution batch ended, PR/review ready, context nearing limit, or task group switch.
- H3 Full handoff: new agent, long interruption, blocked, user decision, North-Star change, unresolved harness failure, forbidden file violation, high-risk migration/API/schema/security change.

## Budget

- `docs/HANDOFF.md`: target under 120 lines.
- Delta prompt: 200-500 words.
- Resume prompt: 800-1200 words.
- Full handoff prompt: under 2000 words.

## Do not put in HANDOFF

- full terminal logs
- full git diff
- old task history
- complete test output
- long background explanation
- rejected candidates
- durable architecture decisions
- reusable failure lessons

Use:

- `docs/RUNLOG.md` for detailed execution history.
- `docs/DECISIONS.md` for durable decisions.
- `docs/LESSONS.md` for reusable lessons.
- `docs/ASSETS.md` for asset state.

## Output

Return:

```markdown
## Handoff Trigger Check

Level: H0 | H1 | H2 | H3
Reason:
HANDOFF.md update required: yes | no

## Handoff Snapshot

Current task:
North-Star status:
Done:
Blocked:
Tests:
Important files:
Next action:
Resume prompt:
```
