# 因果记忆接入超脑系统实施方案 v1

## 现有因果记忆库存盘点

### 已确认的核心文件

| 文件路径 | 功能 | 成熟度 |
|---------|------|--------|
| `/home/admin/atlas-ai-agent-dev/causal_solver.py` | 因果求解器，支持 R2 干预查询 | ⭐⭐⭐⭐ |
| `/home/admin/atlas-hec-v2.1-repo/socs_universe_search/multiverse_engine/akashic_memory_v2.py` | Akashic 记忆 v2，SEED_SPIKE 检测 | ⭐⭐⭐⭐⭐ |
| `/home/admin/atlas-hec-v2.1-repo/socs_universe_search/multiverse_engine/multiverse_runner.py` | 128 宇宙运行器，集成 Akashic | ⭐⭐⭐⭐ |
| `/home/admin/atlas-hec-v2.1-repo/analyze_p1_causal.py` | P1 因果分析脚本 | ⭐⭐⭐ |

---

## 四阶段接入方案

### Phase A: 接入 Akashic（第一周）

**目标**: 让 Akashic 从静态档案升级为因果图记忆

#### A1. 扩展现有 AkashicMemoryV2

```python
# 在 akashic_memory_v2.py 中添加

@dataclass
class CausalEventNode:
    """因果事件节点 - 可接入因果图"""
    event_id: str
    event_type: str  # policy_adoption, rollback, drift_spike, recovery
    timestamp: str
    universe_id: str
    config_snapshot: Dict
    outcome: Dict  # {drift: float, recovery_rate: float, stability: float}
    
@dataclass  
class CausalEdge:
    """因果边 - 连接事件形成因果链"""
    edge_id: str
    cause_event_id: str
    effect_event_id: str
    edge_type: str  # triggers, prevents, amplifies, dampens
    strength: float  # 0-1 因果强度
    confidence: float  # 统计置信度
```

#### A2. 接入 Heavy Mode 的 Akashic

文件: `superbrain/heavy_mode/heavy_akashic_causal.py`

```python
from socs_universe_search.multiverse_engine.akashic_memory_v2 import AkashicMemoryV2, StructureArchive
from atlas_ai_agent_dev.causal_solver import CausalSolver, CausalQuery

class HeavyAkashicWithCausal:
    """Heavy Akashic + Causal Memory 融合"""
    
    def __init__(self):
        self.base_akashic = AkashicMemoryV2()
        self.causal_graph = {}  # event_id -> CausalEventNode
        self.causal_edges = []  # List[CausalEdge]
        self.solver = CausalSolver()
        
    def record_drift_event(self, universe_id, config, drift_before, drift_after):
        """记录漂移事件到因果图"""
        event = CausalEventNode(
            event_id=f"drift_{universe_id}_{timestamp}",
            event_type="drift_spike",
            config_snapshot=config,
            outcome={"drift_before": drift_before, "drift_after": drift_after}
        )
        self.causal_graph[event.event_id] = event
        
    def query_intervention_effect(self, target_config):
        """使用因果求解器查询干预效果"""
        # 构建因果查询
        query = CausalQuery(
            query_text=f"Apply policy {target_config}",
            top_k_nodes=self._retrieve_similar_events(target_config)
        )
        return self.solver.solve(query)
```

**接入点**: 
- Heavy Akashic 的 `run_heavy_synthesis_cycle()` 中记录事件
- 在聚类/分歧分析后建立因果边

---

### Phase B: Heavy Mode 内存压缩（第一周）

**目标**: 用因果记忆解决 1.16TB 内存爆炸问题

#### B1. 状态分层存储策略

```python
# heavy_akashic.py 改造

class CompressedHeavyState:
    """因果压缩的大状态管理"""
    
    def __init__(self, max_ram_gb=400):
        self.max_ram_gb = max_ram_gb
        
        # L1: 热状态 - 当前代全量 (内存)
        self.hot_state = {}
        
        # L2: 温状态 - 最近 10 代摘要 (内存)  
        self.warm_summary = []
        
        # L3: 冷状态 - 因果图 + 关键事件 (内存)
        self.causal_graph = CausalGraph()
        
        # L4: 归档 - 完整历史 (磁盘)
        self.archive_path = "/tmp/akashic_archive/"
        
    def compress_generation(self, generation_data):
        """压缩一代数据"""
        # 提取因果关键事件
        critical_events = self._extract_causal_events(generation_data)
        
        # 稳态期只存摘要
        if self._is_steady_state(generation_data):
            summary = self._create_summary(generation_data)
            self.warm_summary.append(summary)
        else:
            # 变化期存高分辨率
            self.hot_state = generation_data
            
        # 始终更新因果图
        for event in critical_events:
            self.causal_graph.add_event(event)
```

**内存预算分配** (512GB 机器):
- Hot State: 50GB (当前全量)
- Warm Summary: 30GB (最近 10 代)
- Causal Graph: 20GB (事件 + 边)
- 计算缓冲: 50GB
- **总计**: ~150GB (可扩展到 200GB+)

---

### Phase C: 加速演化调度（第二周）

**目标**: 因果记忆支撑"现实 1s = 代码 100 年"

#### C1. Event-Driven Fast Forward

```python
# heavy_fast_genesis.py 改造

class CausalFastScheduler:
    """基于因果事件的快速调度器"""
    
    def __init__(self, causal_graph):
        self.causal_graph = causal_graph
        self.stable_threshold = 0.05  # 变化 < 5% 视为稳态
        
    def should_fast_forward(self, current_gen, population):
        """判断是否可快进"""
        # 检查最近 3 代是否因果稳定
        recent_events = self.causal_graph.get_recent_events(3)
        
        if not recent_events:
            return False, 0
            
        # 计算因果变化强度
        causal_variance = self._compute_causal_variance(recent_events)
        
        if causal_variance < self.stable_threshold:
            # 稳态期可快进
            skip_gens = self._estimate_skip_gens(population)
            return True, skip_gens
            
        return False, 0
        
    def fast_forward_generation(self, population, skip_gens):
        """基于因果模型快进"""
        # 使用因果图预测 skip_gens 后的状态
        predicted_state = self.causal_graph.predict_forward(
            current_state=population,
            n_generations=skip_gens
        )
        return predicted_state
```

**快进规则**:
- 稳态期 (causal_variance < 0.05): 快进 100-1000 代
- 过渡期 (0.05 < cv < 0.2): 正常演化
- 临界期 (cv > 0.2): 逐代精细模拟

---

### Phase D: Bridge 候选评分（第二周）

**目标**: 用因果一致性筛选 Tier A/B 候选

#### D1. Causal Consistency Scorer

```python
# bridge_scheduler.py 添加

class CausalBridgeScorer:
    """Bridge 因果评分器"""
    
    def __init__(self, akashic_causal):
        self.akashic = akashic_causal
        
    def score_candidate(self, candidate_config):
        """
        给候选配置打因果一致性分
        
        评分维度:
        1. 与 stable recipe 的因果相似度
        2. 与 failure archetype 的因果距离
        3. recovery 路径的可解释性
        4. 干预的可预测性
        """
        scores = {}
        
        # 1. 因果相似度 (vs Config 3 PREFERRED)
        scores['causal_similarity'] = self._compute_causal_similarity(
            candidate_config, 
            reference_config={"p": 2, "t": 3, "m": 3, "d": 1}
        )
        
        # 2. 因果距离 (vs Config 6 BLOCKED)
        scores['failure_distance'] = self._compute_failure_distance(
            candidate_config,
            failure_config={"p": 3, "t": 4, "m": 3, "d": 1}
        )
        
        # 3. Recovery 可解释性
        scores['recovery_explainability'] = self._score_recovery_path(candidate_config)
        
        # 4. 干预可预测性
        scores['intervention_predictability'] = self._score_intervention_robustness(candidate_config)
        
        # 综合评分
        total = (
            scores['causal_similarity'] * 0.3 +
            scores['failure_distance'] * 0.3 +
            scores['recovery_explainability'] * 0.2 +
            scores['intervention_predictability'] * 0.2
        )
        
        return total, scores
        
    def _compute_causal_similarity(self, candidate, reference):
        """计算因果相似度 - 基于因果图中的路径相似性"""
        candidate_paths = self.akashic.get_causal_paths(candidate)
        reference_paths = self.akashic.get_causal_paths(reference)
        
        # Jaccard 相似度 on causal path signatures
        intersection = len(set(candidate_paths) & set(reference_paths))
        union = len(set(candidate_paths) | set(reference_paths))
        
        return intersection / union if union > 0 else 0.0
```

**新的 Bridge 评分标准**:
- Tier A 候选: causal_score > 0.85 + fitness_score > 0.80
- Tier B 候选: causal_score > 0.70 + fitness_score > 0.65
- 直接拒绝: causal_score < 0.50 (不管 fitness 多高)

---

## 实施优先级

### Week 1: 打通 Akashic 因果链
- [x] Day 1-2: 集成 `akashic_memory_v2.py` 到 heavy mode
- [ ] Day 3-4: 实现 CausalEventNode + CausalEdge
- [ ] Day 5-7: 在 heavy_akashic.py 中记录漂移/恢复事件

### Week 2: 状态压缩 + Bridge 评分
- [ ] Day 8-10: 实现 CompressedHeavyState (L1-L4 分层)
- [ ] Day 11-12: 集成 CausalFastScheduler 到 fast_genesis
- [ ] Day 13-14: 实现 CausalBridgeScorer

### Week 3: 验证与优化
- [ ] 跑通 128 宇宙 + 因果记忆的完整流程
- [ ] 内存占用测试 (目标 < 200GB)
- [ ] CPU 利用率优化 (目标 > 70%)

---

## 最小可复用接口

### 1. 从 `causal_solver.py` 复用
```python
# 直接复用的类
from atlas_ai_agent_dev.causal_solver import (
    CausalQuery,      # 查询输入
    CausalAnswer,     # 答案输出
    PolicyNormalizer  # 政策归一化
)

# 调用方式
from causal_solver import solve_intervention_query

answer = solve_intervention_query(
    query=CausalQuery(
        query_text="Apply P2T3M3D1 policy",
        top_k_nodes=retrieved_events
    )
)
```

### 2. 从 `akashic_memory_v2.py` 复用
```python
# 直接复用
from socs_universe_search.multiverse_engine.akashic_memory_v2 import (
    AkashicMemoryV2,
    StructureArchive,
    SeedSpikeProfile
)

# 扩展方式
class CausalAkashicMemory(AkashicMemoryV2):
    """继承并扩展"""
    def __init__(self):
        super().__init__()
        self.causal_graph = CausalGraph()  # 新增
```

### 3. 从 `multiverse_runner.py` 复用
```python
# 复用 DNA 结构和宇宙运行逻辑
from socs_universe_search.multiverse_engine.multiverse_runner import (
    StructureDNA,
    simulate_universe,
    MultiverseRunner
)

# Heavy mode 中可直接用 StructureDNA 作为候选表示
```

---

## 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 因果图内存爆炸 | 中 | 高 | L1-L4 分层 + 定期剪枝 |
| 因果推理延迟 | 中 | 中 | 预计算因果路径 + 缓存 |
| 快进跳过关键事件 | 低 | 高 | 保守阈值 + 回退机制 |
| 与现有代码冲突 | 低 | 中 | 渐进式集成 + 单元测试 |

---

## 下一步行动

1. **立即**: 创建 `superbrain/heavy_mode/heavy_akashic_causal.py` 作为融合入口
2. **今天**: 跑通 AkashicMemoryV2 + heavy_akashic 的联合测试
3. **明天**: 实现第一批 CausalEventNode 记录
4. **本周**: 完成 Phase A 接入

---

**状态**: 已有成熟代码基础，可直接开始集成  
**预计完成**: 3 周内全功能上线
