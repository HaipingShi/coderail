# Metrics

- coordinate coverage:
- trace coverage:
- done-without-verify count:
- orphan event count:
- handoff trace link coverage:
- unnecessary stop count:
- autonomous task transition count:
- no-progress exhaustion count:
- unsafe decision crossing count:
- drive scenario agreement:

## M-012 Lean Convergence

| Measure | T-011 baseline | T-011 result | Direction |
| --- | ---: | ---: | --- |
| closeout runtime lines | 3,258 | 3,237 | decrease |
| repository-state adapter definitions | 3 | 0 | zero |
| runtime adapter call sites | 4 | 0 | zero |
| porcelain parsers | 1 | 1 | hold |
| ownership classifiers | 1 | 1 | hold |
| tests | 103 | 104 | no decrease |
| `test_structure.py` lines | 1,910 | measured in T-012 | decrease |

T-012 will record per-module lines, unique discovered test names, targeted
group results, and unchanged full-suite entry points.

### T-012 Result

| Test module | Lines | Tests |
| --- | ---: | ---: |
| `test_structure.py` | 37 | aggregator |
| `test_support.py` | 247 | support |
| `test_static.py` | 418 | 28 |
| `test_drive.py` | 292 | 29 |
| `test_inspect.py` | 98 | 7 |
| `test_task_switch.py` | 197 | 11 |
| `test_lifecycle.py` | 337 | 15 |
| `test_closeout.py` | 273 | 14 |

T-012 retained 104 unique tests with zero duplicate names and a maximum module
size of 418 lines. T-014 adds one observer contract test, bringing the current
inventory to 105. T-015 adds three authority, threshold, and recovery
regressions, bringing the current inventory to 108. All six responsibility
groups remain independently runnable.

## M-013 Stabilization Freeze

- observations awaiting reproduction: 0 known
- reproduced observations awaiting admission decision: 1 context-growth case
- admitted defects awaiting a numbered bug task: 0
- fixes requiring scope expansion: 0
- regressions found after successful `done`: 0
- explicitly approved feature-freeze exceptions: 0

These are observation measures, not activity targets. Do not create tasks to
improve an empty counter.

## M-014 Synthetic Context Growth

- standard disposable project cycles: 10
- required-read growth: 896.818 bytes per closed task
- `TASKS.md` growth: 869.5 bytes per closed task
- closed-history growth: 814.955 bytes per task
- initial/final estimated tokens: 2,740 / 5,080
- final active/queued/paused task bytes: 0 / 0 / 0
- start median/P95: 325.227 / 366.057 ms
- check median/P95: 440.959 / 471.840 ms
- done median/P95: 4,057.103 / 4,173.385 ms
- eager-import proxy median: 70.187 ms

Outcome: linear closed-history context growth is reproduced. Eager imports are
observable but remain below the provisional admission threshold.

## M-015 Bounded Hot Context

| Measure | T-014 baseline | T-015 result |
| --- | ---: | ---: |
| final required-read bytes after 10 closes | 20,320 | 10,330 |
| final estimated tokens | 5,080 | 2,583 |
| TASKS growth after closes 2-10 | linear | 0 bytes |
| required-read growth after closes 2-10 | linear | 0 bytes |
| closed-history TASKS growth/task | 814.955 bytes | 0 bytes |
| unique increasing task IDs | not asserted | 10 / 10 |
| PROGRESS / TRACE task evidence | not asserted | 10 / 10 each |

The runtime line count remains a maintenance observation, not a context proxy.
The accepted regression boundary is the fixed five-file read set and its
byte-based threshold.
