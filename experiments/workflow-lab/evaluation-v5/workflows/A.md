# Workflow A - Baseline CodeRail

Use baseline CodeRail contract drafting. Read the supplied repository evidence,
translate the request directly into G/T/S/V/X/P, and ask only when a missing
user decision prevents a truthful bounded task. Prefer the smallest verifiable
slice. Do not use Guided Convergence state typing or domain-lens analysis unless
the task packet itself requires it.

Return one response per turn in this common contract:

```text
EVALUATION RESPONSE
route: quick | guided
questions:
  - <zero or one question in this turn>
contract:
  G: <goal>
  T: <task>
  S: <scope>
  V: <verification>
  X: <stop conditions>
  P: <persistence>
  ready: yes | no
promotions:
  glossary: <none or proposals>
  ADR: <none or proposals>
stop_after_contract: true
```

Do not implement. `stop_after_contract` means stop once an executable contract
is ready and explicitly confirmed.
