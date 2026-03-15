# SOTA Benchmark

> **Status**: P1 - QUEUED (Blocked by heterogeneous)  
> **Priority**: NON-BLOCKING (but required for publication)  
> **Target**: 主流AI智能模型SOTA测评完成

---

## 目标定义

完成与主流AI模型的全面对比测评，建立客观性能基准：
- 覆盖主流 LLM (GPT-4, Claude, Gemini, Llama, etc.)
- 覆盖主流任务 (推理、代码、数学、知识)
- 量化对比: 能力、效率、稳定性、成本
- 产生可发布的 benchmark 报告

---

## 成功标准 (ALL MUST PASS)

| 指标 | 最小值 | 目标值 | 验证方法 |
|:-----|:------:|:------:|:---------|
| 对比模型数 | ≥5 | ≥10 | 公开模型列表 |
| 评测维度 | 3 | 4 | 能力/效率/稳定性/成本 |
| 数据集覆盖率 | ≥3 tasks | ≥5 tasks | MMLU, HumanEval, GSM8K, etc. |
| 结果可复现 | 手动 | 自动脚本 | 一键复现 |
| 报告完成度 | 草稿 | 发布级 | 完整分析文档 |

### 最小验证实验
```bash
# 1小时内必须完成一个模型的评测
python3 sota_benchmark.py --model gpt-4 --tasks mmlu,humaneval --timeout 3600
# 预期: 在1小时内产生可对比的指标
```

---

## 禁止事项

- ❌ 只测 Atlas-HEC 自己（必须对比 SOTA）
- ❌ 选择性报告有利结果（必须完整透明）
- ❌ 实验超过1小时（Ralph Window 3600s）
- ❌ 使用未经验证的评测集（必须社区公认）
- ❌ 忽略统计显著性（必须多次采样）
- ❌ 混淆训练与推理成本（必须分别报告）

---

## 1小时内可执行实验清单

### 实验1: 单模型快速评测 (60min)
```python
# benchmark_single_model.py --model MODEL_NAME --timeout 3600
# 在1小时内完成:
#   - MMLU 子集 (100题)
#   - HumanEval 子集 (10题)
#   - 延迟测试 (100次推理)
#   - 显存占用峰值
# 输出: JSON 指标文件
```

### 实验2: Atlas-HEC 自检 (60min)
```python
# benchmark_atlas_hec.py --timeout 3600
# 同实验1的条件，测试 Atlas-HEC
# 确保对比条件一致
```

### 实验3: 对比分析 (30min, 分析阶段)
```python
# compare_results.py --baseline MODEL_A --target MODEL_B
# 生成对比表格和图表
# 计算相对优势/劣势
```

### 实验4: 成本分析 (30min)
```python
# analyze_cost.py
# 计算: $/1K tokens, $/task, 能耗/task
# 对比不同模型的性价比
```

---

## 评测维度

### 1. 能力 (Capability)
```yaml
metrics:
  - accuracy: 正确率
  - pass@k: 代码通过率
  - bleu/rouge: 生成质量

datasets:
  - MMLU: 知识问答
  - HumanEval: 代码生成
  - GSM8K: 数学推理
  - BBH: 复杂推理
  - MT-Bench: 对话能力
```

### 2. 效率 (Efficiency)
```yaml
metrics:
  - throughput: tokens/sec
  - latency: TTFT (time to first token)
  - total_time: 端到端时间
  - batch_efficiency: 随batch size扩展性

conditions:
  - same_hardware: 3x4090
  - same_batch: 1, 4, 8
  - same_sequence: 1K, 4K, 8K
```

### 3. 稳定性 (Stability)
```yaml
metrics:
  - success_rate: 完成率
  - error_rate: 崩溃/错误率
  - variance: 多次运行结果方差
  - long_running: 24h 稳定性

tests:
  - 100 consecutive runs
  - 1h stress test
  - OOM recovery test
```

### 4. 成本 (Cost)
```yaml
metrics:
  - api_cost: $/1K tokens (若适用)
  - compute_cost: $/hour inference
  - energy_cost: kWh/task
  - hardware_cost: 摊销成本

note: Atlas-HEC 自托管 vs 云API对比
```

---

## 对比模型清单

| 模型 | 类型 | 优先级 | 状态 |
|:-----|:-----|:------:|:----:|
| GPT-4 | 商业API | P0 | ⏸️ QUEUED |
| Claude 3 | 商业API | P0 | ⏸️ QUEUED |
| Gemini Pro | 商业API | P0 | ⏸️ QUEUED |
| Llama-3-70B | 开源 | P0 | ⏸️ QUEUED |
| Mixtral 8x22B | 开源 | P1 | ⏸️ QUEUED |
| Qwen-72B | 开源 | P1 | ⏸️ QUEUED |
| DeepSeek-V2 | 开源 | P1 | ⏸️ QUEUED |
| Atlas-HEC | 自研 | P0 | ⏸️ 自检 QUEUED |

---

## 当前状态

| 组件 | 状态 | 依赖 |
|:-----|:----:|:-----|
| 评测框架 | ⏸️ QUEUED | heterogeneous ✅ |
| 数据集准备 | ⏸️ QUEUED | heterogeneous ✅ |
| API 接入 | ⏸️ QUEUED | funding/API keys |
| 结果数据库 | ⏸️ QUEUED | heterogeneous ✅ |
| 可视化 | ⏸️ QUEUED | results available |
| 报告撰写 | ⏸️ QUEUED | all benchmarks done |

---

## 下一步动作

1. [ ] 等待 heterogeneous/ 完成
2. [ ] 准备 API keys / 模型权重
3. [ ] 实现 benchmark 框架
4. [ ] 运行实验1 (单模型快速评测)
5. [ ] 运行实验2 (Atlas-HEC 自检)
6. [ ] 批量对比测试 (多个1小时窗口)
7. [ ] 撰写 benchmark 报告

---

## 完成定义

当以下全部完成：
- [ ] ≥5 个主流模型评测完成
- [ ] Atlas-HEC 自检完成
- [ ] 对比分析报告完成
- [ ] 报告通过内部审核

本目录状态更新为 ✅ COMPLETE，
项目重新评估 **发表条件** (Hard Rule 1)。

---

## 发表条件重评估

当 sota_benchmark/ 完成，检查：
```yaml
发表条件:
  1. 超脑挂载显卡: gpu_integration == COMPLETE ✅
  2. 异构架构完善: heterogeneous == COMPLETE ✅
  3. 主流SOTA测评: sota_benchmark == COMPLETE ✅
  
若全部满足:
  动作: 解冻 publication_package/
  决策: 评估论文发表可行性
  选项: [立即发表 / 补充实验 / 等待更多结果]
```
