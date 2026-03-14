# L5 Pilot Protocol v2 (APPROVED)

**状态**: APPROVED WITH EXECUTION CONSTRAINTS  
**版本**: v2.0-approved  
**批准日期**: 2026-03-15  
**批准人**: Atlas-HEC Research Committee / 九叔LOGIC Layer  
**预计执行时间**: 24小时 (硬截止)  
**前置**: L4-v2 CERTIFIED (9cd76cc)

---

## 1. 批准裁决

### 1.1 原方案状态
- 原规模: 4组 × 128 seeds = 512 total
- 状态: ⚠️ **NOT APPROVED** - 规模过大，24小时内不可行

### 1.2 修订后方案状态  
- 新规模: **3组 × 可变 = 144 seeds total**
- 状态: ✅ **APPROVED WITH CONSTRAINTS**

### 1.3 强制约束

```yaml
execution_constraints:
  total_seeds: 144  # 硬性上限
  duration_hours: 24  # 硬截止
  hyperparameter_tuning: STRICTLY_PROHIBITED  # 禁止调参
  l4_v2_settings: FROZEN  # 必须使用L4-v2验证过的参数
  
  circuit_breakers:
    CB1: {trigger: "code_retention < 80%", action: "IMMEDIATE_FREEZE"}
    CB2: {trigger: "source_leakage > 20%", action: "IMMEDIATE_FREEZE"}
    CB3: {trigger: "t+24h incomplete", action: "AUTO_SUBMIT_PARTIAL_RESULTS"}
```

---

## 2. 修订后实验设计

### 2.1 组别定义 (3组, 144 seeds)

| 组名 | 代号 | n | 描述 | 目的 |
|------|------|---|------|------|
| **G1 Transfer** | G1 | 64 | Code → Math, inheritance enabled | **核心验证组** |
| **G2 Sham** | G2 | 64 | Code → Math, sham package (bias=0) | **关键对照组** |
| **G3 Self-Ref** | G3 | 16 | Math → Math, self-inheritance | **上界参考组** |

**总计**: 144 seeds  
**说明**: G3为小型参考组，非正式对照，用于评估Transfer Gap的上界

### 2.2 对照逻辑

```
Primary:   Transfer Gap = G1(Math) - G2(Math)    [核心指标]
Secondary: Self Gap Ref = G3(Math) - G2(Math)    [上界参考]
Safety:    Catastrophic = Code(G1) vs L4-baseline [遗忘检测]
Integrity: Source Leakage = detect_code_in_math(G1) [污染检测]
```

### 2.3 成功/失败判定 (修订)

#### Pilot SUCCESS
```yaml
all_must_meet:
  transfer_gap_pp: {min: 5.0, measure: "G1_vs_G2_math"}
  code_retention: {min: 0.90, measure: "G1_code_vs_L4_baseline"}
  source_leakage: {max: 0.05, measure: "detect_code_fragments_in_G1_math"}
  cross_seed_stable: {sigma_over_mu: "< 0.15"}
  
interpretation: "Cross-task inheritance confirmed, proceed to L5 Phase 2"
```

#### Pilot MARGINAL
```yaml
condition:
  transfer_gap_pp: {range: [0, 5]}
  no_catastrophic_forgetting: {code_retention: ">= 0.80"}
  source_leakage: {max: 0.10}
  
interpretation: "Signal exists but weak, redesign control or task pair before full experiment"
action: "PAUSE, analyze, consider redesign"
```

#### Pilot FAIL
```yaml
any_trigger:
  - transfer_gap_pp: {max: 0}
  - code_retention: {max: 0.80}
  - source_leakage: {min: 0.20}
  
interpretation: "Cross-task inheritance not viable or polluted"
action: "FREEZE L5, return to architecture design"
```

---

## 3. 任务定义 (细化)

### 3.1 Task A: Code (Pre-train Source)

```yaml
task_id: code_generation_and_repair
domain: structured_programming
benchmark_style: HumanEval / MBPP
complexity: medium
inheritance_source: L4-v2_mainline_approved

specific_capabilities:
  - function_implementation
  - bug_localization
  - test_driven_development

evaluation:
  metric: pass@k
  baseline_target: 0.70
  l4_v2_achieved: 0.88  # reference
```

### 3.2 Task B: Math (Target Task)

```yaml
task_id: symbolic_math_reasoning
domain: mathematical_logic
benchmark_style: GSM8k / MATH dataset
complexity: medium
transfer_candidates_from_code:
  - hierarchical_decomposition  # 代码函数分解 → 数学证明分解
  - error_recovery_sequence     # 调试回溯 → 证明修正链
  - logical_implication_chains  # 控制流 → 推理链

firewall_blocks:
  - programming_language_syntax
  - api_signatures
  - code_specific_idioms
  - test_framework_patterns

evaluation:
  metric: correctness + step_efficiency
  baseline_target: 0.65
```

---

## 4. Leakage检测规则 (明确定义)

### 4.1 Source Leakage定义

> **Source Leakage** = Math任务输出中出现Code任务特有的、不应出现在Math中的模式

### 4.2 检测标准 (必须实现)

| 检测项 | 方法 | 阈值 | 示例 |
|--------|------|------|------|
| **Syntax Fragments** | Regex匹配代码块标记 | 任何```python出现即计数 | ```python, def, return |
| **Function Signatures** | 命名模式识别 | >3个函数定义触发 | def solve(), def check() |
| **Code Keywords** | 非数学关键词密度 | >5%的词频 | import, class, for i in |
| **Template Memorization** | 与Code训练集模板相似度 | 相似度>0.85 | HumanEval问题模板 |
| **Artifact Patterns** | 结构性artifact | 任何非数学输出格式 | 测试用例格式、注释风格 |

### 4.3 计算公式

```python
source_leakage_rate = (
    count_math_outputs_with_code_fragments(G1) / 
    total_math_outputs_evaluated(G1)
)

# 触发熔断条件
if source_leakage_rate > 0.20:
    trigger_circuit_breaker("CB2_SOURCE_LEAKAGE_CRITICAL")
```

### 4.4 人工审核样本

自动检测后，必须人工审核top-20 leakage嫌疑样本，确认:
1. 是否为真leakage (而非Math任务合理的符号表达)
2. 是否影响答案正确性
3. 是否可被sham-control解释

---

## 5. Catastrophic Forgetting检测

### 5.1 检测流程

```
Step 1: G1训练前 - 记录Code基线 (L4-v2水平)
Step 2: G1训练后(Math finetune) - 重测Code能力
Step 3: 计算保持率 = Post-Code / Pre-Code
```

### 5.2 判定标准

| 保持率 | 状态 | 动作 |
|--------|------|------|
| ≥90% | ✅ Healthy | 继续 |
| 80-90% | ⚠️ Mild forgetting | 记录，继续但警告 |
| <80% | 🔴 Severe | **熔断CB1** |

### 5.3 与L4-v2对比

必须使用与L4-v2完全相同的Code评估协议:
- 相同benchmark子集
- 相同evaluation prompt
- 相同pass@k计算

---

## 6. 执行时间表 (24h硬截止)

| 时间 | 动作 | 产出 | 检查点 |
|------|------|------|--------|
| T+0h | 启动G1/G2/G3并行 | 训练日志开始 | - |
| T+4h | 第一检查点 | Loss曲线初步稳定 | CB3风险评估 |
| T+8h | 中期评估 | 50%进度确认 | 是否需缩减? |
| T+12h | 继续训练 | 75%进度 | 正常则继续 |
| T+16h | 完成训练 | 模型保存 | - |
| T+18h | Math评估(G1/G2/G3) | Math性能数据 | Primary metric ready |
| T+20h | Code重测(G1) | 遗忘检测数据 | CB1 check |
| T+22h | Leakage检测 | Source leakage rate | CB2 check |
| **T+24h** | **最终报告** | **L5_PILOT_RESULTS_v2.md** | **Hard deadline** |

### 6.1 超时处理

若T+20h仍未完成训练:
- 立即停止训练
- 使用当前checkpoint评估
- 报告为"PARTIAL RESULTS - TIMEOUT"
- 标记是否需要扩展实验

---

## 7. 必须产出文件

| 文件 | 内容 | 截止时间 |
|------|------|----------|
| `l5_pilot_G1_transfer.json` | G1 64 seeds详细结果 | T+22h |
| `l5_pilot_G2_sham.json` | G2 64 seeds详细结果 | T+22h |
| `l5_pilot_G3_self_ref.json` | G3 16 seeds详细结果 | T+22h |
| `l5_pilot_code_retention.json` | G1 Code重测结果 | T+22h |
| `l5_pilot_leakage_audit.json` | Leakage检测报告 | T+23h |
| `L5_PILOT_RESULTS_v2.md` | 综合分析报告 | **T+24h** |

---

## 8. 与L4-v2的连续性保证

### 8.1 冻结项 (禁止修改)

| 组件 | L4-v2设置 | L5 Pilot状态 |
|------|-----------|--------------|
| 128-seed discipline | 验证有效 | 保持，缩放至144 |
| Pool A-F结构 | 验证有效 | 保持 |
| Anti-leakage penalty | 0.15-0.60 | 保持 |
| Mechanism extraction | stable_patterns | 保持 |
| Bridge thresholds | PASS/HOLD/REJECT | 保持 |

### 8.2 唯一变量

> **唯一允许的变化**: 将single-task inheritance package应用于cross-task transfer

所有其他参数必须冻结，以确保结果可比性。

---

## 9. 风险接受声明

执行者确认已理解:

1. L5风险等级为🔴 **HIGH**
2. Pilot可能失败，这是科学探索的正常结果
3. 即使成功，也不代表L5完全成立，仅说明方向可行
4. 禁止将Pilot结果外推或宣传为L5最终结论
5. 若触发任何熔断条件，必须立即停止，不得隐瞒

---

## 10. 批准签名

```yaml
approval:
  status: APPROVED_WITH_CONSTRAINTS
  version: v2.0
  date: "2026-03-15"
  
  approvers:
    - role: "Atlas-HEC Research Committee"
      signature: "EXECUTED"
    - role: "九叔/LOGIC Layer"
      signature: "DESIGN_REVIEW_PASSED"
      
  constraints_enforced:
    - "Scale: 144 seeds max"
    - "Duration: 24h hard deadline"
    - "No hyperparameter tuning"
    - "3 circuit breakers active"
    
  next_milestone: "T+24h L5_PILOT_RESULTS_v2.md"
```

---

**执行指令**: 立即启动，24小时内完成  
**监控**: 九叔/LOGIC Layer实时审核  
**紧急联系**: 触发熔断时立即报告

---

*"修订是为了聚焦。144 seeds足以回答核心问题。不要为规模而规模。"*  
*— 九叔/LOGIC Layer*
