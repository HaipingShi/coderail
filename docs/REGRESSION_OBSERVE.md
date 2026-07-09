# Regression Observation

CodeRail keeps the reusable regression harness in source control and keeps run
artifacts out of source control.

## What Is Committed

- `scripts/regression_observe.py`
- `npm run regression-observe`
- this developer note
- tests that protect the artifact boundary

## What Is Not Committed

- run workspaces
- command logs
- comparison reports
- generated summaries
- caches and snapshots

By default, every run writes to:

```text
.coderail-runs/regression-observe/<timestamp>/
```

That directory is ignored by git.

## Usage

Run the full observation:

```bash
npm run regression-observe
```

Run a faster observation without nested `npm test`:

```bash
python scripts/regression_observe.py --target . --skip-npm-test
```

Compare against a different baseline ref:

```bash
python scripts/regression_observe.py --target . --baseline-ref origin/main
```

## Reading Results

The script prints a compact comparison and writes detailed artifacts under the
ignored run directory:

- `summary.json`
- `report.md`
- `logs/baseline/*.log`
- `logs/current/*.log`

Only use the printed summary or manually copied excerpts in reviews. Do not
stage the run directory.
