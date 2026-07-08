# Blueprints

> Architecture Blueprint Layer. Keep this index small and link to diagrams kept in Git, design tools, or generated artifacts.

Lifecycle status values:

- `planned`: needed but not created yet
- `current`: accurate enough to guide implementation and maintenance
- `stale`: exists but no longer reflects the system
- `missing`: required and absent
- `not-applicable`: intentionally not needed for this project

## Blueprint Index

| ID | Diagram | Status | Path / URL | Owner | Updated | Notes |
|---|---|---|---|---|---|---|
| UJM | User Journey Map | not-applicable | | | | User goal path across pages or channels. |
| UF | User Flow | not-applicable | | | | Branching interaction logic and exceptions. |
| PF | Page Flow / Wireframe Flow | not-applicable | | | | Page-to-page navigation and wireframe links. |
| SA | System Architecture | not-applicable | | | | Frontend, gateway, services, cache, storage, ops. |
| CD | Component Diagram | not-applicable | | | | Internal modules, dependencies, and service boundaries. |
| SEQ | Sequence Diagram | not-applicable | | | | Request/response chains across components. |
| SM | State Machine Diagram | not-applicable | | | | Status transitions, triggers, rollbacks. |
| ERD | ER Diagram / Database Model | not-applicable | | | | Tables/entities, fields, keys, relations. |
| DFD | Data Flow Diagram | not-applicable | | | | Inputs, transforms, stores, outputs. |
| DD | Deployment Diagram | not-applicable | | | | Runtime nodes, network, cloud resources, firewalls. |
| CICD | CI/CD Pipeline Flow | not-applicable | | | | Commit-to-release automation path. |

## Notes

- Mark a diagram `current` only when it can guide a new engineer or agent without guesswork.
- Mark a diagram `stale` as soon as code and diagram disagree.
- Use `not-applicable` deliberately; do not use it to hide unknown architecture.
