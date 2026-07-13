# Convergent Coding / 收敛式编码

> Spec is the output, not the input.
> Spec 是产出，不是前提。

This document defines the idea behind CodeRail. It is a positioning statement,
not a methodology to study — the tool applies it automatically.

本文定义 CodeRail 背后的思想。它是一份定位陈述，不是需要学习的方法论——工具会自动应用它。

## The problem / 问题

Two camps dominate how people build software with AI:

- **Vibe coding**: describe, generate, look, react. Fast, creative, and honest
  about how amateurs actually work — but it does not converge. Docs rot,
  assistants drift, sessions forget each other, and late in the project the
  owner loses the ability to judge what is going on.
- **Spec-driven development**: write the specification first, then build.
  It converges — but it assumes you already know what you want. Amateur
  builders discover what they want *by building*. For them spec-first is not
  merely difficult; the arrow points the wrong way.

当下用 AI 造软件的两大阵营：

- **Vibe coding**：描述、生成、看、反应。快、有创造力、忠于业余开发者的真实
  工作方式——但它不收敛。文档腐烂、助手漂移、会话失忆，项目后期连项目
  拥有者自己都失去了判断力。
- **Spec 驱动开发**：先写规格再动手。它收敛——但它假设你早就知道自己要
  什么。业余开发者恰恰是**做出来才知道要什么**。对他们来说 spec 前置不是
  太难，是方向反了。

## The idea / 思想

Convergent Coding keeps vibe coding's direction of discovery and adds the one
thing it lacks: a mechanism that makes exploration accumulate instead of
unravel.

The loop has three beats:

1. **Explore** — build freely, in whatever language you think in
   ("make the button do X"). No upfront modelling required.
2. **Ratify** — each time something proves true — a task verified, a decision
   made, a boundary learned the hard way — the tool records it as a
   constraint. The spec grows *behind* you, assembled from verified facts,
   never written in advance.
3. **Converge or escalate** — feedback is compared against what was ratified.
   If the work drifts, the tool says so. If repeated fixing fails to converge,
   that is itself a signal (Wiener's second-order feedback): the problem lives
   one level up. The tool then points there explicitly — rethink the design,
   or rethink the goal.

Convergent Coding 保留 vibe coding 的发现方向，补上它唯一缺失的东西：一个让
探索层层累积、而非层层瓦解的机制。

循环有三拍：

1. **探索**——用你自己的语言自由地做（"让这个按钮做 X"），不要求任何前置建模。
2. **追认**——每当一件事被证实——任务通过验证、决策被做出、边界被踩明白——
   工具就把它记录为约束。spec 在你**身后**生长，由被验证过的事实拼装而成，
   从不预先书写。
3. **收敛或升层**——反馈与已追认的约束对照。工作跑偏，工具直说。反复修补
   仍不收敛，这本身就是信号（维纳的二阶反馈）：问题在上一层。工具会明确
   指过去——重新想设计，或重新想目标。

## What it borrows, and what it changes / 借用与改造

Convergent Coding is not a rejection of existing ideas. It extracts the
smallest effective ingredient from each and re-mounts them on the
explore–ratify–converge loop:

| Source | Ingredient kept | Change made |
|---|---|---|
| Spec-driven | Explicit goal, scope, done-criteria | Shrunk to three lines per task; produced during work, not before it |
| TDD | "State the expectation verifiably before claiming success" | Enforced only where correctness matters (bugs, parsers, domain logic, APIs); waived for exploration |
| Domain-driven design | A shared reference the whole project aligns to | Reduced to one plain-language North Star; alignment triggered by non-convergence, not by ceremony |
| Cybernetics (Wiener) | Feedback against a reference signal; escalate when feedback fails to converge | Implemented as deterministic counters, never LLM judgment |

Convergent Coding 不是对既有思想的否定。它从每一种思想中萃取最小有效成分，
重新装配在"探索—追认—收敛"循环上：

| 来源 | 保留的成分 | 所做的改造 |
|---|---|---|
| Spec 驱动 | 显式的目标、范围、完成标准 | 缩到每任务三行；在工作中产出，而非工作前 |
| TDD | "在宣称成功前，用可验证的语言说清期望" | 只在正确性敏感处强制（bug、解析器、领域逻辑、API）；探索性工作自动豁免 |
| 领域驱动设计 | 全项目对齐的共同参照 | 退化为一段人话 North Star；由"不收敛"触发对齐，而非仪式 |
| 控制论（维纳） | 对照参考信号的反馈；反馈不收敛时升层 | 以确定性计数实现，绝不依赖 LLM 判断 |

## Design commitments / 设计承诺

Any tool claiming to implement Convergent Coding should honor these:

1. **The user never writes a spec.** The tool assembles one from verified work.
2. **Ratified facts are cheap to create and hard to violate.** Three lines to
   start a task; a gate that cannot be talked past to finish one.
3. **Escalation is counted, not felt.** "You are going in circles" comes from
   arithmetic on the history, never from a model's mood.
4. **Every report is decodable by the owner.** Plain language, three questions:
   what changed, how it was verified, what's next. An owner who can always
   decode the feedback never loses judgment.
5. **Everything lives in the repo as plain text.** Delete the folder and the
   tool is gone; the ratified history remains readable.

任何声称实现 Convergent Coding 的工具都应遵守：

1. **用户从不写 spec。**工具从被验证的工作中拼装出 spec。
2. **追认的事实创建成本极低、违反成本极高。**开始任务只需三行；结束任务
   要过一道无法用话术绕过的门。
3. **升层靠计数，不靠感觉。**"你在原地打转"来自对历史的算术，绝不来自
   模型的情绪。
4. **每一份汇报都是项目拥有者可解码的。**人话、三个问题：改了什么、怎么
   验证的、下一步是什么。永远能解码反馈的人，永远不会失去判断力。
5. **一切以纯文本存在于仓库中。**删掉目录工具即卸载，被追认的历史依然可读。

## One sentence / 一句话

Vibe coding explores; Convergent Coding makes exploration converge.

Vibe coding 负责发散，Convergent Coding 让发散收敛。
