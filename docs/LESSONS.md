# Lessons

Record reusable failure lessons only.

## Preserve intent, not only the current expansion

Expanding a task glob only at `start` converts a durable ownership rule into a stale file list. Keep the pattern and use the same matcher at closeout. Also validate the final dirty set before changing a task to `[x]`; post-close detection is too late to preserve a truthful lifecycle.

## Success text is part of the transaction

Printing `Done` after the first implementation commit is premature when ledger writes, cleanup, hooks, or a second commit can still change Git state. The success label belongs after the last observable mutation and a fresh evaluation using the same state model as inspect.

## Queued task contracts must hydrate runtime evidence

A queued task activated from TASKS can have complete V and A clauses while `.coderail/tasks.json` contains only its baseline. Runtime reporting must fall back to the committed task contract; otherwise a fully exercised closeout can be recorded as unverified. Only executable-looking backtick spans inside V are hydrated; prose examples and lifecycle arrows remain documentation, not commands.
