# Lessons

Record reusable failure lessons only.

## Preserve intent, not only the current expansion

Expanding a task glob only at `start` converts a durable ownership rule into a stale file list. Keep the pattern and use the same matcher at closeout. Also validate the final dirty set before changing a task to `[x]`; post-close detection is too late to preserve a truthful lifecycle.

## Success text is part of the transaction

Printing `Done` after the first implementation commit is premature when ledger writes, cleanup, hooks, or a second commit can still change Git state. The success label belongs after the last observable mutation and a fresh evaluation using the same state model as inspect.

## Queued task contracts must hydrate runtime evidence

A queued task activated from TASKS can have complete V and A clauses while `.coderail/tasks.json` contains only its baseline. Runtime reporting must fall back to the committed task contract; otherwise a fully exercised closeout can be recorded as unverified. Only executable-looking backtick spans inside V are hydrated; prose examples and lifecycle arrows remain documentation, not commands.

## Characterize behavior, then delete the translation layer

A shared state model does not reduce complexity while every caller immediately
projects it back into the old shape. Freeze correct behavior first, migrate
callers to the canonical dataclasses, and serialize only at durable storage
boundaries. Treat an adapter with no external consumer as deletion work, not as
compatibility value.

## Split tests around facts, not around command history

A test monolith becomes safer to split once the behavior count is an explicit
invariant. Extract shared repository construction once, move whole test
functions mechanically into responsibility modules, and keep the existing
suite command as a thin deterministic aggregator. This makes each concern
runnable alone without changing the product or duplicating fixtures.

## Measure required reads separately from runtime size

Python module lines affect maintenance and process startup, but they are not
automatically model context. The required governance files are the hot read
set. A controlled ten-task run kept the project file count constant and still
added about 897 bytes to that set per closed task, while the eager-import proxy
was only about 16% of median check latency. Optimize the reproduced context
growth first; do not use runtime line count as a token proxy.

## Compact only after the replacement authority is durable

Deleting completed task bodies is safe only when the tracked replacement facts
already exist and the deletion shares their successful ledger commit. A failed
commit must restore the old readable body rather than leave history dependent
on an ignored report or an uncommitted index. Readers such as inspect, repair,
legacy cutoff, and ID allocation must migrate before writers compact.
