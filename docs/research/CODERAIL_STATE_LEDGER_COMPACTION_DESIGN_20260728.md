# CodeRail 状态账本压缩设计

日期：2026-07-28  
任务：T-050  
状态：仅设计，不实施

## 1. 决策摘要

`.coderail/tasks.json` 应继续作为当前任务和故障恢复的补充元数据，而不应
承担已完成任务的永久历史存储。已完成历史的仓库权威仍是
`docs/PROGRESS.md` 与 `docs/TRACELOG.jsonl`；`docs/TASKS.md` 只保存热任务，
`docs/CODERAIL_STATUS.md` 只是可重建投影。

未来若单独获准执行压缩，建议删除满足资格门的整个已关闭任务元数据项，
而不是长期维护另一种“半关闭”结构。当前任务不删除任何账本条目，不修改
CodeRail 内核，也不新增命令、hook、遥测或监控。

## 2. 可复现基线

基线锚点是 T-049 完成提交 `09ca9d2`。选择该提交是为了排除 T-050 启动后
自然新增的活动任务元数据。

| 指标 | T-049 完成后 |
| --- | ---: |
| `.coderail/tasks.json` Git blob 字节数 | 194,449 |
| 元数据任务项 | 47 |
| 含 baseline 文件记录的任务项 | 10 |
| baseline 文件记录总数 | 620 |
| 拥有关系字段的任务项 | 2 |
| 同时拥有 PROGRESS 和 verify TRACE 的任务项 | 47 |

最大三项分别是：

| 任务 | baseline 文件记录 | 主要来源 |
| --- | ---: | --- |
| T-041 | 257 | Workflow Lab 评估结果 |
| T-034 | 160 | Workflow Lab 评估结果 |
| T-031 | 159 | Workflow Lab 评估结果 |

三项合计 576 条，占全部 baseline 文件记录的 92.9%。这是数据分布事实，
不是单凭文件大小授权治理的理由。

复现命令（PowerShell）：

```powershell
git cat-file -s 09ca9d2:.coderail/tasks.json
$raw = git show 09ca9d2:.coderail/tasks.json
$ledger = $raw | ConvertFrom-Json
@($ledger.PSObject.Properties).Count
($ledger.PSObject.Properties |
  ForEach-Object { @($_.Value.baseline.files).Count } |
  Measure-Object -Sum).Sum
```

用当前仓库核对已完成证据：

```powershell
Select-String -Path docs/PROGRESS.md -Pattern 'T-041'
Select-String -Path docs/TRACELOG.jsonl -Pattern '"type": "verify".*"task": "T-041"'
Select-String -Path docs/TRACELOG.jsonl -Pattern '"task": "T-046".*"depends_on"'
```

## 3. 状态权威

| 文件 | 权威职责 | 是否保存已完成历史 | 压缩约束 |
| --- | --- | --- | --- |
| `docs/TASKS.md` | 当前 active、queued、paused、blocked、reopened 所有权 | 否 | 热任务不得压缩 |
| `docs/PROGRESS.md` | 已完成任务的可读摘要和验证结果 | 是 | 缺失对应条目时拒绝压缩 |
| `docs/TRACELOG.jsonl` | verify 事实、显式关系和可追溯事件 | 是 | 缺失验证或唯一关系事实时拒绝压缩 |
| `docs/TRACE_INDEX.md` | TRACE 的可重建索引 | 否 | 压缩后必须可重建且健康 |
| `docs/CODERAIL_STATUS.md` | Inspect 的时点投影 | 否 | 不得作为迁移输入权威 |
| `.coderail/tasks.json` | 当前任务、切换、暂停和恢复所需补充元数据 | 否 | 只保留仍有运行时用途的项 |
| `.coderail/pending_close.json` | 未完成收口事务的精确恢复快照 | 否 | 存在时禁止压缩相关任务 |

该分工延续 ADR-011 和 ADR-012，不建立新的判断或写入权威。

## 4. 字段观察

当前 47 项元数据可能包含：

- `verify`：42 项
- `accept`：42 项
- `tests`：32 项
- `baseline`：47 项，其中 10 项的 `files` 非空
- `display_id`：20 项
- `pause`：6 项
- `dirty_fork`：6 项
- `relations`：2 项

这些字段对活动、暂停或恢复中的任务有直接用途；任务完成且 durable
证据齐备后，其历史价值已由 PROGRESS 和 TRACE 承担。

T-046 的 `depends_on: T-045` 和 T-047 的 `depends_on: T-046` 已存在于
TRACE 的 accepted decision 事件中。因此当前没有发现只能从
`.coderail/tasks.json` 读取的独立关系事实。迁移前仍必须逐项重新核对，
不能把这次抽样结论写成永久假设。

## 5. 压缩资格门

一个任务只有同时满足下列条件，才可从 `.coderail/tasks.json` 删除：

1. 不在 TASKS 的 active、queued、paused、blocked 或 reopened 集合中。
2. PROGRESS 存在同一内部任务 ID 的完成条目，并包含验证结果。
3. TRACE 至少存在同一任务 ID 的 verify 事实。
4. 元数据中的 `depends_on`、`blocks`、`supersedes` 等关系已由 TRACE 的
   显式事件承载，且 Trace Doctor 能解析。
5. 不存在该任务的 `COMMIT_PENDING`、`closed_pending` 或
   `.coderail/pending_close.json` 恢复事务。
6. 不存在只保存在 metadata 中、仍被 Inspect、编号或任务图需要的事实。
7. 压缩与 PROGRESS、TRACE、TASKS、STATUS 更新处于一个精确 Git 提交中。

任一条件不满足都必须拒绝压缩，不允许用“文件太大”覆盖证据缺口。

### 明确拒绝情形

- TASKS 与 PROGRESS 对任务状态意见不一致。
- PROGRESS 有条目但 TRACE 没有 verify 事实，或反之。
- 关系只在 `.coderail/tasks.json` 中出现。
- 当前存在暂停、脏分叉、手工提交或收口恢复需要。
- 压缩导致下一任务编号回退或复用。
- Inspect 只能依靠即将删除的数据得出当前状态。

## 6. 保留规则

| 任务状态 | `.coderail/tasks.json` 策略 |
| --- | --- |
| active / queued / paused / blocked / reopened | 保留完整元数据 |
| commit pending / closeout recovery | 保留完整恢复数据，禁止压缩 |
| closed，但未通过资格门 | 原样保留并报告缺口 |
| closed，已通过资格门 | 删除整个任务项 |

选择“删除合格项”而不是保留 `display_id` 或简化的 closed 记录，有三个
原因：

1. TASKS、PROGRESS、TRACE 已共同保证编号不复用。
2. 简化 closed 结构会形成第三种长期 schema 和新的兼容负担。
3. 若关系仍有保留必要，应先进入 TRACE，而不是让 metadata 成为隐蔽权威。

当没有热任务和恢复事务时，理论下界可以接近空 JSON 对象。这个下界只是
一致性结果，不是大小 KPI，也不是要求立即实现的目标。

## 7. 一次性迁移方案

未来执行必须建立新的 CodeRail 数据维护任务，并与任何内核修改分开：

1. 记录迁移前提交、账本字节数、任务项数和 baseline 文件记录数。
2. 用现有 Git、TASKS、PROGRESS、TRACE 生成逐任务资格表；不新增运行时
   命令或遥测。
3. 对缺失的关系历史，只能先用现有 `coderail link` 记录真实关系；不得
   推测或补造事实。
4. 只编辑 `.coderail/tasks.json`，删除通过全部资格门的 closed 项。
5. 运行完整验证并比较压缩前后的任务编号、Inspect 状态和任务图。
6. 使用唯一 `coderail done` 创建精确范围提交，不夹带内核或测试改动。
7. 在 Done Report 中记录删除项、保留项、拒绝原因和前后尺寸。

一次性数据迁移成功，并不自动授权修改 `done` 使其持续自动压缩。是否需要
自动压缩，必须根据后续增长和维护伤害另行立项。

## 8. 验证协议

迁移任务至少执行：

```text
python tests/test_structure.py
python scripts/doctor.py --target .
python .coderail/coderail.py check
python .coderail/coderail.py inspect --no-write
python scripts/trace_doctor.py --target .
git diff --check
```

还必须人工核对：

- 压缩前后计算出的下一个内部任务 ID 相同。
- T-046 -> T-045 与 T-047 -> T-046 关系仍可由 TRACE 重建。
- TASKS 中所有热任务完整保留。
- PROGRESS 和 TRACE 的历史条目没有变化。
- `scripts/**`、`tests/**` 和其他生产边界没有变化。
- 工作树在 `coderail done` 后干净。

## 9. 回滚

压缩必须是独立、纯数据提交。回滚时使用普通 Git revert 恢复该提交中的
`.coderail/tasks.json`，然后重新运行 Doctor、Inspect、Trace Doctor 和
核心测试。不得从 PROGRESS 或 TRACE 反向猜测完整 baseline，也不得改写
历史提交。

如果迁移后首次正常任务出现编号复用、关系缺失、Inspect 漂移或恢复失败，
应立即停止继续压缩并回滚数据提交，再把现象作为独立缺陷处理。

## 10. 触发与停止条件

允许申请一次性数据压缩的触发条件：

- 已关闭元数据持续占用主要账本体积，并已逐项证明 durable 历史齐备。
- Agent 为读取当前任务反复加载大量已关闭 baseline。
- tasks.json 的合并冲突或审查噪声明显拖慢正常维护。
- 现有 Doctor 已持续提示热任务或上下文增长，而不是只有字节数上涨。

不得触发的情况：

- 只有“194 KB 看起来大”或任务项数量上涨。
- 仍有历史验证、关系或恢复权威缺口。
- 需要同时修改 `scripts/coderail.py` 才能完成一次性数据清理。

T-049 收口曾在 Windows 上因 660 个精确安全路径触发命令行长度限制，并
通过现有 manual commit + `done --resume` 协议恢复。该现象属于精确暂存
路径的可扩展性问题，不是旧 metadata 体积导致，因此不作为本压缩设计的
实施证据；若再次发生，应作为独立缺陷立项。

## 11. 当前结论

**DESIGN ONLY**：账本权威分工和安全压缩资格门已经可以定义，且 T-049
锚点上的 47 个 metadata 任务均能找到 PROGRESS 与 verify TRACE；两个
显式依赖也已在 TRACE 中。但本任务不执行删除，也不授权持续自动压缩。
下一步只有在仓库所有者另行批准数据迁移任务后，才能按本设计逐项审计并
压缩。
