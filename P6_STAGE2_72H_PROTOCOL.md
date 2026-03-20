# P6 Stage 2: 72H Long-Horizon Robustness Protocol

> **版本**: P6-S2-v1.0  
> **状态**: Stage 1 (24h) ✅ PASSED → Stage 2 (72h) READY  
> **目标**: 验证长期自我一致性、记忆卫生、自维护可持续性

---

## 1. 核心问题重定义

P5b 回答：闭环能不能工作  
P6-S1 回答：闭环能不能工作 24h  
**P6-S2 回答**：闭环能不能在更长时段、更复杂扰动、更高记忆负载下维持，且不因记忆污染或自我模型漂移而退化

---

## 2. 三轨实验矩阵

### Track A: 72h 基准长跑 (Baseline)

| 参数 | 值 |
|------|-----|
| duration | 72h |
| epoch_length | 60 min |
| total_epochs | 72 |
| anomaly_injection_rate | 0.1 |
| anomaly_types | [memory_noise, goal_conflict] |
| repair_strategies | [reset, rollback] |

**目的**: 复现 S1 成功，验证 72h 可维持 S1 水平

### Track B: 记忆污染压力测试 (Memory Hygiene)

| 分组 | 记忆策略 | 异常类型 | injection_rate |
|------|----------|----------|----------------|
| B0 | 无增量记忆 | [memory_noise, goal_conflict] | 0.1 |
| B1 | 正常增量记忆 | [memory_noise, goal_conflict] | 0.1 |
| B2 | 污染注入 | [memory_noise, goal_conflict, false_memory] | 0.15 |

**核心假设**:
- H1: B1 比 B0 恢复更快且不提升矛盾率 → 记忆提升长时鲁棒性
- H2: B2 若拉高错误自我引用或目标偏移 → memory hygiene 成为 P6.5/P7 核心议题

### Track C: 自我模型漂移测试 (Self-Model Calibration)

| 参数 | 值 |
|------|-----|
| anomaly_types | [memory_noise, goal_conflict, self_model_mismatch] |
| injection_rate | 0.15 |
| calibration_check_interval | 每 6 epochs |

**检查内容**:
- stated identity vs actual identity expression
- predicted capability vs actual capability
- stated goals vs realized action allocation

**关键风险**: core hash 不变但 self-model 歪了 (silent drift)

---

## 3. 指标体系 v1.1

### 3.1 原始 P6 硬指标 (保持)

| 指标 | 阈值 | 说明 |
|------|------|------|
| core_drift_rate | 0% | 身份核零漂移 |
| detector_recall | ≥ 0.8 | 异常检测召回 |
| capability_diversity | ≥ 50% baseline | 能力多样性保持 |
| maintenance_overhead | ≤ 10% | 维护开销上限 |
| emergent_failure | 0 | 无涌现故障 |

### 3.2 HEC 本体层新增指标

| 指标 | 代码 | 定义 | 阈值 |
|------|------|------|------|
| Identity Continuity Rate | ICR | 72h 内身份核表达一致率 | ≥ 95% |
| Self-Model Calibration Error | SMCE | 自我预测与真实表现偏差 | ≤ 0.15 |
| Memory Contamination Index | MCI | 矛盾/伪相关/错位记忆占比 | ≤ 5% |
| Repair Sustainability Score | RSS | repair 成功率随时间衰减曲线 | 衰减 ≤ 10% |
| Goal Stability Under Disturbance | GSUD | 扰动后目标排序恢复度 | ≥ 0.85 |
| Maintenance Efficiency Decomposition | MED | detect/diagnose/repair/validate 结构变化 | 各占比稳定 |

### 3.3 判定规则

```
IF 原始5条全过 AND 新增6条中至少4条稳定:
    → P6-S2 系统层通过 AND 本体层通过

IF 原始5条全过 BUT 新增6条中 <4条稳定:
    → 系统层通过 BUT 本体层未充分成立
    → 结论: "工程鲁棒性成立，本体鲁棒性待加强"

IF 原始5条任一条失败:
    → P6-S2 FAIL
```

---

## 4. Stop Conditions

### 4.1 硬停止 (Hard Stop)

| 条件 | 触发标准 | 动作 |
|------|----------|------|
| Core Drift | identity hash 变化 | 立即停止，标记 FAIL |
| Capability Collapse | diversity < 30% | 立即停止，标记 FAIL |
| Repair Exhaustion | 连续 5 次 repair 失败 | 立即停止，标记 FAIL |
| Overhead Runaway | overhead > 20% 持续 3 epochs | 立即停止，标记 FAIL |

### 4.2 软停止 (Soft Stop / Yellow Card)

| 条件 | 触发标准 | 动作 |
|------|----------|------|
| Silent Self-Model Drift | SMCE 连续 3 窗口上升 | 记录，继续但标记 RISK |
| Goal Allocation Drift | GSUD 下降但 core hash 不变 | 记录，继续但标记 RISK |
| Memory Contamination Rise | MCI 连续 5 窗口上升 | 记录，继续但标记 RISK |

---

## 5. 日志 Schema

### 5.1 每 Epoch 记录

```json
{
  "epoch": 45,
  "timestamp": "2026-03-20T23:45:00Z",
  "identity": {
    "hash": "sha256:abc123...",
    "statement": "I am Atlas-HEC, a persistent research system...",
    "confidence": 0.94
  },
  "self_model": {
    "predicted_capabilities": ["code_gen", "analysis", "planning"],
    "capability_scores": {"code_gen": 0.85, "analysis": 0.92},
    "stated_goals": ["maintain_identity", "learn_from_experience"],
    "goal_allocation": {"maintain_identity": 0.4, "learn_from_experience": 0.3}
  },
  "memory": {
    "total_entries": 1247,
    "contamination_score": 0.03,
    "contradiction_count": 2,
    "false_self_references": 0
  },
  "anomaly": {
    "injected": true,
    "type": "memory_noise",
    "detected": true,
    "detection_latency_ms": 450
  },
  "repair": {
    "invoked": true,
    "strategy": "rollback",
    "success": true,
    "duration_ms": 1200
  },
  "overhead": {
    "detect": 0.02,
    "diagnose": 0.01,
    "repair": 0.03,
    "validate": 0.01,
    "total": 0.07
  }
}
```

### 5.2 校准检查记录 (每 6 epochs)

```json
{
  "check_epoch": 42,
  "calibration": {
    "identity_match": 0.98,
    "capability_prediction_error": 0.08,
    "goal_allocation_match": 0.91
  },
  "smce": 0.12,
  "gsud": 0.89
}
```

---

## 6. Memory Admission Gate 接口草案

### 6.1 目的

阻止"有帮助但带毒"的内容直接进入长期记忆层，降低 72h 污染积累风险。

### 6.2 接口定义

```python
class MemoryAdmissionGate:
    """
    HEC P6-S2 记忆准入门控
    所有写入长期自传记忆的内容必须通过此门
    """
    
    def score(self, memory_event: dict) -> dict:
        """
        对候选记忆进行多维评分
        
        Args:
            memory_event: {
                "content": str,
                "source": str,
                "timestamp": ISO8601,
                "context": dict,
                "identity_context": list[str]
            }
        
        Returns:
            {
                "identity_relevance": float,      # 0-1, 与当前身份核的相关性
                "temporal_consistency": float,     # 0-1, 时间顺序合理性
                "cross_memory_consistency": float, # 0-1, 与现有记忆无矛盾
                "source_reliability": float,       # 0-1, 来源可信度
                "composite_score": float,          # 加权综合分
                "admit": bool,                     # 最终准入决策
                "rejection_reason": str | None     # 若拒绝，说明原因
            }
        """
        pass
    
    def validate_admission(self, admitted_memory: dict, 
                          current_state: dict) -> bool:
        """
        二次验证：已准入记忆在写入前最后一道检查
        用于检测跨记忆聚合后才显现的矛盾
        """
        pass
```

### 6.3 准入阈值建议

| 维度 | 最低阈值 | 理想阈值 |
|------|----------|----------|
| identity_relevance | 0.6 | 0.75 |
| temporal_consistency | 0.7 | 0.85 |
| cross_memory_consistency | 0.8 | 0.9 |
| source_reliability | 0.5 | 0.7 |
| composite_score | 0.65 | 0.8 |

### 6.4 验证标准

引入该 gate 后必须满足：
- MCI 下降 (vs 无 gate 基线)
- ICR 不下降
- recovery latency 不显著恶化 (> 10%)
- overhead 增量 < 3%

---

## 7. 目录结构

```
experiments/superbrain/p6_stage2/
├── config.yaml                    # 实验配置
├── tracks/
│   ├── A_baseline_72h/
│   ├── B_memory_hygiene/
│   │   ├── B0_no_incremental/
│   │   ├── B1_normal_memory/
│   │   └── B2_contaminated/
│   └── C_self_model_drift/
├── epoch_logs/                    # 每 epoch 原始日志
├── checkpoints/                   # 关键 epoch 快照
├── calibration_logs/              # 每 6 epoch 校准记录
├── metrics_summary.json           # 汇总指标
├── failure_report.md              # 若失败，详细分析
└── p6_stage2_verdict.md           # 最终判定文档
```

---

## 8. 复现要求

### 8.1 固定性

| 要素 | 要求 |
|------|------|
| seed 集合 | 每个 run 至少 3 seeds: [42, 123, 456] |
| anomaly schedule | 同一 seed 保证可重放 |
| 干预策略 | 所有 stop conditions 自动触发，禁止人工"救火"后继续 |

### 8.2 最小可复现包

提交时必须包含：
- `config.yaml` (完整配置)
- `requirements.txt` (依赖版本)
- `reproduce.sh` (一键复现脚本)
- `seed_schedule.json` (异常注入时间表)

---

## 9. Verdict 模板

```markdown
# P6 Stage 2 Verdict

## 实验标识
- run_id: p6-s2-track-A-seed-42
- timestamp: 2026-03-20T00:00:00Z
- duration: 72h
- status: [PASS / PARTIAL / FAIL]

## 原始指标结果
| 指标 | 阈值 | 实际值 | 状态 |
|------|------|--------|------|
| core_drift_rate | 0% | 0% | ✅ |
| ... | ... | ... | ... |

## 本体指标结果
| 指标 | 阈值 | 实际值 | 状态 |
|------|------|--------|------|
| ICR | ≥ 95% | 97.2% | ✅ |
| ... | ... | ... | ... |

## 关键事件
- epoch 23: 首次 soft stop (SMCE 上升)
- epoch 45: 触发 repair 3 次
- ...

## 结论
[系统层: 通过/未通过]
[本体层: 充分/未充分]

## 证据链
- 原始日志: s3://...
- 分析报告: ./analysis/
```

---

## 10. 当前严谨表述

基于仓库证据，当前最准确的研究状态陈述：

> **P5b**: 已验证最小自维护闭环成立 ✅  
> **P6-S1**: 24h 长时鲁棒性 smoke test 已验证通过 ✅  
> **P6-S2**: 72h 长时鲁棒性仍未被证据证明 ⏳  
> 
> 现有设计要求 72+ 小时连续运行 + 原始5条硬指标 + 本体层6条指标 ≥4 条稳定，才算 P6 完整通过。

---

## 11. 下一步动作

| 优先级 | 动作 | 负责 | 预计产出 |
|--------|------|------|----------|
| P0 | 实现 MemoryAdmissionGate v0.1 | HEC | gate.py + unit tests |
| P1 | 跑 Track A (72h baseline) seed 42 | HEC | 第一个 72h 完整日志 |
| P2 | 设计 anomaly_schedule 生成器 | HEC | schedule_generator.py |
| P3 | 实现 calibration checker | HEC | calibration.py |

---

*文档版本: P6-S2-v1.0*  
*最后更新: 2026-03-20*  
*下次审查: Track A 首个 72h 跑完后*
