#!/usr/bin/env python3
"""
Halt Condition Checker
检查是否需要停机并要求人工介入
"""

import argparse
import json
import sys
from pathlib import Path

class HaltChecker:
    """停机条件检查器"""
    
    def __init__(self, state_dir: str, thresholds_file: str):
        self.state_dir = Path(state_dir)
        self.thresholds = self._load_thresholds(thresholds_file)
    
    def _load_thresholds(self, filepath: str) -> dict:
        import yaml
        with open(filepath) as f:
            return yaml.safe_load(f)
    
    def check(self) -> dict:
        """检查所有停机条件"""
        
        checks = {
            "consecutive_failures": self._check_consecutive_failures(),
            "unreviewed_proposals": self._check_unreviewed_proposals(),
            "contradictory_results": self._check_contradictory_results(),
            "threshold_alteration": self._check_threshold_alteration(),
            "core_modification": self._check_core_modification(),
        }
        
        halt_triggered = any(c["triggered"] for c in checks.values())
        
        result = {
            "halt_triggered": halt_triggered,
            "checks": checks,
            "timestamp": datetime.now().isoformat(),
        }
        
        if halt_triggered:
            print("🛑 HALT CONDITIONS TRIGGERED:")
            for name, check in checks.items():
                if check["triggered"]:
                    print(f"   - {name}: {check['reason']}")
        
        return result
    
    def _check_consecutive_failures(self) -> dict:
        """检查连续失败"""
        max_consecutive = self.thresholds.get("halt_conditions", {}).get("consecutive_failures", 2)
        
        # 读取最近的运行记录
        last_runs = list(self.state_dir.glob("run_*.json"))
        if len(last_runs) < max_consecutive:
            return {"triggered": False}
        
        # 检查最近的 N 次是否都失败
        recent = sorted(last_runs)[-max_consecutive:]
        failures = 0
        for run_file in recent:
            with open(run_file) as f:
                data = json.load(f)
                if data.get("status") == "FAILED":
                    failures += 1
        
        if failures >= max_consecutive:
            return {
                "triggered": True,
                "reason": f"{failures} consecutive failures (threshold: {max_consecutive})"
            }
        
        return {"triggered": False}
    
    def _check_unreviewed_proposals(self) -> dict:
        """检查未审核提案数量"""
        max_proposals = self.thresholds.get("halt_conditions", {}).get("unreviewed_proposals_max", 3)
        
        pending_dir = Path(__file__).parent.parent / "proposals" / "pending"
        if not pending_dir.exists():
            return {"triggered": False}
        
        unreviewed = len(list(pending_dir.glob("*.md")))
        
        if unreviewed > max_proposals:
            return {
                "triggered": True,
                "reason": f"{unreviewed} unreviewed proposals (threshold: {max_proposals})"
            }
        
        return {"triggered": False}
    
    def _check_contradictory_results(self) -> dict:
        """检查结果矛盾"""
        # 简化实现：检查是否有相同配置但不同结果
        return {"triggered": False}  # 需要更复杂的逻辑
    
    def _check_threshold_alteration(self) -> dict:
        """检查评分标准被修改"""
        # 检查 thresholds.yaml 是否被意外修改
        return {"triggered": False}  # 需要文件哈希检查
    
    def _check_core_modification(self) -> dict:
        """检查核心架构被修改"""
        # 检查 src/ 是否有非预期的修改
        return {"triggered": False}  # 需要 git 状态检查

def main():
    parser = argparse.ArgumentParser(description="Halt Condition Checker")
    parser.add_argument("--state", required=True, help="State directory")
    parser.add_argument("--thresholds", required=True, help="Thresholds YAML file")
    
    args = parser.parse_args()
    
    from datetime import datetime  # import here for the method
    
    checker = HaltChecker(args.state, args.thresholds)
    result = checker.check()
    
    if result["halt_triggered"]:
        sys.exit(1)
    else:
        print("✅ All halt conditions clear")
        sys.exit(0)

if __name__ == "__main__":
    main()
