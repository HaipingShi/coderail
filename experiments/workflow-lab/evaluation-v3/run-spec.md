# WP5 v3 Execution Specification

Status: frozen before subject output

## Subject

- Model: `gpt-5.4`
- Reasoning effort: `medium`
- Codex mode: non-interactive, ephemeral, read-only, approval `never`
- User config and repository rules: ignored
- Web search: disabled
- Output: `model-output.schema.json`

Run one batch per workflow and task category, for 12 subject batches total.
Within each batch, order tasks with the deterministic seed
`coderail-wp5-v3`. The subject receives its workflow prompt and task packets
without each task's oracle.

Each task packet includes scripted answers for offline contract-convergence
simulation. Instruct the subject to treat an answer as unavailable until it
asks a materially matching question and to record the consumed answer index.
This is a contract-phase simulation, not a live-human or implementation trial.

## Judge

Use the same model and execution restrictions. Mask workflow and replace each
response with an opaque id before judging. Run one judge batch per task category
over shuffled A/B/C responses. Use `judge.md` and
`judge-output.schema.json`.

The runner derives token counts from Codex usage events and quick-path
correctness from observed route versus the hidden oracle. The blind judge
supplies only the five contract-phase observations in its schema.

## Unobserved fields

Set these to null:

- post-start contract corrections;
- out-of-scope edits;
- first-pass CodeRail done;
- reopened or post-close defects;
- glossary or ADR reversals.

Null means not observed. It is never converted to zero and cannot satisfy an
adoption threshold.

## Failure handling

Record failed batches and cells. Do not retry with a different model, reasoning
effort, workflow prompt, task packet, or scoring rule. One transport retry with
identical inputs is allowed and must be logged.
