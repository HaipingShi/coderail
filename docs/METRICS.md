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

Inventory: 104 unique tests, zero duplicate names, maximum module size 418
lines. All six responsibility groups run independently.

## M-013 Stabilization Freeze

- observations awaiting reproduction: 0 known
- reproduced defects awaiting a numbered task: 0
- fixes requiring scope expansion: 0
- regressions found after successful `done`: 0
- explicitly approved feature-freeze exceptions: 0

These are observation measures, not activity targets. Do not create tasks to
improve an empty counter.
