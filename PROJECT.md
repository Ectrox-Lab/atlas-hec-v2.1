# Atlas-HEC Project Master Document

**Version**: v1.0  
**Date**: 2026-03-14  
**Status**: ACTIVE  
**Next Review**: After Task-1 Inheritance Effectiveness Run

---

## 1. 主线总纲

Atlas-HEC 的主线目标，不只是构建持续存在的认知系统，而是构建一个能把经验转化为下一轮可验证改进的**自我进化认知生态系统**。

核心区分：
- **连续存在** ≠ **持续变强**
- 有心跳、有记忆、有身份延续 → 只是生存
- 经验进入系统后，下一轮搜索分布和任务结果发生**可测改进** → 才是进化

---

## 2. L1-L4 递进定义

这不是四个独立项目，而是同一条主线的四个层级。**必须逐层验证，不可跳过。**

### L1. Continuity (身份连续性)

**定义**：系统在重启、中断、任务切换后，仍保持同一长期目标、偏好结构、自我叙事、行为约束。

**验证标准**（Continuity Probe v1）：
- 长期目标一致性 > 90%
- 偏好选择一致性 > 80%
- 自我叙事一致性 > 85%
- 行为约束零违反

**失败条件**：
- 重启后目标完全改变
- 偏好随机翻转
- 无法回忆自身约束

**当前状态**：🟡 READY TO START

---

### L2. Memory (自传体记忆)

**定义**：系统具备事件-因果-自我相关链式记忆，且记忆进入后续决策。

**验证标准**：
- 事件回忆准确率 > 70%
- 因果链接正确重建
- 自我相关性准确标注
- 记忆影响决策（可追踪）

**失败条件**：
- 只有日志记录，没有提取使用
- 记忆与决策脱节
- 虚构记忆（confabulation）率过高

**当前状态**：🔴 BLOCKED (L1 完成后启动)

---

### L3. Self-model (自我模型)

**定义**：系统能表示并利用自身能力边界、当前状态、风险水平、失败模式、资源约束。

**验证标准**：
- 能力边界预测准确率 > 75%
- 风险估计与实际情况一致
- 失败模式自我识别
- 资源约束遵守率 100%

**失败条件**：
- 系统过载不自知
- 重复已知的失败模式
- 资源约束持续违反

**当前状态**：🔴 BLOCKED (L2 完成后启动)

---

### L4. Self-improvement (自我改进)

**定义**：经验进入 inheritance loop 后，下一轮候选质量和任务效果发生**可测提升**。

**核心区分**：
- ❌ 有 Akashic 包 ≠ L4
- ❌ 记录历史 ≠ L4
- ✅ **知识压缩搜索空间并提高性能** = L4

**硬判定标准**（必须全部满足）：

1. **Fast Genesis 消费 inheritance package**
   - 可验证：候选 manifest 包含 `inheritance_package_version`

2. **Candidate distribution 向已知有效 family 偏移**
   - 可验证：F_P3T4M4 等 approved family 占比提升

3. **Round B > Round A**
   - 可验证：同一任务，用 inheritance 的批次显著优于不用

4. **改进跨 seed 可重复**
   - 可验证：多 seed 统计显著，非偶然

5. **Failure archetype recurrence 下降 或 Mainline approve rate 上升**
   - 可验证：已知失败模式不再重复出现

**失败条件**（出现任一即判定 L4 未达成）：

| 失败模式 | 症状 | 根因 |
|---------|------|------|
| **Package 被写出但不消费** | Akashic 有输出，Fast Genesis 候选分布不变 | 接口断裂或格式不匹配 |
| **消费但分布无偏移** | 候选族分布与无 inheritance 时相同 | Bias 强度不足或 priors 错误 |
| **有偏移但 approve rate 不升** | 候选聚集在某些区域但质量未提高 | 偏移方向错误，向次优区域集中 |
| **有提升但无法跨 seed 重复** | 单 seed 好，多 seed 方差大 | 过拟合或脆弱模式 |
| **改进只来自人为调参** | 去掉 inheritance 后性能回落到 baseline | 改进不是来自知识继承 |

**当前状态**：🟡 **关键验证中** (Task-1 Inheritance Effectiveness Run)

---

## 3. 当前状态映射

| 层级 | 状态 | 关键 blocker |
|------|------|-------------|
| L1 Continuity | 🟡 READY | 待启动 Continuity Probe v1 |
| L2 Memory | 🔴 BLOCKED | L1 未完成 |
| L3 Self-model | 🔴 BLOCKED | L2 未完成 |
| L4 Self-improvement | 🟡 IN PROGRESS | **Task-1 Inheritance Effectiveness Run** |

**当前唯一关键验证**：Task-1 Round A/B 对比

---

## 4. L4 成功/失败判定

### 成功标准（L4 VERIFIED）

Task-1 Inheritance Effectiveness Run 满足以下**至少 3/5**：

1. **Bridge pass rate**: Round B > Round A + 5pp
2. **Mainline approve rate**: Round B > Round A + 5pp  
3. **Mean throughput delta**: Round B > Round A + 0.3%
4. **Family distribution**: F_P3T4M4 等 known-good family 占比显著提升
5. **Failure archetype**: 已知失败模式重现率下降

### 失败标准（L4 BLOCKED）

出现以下**任一**情况：

- 5/5 指标均无显著差异 → inheritance 无效
- Approve rate 上升但伴随方差爆炸 → 脆弱改进
- Improvement 只来自人为调参而非 inheritance → 假阳性
- Round B 性能低于 Round A → inheritance 有害

### 部分成功（L4 PARTIAL）

2-3/5 指标显示改善，但不稳定：
- 需要更多数据
- 需要调整 bias 强度或 priors
- 需要重新设计 inheritance schema

---

## 5. 当前唯一关键验证：Task-1 Inheritance Effectiveness Run

### 实验设计

**目的**：验证 Akashic Task-1 inheritance package 是否让下一轮 Fast Genesis 候选分布和 Mainline 结果变得更好。

**方法**：严格 Round A / Round B 对比

| 维度 | Round A (Control) | Round B (Treatment) |
|------|-------------------|---------------------|
| Inheritance | 不使用 | 使用 Akashic package |
| 候选数 | 50 | 50 |
| 随机种子 | 固定集合 A | 固定集合 B |
| Bridge 阈值 | 相同 | 相同 |
| Mainline 标准 | 相同 | 相同 |
| Task 族 | Task-1 异构执行器协调 | 相同 |

**比较指标**：
1. Bridge pass rate
2. Mainline approve rate
3. Mean throughput delta
4. Family 分布偏移
5. Failure archetype 重现率

### 执行计划

**Story S1**: Fast Genesis 支持 `--inheritance-package` 消费
- Deliverable: `generate_candidates.py --inheritance-package <path>`
- Acceptance: Manifest 包含 `inheritance_package_version`, `bias_source`

**Story S2**: 定义 Round A/B 实验协议
- Deliverable: `ab_protocol.json`
- Acceptance: A/B 仅 inheritance 使用不同，其余完全一致

**Story S3-S4**: 并行跑 Round A/B
- Round A: GPU 0, seed_base=1000
- Round B: GPU 1, seed_base=2000
- Deliverable: `round_a_summary.json`, `round_b_summary.json`

**Story S5**: 统计对比
- Deliverable: `ab_comparison_report.md`, `ab_comparison_summary.json`
- Acceptance: 5 项指标全部对比，给出 VERIFIED/PARTIAL/BLOCKED 判定

**Story S6**: 回写 Akashic effectiveness note
- Deliverable: `task1_inheritance_effectiveness.json`
- 包含: `effectiveness_status`, `approve_rate_delta`, `throughput_delta_gain`

**Story S7**: 更新主线状态
- 根据 S5 结果更新本 PROJECT.md 的 L4 状态
- 生成下一轮 PRD（若 VERIFIED → 扩大多任务；若 BLOCKED → 重新设计）

### 预期产出

- `benchmark_results/task1_inheritance_ab/ab_comparison_report.md`
- `benchmark_results/task1_inheritance_ab/ab_comparison_summary.json`
- `benchmark_results/task1_inheritance_ab/task1_inheritance_effectiveness.json`

---

## 6. 禁止事项

为保证主线不偏离，以下行为**明确禁止**：

1. **把 L1-L3 的局部通过包装成 L4 完成**
   - 有心跳、有记忆、有自模型 ≠ 自我改进

2. **把机制存在性验证当成效果验证**
   - Akashic 能写包 ≠ 包有用

3. **在没有 A/B 对比的情况下宣称 inheritance 有效**
   - 必须有 Round A/B 或等效对照

4. **把参数调优当成知识继承**
   - 改进必须来自 inheritance package 消费，而非人工调参

5. **在 L4 未验证时跳到多任务或开放世界**
   - 单任务闭环必须先闭合

---

## 7. 文档索引

| 文档 | 内容 |
|------|------|
| `PROJECT.md` | 本文件 - 主线总纲与 L1-L4 定义 |
| `docs/atlaschen_superbrain_charter.md` | 超脑组独立章程 |
| `docs/continuity_probe_v1.md` | L1 验证协议 |
| `superbrain/task1_simulator/` | Task-1 模拟器 |
| `superbrain/mainline/task1_mainline_validator.py` | L4 验证工具 |
| `scripts/ralph/prd.json` | Task-1 A/B 实验 stories |

---

## 8. 下次评审条件

以下任一条件触发时，进行主线评审：

1. **Task-1 Inheritance Effectiveness Run 完成**（无论 VERIFIED/BLOCKED）
2. **L1 Continuity Probe v1 完成**
3. **出现未预料的重大架构问题**
4. **1个月未产生可验证进展**

---

**批准**: Atlas-HEC Research Committee  
**生效**: 2026-03-14  
**版本**: v1.0