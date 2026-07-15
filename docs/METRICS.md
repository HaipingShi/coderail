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
