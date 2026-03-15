# GPU Integration

> **Status**: P0 - IN PROGRESS  
> **Priority**: BLOCKING  
> **Target**: 超脑稳定挂载到 GPU

---

## 目标定义

超脑核心计算模块可调用 GPU 加速，实现：
- 模型推理 offload 到 GPU
- 显存管理与动态分配
- 错误恢复与降级机制
- 稳定运行 >24h 无崩溃

---

## 成功标准 (ALL MUST PASS)

| 指标 | 最小值 | 目标值 | 验证方法 |
|:-----|:------:|:------:|:---------|
| GPU Utilization | >60% | >80% | nvidia-smi dmon |
| VRAM Usage | <90% | <80% | nvidia-smi |
| Token Throughput | >1000 tok/s | >2000 tok/s | 自定义 benchmark |
| 稳定运行时长 | >1h | >24h | 连续运行测试 |
| 错误率 | <1% | <0.1% | 日志监控 |

### 最小验证实验
```bash
# 1小时内必须完成
python3 gpu_stress_test.py --duration 3600 --model gpt-oss-120b
# 预期: GPU util >60%, 显存稳定, 无 OOM/崩溃
```

---

## 禁止事项

- ❌ 实验超过1小时（强制 Ralph Window 3600s）
- ❌ 未经测试直接上生产模型
- ❌ 忽略显存泄漏（必须监控峰值后释放）
- ❌ 单点故障无降级（必须保留CPU fallback）
- ❌ 在不稳定驱动上开发（必须使用验证版本）

---

## 1小时内可执行实验清单

### 实验1: GPU 基础连接 (15min)
```python
# test_gpu_basic.py
import torch
assert torch.cuda.is_available()
assert torch.cuda.device_count() >= 1
# 显存分配测试
x = torch.randn(1000, 1000).cuda()
del x; torch.cuda.empty_cache()
print("✅ GPU基础连接通过")
```

### 实验2: 模型加载与推理 (30min)
```python
# test_gpu_inference.py
# 加载 gpt-oss-120b 到 GPU
# 执行 100 次推理
# 监控: GPU util, VRAM, latency
# 必须在 30min 内完成，记录指标
```

### 实验3: 显存压力测试 (30min)
```python
# test_vram_stress.py
# 模拟大 batch/long sequence
# 监控峰值显存使用
# 验证自动释放机制
# 禁止: OOM crash
```

### 实验4: 稳定性长测 (60min, 单独窗口)
```python
# test_gpu_stability.py --duration 3600
# 连续推理 1 小时
# 每 5min 记录一次指标
# 成功标准: 零崩溃，零OOM，util >60%
```

---

## 监控指标

### 实时脚本
```bash
# 启动 GPU 监控
watch -n 1 nvidia-smi

# 日志记录
nvidia-smi dmon -s pucm -f gpu_log.csv &
```

### 关键指标
- `gpu_util`: GPU 利用率 %
- `mem_used`: 显存使用 MB
- `temperature`: 温度 °C
- `power_draw`: 功耗 W
- `ecc_err`: ECC 错误计数

---

## 当前状态

| 组件 | 状态 | 阻塞问题 |
|:-----|:----:|:---------|
| CUDA 驱动 | ⏸️ 待验证 | 版本兼容性 |
| PyTorch GPU | ⏸️ 待验证 | 编译/安装 |
| 模型加载 | ⏸️ 待验证 | 显存需求 |
| 推理管道 | ⏸️ 待验证 | batch size |
| 错误处理 | ⏸️ 待验证 | fallback 机制 |

---

## 下一步动作

1. [ ] 验证 CUDA 驱动版本
2. [ ] 安装 PyTorch with CUDA
3. [ ] 运行实验1 (基础连接)
4. [ ] 运行实验2 (模型加载)
5. [ ] 运行实验4 (稳定性测试，1小时窗口)

---

## 完成定义

当所有成功标准满足，且 `test_gpu_stability.py --duration 3600` 通过时，
本目录状态更新为 ✅ COMPLETE，项目进入 heterogeneous/ 阶段。
