# SOCS Research Operating System (4-Layer Architecture)

## 核心原则

> Autonomous Research Operator ≠ Autonomous Superbrain
> 
> 研究自动化层 ≠ 超脑核心层

## 4 层架构

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: Human-Gated Architecture Editor                    │
│ 人工审核架构修改层                                           │
│ • 只允许提出结构代码修改提案                                  │
│ • 必须包含：为什么改、风险、回滚条件                          │
│ • 人类决定是否执行                                           │
│ • 禁止直接修改主系统核心                                      │
└──────────────────────┬──────────────────────────────────────┘
                       │ 提案流 (Proposal Stream)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: Failure-Mode Triage                                │
│ 失败模式诊断层                                               │
│ • 自动输出 first degradation mode                           │
│ • 识别 simulation-limited vs realism-limited                 │
│ • 生成最小修正假设 (最多3条)                                  │
│ • 不推荐泛泛的调参建议                                       │
└──────────────────────┬──────────────────────────────────────┘
                       │ 诊断报告 (Triage Report)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: Hypothesis Manager                                 │
│ 假设树管理层                                                 │
│ • 管理 O1 / OQS / BeeHive / AntColony 假设树                 │
│ • 追踪 Gate 状态 (PENDING/IN_PROGRESS/PASSED/FAILED)         │
│ • 维护阻塞项清单 (Blockers)                                  │
│ • 生成分支/合并建议                                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ 任务指令 (Task Directive)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Experiment Operator                                │
│ 实验操作层 (唯一允许自动执行的层)                             │
│ • 读取假设文档 (HYPOTHESIS_*.md)                             │
│ • 运行实验脚本 (run_*_gate*.py)                              │
│ • 汇总指标 (retention/CWCI/spec/integ/bcast)                 │
│ • 判断 PASS/PARTIAL/FAIL                                     │
│ • 生成报告到 research_ops/outputs/                           │
│ • 禁止修改主系统核心文件                                      │
└─────────────────────────────────────────────────────────────┘
```

## 沙箱边界

### ✅ Layer 1 允许修改
```
research_ops/
  ├── experiment_configs/      # 实验配置
  ├── result_aggregators/      # 结果聚合脚本
  ├── report_templates/        # 报告模板
  └── outputs/                 # 实验输出

hypothesis_tree/
  ├── status_tracker.md        # Gate 状态追踪
  └── blocker_log.md           # 阻塞项日志

failure_triage/
  └── diagnosis_reports/       # 诊断报告

proposed_edits/
  └── *.patch / *.md           # 架构修改提案 (L4)
```

### ❌ 禁止直接修改 (需 L4 提案 + 人工审核)
```
src/
  ├── universe_runner.rs       # 核心运行时
  ├── consciousness_index.rs   # CWCI 评估器
  ├── evaluation.rs            # 动力学评估
  └── bin/                     # 主二进制

experiments/
  ├── HYPOTHESIS_O1.md         # 已确认假设 (只读)
  └── HYPOTHESIS_OQS.md        # 已确认假设 (只读)
```

## 操作协议

### Layer 1 → Layer 2
```
输入: HYPOTHESIS_O1.md, run_hypothesis_o1_gate2.py
输出: {
  "gate": "Gate 2",
  "result": "PASSED",
  "metrics": {
    "retention": 0.943,
    "cwci_mean": 0.629,
    "spec_rank": 1,
    "integ_rank": 1,
    "bcast_rank": 1
  },
  "next_action": "PROCEED_TO_SMOKE"
}
```

### Layer 2 → Layer 3
```
输入: Gate 1.5 FAILED (OQS)
输出: {
  "blockers": [
    "ResourceScarcity: CWCI 0.036",
    "FailureBurst: CWCI 0.015",
    "lineage_improvement: -0.219"
  ],
  "diagnosis_request": "FIRST_FAILURE_MODE"
}
```

### Layer 3 → Layer 4
```
输入: OQS Gate 1 PARTIAL
输出: {
  "first_failure_mode": "budget_conservative",
  "root_cause": "Queen resource_budget static, no dynamic adjustment",
  "simulation_limited": true,
  "minimal_corrections": [
    "Dynamic budget: base * (1 + success_rate - hazard)",
    "Lower return threshold: every 100 tick",
    "Gentler culling: threshold 0.2, 50% chance"
  ],
  "risk_assessment": "LOW - only affects OQS simulation"
}
```

### Layer 4 → Human
```
输入: Architecture Edit Proposal
内容: {
  "target": "src/universe_runner.rs",
  "change": "Add hazard_simulation_mode flag",
  "justification": "Distinguish simulated vs real metrics",
  "risk": "MINOR - additive only",
  "rollback": "Remove 3 lines",
  "test_plan": "Verify smoke test still passes"
}
决策: [APPROVE] [REJECT] [MODIFY]
```

## 当前状态映射

| 现有资产 | 对应层级 | 状态 |
|---------|---------|------|
| run_hypothesis_o1_gate*.py | L1 Experiment Operator | ✅ 已就绪 |
| run_oqs_gate1.py | L1 Experiment Operator | ✅ 已就绪 |
| HYPOTHESIS_O1.md | L2 Hypothesis (只读) | ✅ 已确认 |
| HYPOTHESIS_OQS.md | L2 Hypothesis (只读) | ✅ 已确认 |
| MAINLINE_CONVERGENCE_REPORT.md | L2 Status Tracker | ✅ 已生成 |
| Gate 2 分析结论 | L3 Failure Triage | ✅ 已完成 |
| OQS 修正建议 | L3 → L4 提案 | ⏳ 待生成 |

## 下一步：改造清单

### Phase 1: Layer 1 硬化 (已完成)
- [x] 实验脚本可独立运行
- [x] 输出格式标准化
- [x] 沙箱边界明确

### Phase 2: Layer 2 自动化 (待实现)
- [ ] hypothesis_tree/status_tracker.json
- [ ] 自动更新 Gate 状态
- [ ] 阻塞项自动识别

### Phase 3: Layer 3 诊断器 (待实现)
- [ ] failure_triage/diagnose.py
- [ ] first_failure_mode 提取
- [ ] simulation-limited 标记

### Phase 4: Layer 4 提案系统 (待实现)
- [ ] proposed_edits/ 模板
- [ ] 风险/回滚评估格式
- [ ] 人工审核接口

## 一句话定位

> Autonomous Research Operator 接管"研究协调"，人类保留"架构决策"；
> 它做实验、管假设、诊失败、提建议；
> 你决定是否改核心。
