# Progress - plain language, newest first

If you only read one file in this project, read this one.
Each entry: what got done, how it was checked, what comes next.

## 2026-07-28 - Build evidence-aware trace graph lifecycle and queries (T-046)

- Done: Build evidence-aware trace graph lifecycle and queries
- Checked by: `F:\mathmind\venv\Scripts\python.exe -m pytest -q` exit 0
- Next: decide with the user
- Evidence: `F:\mathmind\venv\Scripts\python.exe -m pytest -q` -> exit 0
- Acceptance [done]: Lifecycle commands automatically record only provable fact edges among north star, task, files, commits, and verification
- Acceptance [done]: Tasks support depends_on, blocks, and supersedes with missing-reference and cycle checks
- Acceptance [done]: why, impact, and graph commands return concise plain-language conclusions
- Acceptance [done]: Uncertain semantic edges remain isolated candidates until evidence or explicit confirmation promotes them
- Acceptance [done]: Trace and introduction documentation describe fact, decision, and candidate boundaries accurately

## 2026-07-27 - Write the CodeRail introduction for vibe coders (T-045)

- Done: Write the CodeRail introduction for vibe coders
- Checked by: `python scripts/trace_doctor.py --target .` exit 0; `npm.cmd test` exit 0
- Next: Use the new vibe-coder introduction as the public explanation; no follow-up implementation is authorized
- Evidence: `python scripts/trace_doctor.py --target .` -> exit 0
- Evidence: `npm.cmd test` -> exit 0
- Acceptance [done]: The document explains CodeRail, the novice communication problem, and the investor/vendor analogy without requiring programming vocabulary
- Acceptance [done]: The document describes actual start/check/switch/done and cross-session persistence behavior accurately
- Acceptance [done]: The rationale maps each design choice to a concrete failure mode and states scientific/evidence limits honestly
- Acceptance [done]: The comparison with Spec Kit, grill-me/grill-with-docs, and Superpowers uses official-source facts and explains composition rather than false competition
- Acceptance [done]: The document provides small, medium, large, bug, and high-risk workflow recipes with one canonical source of task truth
- Acceptance [done]: README links the introduction and repository tests pass

## 2026-07-27 - Finalize release governance metadata before feature merge (T-044)

- Done: Finalize release governance metadata before feature merge
- Checked by: `python scripts/trace_doctor.py --target .` exit 0; `python scripts/trace_index.py --target .` exit 0; `python -m unittest discover -s experiments/workflow-lab/tests -v` exit 0; `npm.cmd test` exit 0
- Next: Push feature/guided-convergence, fast-forward main, and push main
- Evidence: `python scripts/trace_doctor.py --target .` -> exit 0
- Evidence: `python scripts/trace_index.py --target .` -> exit 0
- Evidence: `python -m unittest discover -s experiments/workflow-lab/tests -v` -> exit 0
- Evidence: `npm.cmd test` -> exit 0
- Acceptance [done]: NORTH_STAR defines NS-001, removes the stale T-018 active-task claim, and records the release-governance closeout state
- Acceptance [done]: Every task event in TRACELOG maps to NS-001 and trace doctor reports no warnings
- Acceptance [done]: TRACE_INDEX is regenerated from the repaired structured log
- Acceptance [done]: No product code, experiment inputs, package, or lock file changes
- Acceptance [done]: CodeRail has no active or paused task, closeout pending, verification gap, or historical verification debt after completion
- Acceptance [done]: All workflow-lab and CodeRail tests pass

## 2026-07-27 - Issue WP6 guided-convergence adoption review (T-042)

- Done: Issue WP6 guided-convergence adoption review
- Checked by: `python -m unittest discover -s experiments/workflow-lab/tests -v` exit 0
- Next: No automatic next slice; keep the experiment isolated unless a separately authorized new protocol is requested
- Evidence: `python -m unittest discover -s experiments/workflow-lab/tests -v` -> exit 0
- Acceptance [done]: The review makes exactly one top-level ADOPT, REVISE, or REJECT decision and distinguishes treatment disposition from native integration
- Acceptance [done]: The decision cites v4 and v5 evidence, including the s2 provider-gate stop, unsupported assumptions, clear quick path, token economy, and missing implementation evidence
- Acceptance [done]: No smart hook, kernel change, native skill installation, later v5 seed, or C5p execution is authorized
- Acceptance [done]: A future revision must use a new frozen protocol and novice-facing questions must request outcomes rather than mechanisms
- Acceptance [done]: The plan, report, README, and executable consistency test agree on the final decision
- Acceptance [done]: All workflow-lab tests pass

## 2026-07-27 - Issue WP6 guided-convergence adoption review (T-042)

- Done: Issue WP6 guided-convergence adoption review
- Checked by: `python -m unittest discover -s experiments/workflow-lab/tests -v` exit 0
- Next: No automatic next slice; keep the experiment isolated unless a separately authorized new protocol is requested
- Evidence: `python -m unittest discover -s experiments/workflow-lab/tests -v` -> exit 0
- Acceptance [done]: The review makes exactly one top-level ADOPT, REVISE, or REJECT decision and distinguishes treatment disposition from native integration
- Acceptance [done]: The decision cites v4 and v5 evidence, including the s2 provider-gate stop, unsupported assumptions, clear quick path, token economy, and missing implementation evidence
- Acceptance [done]: No smart hook, kernel change, native skill installation, later v5 seed, or C5p execution is authorized
- Acceptance [done]: A future revision must use a new frozen protocol and novice-facing questions must request outcomes rather than mechanisms
- Acceptance [done]: The plan, report, README, and executable consistency test agree on the final decision
- Acceptance [done]: All workflow-lab tests pass

## 2026-07-27 - Finalize WP6 review under governance-owned closeout scope (T-043)

- Done: Finalize WP6 review under governance-owned closeout scope
- Checked by: `python -m unittest discover -s experiments/workflow-lab/tests -v` exit 0
- Next: No automatic next slice; keep the experiment isolated unless a separately authorized new protocol is requested
- Evidence: `python -m unittest discover -s experiments/workflow-lab/tests -v` -> exit 0
- Acceptance [done]: The review makes exactly one top-level REVISE decision and withholds native integration
- Acceptance [done]: The decision is linked to frozen v4/v5 evidence and the registered s2 stop
- Acceptance [done]: No smart hook, kernel change, native skill installation, later v5 seed, or C5p execution is authorized
- Acceptance [done]: Future work requires a separately authorized new frozen protocol with outcome-level novice questions
- Acceptance [done]: Public documents and executable tests agree
- Acceptance [done]: All workflow-lab tests pass

## 2026-07-27 - Preflight wp5-v5 schema and execution runner (T-038)

- Done: Preflight wp5-v5 schema and execution runner
- Checked by: `python -m unittest discover -s experiments/workflow-lab/tests -v` exit 0
- Next: WP6: issue the evidence-led adoption review and withhold native integration after the v5 provider-gate failure
- Evidence: `python -m unittest discover -s experiments/workflow-lab/tests -v` -> exit 0
- Acceptance [done]: The runner reads primary workflows, contingency workflows, canonical seeds, and sampling plan from manifest.json
- Acceptance [done]: The service accepts model-output.schema.json for protocol wp5-v5
- Acceptance [done]: Preflight sends zero task and oracle payloads and starts zero subject batches
- Acceptance [done]: All v5 frozen hashes remain unchanged
- Acceptance [done]: No v5 results directory or trial output is created

## 2026-07-27 - Run and adjudicate seed-wise wp5-v5 comparison (T-040)

- Done: Run and adjudicate seed-wise wp5-v5 comparison
- Checked by: `python -m unittest discover -s experiments/workflow-lab/tests -v` exit 0
- Next: WP6: issue the evidence-led adoption review; do not run s3-s5 or C5p and do not integrate C5 natively
- Evidence: `python -m unittest discover -s experiments/workflow-lab/tests -v` -> exit 0
- Acceptance [done]: Execution is seed-major and no later seed starts before the prior seed provider gate is judged
- Acceptance [done]: Judge inputs expose neither workflow labels nor seed identifiers and map only through opaque ids
- Acceptance [done]: Every expected completed cell has one seed-bearing trial record, or an explicit frozen-rule early-stop record explains omitted cells
- Acceptance [done]: Aggregates evaluate all five pre-registered gates, category-pooled token ratios, and the baseline-floor rule
- Acceptance [done]: Unobserved implementation and follow-through metrics remain null and cannot authorize ADOPT
- Acceptance [done]: All frozen hashes remain unchanged and retries preserve identical inputs and completed batches

## 2026-07-27 - Finalize wp5-v5 registered early-stop checkpoint (T-041)

- Done: Finalize wp5-v5 registered early-stop checkpoint
- Checked by: `python -m unittest discover -s experiments/workflow-lab/tests -v` exit 0
- Next: WP6: issue the evidence-led adoption review; do not run s3-s5 or C5p and do not integrate C5 natively
- Evidence: `python -m unittest discover -s experiments/workflow-lab/tests -v` -> exit 0
- Acceptance [done]: Protocol tests distinguish the historical zero-trial freeze checkpoint from the current registered early-stop results
- Acceptance [done]: Exactly 90 trials, 21 subject batches, and 7 judge batches cover only the s1/s2 prefix
- Acceptance [done]: No s3-s5 or C5p execution exists after the provider gate observed two user-visible technical choices
- Acceptance [done]: Aggregate disposition is REVISE_PROVIDER_GATE and implementation metrics remain null with no ADOPT decision
- Acceptance [done]: Frozen artifact hashes remain unchanged and blind judge inputs expose neither workflow nor seed labels
- Acceptance [done]: All workflow-lab tests pass

## 2026-07-27 - Complete wp5-v5 schema preflight checkpoint (T-039)

- Done: Complete wp5-v5 schema preflight checkpoint
- Checked by: `python -m unittest discover -s experiments/workflow-lab/tests -v` exit 0
- Next: Implement seed-wise wp5-v5 subject and blind-judge execution with the provider early-stop gate
- Evidence: `python -m unittest discover -s experiments/workflow-lab/tests -v` -> exit 0
- Acceptance [done]: The service accepts model-output.schema.json for protocol wp5-v5
- Acceptance [done]: Preflight artifacts prove zero task and oracle payloads and zero subject or judge batches
- Acceptance [done]: The pre-execution protocol test is advanced to the post-preflight checkpoint
- Acceptance [done]: All frozen hashes remain unchanged and no results or trial output exists

## 2026-07-27 - Preflight wp5-v5 schema and execution runner (T-038)

- Done: Preflight wp5-v5 schema and execution runner
- Checked by: `python -m unittest discover -s experiments/workflow-lab/tests -v` exit 0
- Next: switch to Complete wp5-v5 schema preflight checkpoint
- Evidence: `python -m unittest discover -s experiments/workflow-lab/tests -v` -> exit 0

## 2026-07-27 - Run and adjudicate wp5-v4 A/B/C comparison (T-033)

- Done: Run and adjudicate wp5-v4 A/B/C comparison
- Checked by: `python -m unittest discover -s experiments/workflow-lab/tests -v` exit 0
- Next: Start wp5-v5 schema preflight with zero task and oracle payloads
- Evidence: `python -m unittest discover -s experiments/workflow-lab/tests -v` -> exit 0
- Acceptance [done]: All 12 subject batches and four blind judge batches complete with the frozen model policy or failures are recorded
- Acceptance [done]: Exactly 54 trial cells exist and judge inputs remain workflow-masked
- Acceptance [done]: Frozen v4 hashes remain unchanged
- Acceptance [done]: The report compares A/B/C and v3/v4 C on observed metrics
- Acceptance [done]: Implementation fields remain null and no ADOPT decision is made

## 2026-07-27 - Run frozen wp5-v3 contract trials (T-030)

- Done: Run frozen wp5-v3 contract trials
- Checked by: `python -m unittest discover -s experiments/workflow-lab/tests -v` exit 0
- Next: Close T-033 using the already committed wp5-v4 comparison and recovery evidence
- Evidence: `python -m unittest discover -s experiments/workflow-lab/tests -v` -> exit 0
- Acceptance [done]: all 54 cells have frozen-policy raw output and observation records or explicit identical-input failures
- Acceptance [done]: all v3 pretrial hashes remain unchanged
- Acceptance [done]: workflow labels are masked from judge inputs and aggregate metrics come from judge or deterministic runner evidence
- Acceptance [done]: report states contract-phase limitations and does not make an adoption decision from null implementation evidence
- Warning: Promised test file was never touched: experiments/workflow-lab/tests/test_evaluation_v3_results.py (declared at start with --tests, absent from the diff)

## 2026-07-27 - workflow labels are masked from judge inputs and aggregate metrics come from judge or deterministic runner evidence (T-037)

- Done: workflow labels are masked from judge inputs and aggregate metrics come from judge or deterministic runner evidence
- Checked by: manual check: All four v4 judge-input files omit workflow labels, and aggregate provenance tests prove metrics come from blind judge observations plus deterministic runner evidence
- Next: Close paused T-030 with completed wp5-v3 evidence

## 2026-07-27 - all 54 cells have frozen-policy raw output and observation records or explicit identical-input failures (T-036)

- Done: all 54 cells have frozen-policy raw output and observation records or explicit identical-input failures
- Checked by: manual check: wp5-v4 has 54 exact frozen-policy trial records, 12 completed subject batches, 4 completed judge batches, and preserved identical-input recovery evidence
- Next: Close T-037 using workflow-masked judge inputs and deterministic observation aggregation tests

## 2026-07-27 - Run frozen wp5-v2 contract trials (T-028)

- Done: Run frozen wp5-v2 contract trials
- Checked by: `python -m unittest discover -s experiments/workflow-lab/tests -v` exit 0
- Next: Historical reconciliation complete: v2 execution failed before subjects and was superseded by completed v3/v4 runs
- Evidence: `python -m unittest discover -s experiments/workflow-lab/tests -v` -> exit 0
- Acceptance [deferred]: all 54 cells have frozen-policy raw output and observation records or explicit identical-input failures
- Acceptance [done]: all v2 pretrial hashes remain unchanged
- Acceptance [deferred]: workflow labels are masked from judge inputs and aggregate metrics come from judge or deterministic runner evidence
- Acceptance [done]: report states contract-phase limitations and does not make an adoption decision from null implementation evidence
- Deferred: all 54 cells have frozen-policy raw output and observation records or explicit identical-input failures (registered as a follow-up task)
- Deferred: workflow labels are masked from judge inputs and aggregate metrics come from judge or deterministic runner evidence (registered as a follow-up task)
- Warning: Promised test file was never touched: experiments/workflow-lab/tests/test_evaluation_v2_results.py (declared at start with --tests, absent from the diff)

## 2026-07-27 - Run frozen wp5-v2 contract trials (T-028)

- Done: Run frozen wp5-v2 contract trials
- Checked by: `python -m unittest discover -s experiments/workflow-lab/tests -v` exit 0
- Next: T-028 ended before subject execution because the frozen v2 schema was service-incompatible; wp5-v3 is the completed successor
- Evidence: `python -m unittest discover -s experiments/workflow-lab/tests -v` -> exit 0
- Warning: Promised test file was never touched: experiments/workflow-lab/tests/test_evaluation_v2_results.py (declared at start with --tests, absent from the diff)

## 2026-07-27 - Run frozen wp5-v2 contract trials (T-028)

- Done: Run frozen wp5-v2 contract trials
- Checked by: `python -m unittest discover -s experiments/workflow-lab/tests -v` exit 0
- Next: T-028 is superseded by schema-compatible wp5-v3; close T-030 using completed v3 evidence
- Evidence: `python -m unittest discover -s experiments/workflow-lab/tests -v` -> exit 0

## 2026-07-27 - aggregate metrics are computed from observation records rather than subject self-scoring (T-026)

- Done: aggregate metrics are computed from observation records rather than subject self-scoring
- Checked by: manual check: Tests prove aggregate metrics are read from adjudicated observation records; runner joins blind judge observations to subject references before deterministic aggregation
- Next: Reconcile paused superseded v2/v3/v4 run tasks before starting v5 preflight

## 2026-07-27 - all 54 workflow-task cells use the frozen model policy or failures are explicitly recorded (T-025)

- Done: all 54 workflow-task cells use the frozen model policy or failures are explicitly recorded
- Checked by: manual check: v4 run metadata records 12 completed subject batches and 4 completed blind-judge batches; 54 exact trial records and frozen-hash tests pass
- Next: Close T-026 using aggregate provenance tests that reject subject self-scoring

## 2026-07-25 - Repair and refreeze wp5-v5 machine contracts (T-035)

- Done: Repair and refreeze wp5-v5 machine contracts
- Checked by: `python3 -m unittest discover -s experiments/workflow-lab/tests -v` exit 0; `npm run ci` exit 0
- Next: Keep v5 schema preflight, subject, and judge execution paused until separately authorized
- Evidence: `python3 -m unittest discover -s experiments/workflow-lab/tests -v` -> exit 0
- Evidence: `npm run ci` -> exit 0
- Acceptance [done]: Every v5 trial record requires an auditable seed identifier
- Acceptance [done]: Manifest and schemas consistently name A, B, C5, with C5p only as a contingency
- Acceptance [done]: Automated tests enforce v5 hashes, allowed v4 differences, sampling math, and contract consistency
- Acceptance [done]: No v5 preflight, subject, judge, or result execution occurs

## 2026-07-25 - T-033 (T-033)

- Done: T-033
- Checked by: retroactive entry - verify commands were registered (`python -m unittest discover -s experiments/workflow-lab/tests -v`); original console evidence was lost to a ledger bug
- Next: decide with the user
- Warning: this entry was written by progress --repair, after the close itself skipped the journal

## 2026-07-25 - Finalize wp5-v4 results after UTF-8 runner recovery (T-034)

- Done: Finalize wp5-v4 results after UTF-8 runner recovery
- Checked by: `python -m unittest discover -s experiments/workflow-lab/tests -v` exit 0
- Next: Do not integrate natively; decide between a smaller repeated-seed v5 and implementation follow-through after reviewing v4 cost and remaining novice provider choice
- Evidence: `python -m unittest discover -s experiments/workflow-lab/tests -v` -> exit 0
- Acceptance [done]: The original encoding failure and pre-retry raw output remain preserved
- Acceptance [done]: The runner decodes Codex output as UTF-8 and reuses only complete raw/event batch pairs
- Acceptance [done]: All 54 cells and 16 final batches pass integrity tests
- Acceptance [done]: Frozen v4 input hashes remain unchanged
- Acceptance [done]: The report concludes REVISE and withholds native adoption

## 2026-07-25 - Freeze and preflight wp5-v4 Guided Convergence revision (T-032)

- Done: Freeze and preflight wp5-v4 Guided Convergence revision
- Checked by: `python -m unittest discover -s experiments/workflow-lab/tests -v` exit 0
- Next: Run all wp5-v4 subject and blind-judge batches, compare results with v3, and keep adoption withheld without implementation evidence
- Evidence: `python -m unittest discover -s experiments/workflow-lab/tests -v` -> exit 0
- Acceptance [done]: A and B, all tasks, hidden oracles, rubric semantics, model, batching, and blinding remain byte-identical to v3
- Acceptance [done]: C requires risk controls and every decision dependency before readiness
- Acceptance [done]: C converts novice mechanism choices into agent investigation or outcome authorization
- Acceptance [done]: Clear local reversible tasks retain the zero-question quick path
- Acceptance [done]: Frozen hashes and no-task service schema preflight pass before subject execution

## 2026-07-25 - Finalize wp5-v3 results and lifecycle assertions (T-031)

- Done: Finalize wp5-v3 results and lifecycle assertions
- Checked by: `python -m unittest discover -s experiments/workflow-lab/tests -v` exit 0
- Next: Revise Guided Convergence treatment C around audit boundaries, decision dependencies, and novice technical choices before a v4 rerun
- Evidence: `python -m unittest discover -s experiments/workflow-lab/tests -v` -> exit 0
- Acceptance [done]: all 54 cells and 16 batches remain complete and unchanged
- Acceptance [done]: preflight assertions verify historical metadata rather than forbidding later results
- Acceptance [done]: frozen hashes and workflow-masked judge inputs pass
- Acceptance [done]: report records the unfavorable C metrics and withholds adoption

## 2026-07-25 - Record v2 preflight and freeze service-compatible v3 (T-029)

- Done: Record v2 preflight and freeze service-compatible v3
- Checked by: `python -m unittest discover -s experiments/workflow-lab/tests -v` exit 0
- Next: Run the frozen wp5-v3 subject and blind-judge batches using the successful schema preflight
- Evidence: `python -m unittest discover -s experiments/workflow-lab/tests -v` -> exit 0
- Acceptance [done]: v2 frozen inputs remain unchanged and zero subject outputs are recorded
- Acceptance [done]: freeze tests validate input hashes rather than forbidding later result evidence
- Acceptance [done]: v3 changes only service-required explicit types and execution paths
- Acceptance [done]: v3 schema preflight succeeds before any subject batch

## 2026-07-25 - Freeze corrected wp5-v2 protocol (T-027)

- Done: Freeze corrected wp5-v2 protocol
- Checked by: `python -m unittest discover -s experiments/workflow-lab/tests -v` exit 0
- Next: Execute the frozen wp5-v2 subject and blind-judge batches, aggregate observations, and report contract-phase evidence
- Evidence: `python -m unittest discover -s experiments/workflow-lab/tests -v` -> exit 0
- Acceptance [done]: v2 changes only the preflight defects and preserves task/treatment semantics
- Acceptance [done]: gpt-5.4 medium availability evidence is recorded before freezing
- Acceptance [done]: all contract-unobservable metrics accept null and cannot authorize adoption
- Acceptance [done]: new content hashes are frozen with zero subject outputs

## 2026-07-25 - Run frozen wp5-v1 comparative trials (T-024)

- Done: Run frozen wp5-v1 comparative trials
- Checked by: `python -m unittest discover -s experiments/workflow-lab/tests -v` exit 0
- Next: switch to Freeze corrected wp5-v2 protocol
- Evidence: `python -m unittest discover -s experiments/workflow-lab/tests -v` -> exit 0
- Acceptance [deferred]: all 54 workflow-task cells use the frozen model policy or failures are explicitly recorded
- Acceptance [done]: pretrial hashes remain unchanged throughout execution
- Acceptance [deferred]: aggregate metrics are computed from observation records rather than subject self-scoring
- Acceptance [done]: report distinguishes contract-phase evidence from unmeasured implementation outcomes and makes no premature adoption claim
- Deferred: all 54 workflow-task cells use the frozen model policy or failures are explicitly recorded (registered as a follow-up task)
- Deferred: aggregate metrics are computed from observation records rather than subject self-scoring (registered as a follow-up task)

## 2026-07-25 - Run frozen wp5-v1 comparative trials (T-024)

- Done: Run frozen wp5-v1 comparative trials
- Checked by: `python -m unittest discover -s experiments/workflow-lab/tests -v` exit 0
- Next: Freeze wp5-v2 with gpt-5.4 and nullable follow-through metrics, then run contract-phase trials
- Evidence: `python -m unittest discover -s experiments/workflow-lab/tests -v` -> exit 0

## 2026-07-25 - Freeze Guided Convergence evaluation protocol (T-023)

- Done: Freeze Guided Convergence evaluation protocol
- Checked by: `python -m unittest discover -s experiments/workflow-lab/tests -v` exit 0
- Next: Run wp5-v1 contract-phase A/B/C trials against the frozen hashes without modifying pretrial inputs
- Evidence: `python -m unittest discover -s experiments/workflow-lab/tests -v` -> exit 0
- Acceptance [done]: manifest contains exactly 18 balanced tasks and both novice and expert inputs
- Acceptance [done]: A/B/C prompts share one output contract while preserving their workflow differences
- Acceptance [done]: rubric maps every planned metric to objective fields and adoption thresholds
- Acceptance [done]: freeze hashes and deterministic scorer pass tests before any result file exists

## 2026-07-25 - Compose guided contract orchestration (T-022)

- Done: Compose guided contract orchestration
- Checked by: `python -m unittest discover -s experiments/workflow-lab/tests -v` exit 0
- Next: WP5: freeze the comparative evaluation manifest and scoring rubric before running workflows A, B, and C
- Evidence: `python -m unittest discover -s experiments/workflow-lab/tests -v` -> exit 0
- Acceptance [done]: clear bounded scenarios bypass interview and reach a typed draft
- Acceptance [done]: guided scenarios ask one complete outcome-level question and preserve blocking unknowns
- Acceptance [done]: I do not know, Draft Delta, reversible readiness, and delayed promotion rules are explicit
- Acceptance [done]: diagnosis routing and CodeRail public lifecycle authority remain intact

## 2026-07-25 - Implement model-invoked coderail-frame (T-021)

- Done: Implement model-invoked coderail-frame
- Checked by: `python -m unittest discover -s experiments/workflow-lab/tests -v` exit 0
- Next: WP3: compose coderail-frame into coderail-grill-contract and complete the remaining scenario fixtures
- Evidence: `python -m unittest discover -s experiments/workflow-lab/tests -v` -> exit 0
- Acceptance [done]: standard skill validator passes for coderail-frame
- Acceptance [done]: repository evidence suppresses resolved user-facing questions
- Acceptance [done]: domain lenses are labeled candidates and only one high-impact unknown is surfaced
- Acceptance [done]: CodeRail authority and no-side-effect boundaries remain intact

## 2026-07-25 - Define Guided Convergence WP1 protocol fixtures (T-019)

- Done: Define Guided Convergence WP1 protocol fixtures
- Checked by: `python -m unittest discover -s experiments/workflow-lab/tests -v` exit 0
- Next: Implement WP2 coderail-frame against the frozen protocol fixtures
- Evidence: `python -m unittest discover -s experiments/workflow-lab/tests -v` -> exit 0
- Acceptance [done]: Contract Draft fixture distinguishes FACT ASSUMPTION DECISION and UNKNOWN
- Acceptance [done]: Draft Delta contains only changed item references
- Acceptance [done]: Four initial scenarios encode expected route and at most one first question
- Acceptance [done]: Readiness and glossary ADR promotion invariants are executable

## 2026-07-25 - Ignore phantom Git modifications on Windows (T-020)

- Done: Ignore phantom Git modifications on Windows
- Checked by: `python tests/test_closeout.py` exit 0
- Next: Resume T-019 and close the Guided Convergence WP1 fixtures
- Evidence: `python tests/test_closeout.py` -> exit 0
- Acceptance [done]: A tracked path reported M with an empty unstaged diff is omitted
- Acceptance [done]: Real staged and unstaged modifications remain classified
- Acceptance [done]: The Windows commit-pending regression passes

## 2026-07-21 - Fix scope contradiction and recoverable closeout commit pending (T-018)

- Done: Fix scope contradiction and recoverable closeout commit pending
- Checked by: `python3 tests/test_closeout.py` exit 0; `python3 tests/test_lifecycle.py` exit 0; `python3 tests/test_task_switch.py` exit 0; `python3 tests/test_structure.py` exit 0; `npm run ci` exit 0
- Next: decide with the user
- Evidence: `python3 tests/test_closeout.py` -> exit 0
- Evidence: `python3 tests/test_lifecycle.py` -> exit 0
- Evidence: `python3 tests/test_task_switch.py` -> exit 0
- Evidence: `python3 tests/test_structure.py` -> exit 0
- Evidence: `npm run ci` -> exit 0
- Acceptance [done]: start and switch reject scope contradictions without partial task state
- Acceptance [done]: narrow forbidden production paths allow declared tests through closeout
- Acceptance [done]: commit permission failure preserves verification and exact safe files as commit-pending
- Acceptance [done]: manual exact commit plus resume finalizes without CodeRail residue
- Acceptance [done]: explicit no-commit classifies all generated closeout files in one snapshot
- Acceptance [done]: unrelated dirty files remain untouched during recovery
- Acceptance [done]: resume is idempotent without duplicate progress, trace, or commits
- Acceptance [done]: existing auto-commit, scope, Task Switch Gate, and manual Drive regressions pass

## 2026-07-17 - Accept Markdown code-formatted scope paths (T-017)

- Done: Accept Markdown code-formatted scope paths
- Checked by: `python tests/test_static.py` exit 0; `python tests/test_closeout.py` exit 0; `python tests/test_structure.py` exit 0; `npm run ci` exit 0
- Next: decide with the user
- Evidence: `python tests/test_static.py` -> exit 0
- Evidence: `python tests/test_closeout.py` -> exit 0
- Evidence: `python tests/test_structure.py` -> exit 0
- Evidence: `npm run ci` -> exit 0
- Acceptance [done]: Inline-code allowed paths are accepted as their plain path equivalents
- Acceptance [done]: Inline-code forbidden paths retain blocking behavior
- Acceptance [done]: Plain path behavior remains compatible

## 2026-07-16 - Migrate legacy closed history out of hot TASKS (T-016)

- Done: Migrate legacy closed history out of hot TASKS
- Checked by: `python scripts/coderail.py check` exit 0; `python tests/test_closeout.py` exit 0; `python tests/test_structure.py` exit 0
- Next: observe real production tasks during the stabilization freeze
- Evidence: `python scripts/coderail.py check` -> exit 0
- Evidence: `python tests/test_closeout.py` -> exit 0
- Evidence: `python tests/test_structure.py` -> exit 0
- Acceptance [done]: legacy T-001 and T-002 receive honest retroactive PROGRESS authority
- Acceptance [done]: successful closeout compacts every closed body from TASKS
- Acceptance [done]: immediate inspect is healthy and hot context is at most 3000 estimated tokens

## 2026-07-16 - Doctor generated-marker compatibility (T-002)

- Done: Doctor generated-marker compatibility
- Checked by: retroactive entry - no verify commands were registered
- Next: decide with the user
- Warning: this entry was written by progress --repair, after the close itself skipped the journal

## 2026-07-16 - Self-bootstrap CodeRail execution boundary (T-001)

- Done: Self-bootstrap CodeRail execution boundary
- Checked by: retroactive entry - no verify commands were registered
- Next: decide with the user
- Warning: this entry was written by progress --repair, after the close itself skipped the journal

## 2026-07-16 - Bound governance hot context growth (T-015)

- Done: Bound governance hot context growth
- Checked by: `python tests/observe_context_growth.py --tasks 10 --startup-runs 10 --assert-thresholds` exit 0; `python tests/test_static.py` exit 0; `python tests/test_lifecycle.py` exit 0; `python tests/test_inspect.py` exit 0; `python tests/test_task_switch.py` exit 0; `python tests/test_closeout.py` exit 0; `python tests/test_structure.py` exit 0; `npm run ci` exit 0
- Next: observe real production tasks during the stabilization freeze
- Evidence: `python tests/observe_context_growth.py --tasks 10 --startup-runs 10 --assert-thresholds` -> exit 0
- Evidence: `python tests/test_static.py` -> exit 0
- Evidence: `python tests/test_lifecycle.py` -> exit 0
- Evidence: `python tests/test_inspect.py` -> exit 0
- Evidence: `python tests/test_task_switch.py` -> exit 0
- Evidence: `python tests/test_closeout.py` -> exit 0
- Evidence: `python tests/test_structure.py` -> exit 0
- Evidence: `npm run ci` -> exit 0
- Acceptance [done]: required context files ceil bytes over four estimate and 3000 token limit remain fixed
- Acceptance [done]: closes two through ten add zero bytes to required context and TASKS
- Acceptance [done]: TASKS persists only open work while PROGRESS plus TRACE authoritatively retain completed history
- Acceptance [done]: reports and metadata are supplemental rather than sole history
- Acceptance [done]: ten task IDs are unique and strictly increasing with ten PROGRESS and TRACE facts
- Acceptance [done]: compaction follows durable close evidence and ledger failure remains recoverable
- Acceptance [done]: legacy cutoff verification debt progress repair task switch and paused resume remain correct
- Acceptance [done]: active queued paused ownership and glob intent remain resumable
- Acceptance [done]: done followed by inspect remains healthy with no closed ownership

## 2026-07-16 - Measure synthetic task context growth (T-014)

- Done: Measure synthetic task context growth
- Checked by: `python tests/test_static.py` exit 0; `python tests/observe_context_growth.py --tasks 3` exit 0
- Next: Decide whether the 3000-token hot-context limit and zero closed-history growth become accepted invariants before creating a bug task.
- Evidence: `python tests/test_static.py` -> exit 0
- Evidence: `python tests/observe_context_growth.py --tasks 3` -> exit 0
- Acceptance [done]: a disposable standard project completes 10 sequential start check done cycles
- Acceptance [done]: the report separates active queued paused and closed task bytes
- Acceptance [done]: the report includes median and P95 for start check done and startup proxy
- Acceptance [done]: the experiment changes no production runtime or external repository

## 2026-07-16 - Codify defect-only stabilization freeze (T-013)

- Done: Codify defect-only stabilization freeze
- Checked by: `python tests/test_static.py` exit 0; `python scripts/coderail.py check` exit 0
- Next: Observe current workflows and create no implementation task until a defect is reproduced with exact evidence.
- Evidence: `python tests/test_static.py` -> exit 0
- Evidence: `python scripts/coderail.py check` -> exit 0
- Acceptance [done]: feature freeze and non-goals are explicit
- Acceptance [done]: defect candidates require reproducible evidence before implementation
- Acceptance [done]: accepted fixes require failing characterization or regression coverage
- Acceptance [done]: policy adds no runtime command or gate

## 2026-07-15 - Split characterization test monolith (T-012)

- Done: Split characterization test monolith
- Checked by: `python tests/test_structure.py` exit 0; `npm run ci` exit 0
- Next: Keep the feature freeze; use the split suite to diagnose real lifecycle defects before authorizing any new gate.
- Evidence: `python tests/test_structure.py` -> exit 0
- Evidence: `npm run ci` -> exit 0
- Acceptance [done]: no test module exceeds 650 lines
- Acceptance [done]: all 104 tests remain discoverable exactly once
- Acceptance [done]: responsibility groups run independently
- Acceptance [done]: npm test and npm run ci entry points remain green

## 2026-07-15 - Delete repository-state compatibility adapters (T-011)

- Done: Delete repository-state compatibility adapters
- Checked by: `python tests/test_structure.py` exit 0; `npm run ci` exit 0
- Next: Start T-012 and split the test monolith by responsibility without changing suite entry points.
- Evidence: `python tests/test_structure.py` -> exit 0
- Evidence: `npm run ci` -> exit 0
- Acceptance [done]: no runtime caller uses task_switch git-status or snapshot compatibility adapters
- Acceptance [done]: closeout, inspect, done and switch consume FileState or RepositorySnapshot
- Acceptance [done]: runtime code in touched closeout modules is net-negative
- Acceptance [done]: done and inspect behavior remains characterized and healthy

## 2026-07-15 - Queued task verification evidence hydration (T-010)

- Done: Queued task verification evidence hydration
- Checked by: `python tests/test_structure.py` exit 0; `npm run ci` exit 0
- Next: Keep the closeout feature freeze and collect field evidence before any further decomposition
- Evidence: `python tests/test_structure.py` -> exit 0
- Evidence: `npm run ci` -> exit 0
- Acceptance [done]: queued V commands hydrate without executing prose examples
- Acceptance [done]: verified queued closeout is not labeled unverified

## 2026-07-15 - Single closeout transaction authority (T-009)

- Done: Single closeout transaction authority
- Checked by: closeout CI gate passed (103 structure tests plus all configured gates)
- Evidence: `.coderail/reports/done-20260715-091212-T-009.md` records `103 tests passed` and `CI Gate Report: Status: passed`
- Next: Hold the feature freeze and observe the converged closeout in field repositories
- Acceptance [done]: only FINALIZED can render Done or return success
- Acceptance [done]: stage, commit, persistence, rescan, or inspect failure returns an explicit transaction failure
- Acceptance [done]: provisional closure is compensatingly reopened on late failure
- Acceptance [done]: duplicate closeout sequencing and success judgments are deleted
- Acceptance [done]: immediate inspect agrees with every successful done

## 2026-07-15 - Canonical repository snapshot and ownership classifier (T-008)

- Done: Canonical repository snapshot and ownership classifier
- Checked by: `python tests/test_structure.py` exit 0 (100 tests); closeout CI gate passed
- Evidence: `.coderail/reports/done-20260715-090436-T-008.md` records `100 tests passed` and `CI Gate Report: Status: passed`
- Next: Activate T-009 and move closeout sequencing behind one transaction authority

## 2026-07-15 - Closeout characterization harness and convergence specification (T-007)

- Done: Closeout characterization harness and convergence specification
- Checked by: `python tests/test_structure.py` exit 0; `npm test` exit 0; `npm run ci` exit 0
- Next: Activate T-008 and migrate repository facts without changing characterized behavior
- Evidence: `python tests/test_structure.py` -> exit 0
- Evidence: `npm test` -> exit 0
- Evidence: `npm run ci` -> exit 0
- Acceptance [done]: spec defines invariants, non-goals, state model and migration boundaries
- Acceptance [done]: characterization matrix covers tracked, glob, adoption, outside, sensitive, generated, rename/delete and post-commit mutation
- Acceptance [done]: T-008 and T-009 have explicit dependency, scope, verification and stop contracts

## 2026-07-15 - Atomic closeout success and post-commit inspect (T-006)

- Done: Atomic closeout success and post-commit inspect
- Checked by: `python tests/test_structure.py` exit 0; `npm test` exit 0; `npm run ci` exit 0
- Next: Observe atomic closeout in additional field repositories and consider consolidating the two local closeout commits without weakening recovery
- Evidence: `python tests/test_structure.py` -> exit 0
- Evidence: `npm test` -> exit 0
- Evidence: `npm run ci` -> exit 0
- Acceptance [done]: tracked modifications, new glob files, deletions and renames close cleanly
- Acceptance [done]: unborn baseline adoption closes cleanly without ledger-only commits
- Acceptance [done]: outside, sensitive, generated and ambiguous paths never cause false success
- Acceptance [done]: post-commit rescan and inspect inconsistency force done failure
- Acceptance [done]: no implementation or test uses git add .

## 2026-07-15 - Safe ownership for new files and baseline adoption (T-005)

- Done: Safe ownership for new files and baseline adoption
- Checked by: `python tests/test_structure.py` exit 0; `npm test` exit 0; `npm run ci` exit 0
- Next: Review baseline adoption ergonomics and extend sensitive-pattern configuration if field evidence requires it
- Evidence: `python tests/test_structure.py` -> exit 0
- Evidence: `npm test` -> exit 0
- Evidence: `npm run ci` -> exit 0
- Acceptance [done]: lib/** owns new matching files created after start
- Acceptance [done]: baseline adoption records fingerprints and excludes unsafe files
- Acceptance [done]: done blocks ambiguous or forbidden files before closure
- Acceptance [done]: done followed by inspect has no closed-task ownership

## 2026-07-14 - Prepare v0.9.0 release (T-004)

- Done: Prepare v0.9.0 release
- Checked by: `python3 tests/test_structure.py` exit 0; `npm test` exit 0; `npm run ci` exit 0; `mkdir -p /tmp/coderail-v090-smoke && python3 scripts/init_project.py --target /tmp/coderail-v090-smoke --mode standard --force && rg -q '^SHIM_VERSION = "0\.9\.0"$' /tmp/coderail-v090-smoke/.coderail/coderail.py` exit 0
- Next: Review the v0.9.0 local release candidate, then authorize tag and push separately.
- Evidence: `python3 tests/test_structure.py` -> exit 0
- Evidence: `npm test` -> exit 0
- Evidence: `npm run ci` -> exit 0
- Evidence: `mkdir -p /tmp/coderail-v090-smoke && python3 scripts/init_project.py --target /tmp/coderail-v090-smoke --mode standard --force && rg -q '^SHIM_VERSION = "0\.9\.0"$' /tmp/coderail-v090-smoke/.coderail/coderail.py` -> exit 0
- Acceptance [done]: VERSION, package metadata, plugin manifests, and README badge agree on 0.9.0
- Acceptance [done]: v0.9.0 changelog covers Task Switch Gate, closeout ledger integrity, and FN-029
- Acceptance [done]: fresh install smoke reports shim v0.9.0
- Acceptance [done]: full regression and CI pass
- Acceptance [done]: release review finds no package or lockfile drift
- Acceptance [done]: no tag and no push are created

## 2026-07-14 - Task Switch Gate (T-003)

- Done: Task Switch Gate
- Checked by: `python3 tests/test_structure.py` exit 0; `npm test` exit 0; `npm run ci` exit 0
- Next: Review the T-003 commits, then authorize release/push or downstream production sync separately.
- Evidence: `python3 tests/test_structure.py` -> exit 0
- Evidence: `npm test` -> exit 0
- Evidence: `npm run ci` -> exit 0
- Acceptance [done]: accepted current task closes and commits before the destination starts
- Acceptance [done]: verified checkpoint commits then pauses the source before the destination starts
- Acceptance [done]: uncommittable work writes H3 and requires continue-current or dirty-fork
- Acceptance [done]: closed-task dirty ownership blocks ordinary start and next --go
- Acceptance [done]: pre-existing unrelated changes are fingerprinted and excluded from new-task attribution
- Acceptance [done]: dirty-fork preserves one active task and records the carried baseline
- Acceptance [done]: no switch or closeout path runs git push
