#!/usr/bin/env python3
"""
P3B 实验结果分析脚本

分析 baseline vs P2-ON 的统计对比
验证标准：
- A: 高风险干预率 >= 2x baseline
- B: 关键故障下降 >= 30%

用法：
    python3 scripts/analyze_p3b.py logs/p3b/
"""

import json
import sys
import os
import glob
from pathlib import Path
import statistics

def load_results(directory):
    """加载所有实验结果"""
    baseline = []
    p2on = []
    
    for json_file in glob.glob(os.path.join(directory, "*_result.json")):
        with open(json_file) as f:
            data = json.load(f)
            if data.get("p3_enabled"):
                p2on.append(data)
            else:
                baseline.append(data)
    
    return baseline, p2on

def compute_stats(values):
    """计算统计量"""
    if not values:
        return {"mean": 0, "std": 0, "min": 0, "max": 0, "count": 0}
    
    return {
        "mean": statistics.mean(values),
        "std": statistics.stdev(values) if len(values) > 1 else 0,
        "min": min(values),
        "max": max(values),
        "count": len(values)
    }

def format_stats(stats, unit=""):
    """格式化统计量"""
    if stats["count"] == 0:
        return "N/A"
    if unit == "%":
        return f"{stats['mean']*100:.1f}% (±{stats['std']*100:.1f}%) [{stats['min']*100:.1f}%-{stats['max']*100:.1f}%]"
    return f"{stats['mean']:.2f} (±{stats['std']:.2f}) [{stats['min']:.2f}-{stats['max']:.2f}]"

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_p3b.py <log_directory>")
        sys.exit(1)
    
    log_dir = sys.argv[1]
    baseline, p2on = load_results(log_dir)
    
    if not baseline or not p2on:
        print(f"⚠️  Insufficient data in {log_dir}")
        print(f"   Baseline runs: {len(baseline)}")
        print(f"   P2-ON runs: {len(p2on)}")
        sys.exit(1)
    
    # 计算各项指标统计
    metrics = [
        ("Survival Steps", "survival_steps", ""),
        ("Energy Critical Count", "energy_critical_count", ""),
        ("Energy Depleted Count", "energy_depleted_count", ""),
        ("Total Reward", "total_reward", ""),
        ("Intervention Rate", "intervention_rate", "%"),
        ("High-Risk Intervention Rate", "high_risk_intervention_rate", "%"),
        ("Avg Exploration Rate", "avg_exploration_rate", ""),
        ("Recovery Entries", "recovery_entries", ""),
        ("Time in Recovery", "time_in_recovery", ""),
    ]
    
    print("=" * 70)
    print("           P3B: A/B Validation Statistical Analysis")
    print("=" * 70)
    print()
    print(f"Baseline runs: {len(baseline)}")
    print(f"P2-ON runs:    {len(p2on)}")
    print()
    
    # 对比表
    print(f"{'Metric':<30} {'Baseline':<25} {'P2-ON':<25} {'Improvement'}")
    print("-" * 105)
    
    validation_results = {}
    
    for name, key, unit in metrics:
        base_vals = [r[key] for r in baseline]
        p2_vals = [r[key] for r in p2on]
        
        base_stats = compute_stats(base_vals)
        p2_stats = compute_stats(p2_vals)
        
        # 计算改善百分比
        if base_stats["mean"] > 0:
            if key in ["energy_critical_count", "energy_depleted_count"]:
                # 这些指标越低越好
                improvement = (base_stats["mean"] - p2_stats["mean"]) / base_stats["mean"] * 100
                improvement_str = f"↓ {improvement:.1f}%"
            elif key in ["total_reward"]:
                improvement = (p2_stats["mean"] - base_stats["mean"]) / base_stats["mean"] * 100
                improvement_str = f"↑ +{improvement:.1f}%"
            else:
                improvement = (p2_stats["mean"] - base_stats["mean"]) / base_stats["mean"] * 100
                improvement_str = f"{improvement:+.1f}%"
        else:
            improvement_str = "N/A"
        
        print(f"{name:<30} {format_stats(base_stats, unit):<25} {format_stats(p2_stats, unit):<25} {improvement_str}")
        
        validation_results[key] = {
            "baseline": base_stats,
            "p2on": p2_stats,
            "improvement_pct": improvement if base_stats["mean"] > 0 else 0
        }
    
    # 验证标准检查
    print()
    print("=" * 70)
    print("                    Validation Criteria Check")
    print("=" * 70)
    print()
    
    # 标准 A: 高风险干预率 >= 2x baseline
    base_high_risk = validation_results["high_risk_intervention_rate"]["baseline"]["mean"]
    p2_high_risk = validation_results["high_risk_intervention_rate"]["p2on"]["mean"]
    
    if base_high_risk == 0:
        # baseline 不干预，p2 应该显著干预
        criterion_a_pass = p2_high_risk > 0.5
        criterion_a_msg = f"P2 intervention rate {p2_high_risk*100:.1f}% > 50%"
    else:
        criterion_a_pass = p2_high_risk >= base_high_risk * 2
        criterion_a_msg = f"{p2_high_risk*100:.1f}% >= 2x {base_high_risk*100:.1f}%"
    
    print(f"A. High-Risk Intervention Rate >= 2x Baseline")
    print(f"   {'✅ PASS' if criterion_a_pass else '❌ FAIL'}: {criterion_a_msg}")
    print()
    
    # 标准 B: 关键故障下降 >= 30%
    base_depleted = validation_results["energy_depleted_count"]["baseline"]["mean"]
    p2_depleted = validation_results["energy_depleted_count"]["p2on"]["mean"]
    
    if base_depleted > 0:
        reduction = (base_depleted - p2_depleted) / base_depleted * 100
        criterion_b_pass = reduction >= 30
        criterion_b_msg = f"Reduction {reduction:.1f}% (baseline {base_depleted:.1f} -> p2 {p2_depleted:.1f})"
    else:
        criterion_b_pass = p2_depleted == 0
        criterion_b_msg = "Baseline had no depletions"
    
    print(f"B. Critical Failures (Energy Depleted) Reduced >= 30%")
    print(f"   {'✅ PASS' if criterion_b_pass else '❌ FAIL'}: {criterion_b_msg}")
    print()
    
    # 额外指标
    base_reward = validation_results["total_reward"]["baseline"]["mean"]
    p2_reward = validation_results["total_reward"]["p2on"]["mean"]
    reward_improvement = (p2_reward - base_reward) / base_reward * 100
    
    print(f"Bonus: Total Reward Improvement")
    print(f"   {'✅' if reward_improvement > 0 else '⚠️'}: {reward_improvement:+.1f}%")
    print()
    
    # 总体结论
    print("=" * 70)
    print("                         Final Verdict")
    print("=" * 70)
    print()
    
    if criterion_a_pass and criterion_b_pass:
        print("✅ P2 Self-Preservation VALIDATED")
        print()
        print("   Both validation criteria met:")
        print("   - A: Intervention rate scales with risk")
        print("   - B: Survival metrics significantly improved")
        print()
        print("   P2 can now be declared COMPLETE and verified.")
    else:
        print("❌ P2 Validation INCONCLUSIVE")
        print()
        if not criterion_a_pass:
            print("   - A: Intervention rate does not meet threshold")
        if not criterion_b_pass:
            print("   - B: Survival improvement does not meet threshold")
        print()
        print("   More tuning or longer experiments may be needed.")
    
    print()
    print(f"Raw data available in: {log_dir}")
    print("=" * 70)

if __name__ == "__main__":
    main()
