# Blueprint Standard

Blueprint Gate is CodeRail's architecture blueprint layer. It catches the risk behind "vibe coding": small projects can be built by hand, but complex systems need inspectable drawings so structure, lifecycle, maintenance, and handoff do not collapse late in the work.

The gate is not a design theater requirement. It asks for the minimum useful drawings when the repository shows real complexity.

## Lifecycle Status

Every blueprint row uses one lifecycle value:

| Status | Meaning |
|---|---|
| `planned` | Needed, accepted, and scheduled, but not created yet. |
| `current` | Accurate enough to guide implementation, debugging, maintenance, and handoff. |
| `stale` | Exists, but code or infrastructure has drifted away from it. |
| `missing` | Required and absent. |
| `not-applicable` | Deliberately not needed for this project. |

## Blueprint Index

Projects track drawings in `docs/BLUEPRINTS.md`.

Required columns:

```text
ID | Diagram | Status | Path / URL | Owner | Updated | Notes
```

## 4 Classes, 11 Core Drawings

### 1. User & Interaction Layer

Audience: product managers, designers, frontend engineers, agents touching user-facing flows.

Pain addressed: prevents frontend work from becoming a pile of screens with no business journey, branch logic, or navigation map.

| ID | Diagram | When required or recommended |
|---|---|---|
| `UJM` | User Journey Map | Recommended when the repository has user-facing frontend flows. |
| `UF` | User Flow | Recommended when interaction branches, auth paths, or error paths matter. |
| `PF` | Page Flow / Wireframe Flow | Recommended when there are multiple pages, routes, or clickable prototypes. |

### 2. System & Application Architecture Layer

Audience: full-stack engineers, architects, agents changing service boundaries or cross-module behavior.

Pain addressed: prevents late-stage structural ambiguity: unknown module ownership, hidden service boundaries, and untraceable request paths.

| ID | Diagram | When required or recommended |
|---|---|---|
| `SA` | System Architecture | Required when two or more core layers appear: frontend, backend, data, operations. Blocking when high-complexity projects have no architecture index. |
| `CD` | Component Diagram | Required when backend modules or service boundaries are detected. |
| `SEQ` | Sequence Diagram | Required when frontend and backend/API layers are both detected. |
| `SM` | State Machine Diagram | Recommended when status/state/workflow language is detected. |

### 3. Data & Model Layer

Audience: backend engineers, database maintainers, DBA reviewers, agents changing schema or reporting paths.

Pain addressed: prevents data persistence and reporting logic from becoming invisible plumbing.

| ID | Diagram | When required or recommended |
|---|---|---|
| `ERD` | ER Diagram / Database Model | Required when schema, migrations, ORM models, or database files are detected. |
| `DFD` | Data Flow Diagram | Recommended when imports, exports, reporting, analytics, queues, webhooks, or sync paths appear. |

### 4. Deployment & Operations Layer

Audience: DevOps engineers, full-stack maintainers, release managers, agents changing deployment or CI.

Pain addressed: prevents software from being understood only as code while runtime topology, network boundaries, and release automation remain implicit.

| ID | Diagram | When required |
|---|---|
| `DD` | Deployment Diagram | Required when Docker, Kubernetes, cloud config, render/vercel config, or infrastructure files are detected. |
| `CICD` | CI/CD Pipeline Flow | Required when CI workflow files are detected. |

## Detection Policy

`scripts/blueprint_check.py` detects project signals and classifies blueprint coverage:

- `healthy`: required diagrams are current or intentionally not needed.
- `usable with warnings`: diagrams are missing, planned, or stale for moderate complexity.
- `unhealthy`: high-complexity projects lack `docs/BLUEPRINTS.md`, have invalid lifecycle values, or mark required diagrams as missing.

## Tooling Guidance

Recommended tools:

| Diagram type | Good tools | Code-friendly option |
|---|---|---|
| User journey, user flow, page flow | Figma, Axure, MockingBot, draw.io | Mermaid flowchart |
| Architecture, component, sequence, state machine | draw.io, ProcessOn, PlantUML | PlantUML or Mermaid |
| ERD, DFD | draw.io, PlantUML, database tools | Mermaid ER or PlantUML |
| Deployment, CI/CD | Cloud-provider icons, Lucidchart, draw.io | Mermaid flowchart |

Prefer diagrams that can live in Git or be linked from Git. PlantUML and Mermaid are good defaults because they are reviewable, diffable, and agent-readable.
