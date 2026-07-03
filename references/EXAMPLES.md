# Examples

## Bad task prompt

"Add login."

Problems: no North-Star Link, no boundaries, no acceptance, no harness, no stop triggers.

## Good task contract

```markdown
## T-014 Add session timeout handling

Status: [ ]
Type: feature

### North-Star Link
Outcome served:
- Reduce unsafe long-lived authenticated sessions.
Invariant preserved:
- Do not change password storage or auth provider.
What this task must not become:
- Do not redesign auth.
- Do not add RBAC.

### Task Contract
Allowed Files:
- src/auth/session.ts
- tests/auth/session-timeout.test.ts
Forbidden Files:
- migrations/**
- src/auth/password.ts
Acceptance:
- [ ] Session expires after configured idle timeout.
- [ ] Active session refresh behavior remains unchanged.
Harness:
- [ ] pnpm test tests/auth/session-timeout.test.ts
```

## Bad handoff

A long narrative of everything tried, full terminal logs, repeated project background, and no next action.

## Good handoff

```markdown
Handoff Level: H2
Current task: T-014
North-Star status: aligned
Done: timeout logic and focused tests
Blocked: none
Tests: pnpm test tests/auth/session-timeout.test.ts passed
Next: run global typecheck and commit
Resume prompt: Continue T-014. Read NORTH_STAR, TASKS, HARNESS_SPEC. Do not edit migrations or password auth.
```
