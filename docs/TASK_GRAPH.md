# Task Graph

The formal task graph is generated from explicit `depends_on`, `blocks`, and
`supersedes` registrations in `.coderail/tasks.json` and append-only decision
events in `docs/TRACELOG.jsonl`.

Uncertain model suggestions stay in `docs/TRACE_CANDIDATES.jsonl` until
evidence or explicit confirmation promotes them.
