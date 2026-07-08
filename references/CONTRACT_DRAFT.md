# Coordinate Contract Draft

A Coordinate Contract Draft is CodeRail's formal pre-implementation gate.
It prevents vague intent from becoming code by forcing the agent to compress the work into G/T/S/V/X/P before editing files.

It is not a project-management object and it is not a workflow engine. It is a short draft that becomes either an accepted task contract, a rejected idea, a backlog item, or a user question.

## When to create one

Create a draft before implementation when:

- The request is vague, high-level, or changes direction mid-session.
- The work may touch multiple files or modules.
- The task changes scope, dependencies, data model, public API, security, permissions, payments, or persistence.
- The agent cannot clearly map the work to `docs/NORTH_STAR.md`.
- The user introduces a side requirement while another task is in progress.

## Draft template

```markdown
## CD-XXX Contract title

Status: proposed | accepted | rejected | superseded
Created at:
Source: user | agent | handoff | trace | issue
Trace:

### Coordinate Contract Draft

G — Goal:
- North Star:
- Outcome served:
- Why now:

T — Task:
- Task ID:
- Exact task:
- What this task must not become:

S — Scope:
- Allowed:
  -
- Forbidden:
  -

V — Verify:
- TDD mode: required | optional | waived
- Red check:
- Green check:
- Refactor check:
- Regression check:
- CI check:
- Waiver reason:
- Harness:
  -
- Manual acceptance:
  -

X — Stop:
-
-

P — Persist:
- TASKS:
- HANDOFF:
- DECISIONS:
- LESSONS:
- ASSETS:
- TRACE:

Decision:
- proceed | revise | ask user | split task | backlog

Notes:
-
```

## Acceptance rule

A draft may become an active task only when:

1. G maps to North Star.
2. T is concrete enough to verify.
3. S includes allowed and forbidden scope.
4. V is executable or has explicit manual acceptance.
5. X has real stop conditions.
6. P includes at least TASKS and TRACE.

## Anti-patterns

- Draft says "optimize system" without a precise T.
- G says "finish task" without a North Star link.
- S only lists allowed files and no forbidden boundary.
- V says "looks good" without harness or manual acceptance.
- X is empty.
- P omits TRACE or TASKS.
- User adds a new requirement and the agent silently folds it into the current task.
