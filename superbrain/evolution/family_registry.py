#!/usr/bin/env python3
"""
FAMILY REGISTRY - 家族延续性追踪
满足协议字段3: Family Continuity
"""

import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class FamilyGeneration:
    """单轮中的家族表现"""
    round: int
    rank: int  # 最佳成员排名
    members: List[str]  # 成员ID列表
    avg_score: float
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ArchitectureFamily:
    """架构家族 - 核心配置签名相同的候选集群"""
    family_id: str  # 如 "F_P2T3M3"
    core_signature: Dict  # {P: 2, T: 3, M: 3} 忽略D
    created_round: int
    generations: List[FamilyGeneration]
    family_age: int = 0  # 连续存活轮数
    adaptation_trend: str = "stable"  # improving | stable | declining
    convergence_score: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "family_id": self.family_id,
            "core_signature": self.core_signature,
            "created_round": self.created_round,
            "family_age": self.family_age,
            "adaptation_trend": self.adaptation_trend,
            "convergence_score": self.convergence_score,
            "generations": [g.to_dict() for g in self.generations]
        }


class FamilyRegistry:
    """
    家族注册表 - 追踪架构家族的跨轮延续性
    
    核心功能:
    1. 识别候选所属的家族 (基于核心配置签名)
    2. 记录每轮家族表现
    3. 计算家族延续性和收敛度
    4. 识别稳定占据前列的架构家族
    """
    
    def __init__(self):
        self.families: Dict[str, ArchitectureFamily] = {}
        self.current_round = 0
        
    def get_core_signature(self, config: Dict) -> Tuple[str, Dict]:
        """
        提取核心配置签名 (忽略D)
        
        Returns:
            (family_id, core_config)
        """
        core = {
            "P": config.get("P", config.get("p", 2)),
            "T": config.get("T", config.get("t", 3)),
            "M": config.get("M", config.get("m", 3))
        }
        family_id = f"F_P{core['P']}T{core['T']}M{core['M']}"
        return family_id, core
    
    def belongs_to_family(self, config: Dict, family: ArchitectureFamily) -> bool:
        """判断配置是否属于某家族 (允许±1偏差)"""
        config_family_id, config_core = self.get_core_signature(config)
        
        if config_family_id == family.family_id:
            return True
        
        # 检查是否在±1范围内
        for dim in ["P", "T", "M"]:
            if abs(config_core[dim] - family.core_signature[dim]) > 1:
                return False
        
        return True
    
    def register_candidates(
        self, 
        round_num: int, 
        top_candidates: List[Dict]
    ) -> Dict:
        """
        注册本轮候选，更新家族记录
        
        Args:
            round_num: 当前轮次
            top_candidates: 排名前列的候选列表，每项包含config和score
        
        Returns:
            家族延续性评估报告
        """
        self.current_round = round_num
        
        # 按家族分组
        family_members: Dict[str, List[Dict]] = defaultdict(list)
        
        for rank, candidate in enumerate(top_candidates, 1):
            config = candidate.get("config", candidate)
            family_id, core = self.get_core_signature(config)
            
            # 创建或获取家族
            if family_id not in self.families:
                self.families[family_id] = ArchitectureFamily(
                    family_id=family_id,
                    core_signature=core,
                    created_round=round_num,
                    generations=[]
                )
            
            family_members[family_id].append({
                "rank": rank,
                "candidate": candidate,
                "score": candidate.get("score", 0)
            })
        
        # 更新每个家族
        for family_id, members in family_members.items():
            family = self.families[family_id]
            
            # 创建generation记录
            best = min(members, key=lambda x: x["rank"])
            generation = FamilyGeneration(
                round=round_num,
                rank=best["rank"],
                members=[f"R{round_num}_E{m['rank']:02d}" for m in members],
                avg_score=np.mean([m["score"] for m in members])
            )
            
            family.generations.append(generation)
            
            # 更新家族年龄
            if len(family.generations) >= 2:
                # 检查上一轮是否有记录
                prev_rounds = [g.round for g in family.generations]
                if round_num - 1 in prev_rounds:
                    family.family_age += 1
                else:
                    family.family_age = 1  # 中断后重新计数
            else:
                family.family_age = 1
            
            # 计算适应趋势
            family.adaptation_trend = self._compute_trend(family)
            
            # 计算收敛度
            family.convergence_score = self._compute_convergence(family)
        
        # 标记未出现的家族为declining
        for family_id, family in self.families.items():
            if family_id not in family_members:
                family.adaptation_trend = "declining"
        
        return self.generate_report()
    
    def _compute_trend(self, family: ArchitectureFamily) -> str:
        """计算家族的适应趋势"""
        if len(family.generations) < 2:
            return "stable"
        
        # 看最近3轮排名变化
        recent = family.generations[-3:]
        ranks = [g.rank for g in recent]
        
        if len(ranks) >= 2:
            if ranks[-1] < ranks[0]:  # 排名提升 (数字变小)
                return "improving"
            elif ranks[-1] > ranks[0]:
                return "declining"
        
        return "stable"
    
    def _compute_convergence(self, family: ArchitectureFamily) -> float:
        """计算家族内部收敛度"""
        if len(family.generations) < 2:
            return 0.0
        
        # 基于排名的稳定性
        recent_ranks = [g.rank for g in family.generations[-3:]]
        if len(recent_ranks) >= 2:
            rank_variance = np.var(recent_ranks)
            # 方差越小，收敛度越高
            convergence = max(0, 1.0 - rank_variance / 10.0)
            return float(convergence)
        
        return 0.0
    
    def get_dominant_families(self, min_age: int = 3) -> List[ArchitectureFamily]:
        """
        获取占据主导地位家族
        
        Args:
            min_age: 最小连续存活轮数
        
        Returns:
            按family_age和convergence排序的家族列表
        """
        dominant = [
            f for f in self.families.values()
            if f.family_age >= min_age and f.adaptation_trend != "declining"
        ]
        
        # 按年龄和收敛度排序
        dominant.sort(key=lambda f: (f.family_age, f.convergence_score), reverse=True)
        return dominant
    
    def check_convergence_criteria(
        self, 
        min_age: int = 3, 
        min_convergence: float = 0.85
    ) -> Optional[ArchitectureFamily]:
        """
        检查是否有家族满足收敛标准
        
        Returns:
            满足标准的家族，或None
        """
        for family in self.families.values():
            if (family.family_age >= min_age and 
                family.convergence_score >= min_convergence):
                return family
        return None
    
    def generate_report(self) -> Dict:
        """生成家族延续性报告"""
        return {
            "current_round": self.current_round,
            "total_families": len(self.families),
            "active_families": len([
                f for f in self.families.values() 
                if f.adaptation_trend != "declining"
            ]),
            "dominant_families": [
                f.family_id for f in self.get_dominant_families(min_age=2)
            ],
            "convergence_candidate": self.check_convergence_criteria(),
            "families": {k: v.to_dict() for k, v in self.families.items()}
        }
    
    def save(self, filepath: str):
        """保存注册表"""
        report = self.generate_report()
        # Convert families to dict for JSON serialization
        report['families'] = {k: v.to_dict() if hasattr(v, 'to_dict') else v 
                             for k, v in report.get('families', {}).items()}
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)


# ============================================================================
# 测试
# ============================================================================

if __name__ == "__main__":
    print("FAMILY REGISTRY TEST")
    print("=" * 50)
    
    registry = FamilyRegistry()
    
    # 模拟3轮演化
    for round_num in range(1, 4):
        print(f"\n--- Round {round_num} ---")
        
        # 模拟top-6候选
        if round_num == 1:
            candidates = [
                {"P": 2, "T": 3, "M": 3, "D": 1, "score": 0.95},  # F_P2T3M3
                {"P": 2, "T": 3, "M": 3, "D": 2, "score": 0.93},  # 同家族
                {"P": 3, "T": 4, "M": 4, "D": 1, "score": 0.87},  # F_P3T4M4
                {"P": 1, "T": 2, "M": 2, "D": 1, "score": 0.82},
                {"P": 2, "T": 3, "M": 4, "D": 1, "score": 0.79},  # 邻域
                {"P": 4, "T": 4, "M": 4, "D": 2, "score": 0.75},
            ]
        elif round_num == 2:
            # F_P2T3M3 继续表现好
            candidates = [
                {"P": 2, "T": 3, "M": 3, "D": 1, "score": 0.96},
                {"P": 2, "T": 3, "M": 3, "D": 3, "score": 0.94},
                {"P": 2, "T": 4, "M": 3, "D": 1, "score": 0.88},  # 邻域
                {"P": 3, "T": 4, "M": 4, "D": 2, "score": 0.85},
                {"P": 2, "T": 3, "M": 4, "D": 1, "score": 0.81},
                {"P": 1, "T": 2, "M": 2, "D": 2, "score": 0.78},
            ]
        else:  # round 3
            # F_P2T3M3 家族继续占据前列
            candidates = [
                {"P": 2, "T": 3, "M": 3, "D": 2, "score": 0.97},
                {"P": 2, "T": 3, "M": 3, "D": 1, "score": 0.95},
                {"P": 2, "T": 3, "M": 4, "D": 1, "score": 0.90},
                {"P": 3, "T": 4, "M": 4, "D": 1, "score": 0.86},
                {"P": 2, "T": 4, "M": 4, "D": 2, "score": 0.83},
                {"P": 1, "T": 2, "M": 3, "D": 1, "score": 0.80},
            ]
        
        report = registry.register_candidates(round_num, candidates)
        
        print(f"  Total families: {report['total_families']}")
        print(f"  Active families: {report['active_families']}")
        print(f"  Dominant families: {report['dominant_families']}")
    
    # 最终报告
    print("\n" + "=" * 50)
    print("FINAL FAMILY CONTINUITY REPORT")
    print("=" * 50)
    
    for family_id, family in registry.families.items():
        print(f"\n{family_id}:")
        print(f"  Age: {family.family_age} rounds")
        print(f"  Trend: {family.adaptation_trend}")
        print(f"  Convergence: {family.convergence_score:.2f}")
        print(f"  Generations: {len(family.generations)}")
    
    # 检查收敛
    converged = registry.check_convergence_criteria(min_age=3, min_convergence=0.7)
    if converged:
        print(f"\n✓ CONVERGENCE DETECTED: {converged.family_id}")
    else:
        print("\n⚠ No convergence yet (need more rounds)")
    
    print("\n✓ Family Registry Test Complete")
