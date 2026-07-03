---
name: asset-boundary
description: Classify raw material, working notes, candidates, permanent assets, generated artifacts, and releases. Use when user-provided material, exports, generated files, or document updates are involved.
---

# Asset Boundary

Prevent raw material, drafts, candidates, permanent assets, generated artifacts, and releases from being confused.

## Asset types

- A0 Raw Material: pasted text, screenshots, logs, outside articles, unverified AI output.
- A1 Working Notes: temporary analysis, scratchpad, debug notes, draft plans.
- A2 Candidate Artifact: proposed architecture, API draft, option, plan candidate.
- A3 Permanent Project Asset: source code, tests, `NORTH_STAR.md`, `TASKS.md`, `HARNESS_SPEC.md`, `DECISIONS.md`, `LESSONS.md`.
- A4 Generated Artifact: build output, coverage, generated client, exported PDF/DOCX.
- A5 Release Artifact: versioned package, release zip, image, published docs.

## Promotion rule

A0 and A1 are not facts. To promote them:

1. State source and scope.
2. State what is accepted and what is rejected.
3. Write accepted content into the target A3 asset.
4. Record source and promotion in `docs/ASSETS.md` or `docs/DECISIONS.md`.
5. Preserve canonical source.

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
- target:
- accepted scope:
- rejected scope:

Do not treat as permanent:
- 
```
