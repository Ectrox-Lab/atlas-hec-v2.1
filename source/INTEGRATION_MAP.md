# Bio-World v19 Integration Map

**Date**: 2026-03-09  
**Status**: Ready for Wiring

---

## Found Modules (Ready to Use)

| 指标 | 来源文件 | 输入 | 输出 | 动作 |
|------|---------|------|------|------|
| **r** | `src/candidates/e1_critical_coupling/src/bin/e1_overnight_batch.rs` | `&[f64]` phases | `f64` | **Wrap** |
| **CI** | `src/candidates/e1_critical_coupling/src/bin/e1_overnight_batch.rs` | `&[f64]` phases | `f64` | **Wrap** |
| **P** | `src/candidates/e3_percolation/src/main.rs` | `&[f64]` phases or graph | `f64` | **Wrap** |
| **CDI** | `src/bio_superbrain_interface/lineage_adapter.rs` | `LineageMemory` | `f32` | **Keep** (已接入) |

---

## Wrapper Interface (Target)

```rust
// bio_world_v19/metrics/mod.rs
pub struct StateVector {
    pub cdi: f64,
    pub ci: f64, 
    pub r: f64,
    pub n: usize,
    pub e: f64,
    pub h: f64,
}

pub fn compute_sync_order_parameter(phases: &[f64]) -> f64;
pub fn compute_condensation_index(phases: &[f64]) -> f64;
pub fn compute_percolation_ratio(phases: &[f64]) -> f64;
```

---

## Missing Components (Need Implementation)

| 组件 | 用途 | 当前状态 | 决策 |
|------|------|---------|------|
| **50×50×16 Grid Engine** | Agent movement, spatial world | 只有 16×16 GridWorld | **实现** |
| **Birth/Death/Food Loop** | Population dynamics (N) | Stub only | **实现** |
| **Hazard Rate h(t)** | Extinction prediction | Not found | **实现** |
| **Dynamic Network** | CI computation from edges | Static only | **实现** |

---

## Integration Target

```
bio_superbrain_interface/
├── experiment_runner.rs (当前: stub simulation)
│   └── 替换为: 实际 GridWorld + PopulationDynamics
│
└── 新接入:
    ├── StateVector (从 metrics/mod.rs)
    ├── HazardRateTracker
    └── 每 tick 输出 system_state.csv
```

---

## Action Plan

1. **Wrap metrics** (5 min)
   - 创建 `bio_world_v19/metrics/` 模块
   - 包装 r, CI, P 计算函数

2. **实现缺失组件** (30 min)
   - `core/grid.rs`: 50×50×16 3D world
   - `core/agent.rs`: Energy + phase + position
   - `core/population.rs`: Birth/death/food
   - `hazard/rate.rs`: h(t) = d(extinctions)/dt

3. **替换 stub** (10 min)
   - `experiment_runner.rs` 接真实 simulation
   - 输出统一 state vector 到 CSV

4. **验证** (5 min)
   - 运行 A-E matrix 测试
   - 确认 state vector 有值

---

## Decision

如果定点搜索后 4 类组件仍然缺失 → **立即实现，不再搜索**。
