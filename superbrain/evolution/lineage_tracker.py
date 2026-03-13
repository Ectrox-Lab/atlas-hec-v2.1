#!/usr/bin/env python3
"""
LINEAGE TRACKER - 父代来源追踪
满足协议字段1: Parental Lineage
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class LineageRecord:
    """单个种子的血统记录"""
    seed_id: str
    generation: int  # Round number
    parent_type: str  # mutation | crossover | immigrant
    parent_ids: List[str]
    mutation_operator: Optional[str] = None
    crossover_partner: Optional[str] = None
    config: Dict = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @property
    def lineage_depth(self) -> int:
        """计算血统深度（追溯轮数）"""
        if not self.parent_ids or self.parent_type == "immigrant":
            return 1
        # 实际深度需要从registry查询父代
        return 1  # 简化，实际应递归查询


class LineageTracker:
    """
    血统追踪器 - 记录每个种子的父代来源
    
    核心功能:
    1. 记录变异操作的父代
    2. 记录重组交叉的双亲
    3. 标记随机移民
    4. 提供血统追溯查询
    """
    
    def __init__(self, round_num: int):
        self.round_num = round_num
        self.records: Dict[str, LineageRecord] = {}
        self.mutation_operators = [
            "P+1", "P-1", "T+1", "T-1", "M+1", "M-1", "D+1", "D-1",
            "P+2", "P-2", "SWAP_PT", "SWAP_MD"
        ]
        
    def generate_seed_id(self, parent_id: str, op: str, idx: int) -> str:
        """生成唯一种子ID"""
        sig = f"R{self.round_num}_{parent_id}_{op}_{idx}_{datetime.now().timestamp()}"
        return f"R{self.round_num}_S{hashlib.md5(sig.encode()).hexdigest()[:4].upper()}"
    
    def record_mutation(
        self, 
        parent_config: Dict, 
        parent_id: str,
        mutation_op: str,
        child_config: Dict,
        index: int
    ) -> str:
        """
        记录变异产生的子代
        
        Returns:
            child_seed_id
        """
        seed_id = self.generate_seed_id(parent_id, mutation_op, index)
        
        record = LineageRecord(
            seed_id=seed_id,
            generation=self.round_num,
            parent_type="mutation",
            parent_ids=[parent_id],
            mutation_operator=mutation_op,
            config=child_config
        )
        
        self.records[seed_id] = record
        return seed_id
    
    def record_crossover(
        self,
        parent1_id: str,
        parent2_id: str,
        child_config: Dict,
        index: int
    ) -> str:
        """记录重组交叉产生的子代"""
        sig = f"X_{parent1_id}_{parent2_id}_{index}"
        seed_id = f"R{self.round_num}_X{hashlib.md5(sig.encode()).hexdigest()[:4].upper()}"
        
        record = LineageRecord(
            seed_id=seed_id,
            generation=self.round_num,
            parent_type="crossover",
            parent_ids=[parent1_id, parent2_id],
            crossover_partner=parent2_id,
            config=child_config
        )
        
        self.records[seed_id] = record
        return seed_id
    
    def record_immigrant(self, config: Dict, index: int) -> str:
        """记录随机移民"""
        sig = f"I_{index}_{datetime.now().timestamp()}"
        seed_id = f"R{self.round_num}_I{hashlib.md5(sig.encode()).hexdigest()[:4].upper()}"
        
        record = LineageRecord(
            seed_id=seed_id,
            generation=self.round_num,
            parent_type="immigrant",
            parent_ids=[],
            config=config
        )
        
        self.records[seed_id] = record
        return seed_id
    
    def get_lineage(self, seed_id: str, depth: int = 5) -> List[Dict]:
        """
        追溯血统
        
        Returns:
            从当前种子向上追溯的lineage链
        """
        chain = []
        current_id = seed_id
        
        for _ in range(depth):
            if current_id not in self.records:
                break
            
            record = self.records[current_id]
            chain.append(record.to_dict())
            
            # 向上追溯
            if record.parent_ids:
                current_id = record.parent_ids[0]  # 主要父代
            else:
                break
        
        return chain
    
    def get_mutation_stats(self) -> Dict:
        """获取变异统计"""
        stats = defaultdict(int)
        for record in self.records.values():
            if record.mutation_operator:
                stats[record.mutation_operator] += 1
        return dict(stats)
    
    def export_registry(self) -> Dict:
        """导出完整注册表"""
        return {
            "round": self.round_num,
            "total_seeds": len(self.records),
            "by_type": {
                "mutation": len([r for r in self.records.values() if r.parent_type == "mutation"]),
                "crossover": len([r for r in self.records.values() if r.parent_type == "crossover"]),
                "immigrant": len([r for r in self.records.values() if r.parent_type == "immigrant"])
            },
            "mutation_stats": self.get_mutation_stats(),
            "records": {k: v.to_dict() for k, v in self.records.items()}
        }
    
    def save(self, filepath: str):
        """保存到文件"""
        with open(filepath, 'w') as f:
            json.dump(self.export_registry(), f, indent=2)


# ============================================================================
# 测试
# ============================================================================

if __name__ == "__main__":
    print("LINEAGE TRACKER TEST")
    print("=" * 50)
    
    tracker = LineageTracker(round_num=3)
    
    # 模拟上一轮精英
    elites = [
        ("R2_E01", {"P": 2, "T": 3, "M": 3, "D": 1}),
        ("R2_E02", {"P": 2, "T": 4, "M": 4, "D": 2}),
    ]
    
    # 1. 记录变异
    print("\n1. Recording mutations...")
    for parent_id, parent_config in elites:
        for i in range(3):
            op = tracker.mutation_operators[i % len(tracker.mutation_operators)]
            child_config = parent_config.copy()
            child_config["D"] += 1  # 模拟变异
            
            seed_id = tracker.record_mutation(
                parent_config, parent_id, op, child_config, i
            )
            print(f"  {parent_id} --[{op}]--> {seed_id}")
    
    # 2. 记录重组
    print("\n2. Recording crossovers...")
    for i in range(2):
        p1, p2 = elites[0][0], elites[1][0]
        child_config = {"P": 2, "T": 3, "M": 4, "D": 1}  # 混合
        
        seed_id = tracker.record_crossover(p1, p2, child_config, i)
        print(f"  {p1} x {p2} --> {seed_id}")
    
    # 3. 记录移民
    print("\n3. Recording immigrants...")
    for i in range(2):
        config = {"P": 4, "T": 4, "M": 4, "D": 2}
        seed_id = tracker.record_immigrant(config, i)
        print(f"  random --> {seed_id}")
    
    # 统计
    print("\n4. Statistics:")
    stats = tracker.export_registry()
    print(f"  Total seeds: {stats['total_seeds']}")
    print(f"  By type: {stats['by_type']}")
    print(f"  Mutation ops: {stats['mutation_stats']}")
    
    print("\n✓ Lineage Tracker Test Complete")
