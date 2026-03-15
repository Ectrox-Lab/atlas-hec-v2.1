# Heterogeneous Architecture

> **Status**: P0 - QUEUED (Blocked by gpu_integration)  
> **Priority**: BLOCKING  
> **Target**: CPU+GPU 异构专用架构完善

---

## 目标定义

构建 CPU+GPU 协同工作的专用架构，实现：
- CPU 负责任务调度、数据预处理、逻辑控制
- GPU 负责大规模并行计算、模型推理
- 流水线并行，最小化数据搬运
- 动态负载均衡，避免资源闲置
- 故障时自动降级到 CPU-only 模式

---

## 成功标准 (ALL MUST PASS)

| 指标 | 最小值 | 目标值 | 验证方法 |
|:-----|:------:|:------:|:---------|
| CPU+GPU 同时满载 | >50% each | >70% each | htop + nvidia-smi |
| 数据搬运 overhead | <30% | <15% | profiling |
| 端到端吞吐 | >baseline | >1.5x baseline | benchmark |
| 故障降级时间 | <10s | <5s | 模拟故障测试 |
| 稳定运行 | >1h | >24h | 连续测试 |

### 最小验证实验
```bash
# 1小时内必须完成
python3 heterogeneous_stress_test.py --duration 3600 --cpu-workers 4 --gpu-batch 8
# 预期: CPU util >50%, GPU util >50%, 无 pipeline stall
```

---

## 禁止事项

- ❌ CPU 或 GPU 单方面闲置（必须同时满载）
- ❌ 频繁数据搬运（必须 batch 化）
- ❌ 硬编码调度策略（必须动态自适应）
- ❌ 实验超过1小时（Ralph Window 3600s）
- ❌ 无降级方案（必须支持 CPU-only fallback）
- ❌ 忽略内存带宽瓶颈（必须 profiling）

---

## 1小时内可执行实验清单

### 实验1: CPU-GPU 分工验证 (20min)
```python
# test_cpu_gpu_partition.py
# CPU: 数据加载 + 预处理
# GPU: 模型推理
# 验证: 两者同时运行，无等待
```

### 实验2: Pipeline 并行 (30min)
```python
# test_pipeline_parallel.py
# 构建 3-stage pipeline:
#   Stage1: CPU 预处理 -> Stage2: GPU 推理 -> Stage3: CPU 后处理
# 目标: pipeline 无 stall，吞吐 > sequential
```

### 实验3: 负载均衡 (30min)
```python
# test_load_balancing.py
# 动态调整 batch size 和 worker 数
# 目标: CPU util ≈ GPU util（差距 <20%）
# 禁止: 一方满载，另一方闲置
```

### 实验4: 故障降级 (20min)
```python
# test_fallback.py
# 模拟 GPU 故障
# 验证: 自动切换到 CPU-only，延迟增加但服务不中断
# 恢复 GPU 后自动切回
```

### 实验5: 异构稳定性长测 (60min, 单独窗口)
```python
# test_hetero_stability.py --duration 3600
# 连续运行 1 小时
# 监控: CPU util, GPU util, memory bw, throughput
# 成功标准: 两者同时 >50%，零崩溃
```

---

## 架构组件

### CPU 职责
```yaml
tasks:
  - 数据加载 (I/O bound)
  - 预处理 (tokenization, padding)
  - 调度决策 (dynamic batching)
  - 后处理 (decoding, formatting)
  - 错误处理 / fallback 控制

threads: 4-8 workers
memory: 预留 16GB+ for data buffer
```

### GPU 职责
```yaml
tasks:
  - 模型前向 (inference)
  - 注意力计算 (parallel)
  - 矩阵运算 (GEMM)

memory: 24GB+ VRAM (3x4090 = 72GB total)
utilization: target >70%
```

### 数据流
```
Input → [CPU: 预处理] → Queue → [GPU: 推理] → Queue → [CPU: 后处理] → Output
         ↓                    ↓                   ↓
      Prefetch           Batch调度           Stream output
      (overlap)          (dynamic)            (non-blocking)
```

---

## 瓶颈识别清单

| 瓶颈类型 | 症状 | 诊断方法 | 解决策略 |
|:---------|:-----|:---------|:---------|
| 数据搬运 | GPU util 低，CPU 等待 | profiling | 增大 batch，prefetch |
| 内存带宽 | throughput  plateau | memory profiler | 压缩数据，pin memory |
| 调度不均 | CPU/GPU util 差距大 | htop + nvidia-smi | 动态调整 workers |
| 串行依赖 | pipeline stall | timeline tracing | 异步化，重叠计算 |

---

## 当前状态

| 组件 | 状态 | 依赖 |
|:-----|:----:|:-----|
| CPU 调度器 | ⏸️ QUEUED | gpu_integration ✅ |
| GPU 执行器 | ⏸️ QUEUED | gpu_integration ✅ |
| 队列系统 | ⏸️ QUEUED | gpu_integration ✅ |
| 负载均衡器 | ⏸️ QUEUED | gpu_integration ✅ |
| 故障检测 | ⏸️ QUEUED | gpu_integration ✅ |
| 降级机制 | ⏸️ QUEUED | gpu_integration ✅ |

---

## 下一步动作

1. [ ] 等待 gpu_integration/ 完成
2. [ ] 设计 CPU-GPU 分工接口
3. [ ] 实现 pipeline 框架
4. [ ] 运行实验2 (pipeline 并行)
5. [ ] 运行实验5 (稳定性测试，1小时窗口)

---

## 完成定义

当 `test_hetero_stability.py --duration 3600` 通过，
且 CPU+GPU 同时满载 >50%，本目录状态更新为 ✅ COMPLETE，
项目进入 sota_benchmark/ 阶段。
