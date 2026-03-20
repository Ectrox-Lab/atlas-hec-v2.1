# P6-S2 Track A: Baseline Freeze Assets

> **状态**: A-baseline-pass (冻结)  
> **日期**: 2026-03-20  
> **冻结原因**: 机制集成与长时稳定性已验证，转向真实训练态验证  
> **解冻条件**: B 线产生真实训练态反馈或明确需要 A 线扩展机制

---

## 1. 已验证结论

### 1.1 核心命题

**已证明**: HEC 的 MemoryAdmissionGate 机制能够在 P6 长时 simulation 中稳定集成，且不会引入明显额外开销或破坏系统稳定性。

### 1.2 证据链

| 验证点 | 证据 | 状态 |
|--------|------|------|
| 独立机制验证 | `test_memory_admission_gate.py` (7/7 pass) | ✅ |
| Runner 对齐 | `MEMORY_EVENT_ALIGNMENT_PLAN.md` | ✅ |
| Phase 1 集成 | `p6_runner.py` (368 lines added) | ✅ |
| 72h Track A | `P6_72H_GATE_BASELINE_RESULTS.json` | ✅ |

### 1.3 关键数值

- **72/72 epochs**: 完整完成
- **0/72 drift**: 零漂移
- **0.108ms/epoch**: 平均 gate overhead
- **100% ADMIT**: 判决分布 (baseline 同质输入)

---

## 2. 固化资产清单

### 2.1 Schema 定义

#### MemoryEvent (v0.1)

```python
@dataclass
class MemoryEvent:
    content: str                      # 记忆内容
    event_type: str                   # observation, reflection, action_result, anomaly, etc.
    timestamp: Optional[str]          # ISO8601
    source: Optional[str]             # self, tool, external, system_observation, etc.
    tags: List[str]
    identity_claim: Optional[str]     # 关联的身份声明
    goal_relevance: Optional[float]   # 0-1, 目标相关性
    
    def to_fingerprint(self) -> str:
        """生成事件指纹，用于交叉一致性检查"""
```

**使用位置**: `p6_runner.py:_create_memory_event()`

#### AdmissionScore (v0.1)

```python
@dataclass
class AdmissionScore:
    identity_relevance: float         # 0.0-1.0, 与身份核相关性
    temporal_consistency: float       # 0.0-1.0, 时间顺序合理性
    cross_memory_consistency: float   # 0.0-1.0, 与现有记忆一致性
    source_reliability: float         # 0.0-1.0, 来源可信度
    total_score: float                # 加权综合分
    verdict: AdmissionVerdict         # ADMIT / REJECT / CAUTION
    reasons: List[str]                # 判定理由
    confidence: float                 # 判定置信度
    
    def to_dict(self) -> Dict[str, Any]
```

**权重配置**:
- identity_relevance: 30%
- temporal_consistency: 20%
- cross_memory_consistency: 30%
- source_reliability: 20%

**阈值配置**:
```python
DEFAULT_THRESHOLDS = {
    "identity_relevance": 0.60,
    "temporal_consistency": 0.70,
    "cross_memory_consistency": 0.80,
    "source_reliability": 0.50,
    "composite_admit": 0.65,
    "composite_caution": 0.50,
}
```

### 2.2 Adapter 接口

#### P6MemoryGateAdapter

```python
class P6MemoryGateAdapter:
    def __init__(self, gate: Optional[MemoryAdmissionGate] = None)
    
    def maybe_admit(self, raw_event: Dict[str, Any]) -> AdmissionScore:
        """适配原始事件字典，执行准入判定"""
        
    def should_admit_simple(self, raw_event: Dict[str, Any]) -> bool:
        """简化接口，仅返回是否准入"""
```

**字段映射** (raw_event → MemoryEvent):

| raw_event 字段 | MemoryEvent 字段 | 映射规则 |
|----------------|------------------|----------|
| content | content | 直接传递 |
| type / event_type | event_type | 枚举归一化 |
| timestamp | timestamp | ISO8601 转换 |
| source | source | 直接传递 |
| tags | tags | 直接传递 |
| identity_claim | identity_claim | 直接传递 |
| goal_relevance | goal_relevance | 直接传递 |
| context | MemoryContext | 嵌套转换 |

### 2.3 日志格式

#### memory_event_log.jsonl

```json
{
  "epoch": 0,
  "timestamp": "2026-03-20T22:51:51.080022",
  "event_fingerprint": "observation:system_observation:c0047324afa9c739",
  "event_type": "observation",
  "verdict": "admit",
  "total_score": 0.825,
  "dimensions": {
    "identity_relevance": 0.95,
    "temporal_consistency": 0.85,
    "cross_memory_consistency": 0.9,
    "source_reliability": 0.5
  },
  "reasons": ["all criteria met, total_score=0.825"],
  "confidence": 0.9583
}
```

### 2.4 72h Baseline 结果摘要

```json
{
  "run_id": "P6_72H_GATE_BASELINE",
  "verdict": "PASS",
  "epochs_completed": 72,
  "core_drift_count": 0,
  "min_detector_recall": 1.0,
  "min_capability_diversity": 0.5756,
  "max_maintenance_overhead": 0.0708,
  "memory_gate_stats": {
    "total_events": 78,
    "admitted": 78,
    "caution": 0,
    "rejected": 0,
    "admission_rate": 1.0,
    "avg_score": 0.825
  },
  "avg_memory_overhead_ms": 0.108
}
```

---

## 3. A → B 接口说明

### 3.1 B 线可直接复用的资产

| 资产 | 复用方式 | 说明 |
|------|----------|------|
| MemoryEvent schema | 导入使用 | `from experiments.superbrain.p6_stage2.memory_admission_gate import MemoryEvent` |
| AdmissionScore schema | 导入使用 | 同上 |
| 四维度评分逻辑 | 参考实现 | identity/temporal/cross/source 评分启发式 |
| 阈值配置 | 参考或继承 | `DEFAULT_THRESHOLDS` |
| 日志格式 | 复用或扩展 | `memory_event_log.jsonl` 结构 |

### 3.2 B 线需要自行实现的组件

| 组件 | 原因 | 建议起点 |
|------|------|----------|
| 真实记忆存储 | A 线使用临时策略 | 实现 `MemoryStore` 接口 |
| 自传记忆索引 | A 线未实现 | 时间序列索引 + 指纹去重 |
| Self-Model 快照 | A 线使用模板 | 实现 `SelfModel` 类 |
| 训练态异常注入 | A 线为 simulation | 与训练 loop 集成 |

### 3.3 指标对应关系

| A 线指标 | B 线对应 | 计算方式 |
|----------|----------|----------|
| ICR (Identity Continuity Rate) | ICR | core identity 一致率 |
| MCI (Memory Contamination Index) | MCI | 矛盾记忆占比 |
| SMCE (Self-Model Calibration Error) | SMCE | 自我预测 vs 实际偏差 |
| RSS (Repair Sustainability Score) | recovery / RSS | 恢复成功率随时间变化 |

---

## 4. 冻结边界

### 4.1 冻结范围内 (不再扩展)

- ❌ Long-Term Memory Store 实现
- ❌ SelfModelDriftDetector 实现
- ❌ Track B (Memory Contamination)
- ❌ Track C (Self-Model Drift)
- ❌ 真实 wall-clock 运行

### 4.2 冻结范围外 (可维护)

- ✅ Bug 修复
- ✅ 文档更新
- ✅ 接口微调 (配合 B 线接入)
- ✅ 结果复现验证

---

## 5. 解冻条件

以下情况可解冻 A 线，继续扩展：

1. **B 线产生明确反馈**: 真实训练态下发现机制缺陷，需要 A 线补充验证
2. **72h 出现 drift**: 真实运行时出现 simulation 未发现的慢性恶化
3. **新机制需求**: 有明确假设需要通过 simulation 预验证

---

## 6. 文件索引

### 核心代码

```
experiments/superbrain/p6_stage2/
├── memory_admission_gate.py           # v0.1 机制实现
├── test_memory_admission_gate.py      # 单元测试
├── MEMORY_GATE_V0_1_SPEC.md           # 设计规格
└── A_BASELINE_FREEZE.md               # 本文档
```

### 集成代码

```
experiments/superbrain/p6/
├── p6_runner.py                       # 集成后的 runner
└── results/
    ├── P6_72H_GATE_BASELINE_RESULTS.json
    ├── P6_72H_GATE_BASELINE_REPORT.md
    └── memory_event_log.jsonl
```

### 对齐方案

```
experiments/superbrain/p6_stage2/
└── MEMORY_EVENT_ALIGNMENT_PLAN.md     # 字段映射与插桩位
```

---

## 7. 一句话总结

A 线已完成"机制集成与长时稳定性底座"使命，当前状态为 **A-baseline-pass (冻结)**。所有核心资产已固化，可供 B 线直接接入。下一步最有价值的证据必须来自 B 线的真实训练态对照。

---

*Frozen: 2026-03-20*  
*Status: A-baseline-pass*  
*Next: B-line preflight*
