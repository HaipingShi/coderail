# CodeRail — Convergent Coding

![version](https://img.shields.io/badge/version-v0.8.4-2f80ed)
![license](https://img.shields.io/badge/license-MIT-27ae60)
![python](https://img.shields.io/badge/python-3.x-ffd43b)
![agent](https://img.shields.io/badge/agent--ready-Codex%20%7C%20Claude-8e44ad)
![scope](https://img.shields.io/badge/scope-repo--local-16a085)

**Spec is the output, not the input.**

**Spec 是产出，不是前提。**

Vibe coding explores; CodeRail converges. As you build, discover, and change your mind, the tool quietly turns what you learned into guardrails — so exploration compounds instead of unravelling. Your AI assistant stops drifting, stops declaring victory too early, and always leaves a state the next session can pick up.

Vibe coding 负责发散探索，CodeRail 负责收敛。你一边做、一边发现、一边改主意，工具在背后把你学到的东西悄悄追认为护栏——让探索层层累积，而不是层层瓦解。你的 AI 助手不再跑偏、不再过早宣布完成、并且永远留下下一个会话能接得住的项目状态。

No server. No accounts. No new methodology to learn. Just three commands and a `docs/` folder that stays honest.

没有服务端、不需要账号、不用学任何新方法论。只有三个命令，和一个不会说谎的 `docs/` 目录。

## 60-second start / 60 秒上手

```bash
# 1. Get CodeRail and install it into your project
git clone https://github.com/HaipingShi/coderail
python3 coderail/scripts/init_project.py --target /path/to/your/project

# 2. In your project, work with three commands
python .coderail/coderail.py start "add a login page"   # begin a task
python .coderail/coderail.py check                      # am I on track?
python .coderail/coderail.py done                       # finish safely
```

That is the whole interface. Your AI assistant reads the installed `AGENTS.md` and follows the same three commands automatically.

这就是全部界面。你的 AI 助手会读取安装好的 `AGENTS.md`，自动遵循同样的三个命令。

## What each command does / 三个命令做什么

**`start "..."`** — records what you are about to do, which files it may touch, and how you will know it is finished. This one step is what prevents scope creep and "wait, what was I doing?" later.

**`start`** — 记下你要做什么、会动哪些文件、怎么算完成。就这一步，避免了范围蔓延和"我刚才在干嘛来着"。

**`check`** — answers "am I on track?" in plain language: what is active, what is missing, whether you could finish right now.

**`check`** — 用大白话回答"我现在没跑偏吧"：当前任务是什么、还缺什么、现在能不能收尾。

**`done`** — the safety net. It verifies tests/checks pass (or you explicitly recorded a manual check), confirms changes stayed inside the promised files, syncs the docs, commits only the safe task-related files, and tells you the next step. If something is off, it refuses and says exactly what to fix. An AI assistant cannot talk its way past it.

**`done`** — 安全网。它验证测试通过（或你明确记录了人工检查）、确认改动没超出承诺的文件、同步文档、只提交安全的任务相关文件，然后告诉你下一步。有问题它会拒绝并明确说出要修什么——AI 助手无法用话术绕过它。

## Switching tasks safely / 安全切换任务

`start` and `next --go` refuse to create ambiguous ownership. Use the explicit
switch gate when work must branch:

```bash
python .coderail/coderail.py switch "new task"              # close and commit the accepted source first
python .coderail/coderail.py switch "new task" --checkpoint # commit a verified checkpoint, then pause it
python .coderail/coderail.py switch "new task" --dirty-fork # explicit waiver: carry a fingerprinted dirty baseline
python .coderail/coderail.py switch --to T-012               # resume a paused or queued task
```

If current work is not safely committable, CodeRail writes an H3 handoff and
requires `switch --continue-current` or an explicit `--dirty-fork`. Pre-existing
dirty files are recorded by path, Git state, and SHA-256 fingerprint so unchanged
work is not attributed to the new task. Auto-commit never means auto-push.

`start` 和 `next --go` 不允许产生模糊归属。切换任务必须经过 `switch`：已验收
任务先完成并提交；可验证检查点先提交再进入 `[p] paused`；不可提交的改动只写
H3，必须明确选择继续当前任务或携带指纹化脏基线。自动提交永远不等于自动推送。

## Why "Convergent Coding" / 为什么叫"收敛式编码"

Vibe coding is fast and creative — until the project grows. Then docs rot, the assistant drifts from the goal, sessions forget each other, and "done" stops meaning done. The usual fix is spec-driven development: write the spec first, then build. But that assumes you already know what you want — and vibe coders discover what they want *by building*. Spec-first is not too hard for them; it points the wrong way.

Vibe coding 又快又自由——直到项目变大。然后文档腐烂、助手偏离目标、会话之间互相失忆、"完成"不再意味着真的完成。常规解法是 spec 驱动开发：先写规格、再动手。但它假设你早就知道自己要什么——而 vibe coder 恰恰是**做出来才知道要什么**。spec 前置对他们不是太难，是方向反了。

Convergent Coding inverts the arrow. You explore freely; each time something proves true — a task verified, a decision made, a boundary learned — the tool records it as a constraint the next round of exploration must respect. The spec accumulates behind you instead of blocking the road ahead. Exploration stays free; the project stops oscillating and starts converging. When repeated fixing fails to converge, the tool says so and points one level up: rethink the design, or rethink the goal.

Convergent Coding 把箭头倒过来。你自由探索；每当一件事被证实——一个任务通过验证、一个决策被做出、一条边界被踩明白——工具就把它记录为下一轮探索必须尊重的约束。spec 在你身后累积，而不是挡在你前面。探索依旧自由，项目却不再震荡、开始收敛。当反复修补无法收敛时，工具会直说，并把你的注意力抬高一层：重新想设计，或者重新想目标。

In short: discipline runs automatically behind three plain commands. You never write a spec; the tool quietly maintains one for you (goal, task list, decision log, change history) and refuses to let anyone — human or AI — skip verification.

一句话：纪律在三个命令背后自动运行。你从不写 spec，工具在背后悄悄替你维护（目标、任务清单、决策记录、变更历史），并且拒绝让任何人——无论人类还是 AI——跳过验证。

## What lives in your repo / 装进仓库的是什么

```
your-project/
├── AGENTS.md            # plain-language rules your AI assistant follows
├── .coderail/           # the single entry command
└── docs/
    ├── NORTH_STAR.md    # what you are building, one page
    ├── TASKS.md         # every task: goal, files, how it was verified
    ├── DECISIONS.md     # why things are the way they are
    ├── HANDOFF.md       # how the next session picks up
    └── TRACELOG.jsonl   # append-only history linking changes to reasons
```

Plain text, all in git, nothing hidden. Delete the folder and CodeRail is gone.

全是纯文本、全在 git 里、没有黑盒。删掉目录，CodeRail 就卸载了。

## Zero dependencies / 零依赖

Pure Python 3 standard library. Works with Codex, Claude Code, and any agent that reads `AGENTS.md` / `CLAUDE.md`.

纯 Python 3 标准库。适配 Codex、Claude Code，以及任何会读 `AGENTS.md` / `CLAUDE.md` 的 Agent。

## Advanced / 进阶

The three commands are a facade over a deeper kernel: verification gates, TDD evidence, drift detection, deterministic drive decisions for long-running autonomous sessions, architecture blueprints, and trace graphs. Power users can call these directly:

三个命令是一层门面，背后是完整内核：验证门禁、TDD 证据、漂移检测、长时自主会话的确定性推进决策、架构图纸、追踪图谱。进阶用户可以直接调用：

```bash
python .coderail/coderail.py --help    # lists advanced commands
```

The idea behind the tool — Convergent Coding — is written up in [`references/CONVERGENT_CODING.md`](references/CONVERGENT_CODING.md). Deep documentation lives in [`references/`](references/). Install details in [`INSTALL.md`](INSTALL.md). Skills for Claude Code / Codex live in [`skills/`](skills/).

工具背后的思想——Convergent Coding（收敛式编码）——完整阐述见 [`references/CONVERGENT_CODING.md`](references/CONVERGENT_CODING.md)。深度文档见 [`references/`](references/)，安装细节见 [`INSTALL.md`](INSTALL.md)，Claude Code / Codex 的 skills 见 [`skills/`](skills/)。

## License

MIT
