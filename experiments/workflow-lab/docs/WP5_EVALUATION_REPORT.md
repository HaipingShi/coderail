# WP5 Comparative Evaluation Report

Status: preflight blocked; no subject trial observed
Protocol: `wp5-v1`
Date: 2026-07-25

## Preflight result

The frozen subject model was `gpt-5.6-terra` at medium reasoning. The installed
Codex CLI reached the service but received HTTP 400: that model requires a
newer Codex version. No A, B, or C subject trial was started and no task output
was observed.

A separate availability probe confirmed that `gpt-5.4` at medium reasoning can
run on the installed CLI. It was not used as an undeclared replacement.

## Protocol defect found

The contract-phase result schema requires an integer for
`promotion_reversals`, although reversal can be known only from later
follow-through evidence. Recording zero would confuse "not observed" with "no
reversal." The same experiment rules already require unobserved implementation
fields to remain null.

## Decision

Do not score `wp5-v1`. Create `wp5-v2` before subject execution:

1. pin the available `gpt-5.4` model at medium reasoning;
2. allow null for every metric that contract-only trials cannot observe;
3. retain the same 18 tasks, A/B/C treatments, oracles, and adoption
   thresholds;
4. freeze new hashes before the first subject output.

This is a pretrial protocol correction, not an unfavorable result and not
evidence for ADOPT, REVISE, or REJECT.
