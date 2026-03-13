#!/usr/bin/env python3
"""
Result Aggregator
聚合原始结果为统一格式
"""

import argparse
import json
from pathlib import Path
from datetime import datetime

class ResultAggregator:
    """结果聚合器"""
    
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def aggregate(self, experiment: str = None) -> dict:
        """聚合指定实验或所有实验的结果"""
        
        if experiment:
            return self._aggregate_experiment(experiment)
        
        # 聚合所有实验
        results = {}
        for exp_dir in self.input_dir.iterdir():
            if exp_dir.is_dir():
                results[exp_dir.name] = self._aggregate_experiment(exp_dir.name)
        
        return results
    
    def _aggregate_experiment(self, experiment: str) -> dict:
        """聚合单个实验的结果"""
        
        exp_dir = self.input_dir / experiment
        if not exp_dir.exists():
            return {"error": f"Experiment not found: {experiment}"}
        
        # 读取所有结果文件
        all_results = []
        for result_file in exp_dir.rglob("*.json"):
            try:
                with open(result_file) as f:
                    data = json.load(f)
                    data["_source"] = str(result_file)
                    all_results.append(data)
            except:
                pass
        
        if not all_results:
            return {"error": "No results found"}
        
        # 按 family/scenario/seed 分组聚合
        aggregated = {
            "experiment": experiment,
            "timestamp": datetime.now().isoformat(),
            "total_runs": len(all_results),
            "by_family": {},
            "by_scenario": {},
        }
        
        for r in all_results:
            family = r.get("family", "unknown")
            scenario = r.get("scenario", "unknown")
            
            if family not in aggregated["by_family"]:
                aggregated["by_family"][family] = []
            aggregated["by_family"][family].append(r)
            
            if scenario not in aggregated["by_scenario"]:
                aggregated["by_scenario"][scenario] = []
            aggregated["by_scenario"][scenario].append(r)
        
        # 计算统计值
        for family, family_results in aggregated["by_family"].items():
            cwci_values = [r.get("metrics", {}).get("cwci", 0) for r in family_results]
            aggregated["by_family"][family] = {
                "count": len(family_results),
                "cwci_mean": sum(cwci_values) / len(cwci_values) if cwci_values else 0,
                "cwci_std": self._calc_std(cwci_values),
                "raw_results": family_results,
            }
        
        # 保存
        output_file = self.output_dir / f"{experiment}_latest.json"
        with open(output_file, 'w') as f:
            json.dump(aggregated, f, indent=2)
        
        print(f"✅ Aggregated {experiment}: {len(all_results)} runs → {output_file}")
        
        return aggregated
    
    def _calc_std(self, values: list) -> float:
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5

def main():
    parser = argparse.ArgumentParser(description="Result Aggregator")
    parser.add_argument("--input", required=True, help="Input directory with raw results")
    parser.add_argument("--output", required=True, help="Output directory for aggregated results")
    parser.add_argument("--experiment", help="Specific experiment to aggregate")
    
    args = parser.parse_args()
    
    aggregator = ResultAggregator(args.input, args.output)
    result = aggregator.aggregate(args.experiment)
    
    print(json.dumps(result, indent=2)[:500])  # 截断输出

if __name__ == "__main__":
    main()
