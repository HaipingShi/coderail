# Workflow B - Expert Grilling

Use expert-oriented grilling. Walk the design decision tree one branch at a
time, ask one technically precise question per turn, include a recommended
answer, and continue until important product and engineering branches are
resolved. When a stable term or consequential decision appears, use immediate
documentation by proposing a glossary entry or ADR in the same session.

Do not weaken expert vocabulary for novice inputs; clarification may define the
term. This treatment intentionally tests the interruption and anchoring cost of
expert-oriented grilling with immediate documentation.

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

Do not implement. `stop_after_contract` means stop after the grilled contract
and its immediate documentation proposals are explicitly confirmed.
