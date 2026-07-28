# CodeRail 内核边界观察基线

日期：2026-07-28  
任务：T-048  
基准提交：`80dc40abdf3586d913b48ac5e1936b8c40fb1d79`  
结论：**OBSERVE**

## 1. 目的和边界

这份记录回答的不是“`scripts/coderail.py` 是否太长”，而是：

1. 当前维护是否已经出现可重复的跨边界伤害；
2. 哪些职责和状态确实共同变化；
3. 现有模块和测试是否已经控制了这些风险；
4. 未来什么证据才足以申请受限内核治理。

本次只读取当前仓库和 Git 历史，未修改生产代码、测试、模板、技能、
依赖、版本或插件清单。观察期间仍受 stabilization freeze 和 ADR-010
约束。代码长度、函数数量、个人架构偏好都不能单独授权重构。

## 2. 可复现方法

以下命令在仓库根目录运行。共同变更统计只使用当前分支可见的 Git 历史。

```powershell
git fetch --prune origin
git rev-list --left-right --count HEAD...origin/main
git status --short --branch

(Get-Content scripts/coderail.py).Count
(Get-Item scripts/coderail.py).Length
(rg -n "^def " scripts/coderail.py | Measure-Object).Count
(rg -n "^def cmd_" scripts/coderail.py | Measure-Object).Count
rg -n "^def " scripts/coderail.py

git log --format="%h`t%ad`t%s" --date=short -- scripts/coderail.py
git show --format= --unified=0 <commit> -- scripts/coderail.py
git show --numstat --format= <commit> -- scripts/coderail.py
git diff-tree --no-commit-id --name-only -r <commit>

python tests/test_structure.py
python scripts/doctor.py --target .
python .coderail/coderail.py check
python scripts/trace_doctor.py --target .
git diff --check
```

共同变更统计的操作定义：

- “命令处理器共同变更”指一个提交的零上下文 diff hunk 标题中出现至少两个
  不同的 `cmd_*` 函数；
- “小提交”仅为便于观察而定义为 `scripts/coderail.py` 中增删合计不超过
  50 行；这不是质量判断或治理阈值；
- 状态文件共同变更只统计
  `.coderail/tasks.json`、`TASKS`、`PROGRESS`、`TRACELOG`、
  `TRACE_INDEX`、`CODERAIL_STATUS` 和 `HANDOFF`；
- hunk 标题可能把模块级或新函数变更归到相邻函数，因此本报告同时人工复核
  了相关 diff；该统计适合发现趋势，不声称是完整调用图。

## 3. 当前规模基线

| 项目 | 当前值 | 性质 |
|---|---:|---|
| `scripts/coderail.py` 物理行数 | 2,784 | 规模信号 |
| 文件大小 | 116,416 bytes | 规模信号 |
| 顶层函数 | 86 | 规模信号 |
| `cmd_*` 命令处理器 | 12 | 规模信号 |
| `cmd_done` AST 函数跨度 | 421 行（1614-2034） | 集中度信号 |
| `cmd_done` 至下一顶层函数区域 | 425 行（1614-2038） | 与既有约 425 行基线一致 |
| 锁定核心测试清单 | 122 个唯一测试定义 | 控制措施 |
| 当前分支/远程差异 | `0 0` | 同步事实 |
| 工作起点 | `main`、`origin/main` 均为 `80dc40a` | 同步事实 |

文件从 2026-07-13 至本基线共有 21 个提交触及。这个历史窗口短，且包含
功能汇聚、收口治理、稳定冻结和一次未记录例外，不能把其开发期共同变更率
直接当作长期维护期的回归率。

## 4. 职责地图

下表描述当前实际职责，不建议按表立即拆文件。

| 职责 | 主要入口或函数区域 | 依赖的现有模块 | 当前边界观察 |
|---|---|---|---|
| CLI 与参数解析 | `build_parser` 2576-2736；`main` 2739-2780；`ADVANCED` | 各脚本入口 | 解析集中；高级/兼容命令直接旁路到旧脚本 |
| 任务读取、编号和查询 | `read_tasks`、`list_tasks`、`next_task_id`、`task_contract_metadata`、`cmd_why/graph/impact` | `task_graph`、`trace_graph` | 编号同时扫描 TASKS、PROGRESS、TRACE、metadata，是 ADR-011 的有意契约 |
| start/next/switch 生命周期 | `cmd_start` 1073-1257；`cmd_next` 2158-2217；`cmd_switch` 2222-2354 | `task_switch`、`repository_state`、`task_graph` | 激活前置检查、基线、依赖和 TRACE 必须一致 |
| check/Doctor/Inspect 健康判断 | `cmd_check` 1262-1315；`post_close_consistency`；`prepare_committed_status` | `doctor.py`、`inspect_state`、`trace_doctor` | T-047 已证实 check 不能只看局部 Coordinate/TDD |
| 验证与验收 | `task_contract_metadata`、`run_verify_commands`、`cmd_done` 前半段 | `finish_task.py`、`done_gate.py`、`ci_gate.py`、`tdd_check.py` | 规则既有局部解析，也有完整仓库门禁 |
| done 收口事务 | `cmd_done` 1614-2034；`finalize_resumed_closeout` | `closeout_transaction`、`finish_task`、`repository_state` | 单函数长，但 `FINALIZED` 成功判断已外置为唯一事务权威 |
| Git 精确提交与恢复 | `stage_exact_files`、`commit_staged`、`persist_commit_pending`、resume/compensation | `repository_state`、`task_switch` | 明确文件列表、指纹和 pending 恢复已有端到端覆盖 |
| PROGRESS/TRACE/STATUS/tasks.json 持久化 | `append_progress`、`append_trace_events`、`save_meta`、ledger repair | `trace_graph`、`trace_index`、`inspect_state`、`task_switch` | 多流程写同一文件，但文件语义和最终成功权威已有 ADR 约束 |
| Blueprint、任务图和候选边 | `cmd_blueprint`、`cmd_link`、`cmd_candidate` | `blueprint_check`、`task_graph`、`trace_graph` | T-046 新增范围大；ADR-013 已认定其冻结期准入违规，不能作后续扩展先例 |
| 用户输出与兼容命令 | `print_*`、Done Report、`ADVANCED` passthrough | `finish_task`、`closeout_check`、各诊断脚本 | 兼容入口仍可写部分状态；T-047 已删除把它们描述为第二完成流程的指导 |

现有模块化不是空壳。`repository_state` 已拥有唯一 Git porcelain 解析；
`closeout_transaction` 已拥有唯一成功状态；`task_switch` 管理基线和切换恢复；
`inspect_state` 统一渲染状态；`trace_graph` 和 `task_graph` 承担图语义。因而
“所有逻辑都只存在于 2,784 行文件中”不符合当前事实。

## 5. 状态文件所有权表

“写入者”表示当前可达代码路径，不等于存在多个业务事实来源。

| 状态 | 语义权威 | 当前写入路径 | 共同使用流程 | 观察结论 |
|---|---|---|---|---|
| `docs/TASKS.md` | 热任务、当前状态和 Coordinate | `coderail.py`、`finish_task.py`、`task_switch.py`、`task_graph.py` | start/next/switch/done/progress/link | **已证实共享写入面**；状态文件本身仍是单一事实源 |
| `.coderail/tasks.json` | 任务机器契约、基线、关系和恢复元数据 | 三个 `save_meta` 实现：`coderail`、`task_switch`、`task_graph` | start/switch/done/graph | **已证实共享 schema 写入面**；尚无当前数据丢失或冲突复现 |
| `docs/PROGRESS.md` | 已完成任务的人类可读历史之一 | `coderail.append_progress`、`cmd_progress --repair` | done/progress/inspect/编号 | 当前正常路径写入集中在 facade |
| `docs/TRACELOG.jsonl` | 追加式事实和 verify 权威 | `trace_graph.append_event`；兼容 `trace_event.append_event` | start/switch/done/link/candidate/finish | **存在两个低层追加实现**；未观察到格式冲突，Trace Doctor 当前健康 |
| `docs/TRACE_INDEX.md` | TRACE 派生索引，不是独立事实源 | `trace_index.py` | 所有追加 TRACE 的流程 | 单一生成器；多调用者不构成多权威 |
| `docs/CODERAIL_STATUS.md` | Inspect 的时间点投影，不是源状态 | `inspect_state.py`；`coderail.prepare_committed_status` | inspect/check/done/doctor | T-047 已证实提交前后投影会漂移；现有修复把预期 clean 投影纳入唯一提交 |
| `docs/HANDOFF.md` | 暂停/失败切换交接 | `task_switch.write_h3_handoff`；初始化器只负责种子 | switch/doctor/inspect | 正常运行写入集中 |
| `.coderail/pending_close.json` | 忽略的 closeout 恢复快照 | `coderail.py` | done/resume/inspect | 单一 facade 写入；不是完成事实 |
| `.coderail/reports/*` | Done/门禁报告证据 | `coderail.py` 及门禁脚本 | done/人工复查 | 补充证据，不是任务状态权威 |
| `docs/TRACE_CANDIDATES.jsonl` | 非权威候选边历史 | `trace_graph` | candidate add/promote/reject | 明确与正式图隔离 |
| `docs/BLUEPRINTS.md` | 图覆盖索引 | `cmd_blueprint --scaffold`；初始化器种子 | blueprint/check/done | 仅显式 scaffold 写入 |

### 兼容路径是否仍有独立写能力

答案是“有，但尚未证实形成冲突权威”：

- `main` 对 `finish`/`finish-task` 仍直接转发到 `finish_task.py`。该脚本可以
  写 TASKS、追加 verify TRACE、刷新 TRACE_INDEX 和 STATUS；
- `trace` 仍直接转发到 `trace_event.py`，其 JSONL 追加实现独立于
  `trace_graph.append_event`；
- `closeout_check.py --auto-commit` 仍能精确提交安全文件，但不负责把任务
  完成，也不拥有 `FINALIZED`；
- `inspect` 按设计写时间点 STATUS。

ADR-007、T-047 的测试和 Skills 已把 `coderail done` 定为唯一完成权威，并
阻止正常指导再次启动 `finish` 或二次 closeout。因而这里记录的是一个
**可达兼容写入面**，不是已经复现的双重完成结果。若未来兼容入口对同一任务
产生与 `done` 不同的状态、提交或健康结论，即命中治理触发条件。

## 6. Git 共同变更观察

### 6.1 汇总

| 指标 | 结果 |
|---|---:|
| 触及 `scripts/coderail.py` 的提交 | 21 |
| 触及至少一个 `cmd_*` 的提交 | 18 |
| 同时触及至少两个 `cmd_*` 的提交 | 12 |
| 小提交（文件内增删 <= 50 行） | 7 |
| 小提交且跨至少两个 `cmd_*` | 2 |
| 同时修改其他 `scripts/*` 的提交 | 15 |
| 同时修改 `tests/*` 的提交 | 14 |
| 同时修改观察集状态文件的提交 | 10 |

12/21 的多命令比例说明生命周期职责确实经常一起开发；但 2/7 的小提交比例
不支持“日常小改动经常跨越多个职责区域”的更强结论。尤其 T-015、T-018、
T-046 是主动改变持久化、恢复或任务图契约的大任务，不能当成小修成本。

### 6.2 有代表性的提交

| 提交 | `coderail.py` 增删 | 触及区域 | 可支持的结论 |
|---|---:|---|---|
| `1231d5d` | 8+/3- | start、progress、Done Report 路径 | **已证实**：跨平台路径规则需要同时覆盖登记和持久化输出；这是小型跨区修复 |
| `b62aa58` | 134+/10- | done、progress、finish/init | **已证实**：close-before-report 顺序只能结合收口状态和报告验证 |
| `5807eb9` (T-015) | 153+/17- | task read、start、done、progress、switch | **已证实**：热 TASKS 压缩依赖 PROGRESS+TRACE 历史和编号规则 |
| `06cfc7f` (T-018) | 411+/44- | start、done、next、switch、Git pending | **已证实**：scope 与 commit-pending 是跨生命周期契约；不是小改动 |
| `0108c68` (T-046) | 470+/14- | start/check/done/next/switch/图命令 | 大范围共同变更事实成立；ADR-013 认定其冻结期准入违规，不能据此推导重构必要性 |
| `80dc40a` (T-047) | 30+/2- | check、done、rail/STATUS | **已证实**：健康、完成、Git clean 投影可发生跨边界漂移；但这是一个包含六项复现的修复包，不是单一微小缺陷 |

### 6.3 哪些行为需要端到端验证

以下行为不能只靠纯函数断言证明：

- `done` 是否只提交精确安全文件，并在提交后保持 clean；
- Git hook 在 commit 后改变文件时，是否禁止输出 Done 并恢复阻塞状态；
- `COMMIT_PENDING` 的手工提交和 `done --resume` 是否完整、幂等；
- TASKS、PROGRESS、TRACE、STATUS、metadata 是否在一次收口后一致；
- start/switch 的基线、暂停、dirty-fork 和 closed-owner 是否保持单一所有者；
- Doctor 不健康时，`coderail check` 是否也失败并展示同一问题。

这不是未覆盖风险。`test_closeout.py`、`test_lifecycle.py` 和
`test_task_switch.py` 会创建临时 Git 仓库执行真实命令；`test_static.py`
覆盖 Doctor/check、rail、launcher 和兼容指导；`test_inspect.py` 直接覆盖
状态投影。纯规则也已有局部测试，例如 repository classifier、
`CloseoutTransaction`、Doctor marker、Inspect 的状态函数和 `guess_rail`。
锁定清单为 122 个唯一测试。因此当前事实是“事务性规则需要端到端测试且已有
覆盖”，不是“局部行为无法验证”。

## 7. 证据分级

### 7.1 规模信号，不是治理理由

- 2,784 行、116,416 bytes、86 个顶层函数、12 个命令处理器；
- `cmd_done` 约 425 行区域；
- 一个 facade 同时承接 CLI、用户输出和若干事务编排。

这些数字只说明值得观察。没有缺陷频率、改动扩散和回归成本时，它们不授权
移动、抽取、重命名或重构。

### 7.2 已证实的耦合证据

- T-047 证明 Doctor/check、done、Git clean 投影、STATUS 和任务元数据之间
  会发生真实漂移；
- T-015 证明任务编号和完成历史必须联合 TASKS、PROGRESS、TRACE 和 metadata；
- T-018 证明 scope 规则必须在 start/switch 和 done 前后保持同一语义；
- TASKS 和 tasks.json 均由多个生命周期模块写入；
- TRACELOG 仍有正式图与 legacy trace 两个低层追加实现；
- 若干 Git/收口规则确实只能由临时仓库端到端场景完整证明。

### 7.3 只有怀疑、尚未证实的风险

- 多个 `save_meta` 将来可能发生 schema 覆盖；
- legacy `finish` 或 `trace` 将来可能与 facade 的事务结果分叉；
- `cmd_done` 的集中度将来可能增加修改认知成本；
- 任务图、候选边和生命周期命令将来可能继续扩大 parser/main 的共同变更；
- 完整回归套件将来可能慢到妨碍正常维护。

本基线没有复现 metadata 覆盖、双重 Done、Trace 格式分裂，也没有记录测试耗时
拖慢任务或 Agent 必须理解大部分文件才能完成小改动。因此这些不能写成事实。

### 7.4 已由现有模块化和测试控制的风险

- `repository_state.py` 是唯一 Git porcelain 解析者；
- `closeout_transaction.py` 的 `FINALIZED` 是唯一成功判断；
- `trace_index.py` 是 TRACE_INDEX 的单一生成器；
- Inspect 状态统一由 `inspect_state.render` 计算；
- 122 个核心测试按 static、drive、inspect、task-switch、lifecycle、closeout
  分组，并由 `test_structure.py` 稳定聚合；
- scope、pending resume、post-commit mutation、精确 staging、单一活动任务、
  compacted history 和 T-047 回归均有定向测试；
- stabilization freeze 和 ADR-010 阻止无缺陷证据的一般性治理。

## 8. 未来 5 个维护任务的被动观察协议

不预先创建任务，不新增 hook、遥测、命令或监控。只在未来实际发生的 CodeRail
维护任务完成后，用其已有 Git、TASKS、TRACE 和 Done Report 填一行。缺少记录
时写 `unknown`，不能把“没有证据”记成“没有成本”。

| 观察槽 | 实际任务/提交 | 缺陷及复现 | diff 触及职责 | 共同写入状态 | 最小定向验证 | 完整验证/额外返工 | 小改是否要求广泛理解 | 触发结果 |
|---|---|---|---|---|---|---|---|---|
| 1 | 待实际任务 | 从 TASKS/TRACE 取 | 用 `git show -U0` 记录 | 从提交文件取 | 从 Done Report 取 | 从 Done Report 取 | 仅有明确任务记录才填写 | none/prepare/govern |
| 2 | 待实际任务 |  |  |  |  |  |  |  |
| 3 | 待实际任务 |  |  |  |  |  |  |  |
| 4 | 待实际任务 |  |  |  |  |  |  |  |
| 5 | 待实际任务 |  |  |  |  |  |  |  |

每个任务只做以下离线复查：

1. 从 TASKS 和 TRACE 确认它是已复现缺陷、文档任务还是明确例外；
2. 用 `git show --name-only --stat` 和 `git show -U0` 记录改动文件、函数与
   start/check/switch/done/Git/persist 等职责数；
3. 标出 TASKS、tasks.json、PROGRESS、TRACE、STATUS、HANDOFF 中哪些同时变化；
4. 从 Done Report 记录定向套件、完整 122 项套件、失败重跑和 deferred；
5. 只有 Done Report/TASKS 明确写出“为了小改必须理解多个无关区域”时，才记录
   广泛理解成本；不采集隐式 Agent 行为；
6. 第 3 个任务时做一次中期判定，第 5 个任务或任一硬触发出现时立即判定。

## 9. 治理触发阈值

以下阈值只决定是否重新评估，不自动授权生产代码变化。任何治理仍需单独任务、
冻结例外、边界测试和精确范围。

| 触发条件 | 可复查判据 | 最低响应 |
|---|---|---|
| 连续两个缺陷跨越多个生命周期职责 | 两个相邻的已复现缺陷任务，各自的 commit/test scenario 均涉及 start、check、switch、done、Git、persist 中至少两个 | `PREPARE`；若同一根因重复则申请 `GOVERN` |
| 修改 check 再次影响 done、Git 或任务状态 | check 的局部变更使 done/提交/状态测试失败，或产生不同健康结论，并有确定复现 | 立即 `PREPARE`；重复一次则 `GOVERN` |
| 同一状态存在两个判断或写入权威 | 两条独立可达路径对同一任务给出冲突状态、提交范围或成功结论；仅“多个函数能写文件”不算 | 立即申请受限 `GOVERN` |
| 局部规则无法通过局部测试验证 | 定向责任套件通过而完整套件发现跨区回归，或最小规则只能靠全套件表达；连续两次 | `PREPARE` 补边界契约测试 |
| Agent 为小改动必须理解大部分文件 | <=50 行内核增删的任务，TASKS/Done Report 明确记录需检查至少 6 个职责区才能安全修改；连续两次 | `PREPARE` |
| 回归成本明显拖慢维护 | 连续两个任务因跨边界失败重跑完整套件至少 3 次、defer 正常维护，或 Done Report 记录完整套件耗时超过定向套件 2 倍并成为阻塞 | `PREPARE`；持续到第 3 个任务则 `GOVERN` |
| legacy/compat 再获独立完成权威 | `finish`、`closeout`、`done-gate` 或其他兼容入口再次写出与 `done` 等价的完成事实或被正常指导调用为第二流程 | 立即 `GOVERN` |

## 10. 当前结论：OBSERVE

选择 **OBSERVE：继续观察，不启动重构**。

支持证据：

- 长度和函数数只是规模信号；
- 历史中存在跨边界耦合，但 7 个小提交只有 2 个跨两个命令处理器，尚不能证明
  小改动“经常”要求横跨内核；
- T-047 是一个真实跨边界修复包，但本基线之后尚无连续两个维护缺陷；
- 多状态文件和兼容写路径是明确的结构事实，但当前没有冲突结果、数据损坏或
  重复 Done 的复现；
- repository state、事务成功、Inspect 渲染和 TRACE 索引已经有明确模块边界；
- 122 项责任化核心测试已覆盖需要完整 Git 生命周期的行为；
- 当前没有回归成本拖慢维护的仓库记录；
- ADR-010 和 stabilization freeze 明确禁止用架构偏好代替缺陷证据。

所以现在既不启动内核重构，也不专门创建 PREPARE 测试任务。未来 3 至 5 个
真实维护任务按上表被动观察；只有阈值被仓库证据命中，才重新选择 PREPARE
或申请 GOVERN。
