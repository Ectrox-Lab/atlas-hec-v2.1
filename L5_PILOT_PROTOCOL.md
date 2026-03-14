# L5 Pilot Protocol: Minimal Transfer Validation

**状态**: READY FOR EXECUTION  
**版本**: v0.1  
**预计执行时间**: 24小时  
**前置**: L5_ARCHITECTURE_DESIGN.md approved

---

## 1. Pilot目标

验证最小可行性:
> **Can Task A (Code) inheritance improve Task B (Math) without causing catastrophic forgetting in A or source leakage?**

---

## 2. 实验设计 (4组 × 128 seeds)

### 2.1 组别定义

| 组名 | 代号 | 描述 | Seeds |
|------|------|------|-------|
| **B-base** | G0 | Task B无inheritance | 128 |
| **B-self** | G1 | Task B使用自身inheritance | 128 |
| **A→B-transfer** | G2 | Task B使用Task A inheritance | 128 |
| **Sham-transfer** | G3 | Task B使用无关package (bias=0) | 128 |

**总计**: 512 seeds (4 × 128)

### 2.2 父代池设计 (每组24 elite → 128)

沿用L4-v2模式:
- 24父代精英 (F_P3T4M4主导)
- Pool A: 32保守
- Pool B: 32重组
- Pool C: 24微变形
- Pool D: 16边界
- Pool E: 16控制
- Pool F: 8泄漏监测

### 2.3 组间对照矩阵

| 比较 | 计算方式 | 目的 |
|------|----------|------|
| **Self Gap** | G1 vs G0 | 确认Task B单任务继承有效 |
| **Transfer Gap** | G2 vs G0 | **核心: 跨任务迁移是否有效** |
| **Leakage Check** | G2 vs G3 | 排除"任何package都抬分" |
| **Gain Attribution** | (G2-G0) vs (G1-G0) | Transfer vs Self的比例 |

---

## 3. Task定义

### 3.1 Task A: Code Generation

```yaml
task_id: code_tool_use
domain: structured_output
complexity: medium
validation: unit_test_pass_rate
baseline_target: 70% pass rate
inheritance_source: L4-v2 certified package
```

### 3.2 Task B: Symbolic Math

```yaml
task_id: math_symbolic_reasoning
domain: abstract_reasoning
complexity: medium
validation: proof_correctness + step_efficiency
baseline_target: 65% correctness
inheritance_from_task_a: package_v3_multi_task
transfer_mechanisms:
  - hierarchical_decomposition
  - error_recovery_sequence
firewall_blocks:
  - syntax_patterns
  - api_specific_knowledge
```

---

## 4. Package Schema v3 (Task A → Task B)

```json
{
  "package_version": "3.0-pilot",
  "source_task": "code_tool_use",
  "target_task": "math_symbolic_reasoning",
  "generated_from": "L4-v2-mainline-approved-families",
  
  "transfer_candidates": {
    "hierarchical_decomposition": {
      "source_mechanism": "function_composition",
      "target_application": "proof_step_decomposition",
      "abstraction_level": "structural",
      "transfer_confidence": 0.72
    },
    "error_recovery_sequence": {
      "source_mechanism": "debugging_traceback",
      "target_application": "proof_correction_chain",
      "abstraction_level": "procedural",
      "transfer_confidence": 0.65
    }
  },
  
  "firewall_rules": [
    {
      "block": "language_syntax_patterns",
      "reason": "task_specific_not_transferable"
    },
    {
      "block": "tool_api_signatures",
      "reason": "domain_knowledge_pollution"
    }
  ],
  
  "expected_transfer_gap_pp": 5,
  "max_acceptable_leakage": 0.05
}
```

---

## 5. 执行流程

### Phase 1: Baseline (0-6h)

```bash
# G0: Task B baseline
python3 l5_pilot.py --group G0 --task B --inheritance none --seeds 128

# Validation: Ensure baseline stable
# Target: 65% correctness ± 5%
```

### Phase 2: Self-inheritance (6-12h)

```bash
# G1: Task B self-inheritance
python3 l5_pilot.py --group G1 --task B --inheritance self --seeds 128

# Expected: Self Gap ≥ 8pp (match L4-v2)
```

### Phase 3: Transfer (12-18h)

```bash
# G2: Task A → Task B transfer
python3 l5_pilot.py --group G2 --task B --inheritance from_task_a --seeds 128

# G3: Sham transfer control
python3 l5_pilot.py --group G3 --task B --inheritance sham --seeds 128

# Core validation: Transfer Gap > 0
```

### Phase 4: Catastrophic forgetting check (18-24h)

```bash
# Re-evaluate Task A with original package
python3 l5_pilot.py --check task_a_regression --compare l4v2_baseline

# Must maintain: Task A performance within 5% of L4-v2
```

---

## 6. 评估指标与熔断器

### 6.1 实时评估 (每32 seeds检查点)

```python
checkpoint_metrics = {
    "self_gap": G1_approve_rate - G0_approve_rate,
    "transfer_gap": G2_approve_rate - G0_approve_rate,
    "sham_baseline": G3_approve_rate,
    "task_a_regression": current_task_a_vs_l4v2
}
```

### 6.2 熔断条件

| 条件 | 触发 | 动作 |
|------|------|------|
| Self Gap < 5pp | G1表现不如L4-v2 | STOP: 基础继承失效 |
| Transfer Gap < Sham | G2不如G3 | STOP: Transfer无效 |
| Task A drop > 10% | Catastrophic forgetting | STOP: 破坏性迁移 |
| Cross-seed σ/μ > 0.2 | 结果不稳定 | EXTEND: 增加sample size |

### 6.3 成功标准

```yaml
pilot_success:
  self_gap_pp: ">= 8"          # 不低于L4-v2
  transfer_gap_pp: "> 0"       # 正向迁移
  transfer_vs_sham: "> 0"      # 真实transfer > 安慰剂
  task_a_regression: "< 5%"    # 无灾难性遗忘
  cross_seed_stable: true      # 可重复
  
partial_success:
  self_gap_pp: ">= 5"
  transfer_gap_pp: "> 0"
  no_catastrophic_forgetting: true
  
failure:
  transfer_gap_pp: "<= 0"
  or: catastrophic_forgetting_detected
```

---

## 7. 产出物

### 7.1 必须生成文件

| 文件 | 内容 | 截止时间 |
|------|------|----------|
| `l5_pilot_G0_baseline.json` | G0结果 | +6h |
| `l5_pilot_G1_self.json` | G1结果 | +12h |
| `l5_pilot_G2_transfer.json` | G2结果 | +18h |
| `l5_pilot_G3_sham.json` | G3结果 | +18h |
| `l5_pilot_task_a_check.json` | 回归测试 | +24h |
| `L5_PILOT_RESULTS.md` | 综合分析 | +24h |

### 7.2 关键图表

1. **4组性能对比柱状图**
2. **Transfer Gap分解** (真实transfer vs sham效应)
3. **Task A回归验证** (L4-v2 vs L5-pilot后)
4. **Family survival跨任务对比**

---

## 8. 决策树

```
Pilot结果
│
├─ Self Gap < 5pp
│   └─ ❌ FAIL: 基础继承失效，回查L4-v2
│
├─ Transfer Gap ≤ 0
│   └─ ❌ FAIL: 跨任务迁移无效，L5 design问题
│
├─ Task A regression > 5%
│   └─ ❌ FAIL: Catastrophic forgetting，停止L5
│
├─ 0 < Transfer Gap < 3pp
│   └─ 🟡 MARGINAL: 信号存在但弱，考虑 redesign
│
└─ Transfer Gap ≥ 5pp + 所有检查通过
    └─ ✅ PROCEED: 进入L5 Phase 2 (bi-directional)
```

---

## 9. 风险控制

### 9.1 已知风险

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| Task B太难 | 中 | 所有组表现差，signal-to-noise低 | 降低task complexity或换task |
| Package v3不成熟 | 高 | Transfer机制无效 | 回退到v2 + 手动选择mechanism |
| Compute不足 | 低 | 512 seeds无法完成 | 先跑64 seeds快速验证 |

### 9.2 紧急联系

若触发任何熔断条件，立即报告:
- L5 Architecture Owner
- Atlas-HEC Research Committee
- 保留所有checkpoint数据用于事后分析

---

**批准**: 待执行  
**执行者**: Atlas-HEC L5 Task Force  
**监督**: 九叔 / LOGIC Layer  
**截止时间**: 2026-03-16 04:56 UTC (24h)

---

*"L5不是L4的延续，是新问题。用L4的经验，但不要有L4的傲慢。"*
