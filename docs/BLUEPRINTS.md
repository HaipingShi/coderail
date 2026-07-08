# CodeRail Blueprints

> Blueprint index for this repository itself.

| ID | Diagram | Status | Path / URL | Owner | Updated | Notes |
|---|---|---|---|---|---|---|
| UJM | User Journey Map | not-applicable | | | | CodeRail is a developer governance kit, not an end-user app. |
| UF | User Flow | not-applicable | | | | No product UI flow in this repository. |
| PF | Page Flow / Wireframe Flow | not-applicable | | | | No page navigation surface. |
| SA | System Architecture | current | README.md | CodeRail | 2026-07-08 | Repo-local governance kit: templates, skills, scripts, references, plugin manifests. |
| CD | Component Diagram | current | README.md | CodeRail | 2026-07-08 | Main components are `skills/`, `scripts/`, `project-template/`, and `references/`. |
| SEQ | Sequence Diagram | planned | docs/BLUEPRINTS.md | CodeRail | 2026-07-08 | Planned for init/check/done gate flows. |
| SM | State Machine Diagram | current | docs/BLUEPRINTS.md | CodeRail | 2026-07-08 | Blueprint lifecycle uses planned/current/stale/missing/not-applicable. |
| ERD | ER Diagram / Database Model | not-applicable | | | | No database layer. |
| DFD | Data Flow Diagram | not-applicable | | | | No persistent data pipeline. |
| DD | Deployment Diagram | not-applicable | | | | No hosted runtime. |
| CICD | CI/CD Pipeline Flow | current | .github/workflows/ci.yml | CodeRail | 2026-07-08 | GitHub Actions runs `npm run ci`: tests, doctor, Blueprint Gate, contract check, and whitespace diff check. |
