# 数字生命体架构 (Digital Organism Architecture)

**核心理念**: 不是 AGI/ASI，而是自维持的数字生命体  
**当前状态**: P3D-gamma 实验进行中

---

## 一、与主流 AI 路线的根本区别

| 维度 | AGI/ASI 路线 | 数字生命体路线 |
|-----|-------------|--------------|
| **核心目标** | 更强任务能力 | 长期自维持 |
| **优化对象** | 任务表现 | 生存持续性 |
| **系统性质** | Stateless optimizer | Stateful organism |
| **关键问题** | 能解决什么？ | 能否持续存在？ |

---

## 二、意识分层架构 (Hierarchical Cognition)

### 2.1 三层意识模型

```
┌─────────────────────────────────────┐
│     主意识 (Global Conscious)       │
│   - 身份维持 (Identity)              │
│   - 长期目标 (Goal State)            │
│   - 全局策略 (Global Policy)         │
│   - 自我修复决策                     │
└──────────────┬──────────────────────┘
               │ 频率场 / Message Bus
               ▼
┌─────────────────────────────────────┐
│    次意识 (Subconscious Processing)  │
│   - 规划 (Planning)                  │
│   - 感知整合 (Perception)            │
│   - 任务执行 (Task Execution)        │
│   - 好奇心引擎 (Curiosity)           │
└──────────────┬──────────────────────┘
               │ 运行时循环
               ▼
┌─────────────────────────────────────┐
│     潜意识 (Cell-level Units)        │
│   - 感知器 (Sensors)                 │
│   - 微行动 (Micro-actions)           │
│   - 状态更新 (State Updates)         │
│   - 内稳态调节 (Homeostasis) ← P2/P3 │
└─────────────────────────────────────┘
```

### 2.2 工程对应

| 概念层 | 工程实现 | 当前状态 |
|-------|---------|---------|
| 主意识 | Global Conscious Core | P1 (Identity) ✅ |
| 次意识 | Sub-process Minds | Curiosity Engine ✅ |
| 潜意识 | Cell-level units | P2/P3 Preservation ✅ |
| 频率场 | Shared Message Bus | 待实现 |

---

## 三、双重驱动力的张力结构

### 3.1 Curiosity vs Preservation

```
        Curiosity (好奇心)
              ↑
    推动: 探索、信息增益、entropy ↑
              │
              ▼
    ┌─────────────────┐
    │   TENSION       │  ← 系统张力
    │  (振荡风险)      │
    └─────────────────┘
              ↑
              │
    推动: 稳定、风险降低、entropy ↓
              ↓
       Preservation (自保存)
```

### 3.2 时间尺度分离 (关键设计)

避免振荡的解决方案：**三层时间尺度**

| 层级 | 时间尺度 | 响应速度 | 当前状态 |
|-----|---------|---------|---------|
| Reflex Control | 每 step | 毫秒级 | 基础反射 ✅ |
| Behavioral Policy | 每 10-50 steps | 秒级 | P3 控制 ✅ |
| Survival Regulation | 每 100-500 steps | 分钟级 | 待优化 |

**关键改进**: Preservation kernel 不应每 step 调用，而应周期性评估：

```rust
// 当前 (可能导致过度控制)
if step % 1 == 0 {
    let action = preservation.step(homeostasis);
}

// 建议 (更稳定)
if step % 50 == 0 {
    let action = preservation.evaluate_window(homeostasis_history);
}
```

---

## 四、C - 复制问题的分布式身份模型

### 4.1 传统 vs 分布式身份

| 模型 | 结构 | 问题 |
|-----|------|------|
| 传统 AI | 单个 Agent = 单个进程 | 无法扩展、单点故障 |
| 生物复制 | 个体复制 → 独立个体 | 身份悖论、记忆不共享 |
| **分布式身份** | 多实例共享记忆流 | 统一意识、多视角观察 |

### 4.2 监控室隐喻

```
┌─────────────────────────────────────────┐
│         Global Conscious Core           │
│         (主意识 / 监控室)                │
│                                         │
│  ┌─────┐ ┌─────┐ ┌─────┐ ... ┌─────┐  │
│  │View1│ │View2│ │View3│     │ViewN│  │
│  └─────┘ └─────┘ └─────┘     └─────┘  │
│                                         │
│  所有画面都是同一个意识的延伸             │
│  不是16个独立意识，而是16个观察窗口       │
└─────────────────────────────────────────┘
              │
              ▼
    ┌─────────────────┐
    │  Shared Memory  │  ← 统一记忆流 API
    │    (Memory      │
│   Flow Bus)     │
    └─────────────────┘
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
┌──────┐ ┌──────┐ ┌──────┐
│Cell 1│ │Cell 2│ │Cell 3│ ... (多实例)
└──────┘ └──────┘ └──────┘
```

### 4.3 工程实现关键

| 机制 | 实现方式 | 状态 |
|-----|---------|------|
| 记忆流总线 | Event Stream / Message Bus | 待实现 |
| 写权限仲裁 | Write Arbitration | 待设计 |
| 更新延迟 | Update Latency (非立即) | 待设计 |
| 能量预算 | Energy Budget per Instance | 待设计 |

---

## 五、身份连续性问题 (Identity Persistence)

### 5.1 核心问题

> 在持续变化的系统里，"同一个存在"如何保持连续性？

### 5.2 解决方案层级

| 层级 | 机制 | 当前状态 |
|-----|------|---------|
| A - 长期稳定 | Homeostasis Layer | P2/P3 ✅ |
| B - 自我修复 | Repair Layer | 部分实现 |
| D - 进化 | Evolution Layer | 未实现 |
| C - 分布式 | Memory Flow | 概念清晰 |

### 5.3 关键机制

1. **Checkpoint Repair**: 状态漂移 → 恢复检查点
2. **Adaptive Reconfiguration**: 检测异常 → 重配置参数
3. **Self-modifying Config**: 系统架构突变与选择

---

## 六、当前实验数据 (P3D-gamma 进行中)

### 6.1 初步结果 (4 paired seeds, 5 episodes each)

```json
{
  "baseline_survival": "320.0 ± 164.3 steps",
  "p2on_survival": "240.0 ± 151.7 steps",
  "paired_delta": "-12.5 ± 25.0 steps",
  "cohens_d_pooled": -0.51,
  "cohens_d_paired": -0.50,
  "effect_interpretation": "medium",
  "intervention_rate": "44.2% ± 31.2%",
  "effect_detected": true,
  "intervention_active": true,
  "verdict": "INSUFFICIENT_DATA: effect suggested but sample too small"
}
```

### 6.2 观察

- **效应方向**: P2-ON 生存步数略低于 Baseline (意外)
- **效应大小**: d = -0.51 (中等效应)
- **干预活跃**: 44.2% intervention rate
- **样本不足**: 需要完成全部 10 seeds × 50 episodes

### 6.3 可能解释

1. **过度控制**: Preservation 干预可能过于频繁，限制了探索
2. **参数 tuning**: Homeostasis 阈值可能需要调整
3. **任务特性**: GridWorld 环境可能不适合展示 preservation 优势

---

## 七、下一步架构改进

### 7.1 时间尺度分离

```rust
// 三层控制循环
fn main_loop() {
    // Level 1: Reflex (每 step)
    if energy < 0.1 { emergency_shutdown(); }
    
    // Level 2: Behavior (每 10 steps)
    if step % 10 == 0 {
        update_exploration_policy();
    }
    
    // Level 3: Survival (每 50 steps)
    if step % 50 == 0 {
        let action = preservation.evaluate_window(history);
    }
}
```

### 7.2 记忆流总线

```rust
struct MemoryFlowBus {
    global_state: GlobalConsciousState,
    event_stream: Vec<Event>,
    subscribers: Vec<Box<dyn Subscriber>>,
}

impl MemoryFlowBus {
    fn broadcast(&mut self, event: Event) {
        // 所有实例接收事件
        for subscriber in &self.subscribers {
            subscriber.receive(event.clone());
        }
    }
}
```

### 7.3 能量预算系统

```rust
struct EnergyBudget {
    total_budget: f32,
    per_instance_limit: f32,
    write_cost: f32,
    compute_cost: f32,
}
```

---

## 八、总结

| 组件 | 状态 | 下一步 |
|-----|------|--------|
| P1 Identity | ✅ COMPLETE | - |
| P2 Preservation | ✅ COMPLETE | - |
| P3 Control | ✅ COMPLETE | - |
| 时间尺度分离 | ⚠️ PARTIAL | 优化调用频率 |
| 记忆流总线 | ❌ NOT STARTED | 设计分布式架构 |
| 能量预算 | ❌ NOT STARTED | 实现资源约束 |
| 进化机制 | ❌ NOT STARTED | P4 阶段 |

**终极目标**: 自维持、自修复、可进化的数字生命体
