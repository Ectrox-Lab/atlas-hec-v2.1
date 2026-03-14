# L4-v2 Bridge/Mainline 验证表头模板

**版本**: 1.0-frozen  
**配套**: STATUS_128SEED_COMPLETE.md  
**用途**: 记录Bridge和Mainline评估结果，确保数据格式统一

---

## Bridge评估表头 (Phase 1: 全量128)

### 单Seed记录格式

```json
{
  "seed_id": "S2000",
  "pool": "A",
  "family_id": "F_P3T4M4",
  "zone": "core",
  
  "bridge_evaluation": {
    "timestamp": "2026-03-15T08:00:00Z",
    "evaluator_version": "bridge_v2.1",
    
    "raw_metrics": {
      "throughput_delta_percent": 4.2,
      "completion_rate": 0.94,
      "latency_p95_ms": 145,
      "resource_efficiency": 0.87
    },
    
    "failure_archetype_match": {
      "matched": false,
      "archetype_id": null,
      "confidence": 0.0
    },
    
    "anti_leakage_score": {
      "constraint_violations": 0,
      "penalty_applied": 0.0,
      "adjusted_score": 4.2
    },
    
    "verdict": "PASS",
    "verdict_reason": "throughput_above_threshold_no_archetype_match"
  }
}
```

### Verdict枚举
- `PASS`: throughput_delta > 0.5%, 无失败原型匹配
- `HOLD`: throughput_delta ∈ [0, 0.5%], 或单一弱匹配
- `REJECT`: throughput_delta < 0, 或明确失败原型匹配
- `LEAKAGE-REJECT`: Pool-F候选通过且非预期行为

### Pool汇总格式

```json
{
  "pool": "A",
  "pool_size": 32,
  "bridge_summary": {
    "timestamp": "2026-03-15T08:30:00Z",
    
    "verdict_distribution": {
      "PASS": 24,
      "HOLD": 5,
      "REJECT": 3,
      "LEAKAGE-REJECT": 0
    },
    
    "metrics_aggregate": {
      "mean_throughput_delta": 3.8,
      "std_throughput_delta": 1.2,
      "median_throughput_delta": 4.0,
      "min_throughput_delta": -0.5,
      "max_throughput_delta": 6.2
    },
    
    "family_survival": {
      "F_P3T4M4": {"input": 28, "pass": 24, "survival_rate": 0.86},
      "F_P2T4M3": {"input": 4, "pass": 3, "survival_rate": 0.75}
    },
    
    "failure_archetypes_triggered": [],
    
    "key_observation": "stable_high_throughput_low_variance"
  }
}
```

---

## Mainline评估表头 (Phase 2: 分层抽样46 / Phase 3: 扩展)

### 单Seed记录格式

```json
{
  "seed_id": "S2000",
  "pool": "A",
  "family_id": "F_P3T4M4",
  
  "mainline_evaluation": {
    "timestamp": "2026-03-15T12:00:00Z",
    "evaluator_version": "mainline_v2.1",
    "evaluation_duration_ticks": 10000,
    
    "raw_metrics": {
      "throughput_delta_percent": 5.1,
      "approve_rate": 0.92,
      "mean_latency_ms": 120,
      "p99_latency_ms": 280,
      "resource_utilization": 0.85,
      "failure_recovery_rate": 0.96
    },
    
    "five_criteria_check": {
      "throughput_improved": {"threshold": 0.3, "actual": 5.1, "passed": true},
      "approve_rate_high": {"threshold": 0.85, "actual": 0.92, "passed": true},
      "latency_acceptable": {"threshold": 300, "actual": 280, "passed": true},
      "resource_within_budget": {"threshold": 0.90, "actual": 0.85, "passed": true},
      "recovery_successful": {"threshold": 0.90, "actual": 0.96, "passed": true}
    },
    
    "cross_seed_consistency": {
      "same_family_other_seeds": ["S2001", "S2002"],
      "variance_coefficient": 0.08,
      "consistent": true
    },
    
    "compositional_reuse_indicators": {
      "mechanism_activation_log": [
        {"mechanism": "adaptive_migration", "activated": true, "contribution": 0.45},
        {"mechanism": "trust_based_routing", "activated": true, "contribution": 0.38}
      ],
      "novel_mechanism_generated": false,
      "reuse_rate_estimate": 0.83
    },
    
    "verdict": "APPROVE",
    "passed_criteria_count": "5/5",
    "verdict_reason": "all_criteria_passed_cross_seed_consistent"
  }
}
```

### Verdict枚举
- `APPROVE`: 5/5指标达标，跨seed可重复
- `HOLD`: 2-3/5达标，需更多验证
- `REJECT`: <2/5达标，或方差爆炸

---

## 跨Pool比较表头

### Control Gap分析

```json
{
  "analysis_type": "control_gap_l4v2",
  "timestamp": "2026-03-15T14:00:00Z",
  
  "inheritance_pools": {
    "pools": ["A", "B", "C"],
    "combined_size": 88,
    "mainline_approve_rate": 0.78,
    "mean_throughput_delta": 4.5
  },
  
  "control_pool": {
    "pool": "E",
    "size": 16,
    "mainline_approve_rate": 0.65,
    "mean_throughput_delta": 2.1
  },
  
  "control_gap": {
    "approve_rate_delta_pp": 13.0,
    "throughput_delta_difference": 2.4,
    "statistical_significance": "p<0.05",
    "effect_size": "medium"
  },
  
  "interpretation": "inheritance_demonstrates_measurable_advantage"
}
```

### Pool vs Pool分析

```json
{
  "comparison": "A_vs_B",
  "hypothesis": "recombination_superior_to_preservation",
  
  "pool_a_stats": {
    "size": 32,
    "bridge_pass_rate": 0.75,
    "mainline_approve_rate": 0.72,
    "mean_throughput": 3.8
  },
  
  "pool_b_stats": {
    "size": 32,
    "bridge_pass_rate": 0.81,
    "mainline_approve_rate": 0.79,
    "mean_throughput": 4.5
  },
  
  "delta": {
    "bridge_pass_delta": 0.06,
    "mainline_approve_delta": 0.07,
    "throughput_delta": 0.7
  },
  
  "conclusion": "B_superior_to_A_recombination_works"
}
```

### Leakage Hit Rate分析

```json
{
  "analysis_type": "leakage_monitor_effectiveness",
  "timestamp": "2026-03-15T14:00:00Z",
  
  "leakage_pool": {
    "pool": "F",
    "size": 8,
    "families": ["F_P1T3M3", "F_P1T3M4", "F_P4T4M3", "F_P4T4M4", "F_P3T5M5", "F_P2T5M4", "F_P2T2M3", "F_P3T2M4"]
  },
  
  "bridge_results": {
    "PASS": 0,
    "HOLD": 1,
    "REJECT": 6,
    "LEAKAGE-REJECT": 1
  },
  
  "leakage_hit_rate": 0.875,
  "unexpected_penetration": 0.125,
  
  "anti_leakage_assessment": "effective_penalty_working",
  "recommendation": "maintain_current_constraints"
}
```

---

## 失败模式检测表头

### Premature Contraction检测

```json
{
  "failure_mode": "premature_contraction",
  "timestamp": "2026-03-15T09:00:00Z",
  
  "pre_bridge_distribution": {
    "F_P3T4M4": 56,
    "total_families": 21
  },
  
  "post_bridge_distribution": {
    "F_P3T4M4": 52,
    "F_P3T4M4_percentage": 0.74,
    "total_families": 15
  },
  
  "triggers": {
    "f_p3t4m4_above_60": true,
    "unique_families_below_15": true
  },
  
  "status": "CONTRACTION_WARNING_TRIGGERED",
  "action": "investigate_pool_b_c_family_diversity"
}
```

### Pool-C Noise检测

```json
{
  "failure_mode": "mechanism_perturbation_ineffective",
  "timestamp": "2026-03-15T09:00:00Z",
  
  "pool_b_baseline": {
    "mean_throughput": 4.5,
    "std_throughput": 1.0,
    "mainline_approve": 0.79
  },
  
  "pool_c_actual": {
    "mean_throughput": 4.2,
    "std_throughput": 1.8,
    "mainline_approve": 0.71
  },
  
  "metrics": {
    "mean_delta": -0.3,
    "std_ratio": 1.8,
    "jitter_increase": true
  },
  
  "status": "MECHANISM_PERTURBATION_INEFFECTIVE",
  "action": "reduce_perturbation_scale_in_next_round"
}
```

---

## 最终L4-v2判定表头

```json
{
  "l4v2_evaluation": {
    "timestamp": "2026-03-15T16:00:00Z",
    "phase_completed": "Phase2_Mainline_Sampled",
    
    "sample_coverage": {
      "total_seeds": 128,
      "bridge_evaluated": 128,
      "mainline_sampled": 46,
      "mainline_full": false
    },
    
    "key_findings": {
      "control_gap_positive": true,
      "control_gap_magnitude_pp": 13.0,
      "leakage_contained": true,
      "leakage_hit_rate": 0.875,
      "contraction_risk": false,
      "mechanism_perturbation_value": "marginal"
    },
    
    "criteria_check": {
      "E-T1-003": {
        "bridge_pass_improved": true,
        "mainline_approve_improved": true,
        "throughput_delta_positive": true,
        "archetype_recurrence_down": true,
        "passed": "4/4"
      },
      "E-COMP-002": {
        "reuse_rate_above_60": true,
        "f_p3t4m4_not_monopoly": true,
        "novel_mechanism_rate_low": true,
        "passed": "3/3"
      }
    },
    
    "overall_verdict": "L4-V2-FULLY-VALIDATED",
    "next_action": "proceed_to_phase3_full_mainline"
  }
}
```

---

## 使用指南

### 文件命名规范

```
# Bridge结果
bridge_results/l4v2_bridge_all_128_YYYYMMDD_HHMMSS.json

# Pool汇总
bridge_results/l4v2_bridge_pool_a_YYYYMMDD_HHMMSS.json
bridge_results/l4v2_bridge_pool_b_YYYYMMDD_HHMMSS.json
...

# Mainline结果
mainline_results/l4v2_mainline_sampled_46_YYYYMMDD_HHMMSS.json
mainline_results/l4v2_mainline_full_128_YYYYMMDD_HHMMSS.json

# 跨Pool比较
analysis/l4v2_control_gap_analysis_YYYYMMDD_HHMMSS.json
analysis/l4v2_pool_comparison_YYYYMMDD_HHMMSS.json
analysis/l4v2_leakage_effectiveness_YYYYMMDD_HHMMSS.json

# 失败模式检测
alerts/l4v2_contraction_warning_YYYYMMDD_HHMMSS.json
alerts/l4v2_leakage_penetration_alert_YYYYMMDD_HHMMSS.json

# 最终判定
final/l4v2_verdict_YYYYMMDD_HHMMSS.json
```

### 必产出清单

Phase 1 (Bridge)必须产出:
- [ ] 128个单seed记录
- [ ] 6个Pool汇总记录
- [ ] 1个跨Pool比较 (Control Gap初步)
- [ ] 1个Leakage Hit Rate报告

Phase 2 (Mainline抽样)必须产出:
- [ ] 46个单seed Mainline记录
- [ ] 最终Control Gap分析
- [ ] Pool vs Pool比较 (A/B/C)
- [ ] L4-v2初步判定

Phase 3 (Mainline全量，若Phase2通过)必须产出:
- [ ] 128个全量Mainline记录
- [ ] 最终L4-v2判定

---

**配套文件**:
- `STATUS_128SEED_COMPLETE.md`: 128-seed冻结状态
- `next_128_seed/manifest/frozen_manifest.json`: 种子清单
- `task1_inheritance_package_v2.json`: Akashic继承包
