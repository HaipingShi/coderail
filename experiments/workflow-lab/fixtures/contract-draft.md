CONTRACT DRAFT wp1-example

G - Goal
  [G.1][DECISION][owner=user] Let one local owner rename the existing Save action without changing behavior.

T - Task
  [T.1][ASSUMPTION][owner=agent][risk=low][falsifier=repository search finds another user-visible Save action] Change the label in the existing toolbar only.

S - Scope
  [S.1][FACT][evidence=repo:src/ui/toolbar.tsx] The toolbar label is owned by src/ui/toolbar.tsx.
  [S.2][DECISION][owner=user] Do not change save behavior, shortcuts, or persistence.

V - Verify
  [V.1][FACT][evidence=command:npm test -- toolbar-label] The focused label test is executable.
  [V.2][DECISION][owner=user] The toolbar displays "Store" and saving still works.

X - Stop
  [X.1][UNKNOWN][blocking=false][deferred=true] Other screens may use Save terminology; defer them unless repository evidence shows shared ownership.

P - Persist
  [P.1][FACT][evidence=repo:docs/TASKS.md+docs/TRACELOG.jsonl] TASKS and TRACE are the existing canonical task records.

READINESS
  ready: yes
  blocking: none
  deferred: X.1
  slice-reversible: yes
  next-question-reason: none; another answer would not change this slice
