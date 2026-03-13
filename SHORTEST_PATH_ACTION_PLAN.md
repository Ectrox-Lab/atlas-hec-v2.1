# 最短路径行动计划：终极超脑结构搜索
## Shortest Path to Strongest Hyperbrain Structure

**目标**: 利用现有硬件（128C/512GB），在最短时间内实验找到最强超脑核心结构  
**当前硬件**: 已验证128并行 workers，CPU利用率96.9%  
**参数预算**: ~1B参数（1GB量级）  
**核心能力优先**: 逻辑分析/判断/调度/信息收集 > 知识量  

---

## 立即执行（接下来24-48小时）

### 任务1: P0-4 Task Effectiveness 验证
**目标**: 确认当前结构真的能完成任务，不是空转

```bash
# 执行命令
cd /home/admin/atlas-hec-v2.1-repo/code-diffusion
cargo run --bin p0_4_verify --release

# 验证指标
# - JS divergence < threshold
# - Trained vs untrained win rate > 60%
# - Reload determinism: 100% match
# - Multi-seed reproducibility: 5 seeds, variance < 5%
```

**通过标准**: 全部4项指标达标  
**失败行动**: 回退到R19/R20修复gradient机制

---

### 任务2: 异构执行体最小验证
**目标**: 确认CPU+GPU真能同时工作，不是"SIMD CPU + future PTX"

```bash
# 检查当前状态
cat /home/admin/atlas-hec-v2.1-repo/src/atlas_superbrain_real.rs | grep -A5 "PTX\|GPU\|CUDA"

# 如果还是"待后续版本"，立即执行：
# 方案A: 调用现有CUDA bridge（如有）
# 方案B: 用PyTorch/TensorFlow GPU wrapper做最小PoC
# 方案C: 直接用NVIDIA nccl/cuda-runtime写最小kernel
```

**最小PoC要求**:
- 矩阵乘法：CPU部分 vs GPU部分 vs 纯CPU对比
- 证明GPU确实在干活，且比CPU快
- 数据传输 overhead < 20%

---

### 任务3: Dominant Family (F_P3T4M4) 任务迁移验证
**目标**: 证明搜索引擎找到的结构真的能干活

**执行**:
1. 提取F_P3T4M4配置: P=3, T=4, M=4
2. 在P0-4任务上跑这个配置
3. 对比随机配置和F_P3T4M4配置的性能差异

**通过标准**: F_P3T4M4显著优于随机（p < 0.05）

---

## 本周内执行（接下来7天）

### 任务4: 8层记忆最小必要集合消融
**目标**: 找出哪些记忆层是真有用，哪些可以砍掉

**实验设计**:
```
Baseline: 8层全上
Ablation1: 去掉L5 Counterfactual
Ablation2: 去掉L6 Value/Constraint  
Ablation3: 只留L1-L4（事件+因果+策略+失败）
Ablation4: 只留L3-L4（策略+失败）
```

**评估**: 在相同计算预算下，哪组配置任务完成率最高

---

### 任务5: 1B参数规模压力测试
**目标**: 验证1B参数在现有硬件上是否可行

**执行**:
```bash
# 生成1B参数规模的合成workload
python3 -c "
import numpy as np
# 模拟1B参数 = 4GB float32
params = np.random.randn(1000000000).astype(np.float32)
print(f'Memory: {params.nbytes / 1e9:.2f} GB')

# 测试前向+反向
grad = np.random.randn(1000000000).astype(np.float32)
params += 0.001 * grad  # 模拟SGD step
print('Update complete')
"
```

**可行性判定**:
- 能加载: ✅ 继续
- 内存溢出: ❌ 需要模型并行/梯度检查点

---

### 任务6: 外部Benchmark Harness搭建
**目标**: 建立可以挑战SOTA的评测框架

**最小集合**:
1. **逻辑推理**: GSM8K (数学), BBH ( BIG-Bench Hard)
2. **代码生成**: HumanEval
3. **知识问答**: MMLU (选subset)
4. **长文本**: 自研长序列追踪任务

**执行**:
```bash
mkdir -p benchmarks/external
# 下载GSM8K
# 下载HumanEval  
# 编写harness: 输入→超脑→输出→评分
```

---

## 持续进行（Background）

### 任务7: 跨轮搜索引擎持续运行
**目标**: 继续发现更好的结构家族

**执行**:
```bash
# Round 11-15 (Optional strengthening)
cd /home/admin/atlas-hec-v2.1-repo/superbrain/evolution
python3 round_controller.py --rounds 11-15

# 或者：改mutation/crossover/immigrant配比做ablation
python3 round_controller.py --mutation-rate 0.8 --crossover-rate 0.15 --immigrant-rate 0.05
```

---

## 关键决策点

### Decision Gate 1: P0-4有效性（48小时内）
- **PASS**: 进入任务4/5/6并行推进
- **FAIL**: 冻结其他任务，全力修复gradient机制

### Decision Gate 2: 异构可行性（48小时内）  
- **PASS**: 开始写真实GPU kernel
- **FAIL**: 先最大化CPU效率（SIMD优化）

### Decision Gate 3: 1B可行性（7天内）
- **PASS**: 开始scale up实验
- **FAIL**: 优化到100M-500M参数，追求效率

---

## 当前状态→目标状态

| 维度 | 当前 | 目标 | 差距 |
|------|------|------|------|
| **任务有效性** | P0-4 ready | P0-4 proven | 48小时验证 |
| **异构执行** | CPU-only | CPU+GPU | 需要PoC |
| **结构搜索** | F_P3T4M4 dominant | 验证迁移 | 1周实验 |
| **记忆系统** | 8层全上 | 最小必要集 | 消融实验 |
| **参数规模** | 33K | 1B | 可行性测试 |
| **外部评测** | 无 | 有harness | 搭建中 |

---

## 一句话执行指令

> **接下来48小时**：验证P0-4有效性 + 异构PoC  
> **接下来7天**：消融实验 + 1B压力测试 + benchmark搭建  
> **持续背景**：搜索引擎继续跑R11-15或ablation  

**不达到P0-4验证通过，不宣布任何"完成"。**
