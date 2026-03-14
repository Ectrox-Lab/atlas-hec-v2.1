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

## 12. S1 完成标准（锁死）

### 12.1 当前阶段判定

**主线已进入 execution bottleneck 阶段，不再是 conceptual bottleneck**

- ❌ 问题不再是"该做什么"
- ✅ 问题是"把 S1 做出来，让 L4 接受生死判定"

**执行原则**: 只做 S1，直到 Round A/B 能真正跑起来

### 12.2 S1 五大完成标准

#### 1. CLI 接口成立
```bash
generate_candidates.py \
  --inheritance-package task1_inheritance_package.json \
  --bias-toward-known-good 0.7 \
  --task-family task1 \
  --output round_b_candidates/
```

#### 2. 不传 package 时，行为与当前版本完全一致
- Round A 对照组必须纯净
- 无隐式 bias、无默认 package 加载
- 当前生成逻辑作为 baseline 冻结

#### 3. 传 package 后，manifest 必须记录
```json
{
  "inheritance_package_version": "v2.1",
  "bias_source": "task1_inheritance_package.json",
  "approved_family_hint": ["F_P3T4M4"],
  "blocked_signature_hint": ["S_...", "S_..."],
  "generation_mode": "inheritance_biased",
  "bias_strength": 0.7,
  "timestamp": "2026-03-14T12:00:00Z"
}
```

#### 4. 候选分布必须可观测地偏移
输出必须显示：
- `family_distribution.json`: 各 family 占比变化
- `generation_log.json`: 每个候选的 family 溯源
- known-good bias 生效证据
- blocked pattern 避让证据

#### 5. 生成逻辑必须可关闭
- bias 是可切换层，非硬编码
- `--bias-toward-known-good 0.0` = 纯探索模式
- 支持 future ablation study

### 12.3 S1 最小输出文件

S1 完成后必须生成：

```
round_b_candidates/
├── manifest.json              # 生成元数据
├── family_distribution.json   # family 占比统计
├── generation_log.json        # 逐候选生成记录
└── candidates/
    ├── candidate_001/
    │   ├── genotype.json
    │   └── metadata.json
    └── ...
```

### 12.4 现在不该做的事（冻结清单）

在 S1 完成前，**禁止**：

- ❌ 再扩写 PROJECT.md（本节是最后一次文档更新）
- ❌ 增加新 task family
- ❌ 扩展更多记忆层讨论
- ❌ 提前讨论 L2/L3 实现
- ❌ 开新的生物启发支线
- ❌ 优化非 S1 相关的代码路径
- ❌ 增加新的实验设计

**唯一允许的修改**: S1 实现代码 + 本节规格锁定

### 12.5 S1 完成后立即触发

S1 完成 → 立即执行：
1. Round A: 50 candidates (no package)
2. Round B: 50 candidates (with package)
3. 并行 GPU0/GPU1 执行
4. 生成报告 A + 报告 B
5. L4 生死判定

---

**批准**: Atlas-HEC Research Committee  
**生效**: 2026-03-14  
**版本**: v1.0 → **v1.1-S1-LOCKED**

---

## 9. 实验登记总表（长期维护）

下面只登记"重要实验 / 重要阶段变化"。每条至少保留：

- 实验名称
- 结论级别
- 关键结果
- 结果目录
- 关键文件

---

### 9.1 已归档参考线

**E-REF-001 AtlasChen Superbrain 归档线**

- **级别**: Archived Reference
- **结论**: 最小持续自我改进闭环、自维护、24h 稳定性已验证
- **结果目录**:
  - `experiments/superbrain/p5b/`
  - `experiments/superbrain/p6/`
- **关键文件**:
  - `SUPERBRAIN_FINAL_REPORT.md`
  - `SUPERBRAIN_STATUS.md`
  - `P6_24H_STATUS.md`

---

### 9.2 进化搜索线

**E-EVO-001 Step 1 Smoke Test**

- **级别**: PASS
- **结论**: 6→128 协议与跨轮编排可运行
- **结果目录**: `benchmark_results/step1_smoke/`
- **关键文件**:
  - `superbrain/evolution/round_controller.py`
  - `superbrain/evolution/lineage_tracker.py`
  - `superbrain/evolution/family_registry.py`

**E-EVO-002 Step 2 Family Emergence**

- **级别**: COMPLETE
- **结论**: Family emergence confirmed (Round 1-4)
- **结果目录**: `benchmark_results/step2_validation/`
- **关键文件**:
  - `STEP2_REPORT.md`
  - `round_1_summary.json` - `round_5_summary.json`
  - `round_1_families.json` - `round_5_families.json`
  - `round_1_elites.json` - `round_5_elites.json`

**E-EVO-003 Step 3 Convergence**

- **级别**: CONVERGING ACHIEVED
- **结论**: F_P3T4M4 dominant family emerged at Round 10
- **结果目录**: `benchmark_results/step3_round6_10/`
- **关键文件**:
  - `STEP3_REPORT.md`
  - `EVOLUTION_SEARCH_CONVERGENCE_REPORT.md`
  - `round_10_summary.json`
  - `round_10_families.json`
  - `round_10_elites.json`

---

### 9.3 P0 学习线

**E-P0-001 P0-4 Real Gradient Unblocked**

- **级别**: PASS
- **结论**: 真实梯度训练链打通，old `apply_noise()` 主路径被替换
- **关键结果**: RealUNetFull + backward() + update() 验证通过
- **结果目录**: `code-diffusion/benchmark_results/`
- **关键文件**:
  - `code-diffusion/src/training/mod.rs` (refactored)
  - `code-diffusion/src/models/realunet_full.rs`
  - `code-diffusion/tests/test_single_step_update.rs`
  - `code-diffusion/tests/test_loss_trend.rs`

**E-P0-002 P0-5 Mini Validation**

- **级别**: PASS
- **结论**: Mean improvement 5.17% > 5% threshold, 3/3 seeds positive
- **关键结果**: LR=0.01, 7500 steps, dim=512
- **结果目录**:
  - `benchmark_results/p0_5_mini_validation/`
  - `benchmark_results/p0_5_hyperparam_sweep/`
  - `benchmark_results/p0_5_final_validation/`
- **关键文件**:
  - `code-diffusion/src/bin/p0_5_mini_validation.rs`
  - `code-diffusion/src/bin/p0_5_hyperparam_sweep.rs`
  - `code-diffusion/src/bin/p0_5_final_validation.rs`
  - `summary.json`, `report.md`

---

### 9.4 Task-1 现实闭环线

**E-T1-001 Task-1 Simulator + Baseline**

- **级别**: PASS
- **结论**: Baseline 与 adaptive 可区分，improvement 可测
- **关键结果**: Baseline 18.67%, Adaptive 19.67%, +5.4%
- **结果目录**: `benchmark_results/task1_baseline/`
- **关键文件**:
  - `superbrain/task1_simulator/environment.py`
  - `superbrain/task1_simulator/schedulers.py`
  - `superbrain/task1_simulator/baseline_fast.py`
  - `superbrain/task1_simulator/adaptive_fast.py`
  - `baseline_v2.json`

**E-T1-002 Task-1 Bridge + Mainline Integration**

- **级别**: COMPLETE
- **结论**: Bridge 相对阈值、Mainline validator、Akashic Task-1 包已接入
- **结果目录**: `benchmark_results/task1_mainline/`
- **关键文件**:
  - `superbrain/bridge/bridge_scheduler.py` (Task-1 thresholds)
  - `superbrain/mainline/task1_mainline_validator.py`
  - `socs_universe_search/multiverse_engine/akashic_memory_v2.py` (Task1KnowledgeArchive)
  - `TASK1_REALITY_LOOP_STATUS.md`

**E-T1-003 Task-1 Inheritance Effectiveness Run**

- **级别**: COMPLETE (L4-v1)
- **结论**: **PARTIAL SUCCESS** - Inheritance mechanism works, drives exploration, but approve rate improvement insufficient
- **关键结果**:
  - Round A: 40.0% approve, +1.51% throughput
  - Round B: 51.6% approve (+11.6pp), +5.13% throughput
  - Ablation: 36.7% approve (validates bias layer)
- **判定**: 2/3 E-T1-003 criteria passed (throughput improved, archetype stable)
- **问题**: Improvement from novel family exploration, not stable family reuse
- **结果目录**: `benchmark_results/task1_inheritance/`

---

### 9.5 Heavy Mode / Phase C

**E-HM-001 Phase C 集成验证**

- **级别**: PLANNED
- **结论**: Fast-Forward scheduler 已实现，待验证真实加速效果
- **目标**: Fast-Forward acceleration ≥ 2×, False skip rate < 10%
- **关键文件**:
  - `superbrain/heavy_mode/causal_fast_forward.py`
  - `PHASE_C_VALIDATION_PLAN.md`

---

### 9.6 组合性与模块重用线

**E-COMP-001 组合性主线假设纳入**

- **级别**: ACTIVE HYPOTHESIS
- **结论**: 主线新增"有限核心能力 + 模块重用/路由/组合"假设
- **核心内容**:
  - 核心能力集合应尽量小而强
  - Task-specific skill 视为可被调用和组合的模块资产
  - 真正关键的是高效激活、抑制、路由与重组
- **结果目录**: `PROJECT.md` (本文档)

**E-COMP-002 Task-1 Compositional Reuse Validation**

- **级别**: PLANNED
- **目标**: 验证 Task-1 成功时，系统是在复用旧模块，还是在隐性重造结构
- **背景**: E-T1-003证明继承能改善性能，E-COMP-002追问：改善来自模块化复用还是隐性重造
- **验证方法**:
  - 候选 family 分布分析（Round A vs Round B）
  - 已知 good family (F_P3T4M4) 占比变化轨迹
  - 模块激活日志分析（哪些模块被复用、新模块生成率）
  - 候选基因型相似度分析（Jaccard距离）
- **通过信号**:
  - Round B中F_P3T4M4及其变体占比>60%
  - 新模块生成率<30%，复用率>70%
  - 相似候选聚集在已知good family周边而非分散探索
- **失败信号**:
  - Round B生成大量全新family，与Round A无继承关系
  - 模块激活模式显示Task-1专用模块被重新创造而非复用
  - F_P3T4M4占比未显著提升
- **关键问题**: Superbrain shows "inheritance-driven exploration bias", NOT "inheritance-driven compositional reuse"
- **判定**: 1/4 E-COMP-002 criteria passed
- **根因**: Family-level bias too coarse, drives exploration to nearby variants
- **下一步**: L4-v2 with mechanism-level inheritance + anti-leakage bias
- **结果目录**: `benchmark_results/task1_compositional_analysis/` (待创建)
- **依赖**: E-T1-003 完成后启动
- **与E-T1-003关系**: E-T1-003问"继承是否有效"，E-COMP-002问"有效是否来自模块化复用"

---

## 10. 当前系统状态总览

### 10.1 精确状态定义

| 组件 | 状态 | 精确定义 |
|------|------|----------|
| **L4 Hypothesis** | 🟢 DEFINED | E-T1-003 + E-COMP-002 实验对设计完成，阈值明确 |
| **Task-1 Reality Loop** | 🟢 CLOSED | Bridge → Mainline → Akashic 链路已打通并验证 |
| **Inheritance Effectiveness Exp** | 🟢 DESIGNED | Round A/B 对比实验设计完成，判定标准量化 |
| **Compositional Reuse Exp** | 🟢 DESIGNED | 模块复用验证方案完成，与E-T1-003绑定执行 |
| **Execution Blocker** | 🔴 **S1 ONLY** | Fast Genesis inheritance consumption 未实现 |

### 10.2 L4 验证实验对设计

**核心绑定逻辑**: E-T1-003 与 E-COMP-002 必须同时回答，缺一不可

| 实验 | 核心问题 | 验证目标 | 关键指标 |
|------|----------|----------|----------|
| **E-T1-003** | 继承是否让下一轮更好？ | Self-improvement Effectiveness | approve rate↑, throughput↑, archetype↓ |
| **E-COMP-002** | 改善是否来自模块复用？ | Compositionality Validity | F_P3T4M4占比>60%, reuse rate>70%, new<30% |

**判定矩阵**:
- ✅ **L4 FULLY VALIDATED**: E-T1-003 PASS + E-COMP-002 PASS → 系统靠组合变强
- ⚠️ **L4 PARTIAL**: E-T1-003 PASS + E-COMP-002 FAIL → 变强但非组合方式（结构膨胀）
- ❌ **L4 FAILED**: E-T1-003 FAIL → 无论复用是否发生，自我改进不成立

### 10.3 关键阈值汇总

| 指标 | E-T1-003 阈值 | E-COMP-002 阈值 |
|------|---------------|-----------------|
| Round B vs A | 3/5 metrics improve | - |
| F_P3T4M4占比 | > Round A +20% | >60% in Round B |
| 复用率 | - | >70% |
| 新模块泄漏 | - | <30% |
| 跨种子重复性 | σ/μ < 0.1 | - |

### 10.4 执行后报告分离策略

**报告 A: L4 Effectiveness** (回答会不会变强)
- Round B vs Round A 对比表
- approve rate / throughput delta / archetype recurrence 改善统计
- 统计显著性检验 (t-test, effect size)

**报告 B: Compositional Reuse** (回答是不是用对的方式变强)
- successful candidates family 分布溯源
- reuse rate 计算（模块激活日志分析）
- new family / new module leakage 量化
- 是否依赖新增专用结构判定

---

| 层级 | 状态 | 关键证据 |
|------|------|----------|
| **L1 Continuity** | 🟡 READY | Continuity Probe v1 待启动 |
| **L2 Memory** | 🔴 BLOCKED | L1 完成后启动 |
| **L3 Self-model** | 🔴 BLOCKED | L2 完成后启动 |
| **L4 Self-improvement** | 🔴 **FAILED (v1)** | **E-T1-003 partial, E-COMP-002 failed - v2 required** |

### 10.5 已成立

- ✅ 进化搜索引擎可运行并出现收敛家族 (E-EVO-003)
- ✅ Task-1 第一现实验证链已闭合 (E-T1-002)
- ✅ P0 真实梯度训练链已打通并通过 P0-5 (E-P0-002)
- ✅ 异构 CPU + GPU 执行 PoC 已成立
- ✅ Akashic 可写 Task-1 继承包
- ✅ E-T1-003 / E-COMP-002 实验对执行完成 (L4-v1)
- ✅ Inheritance mechanism works (consumption + distribution shift)
- ⚠️ **But**: Drives exploration, NOT compositional reuse

### 10.6 尚未成立

- 🔴 **L4 Self-improvement** (v1 FAILED) - Inheritance drives exploration, not reuse
- 🔴 **Compositional Reuse** (v1 FAILED) - F_P3T4M4 share dropped, leakage increased
- 🔴 **Inheritance Effectiveness** (v1 PARTIAL) - Throughput improved but not approve rate
- 🟡 **L4-v2** - Mechanism-level inheritance + anti-leakage bias (planned)
- 🔴 多任务现实闭环尚未建立
- 🔴 真异构执行体尚未完全闭合到主任务引擎

---

## 11. 当前最短行动序列

### 11.1 主线收敛状态

**当前已从"要做什么"进入"只差把 S1 接通就能判生死"阶段**

唯一执行阻塞点：**S1 - Fast Genesis inheritance consumption**

### 11.2 最短序列

```
S1: Fast Genesis --inheritance-package 实现 ─────┐
                                                ↓
S2: Round A (50 candidates, no package) ────┐   │
                                             │   │
S3: Round B (50 candidates, with package) ───┼───┘
                                             ↓
S4: 并行执行 GPU0/GPU1 分离                   │
                                             ↓
S5: 生成报告 A (Effectiveness)               │
    生成报告 B (Compositional Reuse)         │
                                             ↓
S6: 判定 L4 / P4 是否成立 ◄──────────────────┘
     ├── ✅ 成立 → 进入 Task-1 self-improvement loop
     └── ❌ 失败 → 回查 Akashic ↔ Fast Genesis 接口
```

### 11.3 S1 关键实现点

```python
# Fast Genesis 需要支持
--inheritance-package PATH  # CLI flag
--inheritance-bias FLOAT    # 分布偏置强度 (默认 0.7)

# 内部逻辑
if inheritance_package:
    known_families = load_package_families()  # F_P3T4M4 etc.
    candidate_gen = bias_toward_known(known_families, bias_strength)
else:
    candidate_gen = uniform_exploration()
```

### 11.4 执行策略

- **不再扩散**: 冻结所有非 S1 相关开发
- **不再新增概念**: 当前实验对足够判定 L4
- **单一焦点**: 全部工程资源投入 S1 实现
- **执行后双报告**: 严格分离 Effectiveness vs Compositional Reuse 分析

---

**批准**: Atlas-HEC Research Committee  
**生效**: 2026-03-14  
**版本**: v1.0

---

## 13. L4-v1 执行结果与判定

### 13.1 执行摘要

| 实验 | 状态 | 得分 | 关键发现 |
|------|------|------|----------|
| **E-T1-003** | Partial | 2/3 | Throughput improved (+5.13% vs +1.51%), approve rate marginal (+11.6pp) |
| **E-COMP-002** | Failed | 1/4 | Improvement from novel families, NOT compositional reuse |
| **Overall** | **FAILED** | 3/7 | Inheritance drives exploration, not stable reuse |

### 13.2 核心结论

> **当前 inheritance 表现出 "exploration bias"，而非 "compositional reuse-based self-improvement"**

**成立的部分**:
- ✅ Inheritance package 被消费
- ✅ 候选分布确实改变
- ✅ Raw throughput 提升显著

**不成立的部分**:
- ❌ 提升不是来自既有稳定 family 的复用
- ❌ F_P3T4M4 占比下降 (13.3% → 9.7%)
- ❌ Reuse rate 下降 (70.0% → 51.6%)
- ❌ Leakage 上升 (0% → 12.9%，P1/P4/T5 家族)

### 13.3 根因分析

**问题**: Inheritance package 语义太粗（family-level bias）

```json
// Current (v1) - 问题所在
{
  "approved_families": ["F_P3T4M4", "F_P2T3M3"],
  "generator_priors": {"trust_decay_range": [0.05, 0.15]}
}
```

**后果**: 
- 推动候选向 "已知 family 的邻近变体" 跳跃
- 允许向未测试区域（P4, T5）结构性扩张
- 不编码 mechanism-level 可复用模式

### 13.4 两刀修复（不扩散）

**刀 1**: Akashic Package Schema  
**From**: Family-level prior  
**To**: Mechanism/routing prior (`stable_patterns`, `blocked_motifs`, `route_constraints`)

**刀 2**: Fast Genesis Anti-Leakage  
**Add**: `anti_structural_expansion_penalty` 对以下候选降权：
- 超出已知 family 邻域太远
- 引入新的高复杂度组合但没有历史支持
- 违反现有 stable path 的路由模式
- P1/P4/T5 异常扩张

---

## 14. L4-v2 计划

### 14.1 目标

| 指标 | L4-v1 (Round B) | L4-v2 Target |
|------|-----------------|--------------|
| Approve rate | 51.6% | > 60% |
| Reuse rate | 51.6% | > 70% |
| F_P3T4M4 share | 9.7% | > 30% |
| Leakage | 12.9% | < 8% |
| Winners from stable paths | 22.6% | > 60% |

### 14.2 实验结构（不变）

- **Round A-v2**: No inheritance (control)
- **Round B-v2**: Inheritance package v2 + anti-leakage
- **Ablation-v2**: Package loaded, bias=0.0, anti-leakage=0.0
- **Sample**: 30 candidates per round, stratified
- **Evaluation**: Bridge → Mainline (same thresholds)
- **追加约束**: Round B-v2 throughput ≥ Round A-v2, Ablation-v2 ≡ Round A-v2

### 14.3 详细规格

见 `L4_V2_SPEC.md`:
- Akashic package v2 schema (mechanism-level fields)
- Fast Genesis anti-leakage CLI parameters
- Anti-leakage scoring function
- Ablation plan (mechanism-only vs penalty-only)

### 14.4 实现顺序（LOCKED）

1. Akashic schema v2 (mechanism-level)
2. Fast Genesis anti-leakage (CLI + scoring)
3. L4-v2 A/B/Ablation (execute)
4. Post-hoc ablation (mechanism vs penalty)

### 14.3 关键修改

| 组件 | L4-v1 | L4-v2 |
|------|-------|-------|
| Akashic output | Family list | Mechanism patterns + routing constraints |
| Fast Genesis bias | toward-known-good | toward-known-good + anti-leakage |
| Bias strength | 0.7 | 0.6 (conservative) |
| Leakage penalty | None | 0.3-0.4 per novel motif |

### 14.4 判定标准（不变）

**L4-v2 FULLY VALIDATED**:
- Approve rate B > A + 5pp
- Reuse rate > 60%
- Leakage < 10%
- F_P3T4M4 share > 25%
- Winners from stable paths > 50%

---

## 15. 主线状态总结

### 当前精确状态

| 层级 | 状态 | 说明 |
|------|------|------|
| **L0** | ✅ Running | Ralph 外骨骼 |
| **L1-L3** | 🔴 Blocked | 等待 L4 确立 |
| **L4-v1** | 🔴 **FAILED** | Exploration bias confirmed, reuse not established |
| **L4-v2** | 🟡 Planned | Mechanism-level inheritance + anti-leakage |

### 关键认知更新

> **这不是"L4 不可能"的证据，而是"当前 inheritance 语义不对"的信号。**

- Inheritance **mechanism** works (consumption → distribution shift → throughput gain)
- Inheritance **semantics** wrong (family-level → exploration; need mechanism-level → reuse)
- Fix scope: Akashic output schema + Fast Genesis bias logic
- **No architecture diffusion required**

---

**批准**: Atlas-HEC Research Committee  
**生效**: 2026-03-14  
**版本**: v1.1 → **v2.0-L4V2-PLANNED**
