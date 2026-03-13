# Atlas-HEC v2.1

> **Heterogeneous Embodied Cognition Architecture**
> 
> 从"可搜索"到"可自我改进"的具身智能实验平台

[![Status](https://img.shields.io/badge/L4-In%20Progress-yellow)](PROJECT.md)
[![S1](https://img.shields.io/badge/S1-Complete-success)](superbrain/fast_genesis/generate_candidates.py)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 🎯 当前状态：L4 验证阶段

Atlas-HEC v2.1 正处于从**可持续搜索系统**向**自我改进系统**转型的关键验证期。

| 层级 | 状态 | 说明 |
|------|------|------|
| **L0** | ✅ 运行中 | Ralph 外骨骼，项目驱动与心跳 |
| **L1** | 🟡 就绪 | Continuity Probe 待启动 |
| **L2** | 🔴 阻塞 | 等待 L1 完成 |
| **L3** | 🔴 阻塞 | 等待 L2 完成 |
| **L4** | 🟡 **进行中** | E-T1-003 / E-COMP-002 实验对执行中 |

### 当前关键实验

**E-T1-003**: Task-1 Inheritance Effectiveness Run
- Round A (无继承): 150 candidates × 3 seeds ✅
- Round B (有继承): 150 candidates × 3 seeds ✅  
- Ablation (bias=0.0): 150 candidates × 3 seeds ✅
- **下一步**: Bridge/Mainline 评估

**E-COMP-002**: Compositional Reuse Validation
- 与 E-T1-003 绑定执行
- 验证改进是否来自模块复用而非隐性重造

---

## 🏆 核心成就

### 已完成

- ✅ **S1 完成**: Fast Genesis 支持 `--inheritance-package` 消费
- ✅ **Task-1 现实闭环**: Bridge → Mainline → Akashic 链路验证完成
- ✅ **P0-5 验证**: 真实梯度训练链打通 (LR=0.01, 7500 steps, dim=512)
- ✅ **进化搜索收敛**: F_P3T4M4 主导家族出现 (E-EVO-003)
- ✅ **异构执行 PoC**: CPU + GPU 协调环境验证

### 进行中

- 🟡 **L4 验证**: Round A/B 对比实验 (450 candidates 已生成)
- 🟡 **组合性验证**: 模块复用率分析 (E-COMP-002)

---

## 📁 目录结构

```
atlas-hec-v2.1/
├── superbrain/                 # 核心智能架构 (L0-L4)
│   ├── fast_genesis/          # S1: 候选生成 + inheritance 消费
│   ├── bridge/                # Shadow/Dry-Run 过滤
│   ├── mainline/              # 10k-task 严格验证
│   ├── akashic/               # 知识合成与继承包生成
│   └── task1_simulator/       # 异构执行协调环境
├── socs_universe_search/       # 进化搜索引擎
│   └── multiverse_engine/
│       └── akashic_memory_v2.py  # Task1KnowledgeArchive
├── benchmark_results/          # 实验结果
│   └── task1_inheritance/     # Round A/B/Ablation 数据
├── PROJECT.md                  # 主线文档 (L1-L4 定义)
└── README.md                   # 本文件
```

---

## 🚀 快速开始

### S1: 生成候选 (已验证)

```bash
# Round A: 纯探索 (对照组)
python superbrain/fast_genesis/generate_candidates.py \
  --count 50 --seed 1000 \
  --output benchmark_results/task1_inheritance/round_a/seed_1000

# Round B: 继承偏置 (实验组)
python superbrain/fast_genesis/generate_candidates.py \
  --count 50 --seed 1000 \
  --inheritance-package task1_inheritance_package.json \
  --bias-strength 0.7 \
  --output benchmark_results/task1_inheritance/round_b/seed_1000
```

### 查看生成报告

```bash
cat benchmark_results/task1_inheritance/ab_generation_report.md
```

---

## 📊 实验结果

### S1 验证结果

| 检查项 | 状态 | 说明 |
|--------|------|------|
| CLI 接口 | ✅ | `--inheritance-package`, `--bias-strength` 工作正常 |
| Round A 纯净性 | ✅ | 无继承包时 ≡ baseline |
| Manifest 记录 | ✅ | `inheritance_package_version`, `generation_mode` |
| 分布偏移可观测 | ✅ | `family_distribution.json`, `generation_log.json` |
| Bias 可关闭 | ✅ | `--bias-strength 0.0` 退回 uniform_exploration |

### 同 Seed 对比 (控制随机性)

| Seed | Round A (无继承) | Round B (bias=0.7) | Delta |
|------|------------------|-------------------|-------|
| 1000 | 9/50 approved | 18/50 approved | +9 |
| 1001 | 15/50 approved | 8/50 approved | -7 |
| 1002 | 12/50 approved | 10/50 approved | -2 |

*注：Approved families = F_P3T4M4, F_P2T3M3, F_P3T4M3*

---

## 🎯 路线图

### v2.1 当前 (L4 验证)
- [x] S1: Fast Genesis inheritance 消费
- [ ] Bridge/Mainline 评估 (Round A/B)
- [ ] L4 判定: 会不会变强 + 是不是靠复用变强

### v2.2 展望 (L4 扩展)
- [ ] Task-1 自改进循环
- [ ] 多任务 reality loop
- [ ] 真异构执行体集成

### v2.3 ( postponed )
- [ ] 卷积 SNN 架构
- [ ] MNIST >95% 准确率

---

## 📚 关键文档

| 文档 | 说明 |
|------|------|
| [PROJECT.md](PROJECT.md) | **主线文档**: L1-L4 定义，实验注册表，当前状态总览 |
| [ab_generation_report.md](benchmark_results/task1_inheritance/ab_generation_report.md) | Round A/B 生成阶段报告 |
| [INHERITANCE_EFFECTIVENESS_RUN.md](benchmark_results/task1_mainline/INHERITANCE_EFFECTIVENESS_RUN.md) | E-T1-003 实验设计 |

---

## 🔬 实验注册表 (E-系列)

| 实验编号 | 级别 | 状态 | 关键结果 |
|----------|------|------|----------|
| E-P0-002 | P0 | ✅ PASS | 真实梯度训练链 |
| E-EVO-003 | 进化 | ✅ CONVERGED | F_P3T4M4 主导家族 |
| E-T1-002 | Task-1 | ✅ CLOSED | 第一现实验证链 |
| **E-T1-003** | **Task-1** | 🟡 **IN PROGRESS** | **Inheritance Effectiveness** |
| **E-COMP-002** | **组合性** | 🟡 **PLANNED** | **模块复用验证** |

---

*Atlas-HEC Project - Ectrox Lab*  
*当前版本: v1.1-S1-LOCKED → 等待 L4 判定*
