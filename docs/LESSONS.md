# Lessons

Record reusable failure lessons only.

## Preserve intent, not only the current expansion

Expanding a task glob only at `start` converts a durable ownership rule into a stale file list. Keep the pattern and use the same matcher at closeout. Also validate the final dirty set before changing a task to `[x]`; post-close detection is too late to preserve a truthful lifecycle.
