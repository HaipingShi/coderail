# CodeRail

![version](https://img.shields.io/badge/version-v0.6.1-2f80ed)
![license](https://img.shields.io/badge/license-MIT-27ae60)
![python](https://img.shields.io/badge/python-3.x-ffd43b)
![agent](https://img.shields.io/badge/agent--ready-Codex%20%7C%20Claude-8e44ad)
![scope](https://img.shields.io/badge/scope-repo--local-16a085)

🛤️ **Draft before coding. Verify before done. Inspect before handoff.**
🛤️ **先对齐再编码，先验证再完成，先检查再交接。**

CodeRail is a lightweight governance rail for AI coding agents. It keeps long-running coding work aligned through a small repo-local kernel: North Star, CodeRail Coordinate, Coordinate Contract Drafts, task contracts, verification-before-complete, runtime state inspect, short handoffs, asset boundaries, and trace links.

CodeRail 是一个面向 AI 编码 Agent 的轻量级治理轨道。它不是 CI、任务系统或工作流引擎，而是在你的仓库里放入一套小而稳定的执行内核：North Star、CodeRail Coordinate、契约草案、任务契约、完成前验证、运行态检查、交接摘要、资产边界和可追踪链接。

Version: **v0.6.1**

## ✨ What It Does / 它解决什么

| Icon | English | 中文 |
|---|---|---|
| 🎯 | Keeps every coding action tied to a North Star outcome. | 让每个编码动作都能回到明确的目标。 |
| 🧭 | Compresses work into G/T/S/V/X/P before implementation. | 开始实现前，把任务压缩成 G/T/S/V/X/P。 |
| 🧾 | Drafts a contract for vague, risky, or cross-module requests. | 对模糊、高风险、跨模块需求先生成契约草案。 |
| ✅ | Blocks "done" until verification, scope, persistence, and trace are present. | 没有验证、范围约束、持久化和 trace，不允许标记完成。 |
| 🔍 | Produces a compact repo-local state surface for resume/debug/handoff. | 生成可检查的仓库状态，方便恢复、调试和交接。 |
| 🔗 | Records trace events so decisions, changes, and validation stay connected. | 记录 trace 事件，让决策、修改和验证保持连接。 |

## 🧑‍💻 For Users / 面向用户

Use CodeRail when you want your AI coding assistant to stop drifting, stop declaring victory too early, and leave behind a useful state that another session can pick up.

当你希望 AI 编码助手减少跑偏、不要过早宣布完成、并且能留下可恢复的项目状态时，使用 CodeRail。

Good fit / 适合场景：

- 🚀 Long-running feature work with multiple files or phases.
- 🧩 Cross-module refactors where scope creep is easy.
- 🧪 Work that must prove tests, build, lint, or manual acceptance.
- 🤝 Human-to-agent or agent-to-agent handoff.
- 🗂️ Repos that need lightweight governance without adopting a full workflow platform.
- 🚀 多阶段、多文件的功能开发。
- 🧩 容易范围蔓延的跨模块重构。
- 🧪 需要证明测试、构建、lint 或人工验收的任务。
- 🤝 人与 Agent、Agent 与 Agent 之间的交接。
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

Agent rule of thumb / Agent 执行口诀：

```text
Align G/T/S/V/X/P.
Work only inside S.
Stop when X fires.
Do not mark done until V passes and P is synced.
Leave trace evidence.
```

```text
先对齐 G/T/S/V/X/P。
只在 S 范围内工作。
触发 X 就停。
V 未通过、P 未同步，不要标记完成。
留下 trace 证据。
```

## 🌏 5W2H

| Question | English | 中文 |
|---|---|---|
| 🧑 Who | AI coding agents, agent operators, maintainers, and teams that hand work between sessions. | AI 编码 Agent、Agent 使用者、维护者，以及需要跨会话交接的团队。 |
| ❓ What | A repo-local governance rail made of templates, skills, validators, done gate, inspect state, and trace logs. | 一套仓库本地治理轨道：模板、技能、校验器、完成门禁、状态检查和 trace 日志。 |
| 🕰️ When | Before coding starts, before marking done, when resuming, when drift appears, and before handoff. | 编码前、标记完成前、恢复会话时、发现跑偏时、交接前。 |
| 📍 Where | Inside the target repository, mostly under `docs/`, plus `AGENTS.md` and optional plugin manifests. | 在目标仓库内部，主要位于 `docs/`，并包含 `AGENTS.md` 和可选插件 manifest。 |
| 💡 Why | Agents need small, explicit rails: intent, scope, verification, persistence, and traceability. | Agent 需要小而明确的轨道：意图、范围、验证、持久化和可追踪性。 |
| 🛠️ How | Initialize templates, draft/accept a coordinate, execute inside scope, run done gate, record trace, inspect state. | 初始化模板，起草并接受 coordinate，在范围内执行，运行 done gate，记录 trace，检查状态。 |
| 📏 How much | Lightweight: no server, no database, no runtime loop. Standard-library Python scripts and Markdown files. | 很轻：不需要服务端、数据库或循环运行时。主要是标准库 Python 脚本和 Markdown 文件。 |

## 🆕 What v0.6 Adds / v0.6 新增

v0.6 productizes CodeRail without turning it into a loop runtime:

v0.6 将 CodeRail 产品化，但不把它变成循环运行时：

1. 🧾 **Formal contract draft / 正式契约草案**
   `/coderail:contract-draft` and `docs/CONTRACTS.md` create a visible pre-implementation `Coordinate Contract Draft` for vague, high-risk, cross-module, or mid-session requirements.

2. 🔍 **Runtime state inspect / 运行态检查**
   `/coderail:inspect` and `scripts/inspect_state.py` generate `docs/CODERAIL_STATUS.md`, a compact state surface for resuming, debugging drift, or preparing handoff.

3. ✅ **Verification-before-complete / 完成前验证**
   `/coderail:done-gate` and `scripts/done_gate.py` block completion until V passes, S is respected, P is synced, and trace evidence exists.

## 🔁 Closed Loop / 闭环

```text
🎯 North Star
→ 🧾 Coordinate Contract Draft
→ 🧭 Task Contract
→ 🛠️ Execute Batch
→ ✅ Done Gate
→ 🔗 Trace
→ 🔍 Inspect
→ 🤝 Handoff
```

```text
🎯 北极星目标
→ 🧾 Coordinate 契约草案
→ 🧭 任务契约
→ 🛠️ 执行批次
→ ✅ 完成门禁
→ 🔗 Trace 记录
→ 🔍 状态检查
→ 🤝 交接
```

## 🧬 Kernel / 内核

| | Invariant | Plain meaning | 中文解释 |
|---|---|---|---|
| 🎯 K0 | North Star | Every action maps to Outcome / Current Bet / Invariants / Current Slice. | 每个动作都映射到结果、当前押注、不变量和当前切片。 |
| 🧭 K1 | CodeRail Coordinate | Every non-trivial task compresses to G/T/S/V/X/P before implementation. | 非平凡任务在实现前压缩为 G/T/S/V/X/P。 |
| 🧾 K2 | Task Contract | A task has ID, dependencies, acceptance, and completion evidence. | 任务必须有 ID、依赖、验收和完成证据。 |
| ✅ K3 | Done Gate | No done without passing verification or explicit manual acceptance. | 未通过验证或无明确人工验收，不可完成。 |
| 🧰 K4 | Tool-Native Enforcement | Prefer permissions/hooks/CI over prompt-only rules. | 优先使用权限、hooks、CI，而不是只靠提示词。 |
| 🤝 K5 | Handoff | Event-triggered snapshot with Coordinate Summary, never a log dump. | 交接是事件触发的摘要，不是日志倾倒。 |
| 🗂️ K6 | Asset Boundary | Raw material, notes, candidates, permanent assets, generated artifacts, and releases are different. | 区分原料、笔记、候选物、永久资产、生成物和发布物。 |
| 🔗 K7 | Trace Graph | No meaningful action without source, target, modification, validation, and persistence links. | 有意义的动作都应有来源、目标、修改、验证和持久化链接。 |

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
npm run doctor
npm run inspect
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
Before saying done, run the done gate and update trace/status files.
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
在宣布完成前，运行 done gate，并同步 trace/status 文件。
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
- Read docs/NORTH_STAR.md, docs/TASKS.md, and docs/HARNESS_SPEC.md.

Before implementation, produce a CodeRail Coordinate:
G — Goal
T — Task
S — Scope, allowed and forbidden
V — Verify
X — Stop
P — Persist

Work only inside S. Stop if X triggers.
Before marking done, run verification, record trace evidence, run done_gate.py, and refresh inspect state.
```

```text
这个任务请使用 CodeRail。

请先检查仓库本地状态：
- 读取 AGENTS.md。
- 如果存在，读取 docs/CODERAIL_STATUS.md。
- 读取 docs/NORTH_STAR.md、docs/TASKS.md、docs/HARNESS_SPEC.md。

实现前先给出 CodeRail Coordinate：
G — Goal，目标
T — Task，任务
S — Scope，允许和禁止范围
V — Verify，验证方式
X — Stop，停止条件
P — Persist，需要同步的记录

只在 S 范围内工作。触发 X 就停止。
标记完成前，先运行验证，记录 trace 证据，运行 done_gate.py，并刷新 inspect state。
```

## 🕹️ Normal Session / 标准会话

```text
/coderail:align           # align request to North Star / 对齐 North Star
/coderail:contract-draft  # draft formal G/T/S/V/X/P gate / 起草正式契约
/coderail:task-contract   # accept/finalize task contract / 确认任务契约
/coderail:execute-batch   # work inside S until done/blocked/failed/X / 在 S 内执行
/coderail:done-gate       # verification-before-complete / 完成前验证
/coderail:done            # sync P, trace, status, optional handoff / 同步记录
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
python scripts/done_gate.py --target . --task T-001 --harness-result passed
python scripts/trace_event.py --target . --type verify --task T-001 --harness-result passed --summary "tests passed"
python scripts/trace_index.py --target .
python scripts/inspect_state.py --target . --write
python scripts/doctor.py --target .
```

With npm wrappers:

使用 npm 包装命令：

```bash
npm test
npm run doctor
npm run inspect
npm run done-gate
npm run contract-check
```

## 🚦 Boundary / 边界

CodeRail is **not** a CI system, issue tracker, graph database, multi-agent orchestrator, web preview, or workflow runtime. It is a repo-local governance rail for AI coding execution.

CodeRail **不是** CI 系统、issue tracker、图数据库、多 Agent 调度器、Web 预览工具或工作流运行时。它是一条仓库本地的 AI 编码执行治理轨道。

It borrows three productization patterns without copying a loop engine:

它借用了三个产品化模式，但不复制循环引擎：

- 🧾 Formal draft before implementation / 实现前正式草案
- 🔍 Inspectable runtime state from repo-local files / 来自仓库本地文件的可检查运行态
- ✅ Verification-before-complete / 完成前验证

## 🗺️ Layout / 仓库结构

```text
.claude-plugin/      Claude Code manifest
.codex-plugin/       Codex manifest
skills/              self-contained SKILL.md files
project-template/    files copied into target repositories
scripts/             local validators, done gate, inspect, trace tools
references/          full schemas and design notes
examples/            optional hooks and marketplace examples
tests/               structure and script smoke tests
```

## 📚 More / 更多

- [INSTALL.md](INSTALL.md) — installation notes / 安装说明
- [CHANGELOG.md](CHANGELOG.md) — release history / 版本记录
- [references/](references/) — kernel references / 内核参考
- [skills/](skills/) — agent skills / Agent 技能
