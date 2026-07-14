# Progress - plain language, newest first

If you only read one file in this project, read this one.
Each entry: what got done, how it was checked, what comes next.

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
