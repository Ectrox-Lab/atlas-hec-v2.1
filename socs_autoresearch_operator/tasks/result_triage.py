#!/usr/bin/env python3
"""
Task 2: Result Triage
比较结果，输出诊断
top candidate / first failure mode / limitation / recommendation
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

class ResultTriage:
    def __init__(self, results_dir: str = "../results"):
        self.results_dir = Path(__file__).parent.parent / "results"
        self.proposals_dir = Path(__file__).parent.parent / "proposals"
        self.proposals_dir.mkdir(exist_ok=True)
    
    def triage(self, result_files: list) -> dict:
        """对多个结果进行比较诊断"""
        
        results = []
        for f in result_files:
            path = self.results_dir / f
            if path.exists():
                with open(path) as fp:
                    results.append(json.load(fp))
        
        if not results:
            return {"error": "No results found"}
        
        # 找出 top candidate
        top_candidate = self._find_top_candidate(results)
        
        # 识别 first failure mode
        failure_mode = self._identify_failure_mode(results)
        
        # 判断 limitation
        limitation = self._assess_limitation(results)
        
        # 生成 recommendation
        recommendation = self._generate_recommendation(results, failure_mode)
        
        triage_report = {
            "timestamp": datetime.now().isoformat(),
            "top_candidate": top_candidate,
            "first_failure_mode": failure_mode,
            "limitation": limitation,
            "recommendation": recommendation,
            "detailed_results": [
                {
                    "hypothesis": r["hypothesis"],
                    "gate": r["gate"],
                    "verdict": r["verdict"],
                    "metrics": r["metrics"]
                }
                for r in results
            ]
        }
        
        # 保存提案
        proposal_file = self.proposals_dir / f"triage_{datetime.now():%Y%m%d_%H%M%S}.json"
        with open(proposal_file, 'w') as f:
            json.dump(triage_report, f, indent=2)
        
        print(f"📋 Triage report: {proposal_file}")
        print(f"   Top candidate: {top_candidate}")
        print(f   "   Failure mode: {failure_mode}")
        print(f"   Limitation: {limitation}")
        print(f"   Recommendation: {recommendation}")
        
        return triage_report
    
    def _find_top_candidate(self, results: list) -> str:
        """找出当前最佳候选"""
        # 按 CWCI 排序
        best = max(results, key=lambda r: r.get("metrics", {}).get("cwci", 0))
        return f"{best['hypothesis']} ({best['gate']}, CWCI={best['metrics'].get('cwci', 0):.3f})"
    
    def _identify_failure_mode(self, results: list) -> str:
        """识别 first failure mode"""
        failed = [r for r in results if r["verdict"] in ["PARTIAL", "FAILED"]]
        
        if not failed:
            return "none"
        
        # OQS Gate 1 已知的 failure mode
        for r in failed:
            if r["hypothesis"] == "OQS" and r["gate"] == "Gate_1":
                if r["metrics"].get("cwci", 1) < 0.1:
                    return "budget_conservative"
        
        return "unknown"
    
    def _assess_limitation(self, results: list) -> str:
        """评估限制类型"""
        # 检查是否有 simulation-limited 标记
        for r in results:
            if "SIMULATION" in r.get("raw_output", ""):
                return "SIMULATION-LIMITED"
        return "UNKNOWN"
    
    def _generate_recommendation(self, results: list, failure_mode: str) -> str:
        """生成建议"""
        if failure_mode == "budget_conservative":
            return "Apply 3 minimal corrections: dynamic budget, lower return threshold, gentler culling"
        
        # 检查是否有 PASSED 的 Gate 2
        has_gate2_pass = any(
            r["hypothesis"] == "O1" and r["gate"] == "Gate_2" and r["verdict"] == "PASSED"
            for r in results
        )
        
        if has_gate2_pass:
            return "Proceed to open-world smoke test"
        
        return "Continue gate validation"

def main():
    parser = argparse.ArgumentParser(description="Result Triage")
    parser.add_argument("--results", nargs="+", help="Result JSON files to compare")
    
    args = parser.parse_args()
    
    triage = ResultTriage()
    report = triage.triage(args.results or [])
    
    print("\n" + "="*60)
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
