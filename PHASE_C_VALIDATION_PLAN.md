# Phase C Validation: 集成验证计划

**Status**: 核心组件已具备，进入集成验证阶段  
**Date**: 2026-03-14  
**Objective**: 验证现有组件集成后的端到端效果

---

## 已具备组件清单

### ✅ 6→128 协议 (已验证)
- **实现**: `superbrain/evolution/round_controller.py`
- **验证**: Step 3 Round 6-10 实验完成
- **证据**: F_P3T4M4家族在Round 10成为主导 (convergence=0.800)

**协议细节确认**:
```
6 elites × 16 neighbors = 96  (mutation)
C(6,2) pairs × ~1.6 = 24    (crossover, with repetition allowed)
8 random immigrants           (diversity injection)
─────────────────────────────────────
Total: 128 seeds
```

### ✅ Fast-Forward 调度器 (已实现)
- **实现**: `superbrain/heavy_mode/causal_fast_forward.py`
- **机制**: CausalFastForwardScheduler
  - Uncertainty Sampling
  - Causal Jump
  - Adaptive Depth
- **集成点**: HeavyModeFastForwardIntegration

### ✅ 家族与谱系追踪 (已运行)
- **实现**: 
  - `superbrain/evolution/family_registry.py`
  - `superbrain/evolution/lineage_tracker.py`
- **证据**: Round 6-10 family evolution数据完整

### ✅ Fast Genesis 时间压缩 (已配置)
- **实现**: `superbrain/fast_genesis/fast_genesis_orchestrator.py`
- **配置**: compression_ratio = 31536000 (1秒 = 1年)
- **机制**: tick → epoch → era 自动切换

---

## Phase C 验证目标

### 核心问题

现有组件单独运行正常，但**集成后的端到端效果**需要验证：

1. **Fast-Forward Real Acceleration**: 是否真的比线性探索快？
2. **False Skip Rate**: 跳过的区域中，有多少实际包含优质配置？
3. **Heavy Mode → Evolution 闭环**: 从heavy mode输出到下一轮输入是否顺畅？

### 验证指标

| 指标 | 定义 | 目标 |
|------|------|------|
| **Fast-Forward Speedup** | 达到相同convergence所需round数 | ≥2× faster |
| **False Skip Rate** | 被跳过区域中的优质配置占比 | <10% |
| **Elite Retention** | Top-6elite中有多少来自Fast-Forward推荐 | >50% |
| **Family Continuity** | 跨round家族连续性 | age≥3家族占比提升 |

---

## 验证实验设计

### 对照组 (A组): 标准6→128协议

```python
# 使用现有RoundController，无Fast-Forward
controller = RoundController(round_num=11)
seeds = controller.expand_elites_to_128(elites_from_round_10)
# 全部128个seed均匀探索
results = evaluate_all_128(seeds)
top_6 = select_elites(results)
```

### 实验组 (B组): 6→128 + Fast-Forward

```python
# 使用CausalFastForwardScheduler指导探索
scheduler = CausalFastForwardScheduler()
controller = RoundController(round_num=11)

# Phase 1: Fast-Forward规划
fast_forward_plan = scheduler.get_fast_forward_plan(n_steps=10)
# 优先探索高不确定性区域

# Phase 2: 6→128，但按Fast-Forward优先级排序
seeds = controller.expand_elites_to_128(elites_from_round_10)
prioritized_seeds = apply_fast_forward_priority(seeds, fast_forward_plan)

# Phase 3: 预算约束下，优先评估高优先级seed
results = evaluate_with_budget(prioritized_seeds, budget=64)  # 只评估一半

# Phase 4: 用结果更新causal map，推断未评估区域
inferred_results = scheduler.infer_skipped_regions(results)
top_6 = select_elites(inferred_results)
```

### Round 11-12 对比实验

**设置**:
- Round 11-A: 标准协议，输入Round 10的top-6
- Round 11-B: Fast-Forward协议，相同输入
- Round 12-A: 继续标准协议
- Round 12-B: 继续Fast-Forward协议

**比较**:
1. 哪组先达到convergence score > 0.85？
2. 哪组family age增长更快？
3. Fast-Forward组的false skip率是多少？

---

## 具体验证步骤

### Step 1: Fast-Forward Real Acceleration 验证

**方法**:
```python
# 记录达到目标convergence所需的round数

def measure_convergence_speed(protocol: str) -> int:
    round_num = 10
    while round_num < 20:
        elites = run_round(round_num, protocol=protocol)
        max_conv = max(e.get('convergence', 0) for e in elites)
        if max_conv > 0.85:
            return round_num - 10  # rounds needed from R10
        round_num += 1
    return float('inf')  # never converged

standard_rounds = measure_convergence_speed('standard')
fast_forward_rounds = measure_convergence_speed('fast_forward')
speedup = standard_rounds / fast_forward_rounds
```

**通过标准**: speedup ≥ 2.0

### Step 2: False Skip Rate 验证

**方法**:
```python
# 对比被跳过的区域vs实际优质区域

# 获取Fast-Forward跳过的所有配置
skipped_configs = scheduler.get_skipped_configs()

# 用surrogate model快速评估这些配置
skipped_scores = [surrogate_eval(c) for c in skipped_configs]

# false skip = 被跳过但实际得分高的配置
false_skips = [c for c, s in zip(skipped_configs, skipped_scores) if s > 0.7]
false_skip_rate = len(false_skips) / len(skipped_configs)
```

**通过标准**: false_skip_rate < 10%

### Step 3: Heavy Mode → Evolution 闭环验证

**验证流程**:
```
Round 10 elites
    ↓
[Heavy Mode Fast-Forward Integration]
    ↓ 生成fast_forward_plan
CausalFastForwardScheduler
    ↓ 生成prioritized_128_seeds
RoundController.expand_elites_to_128()
    ↓ 按优先级评估
Parallel Evaluation (budget constrained)
    ↓ 更新causal map
HeavyModeFastForwardIntegration.update()
    ↓ 推断未评估区域
infer_skipped_regions()
    ↓ 选择top-6
select_elites()
    ↓
Round 11 elites (输出)
```

**检查点**:
1. Heavy Mode输出格式与Evolution输入格式匹配
2. Fast-Forward plan能被RoundController消费
3. 评估结果能正确更新causal map
4. 最终elite质量不低于标准协议

---

## 已有数据利用

### 利用Round 6-10数据初始化Causal Map

```python
# 用已有实验数据初始化Fast-Forward调度器
scheduler = CausalFastForwardScheduler()

for round_num in range(6, 11):
    data = load_round_data(round_num)
    for candidate in data['candidates']:
        scheduler.record_evaluation(
            config=ConfigPoint(**candidate['config']),
            drift_score=candidate['drift'],
            confidence=0.8 if candidate['n_evaluations'] > 3 else 0.5
        )

# 现在scheduler有了历史知识，可以指导Round 11
```

### 验证F_P3T4M4的Fast-Forward路径

```python
# 检查F_P3T4M4是否会被Fast-Forward正确识别为优质区域

target = ConfigPoint(p=3, t=4, m=4, d=1)
recommendation = scheduler.recommend_next_evaluations(n=10)

# F_P3T4M4或其邻居应该在推荐列表中
is_recommended = any(
    target.distance_to(ConfigPoint(**r['config'])) < 2.0
    for r in recommendation
)
```

---

## 风险控制

### 如果Fast-Forward加速比<2.0

**诊断**:
1. causal map质量不足（历史数据太少）
2. uncertainty estimation不准确
3. jump策略过于保守或激进

**对策**:
- 增加bootstrap rounds (Round 11-12用标准协议积累更多数据)
- 调整uncertainty权重
- 降低/提高jump threshold

### 如果False Skip Rate>10%

**诊断**:
1. surrogate model与真实评估差异大
2. 优质配置分布与假设不符
3. causal edge推断错误

**对策**:
- 增加surrogate model验证
- 缩小jump distance
- 增加验证样本

---

## 产出物

### 1. Phase C Validation Report

```
PHASE_C_VALIDATION_REPORT.md
├── 组件清单确认
├── Fast-Forward Acceleration Results
│   ├── Standard: X rounds to convergence
│   ├── Fast-Forward: Y rounds to convergence
│   └── Speedup: Z×
├── False Skip Analysis
│   ├── Total skipped: N
│   ├── False skips: M (M/N %)
│   └── Recovery actions taken
└── Integration Verification
    ├── Heavy Mode → Evolution ✓/✗
    ├── Data flow check ✓/✗
    └── End-to-end round trip ✓/✗
```

### 2. Updated Architecture Decision

```
ARCHITECTURE_DECISION.md
├── Fast-Forward Adoption: YES/NO/PARTIAL
├── Conditions for Full Adoption
└── Rollback Plan (if validation fails)
```

### 3. Integration Patches (if needed)

```
patches/
├── round_controller_fast_forward_hook.py
├── heavy_mode_output_adapter.py
└── causal_map_persistence.py
```

---

## 时间估算

| 任务 | 预估时间 | 依赖 |
|------|----------|------|
| Step 1: Fast-Forward acceleration | 2-3 rounds (真实实验) | Round 11-12/13 |
| Step 2: False skip analysis | 4-6 hours | Step 1完成 |
| Step 3: Integration verification | 2-3小时 | Heavy Mode可用 |
| Report writing | 2小时 | 所有数据就绪 |
| **Total** | **~1周** | |

---

## 下一步行动

**立即执行**:

1. **确认Round 11实验协议分支**
   - Branch A: 标准6→128 (继续Step 3)
   - Branch B: Fast-Forward增强

2. **初始化Causal Map**
   ```bash
   python superbrain/heavy_mode/causal_fast_forward.py \
       --bootstrap-from benchmark_results/step3_round6_10/ \
       --output causal_map_round10.json
   ```

3. **启动并行Round 11实验**
   - GPU 0-1: Branch A
   - GPU 2-3: Branch B

**Blocker**: 需要确认Heavy Mode当前状态是否可调用。

---

## 与主线关系

本Phase C验证是PROJECT.md中**L4 Self-improvement**的预验证：

- 如果Fast-Forward有效 → L4架构基础确立，进入Task-1继承验证
- 如果Fast-Forward无效 → 回退到标准协议，重新设计加速机制

**不做Phase C，直接做Task-1的风险**：
- 不知道Fast-Forward是否 work
- 不知道Heavy Mode与Evolution集成是否顺畅
- 可能在一个有缺陷的架构上做优化

---

**批准**: Atlas-HEC Research Committee  
**优先级**: P1 (阻塞L4完整验证)  
**ETA**: 1周