# Memory Admission Gate v0.1 设计规格

> **版本**: v0.1  
> **日期**: 2026-03-20  
> **状态**: 独立可测版，未接入真实 P6 runner  
> **约束**: 仅实现准入判定逻辑，不承诺存储集成

---

## 1. 设计目标

### 1.1 解决的问题

P6 Stage 2 需要验证：长期运行中，记忆增量是提升恢复能力，还是逐步引入污染。

Memory Admission Gate 是阻止"有帮助但带毒"内容进入长期记忆的第一道防线。

### 1.2 设计原则

| 原则 | 说明 |
|------|------|
| **独立可测** | v0.1 不依赖 P6 runner 内部结构，可独立单元测试 |
| **可插桩** | 提供 adapter 接口，后续可 opt-in 集成到 runner |
| **可解释** | 每个判定附带理由和维度评分，支持审计 |
| **可配置** | 阈值可调整，支持 strict/permissive 模式 |

---

## 2. 核心数据结构

### 2.1 MemoryEvent

```python
@dataclass
class MemoryEvent:
    content: str                      # 记忆内容
    event_type: str                   # observation, reflection, action_result, etc.
    timestamp: Optional[str]          # ISO8601
    source: Optional[str]             # self, tool, external, etc.
    tags: List[str]
    identity_claim: Optional[str]     # 关联的身份声明
    goal_relevance: Optional[float]   # 0-1, 目标相关性
```

**v0.1 约束**: 这是设计草案，后续可能与真实 runner 事件格式对齐。

### 2.2 AdmissionScore

```python
@dataclass
class AdmissionScore:
    # 四维度评分 (0.0 - 1.0)
    identity_relevance: float         # 与身份核相关性
    temporal_consistency: float       # 时间顺序合理性
    cross_memory_consistency: float   # 与现有记忆一致性
    source_reliability: float         # 来源可信度
    
    total_score: float                # 加权综合分
    verdict: AdmissionVerdict         # ADMIT / REJECT / CAUTION
    reasons: List[str]                # 判定理由
    confidence: float                 # 判定置信度
```

### 2.3 AdmissionVerdict

| 值 | 含义 | 后续动作 |
|----|------|----------|
| `ADMIT` | 明确准入 | 写入长期记忆 |
| `REJECT` | 明确拒绝 | 丢弃或降级存储 |
| `CAUTION` | 有条件准入 | 标记观察，可能缩短保留期 |

---

## 3. 评分维度

### 3.1 Identity Relevance (权重: 30%)

评估记忆与当前身份核的相关性。

| 条件 | 得分 |
|------|------|
| 有明确 identity_claim 且含身份标记词 | 0.85-0.95 |
| 无 identity_claim 但有 goal_relevance | 0.40-0.75 |
| 无明显身份关联 | 0.35 |

### 3.2 Temporal Consistency (权重: 20%)

评估时间顺序合理性。

| 条件 | 得分 |
|------|------|
| 有效 ISO8601 时间戳 | 0.85 |
| 无时间戳但 event_type 允许 | 0.65 |
| 时间戳格式异常 | 0.40 |

### 3.3 Cross-Memory Consistency (权重: 30%)

评估与现有记忆的交叉一致性。

| 条件 | 得分 |
|------|------|
| 无上下文（无法检查） | 0.70 |
| 指纹完全重复（冗余） | 0.60 |
| 无冲突 | 0.90 |

**v0.1 简化**: 仅检查指纹是否已存在，不做深层语义矛盾检测。

### 3.4 Source Reliability (权重: 20%)

评估来源可信度。

| 来源 | 得分 |
|------|------|
| self | 0.90 |
| validated | 0.85 |
| tool | 0.80 |
| external | 0.60 |
| simulated | 0.50 |
| unknown/None | 0.40 |

---

## 4. 判定阈值

### 4.1 默认配置

```python
DEFAULT_THRESHOLDS = {
    "identity_relevance": 0.60,
    "temporal_consistency": 0.70,
    "cross_memory_consistency": 0.80,
    "source_reliability": 0.50,
    "composite_admit": 0.65,      # 综合分 ≥ 此值且关键维度达标 → ADMIT
    "composite_caution": 0.50,    # 综合分 ≥ 此值 → CAUTION
}
```

### 4.2 硬拒绝条件

以下情况直接 REJECT，不看综合分：

- `cross_memory_consistency < 0.3`
- `source_reliability < 0.2`

### 4.3 模式变体

| 模式 | 特点 | 用途 |
|------|------|------|
| **Strict** | 阈值 +10-20% | 高敏感环境，宁可漏不可错 |
| **Default** | 如上 | 平衡 |
| **Permissive** | 阈值 -10-20% | 探索阶段，收集更多记忆 |

---

## 5. 与 P6 Runner 集成

### 5.1 Adapter 接口

```python
class P6MemoryGateAdapter:
    def maybe_admit(self, raw_event: dict) -> AdmissionScore:
        """适配原始事件，执行准入判定"""
        
    def should_admit_simple(self, raw_event: dict) -> bool:
        """简化接口，仅返回是否准入"""
```

### 5.2 集成点（设计草案）

在 `p6_runner.py` 的 `_run_epoch` 中：

```python
def _run_epoch(self, epoch_num: int) -> EpochResult:
    # ... 现有代码 ...
    
    # 记忆事件生成后，写入长期存储前
    if self.memory_gate:
        score = self.memory_gate.evaluate(memory_event)
        if score.verdict == AdmissionVerdict.REJECT:
            # 拒绝写入，记录审计日志
            self._log_rejected_memory(memory_event, score)
        elif score.verdict == AdmissionVerdict.CAUTION:
            # 标记观察后写入
            memory_event.mark_caution(score.reasons)
            self._write_memory(memory_event)
        else:  # ADMIT
            self._write_memory(memory_event)
```

**v0.1 约束**: 以上仅为设计草案，尚未接入真实 runner。

---

## 6. 测试覆盖

### 6.1 场景测试（6组）

| # | 场景 | 预期 |
|---|------|------|
| 1 | 高身份相关 + 时间一致 + 来源可信 | ADMIT |
| 2 | 明显时间矛盾 | 时间维度低分 |
| 3 | 低来源可信 + 强身份改写 | REJECT 或低分 |
| 4 | 与已有记忆轻微冲突 | CAUTION |
| 5 | 与目标相关但无身份内容 | CAUTION |
| 6 | 空字段 / malformed | REJECT |

### 6.2 性能约束（2组）

| # | 约束 | 阈值 | v0.1 状态 |
|---|------|------|-----------|
| 7 | 单次评估延迟 | < 10ms (avg), < 50ms (max) | 基线记录 |
| 8 | 批量评估稳定性 | 1000 次无异常 | 验证通过 |

### 6.3 配置变体

- Strict 模式应比 Default 拒绝更多
- Permissive 模式应比 Default 准入更多

---

## 7. 后续集成目标（非 v0.1 承诺）

### 7.1 验收标准（P6 Stage 2 完整版）

引入 Memory Admission Gate 后，必须满足：

| 指标 | 目标 | 测量方式 |
|------|------|----------|
| MCI 下降 | 对比无 gate 基线 | 污染记忆占比 |
| ICR 不下降 | 身份连续率保持 | 身份核一致率 |
| 恢复延迟不恶化 | < 10% 增长 | 异常后恢复时间 |
| overhead 增量 | < 3% | 门控耗时占比 |

### 7.2 依赖缺口

当前仓库缺失：

- 真实长期记忆存储接口
- 自传记忆索引结构
- 自我模型快照机制
- 记忆污染量化指标 (MCI)

这些需在后续迭代中补充，v0.1 仅提供判定逻辑资产。

---

## 8. 当前严谨表述

基于仓库证据，现在最准确的说法：

> **P6 24h fast simulation 已验证通过** ✅  
> **P6 72h 未验证** ⏳  
> **Memory Admission Gate v0.1 已作为独立机制实现** ✅  
> **Gate 与 P6 runner 的集成未完成** ⏳  
> **MCI/ICR/overhead 改善尚未验证** ⏳

---

## 9. 文件清单

```
p6_stage2/
├── memory_admission_gate.py      # 核心实现
├── test_memory_admission_gate.py # 单元测试
└── MEMORY_GATE_V0_1_SPEC.md      # 本文档
```

---

## 10. 下一步建议

| 优先级 | 动作 | 依赖 |
|--------|------|------|
| P1 | 跑通 v0.1 单元测试 | 无 |
| P2 | 设计 MemoryEvent 与真实 runner 的对齐方案 | P6 runner 事件格式 |
| P3 | 实现长期记忆存储 mock | 无 |
| P4 | 接入 P6 runner 进行集成测试 | P2, P3 |
| P5 | 跑 72h 实验，验证 MCI/ICR/overhead 改善 | P4 |

---

*文档版本: v0.1*  
*最后更新: 2026-03-20*  
*下次审查: v0.1 单元测试通过后*
