# P3 - Wave/Photonic Substrate Lane (波动/光子计算基底)

## 目标
探索波动/光子式 substrate 是否能作为 SOCS 的高速计算底层，提升多宇宙搜索与开放世界评估效率。

## 资源占比
**5%** (探索性，不干扰主线)

## 双重角色

### 角色1: Accelerator Lane (主要)
给主线提供加速能力：
- 快速评估候选结构
- 加速多宇宙筛选
- 给阿卡西提供更多样本

### 角色2: Alternative Substrate Lane (次要)
探索新的认知载体：
- 局部波动单元
- 模式耦合
- 散射介质记忆
- 非电子型传播规则

## 核心问题

不是"它有没有意识"，而是：
1. 同样预算下，能不能跑更多 universe？
2. 同样时间下，能不能筛更多候选？
3. 在不损失区分度的前提下，能不能提升吞吐？

## 实验阶段

### Phase 1: 软件模拟 (当前)
不要碰真实芯片，先做软件抽象：

```rust
// WaveSubstrateLike - 波动基底家族
struct WaveSubstrateConfig {
    // 波动传播参数
    wavelength: f32,           // 等效波长
    scattering_strength: f32,  // 散射强度
    mode_coupling: f32,        // 模式耦合系数
    
    // 可训练介质
    refractive_index_map: Vec<f32>,  // 折射率分布(可训练)
    absorption_mask: Vec<f32>,       // 吸收掩模
    
    // 计算抽象
    linear_transform_depth: usize,   // 线性变换深度
    patch_efficiency: bool,          // 是否使用 patch-efficient adjoint
}
```

### Phase 2: 最小验证

**测试1: 前向传播加速**
```
标准电子 substrate: O(N²) 矩阵乘法
波动 substrate: O(N) 波传播模拟

验证: 同样精度下，波动方式是否更快？
```

**测试2: 结构可分辨性保留**
```
在波动 substrate 上跑:
- OctopusLike vs RandomSparse
- 测量 CWCI 区分度是否保留

验证: 加速是否以牺牲区分度为代价？
```

**测试3: 大规模并行筛选**
```
用波动 substrate 做:
- 128 universe 的前向评估
- 只保留摘要的阿卡西式筛选

验证: 吞吐提升是否线性？
```

### Phase 3: 与 SOCS 整合 (如果 Phase 2 成功)

```
SOCS Runtime Layer
       ↓
WaveSubstrateAdapter
       ↓
Wave/Photonic Simulation (software)
       ↓
Physical Implementation (future)
```

## 限制与约束

| 约束 | 影响 | 应对 |
|-----|------|------|
| 线性系统 | 表达能力受限 | 专注推理/筛选，不替代非线性结构 |
| 光学非线性缺失 | 复杂动态难实现 | 保留电子层做非线性部分 |
| 制造容差 | 真实芯片风险 | Phase 1-2 只软件验证 |
| 校准复杂度 | 部署成本高 | 成功后考虑，不成功则纯软件价值 |

## 产出物
- `wave_substrate_bench.json` - 性能基准测试
- `cwci_fidelity_test.json` - CWCI 区分度验证
- `throughput_analysis.json` - 吞吐分析报告
- `integration_proposal.md` - 整合建议(如果成功)

## 中止条件
如果 Phase 1-2 显示：
- 加速比 < 2× 且 CWCI 区分度下降 > 10%
- 或者实现复杂度超过预期收益

则 P3 冻结，资源回归 P2.5。

## 与主线关系
```
P0/P1/P2.5 (电子 substrate)
        ↑
        └────── 评估候选、产生CWCI
        
P3 (波动 substrate - 如果成功)
        ↓
        └────── 加速评估、提升吞吐、不改变结果
```

P3 不是认知结构候选，而是**计算基底加速器**。
