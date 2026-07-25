---
name: coderail-tdd-quality
description: Implement correctness-sensitive behavior with trustworthy red-green slices under CodeRail. Use for features, bug fixes, parsers, validators, domain logic, public APIs, shared utilities, and risky behavior-preserving refactors.
---

# CodeRail TDD Quality

Use CodeRail's existing TDD evidence contract while improving where and how
tests are written.

## CodeRail boundary

- Read the active task and its G/T/S/V/X/P contract before editing.
- Do not write `.coderail/tasks.json` or edit task state behind the CLI.
- Never stage or commit task changes.
- Finish through `python .coderail/coderail.py done`.
- Preserve CodeRail's Red, Green, Refactor, Regression, and CI evidence. This
  skill does not redefine or remove those fields.

## Select the seam

Test behavior at the highest stable public interface that observes the task's
acceptance criterion. Prefer an existing seam over creating a new one.

Ask the user to confirm a new seam only when it is decision-grade: public,
cross-module, expensive to reverse, or ambiguous between materially different
designs. For an existing low-risk seam, record the choice and continue.

## Run vertical red-green slices

For each behavior:

1. Write one focused test through the selected seam.
2. Run it and capture the expected failure.
3. Add only enough production behavior to make that test pass.
4. Run it green.
5. Let the result inform the next slice.

Do not write every imagined test before implementation. Each slice must leave
the behavior runnable or verifiable through its public interface.

## Reject weak tests

- **Implementation-coupled:** private methods, internal call counts, internal
  collaborator mocks, or assertions that fail after a behavior-preserving
  refactor.
- **Tautological:** expected values are recomputed with the same algorithm as
  production, so implementation and assertion can be wrong together.
- **Side-channel verification:** bypasses the public interface to inspect an
  internal database, cache, or field when the behavior is observable normally.
- **Shape-only:** verifies that code has a class, function, or call structure
  without proving the user-visible capability.

Expected values must come from an independent source: a known literal, worked
example, protocol rule, accepted task criterion, or trusted fixture.

## Complete the CodeRail evidence

After the red-green slices:

1. Clean up without changing behavior and rerun the focused checks.
2. Preserve the exact regression case for a bug or failure mode.
3. Run the task's full registered checks and CI.
4. Inspect `git status` and `git diff --check`; keep generated test artifacts
   out of task ownership.
5. Run `python .coderail/coderail.py tdd` when available.
6. Run `python .coderail/coderail.py done`, including the required
   `--accept-status` verdicts for registered acceptance items.

Never call a test written after the implementation "Red evidence" unless it
was observed failing against the pre-fix behavior.
