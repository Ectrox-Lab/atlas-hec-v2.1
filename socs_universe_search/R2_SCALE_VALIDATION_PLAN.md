# OctopusLike R2 Scale Validation Plan

## 一句话目标

> 10x 规模下 first degradation mode 是什么？

不是再拿第一，是判断结构极限。

## 强制输出指标

| 指标 | 1x 基线 | 10x 目标 | 退化阈值 | 说明 |
|-----|---------|----------|----------|------|
| CWCI retention | 0.688 | ≥ 0.585 (85%) | < 0.55 | 核心保持率 |
| Specialization | 0.948 | track | drop > 20% | 团簇分化 |
| Integration | 0.909 | track | drop > 20% | 信息整合 |
| Broadcast | 1.000 | track | drop > 20% | 广播效率 |
| Communication cost | baseline | measure | increase > 50% | 通信开销 |
| Broadcast coverage | baseline | measure | decrease > 30% | 广播覆盖 |
| Recovery gain | baseline | measure | degradation | 恢复能力 |
| Energy efficiency | baseline | measure | degradation | 能量效率 |
| **First degradation mode** | N/A | **identify** | trigger | 首要退化模式 |

## 实验设计

```yaml
scale: 10x
  - n_units: 100 → 1000
  - n_clusters: 动态
  - simulation_ticks: 5000

families:
  - OctopusLike (primary)
  - ModularLattice (baseline)
  - RandomSparse (chaos baseline)

scenarios: 3
  - RegimeShiftFrequent
  - ResourceScarcity
  - HighCoordinationDemand

seeds: 3
  - 11, 23, 37

total_runs: 3 × 3 × 3 = 27
```

## 输出要求

### 必须回答

1. **CWCI retention ≥ 85%?**
   - YES → Continue to 50x
   - NO → Identify first degradation mode

2. **First degradation mode**
   - Communication bottleneck?
   - Broadcast tyranny?
   - Energy collapse?
   - Recovery failure?
   - Over-synchronization?

3. **Scale-robust or structure-limited?**
   - Scale-robust → R3 50x
   - Structure-limited → R2.5 architecture refinement

## 执行命令

```bash
cd /home/admin/atlas-hec-v2.1-repo/socs_universe_search

# 修改 config 为 10x scale
# 运行实验
./target/release/run_first8_batch --scale 10x

# 生成 R2 专用报告
./target/release/cwci_report --phase R2

# 输出强制指标
cat outputs/R2_metrics.json
```

## 停机条件

- CWCI retention < 70%
- Any family collapse rate > 50%
- Communication cost explosion detected
