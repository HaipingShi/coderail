# Asset Registry

## Asset types

- A0 Raw Material: user paste, screenshot, log, external note, unverified AI analysis.
- A1 Working Notes: scratch analysis, debug notes, temporary plans.
- A2 Candidate Artifact: proposed plan, API draft, architecture option.
- A3 Permanent Project Asset: source code, tests, NORTH_STAR, TASKS, HARNESS_SPEC, DECISIONS, LESSONS.
- A4 Generated Artifact: build output, coverage, exported PDF/DOCX, generated clients.
- A5 Release Artifact: versioned package, release zip, container image, published docs.

## Canonical Sources

| Asset | Type | Canonical | Update Rule |
|---|---|---:|---|
| docs/NORTH_STAR.md | A3 | yes | Update when outcome, invariants, current bet, or current slice changes. |
| docs/TASKS.md | A3 | yes | Update when task status changes. |
| docs/HARNESS_SPEC.md | A3 | yes | Update when verification commands change. |
| docs/HANDOFF.md | A3 volatile | yes | Rolling current-state snapshot only. |

## Raw Materials

| Asset | Source | Status | Promotion Target |
|---|---|---|---|
|  |  | pending |  |

## Working Notes

| Asset | Status | Can Delete | Promotion Target |
|---|---|---:|---|
|  | draft | yes |  |

## Generated Artifacts

| Asset | Canonical Source | Generation Command | Commit |
|---|---|---|---|
|  |  |  |  |

## Release Artifacts

| Asset | Version | Source Commit | Release Notes |
|---|---|---|---|
|  |  |  |  |
