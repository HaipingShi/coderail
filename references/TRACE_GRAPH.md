# Trace Graph

K7 rule: no meaningful action without a trace link.

Trace is a small append-only relationship log, not a graph database. `docs/TRACELOG.jsonl` is the source of truth; `docs/TRACE_INDEX.md` is generated for humans.

## Event types

intent, align, task, decision, research, attempt, change, verify, handoff, lesson.

## Edge types

serves, derived_from, implements, modifies, validated_by, depends_on, supersedes, blocks, relates_to.

## Minimal event

```json
{"id":"TR-...","ts":"...","type":"change","summary":"...","task":"T-001","north_star":"NS-001","files":["src/x.py"],"modifies":["src/x.py"],"coordinate":{"goal":"...","task":"...","verify":["pytest"],"persist":["TASKS","TRACE"]}}
```

Do not store full chat logs, full terminal logs, full git diffs, secrets, or large artifacts.
