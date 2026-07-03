<div align="center">

# CodeRail

**Keep every AI coding task tied to the project's real outcome — not just the current prompt.**

A lightweight, plugin-style governance kit for AI coding agents. North-Star Kernel · Task Contracts · Harness Gates · Drift Checks · Short Handoffs.

`v0.2.0` · MIT · No runtime hooks by default

</div>

---

## The problem it solves

AI coding agents are productive at the *local* task and unreliable at the *project* level. Within a long session they drift: they refactor the wrong layer, edit files they shouldn't, declare work "done" without tests, hand off context as a wall of logs, and lose the thread of what the project was actually trying to achieve.

Most "spec-driven" tools fix the **front** of this — write a spec, plan tasks, then go. CodeRail fixes the **middle and tail**: while execution is happening, it keeps each task bound to a persistent direction, enforces a completion gate, and detects drift before it compounds.

> CodeRail does not write your spec for you, and it does not replace CI. It is the connective tissue that keeps an agent's hands attached to the project's head across long, multi-session work.

## Who it's for

- **Solo developers using AI agents for real projects** — not toy scripts, not one-shot refactors, but multi-session feature work where losing the thread is expensive.
- **Small teams where one human prompts and others (or other agents) continue the work** — the handoff discipline is built for this.
- **Anyone who has watched an agent "successfully" finish a task that no longer served the goal.**

It is **not** for: single-file edits, throwaway prototypes, or anyone who wants the agent to just generate code without any process overhead.

## What it gives you

A compact **kernel** (seven invariants, K0–K6) plus **ten skills** and a **project template** of seven living documents. Together they form one loop:

```text
                    ┌─────────────────────────────────────────┐
                    │            docs/NORTH_STAR.md           │   ← persistent direction
                    │   Outcome · Current Bet · Invariants    │
                    │   Current Slice · Non-Goals · Drift     │
                    └────────────────────┬────────────────────┘
                                         │ every task must map here
                                         ▼
   /project-init ──► /align ──► /task-contract ──► /execute-batch ──► /done
   (once)          (intent)    (boundary)         (work)            (gate)
                                         │                          │
                                         │     /drift-check ◄───────┘ periodic
                                         │     /handoff ◄──── H1/H2/H3 only
                                         ▼
                    ┌─────────────────────────────────────────┐
                    │  harness passes OR manual acceptance     │   ← no done without it
                    └─────────────────────────────────────────┘
```

**The kernel — K0 is the load-bearing wall:**

| | Invariant | Plain meaning |
|---|---|---|
| **K0** | North-Star | Every action maps to Outcome / Current Bet / Invariants / Current Slice |
| **K1** | Task Contract | Each task has ID, allowed/forbidden files, acceptance, harness |
| **K2** | Execution Rhythm | Plan fine, execute in long batches, pause only at risk boundaries |
| **K3** | Harness Gate | No "done" without a passing harness or explicit manual acceptance |
| **K4** | Tool-Native | Enforce via permissions/hooks/CI where possible; prompts are fallback |
| **K5** | Handoff | Event-triggered snapshot, never an execution log |
| **K6** | Asset Boundary | Raw material ≠ working note ≠ candidate ≠ permanent asset ≠ release |

The full reasoning behind each is in [`references/KERNEL.md`](references/KERNEL.md).

## Quick start

CodeRail ships three install paths. Pick the one matching your agent.

**Claude Code** — load as a plugin directory:

```bash
claude --plugin-dir ./coderail
```

Then in any repo:

```text
/coderail:project-init
```

**Codex** — place under `plugins/coderail` and register a repo marketplace (see [`examples/codex/marketplace.example.json`](examples/codex/marketplace.example.json)).

**Any other agent** (Cursor, Gemini CLI, Aider, etc.) — copy the template in. No plugin support needed:

```bash
python3 coderail/scripts/init_project.py --target /path/to/your/repo --mode standard
```

Then point your agent at `AGENTS.md`. That file is the runtime entry point every skill reads from.

**Verify the install:**

```bash
python3 coderail/scripts/doctor.py --target /path/to/your/repo
# Status: healthy
```

### A normal working session

```text
/coderail:align          # for vague or high-level requests — don't code yet
/coderail:task-contract  # bound the task: allowed files, acceptance, harness
/coderail:execute-batch  # work the task; pause only at risk boundaries
/coderail:done           # gate: harness must pass or manual acceptance recorded
```

Reach for `/coderail:handoff` only when a handoff trigger fires (H1/H2/H3), and `/coderail:drift-check` periodically or before a PR.

### Install by telling your agent (no plugin support required)

If your agent has shell access but no plugin marketplace, paste this prompt into a fresh session. It bootstraps CodeRail into the current repo and runs the health check. Works with Cursor, Gemini CLI, Aider, or any agent that can run shell commands.

```text
Install the CodeRail governance kit into this repository, then initialize it.

1. If coderail is not yet on disk, clone it:
   git clone https://github.com/HaipingShi/coderail.git /tmp/coderail

2. Copy the project template into the current repo (do not overwrite existing files):
   python3 /tmp/coderail/scripts/init_project.py --target . --mode standard

3. Fill docs/NORTH_STAR.md with this project's Outcome, Current Bet,
   Invariants, Non-Goals, and Current Slice. Keep it under 100 lines.
   If any field is unknown, mark it and ask me.

4. Run the health check and report the result:
   python3 /tmp/coderail/scripts/doctor.py --target .

From now on, follow AGENTS.md in this repo: output a North-Star Check
before coding, write a task contract before implementation, and do not
mark work done until the harness passes or manual acceptance is recorded.
```

What this does, step by step:

1. **Clone** — gets the kit to `/tmp/coderail` (adjust the path for your OS).
2. **Install** — `init_project.py` copies `AGENTS.md`, `CLAUDE.md`, and the `docs/` set into your repo. It refuses to overwrite non-empty files, so existing docs are safe.
3. **Author** — the agent drafts `NORTH_STAR.md` from your project context and asks you about anything unclear. This is the file every later skill reads from.
4. **Verify** — `doctor.py` confirms the install is healthy before any coding starts.

After this, your repo is self-sufficient: it carries `AGENTS.md` as the runtime entry point, so future sessions stay governed even without the plugin loaded — the agent just reads `AGENTS.md` and follows it.

## How it differs from related work

CodeRail is **not** a competing methodology — it operates at a different layer than most. The honest positioning:

### vs. Superpowers ([obra/superpowers](https://github.com/obra/superpowers))

Superpowers is a **methodology skills library**: it teaches the agent *how to code well* — TDD, brainstorming, phased debugging, systematic verification. It is about **craft**.

CodeRail is a **governance layer**: it keeps the agent's craft pointed at the right target, and makes the project's direction outlive any single session. It is about **alignment and continuity**.

They are complementary. Superpowers answers *"are you building it right?"*; CodeRail answers *"are you building the right thing, and can someone pick up where you left off?"* Nothing prevents using both — Superpowers for execution technique, CodeRail for the North-Star / handoff / drift spine.

### vs. Spec-driven tools ([github/spec-kit](https://github.com/github/spec-kit), Kiro, OpenSpec)

These share CodeRail's premise: **front-load intent before coding.** spec-kit's `spec → plan → tasks` flow and Kiro's `requirements → design → tasks` flow both produce documents that constrain the agent.

**Where they overlap:** both write a spec/North-Star, both decompose into tasks, both want you to plan before implementing. If you already use spec-kit, your `spec.md` and CodeRail's `NORTH_STAR.md` serve the same purpose.

**Where CodeRail differs:**

| Concern | spec-kit / Kiro | CodeRail |
|---|---|---|
| Focus | **Front**: author the spec, plan tasks | **Middle + tail**: bind tasks to the spec *during* execution |
| Drift detection | Not built-in | `/drift-check` flags tasks/code that diverged from the spec |
| Handoff discipline | Not the focus | H0–H3 levels, size budgets, redirects logs out of context |
| Completion gate | Relies on existing CI | Explicit `/done` gate, harness-or-acceptance rule |
| Multi-session continuity | Implicit | First-class (handoff + RUNLOG + resume prompts) |
| Weight | Heavier document set | One persistent file (`NORTH_STAR.md`), the rest are optional |

If spec-kit is your **planning phase**, CodeRail is your **execution and continuity phase**.

### vs. BMAD ([bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD))

BMAD is **multi-agent role orchestration** — an Analyst, Product Manager, Architect, and Scrum Master agent collaborate through story files. It is a **team in a box**.

CodeRail has **no role personas and no orchestrator**. It is a single-agent (or single-human-plus-agent) discipline that one contributor can run solo. If BMAD is an org chart, CodeRail is a checklist the org chart follows.

## The ten skills

Each is a self-contained `SKILL.md` under [`skills/`](skills/), invoked as `/coderail:<name>` in Claude Code (or by name in any agent).

| Skill | When | What it produces |
|---|---|---|
| [`project-init`](skills/project-init/SKILL.md) | Once per repo | `AGENTS.md`, `CLAUDE.md`, the `docs/` set |
| [`align`](skills/align/SKILL.md) | Vague/high-level request, before coding | North-Star Check + task-contract candidate |
| [`task-contract`](skills/task-contract/SKILL.md) | Before implementation | A bounded T-XXX in `TASKS.md` |
| [`execute-batch`](skills/execute-batch/SKILL.md) | Work is authorized | Continuous execution, pauses only at risk boundaries |
| [`done`](skills/done/SKILL.md) | Work believed finished | Completion report; gates on harness |
| [`handoff`](skills/handoff/SKILL.md) | H1/H2/H3 trigger fires | Short snapshot, not a log |
| [`drift-check`](skills/drift-check/SKILL.md) | Periodic / pre-PR / suspicion | aligned / minor drift / major drift |
| [`harness-repair`](skills/harness-repair/SKILL.md) | Harness fails | Classified root cause + fix |
| [`asset-boundary`](skills/asset-boundary/SKILL.md) | Materials/exports appear | A0–A5 classification + promotion rule |
| [`doctor`](skills/doctor/SKILL.md) | Health check | Healthy / warnings / unhealthy |

## Boundary (what this is not)

CodeRail deliberately stays small. It does **not**:

- Replace CI, code review, security scanning, or issue trackers.
- Author your spec — you write `NORTH_STAR.md`; CodeRail keeps work attached to it.
- Run hooks by default. Examples only. You enable tool-native enforcement ([`examples/hooks.example.json`](examples/hooks.example.json)) after review.
- Orchestrate multiple agents or impose role personas.

It only constrains AI coding execution so that local implementation stays connected to the project outcome and its verification path. The four adoption tiers (Lite → Standard → Team → Enterprise) let you take exactly as much process as the project needs — see [`references/MODES.md`](references/MODES.md).

## Project layout

```text
coderail/
├── .claude-plugin/        # Claude Code manifest
├── .codex-plugin/         # Codex manifest
├── skills/                # 10 self-contained SKILL.md files
├── project-template/      # AGENTS.md, CLAUDE.md, docs/*.md — what init_project.py copies
├── references/            # KERNEL, MODES, VALIDATION_HIERARCHY, etc. (the reasoning)
├── scripts/               # init_project.py, doctor.py, drift_check.py
├── examples/              # hooks + permission examples (NOT enabled by default)
└── tests/                 # structure self-tests
```

## License

MIT — see [LICENSE](LICENSE).
