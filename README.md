# Atlas-HEC v2.1

> 异构具身认知脉冲神经网络 (Heterogeneous Embodied Cognition)

## 🏆 核心成就

- ✅ 6小时零崩溃燃烧测试
- ✅ GridWorld环境学习（奖励增长13.8倍：1,800 → 24,867）
- ✅ 异构CPU+GPU架构验证
- ⏸️ MNIST视觉任务（推迟至v2.3）

## 📁 目录结构

```
atlas-hec-v2.1/
├── source/          # 核心源代码（Rust + CUDA）
│   ├── src/         # 52个Rust源文件
│   ├── hetero_bridge/  # CUDA桥接库
│   └── scripts/     # 构建脚本
├── logs/            # 6小时燃烧测试日志
├── docs/            # 架构文档和失败分析
└── experiments/     # 实验代码
```

## 🚀 快速开始

```bash
cd source

# 构建CUDA桥接
cd hetero_bridge
make

# 构建Rust项目
cd ..
cargo build --release

# 运行燃烧测试
./target/release/atlas_burn
```

## 📊 实验结果

| 组别 | 架构 | 步数 | 频率 | 状态 |
|------|------|------|------|------|
| A组 | GPU纯加速 | 2,100,934 | 97.3 Hz | ✅ |
| B组 | CPU单核 | 2,142,755 | 99.2 Hz | ✅ |
| C组 | 异构CPU+GPU | 2,100,850 | 97.3 Hz | ✅⭐ |

## 🎯 v2.3 路线图

- [ ] 卷积SNN架构
- [ ] MNIST >95% 准确率
- [ ] MiniGravity模板集成
- [ ] 数字达尔文生态

## 📝 详细文档

- [架构设计](docs/architecture.md)
- [实验日志](PROJECT_LOG.md)
- [MNIST失败分析](docs/failure_analysis.md)

---

*Atlas-HEC Project - Ectrox Lab*
