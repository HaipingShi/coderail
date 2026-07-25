# Matt Pocock Skills -> CodeRail Absorption Plan

Date: 2026-07-23
Last updated: 2026-07-25

## 1. Research Baseline

- Upstream: `https://github.com/mattpocock/skills.git`
- Analyzed commit: `ed37663cc5fbef691ddfecd080dff42f7e7e350d`
- Commit date: `2026-07-21 11:28:51 +0100`
- Clone: `G:\codeRail\research-mattpocock-skills`
- License: MIT. Any copied or substantially derived text must retain Matt
  Pocock's copyright and MIT notice.
- Upstream main is between release states: `package.json` says `1.1.0`, while
  `.claude-plugin/plugin.json` says `1.2.0`. Integration must pin a commit SHA,
  not follow `main` or infer compatibility from one version field.

The analysis covers promoted engineering/productivity skills, their invocation
metadata, setup assumptions, helper scripts, plugin packaging, and CodeRail
v0.9.0's current task, hook, TDD, closeout, context, and freeze contracts.

## 2. Decision

Do not import the workflow wholesale and do not build an LLM-driven hook that
selects and runs it.

Adopt a three-layer model:

1. **Optional reasoning skills** help the agent clarify, diagnose, test, and
   review.
2. **A thin CodeRail adapter** translates useful outputs into the current
   G/T/S/V/X/P task contract and existing repository records.
3. **The deterministic CodeRail kernel** remains the sole owner of task state,
   file ownership, verification, trace, commit, and finalization.

The first deliverable should be a small optional skill pack, not a command,
state, issue-tracker integration, or new lifecycle.

## 3. What Matt's Repository Actually Is

The promoted system is mostly Markdown agent skills. It is not a runtime
orchestrator and does not use a smart hook to run the main workflow.

It explicitly separates:

- **User-invoked skills**: the human chooses an orchestrator such as
  `ask-matt`, `grill-with-docs`, `to-spec`, `to-tickets`, or `implement`.
- **Model-invoked skills**: the agent may autonomously use references such as
  `diagnosing-bugs`, `tdd`, `domain-modeling`, `codebase-design`, and
  `code-review`.
- **Router**: `ask-matt` reduces the human memory burden but recommends a flow;
  it is not a hook and does not own state.

The promoted set contains no operational hook system. A dangerous-Git
`PreToolUse` hook exists only under `skills/misc/`, which is deliberately not
shipped in the promoted plugin.

## 4. Architectural Comparison

| Concern | Matt Skills | CodeRail | Decision |
|---|---|---|---|
| Primary value | Better reasoning process | Deterministic convergence | Compose, do not merge kernels |
| Canonical work state | Issue tracker/spec/tickets | `TASKS`, metadata, TRACE | CodeRail remains canonical |
| Planning direction | Grill -> spec -> tickets | Explore -> verify -> ratify | Spec flow stays optional |
| Invocation | User/model skill taxonomy | Most skills currently look model-reachable | Adopt taxonomy and router principle |
| TDD | Red -> green at agreed seams | Red/green/refactor/regression/CI evidence | Add seam/test-quality guidance; keep CodeRail evidence |
| Review | Standards and Spec parallel axes | Done gate verifies scope/evidence | Add optional pre-done evidence, never replace done |
| Commit | `implement` commits current branch | Exact audited task snapshot | CodeRail exclusively owns commits |
| Handoff | Temporary OS file | Durable repo-local H0-H3 policy | Keep CodeRail handoff |
| Issue tracker | Required by many skills | Explicit non-goal | Adapt to local tasks or exclude |
| Hooks | One non-promoted Git guard | Prompt/pre-edit/doctor/stop guard | Hooks stay deterministic |

## 5. Direct Conflicts That Must Not Be Vendored Unchanged

### Commit ownership

`implement` ends with a direct commit. `resolving-merge-conflicts` stages
everything and commits. Both conflict with CodeRail's exact safe-file snapshot,
single task owner, commit-pending recovery, and no-`git add .` invariants.

Rule: adapted skills may request `coderail done`; they may never stage or commit
task work themselves.

### Spec as an input

`to-spec` and `to-tickets` form the default multi-session path upstream.
CodeRail's product thesis is that spec is an output of verified discovery.

Rule: these skills are opt-in for sufficiently understood, multi-session work.
They must not become prerequisites for `start`.

### Competing canonical stores

Matt's engineering setup requires an issue tracker, triage labels,
`CONTEXT.md`, and ADR layout. CodeRail explicitly is not an issue tracker and
already owns `TASKS`, `DECISIONS`, `HANDOFF`, `PROGRESS`, and TRACE.

Rule: no duplicate truth. Adapt useful output into existing CodeRail records.
External issue synchronization, if ever added, is a separate future adapter.

### Human-interrupt policy

Matt's TDD skill requires confirmation of every test seam before writing a
test. CodeRail's continuous modes should not stop for low-risk, recoverable
choices.

Rule: record pre-agreed seams in the task contract when risk or ambiguity makes
the choice decision-grade. Otherwise select an existing public seam and
continue.

### Handoff semantics

Matt's handoff writes outside the repository. CodeRail intentionally makes
handoff and resume state inspectable in the repository and only writes it for
H1/H2/H3.

Rule: do not import Matt's handoff implementation.

### Vocabulary collision

`codebase-design` asks agents to avoid words such as component, service, API,
and boundary in favor of its exact glossary. CodeRail already has durable
meanings for boundary, adapter, scope, and kernel.

Rule: absorb design principles, not a mandatory global vocabulary.

## 6. Absorption Matrix

### A. Absorb first

#### `diagnosing-bugs`

Value:

- Makes a tight, red-capable reproduction command the prerequisite for theory.
- Covers test, CLI, browser, replay, fuzz, bisection, differential, and HITL
  feedback loops.
- Matches CodeRail's stabilization policy that only reproduced defects may
  authorize code changes.

Adaptation:

- Output the reproduction command into `V -- Verify`.
- Use `coderail start --type bug --verify "<command>"`.
- Preserve CodeRail's retry/no-progress and stop rules.
- Do not vendor the Bash-only HITL helper as a core dependency; provide a
  portable recipe later only if measurements justify it.

#### TDD test-quality guidance

Value:

- Tests behavior through public seams.
- Detects implementation-coupled and tautological tests.
- Uses one vertical red/green tracer bullet at a time.

Adaptation:

- Add these as guidance to `tdd-gate`.
- Keep CodeRail's existing Refactor, Regression, and CI evidence fields even
  though upstream moved refactoring out of its red/green loop.
- Do not add a new state or command.

#### Two-axis code review

Value:

- Separates "meets standards" from "implements the requested behavior".
- Separate contexts reduce anchoring between the two reviews.

Adaptation:

- Use the task activation baseline already stored by CodeRail instead of asking
  for an arbitrary fixed point.
- Use G/T/A acceptance as the Spec source.
- Use repository instructions as Standards; treat generic smells as advisory.
- Store a compact result as task verification evidence.
- Parallel sub-agents are an optional host capability, not a kernel
  requirement. Sequential isolated reviews must remain valid.

#### Invocation taxonomy and router principle

Value:

- Avoids loading every orchestration skill description into every turn.
- Separates model-autonomous reusable discipline from human-authorized flow
  changes.

Adaptation:

- Mark orchestration/change-of-flow skills user-invoked.
- Keep diagnosis, TDD guidance, review, and state inspection model-reachable.
- Add a user-invoked CodeRail router only after its routing table has
  characterization tests.
- Router recommends one next move and does not execute it.

### B. Absorb after measurement

#### Grilling

Use as an optional front end to `contract-draft` for vague, risky, or
decision-heavy work. Facts are looked up; decisions are asked one at a time.
Do not force it on ordinary `start`.

#### Domain modeling

Adopt:

- Challenge overloaded terms.
- Check claims against code.
- Record only hard-to-reverse, surprising trade-offs as decisions.

Do not make a new glossary a required hot-context file. Put optional domain
assets behind a pointer so the existing 3,000-token governance context contract
does not grow.

#### Tracer-bullet task decomposition

Adopt the vertical-slice and expand-contract rules into task drafting.
Publish to CodeRail queued tasks, not a second local `.scratch` tracker.

This requires a design decision about dependency representation before any
runtime work. It must not be smuggled in as prompt-only text that the kernel
cannot inspect.

#### Codebase design

Adopt deep-module tests such as interface leverage, locality, deletion tests,
and evidence of a real seam. Keep CodeRail terminology authoritative.

### C. Exclude from the first pack

- `setup-matt-pocock-skills`: edits protected agent instructions and creates a
  competing repository configuration.
- `implement`: too thin to add value and directly conflicts on commit ownership.
- `handoff`: competing persistence semantics.
- `resolving-merge-conflicts`: unsafe staging/commit authority.
- `to-spec`: useful only as an optional later adapter, not CodeRail's default.
- `to-tickets`: issue-tracker publishing must be replaced before use.
- `triage`: depends on a tracker/label state machine outside CodeRail's scope.
- `wayfinder`: tracker-centric and overlaps contract/Drive concerns.
- `prototype`: throwaway-branch commits need an ownership model first.
- `research`: useful generic host skill, but not a CodeRail kernel capability.
- `teach` and writing skills: unrelated to CodeRail's product outcome.

## 7. Target Extension Shape

### Skill layer

Use adapted, CodeRail-native names and instructions rather than copying the
entire upstream tree:

```text
skills/
  diagnose/          # model-invoked
  tdd-gate/          # model-invoked, enhanced
  code-review/       # model-invoked
  grill-contract/    # user-invoked
  workflow-router/   # user-invoked, later
```

Each adapted skill must declare:

- invocation policy;
- prerequisites;
- CodeRail task fields it consumes;
- CodeRail evidence it produces;
- allowed side effects;
- explicit prohibition on task-state mutation and direct commit.

### Adapter layer

The adapter is prose plus deterministic data translation, not an autonomous
workflow engine:

```text
reasoning result
  -> proposed G/T/S/V/X/P or review evidence
  -> existing coderail start/check/done interface
  -> existing repository snapshot and transaction
```

No upstream skill may write `.coderail/tasks.json` directly.

### Hook layer

Keep hooks boring:

- `prompt`: remind the agent which invariant applies.
- `pre-edit`: protect governance and detect scope risk.
- `stop`: invoke the existing finish boundary.
- future advisory routing: read explicit task type/metadata and print one
  recommendation; exit zero and mutate nothing.

Hooks must not:

- call an LLM;
- select an issue-tracker workflow from prose;
- create or switch tasks;
- write verification evidence;
- stage or commit;
- turn a recommendation into a hard gate unless the same rule is enforced by
  the deterministic kernel.

## 8. Phased Plan

### Phase 0: freeze-safe research

Scope:

- Keep the upstream clone outside the CodeRail repository.
- Version this report under `docs/research` on the experiment feature branch.
- Make no CodeRail runtime, command, hook, plugin, or lifecycle changes.

Exit:

- Upstream SHA and license are recorded.
- Absorption matrix and conflicts are reviewed.
- Maintainer explicitly decides whether the stabilization freeze is still
  active.

### Phase 1: skill-only experiment

Build an isolated pack under `experiments/workflow-lab` on a feature branch
containing only:

- diagnosing bugs;
- TDD test-quality additions;
- two-axis code review;
- optional grilling for contract drafting.

Run it against disposable repositories or `examples/`, not the CodeRail kernel.
All commits still go through normal CodeRail `done`.

Exit:

- zero direct skill commits;
- zero competing task/state files;
- every bug session records a reproduction command before a fix;
- every review uses a pinned task baseline;
- the pack can be removed without changing CodeRail state.

### Phase 2: comparative evaluation

Use at least 12 representative tasks:

- 3 bugs/regressions;
- 3 ordinary features;
- 2 wide refactors;
- 2 documentation/design tasks;
- 2 multi-session efforts.

Compare baseline CodeRail with CodeRail plus the experimental pack.

Measure:

- first-pass `done` success rate;
- time/turns to a red-capable bug reproduction;
- out-of-scope edit count;
- reopened-task/post-close defect count;
- human decision interruptions;
- review findings that lead to real corrections;
- required governance context tokens;
- task duration and verification runtime.

Guardrails:

- no regression in scope, ownership, commit-pending, or finalization tests;
- required governance context remains at or below 3,000 estimated tokens;
- no new required hot file;
- no new issue tracker, server, account, or network dependency.

### Phase 3: native optional pack

Only after Phase 2 demonstrates benefit:

- add explicit user/model invocation metadata;
- ship adapted skills with attribution;
- add characterization tests for invocation and side-effect contracts;
- document the pack as optional;
- keep `start/check/done` as the complete everyday interface.

Do not add a router yet unless users demonstrably struggle to select the small
pack.

### Phase 4: deterministic router/advisory hook

Only if selection remains a measured problem:

- create a user-invoked router that recommends exactly one next move;
- optionally let `check` or a soft hook print the same recommendation from an
  explicit task type and state;
- keep routing policy as inspectable data with tests;
- never let routing alter state.

Possible deterministic mapping:

| Explicit condition | Recommendation |
|---|---|
| bug with no red-capable command | diagnose |
| correctness-sensitive task with no Red evidence | tdd-gate |
| implementation complete, review absent | two-axis review |
| vague/high-risk request, no accepted contract | grill-contract |
| otherwise | continue current CodeRail task |

## 9. Required Tests Before Shipping

### Invocation

- User-only skills cannot be implicitly invoked on supported hosts.
- Model-invoked descriptions cover distinct trigger branches without
  duplicating the whole workflow.
- The router returns one recommendation and performs no action.

### State and ownership

- Skills cannot create a second active task.
- Skills cannot write task metadata directly.
- Review/diagnosis artifacts outside S are rejected or deliberately added to S.
- Unrelated dirty files remain untouched.

### Verification

- A bug fix cannot be represented as diagnosed without a previously run
  red-capable command.
- Tautological and implementation-coupled example tests are rejected by the
  skill contract.
- Review absence is advisory unless explicitly required by the task contract.

### Closeout

- Adapted `implement` instructions never call Git commit.
- Only `FINALIZED` renders Done.
- Commit failure still enters the existing recoverable pending state.
- Hook and skill failures cannot bypass `done`.

### Context

- Required hot-context file set remains unchanged.
- Skill descriptions stay outside required project reads and are measured
  separately as host context.
- Ten sequential task closes remain byte-stable under the existing observer.

## 10. Stop Conditions

Stop absorption and redesign if any of these occur:

- a second source of task truth appears;
- a skill needs direct commit authority;
- a hook needs an LLM to decide whether the kernel may proceed;
- the three-command everyday interface is no longer complete;
- required governance context exceeds the accepted limit;
- the workflow requires GitHub/Linear/Claude-specific behavior to preserve
  correctness;
- adapted prose cannot be characterized with repeatable scenarios;
- benefit is aesthetic or anecdotal rather than visible in the evaluation
  metrics.

## 11. Recommended Next Decision

Approve only Phase 1 as an isolated, non-shipping feature-branch experiment.
Do not authorize CodeRail runtime integration yet.

The first implementation slice should adapt `diagnosing-bugs` because it has
the strongest fit with the current stabilization policy, the smallest state
surface, and a measurable outcome: a specific command must reproduce the exact
bug before implementation begins.

## 12. Iteration Update: Guided Convergence

Phase 1 produced four validated skills. The experiment was initially kept
outside the repository, then moved to
`experiments/workflow-lab` on `feature/guided-convergence` so its history,
review, and rollback are versioned without weakening the `main` freeze.
Subsequent analysis of `grill-with-docs`, domain modeling, semantic addressing,
and the expert-novice capability gap refined the grilling proposal.

The updated conclusion is:

- retain user-invoked grilling and model-invoked domain framing;
- treat model domain knowledge as a source of candidate lenses, not facts;
- distinguish FACT, ASSUMPTION, DECISION, and UNKNOWN in the live draft;
- show novices outcomes, evidence, uncertainty, and reversibility rather than
  unexplained architecture labels;
- converge on the next bounded, verifiable, reversible slice;
- delay glossary and ADR promotion until evidence and decision-grade criteria
  are satisfied;
- bypass interviewing for clear, local, low-risk work;
- keep routing advisory and outside hooks and the CodeRail kernel.

This adaptation is named **Guided Convergence**. Its rationale and implementation
plan are now the authoritative basis for the next lab iteration:

- `experiments/workflow-lab/docs/GUIDED_CONVERGENCE_RATIONALE.md`
- `experiments/workflow-lab/docs/GUIDED_CONVERGENCE_PLAN.md`

This update supersedes the narrower Phase 1 grilling description in section 6
for future experimentation. It does not authorize native CodeRail integration
or end the stabilization freeze.
