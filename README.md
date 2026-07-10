# CodeRail

![version](https://img.shields.io/badge/version-v0.7.3-2f80ed)
![license](https://img.shields.io/badge/license-MIT-27ae60)
![python](https://img.shields.io/badge/python-3.x-ffd43b)
![agent](https://img.shields.io/badge/agent--ready-Codex%20%7C%20Claude-8e44ad)
![scope](https://img.shields.io/badge/scope-repo--local-16a085)

🛤️ **Draft before coding. Verify before done. Close out before stopping.**
🛤️ **先对齐再编码，先验证再完成，停止前先收口。**

CodeRail is a lightweight governance rail for AI coding agents. It keeps long-running coding work aligned through a small repo-local kernel: North Star, Architecture Blueprint Layer, Full Rail / Light Rail task governance, CodeRail Coordinate, Coordinate Contract Drafts, TDD Gate, task contracts, verification-before-complete, deterministic Drive Decisions, automatic task-scoped commits, CI Gate, runtime state inspect, short handoffs, asset boundaries, and trace links.

CodeRail 是一个面向 AI 编码 Agent 的轻量级治理轨道。它不是任务系统或重型工作流引擎，而是在你的仓库里放入一套小而稳定的执行内核：North Star、Architecture Blueprint Layer、Full Rail / Light Rail 分层、CodeRail Coordinate、契约草案、TDD Gate、任务契约、完成前验证、确定性 Drive Decision、自动任务级提交、CI Gate、运行态检查、交接摘要、资产边界和可追踪链接。

Version: **v0.7.3**

## ✨ What It Does / 它解决什么

| Icon | English | 中文 |
|---|---|---|
| 🎯 | Keeps every coding action tied to a North Star outcome. | 让每个编码动作都能回到明确的目标。 |
| 🧭 | Compresses work into G/T/S/V/X/P before implementation. | 开始实现前，把任务压缩成 G/T/S/V/X/P。 |
| 🧾 | Drafts a contract for vague, risky, or cross-module requests. | 对模糊、高风险、跨模块需求先生成契约草案。 |
| 🔴 | Adds Red-Green-Refactor evidence for correctness-sensitive work. | 对正确性敏感任务加入红绿重构证据。 |
| ✅ | Blocks "done" until verification, scope, persistence, and trace are present. | 没有验证、范围约束、持久化和 trace，不允许标记完成。 |
| 🧹 | Auto-commits safe task-scoped work and leaves one executable next step before stopping. | 停止前自动提交安全的任务级变更，并留下一个可执行下一步。 |
| 🧱 | Runs CI Gate so non-decision checks do not become user interruptions. | 运行 CI Gate，让非决策性检查不再打断用户。 |
| 🚗 | Computes a Drive Decision so continuous goals keep moving until review or terminal states. | 计算 Drive Decision，让持续目标推进到复盘或终态，而不是在非决策步骤停下。 |
| 🔍 | Produces a compact repo-local state surface for resume/debug/handoff. | 生成可检查的仓库状态，方便恢复、调试和交接。 |
| 🔗 | Records trace events so decisions, changes, and validation stay connected. | 记录 trace 事件，让决策、修改和验证保持连接。 |
| 🏗️ | Checks blueprint coverage for architecture, data, deployment, UI flow, and lifecycle complexity. | 检测架构、数据、部署、用户流和生命周期复杂度是否有必要图纸覆盖。 |
| 🪝 | Provides example hooks for prompt reminders, protected governance edits, and periodic health checks. | 提供 hooks 示例，用于提示、保护治理文件、阶段性健康检查。 |

## 🚦 Rail Levels / 治理分层

CodeRail uses two rail levels so productive research projects do not pay the same governance cost for every kind of thinking.

CodeRail 使用两档治理，避免研究型项目把所有思考都压成同等强度的工程闭环。

| Rail | Use for | Required evidence |
|---|---|---|
| **Full Rail** | Code, schema, dependencies, data writes, runners, pipelines, external interfaces, migrations, releases. | Full G/T/S/V/X/P, executable verification or explicit manual acceptance, TASKS + TRACE, Done Gate, Closeout. |
| **Light Rail** | Theory, product positioning, design principles, philosophy boundaries, terminology, ADRs, document drafts. | Goal, boundary, persistence location, next step, and trace/decision backlink or explicit manual acceptance. |

Every current task should declare `Rail: full` or `Rail: light` explicitly. The scripts can still infer a rail for diagnostics, but current task contracts and done checks should not depend on inference; use `--rail-type` only as a deliberate CLI override.

Light Rail lowers process weight, not integrity. It still forbids fake verification, hidden failures, out-of-scope edits, and chat-memory-only state.

每个当前任务都应该显式声明 `Rail: full` 或 `Rail: light`。脚本仍可为了诊断做推断，但当前任务契约和 done check 不应依赖推断；`--rail-type` 只作为明确的 CLI 覆盖。

Light Rail 降低的是流程重量，不是诚信要求：仍然禁止伪验证、隐藏失败、越界修改和用聊天记忆替代项目状态。

## 🧑‍💻 For Users / 面向用户

Use CodeRail when you want your AI coding assistant to stop drifting, stop declaring victory too early, and leave behind a useful state that another session can pick up.

当你希望 AI 编码助手减少跑偏、不要过早宣布完成、并且能留下可恢复的项目状态时，使用 CodeRail。

Good fit / 适合场景：

- 🚀 Long-running feature work with multiple files or phases.
- 🧩 Cross-module refactors where scope creep is easy.
- 🧪 Work that must prove tests, build, lint, or manual acceptance.
- 🔴 Bug fixes, regressions, parsers, APIs, domain logic, and shared utilities that benefit from TDD.
- 🤝 Human-to-agent or agent-to-agent handoff.
- 🧹 Dirty worktrees where safe task-scoped work should be committed automatically.
- 🧱 Repos that need CI/CD checks folded into the agent loop.
- 🗂️ Repos that need lightweight governance without adopting a full workflow platform.
- 🚀 多阶段、多文件的功能开发。
- 🧩 容易范围蔓延的跨模块重构。
- 🧪 需要证明测试、构建、lint 或人工验收的任务。
- 🔴 适合 TDD 的 bug、回归、parser、API、领域逻辑和共享工具。
- 🤝 人与 Agent、Agent 与 Agent 之间的交接。
- 🧹 需要自动提交安全任务级变更、避免 `git add .` 误伤的脏工作区。
- 🧱 需要把 CI/CD 检查纳入 Agent 执行闭环的仓库。
- 🗂️ 想要轻量治理但不想引入完整工作流平台的仓库。

## 🤖 For Agents / 面向 Agent

CodeRail gives the agent a local operating contract:

CodeRail 给 Agent 一个本地执行契约：

| Field | Agent meaning | Agent 应该怎么做 |
|---|---|---|
| 🎯 G — Goal | Name the North Star outcome served by this action. | 说明当前动作服务哪个 North Star 结果。 |
| 🧰 T — Task | State the exact task to complete now. | 明确当前要完成的具体任务。 |
| 🚧 S — Scope | Declare allowed and forbidden files/assets. | 声明允许和禁止触碰的文件或资产。 |
| 🧪 V — Verify | Define executable verification or explicit manual acceptance. | 定义可执行验证，或明确人工验收。 |
| 🛑 X — Stop | List stop/escalation conditions. | 写清需要停止或升级的条件。 |
| 📌 P — Persist | Name the project files that must be updated. | 写明必须同步的项目记录文件。 |

For correctness-sensitive work, `V — Verify` should include TDD mode and Red-Green-Refactor evidence.

对正确性敏感任务，`V — Verify` 应包含 TDD 模式和红绿重构证据。

Agent rule of thumb / Agent 执行口诀：

```text
Align G/T/S/V/X/P.
Work only inside S.
Stop when X fires.
Do not mark done until V passes and P is synced.
Leave trace evidence.
Use TDD Gate when required.
Auto-commit safe task-scoped work before stopping.
```

```text
先对齐 G/T/S/V/X/P。
只在 S 范围内工作。
触发 X 就停。
V 未通过、P 未同步，不要标记完成。
留下 trace 证据。
需要时使用 TDD Gate。
停止前自动提交安全的任务级变更。
```

## 🧠 Best Practice: CodeRail + Docs + Skills / 最佳实践：CodeRail + 文档 + 技能

CodeRail does **not** replace document-driven development. It should make document-driven development harder to skip.

CodeRail **不是**用来替代文档驱动开发的。它应该让 Agent 更难跳过文档、图纸、验证和交接。

Use this split:

使用下面的分工：

| Layer | Responsibility | Examples |
|---|---|---|
| 🛤️ CodeRail | Project governance: why, scope, TDD evidence, verification, persistence, trace, auto-commit, closeout, handoff. | `NORTH_STAR.md`, `TASKS.md`, `BLUEPRINTS.md`, TDD gate, done gate, auto-commit, CI gate, trace |
| 📚 Project docs | Long-lived facts and engineering memory. | PRD, ADR, API contract, ERD, deployment notes |
| 🧠 Superpowers-style skills | Execution craft for a specific task. | TDD, debugging, refactoring, API design, UI implementation |
| 🪝 Hooks / CI | Automatic correction and periodic checks. | `doctor.py`, `blueprint_check.py`, tests, lint, branch protection |

Rule of thumb:

```text
CodeRail decides why/what/boundary/evidence.
Skills decide how to execute well.
Docs record the durable truth.
Hooks catch drift when nobody remembers to ask.
```

执行口诀：

```text
CodeRail 决定为什么做、做什么、边界在哪、证据是什么。
技能负责把这一段高质量完成。
文档记录长期事实。
hooks 在没人主动询问时纠偏。
```

When using Superpowers or any other implementation skill, keep CodeRail as the outer contract:

当使用 Superpowers 或其它实现型 skill 时，把 CodeRail 放在外层作为契约：

```text
Use CodeRail as the project governance layer and use the selected skill as the implementation method.

First read AGENTS.md, docs/NORTH_STAR.md, docs/TASKS.md, docs/BLUEPRINTS.md, and docs/HARNESS_SPEC.md.
Create or confirm a CodeRail Coordinate: G/T/S/V/X/P.
For correctness-sensitive work, set TDD mode and record Red-Green-Refactor evidence.
If this is architecture, API, data, deployment, UI flow, or lifecycle work, run blueprint_check.py and update docs/BLUEPRINTS.md first.

Then use the relevant skill for implementation quality, but do not expand scope beyond S.
Before done, run V, done_gate.py, trace_event.py, trace_index.py, and inspect_state.py. Before stopping, run closeout_check.py with auto-commit when safe.
```

```text
请把 CodeRail 作为项目治理层，把选定 skill 作为具体实现方法。

先读取 AGENTS.md、docs/NORTH_STAR.md、docs/TASKS.md、docs/BLUEPRINTS.md、docs/HARNESS_SPEC.md。
先确认 CodeRail Coordinate：G/T/S/V/X/P。
对正确性敏感任务，设置 TDD 模式并记录红绿重构证据。
如果任务涉及架构、接口、数据、部署、用户流或生命周期，先运行 blueprint_check.py，并更新 docs/BLUEPRINTS.md。

然后使用合适的 skill 提升实现质量，但不能超出 S 范围。
完成前必须运行 V、done_gate.py、trace_event.py、trace_index.py、inspect_state.py。停止前在安全时运行 closeout_check.py 自动提交。
```

## 🌏 5W2H

| Question | English | 中文 |
|---|---|---|
| 🧑 Who | AI coding agents, agent operators, maintainers, and teams that hand work between sessions. | AI 编码 Agent、Agent 使用者、维护者，以及需要跨会话交接的团队。 |
| ❓ What | A repo-local governance rail made of templates, skills, validators, done gate, auto-commit gate, CI gate, inspect state, and trace logs. | 一套仓库本地治理轨道：模板、技能、校验器、完成门禁、自动提交门禁、CI 门禁、状态检查和 trace 日志。 |
| 🕰️ When | Before coding starts, before marking done, before stopping, when resuming, when drift appears, and before handoff. | 编码前、标记完成前、停止前、恢复会话时、发现跑偏时、交接前。 |
| 📍 Where | Inside the target repository, mostly under `docs/`, plus `AGENTS.md` and optional plugin manifests. | 在目标仓库内部，主要位于 `docs/`，并包含 `AGENTS.md` 和可选插件 manifest。 |
| 💡 Why | Agents need small, explicit rails: intent, scope, verification, persistence, and traceability. | Agent 需要小而明确的轨道：意图、范围、验证、持久化和可追踪性。 |
| 🛠️ How | Initialize templates, draft/accept a coordinate, execute inside scope, run CI/done gates, record trace, inspect state, and auto-commit safe task-scoped work. | 初始化模板，起草并接受 coordinate，在范围内执行，运行 CI/done gate，记录 trace，检查状态，并自动提交安全任务级变更。 |
| 📏 How much | Lightweight: no server, no database, no runtime loop. Standard-library Python scripts and Markdown files. | 很轻：不需要服务端、数据库或循环运行时。主要是标准库 Python 脚本和 Markdown 文件。 |

## 🆕 What v0.7 Adds / v0.7 新增

v0.7 adds an Architecture Blueprint Layer without turning CodeRail into a heavyweight architecture platform:

v0.7 增加 Architecture Blueprint Layer，但不把 CodeRail 变成重型架构平台：

1. 🏗️ **Blueprint Gate / 架构图纸门禁**
   `scripts/blueprint_check.py` detects frontend, backend, data, ops, CI, lifecycle, and data-flow signals, then checks `docs/BLUEPRINTS.md`.

2. 🗺️ **4 classes, 11 diagrams / 4 类 11 图**
   User journey, user flow, page flow, system architecture, component, sequence, state machine, ERD, DFD, deployment, and CI/CD diagrams.

3. 🔁 **Lifecycle status / 生命周期状态**
   Each diagram is tracked as `planned`, `current`, `stale`, `missing`, or `not-applicable`.

## 🆕 What v0.7.1 Adds / v0.7.1 新增

v0.7.1 hardens the end of the loop without adding a workflow server:

v0.7.1 加固执行结束时的收口，不引入重型工作流服务：

1. 🧹 **Closeout Gate / 收口门禁**
   Substantial stops must state task result, handoff trigger check, resume anchor, and one next executable step.

2. 🧱 **Commit boundary / 提交边界**
   Final output must classify safe-to-stage, do-not-stage, ignored/generated artifacts, and whether `git add .` is unsafe.

3. 🔁 **Stage-complete state / 阶段完成状态**
   Useful partial progress can stop as `stage-complete` without being mislabeled as `done`.

## 🆕 What v0.7.2 Adds / v0.7.2 新增

v0.7.2 turns commit and CI checks into agent-executed actions instead of user-facing suggestions:

v0.7.2 把提交和 CI 检查变成 Agent 自动执行动作，而不是抛给用户的建议：

1. 🧹 **Auto Commit Gate / 自动提交门禁**
   `closeout_check.py --auto-commit` commits safe task-scoped files and leaves unrelated or generated files unstaged.

2. 🧱 **CI Gate / CI 门禁**
   `scripts/ci_gate.py` runs npm tests, doctor, Blueprint Gate, contract check, and whitespace diff checks where available.

3. 🛤️ **Fewer non-decision stops / 减少非决策停顿**
   Agents should run validation, CI, trace, inspect, and safe auto-commit directly; stop only for decision-grade blockers.

## 🆕 What v0.7.3 Adds / v0.7.3 新增

v0.7.3 makes TDD a first-class gate where it matters:

v0.7.3 让 TDD 在关键任务中成为一等门禁：

1. 🔴 **TDD Gate / TDD 门禁**
   `scripts/tdd_check.py` checks TDD mode and Red-Green-Refactor evidence in task coordinates.

2. 🧪 **Default policy / 默认策略**
   TDD is required by default for bugs, regressions, parsers, validators, domain logic, APIs, shared utilities, and risky refactors.

3. 📝 **Explicit waivers / 显式豁免**
   Docs, scaffolding, release metadata, visual polish, and spikes can waive TDD with a reason.

## 🔁 Closed Loop / 闭环

```text
🎯 North Star
→ 🏗️ Blueprint Gate
→ 🧾 Coordinate Contract Draft
→ 🧭 Task Contract
→ 🔴 TDD Gate
→ 🛠️ Execute Batch
→ ✅ Done Gate
→ 🧱 CI Gate
→ 🔗 Trace
→ 🔍 Inspect
→ 🚗 Drive Decision: continue / repair / advance / review / stop
→ 🧹 Auto Commit / Closeout
→ 🤝 Handoff
```

```text
🎯 北极星目标
→ 🏗️ 图纸门禁
→ 🧾 Coordinate 契约草案
→ 🧭 任务契约
→ 🔴 TDD 门禁
→ 🛠️ 执行批次
→ ✅ 完成门禁
→ 🧱 CI 门禁
→ 🔗 Trace 记录
→ 🔍 状态检查
→ 🚗 Drive Decision：继续 / 修复 / 前进 / 复盘 / 停止
→ 🧹 自动提交 / 收口
→ 🤝 交接
```

## 🚗 Continuous Drive / 持续推进

Drive Loop adds goal-preserving initiative without turning CodeRail into an
agent runtime. Codex Goal or another long-running surface keeps the objective
active; CodeRail computes the next safe project state from repo-local evidence.

Drive Loop 增加“目标保持型主动性”，但不会把 CodeRail 变成 Agent runtime。
Codex Goal 或其他长程运行面负责维持目标，CodeRail 根据仓库证据计算下一安全状态。

Configure `docs/NORTH_STAR.md`:

```markdown
## Drive Contract

- Mode: continuous
- Terminal condition: all current-slice acceptance and terminal checks pass
- Progress signal: completed acceptance items
- Retry budget: 3
- No-progress limit: 2
- Human gates: schema, dependency, API, persistence, security, privacy, payment
```

Mark only pre-authorized tasks with `Autonomy: allowed`, then run:

```bash
python scripts/drive_check.py --target .
```

Continuous Drive proceeds for `CONTINUE`, `REPAIR`, and `ADVANCE`. It returns
control only for `REVIEW_DIRECTION`, `BLOCKED_DECISION`, `COMPLETE`, or
`EXHAUSTED`. See `references/DRIVE_LOOP.md` for the Goal Bridge and full policy.

### Mature-repository cutover / 成熟仓库切入

When adopting CodeRail after a repository already has closed task history, set
the first post-cutover task in `docs/NORTH_STAR.md`:

```markdown
## Legacy Cutoff

- Enforcement starts at: T-178
```

`inspect_state.py` then reports earlier weak verification as historical debt
without turning current status red. The anchor and later tasks remain fully
enforced; a missing anchor fails closed. Leave the field blank for a new project
or when every task should be enforced.

成熟仓库可用首个 post-cutover task 作为文档顺序锚点。旧任务缺口仍会展示，
但不再污染当前阻塞状态；锚点及后续任务继续完整执行门禁。

## 🧬 Kernel / 内核

| | Invariant | Plain meaning | 中文解释 |
|---|---|---|---|
| 🎯 K0 | North Star | Every action maps to Outcome / Current Bet / Invariants / Current Slice. | 每个动作都映射到结果、当前押注、不变量和当前切片。 |
| 🧭 K1 | CodeRail Coordinate | Every non-trivial task compresses to G/T/S/V/X/P before implementation. | 非平凡任务在实现前压缩为 G/T/S/V/X/P。 |
| 🧾 K2 | Task Contract | A task has ID, dependencies, acceptance, and completion evidence. | 任务必须有 ID、依赖、验收和完成证据。 |
| 🔴 K3 | TDD Gate | Correctness-sensitive work records Red-Green-Refactor evidence or an explicit waiver. | 正确性敏感任务记录红绿重构证据或显式豁免。 |
| ✅ K4 | Done Gate | No done without passing verification or explicit manual acceptance. | 未通过验证或无明确人工验收，不可完成。 |
| 🧰 K5 | Tool-Native Enforcement | Prefer permissions/hooks/CI over prompt-only rules. | 优先使用权限、hooks、CI，而不是只靠提示词。 |
| 🤝 K6 | Handoff | Event-triggered snapshot with Coordinate Summary, never a log dump. | 交接是事件触发的摘要，不是日志倾倒。 |
| 🗂️ K7 | Asset Boundary | Raw material, notes, candidates, permanent assets, generated artifacts, and releases are different. | 区分原料、笔记、候选物、永久资产、生成物和发布物。 |
| 🔗 K8 | Trace Graph | No meaningful action without source, target, modification, validation, and persistence links. | 有意义的动作都应有来源、目标、修改、验证和持久化链接。 |
| 🏗️ K9 | Blueprint Gate | Complex systems need current architecture, data, deployment, UI flow, and lifecycle diagrams. | 复杂系统需要当前有效的架构、数据、部署、用户流和生命周期图纸。 |
| 🧹 K10 | Auto Commit / Closeout Gate | No substantial stop without task result, auto-commit action, resume anchor, and next executable step. | 没有任务结果、自动提交动作、恢复入口和可执行下一步，不应停止。 |
| 🧱 K11 | CI Gate | Run available non-decision CI checks before stopping or handing off. | 停止或交接前运行可用的非决策性 CI 检查。 |

Drive Loop sits above K0-K11 as an execution policy. It reuses existing kernel
evidence and does not add a new source of authority.

## ⚡ Quick Start / 快速开始

Recommended path: clone CodeRail, then install its template files into your target repo.

推荐方式：先克隆 CodeRail，再把模板文件安装到目标仓库。

```bash
git clone https://github.com/HaipingShi/coderail.git
cd coderail
python scripts/init_project.py --target /path/to/your/repo --mode standard
python scripts/doctor.py --target /path/to/your/repo
```

Clone is not a hard requirement. You can also download a release archive or install from a Git URL with npm. CodeRail is currently **not published on the npm registry**, so `npm install coderail` is not the supported path yet.

clone 不是强制要求。你也可以下载 release 压缩包，或者用 npm 从 Git URL 安装。目前 CodeRail **尚未发布到 npm registry**，所以暂不支持 `npm install coderail` 这种安装方式。

Npm-style local usage after cloning:

克隆后的 npm 本地用法：

```bash
npm test
npm run ci
npm run doctor
npm run inspect
npm run closeout-check
```

For Claude Code:

```bash
claude --plugin-dir ./coderail
```

For Codex:

```text
Register this repository as a plugin source, or copy it under your plugin directory.
Use `.codex-plugin/plugin.json` as the Codex manifest.
```

## 🧩 Installation Prompt / 安装使用 Prompt

Copy this into your coding agent when CodeRail is not installed yet:

当 CodeRail 尚未安装时，可以把下面的 prompt 发给你的编码 Agent：

```text
Install CodeRail into this repository.

If CodeRail is not already available locally, clone it first:
git clone https://github.com/HaipingShi/coderail.git <path-to-coderail>

Use the local CodeRail package at <path-to-coderail>.
Run:
1. python <path-to-coderail>/scripts/init_project.py --target . --mode standard
2. python <path-to-coderail>/scripts/doctor.py --target .

Then read AGENTS.md, docs/NORTH_STAR.md, docs/TASKS.md, and docs/HARNESS_SPEC.md.
For every non-trivial coding task, draft G/T/S/V/X/P before implementation.
When architecture, data, deployment, UI flow, or lifecycle complexity appears, run blueprint_check.py and update docs/BLUEPRINTS.md.
When the task is a bug, regression, parser, validator, domain logic, API, shared utility, or risky refactor, run TDD Gate.
Before saying done, run the done gate and update trace/status files.
Before stopping, run available CI checks, auto-commit safe task-scoped work, and produce Closeout State, Auto Commit action, Handoff Trigger Check, and one Next Executable Step.
```

```text
请把 CodeRail 安装到当前仓库。

如果本机还没有 CodeRail，请先克隆：
git clone https://github.com/HaipingShi/coderail.git <path-to-coderail>

本地 CodeRail 路径是：<path-to-coderail>
请运行：
1. python <path-to-coderail>/scripts/init_project.py --target . --mode standard
2. python <path-to-coderail>/scripts/doctor.py --target .

然后读取 AGENTS.md、docs/NORTH_STAR.md、docs/TASKS.md、docs/HARNESS_SPEC.md。
每个非平凡编码任务，在实现前先起草 G/T/S/V/X/P。
当出现架构、数据、部署、用户流或生命周期复杂度时，运行 blueprint_check.py 并更新 docs/BLUEPRINTS.md。
当任务是 bug、回归、parser、validator、领域逻辑、API、共享工具或高风险重构时，运行 TDD Gate。
在宣布完成前，运行 done gate，并同步 trace/status 文件。
停止前运行可用 CI 检查，自动提交安全任务级变更，并输出收口状态、自动提交动作、交接触发检查和一个可执行下一步。
```

## 📥 Install Options / 安装方式

| Option | Command | When to use | 中文说明 |
|---|---|---|---|
| 🟢 Git clone | `git clone https://github.com/HaipingShi/coderail.git` | Best default. Works with scripts, plugin manifests, examples, and local development. | 推荐默认方式。脚本、插件 manifest、示例和本地开发都完整可用。 |
| 📦 Release archive | Download a GitHub release zip/tarball. | Useful when Git is unavailable or you want a frozen copy. | 适合不能用 Git，或需要固定版本压缩包的场景。 |
| 🟡 npm from Git URL | `npm install github:HaipingShi/coderail` | Possible as a dependency source, but no `npx coderail` CLI is exposed yet. | 可以作为依赖安装，但目前还没有暴露 `npx coderail` 命令。 |
| 🔴 npm registry | `npm install coderail` | Not available until the package is published to npm. | 尚未发布到 npm registry，暂不可用。 |

If installed through npm from a Git URL, call the scripts through the installed package path:

如果通过 npm Git URL 安装，可以通过安装后的包路径调用脚本：

```bash
node node_modules/coderail/scripts/run_python.js node_modules/coderail/scripts/init_project.py --target . --mode standard
node node_modules/coderail/scripts/run_python.js node_modules/coderail/scripts/doctor.py --target .
```

## 🧠 Daily Agent Prompt / 日常使用 Prompt

Use this at the start of a coding session:

每次开启编码会话时使用：

```text
Use CodeRail for this task.

First inspect the repo-local state:
- Read AGENTS.md.
- Read docs/CODERAIL_STATUS.md if present.
- Read docs/NORTH_STAR.md, docs/TASKS.md, docs/BLUEPRINTS.md, and docs/HARNESS_SPEC.md.

Before implementation, produce a CodeRail Coordinate:
G — Goal
T — Task
S — Scope, allowed and forbidden
V — Verify
X — Stop
P — Persist

Work only inside S. Stop if X triggers.
Use TDD Gate for correctness-sensitive work.
Before marking done, run verification, record trace evidence, run done_gate.py, and refresh inspect state.
Before stopping after substantial work, run ci_gate.py where available, then closeout_check.py --auto-commit.
If the task touches architecture, data, deployment, UI flow, or lifecycle state, run blueprint_check.py and keep required diagrams current.
```

```text
这个任务请使用 CodeRail。

请先检查仓库本地状态：
- 读取 AGENTS.md。
- 如果存在，读取 docs/CODERAIL_STATUS.md。
- 读取 docs/NORTH_STAR.md、docs/TASKS.md、docs/BLUEPRINTS.md、docs/HARNESS_SPEC.md。

实现前先给出 CodeRail Coordinate：
G — Goal，目标
T — Task，任务
S — Scope，允许和禁止范围
V — Verify，验证方式
X — Stop，停止条件
P — Persist，需要同步的记录

只在 S 范围内工作。触发 X 就停止。
对正确性敏感任务使用 TDD Gate。
标记完成前，先运行验证，记录 trace 证据，运行 done_gate.py，并刷新 inspect state。
完成实质性工作后停止前，先运行可用 ci_gate.py，再运行 closeout_check.py --auto-commit。
如果任务触及架构、数据、部署、用户流或生命周期状态，运行 blueprint_check.py，并保持必要图纸为 current。
```

## 🕹️ Normal Session / 标准会话

```text
/coderail:align           # align request to North Star / 对齐 North Star
/coderail:contract-draft  # draft formal G/T/S/V/X/P gate / 起草正式契约
/coderail:blueprint       # check/update architecture blueprint coverage / 检查图纸覆盖
/coderail:task-contract   # accept/finalize task contract / 确认任务契约
/coderail:tdd-gate        # Red-Green-Refactor evidence / TDD 门禁
/coderail:execute-batch   # work inside S until done/blocked/failed/X / 在 S 内执行
/coderail:drive           # continue/repair/advance from deterministic evidence / 根据确定性证据持续推进
/coderail:done-gate       # verification-before-complete / 完成前验证
/coderail:ci-gate         # run non-decision CI/CD checks / CI/CD 门禁
/coderail:done            # sync P, trace, status, optional handoff / 同步记录
/coderail:closeout        # auto-commit and next executable step / 自动提交收口
/coderail:inspect         # refresh CODERAIL_STATUS.md / 刷新状态
/coderail:handoff         # create event-triggered handoff / 生成交接摘要
```

## 📦 Core Files / 核心文件

```text
AGENTS.md                       # agent operating rules / Agent 执行规则
CLAUDE.md                       # Claude Code entry file / Claude Code 入口
docs/NORTH_STAR.md              # outcome alignment / 目标对齐
docs/TASKS.md                   # task contracts / 任务契约
docs/CONTRACTS.md               # coordinate contract drafts / 契约草案
docs/BLUEPRINTS.md              # architecture blueprint index / 架构图纸索引
docs/HARNESS_SPEC.md            # verification harness / 验证约定
docs/HANDOFF.md                 # handoff snapshot / 交接摘要
docs/CODERAIL_STATUS.md         # generated inspect state / 生成的状态面板
docs/TRACELOG.jsonl             # trace event log / trace 事件
docs/TRACE_INDEX.md             # trace index / trace 索引
docs/DECISIONS.md               # decision notes / 决策记录
docs/LESSONS.md                 # lessons learned / 经验记录
docs/ASSETS.md                  # asset boundary / 资产边界
```

## 🛠️ Scripts / 脚本

```bash
python scripts/contract_check.py --target .
python scripts/coordinate_check.py --target .
python scripts/tdd_check.py --target .
python scripts/blueprint_check.py --target .
python scripts/hook_guard.py --stage stop --target . --soft
python scripts/done_gate.py --target . --task T-001 --harness-result passed
python scripts/ci_gate.py --target .
python scripts/closeout_check.py --target . --task T-001 --task-result stage-complete --auto-commit
python scripts/trace_event.py --target . --type verify --task T-001 --harness-result passed --summary "tests passed"
python scripts/trace_index.py --target .
python scripts/inspect_state.py --target . --write
python scripts/drive_check.py --target .
python scripts/drive_observe.py --target .
python scripts/doctor.py --target .
python scripts/regression_observe.py --target .
```

With npm wrappers:

使用 npm 包装命令：

```bash
npm test
npm run ci
npm run doctor
npm run inspect
npm run tdd-check
npm run blueprint-check
npm run done-gate
npm run closeout-check
npm run ci
npm run contract-check
npm run regression-observe
```

## 🚦 Boundary / 边界

CodeRail is **not** a hosted CI system, issue tracker, graph database, multi-agent orchestrator, web preview, or workflow runtime. Drive computes policy state but does not run a model or scheduler. CodeRail remains a repo-local governance rail for AI coding execution.

CodeRail **不是** 托管 CI 系统、issue tracker、图数据库、多 Agent 调度器、Web 预览工具或工作流运行时。Drive 只计算策略状态，不运行模型或调度器；CodeRail 仍是一条仓库本地治理轨道。

It borrows productization patterns without copying a loop engine:

它借用了产品化模式，但不复制循环引擎：

- 🏗️ Blueprint coverage for complex architecture / 复杂架构的图纸覆盖
- 🧾 Formal draft before implementation / 实现前正式草案
- 🔍 Inspectable runtime state from repo-local files / 来自仓库本地文件的可检查运行态
- ✅ Verification-before-complete / 完成前验证
- 🧱 CI Gate and safe auto-commit / CI 门禁与安全自动提交

## 🗺️ Layout / 仓库结构

```text
.claude-plugin/      Claude Code manifest
.codex-plugin/       Codex manifest
skills/              self-contained SKILL.md files
project-template/    files copied into target repositories
scripts/             local validators, CI gate, done gate, closeout, inspect, trace tools
references/          full schemas and design notes
examples/            optional hooks and marketplace examples
tests/               structure and script smoke tests
```

## 📚 More / 更多

- [INSTALL.md](INSTALL.md) — installation notes / 安装说明
- [CHANGELOG.md](CHANGELOG.md) — release history / 版本记录
- [references/](references/) — kernel references / 内核参考
- [skills/](skills/) — agent skills / Agent 技能
