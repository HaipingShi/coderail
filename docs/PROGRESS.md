# Progress - plain language, newest first

If you only read one file in this project, read this one.
Each entry: what got done, how it was checked, what comes next.

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
