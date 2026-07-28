# Task Graph

The formal task graph is generated from explicit `depends_on`, `blocks`, and
`supersedes` registrations in `.coderail/tasks.json` and append-only decision
events in `docs/TRACELOG.jsonl`.

Do not draw inferred dependencies here. Put uncertain relationships in
`docs/TRACE_CANDIDATES.jsonl` with `coderail candidate add`; they gain no
execution authority until evidence or explicit confirmation promotes them.

Useful commands:

```text
coderail link T-002 depends_on T-001 --reason "..." --evidence "docs/..."
coderail graph T-002
coderail candidate list
```
