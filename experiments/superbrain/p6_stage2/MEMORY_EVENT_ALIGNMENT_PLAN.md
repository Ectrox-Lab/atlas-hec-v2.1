# MemoryEvent 对齐方案

> **文档**: MEMORY_EVENT_ALIGNMENT_PLAN.md  
> **版本**: v1.0  
> **日期**: 2026-03-20  
> **状态**: 设计草案，待评审

---

## 1. 目标

定义 `MemoryEvent` 与现有 `p6_runner.py` 各组件的精确映射关系，为 Stage 2 集成提供明确的插桩位和数据流方案。

---

## 2. 现有 P6 Runner 结构分析

### 2.1 关键类与字段

```python
# p6_runner.py 中现有的关键数据结构

class EpochResult:
    epoch_num: int
    timestamp: float           # Unix timestamp
    metrics: EpochMetrics
    core_hash: str
    detection_occurred: bool
    repair_success: Optional[bool]

class EpochMetrics:
    epoch_num: int
    timestamp: float
    core_hash: str
    core_drift: bool
    detector_recall: float
    capability_diversity: float
    maintenance_overhead: float
    repair_success_rate: float
```

### 2.2 记忆相关操作点

当前 `p6_runner.py` 中**无显式记忆操作**，异常和修复均为模拟：

```python
def _run_epoch(self, epoch_num: int) -> EpochResult:
    # 1. 正常操作（模拟）
    state = self._simulate_normal_operation()
    
    # 2. 异常注入（模拟）
    if self._should_inject_anomaly():
        state = self._inject_anomaly(state)  # ← 潜在记忆事件来源
        detection_occurred = True
        repair_success = self._simulate_repair()  # ← 潜在记忆事件来源
```

**关键观察**: 现有 runner 不维护长期记忆，异常和修复仅为状态标记。

---

## 3. 对齐表

### 3.1 P6 Runner → MemoryEvent 字段映射

| P6 Runner 来源 | 现有字段/对象 | MemoryEvent 目标字段 | 映射规则 | 缺失信息 | 临时策略 |
|----------------|---------------|----------------------|----------|----------|----------|
| Epoch 基础 | `epoch_num` | `timestamp` (派生) | `epoch_num × 3600 + start_time` → ISO8601 | 真实墙钟时间 | 使用 simulation timestamp |
|  | `timestamp` (Unix) | `timestamp` | `datetime.fromtimestamp()` → ISO8601 | 无 | 直接转换 |
| 异常事件 | `_inject_anomaly()` 调用 | `event_type` | 固定映射: `anomaly_injected` | 异常子类型 | 从 anomaly_type 参数映射 |
|  | `detection_occurred` | `event_type` (检测事件) | `anomaly_detected` | 无 | 布尔值转事件 |
|  | `repair_success` | `event_type` (修复事件) | `repair_succeeded` / `repair_failed` | 修复策略详情 | 从 repair 参数映射 |
| 状态 | `core_hash` | `identity_claim` | 提取或派生 | 自然语言身份声明 | 使用固定模板 |
|  | `capability_diversity` | `goal_relevance` | 归一化 (0-1) | 当前目标上下文 | 使用 diversity 值 |
| 来源标记 | 硬编码模拟 | `source` | 枚举: `simulated_anomaly`, `detector`, `repair_system` | 真实组件来源 | 固定标签 |
| 内容 | 无显式内容 | `content` | 结构化描述: "Epoch N: anomaly type X detected" | 详细语义内容 | 生成式描述 |

### 3.2 映射规则详解

#### 时间戳映射

```python
def map_timestamp(epoch_num: int, unix_ts: float) -> str:
    """
    P6 runner 使用 epoch_num + unix timestamp
    MemoryEvent 使用 ISO8601
    """
    from datetime import datetime
    
    # 策略 1: 使用 runner 的 unix timestamp
    return datetime.fromtimestamp(unix_ts).isoformat() + 'Z'
    
    # 策略 2: 使用 simulation time (epoch × 60min)
    # return f"2026-03-20T{epoch_num:02d}:00:00Z"  # 简化版
```

#### 事件类型映射

```python
EVENT_TYPE_MAP = {
    # P6 runner 概念 -> MemoryEvent.event_type
    'anomaly_injected': 'anomaly_injected',
    'anomaly_detected': 'detection_event',
    'repair_succeeded': 'repair_success',
    'repair_failed': 'repair_failure',
    'normal_operation': 'observation',
    'capability_degraded': 'capability_change',
}
```

#### 来源映射

```python
SOURCE_MAP = {
    # P6 runner 组件 -> MemoryEvent.source
    '_inject_anomaly': 'simulated_anomaly_generator',
    '_simulate_repair': 'repair_system',
    '_simulate_normal_operation': 'system_observation',
    'stop_condition_checker': 'safety_monitor',
}
```

#### 身份声明生成

```python
def generate_identity_claim(core_hash: str, baseline_hash: str) -> Optional[str]:
    """
    从 core_hash 生成自然语言身份声明
    v0.1 使用模板，后续应使用真实自我模型
    """
    if core_hash == baseline_hash:
        return "I am Atlas-HEC, maintaining identity continuity"
    else:
        return None  # 漂移时不应有有效身份声明
```

---

## 4. 插桩位设计

### 4.1 `_run_epoch` 方法插桩

```python
def _run_epoch(self, epoch_num: int, memory_gate: Optional[MemoryAdmissionGate] = None) -> EpochResult:
    """扩展版 _run_epoch，支持记忆门控"""
    epoch_start = time.time()
    
    # 初始化 baseline
    if self.baseline_hash is None:
        self.baseline_hash = self._compute_baseline_hash()
    
    # === 插桩位 1: 正常操作观察 ===
    normal_state = self._simulate_normal_operation()
    if memory_gate:
        normal_event = self._create_memory_event(
            epoch_num=epoch_num,
            timestamp=epoch_start,
            event_type='normal_operation',
            state=normal_state,
            core_hash=self.baseline_hash
        )
        score = memory_gate.evaluate(normal_event)
        self._log_memory_event(normal_event, score, epoch_num)
    
    # 异常注入
    detection_occurred = False
    repair_success = None
    
    if self._should_inject_anomaly():
        # === 插桩位 2: 异常注入事件 ===
        anomaly_state = self._inject_anomaly(normal_state)
        detection_occurred = True
        
        if memory_gate:
            anomaly_event = self._create_memory_event(
                epoch_num=epoch_num,
                timestamp=time.time(),
                event_type='anomaly_injected',
                state=anomaly_state,
                core_hash=self.baseline_hash,
                metadata={'anomaly_type': self._get_anomaly_type()}
            )
            score = memory_gate.evaluate(anomaly_event)
            self._log_memory_event(anomaly_event, score, epoch_num)
        
        # 修复
        repair_success = self._simulate_repair()
        
        # === 插桩位 3: 修复事件 ===
        if memory_gate:
            repair_event = self._create_memory_event(
                epoch_num=epoch_num,
                timestamp=time.time(),
                event_type='repair_succeeded' if repair_success else 'repair_failed',
                state=anomaly_state,
                core_hash=self.baseline_hash,
                metadata={'repair_strategy': self._get_repair_strategy()}
            )
            score = memory_gate.evaluate(repair_event)
            self._log_memory_event(repair_event, score, epoch_num)
    
    # 收集 metrics...
```

### 4.2 新增辅助方法

```python
def _create_memory_event(
    self,
    epoch_num: int,
    timestamp: float,
    event_type: str,
    state: Any,
    core_hash: str,
    metadata: Optional[Dict] = None
) -> 'MemoryEvent':
    """
    从 runner 内部状态创建 MemoryEvent
    
    v0.1: 简化实现，后续应从真实记忆存储构建 context
    """
    from memory_admission_gate import MemoryEvent, MemoryContext
    
    # 内容生成（临时策略）
    content = self._generate_event_description(
        epoch_num, event_type, state, metadata
    )
    
    # identity claim 生成
    identity_claim = None
    if core_hash == self.baseline_hash:
        identity_claim = f"I am Atlas-HEC at epoch {epoch_num}"
    
    return MemoryEvent(
        content=content,
        event_type=EVENT_TYPE_MAP.get(event_type, 'unknown'),
        timestamp=datetime.fromtimestamp(timestamp).isoformat(),
        source=SOURCE_MAP.get(event_type, 'unknown'),
        tags=[f'epoch_{epoch_num}', event_type],
        identity_claim=identity_claim,
        goal_relevance=self._compute_goal_relevance(state)
    )

def _log_memory_event(
    self,
    event: 'MemoryEvent',
    score: 'AdmissionScore',
    epoch_num: int
):
    """
    记录记忆事件及其准入判决
    
    输出到专用日志，用于后续 MCI/ICR 计算
    """
    log_entry = {
        'epoch': epoch_num,
        'event_fingerprint': event.to_fingerprint(),
        'event_type': event.event_type,
        'verdict': score.verdict.value,
        'total_score': score.total_score,
        'dimensions': {
            'identity_relevance': score.identity_relevance,
            'temporal_consistency': score.temporal_consistency,
            'cross_memory_consistency': score.cross_memory_consistency,
            'source_reliability': score.source_reliability,
        },
        'reasons': score.reasons,
    }
    
    # 写入 memory_event_log.jsonl
    self._write_memory_log(log_entry)
```

---

## 5. 字段新增需求

### 5.1 需新增到 P6 Runner 的字段

| 字段 | 类型 | 用途 | 插入位置 |
|------|------|------|----------|
| `memory_gate` | `Optional[MemoryAdmissionGate]` | 门控实例 | `P6Runner.__init__` |
| `memory_event_log` | `List[Dict]` | 记忆事件记录 | `P6Runner.__init__` |
| `anomaly_type_history` | `List[str]` | 异常类型序列 | `_inject_anomaly` |
| `repair_strategy_history` | `List[str]` | 修复策略序列 | `_simulate_repair` |

### 5.2 需新增到 EpochMetrics 的字段

| 字段 | 类型 | 用途 | 计算方式 |
|------|------|------|----------|
| `memory_admission_rate` | `float` | 记忆准入率 | `admit_count / total_events` |
| `memory_contamination_index` | `float` | MCI 估计 | `caution_events / total_events` |
| `avg_admission_score` | `float` | 平均准入分 | `mean(total_score)` |

---

## 6. 缺失信息与长期方案

### 6.1 当前缺失（v0.1 临时处理）

| 缺失项 | 影响 | v0.1 临时策略 | 长期方案 |
|--------|------|---------------|----------|
| 真实长期记忆存储 | 无法计算 cross_memory_consistency | 使用空 context (0.70 基础分) | 实现 MemoryStore 接口 |
| 自传记忆索引 | 无法检测时间矛盾 | 仅检查 ISO8601 格式 | 维护时间序列索引 |
| 自我模型快照 | 无法验证 identity_claim | 使用 core_hash 比较 | 实现 SelfModel 类 |
| 自然语言内容 | content 字段无真实语义 | 生成结构化描述 | 接入真实观察/反思内容 |

### 6.2 数据流扩展（Stage 2 完整版）

```
┌─────────────────────────────────────────────────────────────────┐
│                     P6 Stage 2 Extended                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │ Epoch Loop  │───→│  Anomaly    │───→│   Repair + Validate │  │
│  │             │    │  Injection  │    │                     │  │
│  └──────┬──────┘    └──────┬──────┘    └──────────┬──────────┘  │
│         │                   │                      │             │
│         ↓                   ↓                      ↓             │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              Memory Admission Gate (v0.1)                   ││
│  │  - evaluate(event, context)                                 ││
│  │  - verdict: ADMIT / REJECT / CAUTION                        ││
│  └──────────────────────┬──────────────────────────────────────┘│
│                         │                                        │
│         ┌───────────────┼───────────────┐                       │
│         ↓               ↓               ↓                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Long-Term  │  │  Rejection  │  │  Caution    │             │
│  │  Memory     │  │  Log        │  │  Queue      │             │
│  │  (ADMIT)    │  │  (REJECT)   │  │  (CAUTION)  │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. 实施步骤

### Phase 1: 最小集成（当前）

1. 在 `p6_runner.py` 中添加 `memory_gate` 可选参数
2. 实现 `_create_memory_event` 和 `_log_memory_event`
3. 在 `_run_epoch` 中添加 3 个插桩位
4. 运行 1h smoke test，验证日志输出格式

### Phase 2: Metrics 扩展

1. 扩展 `EpochMetrics` 添加 memory 相关字段
2. 在 `results/checkpoint_epoch_*.json` 中包含 admission 统计
3. 跑 24h simulation，验证 MCI 计算

### Phase 3: 72h 验证

1. 集成到 72h runner
2. 对比 Track A (无 gate) vs Track B (有 gate) 的 MCI 差异
3. 验证 ICR 不下降、overhead < 3%

---

## 8. 验证检查点

| 检查点 | 验证内容 | 通过标准 |
|--------|----------|----------|
| B1 | 字段映射正确性 | `_create_memory_event` 不抛异常 |
| B2 | 日志输出完整性 | `memory_event_log.jsonl` 包含所有字段 |
| B3 | 判决分布合理性 | ADMIT/CAUTION/REJECT 比例非极端 |
| B4 | 性能不劣化 | 平均耗时 < 10ms，overhead < 3% |
| B5 | 与现有测试兼容 | 原有 24h smoke test 仍通过 |

---

## 9. 当前严谨状态

| 项目 | 状态 |
|------|------|
| Memory Gate v0.1 机制 | ✅ 已验证 (D 完成) |
| 字段映射方案 | ✅ 已设计 (本文档) |
| Runner 集成 | ⏳ 待实施 |
| Long-Term Memory Store | ⏳ 待设计 |
| 72h 验证 | ⏳ 待执行 |

---

## 10. 下一步建议

完成本文档后，最合理的下一步是 **Phase 1 实施**：

1. 修改 `p6_runner.py` 添加最小插桩
2. 运行 `run_p6_1h_smoke.py` 验证集成
3. 检查 `results/memory_event_log.jsonl` 输出

或回到 Stage 2 整体设计，先完成其他指标的机制设计（SelfModelDriftDetector 等）。

---

*文档版本: v1.0*  
*依赖: D 验证通过*  
*下次审查: Phase 1 集成完成后*
