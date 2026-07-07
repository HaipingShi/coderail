---
name: asset-boundary
description: Classify raw material, working notes, candidates, permanent assets, generated artifacts, and releases, and trace promotions. Use when user-provided material, exports, generated files, or document updates are involved. Treats the CodeRail Coordinate P field as the asset-sink checklist.
---

# Asset Boundary

Prevent raw material, drafts, candidates, permanent assets, generated artifacts,
and releases from being confused. The CodeRail Coordinate **P** field is the
checklist of assets that should be updated after the action.

## Asset types

- A0 Raw Material: pasted text, screenshots, logs, outside articles, unverified AI output.
- A1 Working Notes: temporary analysis, scratchpad, debug notes, draft plans.
- A2 Candidate Artifact: proposed architecture, API draft, option, plan candidate.
- A3 Permanent Project Asset: source code, tests, `NORTH_STAR.md`, `TASKS.md`, `HARNESS_SPEC.md`, `DECISIONS.md`, `LESSONS.md`, `TRACELOG.jsonl`.
- A4 Generated Artifact: build output, coverage, generated client, exported PDF/DOCX, `TRACE_INDEX.md` (regenerated).
- A5 Release Artifact: versioned package, release zip, image, published docs.

## Promotion rule

A0 and A1 are not facts. To promote them:

1. State source and scope.
2. State what is accepted and what is rejected.
3. Write accepted content into the target A3 asset.
4. Record source and promotion in `docs/ASSETS.md` or `docs/DECISIONS.md`.
5. Preserve canonical source.
6. Write a trace `change` event recording the promotion (source + target).

## Trace on promotion

- When A0/A1/A2 is promoted to A3/A4/A5, write a trace event with `modifies`
  set to the target asset and `source_ref` set to the canonical source. The
  coordinate's P field must name the target asset.
- A rejected candidate must have a `rejected` or `superseded` trace event so
  the rejection is auditable later.

## P-field sync

After the action, check the coordinate's P field:

- If P declared `DECISIONS` / `LESSONS` / `ASSETS` but those files were not
  updated, flag it. The promotion is incomplete.
- If P declared `TRACE`, the promotion trace event must exist.

## Output

```markdown
## Asset Boundary Report

Inputs classified:
- A0:
- A1:
- A2:
- A3:
- A4:
- A5:

Canonical source:
- 

Promotion needed:
- source:
- target (named in P):
- accepted scope:
- rejected scope:
- trace event: TR-...

P-field sync:
- TASKS: yes | no
- DECISIONS: yes | no | n/a
- LESSONS: yes | no | n/a
- ASSETS: yes | no | n/a
- TRACE: yes | no

Do not treat as permanent:
- 
```
