# SOCS Octopus Mainline Program

## 一句话定位

> 这是一个只负责主线实验推进的自动研究循环器。
> 它自动跑实验、比结果、诊断失败、写报告、产出提案。
> 它不直接修改核心架构。

## 当前主线优先级

自动循环只处理这 3 条：

### Track A: OctopusLike Smoke
- **目标**: 验证高 CWCI 是否转化为开放世界预测力
- **场景**: RegimeShiftFrequent, ResourceScarcity, HighCoordinationDemand
- **对照组**: OctopusLike, ModularLattice, RandomSparse

### Track B: OQS Gate 1.5
- **目标**: 只验证最小修正是否有效
- **修正点仅限**: division-of-labour, lineage initialization, culling
- **不扩大范围**

### Track C: Mainline Reporting
- **目标**: 自动产出当前主线状态
- **自动给出下一步推荐**
- **自动更新 hypothesis tree**

## 自动循环边界

### ✅ 允许自动做
- 跑实验脚本
- 聚合结果
- 判定 PASS / PARTIAL / FAIL
- 输出 failure mode
- 生成 smoke 报告
- 生成 proposal 草案
- 更新 status_tracker.json

### ❌ 不允许自动做
- 改 SOCS 核心运行时
- 改 Three-Layer Memory 护栏
- 改 Archive 访问边界
- 改评分标准
- 改最终主线结论口径
- 直接 merge 架构改动

## 主循环顺序

每一轮只执行这个固定顺序：

```
Step 1: 跑 OctopusLike Smoke
Step 2: 跑 OQS Gate 1.5
Step 3: 聚合结果
Step 4: 做 triage
Step 5: 写 mainline report
Step 6: 产出 proposal，等待人工审核
```

## 停机条件

自动循环必须在以下情况停止，并要求人工介入：

1. smoke 连续 2 轮 FAIL
2. OQS 连续 2 轮 FAIL
3. proposal 数量超过 3 个还未审核
4. 结果相互矛盾，无法定位 failure mode
5. 出现评分标准被误改
6. 检测到核心架构文件被自动修改

## 输出格式

### A. reports/octopus_smoke_report.md
必须包含：
- family × scenario × seed 结果表
- Octopus / Lattice / Random 对比
- Recovery / Energy / Coordination 三条结论
- PASS / PARTIAL / FAIL
- 最准确一句话

### B. reports/oqs_gate15_report.md
必须包含：
- Gate 1 vs Gate 1.5 对比
- 三个修正项是否生效
- 是否仍有 queen bottleneck
- first failure mode 是否变化
- PASS / PARTIAL / FAIL

### C. reports/mainline_status.md
必须包含：
- O1 当前状态
- OQS 当前状态
- BeeHive 当前状态
- 下一步推荐
- 当前主线 blocker

## 提案模板

所有自动提案都只能写进 `proposals/pending/`

```markdown
# Proposal ID: L4_xxx

## Context
What failed or what is uncertain.

## Evidence
Exact metrics / scenarios / seeds.

## First failure mode
Single most likely bottleneck.

## Minimal proposed edit
At most 1-3 changes.

## Expected effect
What should improve if this is correct.

## Risk
What could be confounded or broken.

## Human decision needed
[ ] APPROVE  [ ] REJECT  [ ] POSTPONE
```

## 执行口径

这个自动循环器不是为了"自动产生超脑"，而是为了：
- 自动推进主线假设
- 自动收敛实验结果
- 自动定位 first failure mode
- 自动把人类从机械研究协调里解放出来

## 当前状态

- **O1 OctopusLike**: Gate 2 PASSED → Ready for smoke test
- **OQS**: Gate 1 PARTIAL → Needs minimal corrections
- **BeeHiveLike**: Defined → Waiting for mainline convergence
