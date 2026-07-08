# Loop Engineering

Loop Engineering is CodeRail's rule for keeping long-running work moving.

Task decomposition should be fine-grained for traceability, rollback, and
verification. Execution should be batched so the agent does not stop after every
small internal step.

## Loop shape

```text
Align -> Contract -> Execute Batch -> Verify -> Persist -> Closeout -> Continue or Handoff
```

## Batch rule

Inside an authorized batch, continue until one of these occurs:

1. the task is done and Done Gate passes;
2. the batch reaches a planned stage-complete checkpoint;
3. X fires;
4. V becomes impossible;
5. S must expand;
6. harness fails twice without a clear root cause;
7. a product, security, privacy, API, schema, persistence, or architecture
   decision is required;
8. an automatic task-scoped commit/snapshot cannot be created before more tasks
   would be mixed.

## Anti-fragmentation rule

Do not stop for low-risk internal steps merely because a subtask is complete.
If stopping is useful, close out with:

- task result;
- auto-commit action;
- handoff trigger check;
- resume anchor;
- next executable step.

## Stage-complete checkpoints

Use `stage-complete` when useful work exists but acceptance is not complete.
The task remains active unless a maintainer explicitly splits or closes it.
