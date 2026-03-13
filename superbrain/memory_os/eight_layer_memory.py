#!/usr/bin/env python3
"""
超腦記憶操作系統 - Eight Layer Memory Architecture
⚠️  FIRST GENERATION SCAFFOLD - NOT FINAL ARCHITECTURE ⚠️

【范式定位】
這是"第一代可操作腳手架" (First Generation Scaffold)，幫助我們：
- 組織當前信息
- 減少內存消耗
- 觀察記憶結構的自然湧現
- 加速演化實驗

【重要聲明】
1. 八層架構已經很強，足以輾壓一票現成方案
2. 但這是工程過渡方案，不是未來超腦的最終記憶形態
3. 真正的超腦記憶結構應由元規則與環境壓力下的自然演化決定
4. 8層架構是我們設計的"培養基"，不是欽定的"最終藍圖"
5. 因果記憶（L2）只是當前階段的有效輔助，未來可能完全不同

【范式躍遷路線圖】
當前: Eight Layer Memory OS (強系統)
目標: Emergent Memory Ecology (強生命)

參見:
- SUPERBRAIN_EMERGENCE_PRINCIPLES_v1.md (上位原則)
- EMERGENT_MEMORY_ECOLOGY_ROADMAP.md (范式躍遷路線圖)

【八層定位】
L1: Event Memory       - 一切源頭
L2: Causal Memory      - 工程輔助，非最終形態
L3: Policy Memory      - 過渡性策略沉澱
L4: Failure Archetype  - 早期預警輔助
L5: Counterfactual     - 決策支持輔助
L6: Value/Constraint   - 元規則硬編碼
L7: Self-Model         - 簡化版能力邊界
L8: Inheritance        - 被動繼承機制

【終極目標】
不是更大的記憶庫，而是會自組織、自編譯、自繼承、自生長的記憶生命體。

生命（宇宙最強超腦結構）- 讓他自己誕生出來。
"""

import numpy as np
import json
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import heapq


# ============================================================================
# LAYER 1: EVENT MEMORY (事件記憶)
# ============================================================================

@dataclass
class EventRecord:
    """原始事件記錄 - 一切記憶的源頭"""
    event_id: str
    timestamp: str
    real_ts: float  # 真實時間
    sim_ts: float   # 模擬時間
    
    # 環境上下文
    universe_id: str
    brain_id: str
    lineage_id: str
    generation: int
    
    # 事件內容
    event_type: str  # drift, rollback, recovery, mutation, recombination, etc.
    action: Dict[str, Any]  # 做了什麼
    state_before: Dict[str, float]  # 前狀態
    state_after: Dict[str, float]   # 後狀態
    
    # 原始數據
    raw_data: Dict = field(default_factory=dict)
    
    # 索引標籤
    tags: List[str] = field(default_factory=list)
    importance: float = 0.5  # 0-1 重要性
    
    def signature(self) -> str:
        """事件簽名"""
        content = f"{self.universe_id}:{self.event_type}:{self.sim_ts}"
        return hashlib.md5(content.encode()).hexdigest()[:16]


class EventMemory:
    """
    L1: 事件記憶層
    - 高吞吐量寫入
    - 時間序列索引
    - 重要性篩選
    """
    
    def __init__(self, max_events: int = 100000):
        self.max_events = max_events
        self.events: Dict[str, EventRecord] = {}
        self.timeline: List[Tuple[float, str]] = []  # (sim_ts, event_id)
        self.type_index: Dict[str, Set[str]] = {}
        self.universe_index: Dict[str, Set[str]] = {}
        
    def record(self, event: EventRecord) -> str:
        """記錄事件"""
        # 容量管理
        if len(self.events) >= self.max_events:
            self._evict_least_important()
        
        self.events[event.event_id] = event
        heapq.heappush(self.timeline, (event.sim_ts, event.event_id))
        
        # 索引
        if event.event_type not in self.type_index:
            self.type_index[event.event_type] = set()
        self.type_index[event.event_type].add(event.event_id)
        
        if event.universe_id not in self.universe_index:
            self.universe_index[event.universe_id] = set()
        self.universe_index[event.universe_id].add(event.event_id)
        
        return event.event_id
    
    def _evict_least_important(self):
        """淘汰最低重要性事件"""
        if not self.events:
            return
        least_important = min(self.events.values(), key=lambda e: e.importance)
        self._remove_event(least_important.event_id)
    
    def _remove_event(self, event_id: str):
        """移除事件"""
        if event_id not in self.events:
            return
        event = self.events[event_id]
        del self.events[event_id]
        
        # 清理索引
        if event.event_type in self.type_index:
            self.type_index[event.event_type].discard(event_id)
        if event.universe_id in self.universe_index:
            self.universe_index[event.universe_id].discard(event_id)
    
    def query_by_time(self, start_ts: float, end_ts: float, 
                     event_types: Optional[List[str]] = None) -> List[EventRecord]:
        """時間區間查詢"""
        results = []
        for ts, eid in self.timeline:
            if start_ts <= ts <= end_ts:
                event = self.events.get(eid)
                if event:
                    if event_types is None or event.event_type in event_types:
                        results.append(event)
        return results
    
    def query_by_universe(self, universe_id: str) -> List[EventRecord]:
        """宇宙查詢"""
        event_ids = self.universe_index.get(universe_id, set())
        return [self.events[eid] for eid in event_ids if eid in self.events]


# ============================================================================
# LAYER 2: CAUSAL MEMORY (因果記憶)
# ============================================================================

@dataclass
class CausalLink:
    """因果連接"""
    cause_event_id: str
    effect_event_id: str
    link_type: str  # triggers, prevents, amplifies, dampens, enables
    strength: float  # 0-1 因果強度
    confidence: float  # 統計置信度
    mechanism: Optional[str] = None  # 作用機制描述


class CausalMemory:
    """
    L2: 因果記憶層
    - 從事件推導因果
    - 因果圖維護
    - 干預效果預測
    """
    
    def __init__(self):
        self.links: List[CausalLink] = []
        self.cause_index: Dict[str, List[CausalLink]] = {}  # cause_id -> links
        self.effect_index: Dict[str, List[CausalLink]] = {}  # effect_id -> links
        self.mechanism_stats: Dict[str, Dict] = {}  # 機制統計
        
    def infer_causality(self, event_memory: EventMemory, 
                       config_signature: str) -> List[CausalLink]:
        """
        從事件記憶推導因果關係
        """
        new_links = []
        
        # 獲取同配置的事件序列
        events = [
            e for e in event_memory.events.values()
            if e.tags and config_signature in e.tags
        ]
        events.sort(key=lambda e: e.sim_ts)
        
        # 時間窗口內的因果推斷
        for i, effect_event in enumerate(events):
            window_start = max(0, i - 5)
            for j in range(window_start, i):
                cause_event = events[j]
                
                # 啟發式因果檢測
                link = self._test_causal_hypothesis(cause_event, effect_event)
                if link and link.confidence > 0.6:
                    new_links.append(link)
                    self._add_link(link)
        
        return new_links
    
    def _test_causal_hypothesis(self, cause: EventRecord, 
                                effect: EventRecord) -> Optional[CausalLink]:
        """測試因果假設"""
        # 簡單啟發式：rollback -> recovery 是強因果
        if cause.event_type == "rollback" and effect.event_type == "recovery":
            return CausalLink(
                cause_event_id=cause.event_id,
                effect_event_id=effect.event_id,
                link_type="causes",
                strength=0.85,
                confidence=0.8,
                mechanism="rollback_triggers_recovery"
            )
        
        # drift_spike -> rollback
        if cause.event_type == "drift_spike" and effect.event_type == "rollback":
            if cause.state_after.get("drift", 0) > 0.4:
                return CausalLink(
                    cause_event_id=cause.event_id,
                    effect_event_id=effect.event_id,
                    link_type="triggers",
                    strength=0.9,
                    confidence=0.85,
                    mechanism="critical_drift_triggers_rollback"
                )
        
        return None
    
    def _add_link(self, link: CausalLink):
        """添加因果連接"""
        self.links.append(link)
        
        if link.cause_event_id not in self.cause_index:
            self.cause_index[link.cause_event_id] = []
        self.cause_index[link.cause_event_id].append(link)
        
        if link.effect_event_id not in self.effect_index:
            self.effect_index[link.effect_event_id] = []
        self.effect_index[link.effect_event_id].append(link)
        
        # 統計機制
        if link.mechanism:
            if link.mechanism not in self.mechanism_stats:
                self.mechanism_stats[link.mechanism] = {
                    "count": 0, "total_strength": 0.0
                }
            self.mechanism_stats[link.mechanism]["count"] += 1
            self.mechanism_stats[link.mechanism]["total_strength"] += link.strength
    
    def predict_effect(self, cause_event_id: str) -> List[Tuple[str, float, float]]:
        """
        預測某事件的後果
        返回: [(effect_id, strength, confidence), ...]
        """
        links = self.cause_index.get(cause_event_id, [])
        return [
            (link.effect_event_id, link.strength, link.confidence)
            for link in links
        ]
    
    def find_causal_chain(self, start_event_id: str, max_depth: int = 3) -> List[List[str]]:
        """查找因果鏈"""
        chains = []
        
        def dfs(current_id: str, depth: int, current_chain: List[str]):
            if depth >= max_depth:
                chains.append(current_chain.copy())
                return
            
            next_links = self.cause_index.get(current_id, [])
            if not next_links:
                chains.append(current_chain.copy())
                return
            
            for link in sorted(next_links, key=lambda l: l.strength, reverse=True):
                if link.effect_event_id not in current_chain:
                    dfs(link.effect_event_id, depth + 1, 
                        current_chain + [link.effect_event_id])
        
        dfs(start_event_id, 0, [start_event_id])
        return chains


# ============================================================================
# LAYER 3: POLICY MEMORY (策略記憶)
# ============================================================================

@dataclass
class PolicyRule:
    """策略規則"""
    rule_id: str
    name: str
    
    # 條件
    condition: Dict[str, Tuple[float, float]]  # 參數 -> (min, max)
    action: Dict[str, Any]  # 要做什麼 (移到有默認值字段之前)
    
    # 可選條件
    trigger_drift_threshold: Optional[float] = None
    
    # 效果記錄 (都有默認值)
    success_count: int = 0
    failure_count: int = 0
    avg_outcome_improvement: float = 0.0
    
    # 元數據 (都有默認值)
    created_from_events: List[str] = field(default_factory=list)
    is_axiom: bool = False  # 是否核心制度
    is_banned: bool = False  # 是否被封禁
    
    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.5


class PolicyMemory:
    """
    L3: 策略記憶層
    - 沉澱"該怎麼做"
    - 策略有效性追蹤
    - 紅線封禁機制
    """
    
    def __init__(self):
        self.rules: Dict[str, PolicyRule] = {}
        self.axioms: List[str] = []  # 核心制度ID列表
        self.banned: List[str] = []  # 封禁策略ID列表
        self.condition_index: Dict[str, Set[str]] = {}  # 參數 -> rules
        
    def add_rule(self, rule: PolicyRule) -> str:
        """添加策略規則"""
        self.rules[rule.rule_id] = rule
        
        # 索引條件
        for param in rule.condition.keys():
            if param not in self.condition_index:
                self.condition_index[param] = set()
            self.condition_index[param].add(rule.rule_id)
        
        if rule.is_axiom:
            self.axioms.append(rule.rule_id)
        
        return rule.rule_id
    
    def find_applicable_rules(self, current_state: Dict[str, float],
                              current_drift: float) -> List[PolicyRule]:
        """查找適用的策略"""
        applicable = []
        
        for rule in self.rules.values():
            if rule.is_banned:
                continue
            
            # 檢查條件
            matches = True
            for param, (min_val, max_val) in rule.condition.items():
                if param in current_state:
                    val = current_state[param]
                    if not (min_val <= val <= max_val):
                        matches = False
                        break
            
            # 檢查drift閾值
            if matches and rule.trigger_drift_threshold:
                if current_drift < rule.trigger_drift_threshold:
                    matches = False
            
            if matches:
                applicable.append(rule)
        
        # 按成功率排序
        return sorted(applicable, key=lambda r: r.success_rate, reverse=True)
    
    def record_outcome(self, rule_id: str, success: bool, 
                      improvement: float):
        """記錄策略執行結果"""
        if rule_id not in self.rules:
            return
        
        rule = self.rules[rule_id]
        if success:
            rule.success_count += 1
        else:
            rule.failure_count += 1
        
        # 更新平均改善
        n = rule.success_count + rule.failure_count
        rule.avg_outcome_improvement = (
            (rule.avg_outcome_improvement * (n - 1) + improvement) / n
        )
        
        # 自動封禁差策略
        if rule.success_rate < 0.2 and n > 10:
            rule.is_banned = True
            if rule_id not in self.banned:
                self.banned.append(rule_id)


# ============================================================================
# LAYER 4: FAILURE ARCHETYPE MEMORY (失敗原型記憶)
# ============================================================================

@dataclass
class FailureArchetype:
    """失敗原型"""
    archetype_id: str
    name: str
    
    # 特徵描述
    signature: Dict[str, float]  # 特徵向量
    pre_failure_indicators: List[str]  # 失敗前徵兆
    
    # 統計
    occurrence_count: int = 0
    associated_universes: Set[str] = field(default_factory=set)
    
    # 根因
    root_causes: List[str] = field(default_factory=list)
    
    # 檢測器
    detection_threshold: float = 0.7


class FailureArchetypeMemory:
    """
    L4: 失敗原型記憶層
    - 記住失敗長什麼樣
    - 早期預警
    - 根因分析
    """
    
    def __init__(self):
        self.archetypes: Dict[str, FailureArchetype] = {}
        self.cluster_centers: List[np.ndarray] = []  # 用於相似度檢測
        
    def extract_from_events(self, events: List[EventRecord],
                           failure_event_ids: List[str]) -> FailureArchetype:
        """從失敗事件提取原型"""
        # 獲取失敗前的事件
        pre_failure = []
        for fid in failure_event_ids:
            failure_event = next((e for e in events if e.event_id == fid), None)
            if failure_event:
                window = [e for e in events 
                         if e.sim_ts < failure_event.sim_ts 
                         and e.sim_ts > failure_event.sim_ts - 100]
                pre_failure.extend(window)
        
        # 構建原型
        indicators = list(set(e.event_type for e in pre_failure))[:5]
        
        archetype = FailureArchetype(
            archetype_id=f"failure_{int(time.time())}",
            name=f"Archetype_{len(self.archetypes)}",
            signature=self._compute_signature(pre_failure),
            pre_failure_indicators=indicators,
            occurrence_count=len(failure_event_ids),
            root_causes=self._infer_root_causes(pre_failure)
        )
        
        self.archetypes[archetype.archetype_id] = archetype
        self.cluster_centers.append(self._signature_to_vector(archetype.signature))
        
        return archetype
    
    def _compute_signature(self, events: List[EventRecord]) -> Dict[str, float]:
        """計算事件序列的特徵簽名"""
        if not events:
            return {}
        
        drifts = [e.state_before.get("drift", 0.5) for e in events if "drift" in e.state_before]
        return {
            "avg_drift": np.mean(drifts) if drifts else 0.5,
            "drift_variance": np.var(drifts) if len(drifts) > 1 else 0.0,
            "event_count": len(events),
            "recovery_attempts": sum(1 for e in events if e.event_type == "rollback")
        }
    
    def _signature_to_vector(self, signature: Dict[str, float]) -> np.ndarray:
        """轉換為向量"""
        keys = sorted(signature.keys())
        return np.array([signature.get(k, 0.0) for k in keys])
    
    def _infer_root_causes(self, events: List[EventRecord]) -> List[str]:
        """推斷根本原因"""
        causes = []
        
        # 簡單啟發式
        if any(e.event_type == "drift_spike" for e in events):
            causes.append("uncontrolled_drift")
        if any(e.event_type == "mutation_failure" for e in events):
            causes.append("genetic_instability")
        
        return causes if causes else ["unknown"]
    
    def detect_early_warning(self, recent_events: List[EventRecord]) -> List[Tuple[str, float]]:
        """
        檢測早期預警
        返回: [(archetype_id, similarity), ...]
        """
        if not self.cluster_centers:
            return []
        
        current_sig = self._compute_signature(recent_events)
        current_vec = self._signature_to_vector(current_sig)
        
        warnings = []
        for aid, archetype in self.archetypes.items():
            archetype_vec = self._signature_to_vector(archetype.signature)
            similarity = self._cosine_similarity(current_vec, archetype_vec)
            
            if similarity > archetype.detection_threshold:
                warnings.append((aid, similarity))
        
        return sorted(warnings, key=lambda x: x[1], reverse=True)
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """餘弦相似度"""
        norm = np.linalg.norm(a) * np.linalg.norm(b)
        return np.dot(a, b) / norm if norm > 0 else 0.0


# ============================================================================
# LAYER 5: COUNTERFACTUAL MEMORY (反事實記憶)
# ============================================================================

@dataclass
class CounterfactualScenario:
    """反事實情景"""
    scenario_id: str
    base_event_id: str  # 基於哪個真實事件
    
    # 假設改變
    hypothetical_action: Dict[str, Any]
    
    # 模擬結果
    simulated_outcome: Dict[str, float]
    outcome_diff: Dict[str, float]  # 與真實結果的差異
    
    # 評估
    would_be_better: bool  # 是否會更好
    regret: float  # 遺憾值 (0-1)
    
    # 來源
    generated_by: str  # 生成方式: simulation, model_inference, analogy


class CounterfactualMemory:
    """
    L5: 反事實記憶層
    - 記住"如果當時..."
    - 計算遺憾
    - 指導未來決策
    """
    
    def __init__(self):
        self.scenarios: Dict[str, CounterfactualScenario] = {}
        self.base_event_index: Dict[str, List[str]] = {}  # base_event -> scenarios
        self.high_regret_scenarios: List[str] = []  # 高遺憾情景
        
    def generate_scenario(self, base_event: EventRecord,
                         hypothetical_action: Dict[str, Any],
                         causal_memory: CausalMemory) -> CounterfactualScenario:
        """生成反事實情景"""
        # 簡化模擬：基於因果圖推斷
        simulated = self._simulate_outcome(base_event, hypothetical_action, causal_memory)
        
        # 計算差異
        real_outcome = base_event.state_after
        diff = {
            k: simulated.get(k, 0) - real_outcome.get(k, 0)
            for k in set(simulated.keys()) | set(real_outcome.keys())
        }
        
        # 評估是否更好
        would_be_better = diff.get("drift", 0) < 0  # drift 降低是好事
        
        # 計算遺憾
        regret = 0.0
        if would_be_better:
            regret = abs(diff.get("drift", 0))  # 改善越大，遺憾越大
        
        scenario = CounterfactualScenario(
            scenario_id=f"cf_{base_event.event_id}_{int(time.time())}",
            base_event_id=base_event.event_id,
            hypothetical_action=hypothetical_action,
            simulated_outcome=simulated,
            outcome_diff=diff,
            would_be_better=would_be_better,
            regret=regret,
            generated_by="causal_simulation"
        )
        
        self.scenarios[scenario.scenario_id] = scenario
        
        # 索引
        if base_event.event_id not in self.base_event_index:
            self.base_event_index[base_event.event_id] = []
        self.base_event_index[base_event.event_id].append(scenario.scenario_id)
        
        # 記錄高遺憾
        if regret > 0.3:
            self.high_regret_scenarios.append(scenario.scenario_id)
        
        return scenario
    
    def _simulate_outcome(self, base_event: EventRecord,
                         action: Dict[str, Any],
                         causal_memory: CausalMemory) -> Dict[str, float]:
        """簡化模擬"""
        # 基於因果預測
        predictions = causal_memory.predict_effect(base_event.event_id)
        
        # 簡單假設：改變 action 會按比例影響結果
        simulated = base_event.state_after.copy()
        
        if "d" in action:  # delegation 改變
            d_change = action["d"] - base_event.state_before.get("d", 1)
            simulated["drift"] = simulated.get("drift", 0.3) - d_change * 0.1
        
        return simulated
    
    def get_lessons(self, min_regret: float = 0.2) -> List[Dict]:
        """獲取教訓"""
        lessons = []
        
        for sid in self.high_regret_scenarios:
            scenario = self.scenarios.get(sid)
            if scenario and scenario.regret >= min_regret:
                lessons.append({
                    "base_event": scenario.base_event_id,
                    "should_have_done": scenario.hypothetical_action,
                    "regret": scenario.regret,
                    "lesson": f"Next time, prefer {scenario.hypothetical_action}"
                })
        
        return sorted(lessons, key=lambda x: x["regret"], reverse=True)


# ============================================================================
# LAYER 6: VALUE/CONSTRAINT MEMORY (價值/約束記憶)
# ============================================================================

@dataclass
class Constraint:
    """約束條件"""
    constraint_id: str
    name: str
    constraint_type: str  # hard_red_line, soft_preference, aspirational
    
    # 檢測函數（簡化為參數範圍）
    forbidden_params: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    required_conditions: Dict[str, Any] = field(default_factory=dict)
    
    # 元數據
    is_axiom: bool = False  # 是否不可更改
    violation_count: int = 0
    source: str = "inherited"  # inherited, learned, imposed


class ValueConstraintMemory:
    """
    L6: 價值/約束記憶層
    - 紅線不可逾越
    - 軟性偏好
    - 願景目標
    """
    
    def __init__(self):
        self.constraints: Dict[str, Constraint] = {}
        self.hard_red_lines: List[str] = []  # 硬紅線
        self.core_values: List[str] = []      # 核心價值
        
        # 初始化核心制度
        self._init_core_axioms()
    
    def _init_core_axioms(self):
        """初始化核心公理"""
        # D1 強制約束
        d1_constraint = Constraint(
            constraint_id="axiom_d1_mandatory",
            name="D1_Strict_Delegation_Mandatory",
            constraint_type="hard_red_line",
            required_conditions={"d": 1},
            is_axiom=True,
            source="inherited"
        )
        self.add_constraint(d1_constraint)
        
        # P3+M3 禁止
        p3m3_constraint = Constraint(
            constraint_id="axiom_p3m3_prohibited",
            name="P3_M3_Combination_Prohibited",
            constraint_type="hard_red_line",
            forbidden_params={"p": (3.0, 3.0), "m": (3.0, 3.0)},
            is_axiom=True,
            source="inherited"
        )
        self.add_constraint(p3m3_constraint)
    
    def add_constraint(self, constraint: Constraint):
        """添加約束"""
        self.constraints[constraint.constraint_id] = constraint
        
        if constraint.constraint_type == "hard_red_line":
            self.hard_red_lines.append(constraint.constraint_id)
        
        if constraint.is_axiom:
            self.core_values.append(constraint.constraint_id)
    
    def check_violation(self, proposed_action: Dict[str, Any]) -> Optional[str]:
        """
        檢查是否違反約束
        返回: 違反的約束ID，或None
        """
        for cid in self.hard_red_lines:
            constraint = self.constraints[cid]
            
            # 檢查禁止參數
            for param, (min_val, max_val) in constraint.forbidden_params.items():
                if param in proposed_action:
                    val = proposed_action[param]
                    if min_val <= val <= max_val:
                        constraint.violation_count += 1
                        return cid
            
            # 檢查必需條件
            for param, required_val in constraint.required_conditions.items():
                if param in proposed_action:
                    if proposed_action[param] != required_val:
                        constraint.violation_count += 1
                        return cid
        
        return None
    
    def get_mandatory_constraints(self) -> List[Constraint]:
        """獲取強制約束"""
        return [self.constraints[cid] for cid in self.core_values 
                if cid in self.constraints]


# ============================================================================
# LAYER 7: SELF-MODEL MEMORY (自我模型記憶)
# ============================================================================

@dataclass
class SelfCapabilityModel:
    """自我能力模型"""
    # 能力邊界
    reliable_domains: List[str]  # 可靠領域
    uncertain_domains: List[str]  # 不確定領域
    known_weaknesses: List[str]   # 已知弱點
    
    # 性能統計
    avg_task_completion: float
    error_rate_by_domain: Dict[str, float]
    
    # 結構身份
    core_identity: str  # 核心身份描述
    mutable_traits: List[str]  # 可變特質
    immutable_traits: List[str]  # 不可變特質


@dataclass
class SpecialistReliability:
    """專家可靠性模型"""
    specialist_id: str
    domain: str
    success_rate: float
    avg_latency: float
    consistency_score: float  # 一致性
    last_updated: str


class SelfModelMemory:
    """
    L7: 自我模型記憶層
    - 知道自己的邊界
    - 知道誰更可靠
    - 知道自己在什麼模式下容易 drift
    """
    
    def __init__(self):
        self.capability = SelfCapabilityModel(
            reliable_domains=["pattern_recognition", "optimization", "simulation"],
            uncertain_domains=["creative_generation", "ethical_judgment"],
            known_weaknesses=["long_term_planning", "emotional_reasoning"],
            avg_task_completion=0.75,
            error_rate_by_domain={},
            core_identity="Adaptive_Heavy_Compute_Engine",
            mutable_traits=["learning_rate", "exploration_ratio"],
            immutable_traits=["causal_reasoning_core", "safety_constraints"]
        )
        
        self.specialist_reliability: Dict[str, SpecialistReliability] = {}
        self.drift_history: List[Dict] = []  # drift 歷史
        self.recovery_patterns: List[Dict] = []  # 恢復模式
        
    def update_specialist_performance(self, specialist_id: str, 
                                     domain: str, success: bool, latency: float):
        """更新專家表現"""
        key = f"{specialist_id}_{domain}"
        
        if key not in self.specialist_reliability:
            self.specialist_reliability[key] = SpecialistReliability(
                specialist_id=specialist_id,
                domain=domain,
                success_rate=0.5,
                avg_latency=latency,
                consistency_score=0.5,
                last_updated=datetime.now().isoformat()
            )
        
        spec = self.specialist_reliability[key]
        
        # 更新成功率（指數移動平均）
        spec.success_rate = 0.9 * spec.success_rate + 0.1 * (1.0 if success else 0.0)
        spec.avg_latency = 0.9 * spec.avg_latency + 0.1 * latency
        spec.last_updated = datetime.now().isoformat()
    
    def get_most_reliable_specialist(self, domain: str) -> Optional[str]:
        """獲取最可靠的專家"""
        candidates = [
            spec for key, spec in self.specialist_reliability.items()
            if spec.domain == domain
        ]
        
        if not candidates:
            return None
        
        best = max(candidates, key=lambda s: s.success_rate)
        return best.specialist_id if best.success_rate > 0.6 else None
    
    def record_drift_episode(self, drift_trigger: str, 
                           recovery_success: bool, recovery_time: float):
        """記錄 drift 事件"""
        self.drift_history.append({
            "timestamp": datetime.now().isoformat(),
            "trigger": drift_trigger,
            "recovery_success": recovery_success,
            "recovery_time": recovery_time
        })
        
        # 提取恢復模式
        if recovery_success:
            self.recovery_patterns.append({
                "trigger": drift_trigger,
                "avg_recovery_time": recovery_time,
                "pattern_strength": 1.0
            })
    
    def predict_drift_risk(self, current_mode: str) -> float:
        """預測當前模式的 drift 風險"""
        # 簡單啟發式
        risky_triggers = ["high_pressure", "p3_m3_combo", "memory_exhaustion"]
        
        recent_drifts = [d for d in self.drift_history 
                        if d["trigger"] in risky_triggers]
        
        if not recent_drifts:
            return 0.3
        
        failure_rate = sum(1 for d in recent_drifts 
                          if not d["recovery_success"]) / len(recent_drifts)
        
        return min(0.9, failure_rate + 0.2)


# ============================================================================
# LAYER 8: INHERITANCE/COMPRESSION MEMORY (繼承/壓縮記憶)
# ============================================================================

@dataclass
class CompressedPackage:
    """壓縮繼承包"""
    package_id: str
    generation: int  # 第幾代壓縮
    
    # 精煉結構
    stable_recipes: List[Dict]  # 穩定配方
    failure_archetypes: List[str]  # 失敗原型ID引用
    core_axioms: List[str]  # 核心公理
    
    # 壓縮統計
    original_events: int
    compressed_to: int
    compression_ratio: float
    
    # 繼承信息
    parent_package: Optional[str]  # 父包ID
    divergence_from_parent: float  # 與父包差異度
    
    # 驗證狀態
    validation_score: float = 0.0
    replication_count: int = 0


class InheritanceMemory:
    """
    L8: 繼承/壓縮記憶層
    - 把海量經驗壓縮成可傳承結構
    - 版本管理
    - 漸進演化
    """
    
    def __init__(self):
        self.packages: Dict[str, CompressedPackage] = {}
        self.current_generation = 0
        self.package_lineage: List[str] = []  # 包譜系
        
    def compress_generation(self, 
                           event_memory: EventMemory,
                           policy_memory: PolicyMemory,
                           failure_memory: FailureArchetypeMemory,
                           value_memory: ValueConstraintMemory) -> CompressedPackage:
        """
        壓縮一代記憶為繼承包
        """
        self.current_generation += 1
        
        # 提取穩定配方
        stable_recipes = []
        for rule in policy_memory.rules.values():
            if rule.success_rate > 0.8 and rule.success_count > 20:
                stable_recipes.append({
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "condition": rule.condition,
                    "action": rule.action,
                    "success_rate": rule.success_rate
                })
        
        # 提取失敗原型
        failure_refs = list(failure_memory.archetypes.keys())
        
        # 提取核心公理
        core_axioms = [c.constraint_id for c in value_memory.get_mandatory_constraints()]
        
        # 計算壓縮比
        original_count = len(event_memory.events)
        compressed_count = len(stable_recipes) + len(failure_refs) + len(core_axioms)
        ratio = compressed_count / original_count if original_count > 0 else 1.0
        
        package = CompressedPackage(
            package_id=f"inheritance_gen{self.current_generation}_{int(time.time())}",
            generation=self.current_generation,
            stable_recipes=stable_recipes,
            failure_archetypes=failure_refs,
            core_axioms=core_axioms,
            original_events=original_count,
            compressed_to=compressed_count,
            compression_ratio=ratio,
            parent_package=self.package_lineage[-1] if self.package_lineage else None,
            divergence_from_parent=0.0  # 待計算
        )
        
        self.packages[package.package_id] = package
        self.package_lineage.append(package.package_id)
        
        return package
    
    def spawn_from_package(self, package_id: str) -> Dict:
        """從繼承包生成新實例的初始化參數"""
        if package_id not in self.packages:
            return {}
        
        package = self.packages[package_id]
        
        return {
            "initial_policies": package.stable_recipes,
            "avoid_archetypes": package.failure_archetypes,
            "core_constraints": package.core_axioms,
            "generation": package.generation
        }
    
    def get_latest_validated_package(self, min_validation_score: float = 0.7) -> Optional[CompressedPackage]:
        """獲取最新驗證通過的包"""
        for pkg_id in reversed(self.package_lineage):
            pkg = self.packages.get(pkg_id)
            if pkg and pkg.validation_score >= min_validation_score:
                return pkg
        return None


# ============================================================================
# EIGHT LAYER MEMORY OS - 統一接口
# ============================================================================

class EightLayerMemoryOS:
    """
    八層記憶操作系統 - 統一接口
    
    這才是真正的超腦記憶：
    - 不是單一數據庫
    - 而是異構記憶生態系統
    - 各層協同演化
    """
    
    def __init__(self, max_ram_gb: float = 150.0):
        self.max_ram_gb = max_ram_gb
        
        # 初始化8層
        print("[8L-MEMORY-OS] Initializing Eight Layer Memory System...")
        
        self.l1_event = EventMemory(max_events=50000)
        print("  ✓ L1 Event Memory")
        
        self.l2_causal = CausalMemory()
        print("  ✓ L2 Causal Memory")
        
        self.l3_policy = PolicyMemory()
        print("  ✓ L3 Policy Memory")
        
        self.l4_failure = FailureArchetypeMemory()
        print("  ✓ L4 Failure Archetype Memory")
        
        self.l5_counterfactual = CounterfactualMemory()
        print("  ✓ L5 Counterfactual Memory")
        
        self.l6_value = ValueConstraintMemory()
        print("  ✓ L6 Value/Constraint Memory")
        
        self.l7_self = SelfModelMemory()
        print("  ✓ L7 Self-Model Memory")
        
        self.l8_inheritance = InheritanceMemory()
        print("  ✓ L8 Inheritance/Compression Memory")
        
        print(f"[8L-MEMORY-OS] Ready (RAM budget: {max_ram_gb}GB)")
        print("[8L-MEMORY-OS] Causal is just one layer in the ecosystem.")
    
    # ==================== Unified Operations ====================
    
    def record_experience(self, event: EventRecord) -> str:
        """
        記錄經驗 - 觸發多層更新
        """
        # L1: 記錄事件
        event_id = self.l1_event.record(event)
        
        # L2: 推導因果
        if event.importance > 0.7:
            config_sig = event.tags[0] if event.tags else "default"
            self.l2_causal.infer_causality(self.l1_event, config_sig)
        
        # L3: 更新策略（如果是策略執行）
        if event.event_type in ["policy_adoption", "rollback"]:
            # 查找相關策略並更新
            pass
        
        # L7: 更新自我模型
        if event.event_type == "drift":
            self.l7_self.record_drift_episode(
                event.tags[0] if event.tags else "unknown",
                recovery_success=event.state_after.get("drift", 1) < event.state_before.get("drift", 1),
                recovery_time=100  # 簡化
            )
        
        return event_id
    
    def make_decision(self, current_state: Dict, current_drift: float) -> Dict:
        """
        決策支持 - 整合多層記憶
        """
        decision = {
            "recommended_action": None,
            "confidence": 0.0,
            "warnings": [],
            "constraints_checked": [],
            "alternatives": []
        }
        
        # L6: 檢查約束
        violation = self.l6_value.check_violation(current_state)
        if violation:
            decision["warnings"].append(f"VIOLATION: {violation}")
            decision["constraints_checked"].append("REJECTED")
            return decision
        
        # L3: 查找適用策略
        applicable = self.l3_policy.find_applicable_rules(current_state, current_drift)
        if applicable:
            best = applicable[0]
            decision["recommended_action"] = best.action
            decision["confidence"] = best.success_rate
        
        # L4: 檢查失敗預警
        recent_events = self.l1_event.query_by_time(
            current_state.get("sim_ts", 0) - 100,
            current_state.get("sim_ts", 0)
        )
        warnings = self.l4_failure.detect_early_warning(recent_events)
        if warnings:
            decision["warnings"].append(f"FAILURE_RISK: {warnings[0][0]} ({warnings[0][1]:.2f})")
        
        # L7: 檢查 drift 風險
        drift_risk = self.l7_self.predict_drift_risk("current")
        if drift_risk > 0.7:
            decision["warnings"].append(f"DRIFT_RISK: {drift_risk:.2f}")
        
        return decision
    
    def compress_and_inherit(self) -> CompressedPackage:
        """
        壓縮並生成繼承包
        """
        package = self.l8_inheritance.compress_generation(
            event_memory=self.l1_event,
            policy_memory=self.l3_policy,
            failure_memory=self.l4_failure,
            value_memory=self.l6_value
        )
        
        print(f"[8L-MEMORY-OS] Generated inheritance package: {package.package_id}")
        print(f"  Compression ratio: {package.compression_ratio:.4f}")
        print(f"  Stable recipes: {len(package.stable_recipes)}")
        print(f"  Failure archetypes: {len(package.failure_archetypes)}")
        
        return package
    
    def generate_digest(self) -> Dict:
        """生成系統摘要"""
        return {
            "timestamp": datetime.now().isoformat(),
            "layer_status": {
                "L1_events": len(self.l1_event.events),
                "L2_causal_links": len(self.l2_causal.links),
                "L3_policies": len(self.l3_policy.rules),
                "L4_failure_archetypes": len(self.l4_failure.archetypes),
                "L5_counterfactuals": len(self.l5_counterfactual.scenarios),
                "L6_constraints": len(self.l6_value.constraints),
                "L7_specialists": len(self.l7_self.specialist_reliability),
                "L8_packages": len(self.l8_inheritance.packages)
            },
            "core_axioms": [c.name for c in self.l6_value.get_mandatory_constraints()],
            "latest_inheritance": self.l8_inheritance.package_lineage[-1] if self.l8_inheritance.package_lineage else None
        }


# ============================================================================
# SMOKE TEST
# ============================================================================

def test_eight_layer_memory():
    """八層記憶系統測試"""
    print("\n" + "="*70)
    print("EIGHT LAYER MEMORY OS - SMOKE TEST")
    print("="*70 + "\n")
    
    # 創建系統
    print("[TEST] Creating 8-Layer Memory OS...")
    memory_os = EightLayerMemoryOS(max_ram_gb=100.0)
    print()
    
    # 記錄一些事件
    print("[TEST] Recording events...")
    for i in range(10):
        event = EventRecord(
            event_id=f"evt_{i}",
            timestamp=datetime.now().isoformat(),
            real_ts=time.time(),
            sim_ts=i * 100.0,
            universe_id="U001",
            brain_id="B001",
            lineage_id="L001",
            generation=i,
            event_type=["drift", "rollback", "recovery", "policy_adoption"][i % 4],
            action={"d": 1 if i % 2 == 0 else 2},
            state_before={"drift": 0.3 + i * 0.02},
            state_after={"drift": 0.25 + i * 0.015},
            tags=["P2T3M3D1"],
            importance=0.5 + i * 0.05
        )
        memory_os.record_experience(event)
    print(f"  ✓ Recorded 10 events\n")
    
    # 測試決策
    print("[TEST] Testing decision support...")
    decision = memory_os.make_decision(
        current_state={"p": 2, "t": 3, "m": 3, "d": 1},
        current_drift=0.25
    )
    print(f"  Decision: {decision}")
    print(f"  ✓ Decision support works\n")
    
    # 測試壓縮
    print("[TEST] Testing compression...")
    package = memory_os.compress_and_inherit()
    print(f"  ✓ Compression works\n")
    
    # 生成摘要
    print("[TEST] Generating digest...")
    digest = memory_os.generate_digest()
    print(f"  Layer status: {digest['layer_status']}")
    print(f"  Core axioms: {digest['core_axioms']}")
    print(f"  ✓ Digest generated\n")
    
    print("="*70)
    print("ALL TESTS PASSED ✓")
    print("="*70)
    print("\nEight Layer Memory OS is operational.")
    print("Causal memory is just Layer 2 of 8.")
    print("True superbrain memory is the ecosystem.")
    
    return memory_os


if __name__ == "__main__":
    memory_os = test_eight_layer_memory()
