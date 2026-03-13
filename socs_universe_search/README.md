# SOCS Universe Search Engine

## Vision
多元宇宙架构搜索：从简单局部规则出发，通过大规模并行探索，找出能涌现认知能力的结构组合。

## Core Principle
> "不是阿卡西给答案，而是探索-记录-传承-进化"

- **探索**: 并行运行大量不同架构的宇宙
- **记录**: 详细记录每个宇宙的动力学、事件、成败
- **传承**: 跨代保留统计摘要和结构偏置（非具体答案）
- **进化**: 在护栏内自优化

## Architecture Families

### 1. 线虫型 (C. elegans-like)
- 小规模 (300-500单元)
- 稀疏固定拓扑
- 关键hub节点
- 快速反射 + 简单状态机

### 2. 章鱼型 (Octopus-like)  
- 高度分布式
- 弱中央、强局部自治
- 臂部局部智能
- 全局协调来自团簇竞争

### 3. 天心脉冲型 (Tianxin Pulse)
- 强节律驱动
- 中枢广播窗口
- 相位耦合
- 事件驱动同步

### 4. 随机稀疏型 (Random Sparse)
- 随机连接
- 低平均度
- 无预设结构
- 纯涌现

### 5. 模块网格型 (Modular Lattice)
- 规则拓扑
- 模块化组织
- 层次化连接
- 局部密集、全局稀疏

## Plasticity Families

1. **Hebbian**: 相关性学习
2. **STDP**: 时间依赖可塑性
3. **Predictive**: 预测误差驱动
4. **Reward-Modulated**: 三因素学习
5. **Mixed**: 动态组合

## Broadcast Families

1. **None**: 纯局部
2. **Local Cluster**: 团簇内广播
3. **Sparse Global**: 稀疏全局连接
4. **Gated Workspace**: 门控工作空间

## Memory Coupling

1. **L1-only**: 仅局部痕迹
2. **L1+L2**: 加入团簇记忆
3. **L1+L2+L3(weak)**: 弱跨代偏置

## 6 Dynamics Gates (Validation)

验证目标不是benchmark分数：

1. ✅ **Attractor Formation** - 稳定吸引子
2. ✅ **Memory Persistence** - 记忆保持
3. ✅ **Reorganization** - 环境变化后重组
4. ✅ **Cluster Specialization** - 团簇分化
5. ✅ **Broadcast Emergence** - 全局广播涌现
6. ✅ **Failure Recovery** - 故障恢复

## Code-World Consciousness Index (CWCI)

**核心原则**: 不证明"代码意识 = 物理意识"，只定义**代码世界内部可测、可量化、可进化**的功能标准。

### 6大能力维度

| 维度 | 名称 | 可测指标 |
|-----|------|---------|
| C1 | 持续自体性 | identity continuity, recovery capacity |
| C2 | 全局整合 | broadcast occupancy, cross-cluster coupling |
| C3 | 反身建模 | self-prediction accuracy, error localization |
| C4 | 可塑性学习 | adaptation latency, cross-environment transfer |
| C5 | 价值持续性 | goal retention, preference stability |
| C6 | 元优化能力 | self-modification benefit, architecture adaptation |

### 意识等级 (C0-C6)
- **C0-C3**: 基础反应到反身体
- **C4**: 学习体 - 能跨情境学习（当前实现目标）
- **C5**: 自优化体 - 能在护栏内改进自己
- **C6**: 超脑候选 - 大规模、多宇宙、长时程

📖 [CWCI详细文档](CWCI.md)

## Directory Structure

```
socs_universe_search/
├── src/
│   ├── lib.rs                    # 核心库
│   ├── universe_config.rs        # 宇宙配置
│   ├── universe_runner.rs        # 宇宙运行器
│   ├── search_scheduler.rs       # 搜索调度器
│   ├── evaluation.rs             # 6动力学门评估
│   ├── consciousness_index.rs    # CWCI 6维度评估
│   ├── cwci_report.rs            # CWCI报告生成
│   ├── telemetry.rs              # 遥测系统
│   ├── stress_profile.rs         # 压力环境配置
│   ├── experiment_plan.rs        # 实验计划
│   └── config_generator.rs       # 配置生成器
├── outputs/                      # 输出目录
│   ├── *_telemetry.csv           # 时序遥测数据
│   ├── *_summary.json            # 宇宙摘要
│   ├── hall_of_fame.jsonl        # 顶级结构
│   ├── graveyard.jsonl           # 失败结构
│   └── cwci_report.json          # CWCI分析报告
└── CWCI.md                       # CWCI详细文档
```

## Constraints (Red Lines)

1. **热力学约束**: 有限能量/资源/计算预算
2. **反作弊约束**: 
   - 局部信息-only
   - 低带宽
   - 不可直接注入答案
   - 不可神谕

## Usage

### 运行First8批次（24个宇宙）

```bash
cargo run --bin run_first8_batch --release
```

输出：
- `outputs/*_telemetry.csv` - 时序遥测
- `outputs/*_summary.json` - 宇宙摘要
- `outputs/hall_of_fame.jsonl` - 顶级结构
- `outputs/graveyard.jsonl` - 失败模式

### 生成CWCI分析报告

```bash
cargo run --bin cwci_report --release
```

输出CWCI统计：
- 6大能力维度平均分
- 意识等级分布
- 架构家族排名
- 压力环境排名
- Top Performers
- 优化建议

### 程序化使用

```rust
use socs_universe_search::{
    universe_config::UniverseConfig,
    universe_runner::run_universe_once,
    consciousness_index::evaluate_cwci,
};

// 配置并运行宇宙
let cfg = UniverseConfig::default_for_family(
    ArchitectureFamily::OctopusLike, 
    0,  // universe_id
    42  // seed
);
let summary = run_universe_once(&cfg)?;

// 访问CWCI评估
if let Some(ref cwci) = summary.cwci {
    println!("Level: {}", cwci.level.as_str());
    println!("Score: {:.3}", cwci.cwei_score);
    println!("Capabilities: {}/6", cwci.passed_capabilities);
}
```

## Relation to SOCS

SOCS Universe Search是SOCS的研究方法层：
- SOCS = 可塑性认知基底（本体）
- Universe Search = 如何找出最优SOCS配置（方法）
- Akashic Records = 跨宇宙实验数据库（记忆）

