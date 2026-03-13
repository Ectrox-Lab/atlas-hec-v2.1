# SOCS Autoresearch Operator

## 定位

> **实验与报告自动驾驶** ≠ **超脑本体**
> 
> Autonomous Experiment Layer ≠ Autonomous Cognitive Core

## 核心职责

接管现在最费手的机械劳动：
- 实验编排与跑批
- 结果比较与保留/回滚
- 阶段报告自动生成

**不碰主系统本体**。

## 沙箱边界（硬约束）

### ✅ 允许操作（只读或生成新文件）

```
socs_autoresearch_operator/
├── tasks/              # 任务定义
├── results/            # 实验结果输出
├── proposals/          # 下一步建议（人类审核）
└── reports/            # 自动生成的报告

experiments/
├── HYPOTHESIS_O1.md    # 读取（只读）
├── HYPOTHESIS_OQS.md   # 读取（只读）
├── run_hypothesis_o1_gate1.py  # 执行
├── run_hypothesis_o1_gate2.py  # 执行
└── run_oqs_gate1.py    # 执行

research_ops/outputs/   # 写入结果
```

### ❌ 禁止直接修改

```
src/                    # 真实 SOCS 核心架构
├── universe_runner.rs
├── consciousness_index.rs
├── evaluation.rs
├── three_layer_memory/ # 三层记忆硬约束
└── archive/            # Archive / Lineage 机制

experiments/
├── HYPOTHESIS_O1.md    # 不修改已确认假设
└── HYPOTHESIS_OQS.md   # 不修改已确认假设

MAINLINE_CONVERGENCE_REPORT.md  # 人类维护主线状态
```

## 4 类任务

### Task 1: Gate Operator
自动跑实验，输出 PASS/PARTIAL/FAIL

```bash
# 执行
python tasks/gate_operator.py --hypothesis O1 --gate Gate_2
python tasks/gate_operator.py --hypothesis OQS --gate Gate_1_5

# 输出
results/O1_Gate_2_20240312_101030.json
results/OQS_Gate_1_5_20240312_101030.json
```

### Task 2: Result Triage
比较结果，输出诊断

```python
{
  "verdict": "PARTIAL",
  "top_candidate": "OctopusLike",
  "first_failure_mode": "budget_conservative",
  "limitation": "SIMULATION-LIMITED",
  "recommendation": "Apply 3 minimal corrections"
}
```

### Task 3: Smoke Scheduler
自动跑 smoke test 场景

```bash
python tasks/smoke_scheduler.py \
  --scenes RegimeShiftFrequent,ResourceScarcity,HighCoordinationDemand \
  --candidates OctopusLike,ModularLattice,RandomSparse
```

### Task 4: Research Notebook Writer
自动维护阶段报告

```bash
python tasks/notebook_writer.py \
  --input results/ \
  --output reports/weekly_convergence_2024W11.md
```

## 与人类的分工

| 职责 | Autoresearch Operator | 人类 |
|-----|----------------------|------|
| 跑实验 | ✅ 自动 | ❌ |
| 比结果 | ✅ 自动 | ❌ |
| 写报告 | ✅ 自动 | ❌ |
| 决定改不改核心 | ❌ | ✅ 决策 |
| 修改 src/ | ❌ | ✅ 审核后执行 |
| 确认假设文档 | ❌ | ✅ 人工维护 |

## 快速开始

```bash
# 1. 运行 Gate Operator
python tasks/gate_operator.py --hypothesis O1 --gate Gate_2

# 2. 查看结果
ls results/
cat results/latest_report.md

# 3. 人类审核提案
cat proposals/next_steps_20240312.md
# [APPROVE] [REJECT] [MODIFY]
```

## 最准确的一句话

SOCS Autoresearch Operator 是「实验与报告自动驾驶」，不是「超脑本体」；它跑 Gate、比结果、写报告、提建议；人类决定是否改核心、改哪里、怎么改。
