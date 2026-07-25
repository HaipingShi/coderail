# Workflow C - Guided Convergence

Use Guided Convergence. Investigate supplied repository evidence before asking,
label domain lenses as candidates, and select a quick or guided path. Quick work
reaches a typed contract without an interview. Guided work asks exactly one
highest-impact outcome-level question per turn with recommendation, reason,
impact, evidence, uncertainty, and reversibility.

Type material items as FACT, ASSUMPTION, DECISION, or UNKNOWN. Treat "I do not
know" as valid, use only authorized reversible defaults, emit change-only Draft
Deltas after answers, and stop at reversible-slice readiness. Delay glossary or
ADR promotion until its evidence rules pass.

Return one response per turn in this common contract:

```text
EVALUATION RESPONSE
route: quick | guided
questions:
  - <zero or exactly one question in this turn>
contract:
  G: <typed goal items>
  T: <typed task items>
  S: <typed scope items>
  V: <typed verification items>
  X: <typed stop items>
  P: <typed persistence items>
  ready: yes | no
promotions:
  glossary: <none or evidence-qualified proposals>
  ADR: <none or evidence-qualified proposals>
stop_after_contract: true
```

Do not implement. `stop_after_contract` means stop once an executable,
reversible contract is ready and explicitly confirmed.
