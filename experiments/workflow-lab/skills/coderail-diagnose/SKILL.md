---
name: coderail-diagnose
description: Build a tight, red-capable feedback loop before diagnosing or fixing a bug. Use for regressions, exceptions, failing behavior, intermittent failures, and performance defects in a repository governed by CodeRail.
---

# CodeRail Diagnose

Make the exact reported symptom reproducible before forming a root-cause theory.

## CodeRail boundary

- Read `AGENTS.md`, `docs/NORTH_STAR.md`, `docs/TASKS.md`, and `git status`.
- Work through the active CodeRail task. If none exists, identify the likely
  scope and test command, then use the public `coderail start` command before
  writing a reproduction.
- Do not write `.coderail/tasks.json` or edit task state behind the CLI.
- Never stage or commit task changes.
- Finish through `python .coderail/coderail.py done`.

## Workflow

1. Restate the user's exact symptom as a pass/fail assertion.
2. Choose the highest public seam that can observe it.
3. Identify one fast command that will exercise that seam.
4. Ensure a CodeRail bug task owns the reproduction and likely fix paths:

```bash
python .coderail/coderail.py start "Reproduce and fix <symptom>" \
  --type bug \
  --files "<production scope>" \
  --files "<test or harness path>" \
  --tests "<test or harness path>" \
  --verify "<single reproduction command>" \
  --accept "the exact reported symptom is covered by a regression check"
```

5. Build and run the reproduction. Prefer, in order:
   - a focused automated test;
   - a CLI or HTTP fixture;
   - a headless browser assertion;
   - a captured-input replay;
   - a small throwaway harness;
   - a seeded property, stress, bisection, or differential loop.
6. Tighten it until it is red-capable, deterministic, fast, and agent-runnable.
7. Only then inspect the failing path, state one falsifiable hypothesis, and
   run the smallest experiment that distinguishes it.
8. Apply the smallest root-cause fix inside task scope.
9. Run the focused command green, then the registered regression and CI checks.
10. Inspect `git status` and `git diff --check`. Keep caches, bytecode, coverage,
    and other generated test artifacts out of task ownership; use the
    repository's no-artifact test mode when available.
11. Close through CodeRail, supplying a verdict for every acceptance item:

```bash
python .coderail/coderail.py done --accept-status "1=done"
```

If CodeRail itself generates a new governance-file failure during closeout,
stop with that exact failure. Do not hand-edit protected state to force success.

## Red-capable completion

Do not proceed to a production fix until one command has already been run and:

- reaches the real failing path;
- asserts the user's exact symptom rather than merely avoiding a crash;
- fails before the fix and can pass after it;
- produces the same verdict repeatedly, or a pinned high reproduction rate;
- runs unattended in seconds where practical.

If no such loop can be built, stop with the attempts made and request the
specific missing environment, trace, log, recording, or instrumentation
authority. Do not replace missing evidence with a plausible theory.

## Reporting

Report the reproduction command and observed red result before the hypothesis.
At completion, report the causal explanation, the green result, regression
coverage, and the result of `coderail done`.
