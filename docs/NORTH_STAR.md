# North Star

ID: NS-001
Status: current
Last reviewed: 2026-08-08
Owner: CodeRail maintainers

## Outcome

- Make CodeRail a reliable repo-local governance rail that agents can execute, verify, close out, and resume without dangling state.

## Current Bet

- A single local launcher and finish boundary will improve rule recall, persistence, safe commits, and next-task continuity more than adding more prompt text.

## Invariants

- Governance decisions remain inspectable in repository files.
- Task scope, verification evidence, and persistence links are explicit.
- Failed or blocked work never masquerades as done.

## Current Slice

- Milestone: M-015 owner communication and agent blackboard
- Product capability: localized Owner Receipt, Agent Blackboard, Technical Report,
  and durable Delivery Contract product facts are verified repository-local capabilities.
- Product gap: a separately authorized Chinese downstream A/B acceptance is
  still required before retiring the temporary legacy closeout output.
- Lifecycle note: this section declares no active/finalized/commit/push state;
  use CodeRail live state and Git refs for those facts.

## Non-Goals

- CodeRail is not a hosted CI service, issue tracker, scheduler, or model runtime.
- No automatic Coordinate creation, task activation, push, tag, release,
  historical-ledger rewrite, or broad prose rewrite.

## Known Unknowns

- Which agent hosts will enforce a hard stop hook without a soft override.

## Decision Debt

- None. Unreproduced observations are not decision debt and do not enter the
  implementation queue.

## Legacy Cutoff

- Enforcement starts at: T-001

## Drive Contract

- Mode: manual
- Next-task mode: recommend
- Terminal condition: owner receipts are localized and bounded, product delivery
  facts survive compaction, and Agent Blackboard retains exact governance refs.
- Progress signal: the T-061 Red matrix passes without modifying scope,
  closeout-transaction, Git, TRACE, or publication authority.
- Retry budget: 3
- No-progress limit: 2
- Human gates: changes to public APIs, security, privacy, payment, persistence, or release policy

Continuous Drive is opt-in. `recommend` is the safe default; use `activate` only
when automatic activation of the next dependency-ready task is explicitly authorized.

## Coordinate Rule

Every active task must map to this North Star through its G field.

## Stop Triggers

- A task cannot map to the North Star.
- A code change has no task or trace link.
- Verification fails or a required decision is missing.
- A done task lacks a verify trace or closeout commit.
- A proposed implementation lacks a current deterministic reproduction.
- A bug fix requires new product behavior rather than restoring an accepted invariant.
