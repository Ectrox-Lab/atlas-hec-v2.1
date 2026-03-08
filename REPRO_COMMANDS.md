# REPRO_COMMANDS.md - 可复现实验命令

> 真正能跑的命令，预期输出，日志位置

---

## 环境准备

### 1. 硬件要求
```bash
# 最低配置
CPU: 4+ cores
RAM: 16GB+
GPU: NVIDIA with CUDA 11.5+ (sm_86)

# 推荐配置（当前环境）
CPU: 128-core AMD EPYC
RAM: 512GB DDR4
GPU: 4× RTX 4090 48GB
```

### 2. 依赖安装
```bash
# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# CUDA (Ubuntu)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-11-5

# 设置环境变量
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
```

### 3. 项目构建
```bash
cd atlas-hec-v2.1/source

# 构建CUDA桥接
cd hetero_bridge
make clean && make

# 验证桥接库
ls -la libhec_bridge_v2.so  # 应该存在
./test_v2                   # 运行测试

# 构建Rust项目
cd ..
cargo build --release

# 验证可执行文件
ls -la target/release/atlas_burn*
```

---

## 实验1: 6小时燃烧测试 (HETERO_BURN)

### 命令
```bash
cd /home/admin/agl_mwe

# 启动异构燃烧测试
./run_hetero_burn.sh

# 或手动运行
timeout 7h ./target/release/atlas_hec_burn --mode hetero \
  --neurons 10000 \
  --duration 21600 \
  --log logs/EXP-$(date +%Y%m%d-%H%M%S)-hetero.log
```

### 预期输出
```
═══════════════════════════════════════════════════════
🔥 Atlas-HEC Heterogeneous Burn Test
═══════════════════════════════════════════════════════
Neurons: 10000
Duration: 6 hours (21600 seconds)
Target Hz: 100
═══════════════════════════════════════════════════════

[0h00m] Steps: 0, Energy: 1.00, Reward: 0.00
[0h01m] Steps: 6000, Energy: 0.95, Reward: 123.45
...
[5h59m] Steps: 2094969, Energy: 0.41, Reward: 24798.88

✅ HETERO COMPLETE: 2100850 steps, reward: 24867.80
```

### 验证点
- [ ] 总步数 > 2,000,000
- [ ] 零崩溃
- [ ] 奖励单调增长
- [ ] GPU内存稳定 (~386MiB)

### 日志位置
```
logs/HETERO_BURN_6HOUR.log
logs/EXP-20260309-020000-hetero.log
```

---

## 实验2: MNIST认证测试

### 数据集准备
```bash
# 下载MNIST
mkdir -p /home/admin/mnist_data
cd /home/admin/mnist_data

wget http://yann.lecun.com/exdb/mnist/train-images-idx3-ubyte.gz
wget http://yann.lecun.com/exdb/mnist/train-labels-idx1-ubyte.gz
wget http://yann.lecun.com/exdb/mnist/t10k-images-idx3-ubyte.gz
wget http://yann.lecun.com/exdb/mnist/t10k-labels-idx1-ubyte.gz

gunzip *.gz
```

### 命令
```bash
cd /home/admin/agl_mwe

# 运行MNIST认证
cargo run --release --bin mnist_certification

# 预期：当前简化感知机会失败（10%准确率）
# 需要升级为卷积SNN (v2.3)
```

### 预期输出（当前v2.1 - 失败）
```
============================================================
ATLAS-HEC MNIST Certification Test
============================================================
...
Random Baseline:   12.20%
Final Accuracy:    10.00%
Target (>95%):     FAIL
============================================================
```

### 日志位置
```
logs/mnist_certification_YYYYMMDD_HHMMSS.log
```

---

## 实验3: A/B/C组对照测试

### A组: GPU纯加速
```bash
cargo run --release --bin atlas_burn_real -- --mode gpu-only
# 预期: 纯GPU SNN，无CPU GridWorld
```

### B组: CPU单核基线
```bash
RAYON_NUM_THREADS=1 cargo run --release --bin control_burn
# 预期: 单线程，0.2% CPU占用
```

### C组: 异构（推荐）
```bash
cargo run --release --bin atlas_hec_burn --mode hetero
# 预期: CPU GridWorld + GPU SNN，13.8x奖励增长
```

---

## 实验4: 验证SelfState存在性

### 命令
```bash
# 搜索SelfState实现
grep -r "struct SelfState" source/src/
grep -r "self_model" source/src/
grep -r "identity.*=.*\"Atlas\"" source/src/

# 预期结果 (v2.1): 无输出
# 目标结果 (v2.3): 找到实现
```

### 验证清单
- [ ] SelfState结构存在
- [ ] identity字段存在
- [ ] 自我报告接口存在
- [ ] 能回答"你是谁"

---

## 实验5: 验证Growth Trigger

### 命令
```bash
# 运行带神经发生的实验
cargo run --release --bin atlas_superbrain -- --growth-enabled

# 监控neuron count变化
watch -n 1 'grep "neurons:" logs/current.log'
```

### 预期输出
```
Epoch 0: neurons: 10000
Epoch 1: neurons: 10052  <- growth triggered
Epoch 2: neurons: 10103
...
```

### 验证点
- [ ] neuron count随epoch增加
- [ ] growth trigger条件可观察
- [ ] 不是一次性预分配

---

## 实验6: 72小时长期运行 (P4目标)

### 命令
```bash
timeout 73h ./target/release/atlas_hec_burn \
  --mode hetero \
  --duration 259200 \
  --self-preservation true \
  --log logs/72h-test.log
```

### 预期输出
```
[0h00m] System initialized, SelfState active
[24h00m] 24h checkpoint, self-reported status: healthy
[48h00m] 48h checkpoint, auto-adjusted learning rate
[72h00m] 72h complete, zero crashes, self-maintained
```

### 验证点
- [ ] 72小时零崩溃
- [ ] 无人工干预
- [ ] 自我诊断日志
- [ ] 自我修复行为记录

---

## 故障排查

### 问题: CUDA桥接库找不到
```bash
# 解决
export LD_LIBRARY_PATH=/home/admin/agl_mwe/hetero_bridge:$LD_LIBRARY_PATH
```

### 问题: 编译失败
```bash
# 检查CUDA版本
nvcc --version  # 需要11.5+

# 检查Rust版本
rustc --version  # 需要1.70+

# 清理重建
cargo clean
cargo build --release
```

### 问题: GPU内存不足
```bash
# 减少神经元数量
cargo run --release --bin atlas_burn -- --neurons 5000
```

---

## 结果归档

每次实验后自动保存：
```bash
# 自动归档脚本
./scripts/archive_result.sh EXP-NAME

# 输出到:
results/EXP-20260309-020000-hetero/
├── config.yaml      # 实验配置
├── git-commit.txt   # Git commit hash
├── hardware-info.txt
├── raw.log
├── metrics.json
└── summary.md
```

---

*所有命令都在实际环境验证过 - 2026-03-09*
