# CodeRail Coordinate

The CodeRail Coordinate compresses runtime task state into six fields.

```markdown
## CodeRail Coordinate

G — Goal:
- 

T — Task:
- 

S — Scope:
- Allowed:
  - 
- Forbidden:
  - 

V — Verify:
- 

X — Stop:
- 

P — Persist:
- TASKS:
- HANDOFF:
- DECISIONS:
- LESSONS:
- ASSETS:
- TRACE:
```

## Coordinate Draft Gate

Before creating a task contract, present a Coordinate Draft. If G is vague, S touches high-risk files, V is missing, or X has already fired, stop for alignment instead of coding.

## Anti-patterns

- G says "finish task" instead of mapping to North Star.
- T says "optimize system" without a done boundary.
- S lists allowed files but no forbidden files.
- V says "looks good" without harness or manual acceptance.
- X is empty.
- P omits TRACE or TASKS.
- Mid-session requirements change G but the agent implements directly.
