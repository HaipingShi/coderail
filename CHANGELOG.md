# Changelog

## v0.6.0

Productization spine.

- Added Coordinate Contract Drafts: `skills/contract-draft`, `docs/CONTRACTS.md`, `references/CONTRACT_DRAFT.md`, and `scripts/contract_check.py`.
- Added Runtime State Inspect: `skills/inspect`, `docs/CODERAIL_STATUS.md`, `references/RUNTIME_STATE_INSPECT.md`, and `scripts/inspect_state.py`.
- Added Verification-before-complete: `skills/done-gate`, `references/DONE_GATE.md`, and `scripts/done_gate.py`.
- Updated `/done`, `/handoff`, `/doctor`, `AGENTS.md`, and `CLAUDE.md` to use contract draft, inspect, and done gate.
- Updated `init_project.py` to copy `CONTRACTS.md` and `CODERAIL_STATUS.md`.
- Updated tests to cover v0.6 scripts and entry files.

## v0.5.0

- Optimized current GitHub package.
- Fixed trace edge CLI handling and `--from-file` behavior.
- Tightened coordinate, trace, and doctor checks.
- Kept entry files short and schemas in references.
