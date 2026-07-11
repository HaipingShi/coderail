---
name: blueprint
description: Check and maintain Architecture Blueprint Layer coverage: 4 classes, 11 core diagrams, lifecycle status, and docs/BLUEPRINTS.md.
---

# Blueprint Gate

Use this skill when architecture, lifecycle, data, deployment, UI flow, or cross-layer complexity appears.

## Action

Run:

```bash
python .coderail/coderail.py blueprint
```

Then update `docs/BLUEPRINTS.md` or the linked diagrams when the gate reports missing, stale, planned, or invalid coverage.

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
