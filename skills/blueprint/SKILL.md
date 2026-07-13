---
name: blueprint
description: Keep simple architecture/data/flow diagrams up to date when the project gets structurally complex.
---

# Blueprint Gate

Use this skill when architecture, lifecycle, data, deployment, UI flow, or cross-layer complexity appears — or when `check`/`done` prints a `== Blueprints ==` notice.

## Action

Check coverage (the tool detects which diagrams THIS codebase needs from real code signals):

```bash
python .coderail/coderail.py blueprint
```

Fill the gaps automatically — creates Mermaid stubs under `docs/blueprints/` and marks index rows `planned`:

```bash
python .coderail/coderail.py blueprint --scaffold        # required + stale gaps
python .coderail/coderail.py blueprint --scaffold --all  # also recommended
```

Then replace each stub's placeholder shapes with the project's real structure and set its row in `docs/BLUEPRINTS.md` to `current`.

## Diagram Classes

1. User & Interaction Layer
2. System & Application Architecture Layer
3. Data & Model Layer
4. Deployment & Operations Layer

## Core Diagrams

- `UJM` User Journey Map
- `UF` User Flow
- `PF` Page Flow / Wireframe Flow
- `SA` System Architecture
- `CD` Component Diagram
- `SEQ` Sequence Diagram
- `SM` State Machine Diagram
- `ERD` ER Diagram / Database Model
- `DFD` Data Flow Diagram
- `DD` Deployment Diagram
- `CICD` CI/CD Pipeline Flow

## Lifecycle

Use one status per diagram:

- `planned`
- `current`
- `stale`
- `missing`
- `not-applicable`

## Rules

- Do not create diagrams as ceremony. Create the smallest useful diagram that reduces structural uncertainty.
- Mark `not-applicable` deliberately; do not use it to hide unknown architecture.
- Mark diagrams `stale` when code, schema, deployment, or user flow changes invalidate them.
- Prefer PlantUML, Mermaid, draw.io, or linked design tools that can be reviewed and versioned.
- When `doctor.py` reports Blueprint Gate severe items, resolve them before treating high-complexity work as done.
