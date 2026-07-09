# CodeRail Coordinate

The CodeRail Coordinate compresses runtime task state into six fields.

```markdown
## CodeRail Coordinate

Rail: full | light
Type: feature | bug | refactor | docs | design | research | adr | harness | chore

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
- TDD mode: required | optional | waived
- Red check:
- Green check:
- Refactor check:
- Regression check:
- CI check:
- Harness:

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

## Rail levels

- **Full Rail** is for code, schema, dependencies, data writes, runners, pipelines, external interfaces, migrations, and releases. It requires full G/T/S/V/X/P, executable verification or explicit manual acceptance, TASKS + TRACE persistence, Done Gate, and Closeout.
- **Light Rail** is for theory, product positioning, design principles, philosophy boundaries, terminology, ADRs, and document drafts. It requires a goal, boundary, persistence location, next executable step, and trace/decision backlink or explicit manual acceptance. It does not require a code/test implementation loop when there is no code path.

Current tasks must write `Rail: full` or `Rail: light` explicitly. Inference is only a diagnostic fallback and should not be used as the source of truth for done checks.

## Coordinate Draft Gate

Before creating a task contract, present a Coordinate Draft. If G is vague, S touches high-risk files, V is missing, or X has already fired, stop for alignment instead of coding.

## Anti-patterns

- G says "finish task" instead of mapping to North Star.
- T says "optimize system" without a done boundary.
- S lists allowed files but no forbidden files.
- V says "looks good" without harness or manual acceptance.
- X is empty.
- P omits TRACE or TASKS.
- A docs/design task is forced through Full Rail without code, schema, runner, data, or release risk.
- Mid-session requirements change G but the agent implements directly.
