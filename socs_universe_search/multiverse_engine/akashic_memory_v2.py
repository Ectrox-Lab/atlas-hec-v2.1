#!/usr/bin/env python3
"""
Akashic Memory System v2.0
新增：负面知识 + SEED_SPIKE 标签
"""

import json
import hashlib
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# ============ SEED_SPIKE 定义 ============
@dataclass
class SeedSpikeProfile:
    """
    SEED_SPIKE: 单次或少量seeds下出现异常高分，
    但跨seeds无法稳定复现的候选
    """
    detected: bool
    original_cwci: float
    replication_cwci_min: float
    replication_cwci_variance: float
    seeds_tested: int
    
    def severity(self) -> str:
        """返回严重程度"""
        if not self.detected:
            return "none"
        drop = self.original_cwci - self.replication_cwci_min
        if drop > 0.20:
            return "critical"
        elif drop > 0.10:
            return "high"
        elif drop > 0.05:
            return "medium"
        return "low"


# ============ 结构档案 ============
class StructureArchive:
    """
    单个结构的完整档案 - 正面与负面知识并存
    """
    
    def __init__(self, signature: str, family: str, dna: Dict):
        self.signature = signature
        self.family = family
        self.dna = dna
        self.created_at = datetime.now().isoformat()
        
        # 表现记录
        self.performance_by_stress = {}  # stress -> [cwci samples]
        self.performance_by_seed = {}    # seed -> cwci
        
        # 验证状态
        self.replication_status = "untested"  # untested/passed/failed
        self.intake_status = "pending"        # pending/accepted/rejected
        
        # SEED_SPIKE 档案
        self.seed_spike = SeedSpikeProfile(
            detected=False,
            original_cwci=0.0,
            replication_cwci_min=0.0,
            replication_cwci_variance=0.0,
            seeds_tested=0
        )
        
        # 负面知识
        self.negative_knowledge = {
            "failure_modes": [],           # 观察到的失败模式
            "fragility_indicators": [],    # 脆弱性指标
            "non_robust_conditions": [],   # 非稳健条件
            "rejection_reason": None       # 拒绝原因
        }
        
        # 设计原则 (从摘要中提取)
        self.design_principles = []
        
    def record_surprise_scan(self, stress: str, cwci: float, seed: int):
        """记录P2.5 surprise scan结果"""
        if stress not in self.performance_by_stress:
            self.performance_by_stress[stress] = []
        self.performance_by_stress[stress].append(cwci)
        self.performance_by_seed[seed] = cwci
        
    def record_replication_attempt(self, seeds: List[int], cwcis: List[float]):
        """记录复现尝试结果"""
        self.seed_spike.seeds_tested = len(seeds)
        
        if len(cwcis) == 0:
            return
            
        mean_cwci = sum(cwcis) / len(cwcis)
        min_cwci = min(cwcis)
        variance = sum((c - mean_cwci)**2 for c in cwcis) / len(cwcis)
        
        # 检测SEED_SPIKE
        if len(self.performance_by_seed) > 0:
            original_max = max(self.performance_by_seed.values())
            self.seed_spike.detected = (original_max - min_cwci) > 0.10
            self.seed_spike.original_cwci = original_max
            self.seed_spike.replication_cwci_min = min_cwci
            self.seed_spike.replication_cwci_variance = variance
            
        # 判定复现状态
        cv = (variance ** 0.5) / mean_cwci if mean_cwci > 0 else float('inf')
        if min_cwci < 0.75 or cv > 0.10:
            self.replication_status = "failed"
            self.intake_status = "rejected"
            self.negative_knowledge["rejection_reason"] = "seed_spike_detected"
        else:
            self.replication_status = "passed"
            
    def classify_failure_mode(self, failure_type: str, context: str):
        """分类并记录失败模式"""
        self.negative_knowledge["failure_modes"].append({
            "type": failure_type,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })
        
    def extract_lessons(self) -> Dict:
        """提取可继承的知识"""
        lessons = {
            "structure_type": self.family,
            "robustness": "high" if self.replication_status == "passed" else "low",
            "seed_spike_risk": self.seed_spike.severity(),
            "avoid_combinations": [],
            "promising_combinations": []
        }
        
        # 从DNA分析
        dna = self.dna
        if dna.get("local_autonomy", 0) > 0.8 and dna.get("hierarchy_depth", 0) < 2:
            lessons["avoid_combinations"].append("high_autonomy_low_hierarchy")
            
        if self.seed_spike.detected and dna.get("broadcast_sparsity", 0.1) < 0.05:
            lessons["avoid_combinations"].append("ultra_sparse_broadcast_unstable")
            
        return lessons
        
    def to_dict(self) -> Dict:
        """序列化为字典"""
        return {
            "signature": self.signature,
            "family": self.family,
            "dna": self.dna,
            "created_at": self.created_at,
            "performance_summary": {
                "stress_coverage": len(self.performance_by_stress),
                "seed_samples": len(self.performance_by_seed),
                "max_cwci": max(self.performance_by_seed.values()) if self.performance_by_seed else 0
            },
            "validation_status": {
                "replication": self.replication_status,
                "intake": self.intake_status,
                "seed_spike_detected": self.seed_spike.detected,
                "seed_spike_severity": self.seed_spike.severity()
            },
            "negative_knowledge": self.negative_knowledge,
            "lessons": self.extract_lessons()
        }


# ============ 阿卡西系统 v2 ============
class AkashicMemoryV2:
    """
    跨宇宙记忆系统 v2.0
    记住什么有效，也记住什么无效
    """
    
    def __init__(self):
        self.structures = {}  # signature -> StructureArchive
        self.seed_spike_registry = []  # 已识别的SEED_SPIKE列表
        self.failure_clusters = {}     # 失败模式聚类
        self.robust_patterns = []      # 稳健模式库
        
    def get_or_create_archive(self, signature: str, family: str, dna: Dict) -> StructureArchive:
        """获取或创建结构档案"""
        if signature not in self.structures:
            self.structures[signature] = StructureArchive(signature, family, dna)
        return self.structures[signature]
        
    def record_seed_spike(self, archive: StructureArchive):
        """正式记录SEED_SPIKE"""
        entry = {
            "signature": archive.signature,
            "family": archive.family,
            "original_cwci": archive.seed_spike.original_cwci,
            "replication_min": archive.seed_spike.replication_cwci_min,
            "drop": round(archive.seed_spike.original_cwci - archive.seed_spike.replication_cwci_min, 3),
            "dna_features": {
                "autonomy": archive.dna.get("local_autonomy"),
                "hierarchy": archive.dna.get("hierarchy_depth"),
                "broadcast": archive.dna.get("broadcast_sparsity")
            },
            "lessons": archive.extract_lessons()
        }
        self.seed_spike_registry.append(entry)
        
    def query_seed_spike_risk(self, dna: Dict) -> float:
        """
        查询类似DNA的SEED_SPIKE风险
        返回0-1的风险分数
        """
        if not self.seed_spike_registry:
            return 0.5  # 未知
            
        # 特征匹配
        risk_scores = []
        for entry in self.seed_spike_registry:
            features = entry["dna_features"]
            match_score = 0.0
            
            if abs(features["autonomy"] - dna.get("local_autonomy", 0)) < 0.15:
                match_score += 0.3
            if abs(features["hierarchy"] - dna.get("hierarchy_depth", 0)) <= 1:
                match_score += 0.3
            if abs(features["broadcast"] - dna.get("broadcast_sparsity", 0)) < 0.05:
                match_score += 0.4
                
            if match_score > 0.5:
                risk_scores.append(match_score)
                
        if not risk_scores:
            return 0.3  # 低-中风险
            
        return sum(risk_scores) / len(risk_scores)
        
    def generate_negative_knowledge_digest(self) -> Dict:
        """生成负面知识摘要"""
        return {
            "total_structures_scanned": len(self.structures),
            "seed_spikes_detected": len(self.seed_spike_registry),
            "rejected_by_intake": sum(1 for s in self.structures.values() if s.intake_status == "rejected"),
            "common_failure_patterns": self._cluster_failures(),
            "fragile_combinations": self._identify_fragile_combinations(),
            "robust_patterns": len(self.robust_patterns)
        }
        
    def _cluster_failures(self) -> List[Dict]:
        """聚类失败模式"""
        clusters = {}
        for archive in self.structures.values():
            for failure in archive.negative_knowledge["failure_modes"]:
                ftype = failure["type"]
                if ftype not in clusters:
                    clusters[ftype] = []
                clusters[ftype].append(archive.signature)
                
        return [{"failure_type": k, "count": len(v), "examples": v[:3]} 
                for k, v in sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)]
                
    def _identify_fragile_combinations(self) -> List[str]:
        """识别脆弱组合"""
        fragile = set()
        for entry in self.seed_spike_registry:
            for combo in entry["lessons"].get("avoid_combinations", []):
                fragile.add(combo)
        return list(fragile)
        
    def save(self, filepath: str):
        """保存阿卡西记忆"""
        data = {
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "structures": {k: v.to_dict() for k, v in self.structures.items()},
            "seed_spike_registry": self.seed_spike_registry,
            "negative_knowledge_digest": self.generate_negative_knowledge_digest()
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
            
    def load(self, filepath: str):
        """加载阿卡西记忆"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        # 简化加载 - 实际使用需要完整反序列化
        self.seed_spike_registry = data.get("seed_spike_registry", [])


# ============ 使用示例 ============
if __name__ == "__main__":
    # 初始化阿卡西
    akashic = AkashicMemoryV2()
    
    # 模拟记录3个失败的候选
    candidates = [
        ("157b", "AutonomousHierarchical", {
            "local_autonomy": 0.75, "broadcast_sparsity": 0.08,
            "hierarchy_depth": 3, "division_strength": 0.45
        }),
        ("41c0", "Autonomous", {
            "local_autonomy": 0.82, "broadcast_sparsity": 0.05,
            "hierarchy_depth": 1, "division_strength": 0.20
        }),
        ("92ec", "AutonomousDividedMemorious", {
            "local_autonomy": 0.68, "broadcast_sparsity": 0.06,
            "hierarchy_depth": 2, "division_strength": 0.55
        })
    ]
    
    for sig, family, dna in candidates:
        archive = akashic.get_or_create_archive(sig, family, dna)
        
        # 记录原始惊喜扫描结果
        archive.record_surprise_scan("ResourceScarcity", 0.90 + hash(sig) % 20 / 100, 42)
        
        # 记录复现失败
        archive.record_replication_attempt([101, 202, 303], [0.815, 0.837, 0.749])
        archive.record_seed_spike(archive)
        archive.classify_failure_mode("seed_spike", "High variance across seeds")
        
    # 保存
    akashic.save("outputs/akashic_memory_v2.json")
    
    # 输出摘要
    digest = akashic.generate_negative_knowledge_digest()
    print("\n" + "="*60)
    print("AKASHIC MEMORY V2 - NEGATIVE KNOWLEDGE DIGEST")
    print("="*60)
    print(f"Structures scanned: {digest['total_structures_scanned']}")
    print(f"SEED_SPIKEs detected: {digest['seed_spikes_detected']}")
    print(f"Rejected by intake: {digest['rejected_by_intake']}")
    print(f"\nFragile combinations identified:")
    for combo in digest['fragile_combinations']:
        print(f"  ⚠️ {combo}")
    print("="*60)
