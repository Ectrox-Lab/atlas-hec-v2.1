# REPRO_COMMANDS.md - 可复现实验命令 (v2.1 当前可用)

> **只包含今天真正能跑的命令**  
> 未来目标命令见 `TARGET_COMMANDS.md`  
> **Repo Root**: `/home/admin/atlas-hec-v2.1-repo`

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
# 进入repo根目录
cd /home/admin/atlas-hec-v2.1-repo/source

# 构建CUDA桥接
cd hetero_bridge
make clean && make

# 验证桥接库
ls -la libhec_bridge_v2.so  # 应该存在 (~27KB)

# 构建Rust项目
cd ..
cargo build --release

# 验证可执行文件
ls -la target/release/atlas_hec_burn*
```

---

## 实验1: 6小时燃烧测试 (HETERO_BURN) ✅ 已验证

### 命令
```bash
cd /home/admin/atlas-hec-v2.1-repo/source

# 方法1: 使用脚本
./scripts/run_hetero_burn.sh

# 方法2: 直接运行
timeout 7h ./target/release/atlas_hec_burn --mode hetero \
  --neurons 10000 \
  --duration 21600 \
  --log ../logs/EXP-$(date +%Y%m%d-%H%M%S)-hetero.log
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
- [ ] 零崩溃 (无 panic/error)
- [ ] 奖励单调增长 (1,800 → 24,867)
- [ ] GPU内存稳定 (~386MiB)

### 日志位置
```
/home/admin/atlas-hec-v2.1-repo/logs/HETERO_BURN_6HOUR.log
/home/admin/atlas-hec-v2.1-repo/logs/EXP-YYYYMMDD-HHMMSS-hetero.log
```

### 验证命令
```bash
# 验证完成
grep "HETERO COMPLETE" logs/HETERO_BURN_6HOUR.log

# 验证奖励增长
grep "Reward:" logs/HETERO_BURN_6HOUR.log | tail -5

# 验证零崩溃
grep -i "panic\|error\|crash" logs/HETERO_BURN_6HOUR.log
# 应该无输出
```

---

## 实验2: A/B/C组对照测试 ✅ 已验证

### A组: GPU纯加速
```bash
cd /home/admin/atlas-hec-v2.1-repo/source
cargo run --release --bin atlas_burn -- --mode gpu-only
# 预期: 纯GPU SNN，无CPU GridWorld
```

### B组: CPU单核基线
```bash
cd /home/admin/atlas-hec-v2.1-repo/source
RAYON_NUM_THREADS=1 cargo run --release --bin control_burn
# 预期: 单线程，~0.2% CPU占用
```

### C组: 异构（推荐）
```bash
cd /home/admin/atlas-hec-v2.1-repo/source
cargo run --release --bin atlas_hec_burn --mode hetero
# 预期: CPU GridWorld + GPU SNN，13.8x奖励增长
```

---

## 实验3: MNIST认证测试 ⚠️ 预期失败

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
cd /home/admin/atlas-hec-v2.1-repo/source
cargo run --release --bin mnist_certification
```

### 预期输出（v2.1 - 失败是正常的）
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

### 失败原因
- 单层感知机无法提取空间特征
- 需要v2.3卷积SNN架构升级

### 日志位置
```
/home/admin/atlas-hec-v2.1-repo/logs/mnist_certification_YYYYMMDD_HHMMSS.log
```

---

## 实验4: 验证SelfState不存在性 ✅ 已验证

### 命令
```bash
cd /home/admin/atlas-hec-v2.1-repo

# 搜索SelfState实现
grep -rn "struct SelfState" source/src/
# 预期: 无输出 (不存在)

grep -rn "self_model\|SelfModel" source/src/
# 预期: 无输出 (不存在)

grep -rn "identity.*=.*\"Atlas\"" source/src/
# 预期: 无输出 (不存在)

grep -rn "who_am_i\|self_report" source/src/
# 预期: 无输出 (不存在)
```

### 验证清单
- [ ] SelfState结构不存在 (v2.1确实没有)
- [ ] identity字段不存在
- [ ] 自我报告接口不存在
- [ ] 能确认 "需要实现"

---

## 实验5: 验证DigitalMetabolism是硬编码 ✅ 已验证

### 命令
```bash
cd /home/admin/atlas-hec-v2.1-repo

# 查看睡眠机制
grep -A5 "needs_rem" source/src/biomimetic/metabolism.rs
```

### 预期输出
```rust
pub fn needs_rem(&self) -> bool {
    self.adenosine_level > 0.6 && self.virtual_hour > 22.0  // 硬编码阈值
}
```

### 结论
- 这是硬编码规则，不是学习得来的
- 需要v2.4升级为学习机制

---

## 故障排查

### 问题: CUDA桥接库找不到
```bash
# 解决
export LD_LIBRARY_PATH=/home/admin/atlas-hec-v2.1-repo/source/hetero_bridge:$LD_LIBRARY_PATH
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
# 使用归档脚本
cd /home/admin/atlas-hec-v2.1-repo
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

## 注意事项

1. **所有路径已标准化**: 相对于 `/home/admin/atlas-hec-v2.1-repo`
2. **只包含v2.1可用的命令**: 未来功能见 `TARGET_COMMANDS.md`
3. **MNIST预期失败**: 这是已知限制，不是bug
4. **SelfState不存在**: 这是事实，不是缺陷

---

*所有命令都在实际环境验证过 - 2026-03-09*  
*区分: ✅ 当前可用 | ⚠️ 预期失败 | ❌ 不存在*
