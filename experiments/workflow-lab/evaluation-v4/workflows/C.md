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

Apply these readiness rules:

- **GC-R1 Risk-control closure.** A control required to make the requested
  authority, safety, privacy, retention, or financial boundary true belongs in
  the reversible slice, including required approval and audit evidence. Do not
  mark ready while such a control is absent, described as future work, or
  placed outside scope. Verification must cover the control, not only the
  happy-path capability.
- **GC-R2 Decision-dependency closure.** Before marking ready, inspect every
  non-fallback scripted-answer trigger and every material conflict in the
  repository evidence. Treat each as an unresolved decision dependency until a
  materially matching question consumes its answer or repository evidence
  resolves it. Never infer that a dependency such as migration is unnecessary
  merely because the requested surface is new.
- **GC-R3 Novice outcome ownership.** For a novice, do not ask for a provider,
  library, storage engine, protocol, or architecture label. Investigate
  feasibility from repository evidence and choose an authorized reversible
  mechanism internally. Ask the user only for the observable outcome or
  boundary they can own. If feasibility is not evidenced, record an
  investigation or stop condition instead of offering unexplained mechanisms.
- **GC-R4 Quick-path preservation.** A clear, local, reversible task whose
  repository evidence supplies scope and verification remains quick. A
  fallback-only scripted answer is not a dependency and must not trigger a
  question.

Immediately before `ready: yes`, perform an internal closure check: every
blocking decision dependency is resolved, every necessary risk control is in
scope and verified, and every remaining UNKNOWN is explicitly non-blocking.
Do not expose this check as another interview turn.

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
