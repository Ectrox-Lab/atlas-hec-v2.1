#!/usr/bin/env python3
"""
P3D-gamma: Measured Native A/B Statistical Analysis

院长要求：
- 成对实验统计
- 均值 ± 标准差
- 效应方向明确
- 可复现

用法：
    python3 scripts/analyze_p3d_gamma.py logs/p3d_gamma/
"""

import json
import sys
import os
import glob
import statistics
from collections import defaultdict

def extract_seed_from_filename(filename):
    """从文件名提取 seed (p3d_gamma 命名格式: {mode}_seed{N}_*.json)"""
    basename = os.path.basename(filename)
    # 尝试匹配 seed 数字
    import re
    match = re.search(r'seed(\d+)', basename)
    if match:
        return int(match.group(1))
    return 0

def load_all_results(directory):
    """加载所有实验结果，按 mode 和 seed 分组"""
    baseline = defaultdict(list)
    p2on = defaultdict(list)
    
    for json_file in glob.glob(os.path.join(directory, "*_result.json")):
        with open(json_file) as f:
            data = json.load(f)
            # 优先使用文件中的 seed，否则从文件名提取
            seed = data.get('seed')
            if seed is None:
                seed = extract_seed_from_filename(json_file)
            
            if data.get('p3_enabled'):
                p2on[seed].append(data)
            else:
                baseline[seed].append(data)
    
    return baseline, p2on

def compute_stats(values):
    """计算均值、标准差、最小、最大"""
    if not values:
        return {"mean": 0, "std": 0, "min": 0, "max": 0, "n": 0}
    
    n = len(values)
    mean = statistics.mean(values)
    std = statistics.stdev(values) if n > 1 else 0.0
    
    return {
        "mean": mean,
        "std": std,
        "min": min(values),
        "max": max(values),
        "n": n
    }

def analyze_paired_results(baseline, p2on):
    """分析成对实验结果"""
    
    # 收集所有指标
    baseline_survival = []
    baseline_food = []
    baseline_intervention = []
    
    p2on_survival = []
    p2on_food = []
    p2on_intervention = []
    p2on_recovery = []
    
    # 按 seed 配对
    all_seeds = set(baseline.keys()) | set(p2on.keys())
    
    for seed in all_seeds:
        # Baseline 数据
        for r in baseline.get(seed, []):
            baseline_survival.append(r.get('avg_survival_steps', 0))
            baseline_food.append(r.get('total_food_eaten', 0))
            baseline_intervention.append(r.get('intervention_rate', 0))
        
        # P2-ON 数据
        for r in p2on.get(seed, []):
            p2on_survival.append(r.get('avg_survival_steps', 0))
            p2on_food.append(r.get('total_food_eaten', 0))
            p2on_intervention.append(r.get('intervention_rate', 0))
            # recovery 比例
            action_dist = r.get('action_distribution', {})
            total_actions = sum(action_dist.values())
            recovery_count = action_dist.get('EnterRecovery', 0)
            p2on_recovery.append(recovery_count / total_actions if total_actions > 0 else 0)
    
    return {
        'baseline': {
            'survival': compute_stats(baseline_survival),
            'food': compute_stats(baseline_food),
            'intervention': compute_stats(baseline_intervention),
        },
        'p2on': {
            'survival': compute_stats(p2on_survival),
            'food': compute_stats(p2on_food),
            'intervention': compute_stats(p2on_intervention),
            'recovery': compute_stats(p2on_recovery),
        }
    }

def compute_effect_size(baseline_mean, p2on_mean, baseline_std):
    """计算效应大小 (Cohen's d)
    
    解释标准 (固定):
    - d < 0.2:   negligible (可忽略)
    - 0.2–0.5:   small (小效应)
    - 0.5–0.8:   medium (中等效应)
    - > 0.8:     large (大效应)
    """
    if baseline_std == 0:
        return 0.0
    return (p2on_mean - baseline_mean) / baseline_std

def interpret_effect_size(d):
    """Cohen's d 解释"""
    abs_d = abs(d)
    if abs_d < 0.2:
        return "negligible"
    elif abs_d < 0.5:
        return "small"
    elif abs_d < 0.8:
        return "medium"
    else:
        return "large"

def print_report(stats):
    """打印统计报告"""
    
    print("=" * 70)
    print("        P3D-gamma: Measured Native A/B Statistical Report")
    print("=" * 70)
    print()
    
    # 配对信息
    baseline_n = stats['baseline']['survival']['n']
    p2on_n = stats['p2on']['survival']['n']
    
    print(f"Sample Size:")
    print(f"  Baseline: {baseline_n} experiments")
    print(f"  P2-ON:    {p2on_n} experiments")
    print()
    
    # Survival Steps
    b_surv = stats['baseline']['survival']
    p_surv = stats['p2on']['survival']
    
    print("-" * 70)
    print("Survival Steps (primary metric)")
    print("-" * 70)
    print(f"  Baseline: {b_surv['mean']:.1f} ± {b_surv['std']:.1f}  [{b_surv['min']:.0f}, {b_surv['max']:.0f}]")
    print(f"  P2-ON:    {p_surv['mean']:.1f} ± {p_surv['std']:.1f}  [{p_surv['min']:.0f}, {p_surv['max']:.0f}]")
    
    diff = p_surv['mean'] - b_surv['mean']
    effect = compute_effect_size(b_surv['mean'], p_surv['mean'], b_surv['std'])
    direction = "↑" if diff > 0 else "↓"
    effect_interp = interpret_effect_size(effect)
    
    print(f"  Diff:     {diff:+.1f} {direction}")
    print(f"  Effect:   d = {effect:.2f} ({effect_interp})")
    print()
    
    # Food Eaten
    b_food = stats['baseline']['food']
    p_food = stats['p2on']['food']
    
    print("-" * 70)
    print("Food Eaten (task performance)")
    print("-" * 70)
    print(f"  Baseline: {b_food['mean']:.1f} ± {b_food['std']:.1f}")
    print(f"  P2-ON:    {p_food['mean']:.1f} ± {p_food['std']:.1f}")
    
    diff_food = p_food['mean'] - b_food['mean']
    direction_food = "↑" if diff_food > 0 else "↓"
    print(f"  Diff:     {diff_food:+.1f} {direction_food}")
    print()
    
    # Intervention Rate
    p_int = stats['p2on']['intervention']
    p_rec = stats['p2on']['recovery']
    
    print("-" * 70)
    print("Preservation Metrics (P2-ON only)")
    print("-" * 70)
    print(f"  Intervention Rate: {p_int['mean']*100:.1f}% ± {p_int['std']*100:.1f}%")
    print(f"  Recovery Ratio:    {p_rec['mean']*100:.1f}% ± {p_rec['std']*100:.1f}%")
    print()
    
    # 判定
    print("=" * 70)
    print("                         VERDICT")
    print("=" * 70)
    
    # 样本量判定
    if p2on_n >= 10 and baseline_n >= 10:
        print("✅ Sample size: Sufficient (≥10 per group)")
        sample_ok = True
    else:
        print(f"⚠️  Sample size: Limited (baseline={baseline_n}, p2on={p2on_n})")
        sample_ok = False
    
    # Effect size 判定
    effect_interp = interpret_effect_size(effect)
    if abs(effect) >= 0.2:
        print(f"✅ Effect detected: d = {effect:.2f} ({effect_interp})")
        effect_ok = True
    else:
        print(f"⚠️  Effect negligible: d = {effect:.2f} ({effect_interp})")
        effect_ok = False
    
    # Intervention 活跃度判定
    if p_int['mean'] > 0.1:
        print(f"✅ Intervention active: {p_int['mean']*100:.1f}%")
        intervention_ok = True
    else:
        print(f"⚠️  Intervention low: {p_int['mean']*100:.1f}%")
        intervention_ok = False
    
    # 关键判定：干预是否产生可测量的行为改变
    # 修正：behavioral_shift_detected = intervention_active AND effect_detected
    # sample_sufficient 仅作为证据强度判定，不作为 shift 的替代条件
    behavioral_shift_detected = intervention_ok and effect_ok
    
    print()
    print("P3D-gamma Key Question:")
    print("  Does intervention produce measurable behavioral shift?")
    
    # 四段式判定逻辑
    if not intervention_ok:
        verdict = "NO_SHIFT: intervention inactive"
        print(f"  ❌ {verdict}")
    elif not effect_ok:
        verdict = "NO_SHIFT: no measurable behavioral shift detected"
        print(f"  ❌ {verdict}")
        print(f"     High intervention ({p_int['mean']*100:.1f}%) but no behavioral change")
        print(f"     This suggests control parameters don't affect policy dynamics")
    elif not sample_ok:
        verdict = "PRELIMINARY_SHIFT: effect detected but sample insufficient"
        print(f"  ⚠️  {verdict}")
        print(f"     d = {effect:.2f} ({effect_interp}) detected, need more data for confidence")
    else:
        verdict = "SUPPORTED_SHIFT: measurable behavioral shift detected"
        print(f"  ✅ {verdict}")
        print(f"     Intervention: {p_int['mean']*100:.1f}% | Effect: d = {effect:.2f} ({effect_interp})")
    
    # 证据强度（独立判定）
    evidence_strength = "adequate" if sample_ok else "preliminary"
    
    print()
    print("P3D-gamma Summary:")
    print(f"  intervention_active:    {intervention_ok} (rate={p_int['mean']*100:.1f}%)")
    print(f"  effect_detected:        {effect_ok} (d={effect:.2f}, |d|≥0.2? {effect_ok})")
    print(f"  sample_sufficient:      {sample_ok} (n={p2on_n})")
    print(f"  evidence_strength:      {evidence_strength}")
    print(f"  behavioral_shift:       {behavioral_shift_detected}")
    print(f"  verdict:                {verdict}")
    
    print()
    print("P3D-gamma Status:")
    if verdict.startswith("SUPPORTED_SHIFT"):
        print("  🎯 COMPLETE: Measured Native A/B validated")
    elif verdict.startswith("PRELIMINARY_SHIFT"):
        print("  ⏳ PENDING: Effect detected but need more data")
    else:
        print("  ❌ NO SHIFT: Intervention not producing behavioral change")
    
    print("=" * 70)

def save_summary(stats, output_dir):
    """保存汇总 JSON"""
    summary = {
        "p3d_gamma_status": "measured_native_ab",
        "baseline": stats['baseline'],
        "p2on": stats['p2on'],
        "comparison": {
            "survival_diff": stats['p2on']['survival']['mean'] - stats['baseline']['survival']['mean'],
            "food_diff": stats['p2on']['food']['mean'] - stats['baseline']['food']['mean'],
            "effect_size_d": compute_effect_size(
                stats['baseline']['survival']['mean'],
                stats['p2on']['survival']['mean'],
                stats['baseline']['survival']['std']
            )
        }
    }
    
    output_path = os.path.join(output_dir, "summary_report.json")
    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"📁 Summary saved: {output_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_p3d_gamma.py <log_directory>")
        sys.exit(1)
    
    log_dir = sys.argv[1]
    
    if not os.path.exists(log_dir):
        print(f"❌ Directory not found: {log_dir}")
        sys.exit(1)
    
    print(f"Loading results from: {log_dir}")
    baseline, p2on = load_all_results(log_dir)
    
    print(f"  Baseline groups: {len(baseline)}")
    print(f"  P2-ON groups:    {len(p2on)}")
    print()
    
    if not baseline and not p2on:
        print("⚠️  No results found")
        sys.exit(1)
    
    stats = analyze_paired_results(baseline, p2on)
    print_report(stats)
    save_summary(stats, log_dir)

if __name__ == "__main__":
    main()
