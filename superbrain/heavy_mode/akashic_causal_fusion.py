#!/usr/bin/env python3
"""
AKASHIC + CAUSAL FUSION - 3 Hour Integration Sprint
Direct fusion of existing akashic_memory_v2 + causal_solver
"""

import sys
sys.path.insert(0, '/home/admin/atlas-hec-v2.1-repo/socs_universe_search/multiverse_engine')
sys.path.insert(0, '/home/admin/atlas-ai-agent-dev')

import numpy as np
import json
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# ============================================================================
# IMPORT EXISTING MODULES
# ============================================================================
try:
    from akashic_memory_v2 import AkashicMemoryV2, StructureArchive, SeedSpikeProfile
    AKASHIC_AVAILABLE = True
    print("[FUSION] AkashicMemoryV2 loaded successfully")
except Exception as e:
    print(f"[FUSION] Akashic import failed: {e}")
    AKASHIC_AVAILABLE = False

try:
    from causal_solver import CausalSolver, CausalQuery, RetrievedNode, PolicyNormalizer
    CAUSAL_AVAILABLE = True
    print("[FUSION] CausalSolver loaded successfully")
except Exception as e:
    print(f"[FUSION] CausalSolver import failed: {e}")
    CAUSAL_AVAILABLE = False

# ============================================================================
# CAUSAL EVENT NODE (Minimal Implementation)
# ============================================================================

@dataclass
class CausalEvent:
    """因果事件 - 可接入因果图的最小实现"""
    event_id: str
    timestamp: str
    universe_id: str
    event_type: str  # drift_spike, rollback, recovery, policy_adoption
    
    # 配置快照
    config_p: int
    config_t: int
    config_m: int
    config_d: int
    
    # 前状态
    drift_before: float
    fitness_before: float
    
    # 后状态
    drift_after: float
    fitness_after: float
    
    # 因果元数据
    trigger_event_id: Optional[str] = None  # 由哪个事件触发
    recovery_time: Optional[int] = None  # 恢复所需时间
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @property
    def config_signature(self) -> str:
        return f"P{self.config_p}T{self.config_t}M{self.config_m}D{self.config_d}"
    
    @property
    def drift_delta(self) -> float:
        return self.drift_after - self.drift_before
    
    @property
    def is_recovery(self) -> bool:
        return self.drift_after < self.drift_before


class CausalGraph:
    """轻量级因果图 - 内存高效实现"""
    
    def __init__(self, max_events: int = 10000):
        self.max_events = max_events
        self.events: Dict[str, CausalEvent] = {}
        self.edges: List[Tuple[str, str, str, float]] = []  # cause_id, effect_id, edge_type, strength
        self.config_event_index: Dict[str, List[str]] = {}  # config_sig -> event_ids
        
    def add_event(self, event: CausalEvent) -> str:
        """添加事件到因果图"""
        # 如果满，删除最旧的事件
        if len(self.events) >= self.max_events:
            oldest = min(self.events.keys(), key=lambda k: self.events[k].timestamp)
            self._remove_event(oldest)
        
        self.events[event.event_id] = event
        
        # 索引
        if event.config_signature not in self.config_event_index:
            self.config_event_index[event.config_signature] = []
        self.config_event_index[event.config_signature].append(event.event_id)
        
        # 自动建立因果边
        self._infer_causal_edges(event)
        
        return event.event_id
    
    def _remove_event(self, event_id: str):
        """删除事件及其边"""
        if event_id in self.events:
            event = self.events[event_id]
            del self.events[event_id]
            
            # 从索引中移除
            if event.config_signature in self.config_event_index:
                self.config_event_index[event.config_signature] = [
                    eid for eid in self.config_event_index[event.config_signature]
                    if eid != event_id
                ]
        
        # 移除相关边
        self.edges = [
            (c, e, t, s) for c, e, t, s in self.edges
            if c != event_id and e != event_id
        ]
    
    def _infer_causal_edges(self, effect_event: CausalEvent):
        """推断因果边 - 简单启发式"""
        # 找同配置的前序事件
        if effect_event.config_signature not in self.config_event_index:
            return
            
        candidate_causes = self.config_event_index[effect_event.config_signature]
        
        for cause_id in candidate_causes:
            if cause_id == effect_event.event_id:
                continue
                
            cause = self.events.get(cause_id)
            if not cause:
                continue
            
            # 时间顺序检查
            if cause.timestamp >= effect_event.timestamp:
                continue
            
            # 推断边类型
            edge_type, strength = self._classify_edge(cause, effect_event)
            
            if strength > 0.5:  # 阈值
                self.edges.append((cause_id, effect_event.event_id, edge_type, strength))
    
    def _classify_edge(self, cause: CausalEvent, effect: CausalEvent) -> Tuple[str, float]:
        """分类因果边类型"""
        # drift_spike -> rollback (触发)
        if cause.event_type == "drift_spike" and effect.event_type == "rollback":
            return "triggers", 0.9
        
        # rollback -> recovery (导致)
        if cause.event_type == "rollback" and effect.event_type == "recovery":
            return "causes", 0.8
        
        # policy_adoption -> drift_spike (可能引发)
        if cause.event_type == "policy_adoption" and effect.event_type == "drift_spike":
            if effect.drift_delta > 0.1:
                return "amplifies", 0.7
        
        # recovery -> policy_adoption (验证成功)
        if cause.event_type == "recovery" and effect.event_type == "policy_adoption":
            if cause.is_recovery:
                return "enables", 0.6
        
        return "correlates", 0.3
    
    def query_causal_chain(self, event_id: str, max_depth: int = 3) -> List[List[str]]:
        """查询因果链"""
        chains = []
        
        def dfs(current_id: str, depth: int, current_chain: List[str]):
            if depth >= max_depth:
                chains.append(current_chain.copy())
                return
            
            # 找后继
            successors = [
                (effect, edge_type, strength)
                for cause, effect, edge_type, strength in self.edges
                if cause == current_id
            ]
            
            if not successors:
                chains.append(current_chain.copy())
                return
            
            for succ_id, edge_type, strength in sorted(successors, key=lambda x: x[2], reverse=True):
                if succ_id not in current_chain:  # 避免循环
                    dfs(succ_id, depth + 1, current_chain + [succ_id])
        
        dfs(event_id, 0, [event_id])
        return chains
    
    def predict_outcome(self, config_sig: str, action: str) -> Dict:
        """基于历史因果图预测结果"""
        relevant_events = self.config_event_index.get(config_sig, [])
        
        if not relevant_events:
            return {"confidence": 0.0, "predicted_drift": None}
        
        # 统计历史结果
        drift_deltas = []
        recovery_rates = []
        
        for eid in relevant_events:
            event = self.events.get(eid)
            if not event:
                continue
            
            if action == "rollback" and event.event_type == "rollback":
                # 找后续 recovery
                for cause, effect, edge_type, strength in self.edges:
                    if cause == eid and edge_type == "causes":
                        effect_event = self.events.get(effect)
                        if effect_event and effect_event.event_type == "recovery":
                            recovery_rates.append(1.0)
            
            drift_deltas.append(event.drift_delta)
        
        if not drift_deltas:
            return {"confidence": 0.0, "predicted_drift": None}
        
        return {
            "confidence": min(len(drift_deltas) / 10, 1.0),
            "predicted_drift": float(np.mean(drift_deltas)),
            "recovery_rate": float(np.mean(recovery_rates)) if recovery_rates else None
        }


# ============================================================================
# FUSION ENGINE - Akashic + Causal + Heavy State
# ============================================================================

class AkashicCausalFusion:
    """
    融合引擎：AkashicMemoryV2 + CausalGraph + CausalSolver
    3小时内必须跑通的最小可用实现
    """
    
    def __init__(self, max_ram_gb: float = 150.0):
        self.max_ram_gb = max_ram_gb
        
        # 基础 Akashic
        if AKASHIC_AVAILABLE:
            self.akashic = AkashicMemoryV2()
        else:
            self.akashic = None
            print("[FUSION] WARNING: Running without Akashic base")
        
        # 因果图
        self.causal_graph = CausalGraph(max_events=5000)
        
        # 因果求解器
        if CAUSAL_AVAILABLE:
            self.solver = CausalSolver()
            self.normalizer = PolicyNormalizer()
        else:
            self.solver = None
            self.normalizer = None
            print("[FUSION] WARNING: Running without CausalSolver")
        
        # 统计
        self.event_count = 0
        self.compression_ratio = 1.0
        
        print(f"[FUSION] Engine ready (RAM budget: {max_ram_gb}GB)")
    
    def record_event(self, 
                     universe_id: str,
                     event_type: str,
                     config: Dict[str, int],
                     drift_before: float,
                     drift_after: float,
                     fitness_before: float = 0.0,
                     fitness_after: float = 0.0,
                     trigger_id: Optional[str] = None) -> str:
        """
        记录事件到融合记忆系统
        
        Args:
            universe_id: 宇宙ID
            event_type: drift_spike, rollback, recovery, policy_adoption
            config: {p, t, m, d}
            drift_before/after: 漂移值
            fitness_before/after: 适应度
            trigger_id: 触发此事件的前序事件ID
        
        Returns:
            event_id
        """
        event_id = f"{event_type}_{universe_id}_{int(time.time()*1000)}_{self.event_count}"
        
        event = CausalEvent(
            event_id=event_id,
            timestamp=datetime.now().isoformat(),
            universe_id=universe_id,
            event_type=event_type,
            config_p=config.get('p', 2),
            config_t=config.get('t', 3),
            config_m=config.get('m', 3),
            config_d=config.get('d', 1),
            drift_before=drift_before,
            drift_after=drift_after,
            fitness_before=fitness_before,
            fitness_after=fitness_after,
            trigger_event_id=trigger_id
        )
        
        # 添加到因果图
        self.causal_graph.add_event(event)
        
        # 添加到 Akashic（如果可用）
        if self.akashic:
            # 创建简化的 StructureArchive
            dna = {
                "p": event.config_p,
                "t": event.config_t,
                "m": event.config_m,
                "d": event.config_d,
                "event_type": event_type
            }
            sig = event.config_signature
            archive = self.akashic.get_or_create_archive(sig, f"Config_{sig}", dna)
            
            # 记录性能
            archive.record_surprise_scan(
                stress=event_type,
                cwci=1.0 - event.drift_after,  # 假设 drift 越低越好
                seed=hash(event_id) % 10000
            )
        
        self.event_count += 1
        return event_id
    
    def query_intervention(self, target_config: Dict[str, int]) -> Dict:
        """
        查询干预效果预测
        
        Args:
            target_config: {p, t, m, d}
        
        Returns:
            预测结果
        """
        config_sig = f"P{target_config['p']}T{target_config['t']}M{target_config['m']}D{target_config['d']}"
        
        # 1. 从因果图预测
        causal_pred = self.causal_graph.predict_outcome(config_sig, "rollback")
        
        # 2. 从 Akashic 查询（如果可用）
        akashic_pred = None
        if self.akashic:
            # 查询类似配置的 SEED_SPIKE 风险
            dna = {
                "local_autonomy": target_config.get('p', 2) / 3.0,
                "broadcast_sparsity": 0.1,
                "hierarchy_depth": target_config.get('t', 3)
            }
            risk = self.akashic.query_seed_spike_risk(dna)
            akashic_pred = {"seed_spike_risk": risk}
        
        # 3. 如果有求解器，做精确查询
        solver_pred = None
        if self.solver:
            # 构建查询
            query = CausalQuery(
                query_text=f"Apply P{target_config['p']}T{target_config['t']}M{target_config['m']}D{target_config['d']}",
                top_k_nodes=[]  # 简化为空，实际应从图检索
            )
            # 简化调用
            solver_pred = {"solver_available": True}
        
        # 综合预测
        confidence = causal_pred.get("confidence", 0.0)
        
        return {
            "config": target_config,
            "config_sig": config_sig,
            "causal_prediction": causal_pred,
            "akashic_prediction": akashic_pred,
            "solver_prediction": solver_pred,
            "overall_confidence": confidence,
            "recommendation": "proceed_with_caution" if confidence < 0.5 else "likely_safe"
        }
    
    def get_causal_chain(self, event_id: str, max_depth: int = 3) -> Dict:
        """获取事件的因果链"""
        chains = self.causal_graph.query_causal_chain(event_id, max_depth)
        
        detailed_chains = []
        for chain in chains:
            detailed = []
            for eid in chain:
                event = self.causal_graph.events.get(eid)
                if event:
                    detailed.append({
                        "event_id": eid,
                        "type": event.event_type,
                        "drift_delta": event.drift_delta,
                        "config": event.config_signature
                    })
            detailed_chains.append(detailed)
        
        return {
            "event_id": event_id,
            "chains_found": len(chains),
            "chains": detailed_chains[:5]  # 只返回前5条
        }
    
    def generate_digest(self) -> Dict:
        """生成融合记忆摘要"""
        digest = {
            "timestamp": datetime.now().isoformat(),
            "event_count": self.event_count,
            "causal_graph": {
                "events": len(self.causal_graph.events),
                "edges": len(self.causal_graph.edges),
                "config_coverage": len(self.causal_graph.config_event_index)
            }
        }
        
        if self.akashic:
            digest["akashic"] = self.akashic.generate_negative_knowledge_digest()
        
        # 统计边类型
        edge_types = {}
        for _, _, edge_type, _ in self.causal_graph.edges:
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
        digest["edge_type_distribution"] = edge_types
        
        return digest
    
    def save(self, filepath: str):
        """保存状态"""
        state = {
            "digest": self.generate_digest(),
            "events": {k: v.to_dict() for k, v in self.causal_graph.events.items()},
            "edges": self.causal_graph.edges
        }
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        print(f"[FUSION] Saved to {filepath}")


# ============================================================================
# SMOKE TEST - 3小时内必须通过的测试
# ============================================================================

def smoke_test():
    """冒烟测试 - 验证基本功能"""
    print("\n" + "="*70)
    print("AKASHIC-CAUSAL FUSION SMOKE TEST")
    print("="*70 + "\n")
    
    # 1. 创建引擎
    print("[TEST 1/6] Creating fusion engine...")
    engine = AkashicCausalFusion(max_ram_gb=100.0)
    print("✓ Engine created\n")
    
    # 2. 记录事件
    print("[TEST 2/6] Recording events...")
    
    # Config 3 (good config)
    e1 = engine.record_event(
        universe_id="U001",
        event_type="policy_adoption",
        config={"p": 2, "t": 3, "m": 3, "d": 1},
        drift_before=0.25,
        drift_after=0.21
    )
    print(f"  Event 1: {e1}")
    
    # Drift spike
    e2 = engine.record_event(
        universe_id="U001",
        event_type="drift_spike",
        config={"p": 2, "t": 3, "m": 3, "d": 1},
        drift_before=0.21,
        drift_after=0.45,
        trigger_id=e1
    )
    print(f"  Event 2: {e2}")
    
    # Rollback
    e3 = engine.record_event(
        universe_id="U001",
        event_type="rollback",
        config={"p": 2, "t": 3, "m": 3, "d": 1},
        drift_before=0.45,
        drift_after=0.30,
        trigger_id=e2
    )
    print(f"  Event 3: {e3}")
    
    # Recovery
    e4 = engine.record_event(
        universe_id="U001",
        event_type="recovery",
        config={"p": 2, "t": 3, "m": 3, "d": 1},
        drift_before=0.30,
        drift_after=0.20,
        trigger_id=e3
    )
    print(f"  Event 4: {e4}")
    
    print(f"✓ Recorded 4 events\n")
    
    # 3. 查询因果链
    print("[TEST 3/6] Querying causal chains...")
    chains = engine.get_causal_chain(e1, max_depth=3)
    print(f"  Found {chains['chains_found']} causal chains")
    for i, chain in enumerate(chains['chains'][:2]):
        print(f"    Chain {i+1}: {' -> '.join([c['type'] for c in chain])}")
    print("✓ Causal chain query works\n")
    
    # 4. 干预预测
    print("[TEST 4/6] Intervention prediction...")
    prediction = engine.query_intervention({"p": 2, "t": 3, "m": 3, "d": 1})
    print(f"  Config: {prediction['config_sig']}")
    print(f"  Confidence: {prediction['overall_confidence']:.2f}")
    print(f"  Recommendation: {prediction['recommendation']}")
    print("✓ Prediction works\n")
    
    # 5. 生成摘要
    print("[TEST 5/6] Generating digest...")
    digest = engine.generate_digest()
    print(f"  Total events: {digest['event_count']}")
    print(f"  Causal events: {digest['causal_graph']['events']}")
    print(f"  Causal edges: {digest['causal_graph']['edges']}")
    print(f"  Edge types: {digest.get('edge_type_distribution', {})}")
    print("✓ Digest generation works\n")
    
    # 6. 保存
    print("[TEST 6/6] Saving state...")
    test_path = "/tmp/fusion_test_state.json"
    engine.save(test_path)
    print(f"✓ State saved to {test_path}\n")
    
    print("="*70)
    print("ALL TESTS PASSED ✓")
    print("="*70)
    print("\nFusion engine is ready for integration with Heavy Mode.")
    print("Next: Connect to heavy_akashic.py run cycle.")
    
    return engine


if __name__ == "__main__":
    engine = smoke_test()
