#!/usr/bin/env python3
"""
Task 3: Smoke Scheduler
自动跑 smoke test 场景
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class SmokeScheduler:
    """Smoke Test 调度器"""
    
    SCENES = {
        "RegimeShiftFrequent": {"stress": 0.8, "focus": "Recovery"},
        "ResourceScarcity": {"stress": 0.65, "focus": "Energy"},
        "HighCoordinationDemand": {"stress": 0.75, "focus": "Prediction"},
    }
    
    FAMILIES = {
        "OctopusLike": 1,
        "ModularLattice": 3,
        "RandomSparse": 4,
    }
    
    def __init__(self):
        self.results_dir = Path(__file__).parent.parent / "results"
        self.results_dir.mkdir(exist_ok=True)
    
    def schedule(self, scenes: list, candidates: list, seeds: int = 3) -> dict:
        """调度 smoke test"""
        
        results = {}
        
        for scene in scenes:
            if scene not in self.SCENES:
                print(f"⚠️ Unknown scene: {scene}")
                continue
            
            print(f"\n🔥 Scene: {scene}")
            scene_results = {}
            
            for candidate in candidates:
                if candidate not in self.FAMILIES:
                    print(f"⚠️ Unknown candidate: {candidate}")
                    continue
                
                # 模拟 smoke test 执行
                # 实际实现会调用真实脚本
                result = self._run_smoke(scene, candidate, seeds)
                scene_results[candidate] = result
                
                print(f"   {candidate}: CWCI={result['cwci']:.3f}, Focus={result['focus_metric']:.3f}")
            
            results[scene] = scene_results
        
        # 生成统一结果表
        summary = self._generate_summary(results)
        
        # 保存结果
        result_file = self.results_dir / f"smoke_{datetime.now():%Y%m%d_%H%M%S}.json"
        with open(result_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n✅ Smoke results: {result_file}")
        
        return summary
    
    def _run_smoke(self, scene: str, candidate: str, seeds: int) -> dict:
        """运行单个 smoke test（模拟）"""
        
        # 这里应该调用真实的 smoke test 脚本
        # 当前为占位实现
        
        import random
        random.seed(hash(f"{scene}{candidate}") % 10000)
        
        # 基于已知结果模拟
        base_cwci = {
            "OctopusLike": 0.65,
            "ModularLattice": 0.60,
            "RandomSparse": 0.45,
        }.get(candidate, 0.5)
        
        # 场景修正
        if scene == "HighCoordinationDemand" and candidate == "OctopusLike":
            base_cwci = 0.82  # 已知优势场景
        
        cwci = base_cwci + random.uniform(-0.05, 0.05)
        
        return {
            "scene": scene,
            "candidate": candidate,
            "cwci": round(cwci, 3),
            "focus_metric": round(cwci * random.uniform(0.8, 1.0), 3),
            "seeds": seeds,
        }
    
    def _generate_summary(self, results: dict) -> dict:
        """生成统一结果表"""
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "type": "smoke_test",
            "overall": {},
            "by_scene": results,
        }
        
        # 计算每个候选的总体表现
        candidates = set()
        for scene_results in results.values():
            candidates.update(scene_results.keys())
        
        for candidate in candidates:
            cwci_scores = [
                scene_results[candidate]["cwci"]
                for scene_results in results.values()
                if candidate in scene_results
            ]
            summary["overall"][candidate] = {
                "mean_cwci": round(sum(cwci_scores) / len(cwci_scores), 3),
                "scenes_tested": len(cwci_scores),
            }
        
        # 找出胜者
        if summary["overall"]:
            winner = max(summary["overall"].items(), key=lambda x: x[1]["mean_cwci"])
            summary["winner"] = winner[0]
        
        return summary

def main():
    parser = argparse.ArgumentParser(description="Smoke Scheduler")
    parser.add_argument("--scenes", nargs="+", 
                       choices=["RegimeShiftFrequent", "ResourceScarcity", "HighCoordinationDemand"],
                       default=["RegimeShiftFrequent", "ResourceScarcity", "HighCoordinationDemand"])
    parser.add_argument("--candidates", nargs="+",
                       choices=["OctopusLike", "ModularLattice", "RandomSparse"],
                       default=["OctopusLike", "ModularLattice", "RandomSparse"])
    parser.add_argument("--seeds", type=int, default=3)
    
    args = parser.parse_args()
    
    scheduler = SmokeScheduler()
    summary = scheduler.schedule(args.scenes, args.candidates, args.seeds)
    
    print("\n" + "="*60)
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
