# CodeRail Architecture and Lifecycle Diagrams

Status: current  
Owner: CodeRail  
Updated: 2026-08-08
Task: T-061

These diagrams describe the repository as implemented. They are maintenance
maps, not a proposal for a future architecture. File ownership follows
ADR-011 and ADR-012: hot task ownership, completed history, trace facts,
derived status, and recovery state remain separate.

## 1. System Architecture and Component Boundaries

CodeRail has two runtime boundaries: a small launcher installed in the target
repository and the CodeRail home that contains the Python kernel. All durable
project truth stays in the target repository.

```mermaid
flowchart TB
    User["Human or AI agent"]
    Verify["Registered verification commands<br/>tests, lint, build, manual evidence"]
    Git["Local Git repository<br/>exact task-scoped commits"]

    subgraph Project["Target project repository"]
        Rules["Agent instructions<br/>AGENTS.md / CLAUDE.md"]
        Shim["Repo-local launcher<br/>.coderail/coderail.py"]
        Truth["Repository-tracked project truth<br/>NORTH_STAR / TASKS / PROGRESS / TRACE / DELIVERIES"]
        Supplemental["Supplemental task metadata<br/>.coderail/tasks.json"]
        Recovery["Ignored recovery artifacts<br/>pending_close.json / reports"]
        Projection["Derived views<br/>CODERAIL_STATUS / TRACE_INDEX / TASK_GRAPH"]
    end

    subgraph Home["CodeRail home"]
        Facade["CLI facade<br/>scripts/coderail.py"]
        Lifecycle["Lifecycle services<br/>task_switch / finish_task / closeout_transaction"]
        Gates["Policy and evidence gates<br/>coordinate / TDD / done / doctor / blueprint"]
        State["Repository state model<br/>repository_state / inspect_state"]
        Audience["Audience projections<br/>closeout_facts / owner_receipt"]
        Graph["Evidence graph<br/>trace_graph / task_graph"]
        Distribution["Distribution assets<br/>project-template / skills / references"]
        Installer["Project installer<br/>init_project.py"]
    end

    User --> Rules
    Rules --> Shim
    Shim -->|"resolve CodeRail home and pass --target"| Facade
    Facade --> Lifecycle
    Facade --> Gates
    Facade --> State
    Facade --> Audience
    Facade --> Graph
    Lifecycle --> Truth
    Lifecycle --> Supplemental
    Lifecycle --> Recovery
    State -.-> Truth
    State -.-> Supplemental
    Graph --> Truth
    Graph --> Projection
    Gates -.-> Truth
    Facade --> Verify
    Verify --> Facade
    Facade --> Git
    Git --> Truth
    Git --> Supplemental
    State --> Projection
    Audience --> Truth
    Audience --> Recovery
    Distribution --> Installer
    Installer --> Rules
    Installer --> Shim
    Installer --> Truth
```

### Audience Projection Boundary

```mermaid
flowchart LR
    Contract["Explicit Delivery Contract<br/>product facts"]
    Verify["Observed closeout evidence<br/>verification results"]
    Facts["CloseoutFacts<br/>normalized value"]
    Deliveries["DELIVERIES.jsonl<br/>append-only product evidence"]
    Owner["Owner Receipt<br/>localized, 3-6 sentences"]
    Blackboard["Agent Blackboard<br/>control plane and references"]
    Technical["Technical Report<br/>commands, paths, Git facts"]
    Lifecycle["Lifecycle authority<br/>TASKS / pending / TRACE+PROGRESS / Git"]

    Contract --> Facts
    Verify --> Facts
    Facts --> Deliveries
    Facts --> Owner
    Facts --> Technical
    Deliveries -. latest reference .-> Blackboard
    Lifecycle --> Blackboard
    Lifecycle -. not owned by .-> Facts
```

Owner Receipt is the only default human-facing success surface when a locale is
selected. Blackboard and Technical Report are agent surfaces. DELIVERIES keeps
product/evidence history across TASKS compaction but cannot activate, finalize,
commit, or push work.

Boundary rules:

- The launcher locates CodeRail; it does not own lifecycle behavior.
- `scripts/coderail.py` is the user-facing facade and orchestration entry.
- Specialized modules own repository classification, task switching,
  inspection, graph queries, and the closeout transaction model.
- Verification commands and Git are subprocess boundaries. CodeRail never
  pushes automatically.
- Project truth is plain repository data; ignored recovery artifacts cannot
  become the sole historical authority.

## 2. Task Lifecycle State Machine

The lifecycle is split into two views so the normal path stays readable while
failure and recovery detail remains explicit. `[~]` and `[!]` both count as the
current owner, so `start` cannot create a second active task.

### 2.1 Normal Lifecycle

```mermaid
flowchart TB
    subgraph Intake["Enter ownership"]
        direction LR
        Ready["No active owner"]
        Queued["Queued [ ]"]
        Reopened["Reopened [r]"]
    end

    subgraph Work["Single active ownership"]
        direction LR
        Active["Active [~]"]
        CheckNote["check reads state<br/>and changes no status"]
        SwitchGate["Switch Gate"]
        Paused["Paused [p]"]
        Resumed["Resumed as Active [~]"]
    end

    subgraph Close["Successful closeout"]
        direction LR
        CloseoutGate["Closeout Gate"]
        Completed["Completed history<br/>PROGRESS + verify TRACE"]
        Clear["Task list clear"]
        NextOwner["Destination becomes Active [~]"]
    end

    Ready -->|start| Active
    Ready -->|register| Queued
    Queued -->|next| Active
    Reopened -->|switch| Active

    Active -.-> CheckNote
    Active -->|done| CloseoutGate
    Active -->|switch| SwitchGate
    SwitchGate -->|checkpoint| Paused
    Paused -->|resume| Resumed
    SwitchGate -->|accepted| CloseoutGate

    CloseoutGate -->|finalized| Completed
    Completed -->|clear| Clear
    Completed -->|destination| NextOwner
```

`Resumed` and `NextOwner` are re-entry anchors: each becomes the next
`Active [~]` ownership period. They are drawn as endpoints instead of long
backward arrows so the diagram preserves meaning without routing lines across
the full graph.

Here `checkpoint` includes both an explicit checkpoint and the dirty-fork
pause path. `accepted` means the source task passed switch closeout and joins
the same `Closeout Gate` used by `done`.

### 2.2 Failure and Recovery

```mermaid
flowchart TB
    Owner["Current owner<br/>Active [~] or Blocked [!]"]

    subgraph Gate["Closeout Gate"]
        direction TB
        Verify["Run registered verification"]
        Policy["Coordinate / TDD / Done gates"]
        Classify["Classify final repository snapshot"]
        Commit["Stage exact paths and commit"]
        ResumeCommit["Retry the same exact commit"]
        Rescan["Inspect-equivalent rescan"]
        Finalized["FINALIZED"]
    end

    subgraph Recovery["Failure and recovery exits"]
        direction LR
        Retry["Keeps ownership<br/>fix and rerun done"]
        Blocked["Blocked owner [!]"]
        RepairNote["repair stays inside<br/>the same Coordinate"]
        Pending["Verified commit pending"]
        Resume["done --resume"]
        Drift["Snapshot drift<br/>new verification required"]
    end

    Completed["Completed history"]

    Owner --> Verify
    Verify -->|pass| Policy
    Verify -->|verify failed| Retry
    Policy -->|pass| Classify
    Policy -->|refused| Blocked
    Classify -->|safe| Commit
    Classify -->|unsafe| Blocked

    Commit -->|committed| Rescan
    Commit -->|commit failed| Pending
    Pending -->|resume| Resume
    Pending -->|drift| Drift
    Resume --> ResumeCommit
    ResumeCommit -->|committed| Rescan

    Rescan -->|clean| Finalized
    Rescan -->|inconsistent| Blocked
    Blocked -.-> RepairNote
    Finalized --> Completed
```

Short edge labels carry only the decision. Their full meanings are:

| Label | Meaning |
|---|---|
| `verify failed` | At least one registered command returned non-zero; the task keeps ownership. |
| `refused` | A Coordinate, TDD, Done, or closeout preflight gate rejected the close. |
| `unsafe` | Final classification found an outside, forbidden, sensitive, generated, or ambiguous path. |
| `commit failed` | Verification and ledger preparation are preserved as verified commit-pending. |
| `resume` | `done --resume` retries the unchanged exact snapshot without rerunning verification. |
| `drift` | Verified files or HEAD changed; the snapshot is refused and new verification is required. |
| `inconsistent` | The final rescan found residue or a blocked Inspect projection, so no Done claim is emitted. |

Important invariants:

- Activation is fail-closed when another task owns changes.
- `switch` resolves the source before activating the destination.
- A checkpoint or dirty-fork pauses the source and preserves ownership
  evidence; it does not silently discard work.
- A task is only reported as Done after the exact commit and final consistency
  rescan succeed.
- Completed task bodies may leave hot TASKS only after PROGRESS and verify
  TRACE are durable.

## 3. Done Closeout Sequence

`CloseoutTransaction` is the single success authority. The facade prepares one
source-plus-ledger snapshot, stages only classified safe paths, and emits
success only after the post-commit Inspect-equivalent rescan.

```mermaid
sequenceDiagram
    autonumber
    actor Owner as Human or AI agent
    participant Facade as coderail done + CloseoutTransaction
    participant Verify as Registered verify commands
    participant Recovery as pending_close.json
    participant Gate as finish_task + gates
    participant Ledger as TASKS / PROGRESS / TRACE / STATUS
    participant Repo as repository_state classifier
    participant Git as Local Git
    participant Inspect as Inspect-equivalent rescan

    Owner->>Facade: coderail done
    Facade->>Verify: run every registered command

    alt Any verification command fails
        Verify-->>Facade: non-zero exit and output tail
        Facade-->>Owner: refuse close; task keeps ownership
    else Verification passes
        Verify-->>Facade: exit 0 evidence
        Facade->>Recovery: snapshot task, acceptance, evidence, and next step
        Facade->>Gate: finish task with --no-auto-commit
        Gate->>Gate: Coordinate, TDD, Done, and closeout preflight

        alt Gate or preflight refuses
            Gate-->>Facade: exact blocking reason
            Facade-->>Owner: no success; repair and rerun done
        else Task state closes
            Gate->>Ledger: mark task and append verify lifecycle facts
            Gate-->>Facade: closed-state facts
            Facade->>Ledger: write Done Report and PROGRESS
            Facade->>Ledger: compact durable TASKS and prepare STATUS
            Facade->>Repo: capture and classify final repository snapshot

            alt Outside, forbidden, sensitive, or ambiguous path exists
                Repo-->>Facade: unsafe path list
                Facade->>Ledger: reopen task as blocked
                Facade-->>Owner: refuse commit with exact paths
            else Snapshot is safe
                Repo-->>Facade: exact safe file list
                Facade->>Recovery: persist verified commit-pending snapshot
                Facade->>Git: git add exact paths; commit with task trailers

                alt Stage or commit fails
                    Git-->>Facade: failure
                    Facade-->>Owner: preserve commit-pending; use done --resume
                else Commit succeeds
                    Git-->>Facade: durable commit
                    Facade->>Recovery: clear recovery snapshot
                    Facade->>Inspect: rescan worktree and projected state

                    alt Residue or blocked projection remains
                        Inspect-->>Facade: inconsistent
                        Facade->>Ledger: reopen task as blocked
                        Facade-->>Owner: no Done claim
                    else Clean and consistent
                        Inspect-->>Facade: consistent
                        Facade-->>Owner: FINALIZED; report Done
                    end
                end
            end
        end
    end
```

The recoverable `verified-commit-pending` state preserves successful
verification without pretending that a commit succeeded. `done --resume`
either retries the same exact snapshot or verifies a manually created exact
commit; it does not rerun verification or duplicate ledger history.

## 4. State Authority and Data Flow

The same task appears in several files for different reasons. The arrows below
show which commands write them and which outputs are derived.

```mermaid
flowchart TB
    subgraph Commands["Lifecycle commands"]
        Start["start / next --go"]
        Check["check / Doctor / Blueprint"]
        Switch["switch"]
        Done["done / done --resume"]
        Inspect["inspect"]
        OwnerSummary["owner-summary"]
        Sync["sync-projections<br/>preview / --apply"]
        Queries["why / graph / impact"]
    end

    subgraph Authority["Repository-tracked authority"]
        NorthStar["NORTH_STAR.md<br/>goal and Drive contract"]
        Tasks["TASKS.md<br/>hot ownership and Coordinate"]
        Progress["PROGRESS.md<br/>completed human-readable history"]
        Trace["TRACELOG.jsonl<br/>append-only facts and decisions"]
        Deliveries["DELIVERIES.jsonl<br/>append-only product evidence"]
        Handoff["HANDOFF.md<br/>paused or blocked continuation"]
    end

    subgraph Supplemental["Supplemental and recovery state"]
        Meta[".coderail/tasks.json<br/>verify, acceptance, baseline, relations"]
        Pending["pending_close.json<br/>ignored exact recovery snapshot"]
        Reports[".coderail/reports<br/>ignored detailed Done evidence"]
    end

    subgraph Derived["Derived, rebuildable views"]
        Status["CODERAIL_STATUS.md<br/>Inspect projection"]
        TraceIndex["TRACE_INDEX.md<br/>TRACE index"]
        TaskGraph["TASK_GRAPH.md and graph output<br/>formal relation view"]
    end

    Git["Exact task-scoped Git commit<br/>durability boundary"]

    Start --> Tasks
    Start --> Meta
    Start --> Trace
    Switch --> Tasks
    Switch --> Handoff
    Switch --> Trace

    Check -. reads .-> NorthStar
    Check -. reads .-> Tasks
    Check -. reads .-> Meta
    Check -. reads .-> Trace

    Done --> Pending
    Done --> Reports
    Done --> Tasks
    Done --> Progress
    Done --> Trace
    Done --> Deliveries
    Done --> Meta
    Done --> Status
    Done --> Git
    Git --> Tasks
    Git --> Progress
    Git --> Trace
    Git --> Deliveries
    Git --> Meta
    Git --> Status

    Inspect -. reads .-> NorthStar
    Inspect -. reads .-> Tasks
    Inspect -. reads .-> Meta
    Inspect -. reads .-> Progress
    Inspect -. reads .-> Trace
    Inspect -. latest reference .-> Deliveries
    Inspect -. reads .-> Handoff
    Inspect -. read-only .-> Status
    Sync -. preview reads .-> Handoff
    Sync -. preview reads .-> Status
    Sync -->|"--apply only"| Handoff
    Sync -->|"--apply only"| Status

    Trace --> TraceIndex
    Trace --> TaskGraph
    Meta --> TaskGraph
    Queries -. reads .-> Trace
    Queries -. reads .-> Meta
    Queries --> TaskGraph
    OwnerSummary -. read-only .-> Deliveries
```

Authority table:

| State | Primary purpose | Historical authority? | Main writers |
|---|---|---|---|
| `NORTH_STAR.md` | Outcome, boundaries, Drive contract | current goal | owner and alignment workflow |
| `TASKS.md` | Active, queued, paused, blocked, or reopened ownership | no | start, next, switch, done |
| `PROGRESS.md` | Compact completed-task journal | yes | done, progress repair |
| `TRACELOG.jsonl` | Verify facts, lifecycle facts, explicit decision edges | yes | lifecycle and link commands |
| `DELIVERIES.jsonl` | Explicit product delivery and evidence facts | yes, product only | successful done |
| `HANDOFF.md` | Cross-session continuation projection for non-H0 situations | no | switch, closeout, explicit projection sync |
| `.coderail/tasks.json` | Machine-checkable task contract and recovery detail | supplemental only | lifecycle commands |
| `CODERAIL_STATUS.md` | Point-in-time generated projection | no | done and explicit projection sync; Inspect reads only |
| `TRACE_INDEX.md` | Searchable TRACE projection | no | trace index regeneration |
| `pending_close.json` | Exact interrupted-close recovery | no | done and done --resume |

No derived file may overrule its source authority. No ignored recovery file may
become the only record that a completed task or decision existed.

## 5. Diagnostic Blocking by Stage

Severity describes importance; `blocks` names the lifecycle stage whose action
is refused. The two fields are independent, and formulation stays available
unless a future explicit policy names it.

| Evidence | Category | Severity | Blocks |
|---|---|---|---|
| stale README/HANDOFF/task prose after finalized or pushed | `projection_staleness` | warning | none |
| stale generated snapshot | `projection_staleness` | warning | none |
| multiple active owners or exact live-marker conflict | `control_plane_conflict` | error | activation |
| outside/forbidden task delta or protected baseline conflict | `scope_authorization` | error | execution |
| failed verification or closeout transaction | `closeout_integrity` | error | closeout |
| unsupported safety-relevant product claim | `product_evidence_conflict` | error | delivery |

Historical TRACELOG/PROGRESS wording is excluded before this table is applied.
Recommendation and formulation read the diagnostic report but cannot register,
activate, or execute a Coordinate.
