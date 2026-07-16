# Synthetic Context Growth Observation

Status: reproduced observation; implementation not authorized
Task: T-014
Candidate runtime: `f33d14a`
Environment: Windows, Python 3.13
Raw evidence: `docs/observations/context-growth-20260716.json`

## Method

The observer created one disposable Git repository using CodeRail's local
standard installation template. It added one stable `src/state.txt`, committed
the baseline, then completed ten real `start -> check -> done -> inspect`
cycles. Every task owned the same `src/**` scope and modified the same file, so
project growth did not inflate the governance measurement.

Each successful done was followed by a read-only inspect and a clean-worktree
assertion. Startup timing used twenty fresh Python processes. No production
runtime file, external repository, remote, or network resource was changed.

## Result

| Measure | Initial | After 10 tasks | Change |
| --- | ---: | ---: | ---: |
| required governance read | 10,958 B | 20,320 B | +9,362 B |
| estimated context | 2,740 tokens | 5,080 tokens | +2,340 tokens |
| `TASKS.md` | 2,317 B | 11,078 B | +8,761 B |
| closed task bodies | 0 B | 8,149 B | +8,149 B |
| logical context without closed bodies | 10,958 B | 12,171 B | +1,213 B |

Measured slopes:

- `TASKS.md`: 869.5 bytes per closed task;
- required governance read: 896.818 bytes per closed task;
- closed history: 814.955 bytes per task;
- after the first cycle, each additional synthetic task added exactly 864
  bytes to `TASKS.md` in this controlled fixture.

At the final measurement there were no active, queued, or paused tasks. Closed
task bodies still occupied 73.6% of `TASKS.md` and 40.1% of the complete
required-read set. The required-read estimate exceeded the proposed 3,000
token threshold after the first completed task and reached 5,080 tokens after
ten.

## Latency

| Command | Median | P95 |
| --- | ---: | ---: |
| start | 325.227 ms | 366.057 ms |
| check | 440.959 ms | 471.840 ms |
| done | 4,057.103 ms | 4,173.385 ms |

Fresh-process startup medians:

- empty Python: 74.008 ms;
- `coderail --help`: 144.195 ms;
- eager-import proxy: 70.187 ms.

The proxy is about 15.9% of median `check` time, below the proposed 30%
admission threshold. Eager imports are measurable but are not the primary
candidate from this experiment.

## Classification

The experiment reproduces linear governance-context growth caused primarily by
closed task bodies remaining in the required `TASKS.md` read path. It does not
yet authorize a fix. The next decision is whether the 3,000-token hot-context
limit and zero closed-history growth become accepted product invariants.

If admitted, the regression harness should require completed history to move
off the hot path while retaining active/queued summaries, glob intent,
fingerprinted metadata, PROGRESS, TRACE, and done reports. Runtime line count
must remain a separate maintainability measure.
