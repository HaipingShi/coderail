# CodeRail Blueprints

> Blueprint index for this repository itself.

| ID | Diagram | Status | Path / URL | Owner | Updated | Notes |
|---|---|---|---|---|---|---|
| UJM | User Journey Map | not-applicable | | | | CodeRail is a developer governance kit, not an end-user app. |
| UF | User Flow | not-applicable | | | | No product UI flow in this repository. |
| PF | Page Flow / Wireframe Flow | not-applicable | | | | No page navigation surface. |
| SA | System Architecture | current | docs/CODERAIL_DIAGRAMS.md | CodeRail | 2026-07-28 | Section 1 plus the README overview show target-repository and CodeRail-home boundaries. |
| CD | Component Diagram | current | docs/CODERAIL_DIAGRAMS.md | CodeRail | 2026-07-28 | Section 1 shows facade, lifecycle services, gates, state model, graph, distribution, Git, and verification boundaries. |
| SEQ | Sequence Diagram | current | docs/CODERAIL_DIAGRAMS.md | CodeRail | 2026-07-28 | Section 3 shows verification, ledger preparation, exact commit, commit-pending recovery, and final rescan. |
| SM | State Machine Diagram | current | docs/CODERAIL_DIAGRAMS.md | CodeRail | 2026-07-28 | Section 2 shows task ownership across start, next, switch, check, done, and resume. |
| ERD | ER Diagram / Database Model | not-applicable | | | | No database layer. |
| DFD | Data Flow Diagram | current | docs/CODERAIL_DIAGRAMS.md | CodeRail | 2026-07-28 | Section 4 shows ownership and writes across TASKS, PROGRESS, TRACE, HANDOFF, metadata, recovery, projections, and Git. |
| DD | Deployment Diagram | not-applicable | | | | No hosted runtime. |
| CICD | CI/CD Pipeline Flow | current | .github/workflows/ci.yml | CodeRail | 2026-07-08 | GitHub Actions runs `npm run ci`: tests, doctor, Blueprint Gate, contract check, TDD Gate, and whitespace diff check. |
