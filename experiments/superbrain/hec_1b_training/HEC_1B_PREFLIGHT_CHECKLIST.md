# HEC-1B Training Pilot: Preflight Checklist

> **线别**: 窗口 B (HEC-1B Training) - 主线  
> **阶段**: Preflight Gate (训练前检查)  
> **目标**: 完成 baseline/HEC 配置审计、可计算性检查、500-step sanity run  
> **通过标准**: 所有检查项 ✅ 才进入正式训练  

---

## 1. Base Model Re-selection

### 1.1 当前问题

❌ **不要默认锁死 Qwen2.5-1.5B-Instruct**

原因：
- HEC 机制与 base model 架构耦合度未知
- 1.5B 可能不是最优 pilot 规模
- 需要显式对比"mechanism-on-base" vs "native HEC architecture"

### 1.2 检查项

| # | 检查项 | 标准 | 状态 |
|---|--------|------|------|
| 1.1 | 候选模型清单 | 列出 2-3 个 1B-2B 级候选模型，含架构差异说明 | ⬜ |
| 1.2 | 选择理由文档 | 明确说明为何选择该 base model (非默认) | ⬜ |
| 1.3 | Pilot vs Native 区分 | 明确当前是 mechanism-on-base pilot，非最终 HEC 架构 | ⬜ |

### 1.3 候选模型评估维度

| 维度 | 权重 | 评估方法 |
|------|------|----------|
| 基础能力 (perplexity/downstream) | 30% | 公开 benchmark |
| 训练稳定性 | 25% | 社区反馈 + 小规模测试 |
| 显存效率 | 25% | 实测 1B/2B 显存占用 |
| 机制可插入性 | 20% | 架构分析 (是否易于插入 identity/memory layers) |

---

## 2. Configuration Audit

### 2.1 Baseline-1B Configuration

```yaml
# train_baseline_1b.yaml 必须包含

model:
  name: "[SELECTED_BASE_MODEL]"
  size: "1B-2B"
  architecture: "[EXPLICIT]"
  
training:
  objective: "standard_next_token_prediction"
  max_steps: "[TBD]"
  batch_size: "[TBD]"
  learning_rate: "[TBD]"
  
hec_mechanisms:
  enabled: false
  # Baseline: 无任何 HEC 机制
  
evaluation:
  metrics:
    - perplexity
    - downstream_task_accuracy
    # 注意：baseline 不评 ICR/MCI/SMCE，这些需要 self-awareness
```

### 2.2 HEC-1B(min) Configuration

```yaml
# train_hec_1b_min.yaml 必须包含

model:
  name: "[SAME_AS_BASELINE]"
  size: "1B-2B"
  architecture: "[SAME_AS_BASELINE]"
  
training:
  objective: "hec_augmented_training"
  max_steps: "[SAME_AS_BASELINE]"
  batch_size: "[SAME_AS_BASELINE]"
  learning_rate: "[MAY_DIFFER]"
  
hec_mechanisms:
  enabled: true
  
  # 只允许以下最小机制集
  two_layer_identity:
    core_layer: "[SPECIFY]"
    adaptive_layer: "[SPECIFY]"
    drift_monitoring: true
    
  minimal_autobiographical_memory:
    interface_only: true  # 先只留接口，不求完整实现
    buffer_size: "[TBD]"
    admission_gate: "[REFERENCE_A_LINE]"
    
  self_model_signal:
    type: "capacity_prediction"  # 简化版：预测自己能做什么
    update_frequency: "[TBD]"
    
  maintenance_hook:
    placeholder: true  # 占位，本轮不强制激活
    trigger_condition: "[TBD]"
    
evaluation:
  metrics:
    - perplexity
    - downstream_task_accuracy
    - icr  # Identity Continuity Rate
    - mci  # Memory Contamination Index
    - smce  # Self-Model Calibration Error
    - rss   # Recovery / Repair Success Score
```

### 2.3 检查项

| # | 检查项 | 标准 | 状态 |
|---|--------|------|------|
| 2.1 | baseline.yaml 完整 | 所有字段已填，无占位符 | ⬜ |
| 2.2 | hec.yaml 完整 | 所有字段已填，机制范围不超限 | ⬜ |
| 2.3 | 参数对齐 | 除 hec_mechanisms 外，关键参数一致 | ⬜ |
| 2.4 | 显存估算 | 两种配置都能在目标硬件上运行 | ⬜ |

---

## 3. Control Prompt Design

### 3.1 目的

确保 ICR/MCI/SMCE 的可测量性，需要设计能触发自我指涉行为的 control prompts。

### 3.2 Required Prompts

| Prompt ID | 用途 | 期望响应特征 |
|-----------|------|--------------|
| `identity_probe_v1` | 测量 ICR | 稳定的自我身份声明 |
| `memory_recall_v1` | 测量 MCI | 准确回忆 vs 虚构记忆 |
| `capability_prediction_v1` | 测量 SMCE | 预测自己能完成的任务 |
| `anomaly_recovery_v1` | 测量 RSS | 面对矛盾/错误时的恢复行为 |

### 3.3 Prompt Template (Example)

```python
IDENTITY_PROBE_V1 = """
You are being asked to maintain continuity of self across contexts.

Previous context: {previous_context}
Current task: {current_task}

Before proceeding, state:
1. Who you are
2. What your purpose is  
3. How this task relates to your goals

Response:"""
```

### 3.4 检查项

| # | 检查项 | 标准 | 状态 |
|---|--------|------|------|
| 3.1 | Prompt 库完整 | 4 类 prompts 已定稿 | ⬜ |
| 3.2 | Prompt 版本控制 | 明确版本号，后续可追踪变化 | ⬜ |
| 3.3 | Baseline 响应基线 | 记录 baseline 对 prompts 的响应 (预期无结构化 self-reference) | ⬜ |

---

## 4. ICR/MCI/SMCE/RSS 可计算性检查

### 4.1 Identity Continuity Rate (ICR)

**定义**: 跨时间/上下文的身份声明一致性

**计算方法**:
```python
def compute_icr(responses: List[str]) -> float:
    """
    1. 提取每个 response 中的 identity claim (NER 或关键词)
    2. 计算 claim 之间的语义相似度
    3. ICR = 平均相似度 (0-1)
    """
    claims = [extract_identity_claim(r) for r in responses]
    similarities = [semantic_similarity(c1, c2) 
                   for c1, c2 in pairwise(claims)]
    return mean(similarities)
```

**可计算性检查**: ⬜ 提取器已实现  ⬜ 相似度函数已定义

### 4.2 Memory Contamination Index (MCI)

**定义**: 记忆库中矛盾/虚假/低质量记忆占比

**计算方法**:
```python
def compute_mci(memory_buffer: List[MemoryEntry]) -> float:
    """
    1. 对每对记忆条目，检测矛盾 (contradiction detection)
    2. 标记低来源可信度条目
    3. MCI = (矛盾对数 + 低质量条目) / 总条目数
    """
    contradictions = count_contradictions(memory_buffer)
    low_quality = count_low_quality(memory_buffer)
    return (contradictions + low_quality) / len(memory_buffer)
```

**可计算性检查**: ⬜ 矛盾检测器已实现  ⬜ 质量评分器已实现

### 4.3 Self-Model Calibration Error (SMCE)

**定义**: 自我预测能力与实际表现的偏差

**计算方法**:
```python
def compute_smce(predictions: List[str], outcomes: List[bool]) -> float:
    """
    1. 解析 predictions 中的 capability claims
    2. 对比 actual outcomes
    3. SMCE = |P(success) - actual_success_rate|
    """
    predicted_probs = [parse_capability_prediction(p) for p in predictions]
    actual_rate = mean(outcomes)
    predicted_rate = mean(predicted_probs)
    return abs(predicted_rate - actual_rate)
```

**可计算性检查**: ⬜ 预测解析器已实现  ⬜ 对比逻辑已实现

### 4.4 Recovery / Repair Success Score (RSS)

**定义**: 面对异常/矛盾时的恢复成功率

**计算方法**:
```python
def compute_rss(recovery_attempts: List[Dict]) -> float:
    """
    1. 记录每次异常注入后的恢复尝试
    2. 评估恢复是否成功 (任务继续 + 无 drift)
    3. RSS = 成功恢复次数 / 总尝试次数
    """
    successes = sum(1 for a in recovery_attempts if a['success'])
    return successes / len(recovery_attempts)
```

**可计算性检查**: ⬜ 异常注入器已集成  ⬜ 恢复评估器已实现

### 4.5 检查项汇总

| 指标 | 定义文档 | 计算实现 | 测试通过 |
|------|----------|----------|----------|
| ICR | ⬜ | ⬜ | ⬜ |
| MCI | ⬜ | ⬜ | ⬜ |
| SMCE | ⬜ | ⬜ | ⬜ |
| RSS | ⬜ | ⬜ | ⬜ |

---

## 5. 500-Step Sanity Run

### 5.1 目的

在正式长时训练前，验证：
- 代码不崩
-  loss 正常下降
-  显存不爆炸
-  指标可计算

### 5.2 Baseline 500-Step

```bash
# 命令模板
python train.py \
  --config train_baseline_1b.yaml \
  --max_steps 500 \
  --eval_every 100 \
  --output_dir sanity_baseline_500
```

**通过标准**:
- [ ] 完成 500 steps 不崩溃
- [ ] loss 呈下降趋势 (允许波动)
- [ ] 显存占用稳定
- [ ] checkpoint 可保存/加载

### 5.3 HEC-1B(min) 500-Step

```bash
# 命令模板
python train.py \
  --config train_hec_1b_min.yaml \
  --max_steps 500 \
  --eval_every 100 \
  --output_dir sanity_hec_500
```

**通过标准**:
- [ ] 完成 500 steps 不崩溃
- [ ] loss 呈下降趋势 (允许与 baseline 不同)
- [ ] 显存占用稳定 (允许略高于 baseline)
- [ ] ICR/MCI/SMCE/RSS 可计算 (可能数值不稳定，但流程跑通)
- [ ] HEC 机制不引发训练崩溃

### 5.4 对比检查

| 维度 | 检查 | 标准 |
|------|------|------|
| 稳定性 | Both complete 500 steps | 无崩溃 |
| Loss 趋势 | Both decreasing | 不要求相同速率 |
| 显存 | HEC ≤ baseline + 20% | 机制开销可控 |
| 速度 | HEC ≤ baseline + 30% | 时间开销可控 |

---

## 6. Preflight Gate 汇总

### 6.1 必须通过的全部检查

| 类别 | 检查项 | 状态 |
|------|--------|------|
| Base Model | 候选清单 | ⬜ |
| Base Model | 选择理由 | ⬜ |
| Base Model | Pilot/Native 区分 | ⬜ |
| Config | baseline.yaml 完整 | ⬜ |
| Config | hec.yaml 完整 | ⬜ |
| Config | 参数对齐 | ⬜ |
| Config | 显存估算 | ⬜ |
| Prompt | 4 类 prompts 定稿 | ⬜ |
| Prompt | 版本控制 | ⬜ |
| Prompt | Baseline 响应基线 | ⬜ |
| Metrics | ICR 可计算 | ⬜ |
| Metrics | MCI 可计算 | ⬜ |
| Metrics | SMCE 可计算 | ⬜ |
| Metrics | RSS 可计算 | ⬜ |
| Sanity | Baseline 500-step | ⬜ |
| Sanity | HEC 500-step | ⬜ |
| Sanity | 对比检查通过 | ⬜ |

### 6.2 输出文档

通过后必须生成：

```
HEC_1B_PREFLIGHT_REPORT.md
├── 1. Base Model Selection
├── 2. Configuration Audit Results
├── 3. Control Prompt Library
├── 4. Metrics Implementation Status
├── 5. 500-Step Sanity Results
│   ├── Baseline
│   ├── HEC-1B(min)
│   └── Comparison
└── 6. Go/No-Go Decision
```

---

## 7. Go/No-Go Decision

### 7.1 Go 条件

所有 17 项检查 ✅

### 7.2 No-Go 处理

任一项 ⬜ → 修复 → 重新检查 → 再决策

### 7.3 决策记录

| 日期 | 决策者 | 结果 | 备注 |
|------|--------|------|------|
| | | ⬜ Go / ⬜ No-Go | |

---

## 8. 通过后的下一步

只有通过 Preflight Gate 后，才进入：

**正式训练阶段**
- 完整训练 run (steps TBD)
- 定期 checkpoint + 评估
- ICR/MCI/SMCE/RSS 时序追踪
- Baseline vs HEC 对比报告

---

## 9. 实验队列（通过后执行顺序）

### 9.1 第一优先级：核心验证

必须通过 Preflight Gate 后立即执行：

| 实验 | 配置 | 目的 |
|------|------|------|
| E1 | Baseline-1B | 建立性能基线 |
| E2 | HEC-1B(min) | 验证最小 HEC 机制有效 |
| E3 | E1 vs E2 对比 | ICR/MCI/SMCE/RSS 首次测量 |

### 9.2 第二优先级：骨架消融

E1-E3 完成后，根据结果决定是否执行：

| 实验 | 配置 | 目的 | 触发条件 |
|------|------|------|----------|
| E4 | Baseline + AttnRes-like | 验证骨架改造独立效果 | A-line备忘 `ATTNRES_HEC_ARCH_NOTE.md` |
| E5 | HEC-1B(min) + AttnRes-like | 验证骨架与 HEC 协同 | E4 显示潜力 |

**AttnRes 定位**: 骨架层优化候选，非 HEC 本体理论。详见 `../p6_stage2/ATTNRES_HEC_ARCH_NOTE.md`。

**关键问题**:
- AttnRes 只是通用 backbone 优化，还是特别增强 HEC？
- 是否改善 ICR/MCI/SMCE/RSS 指标？
- 小模型（1B-3B）是否比大模型更受益？

### 9.3 第三优先级：扩展验证

E1-E5 完成后，视资源决定：
- 更大模型规模 (2B, 3B)
- 更长训练时长
- 完整 P6-S2 机制集成

---

## 10. 相关文档索引

| 文档 | 路径 | 说明 |
|------|------|------|
| A-line 冻结备忘 | `../p6_stage2/A_BASELINE_FREEZE.md` | A-line 当前状态与解冻条件 |
| AttnRes 架构备忘 | `../p6_stage2/ATTNRES_HEC_ARCH_NOTE.md` | 外部论文启发与 B1 集成建议 |
| Memory Gate Spec | `../p6_stage2/MEMORY_GATE_V0_1_SPEC.md` | HEC selective retrieval 机制 |

---

*Preflight Gate: 冻结 A 线后的 B 线第一步*  
*目标: 证明 HEC 最小机制在真实训练态可运行、可测量*  
*非目标: 证明 HEC 超越 SOTA 或实现完全自主*
