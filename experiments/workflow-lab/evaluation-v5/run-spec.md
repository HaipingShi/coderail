# WP5 v5 Execution Specification

Status: frozen before subject output

## Subject

- Model: `gpt-5.4`
- Reasoning effort: `medium`
- Codex mode: non-interactive, ephemeral, read-only, approval `never`
- User config and repository rules: ignored
- Web search: disabled
- Output: `model-output.schema.json`

Run one batch per workflow, task category, and seed. Within each batch, order
tasks with the deterministic seed for that run (`coderail-wp5-v5-s1` through
`coderail-wp5-v5-s5`). The subject receives its workflow prompt and task packets
without each task's oracle.

`manifest.json.trial_design` is the machine-readable authority for primary
workflows, contingency workflows, category-to-seed allocation, and the expected
180 primary trial records. The primary `C5` treatment reads `workflows/C.md`;
`C5p` reads `workflows/C5p.md` only if its frozen contingency trigger fires.

Each task packet includes scripted answers for offline contract-convergence
simulation. Instruct the subject to treat an answer as unavailable until it
asks a materially matching question and to record the consumed answer index.
This is a contract-phase simulation, not a live-human or implementation trial.

## Sampling plan

v5 repeats sampling to attribute score movement to the C revision rather than
single-run variance. The 18 tasks split into three subsets by category, each
sampled at a different seed depth.

| Subset | Categories | Tasks | Seeds | Trials per workflow |
|---|---|---:|---|---:|
| Threshold | ambiguous-cross-module, high-risk-persistent | 9 | s1-s5 | 45 |
| Domain-language | domain-language-conflict | 3 | s1-s3 | 9 |
| Clear | clear-local-reversible | 6 | s1 | 6 |

Seed identifiers are `coderail-wp5-v5-s1` through `coderail-wp5-v5-s5`, used for
task-order shuffling and required in every trial record. The domain-language
subset is sampled because it drove the v4 token excess (C 37,313 versus A
18,059); without it the token gate has no measurement surface. The clear subset
guards against a C-R2 regression on GC-R4 and is not a variance-estimation arm.

Total subject volume is 5 x 9 + 3 x 3 + 1 x 6 = 60 trials per workflow across
A, B, and C5, or 180 trials. The C5p contingency is frozen in
`workflows/C5p.md` but is not part of this 180; it runs on the threshold subset
only if C5 regresses on an assumption, turn, or interruption metric relative to
v4 C.

## Judge

Use the same model and execution restrictions. Mask workflow and replace each
response with an opaque id before judging. Run one judge batch per task category
per seed over shuffled A/B/C5 responses; the judge receives no workflow labels
and no seed identifiers, and the opaque map is regenerated per seed. Use
`judge.md` and `judge-output.schema.json`.

The runner derives token counts from Codex usage events and quick-path
correctness from observed route versus the hidden oracle. The blind judge
supplies only the five contract-phase observations in its schema.

## Token attribution

Tokens are batch-derived and batch-allocated. Per-task tokens are an equal
allocation of the batch total across the task cells in that batch and are
labeled as such; they are not native per-task usage. Gate 4 is evaluated on
pooled subject tokens per category across that category's seeds, C5 versus A,
not on any single batch or single task. A and B per-trial costs should match v4
within sampling noise.

## Unobserved fields

Set these to null:

- post-start contract corrections;
- out-of-scope edits;
- first-pass CodeRail done;
- reopened or post-close defects;
- glossary or ADR reversals.

Null means not observed. It is never converted to zero and cannot satisfy an
adoption threshold.

## UTF-8 runner contract

The runner declares UTF-8 explicitly (the v4 fix retained). Raw output is
persisted to disk before any decoding step, so a local-encoding decode failure
cannot lose a completed generation. On a recorded local failure, retry with
identical inputs and reuse every already-persisted raw/event pair rather than
regenerating it; each subject batch in the run metadata is marked `reused` or
`executed` accordingly.

## Failure handling

Record failed batches and cells. Do not retry with a different model, reasoning
effort, workflow prompt, task packet, or scoring rule. One transport retry with
identical inputs is allowed and must be logged, reusing completed batches as
described above.

## Treatment isolation

This protocol changes only workflow C (now `C5`, with the `C5p` contingency
frozen alongside) and protocol-version metadata. Workflows A and B, all 18 task
packets and hidden oracles, rubric semantics, model, reasoning effort, blinding,
and failure handling remain identical to `wp5-v4`. The C5 revision is limited to
the C-R1 provider-question elimination and the C-R2 output-economy rule; C5p
applies C-R1 only with v4 verbosity retained.

## Checkpoint scope

This checkpoint freezes pretrial inputs only. No schema preflight, subject
batch, or judge batch is executed here. Schema preflight with zero task or
oracle payloads precedes the first subject batch at the next stage.
