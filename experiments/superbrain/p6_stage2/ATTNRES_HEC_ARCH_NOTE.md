# AttnRes / Block AttnRes: HEC 架构候选备忘

> **文档类型**: A-line 冻结期备忘 / 未来骨架候选  
> **状态**: 已阅，未解冻，待 B1 验证  
> **日期**: 2026-03-20  
> **关联**: 外部论文 Attention Residuals, https://github.com/closure/attn-res

---

## 1. 一句话定位

**AttnRes 不是 HEC 本体理论，但它提供了一个重要的架构原则：**

> 长期系统中的信息整合，不应依赖固定等权累加，而应依赖状态相关的选择性检索与层级压缩。

---

## 2. 论文核心贡献（摘要级理解）

### 2.1 问题识别

标准 PreNorm Transformer 的残差连接：
- 将前层表示按**固定单位权重**累加
- 导致：hidden state 随深度增长失控、早期层贡献被逐步稀释

### 2.2 解决方案

**Attention Residuals (AttnRes)**:
- 每层不再固定相加
- 对前面层输出做 **softmax attention**
- 用输入相关、可学习的权重选择需要的历史层表示

**Block AttnRes**:
- 只对**块级代表**做跨层注意力
- 减少内存和通信开销
- 使其可扩展到 Kimi Linear 48B/3B-activated 规模

### 2.3 声称收益

- Scaling law 一致增益
- 深度梯度/幅值更均匀
- 所有评估任务提升

---

## 3. 与 HEC 的关联性分析

### 3.1 方法论相似（精神层面）

| HEC 设计 | AttnRes 设计 |
|----------|--------------|
| P2: 自传记忆不是缓存，而是带 self-relevance 的结构化选择 | 深度方向不是固定残差，而是 attention-based 选择 |
| P5a: core/adaptive 分层，避免变化混成 identity drift | 早层/深层信息分层，避免固定累加稀释 |
| 8-layer Memory OS: 异构记忆层交互优于单层因果记忆 | Block 级代表通信优于全层 dense 连接 |

**核心共鸣**: 都不接受"无差别累加"，都改成"有选择、有权重、有边界的结构化聚合"

### 3.2 抽象层级差异（技术层面）

| 层级 | HEC 主线 | AttnRes |
|------|----------|---------|
| **本体层** | Identity / Memory / Self-Model / Maintenance | ❌ 不涉及 |
| **机制层** | Admission Gate / Drift Detection / Repair | ❌ 不涉及 |
| **骨架层** | 标准 Transformer / 外挂 Memory | ✅ 深度残差改造 |

**结论**: AttnRes 在"骨架层"，HEC 本体研究在"本体层+机制层"。

---

## 4. 对 HEC 的可吸收原则（3条）

### 原则 1: 深度方向也要 selective retrieval

**HEC 现状**: 已在 external memory 做 selective retrieval (P2/P3/Memory Gate)

**AttnRes 启发**: 这种原则也应扩展到模型**内部层间信息流**

**HEC 化表述**:
```
不只是 external memory 要检索
internal layer history 也要按任务和状态选择
```

### 原则 2: 层/块级代表通信

**HEC 现状**: 8-layer Memory OS 已明确异构记忆层

**AttnRes 启发**: 当这些层输出要重新进入当前决策时，不应一视同仁拼接/累加

**HEC 化表述**:
```
memory fusion = query-conditioned selection across memory layers
而非 memory fusion = concat / sum
```

### 原则 3: 稳定幅值与均匀梯度

**HEC 现状**: 担心 drift、信息稀释、能力演化过度覆盖 core

**AttnRes 启发**: 如果做 native HEC backbone，这类机制可能有助于长时训练稳定性

**HEC 化表述**:
```
Core pathway: 身份/约束/长期目标 → 保真传输
Adaptive pathway: 策略/技能/局部上下文 → 动态加权选择
Depth retrieval gate: 当前层按任务状态取所需深层历史表示
```

---

## 5. 为什么不现在解冻 A 线验证

### 5.1 A 线冻结边界

根据 `A_BASELINE_FREEZE.md`:
- ✅ 允许: Bug 修复、文档更新、接口微调、B 线接入配合
- ❌ 禁止: Long-Term Memory Store、SelfModelDriftDetector、Track B/C、新机制扩展

### 5.2 AttnRes 的位置

AttnRes 是**骨架层改造**，不是 A 线当前冻结主题下的"本体机制扩展"。

现在往 A 线塞 AttnRes 实验会:
1. 违反 A 线冻结意图（底座已验证，不再扩展）
2. 抽象层级混乱（本体机制 vs 骨架残差混在一起）
3. 证据价值不如 B1（缺真实训练态证据，而非更多 simulation）

### 5.3 正确时机

**A 线解冻条件**（满足任一）:
- B 线产生明确反馈，表明 backbone 信息流成为瓶颈
- 真实运行出现未预期 drift，需要 simulation 预验证
- 有明确假设需要通过 A 线 simulation 验证

**当前**: 不满足任何条件。

---

## 6. B1 线实验建议（解冻后第一优先）

### 6.1 实验矩阵

一旦 `HEC_1B_PREFLIGHT_CHECKLIST.md` 通过，AttnRes 应作为**第二优先级的骨架消融**:

| 配置 | Backbone | HEC-min | 目的 |
|------|----------|---------|------|
| A | Baseline | ❌ | 纯基线 |
| B | Baseline + AttnRes-like | ❌ | AttnRes 独立效果 |
| C | Baseline | ✅ | HEC-min 独立效果 |
| D | Baseline + AttnRes-like | ✅ | 协同效果 |

### 6.2 关键问题

通过此矩阵回答：

1. **通用性**: AttnRes 只是 backbone 优化，还是特别增强 HEC？
2. **本体指标**: 是否改善 ICR / MCI / SMCE / RSS？
3. **规模效应**: 小模型（1B-3B）是否比大模型更受益？

### 6.3 最小实现点

```python
# 伪代码：AttnRes-like residual for HEC
class HECAttnResBlock(nn.Module):
    def __init__(self, block_size=4):
        self.block_size = block_size
        self.depth_attn = DepthWiseAttention()  # 跨块注意力
        
    def forward(self, x, block_history):
        # 不是固定相加，而是 attention-weighted aggregation
        selected_history = self.depth_attn(
            query=x,
            keys=block_history[::self.block_size]  # Block 采样
        )
        return x + selected_history
```

### 6.4 与 A 线接口

B1 可直接复用 A 线资产：
- `MemoryEvent` schema (日志格式)
- `AdmissionScore` 结构 (评估维度)
- 4 维度评分启发式
- `memory_event_log.jsonl` 格式

---

## 7. 相关文档索引

| 文档 | 关系 |
|------|------|
| `A_BASELINE_FREEZE.md` | A 线冻结状态主文档 |
| `MEMORY_GATE_V0_1_SPEC.md` | HEC selective retrieval 机制已验证 |
| `HEC_1B_PREFLIGHT_CHECKLIST.md` | B 线预飞行检查，通过后 AttnRes 可进入实验队列 |
| 本备忘 | 桥梁文档，记录外部启发，明确解冻条件 |

---

## 8. 一句话总结

**AttnRes 值得被记住，但不应现在就被实现。**

它提供的方法论（selective retrieval over fixed sum）与 HEC 核心设计哲学一致，但它属于骨架层优化，应在 B1 真实训练态下与 HEC-min 协同验证，而非现在回 A 线开新坑。

---

*Frozen with note: 2026-03-20*  
*Unfreeze condition: B1 indicates backbone bottleneck or explicit simulation need*  
*Next action: Queue for B1 backbone ablation after preflight pass*
