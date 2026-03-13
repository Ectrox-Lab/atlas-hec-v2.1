# OQS Gate 1.5 Minimal Fix Plan

## 一句话目标

> 从"局部强"→"整体稳"

只验证三件事，不扩场景，不扩指标，不加新机制。

## 三件事

### 1. Division-of-labour 修正

**当前**: 均匀初始化，无场景偏置
```
role_lineage = {all: 0.5}
```

**修正**: 场景自适应偏置
```
if stress == "ResourceScarcity":
    scout_bias = 0.7  # 探索优先
elif stress == "HighCoordinationDemand":
    builder_bias = 0.6  # 建设优先
elif stress == "FailureBurst":
    defender_bias = 0.6  # 防御优先
```

**验证指标**: division_of_labour_score > 0.5 (vs current 0.316)

### 2. Lineage initialization 修正

**当前**: 静态 budget = 100
```
resource_budget = 100  # 固定
```

**修正**: 动态预算分配
```
resource_budget = base_budget * (1 + success_rate - hazard_level)
```

**验证指标**: 
- ResourceScarcity CWCI > 0.25 (vs current 0.036)
- FailureBurst CWCI > 0.25 (vs current 0.015)

### 3. Culling 修正

**当前**: 激进立即清除
```
if utility < 0.3:
    cull_immediate()  # 100%
```

**修正**: 温和选择+恢复
```
if utility < 0.2:  # 降低阈值
    if random() < 0.5:  # 50%概率
        cull()
    utility += 0.15  # 恢复缓冲
```

**验证指标**: 
- lineage_improvement > 0 (vs current -0.219)
- experience_return_quality > 0 (vs current 0.000)
- HighCoordinationDemand maintain > 0.77 (允许5%退化)

## 实验设计

```yaml
family: OQS (OctoQueenSwarm)
fixes: [division_of_labour, lineage_init, culling]
scenarios: 3
  - HighCoordinationDemand  (维持优势)
  - ResourceScarcity        (必须改善)
  - FailureBurst            (必须改善)
seeds: [11, 23, 37]
baseline: Gate 1 results
target: "整体稳健"
```

## 通过标准

| 场景 | Gate 1 CWCI | Gate 1.5 Target | 判定 |
|-----|-------------|-----------------|------|
| HighCoordinationDemand | 0.815 | ≥ 0.770 | ✅ 维持 |
| ResourceScarcity | 0.036 | ≥ 0.250 | ✅ 改善 |
| FailureBurst | 0.015 | ≥ 0.250 | ✅ 改善 |
| lineage_improvement | -0.219 | > 0 | ✅ 转正 |
| experience_return_quality | 0.000 | > 0 | ✅ 生效 |

**综合判定**:
- PASS: 5/5 达标
- PARTIAL: 3-4/5 达标
- FAIL: < 3/5 达标

## 禁止行为

- ❌ 扩场景 (只保持3个)
- ❌ 扩指标 (只验证上表)
- ❌ 加新机制 (只修3项)
- ❌ 调评分标准
- ❌ 改核心架构

## 执行命令

```bash
python socs_autoresearch_operator/tasks/gate_operator.py \
  --hypothesis OQS \
  --gate Gate_1_5 \
  --fixes division_of_labour,lineage_init,culling
```

## 输出

```json
{
  "gate": "1.5",
  "fixes_applied": ["division_of_labour", "lineage_init", "culling"],
  "results": {
    "HighCoordinationDemand": 0.XXX,
    "ResourceScarcity": 0.XXX,
    "FailureBurst": 0.XXX,
    "lineage_improvement": 0.XXX,
    "experience_return_quality": 0.XXX
  },
  "verdict": "PASSED|PARTIAL|FAILED",
  "transition": "locally_strong → globally_stable?"
}
```

## 下一步决策

- **PASS (5/5)**: OQS 可挑战主线，启动对比实验
- **PARTIAL (3-4/5)**: 继续修正特定项，保持副线
- **FAIL (<3/5)**: OQS 降级为探索性架构，专注 OctopusLike
