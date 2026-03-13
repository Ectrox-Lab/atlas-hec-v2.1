# 🔥 HEAVY COMPUTE EXPERIMENT MODE

## 这是你要的实验

不再是轻量机制验证，而是**真正的资源压榨实验**。

| 指标 | 轻量模式 | **重载模式** |
|------|----------|--------------|
| CPU | 0-2% | **70-95%** |
| RAM | 20-50GB | **200-400GB** |
| 核心状态 | 大量 idle | **全部满载** |
| 计算类型 | Sleep-heavy | **Pure compute** |
| 实验类型 | 日志心跳 | **O(N^2) 矩阵运算** |

## 三个并行实验

### 1. HEAVY AKASHIC (`heavy_akashic.py`)

**内存目标**: 200-400GB

**核心运算**:
- 50,000 候选者的距离矩阵 (50k × 1k = 400MB)
- O(N²) 成对距离计算
- K-means 聚类 (50 iterations)
- 谱系分歧分析 (KS-test like)
- DAG 压缩 (图遍历)
- SVD 矩阵分解

**状态常驻内存**:
- Lineage graph (500k 节点)
- Phenotype index (50k × 128-dim vectors)
- Conflict matrix (1k × 1k)

### 2. HEAVY 128 UNIVERSE (`heavy_128_universe.py`)

**CPU目标**: 70-90% on 128C

**核心运算**:
- 每个 universe: 10,000 agents × 64-dim state
- 128 个 universe 并行进化
- Tournament selection (O(N) per generation)
- SBX crossover (vectorized but heavy)
- O(N²) cross-universe similarity matrix
- 谱聚类 (Eigendecomposition)
- PCA on 320k states

**跨宇宙分析**:
- Pairwise phenotype comparison
- Divergence detection
- Clustering by behavior

### 3. HEAVY FAST GENESIS (`heavy_fast_genesis.py`)

**目标**: 10,000+ 候选者大种群进化

**核心运算**:
- 每个候选者: 256-dim genotype
- 6 目标 fitness 评估
- 每个 fitness: 1000-step micro-simulation
- NSGA-II 非支配排序 (O(MN²))
- Crowding distance 计算
- Conflict graph 构建 (O(N²))
- Surrogate model 训练/推理

**高强度变异**:
- Tournament selection
- Blend crossover (Beta distribution)
- Multi-point mutation

## 启动命令

```bash
cd /home/admin/atlas-hec-v2.1-repo
./superbrain/heavy_mode/launch_heavy_mode.sh
```

## 监控

```bash
# 实时资源使用
watch -n 1 'top -bn1 | head -20'

# 内存使用
watch -n 1 'free -h'

# 日志
tail -f heavy_logs/*.log
```

## 停止

```bash
./superbrain/heavy_mode/stop_heavy_mode.sh
```

## 资源预期

运行 1 小时后应该看到:

```
[MONITOR] T+1.0h | CPU: 85% | RAM: 320/466GB (69%) | Load: 120.5
```

如果 CPU < 50% 或 RAM < 100GB，说明实验设计有问题。

## 与轻量模式的区别

| 轻量模式 | 重载模式 |
|----------|----------|
| `time.sleep(300)` | **NO SLEEP** |
| 写一行日志，sleep | **每一轮都烧CPU** |
| JSON 文件读写 | **大矩阵常驻内存** |
| 128 个各写各的 CSV | **O(N²) 跨宇宙比较** |
| 20 个体慢慢玩 | **10k 候选者并行筛选** |
| "文件在增长" | **CPU/RAM 吃满** |

## 硬指标

以后汇报必须给:
- ✅ 平均 CPU 利用率
- ✅ 峰值 CPU 利用率  
- ✅ RAM 常驻占用
- ✅ 峰值 RAM 占用
- ✅ 每小时真实计算量

不接受:
- ❌ "文件在增长"
- ❌ "进程在活着"
- ❌ "日志很多"
- ❌ "候选在生成"

---

**这才是你要的实验。**
