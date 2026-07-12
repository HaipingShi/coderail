# Coordinate Contract Drafts

Use this file for proposed or accepted Coordinate Contract Drafts before they become active tasks in `docs/TASKS.md`.

Copy this block and rename the heading to `## CD-001 Short title` when creating a real draft.

```markdown
\## CD-001 Short title

Status: proposed
Created at:
Source: user | agent | handoff | trace | issue
Trace:

### Coordinate Contract Draft

G — Goal:
- North Star:
- Outcome served:
- Why now:

T — Task:
- Task ID:
- Exact task:
- What this task must not become:

S — Scope:
- Allowed:
  -
- Forbidden:
  - none

V — Verify:
- TDD mode: required | optional | waived
- Red check:
- Green check:
- Refactor check:
- Regression check:
- CI check:
- Waiver reason:
- Harness:
  -
- Manual acceptance:
  -

X — Stop:
- forbidden files needed
- harness fails twice with unclear root cause

P — Persist:
- TASKS:
- HANDOFF:
- DECISIONS:
- LESSONS:
- ASSETS:
- TRACE:

Decision:
- proceed | revise | ask user | split task | backlog

Notes:
-
```

## CD-002 Doctor marker compatibility

Status: accepted
Created at: 2026-07-12
Source: user
Trace: pending T-002 verification trace

### Coordinate Contract Draft

G — Goal:
- North Star: keep CodeRail executable and diagnosable across launcher migrations
- Outcome served: Doctor reports current generated Inspect state without false warnings
- Why now: downstream timeBuilderEngin sync must start from a healthy source release

T — Task:
- Task ID: T-002
- Exact task: accept both the legacy inspect script marker and the repo-local launcher marker in Doctor
- What this task must not become: a broader Doctor refactor or target-project sync implementation

S — Scope:
- Allowed:
  - scripts/doctor.py
  - tests/test_structure.py
  - docs/NORTH_STAR.md
  - docs/TASKS.md
  - docs/CONTRACTS.md
  - docs/TRACELOG.jsonl
  - docs/TRACE_INDEX.md
  - docs/CODERAIL_STATUS.md
  - docs/HANDOFF.md
- Forbidden:
  - package.json
  - lockfiles
  - timeBuilderEngin files

V — Verify:
- TDD mode: required
- Red check: new and legacy marker compatibility test fails before implementation
- Green check: both markers pass and unrelated text remains rejected
- Refactor check: marker parsing stays localized in Doctor
- Regression check: npm test
- CI check: npm run ci
- Harness:
  - python scripts/doctor.py --target project-template
  - python scripts/drift_check.py --target project-template

X — Stop:
- compatibility requires changing Inspect output contract
- validation reveals unrelated source drift

P — Persist:
- TASKS: T-002 completion
- HANDOFF: H0 unless sync becomes blocked
- DECISIONS: none
- LESSONS: none
- ASSETS: none
- TRACE: T-002 verify event

Decision:
- proceed

Notes:
- Downstream sync remains a separate target-repository boundary.
