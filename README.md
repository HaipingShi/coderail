**English** | [中文](#中文)

<div align="center">

# CodeRail

**Keep every AI coding task tied to the project's real outcome — not just the current prompt.**

A lightweight, plugin-style governance kit for AI coding agents. North-Star Kernel · Task Contracts · Harness Gates · Drift Checks · Short Handoffs.

<a href="https://github.com/HaipingShi/coderail/releases/tag/v0.2.0"><img alt="version" src="https://img.shields.io/badge/version-v0.2.0-2EA44F?logo=semver&logoColor=white"></a>
<a href="LICENSE"><img alt="license" src="https://img.shields.io/badge/license-MIT-blue.svg?logo=opensourceinitiative&logoColor=white"></a>
<img alt="python" src="https://img.shields.io/badge/python-3.7%2B-3776AB?logo=python&logoColor=white">
<img alt="tests" src="https://img.shields.io/badge/tests-passing-brightgreen">
<a href="https://github.com/HaipingShi/coderail/releases"><img alt="release" src="https://img.shields.io/badge/release-v0.2.0-6E40C9?logo=github&logoColor=white"></a>

<br>

<img alt="Claude Code" src="https://img.shields.io/badge/Claude_Code-compatible-D97757?logo=anthropic&logoColor=white">
<img alt="Codex" src="https://img.shields.io/badge/Codex-compatible-412991?logo=openai&logoColor=white">
<img alt="Cursor" src="https://img.shields.io/badge/Cursor-compatible-555">
<img alt="No hooks" src="https://img.shields.io/badge/runtime_hooks-off_by_default-888">

</div>

---

> **TL;DR** — CodeRail keeps AI coding agents from drifting. Before coding, the agent checks the task against a persistent *North Star*. Before declaring done, it must pass a harness gate. Before handoff, it writes a snapshot, not a log.

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

## Closed loop with vibecoding-observer

CodeRail and [vibecoding-observer](https://github.com/HaipingShi/vibecoding-observer) are two projects by the same author, started at the same time. They are two faces of one idea rather than two separate products.

- **CodeRail is the preventive side.** The K0–K6 kernel sets constraints *before* work happens — it tries to keep an agent from drifting in the first place.
- **vibecoding-observer is the diagnostic side.** It reads sessions *after* they happen and quantifies the degradation modes that slipped through (28 patterns such as wrong-layer refactors, wasted direction) — it measures drift that already occurred.

One keeps deviation out; the other shines a light on deviation that got in. Together they cover a *prevent → detect → improve* loop, conceptually. But it is worth being precise about what they are **not**:

- There is **no technical integration today.** Each is usable on its own; neither requires the other.
- They are **not positioned as a product suite.** Coupling two tools with their own setup cost would add friction, not reduce it — and friction is precisely what makes governance kits get abandoned. The two stay independent on purpose.
- No roadmap promises future integration.

Each stands alone. They share a philosophy, not a codebase.

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

---

# 中文

[English](#english) | **中文**

<div align="center">

# CodeRail

**让每一个 AI 编码任务都对齐项目的真实目标——而不只是眼前的 prompt。**

一个轻量的、插件式 AI 编码 agent 治理工具包。北极星内核 · 任务契约 · 验证门禁 · 漂移检测 · 短交接。

<a href="https://github.com/HaipingShi/coderail/releases/tag/v0.2.0"><img alt="version" src="https://img.shields.io/badge/version-v0.2.0-2EA44F?logo=semver&logoColor=white"></a>
<a href="LICENSE"><img alt="license" src="https://img.shields.io/badge/license-MIT-blue.svg?logo=opensourceinitiative&logoColor=white"></a>
<img alt="python" src="https://img.shields.io/badge/python-3.7%2B-3776AB?logo=python&logoColor=white">
<img alt="tests" src="https://img.shields.io/badge/tests-passing-brightgreen">
<a href="https://github.com/HaipingShi/coderail/releases"><img alt="release" src="https://img.shields.io/badge/release-v0.2.0-6E40C9?logo=github&logoColor=white"></a>

<br>

<img alt="Claude Code" src="https://img.shields.io/badge/Claude_Code-compatible-D97757?logo=anthropic&logoColor=white">
<img alt="Codex" src="https://img.shields.io/badge/Codex-compatible-412991?logo=openai&logoColor=white">
<img alt="Cursor" src="https://img.shields.io/badge/Cursor-compatible-555">
<img alt="No hooks" src="https://img.shields.io/badge/runtime_hooks-off_by_default-888">

</div>

---

> **一句话** —— CodeRail 防止 AI 编码 agent 漂移。写代码之前,agent 先把任务对齐到一个持久的「北极星」;宣布完成之前,必须通过验证门禁;交接之前,写的是快照,不是流水账。

## 它解决什么问题

AI 编码 agent 在**局部任务**上很高效,在**项目层面**却不可靠。在长会话里它们会漂移:重构错的层、改不该改的文件、没跑测试就声称「完成」、把交接内容写成一面墙的日志、最终忘了项目到底想达成什么。

多数「spec 驱动」工具修的是这件事的**前端**——先写 spec、拆任务、再开工。CodeRail 修的是**中段和尾段**:执行进行中,它把每个任务绑定到一个持久的方向,强制走完验收门禁,并在漂移滚雪球之前检测出来。

> CodeRail 不会替你写 spec,也不取代 CI。它是连接组织——让 agent 的手始终连着项目的脑袋,跨越漫长的多会话工作。

## 适合谁

- **用 AI agent 做真实项目的独立开发者**——不是玩具脚本、不是一次性重构,而是多会话的功能开发,丢线索代价很高。
- **一个人 prompt、其他人(或其他 agent)接力的团队**——交接纪律就是为这种场景设计的。
- **见过 agent「成功」完成了一个已经不服务于目标的任务的人。**

**不适合**:单文件改动、一次性原型、或任何希望 agent 只管生成代码、不要任何流程的人。

## 它给你什么

一个紧凑的**内核**(七条不变量,K0–K6)加上**十个 skill** 和一个**项目模板**(七份活文档)。它们组成一个闭环:

```text
                    ┌─────────────────────────────────────────┐
                    │            docs/NORTH_STAR.md           │   ← 持久方向
                    │   目标 · 当前赌注 · 不变量               │
                    │   当前切片 · 非目标 · 漂移信号           │
                    └────────────────────┬────────────────────┘
                                         │ 每个任务都必须映射到这里
                                         ▼
   /project-init ──► /align ──► /task-contract ──► /execute-batch ──► /done
   (一次)          (意图)      (边界)            (干活)             (门禁)
                                         │                          │
                                         │     /drift-check ◄───────┘ 定期
                                         │     /handoff ◄──── 仅 H1/H2/H3
                                         ▼
                    ┌─────────────────────────────────────────┐
                    │  harness 通过 OR 显式人工验收            │   ← 否则不算完成
                    └─────────────────────────────────────────┘
```

**内核——K0 是承重墙:**

| | 不变量 | 通俗解释 |
|---|---|---|
| **K0** | 北极星 | 每个动作都映射到 目标 / 当前赌注 / 不变量 / 当前切片 |
| **K1** | 任务契约 | 每个任务有 ID、允许/禁止文件、验收标准、harness |
| **K2** | 执行节奏 | 细粒度规划,长批次执行,只在风险边界暂停 |
| **K3** | 验证门禁 | 没有「完成」状态,除非 harness 通过或显式记录人工验收 |
| **K4** | 工具原生 | 尽量用权限/hooks/CI 强制,prompt 规则只是兜底 |
| **K5** | 交接 | 事件触发的快照,绝不是执行日志 |
| **K6** | 资产边界 | 原始素材 ≠ 工作笔记 ≠ 候选件 ≠ 永久资产 ≠ 发布物 |

每条背后的完整论证在 [`references/KERNEL.md`](references/KERNEL.md)。

## 快速开始

CodeRail 提供三种安装方式,按你的 agent 选。

**Claude Code** —— 作为插件目录加载:

```bash
claude --plugin-dir ./coderail
```

然后在任意仓库:

```text
/coderail:project-init
```

**Codex** —— 放到 `plugins/coderail` 下,注册一个仓库级 marketplace(见 [`examples/codex/marketplace.example.json`](examples/codex/marketplace.example.json))。

**任何其它 agent**(Cursor、Gemini CLI、Aider 等)—— 拷模板进去,不需要插件支持:

```bash
python3 coderail/scripts/init_project.py --target /path/to/your/repo --mode standard
```

然后让你的 agent 读 `AGENTS.md`。这是每个 skill 都会读取的运行时入口文件。

**验证安装:**

```bash
python3 coderail/scripts/doctor.py --target /path/to/your/repo
# Status: healthy
```

### 一次正常的工作会话

```text
/coderail:align          # 用于模糊或高层请求——先别写代码
/coderail:task-contract  # 约束任务:允许文件、验收标准、harness
/coderail:execute-batch  # 干这个任务;只在风险边界暂停
/coderail:done           # 门禁:harness 必须通过或记录人工验收
```

只有当交接触发器命中(H1/H2/H3)才用 `/coderail:handoff`;定期或在 PR 前用 `/coderail:drift-check`。

### 用一句话让你的 agent 装好(无需插件支持)

如果你的 agent 有 shell 权限但没有插件市场,把下面这段 prompt 贴进一个全新会话。它会把 CodeRail 引导进当前仓库并跑健康检查。适用于 Cursor、Gemini CLI、Aider 等任何能跑 shell 命令的 agent。

```text
把 CodeRail 治理工具包安装进当前仓库,然后初始化它。

1. 如果 coderail 还没在磁盘上,克隆它:
   git clone https://github.com/HaipingShi/coderail.git /tmp/coderail

2. 把项目模板拷进当前仓库(不要覆盖已有文件):
   python3 /tmp/coderail/scripts/init_project.py --target . --mode standard

3. 用本项目的 目标、当前赌注、不变量、非目标、当前切片 填好 docs/NORTH_STAR.md。
   控制在 100 行以内。任何字段不确定就标注出来问我。

4. 跑健康检查并报告结果:
   python3 /tmp/coderail/scripts/doctor.py --target .

从现在起,遵循本仓库的 AGENTS.md:写代码前输出 North-Star Check,
实现前写任务契约,harness 没通过或没记录人工验收前不要标记完成。
```

每一步在做什么:

1. **克隆** —— 把工具包拿到 `/tmp/coderail`(按你的系统调整路径)。
2. **安装** —— `init_project.py` 把 `AGENTS.md`、`CLAUDE.md` 和 `docs/` 集合拷进你的仓库。它拒绝覆盖非空文件,所以已有文档是安全的。
3. **撰写** —— agent 根据你的项目上下文起草 `NORTH_STAR.md`,不清楚的地方问你。这是之后每个 skill 都要读的文件。
4. **验证** —— `doctor.py` 在任何编码开始前确认安装健康。

之后你的仓库就自给自足了:它带着 `AGENTS.md` 作为运行时入口,所以哪怕没加载插件,后续会话也保持被治理状态——agent 读 `AGENTS.md` 并照做即可。

## 与同类工作的差异

CodeRail **不是**一个竞争方法论——它和大多数工具处在不同层。诚实的定位:

### vs. Superpowers([obra/superpowers](https://github.com/obra/superpowers))

Superpowers 是一个**方法论 skill 库**:它教 agent *怎么把代码写好*——TDD、头脑风暴、分阶段调试、系统性验证。它讲的是**手艺**。

CodeRail 是一个**治理层**:它让 agent 的手艺始终对准正确的目标,让项目方向活过单个会话。它讲的是**对齐和连续性**。

两者是互补的。Superpowers 回答「你建得对吗?」;CodeRail 回答「你建的是对的东西吗?别人能接得上吗?」完全可以两个都用——Superpowers 管执行技巧,CodeRail 管北极星 / 交接 / 漂移这条主心骨。

### vs. Spec 驱动工具([github/spec-kit](https://github.com/github/spec-kit)、Kiro、OpenSpec)

这些工具和 CodeRail 有同一个前提:**编码前先把意图前置。** spec-kit 的 `spec → plan → tasks` 流程和 Kiro 的 `requirements → design → tasks` 流程都产出约束 agent 的文档。

**重叠之处**:都写 spec/北极星,都拆任务,都要你实现前先规划。如果你已经在用 spec-kit,你的 `spec.md` 和 CodeRail 的 `NORTH_STAR.md` 是同义的。

**差异之处**:

| 关注点 | spec-kit / Kiro | CodeRail |
|---|---|---|
| 重点 | **前端**:写 spec、拆任务 | **中后段**:执行中把任务绑到 spec |
| 漂移检测 | 不内置 | `/drift-check` 标出偏离 spec 的任务/代码 |
| 交接纪律 | 不是重点 | H0–H3 等级、篇幅预算、把日志导流出上下文 |
| 完成门禁 | 依赖现有 CI | 显式的 `/done` 门禁,harness 或验收规则 |
| 多会话连续性 | 隐式 | 一等公民(交接 + RUNLOG + 恢复 prompt) |
| 重量 | 文档集更重 | 一份持久文件(`NORTH_STAR.md`),其余可选 |

如果说 spec-kit 是你的**规划阶段**,CodeRail 就是你的**执行和连续性阶段**。

### vs. BMAD([bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD))

BMAD 是**多 agent 角色编排**——分析师、产品经理、架构师、Scrum Master 等 agent 通过 story 文件协作。它是一个**盒子里的小团队**。

CodeRail **没有角色人设,没有编排器**。它是一种单人(或单人+agent)的纪律,一个贡献者就能独立跑。如果 BMAD 是一张组织架构图,CodeRail 就是这张组织架构图要遵守的清单。

## 与 vibecoding-observer 的闭环

CodeRail 和 [vibecoding-observer](https://github.com/HaipingShi/vibecoding-observer) 是同一个作者、同一时间起步的两个项目。它们更像是一个想法的两张面孔,而不是两个独立产品。

- **CodeRail 是预防侧。** K0–K6 内核在工作发生*之前*设定约束——它试图从一开始就不让 agent 漂移。
- **vibecoding-observer 是诊断侧。** 它在会话发生*之后*读取会话,量化溜进来的退化模式(28 种,比如错层重构、浪费方向)——它测量已经发生的漂移。

一个把偏差挡在门外,一个把已经溜进来的偏差照出来。概念上,两者合起来覆盖一个「预防 → 检测 → 改进」闭环。但有几件事必须说清楚:

- **今天两者没有任何技术集成。** 各自独立可用,谁也不依赖谁。
- **不构成「产品套件」。** 把两个各有安装成本的工具耦合起来,只会增加摩擦,而非减少——而摩擦恰恰是治理工具包被弃用的原因。两者刻意保持独立。
- 没有任何路线图承诺未来联动。

各自独立。它们共享的是哲学,不是代码库。

## 十个 skill

每个都是 [`skills/`](skills/) 下独立的 `SKILL.md`,在 Claude Code 里以 `/coderail:<name>` 调用(其它 agent 按名字调用)。

| Skill | 何时用 | 产出什么 |
|---|---|---|
| [`project-init`](skills/project-init/SKILL.md) | 每个仓库一次 | `AGENTS.md`、`CLAUDE.md`、`docs/` 集合 |
| [`align`](skills/align/SKILL.md) | 模糊/高层请求,写代码前 | North-Star Check + 任务契约候选 |
| [`task-contract`](skills/task-contract/SKILL.md) | 实现前 | `TASKS.md` 里一个有边界的 T-XXX |
| [`execute-batch`](skills/execute-batch/SKILL.md) | 工作已授权 | 连续执行,只在风险边界暂停 |
| [`done`](skills/done/SKILL.md) | 工作认为完成时 | 完成报告;以 harness 为门禁 |
| [`handoff`](skills/handoff/SKILL.md) | H1/H2/H3 触发器命中 | 短快照,不是日志 |
| [`drift-check`](skills/drift-check/SKILL.md) | 定期 / PR 前 / 起疑时 | aligned / minor drift / major drift |
| [`harness-repair`](skills/harness-repair/SKILL.md) | harness 失败 | 分类过的根因 + 修复 |
| [`asset-boundary`](skills/asset-boundary/SKILL.md) | 出现素材/导出件时 | A0–A5 分类 + 提升规则 |
| [`doctor`](skills/doctor/SKILL.md) | 体检 | 健康 / 有警告 / 不健康 |

## 边界(它不是什么)

CodeRail 刻意保持小巧。它**不**:

- 取代 CI、代码审查、安全扫描或 issue 跟踪系统。
- 替你写 spec——`NORTH_STAR.md` 你自己写,CodeRail 让工作始终连着它。
- 默认跑 hooks。只提供示例。你在审查后自行启用工具原生强制([`examples/hooks.example.json`](examples/hooks.example.json))。
- 编排多个 agent 或强加角色人设。

它只约束 AI 编码的执行,让局部实现始终连着项目目标和验证路径。四档采纳层级(Lite → Standard → Team → Enterprise)让你恰好拿够这个项目需要的流程量——见 [`references/MODES.md`](references/MODES.md)。

## 项目结构

```text
coderail/
├── .claude-plugin/        # Claude Code 清单
├── .codex-plugin/         # Codex 清单
├── skills/                # 10 个独立 SKILL.md 文件
├── project-template/      # AGENTS.md、CLAUDE.md、docs/*.md —— init_project.py 拷贝的模板
├── references/            # KERNEL、MODES、VALIDATION_HIERARCHY 等(背后的论证)
├── scripts/               # init_project.py、doctor.py、drift_check.py
├── examples/              # hooks + 权限示例(默认不启用)
└── tests/                 # 结构自测
```

## 许可证

MIT —— 见 [LICENSE](LICENSE)。
