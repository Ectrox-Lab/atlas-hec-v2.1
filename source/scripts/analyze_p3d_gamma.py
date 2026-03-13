#!/usr/bin/env python3
"""
P3D-gamma: Paired Native A/B Statistical Analysis

院长修正要求：
1. 严格 paired analysis (seed 交集，pair-wise delta)
2. 标准 Cohen's d (pooled SD)
3. 分层 sample size 判定
4. JSON 保存 verdict 等关键字段
5. 明确方向性和控制语义

用法：
    python3 scripts/analyze_p3d_gamma.py logs/p3d/
"""

import json
import sys
import os
import glob
import statistics
import math
import time
from datetime import datetime, timezone
from collections import defaultdict

def extract_seed_from_filename(filename):
    """从文件名提取 seed"""
    basename = os.path.basename(filename)
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
            seed = data.get('seed')
            if seed is None:
                seed = extract_seed_from_filename(json_file)
            
            if data.get('p3_enabled'):
                p2on[seed].append(data)
            else:
                baseline[seed].append(data)
    
    return baseline, p2on

def compute_paired_deltas(baseline, p2on):
    """
    严格 paired analysis:
    只对交集 seed 计算 pair-wise delta
    """
    # 只使用交集 seed（严格配对）
    paired_seeds = sorted(set(baseline.keys()) & set(p2on.keys()))
    
    if not paired_seeds:
        return [], [], []  # 修正：返回3个值，与正常路径一致
    
    survival_deltas = []
    food_deltas = []
    
    for seed in paired_seeds:
        # 对每个 seed，取该 seed 下所有 episodes 的均值
        b_survival = [r.get('avg_survival_steps', 0) for r in baseline[seed]]
        p_survival = [r.get('avg_survival_steps', 0) for r in p2on[seed]]
        
        b_food = [r.get('total_food_eaten', 0) for r in baseline[seed]]
        p_food = [r.get('total_food_eaten', 0) for r in p2on[seed]]
        
        # 计算该 seed 的均值
        b_surv_mean = statistics.mean(b_survival) if b_survival else 0
        p_surv_mean = statistics.mean(p_survival) if p_survival else 0
        
        b_food_mean = statistics.mean(b_food) if b_food else 0
        p_food_mean = statistics.mean(p_food) if p_food else 0
        
        # pair-wise delta
        survival_deltas.append(p_surv_mean - b_surv_mean)
        food_deltas.append(p_food_mean - b_food_mean)
    
    return survival_deltas, food_deltas, paired_seeds

def compute_cohens_d_pooled(mean1, std1, n1, mean2, std2, n2):
    """
    标准 Cohen's d (pooled SD 版本)
    
    d = (mean2 - mean1) / pooled_std
    pooled_std = sqrt(((n1-1)*s1^2 + (n2-1)*s2^2) / (n1+n2-2))
    """
    if n1 < 2 or n2 < 2:
        return 0.0
    
    # Pooled variance
    pooled_var = (((n1 - 1) * std1**2) + ((n2 - 1) * std2**2)) / (n1 + n2 - 2)
    pooled_std = math.sqrt(pooled_var)
    
    if pooled_std == 0:
        return 0.0
    
    return (mean2 - mean1) / pooled_std

def compute_paired_cohens_d(deltas):
    """
    Paired design 的 Cohen's d
    d = mean(delta) / std(delta)
    """
    if len(deltas) < 2:
        return 0.0
    
    mean_delta = statistics.mean(deltas)
    std_delta = statistics.stdev(deltas)
    
    if std_delta == 0:
        return 0.0
    
    return mean_delta / std_delta

def interpret_effect_size(d):
    """Cohen's d 解释 (固定标准)"""
    abs_d = abs(d)
    if abs_d < 0.2:
        return "negligible"
    elif abs_d < 0.5:
        return "small"
    elif abs_d < 0.8:
        return "medium"
    else:
        return "large"

def determine_sample_level(n_paired_seeds, n_total_episodes):
    """
    分层 sample size 判定
    
    层级:
    - adequate: 足够支撑 SUPPORTED_SHIFT
    - preliminary: 可以检测效应，但证据较弱  
    - limited: 样本不足，结论不可靠
    """
    if n_paired_seeds >= 10 and n_total_episodes >= 500:
        return "adequate"
    elif n_paired_seeds >= 5 and n_total_episodes >= 100:
        return "preliminary"
    else:
        return "limited"

def analyze_paired_results(baseline, p2on):
    """分析配对实验结果"""
    
    # 1. 严格 paired analysis
    survival_deltas, food_deltas, paired_seeds = compute_paired_deltas(baseline, p2on)
    n_paired = len(paired_seeds)
    
    if n_paired == 0:
        return None, "NO_PAIRED_DATA: no matching seeds found"
    
    # 2. 基础统计（严格 paired：只使用 paired_seeds）
    # 修正：与 survival_deltas 保持一致的样本基底
    baseline_survival = []
    baseline_food = []
    for seed in paired_seeds:  # 修正：只用 paired seeds
        for r in baseline[seed]:
            baseline_survival.append(r.get('avg_survival_steps', 0))
            baseline_food.append(r.get('total_food_eaten', 0))
    
    # P2-ON 组（严格 paired：只使用 paired_seeds）
    p2on_survival = []
    p2on_food = []
    p2on_intervention = []
    p2on_recovery = []
    
    for seed in paired_seeds:  # 修正：只用 paired seeds
        for r in p2on[seed]:
            p2on_survival.append(r.get('avg_survival_steps', 0))
            p2on_food.append(r.get('total_food_eaten', 0))
            p2on_intervention.append(r.get('intervention_rate', 0))
            
            # recovery 比例
            action_dist = r.get('action_distribution', {})
            total_actions = sum(action_dist.values())
            recovery_count = action_dist.get('EnterRecovery', 0)
            p2on_recovery.append(recovery_count / total_actions if total_actions > 0 else 0)
    
    # 3. 计算统计量
    b_surv_stats = {
        'mean': statistics.mean(baseline_survival) if baseline_survival else 0,
        'std': statistics.stdev(baseline_survival) if len(baseline_survival) > 1 else 0,
        'n': len(baseline_survival),
    }
    
    p_surv_stats = {
        'mean': statistics.mean(p2on_survival) if p2on_survival else 0,
        'std': statistics.stdev(p2on_survival) if len(p2on_survival) > 1 else 0,
        'n': len(p2on_survival),
    }
    
    # 4. Cohen's d (pooled 标准版本)
    cohens_d = compute_cohens_d_pooled(
        b_surv_stats['mean'], b_surv_stats['std'], b_surv_stats['n'],
        p_surv_stats['mean'], p_surv_stats['std'], p_surv_stats['n']
    )
    
    # Paired delta 统计
    delta_stats = {
        'mean': statistics.mean(survival_deltas),
        'std': statistics.stdev(survival_deltas) if len(survival_deltas) > 1 else 0,
        'min': min(survival_deltas),
        'max': max(survival_deltas),
    }
    
    # Paired Cohen's d
    paired_d = compute_paired_cohens_d(survival_deltas)
    
    # 5. Intervention 统计
    intervention_stats = {
        'mean': statistics.mean(p2on_intervention) if p2on_intervention else 0,
        'std': statistics.stdev(p2on_intervention) if len(p2on_intervention) > 1 else 0,
    }
    
    recovery_stats = {
        'mean': statistics.mean(p2on_recovery) if p2on_recovery else 0,
    }
    
    return {
        'n_paired_seeds': n_paired,
        'paired_seeds': paired_seeds,
        'baseline': b_surv_stats,
        'p2on': p_surv_stats,
        'delta': delta_stats,
        'cohens_d_pooled': cohens_d,
        'cohens_d_paired': paired_d,
        'intervention': intervention_stats,
        'recovery': recovery_stats,
        'total_episodes_baseline': len(baseline_survival),
        'total_episodes_p2on': len(p2on_survival),
    }, None

def print_report(stats, error=None):
    """打印统计报告"""
    
    print("=" * 70)
    print("     P3D-gamma: Paired Native A/B Statistical Report")
    print("=" * 70)
    print()
    
    if error:
        print(f"❌ ERROR: {error}")
        print("=" * 70)
        return None
    
    # 配对信息
    print(f"Paired Analysis:")
    print(f"  Paired seeds: {stats['n_paired_seeds']}")
    print(f"  Seeds: {stats['paired_seeds']}")
    print(f"  Total episodes (baseline): {stats['total_episodes_baseline']}")
    print(f"  Total episodes (P2-ON): {stats['total_episodes_p2on']}")
    print()
    
    # Survival Steps
    b = stats['baseline']
    p = stats['p2on']
    d = stats['delta']
    
    print("-" * 70)
    print("Survival Steps (paired analysis)")
    print("-" * 70)
    print(f"  Baseline:     {b['mean']:.1f} ± {b['std']:.1f}  [n={b['n']}]")
    print(f"  P2-ON:        {p['mean']:.1f} ± {p['std']:.1f}  [n={p['n']}]")
    print(f"  Paired Delta: {d['mean']:+.1f} ± {d['std']:.1f}  [range: {d['min']:.1f}, {d['max']:.1f}]")
    
    # Effect size
    cohens_d = stats['cohens_d_pooled']
    paired_d = stats['cohens_d_paired']
    effect_interp = interpret_effect_size(cohens_d)
    
    print(f"  Cohen's d (pooled):  {cohens_d:.2f} ({effect_interp})")
    print(f"  Cohen's d (paired):  {paired_d:.2f}")
    print()
    
    # Intervention
    i = stats['intervention']
    r = stats['recovery']
    
    print("-" * 70)
    print("Preservation Metrics (P2-ON)")
    print("-" * 70)
    print(f"  Intervention rate:  {i['mean']*100:.1f}% ± {i['std']*100:.1f}%")
    print(f"  Recovery ratio:     {r['mean']*100:.1f}%")
    print()
    
    # 判定逻辑
    intervention_active = i['mean'] > 0.10
    # 修正：严格 paired design 应使用 paired_d，或双重防线
    # 方案 B（保守）：pooled 和 paired 都需达标
    pooled_significant = abs(cohens_d) >= 0.20
    paired_significant = abs(paired_d) >= 0.20
    effect_detected = pooled_significant and paired_significant  # 双重防线
    
    # 修正：样本量使用两组中的较小值，确保平衡
    n_total_episodes = min(stats['total_episodes_baseline'], stats['total_episodes_p2on'])
    sample_level = determine_sample_level(stats['n_paired_seeds'], n_total_episodes)
    sample_sufficient = sample_level == "adequate"
    
    # 关键判定
    behavioral_shift_detected = intervention_active and effect_detected
    
    print("=" * 70)
    print("                         VERDICT")
    print("=" * 70)
    
    # 四段式判定
    if not intervention_active:
        verdict = "NO_SHIFT: intervention inactive"
        print(f"  ❌ {verdict}")
    elif not effect_detected:
        verdict = "NO_SHIFT: no measurable behavioral shift detected"
        print(f"  ❌ {verdict}")
        print(f"     Intervention: {i['mean']*100:.1f}% but Cohen's d = {cohens_d:.2f} (negligible)")
        print(f"     → control parameters may not affect policy dynamics")
    elif sample_level == "limited":
        verdict = "INSUFFICIENT_DATA: effect suggested but sample too small"
        print(f"  ⚠️  {verdict}")
    elif sample_level == "preliminary":
        verdict = "PRELIMINARY_SHIFT: effect detected but need more data"
        print(f"  ⚠️  {verdict}")
        print(f"     d = {cohens_d:.2f} ({effect_interp}), n_seeds = {stats['n_paired_seeds']}")
    else:
        verdict = "SUPPORTED_SHIFT: measurable behavioral shift detected"
        print(f"  ✅ {verdict}")
        print(f"     d = {cohens_d:.2f} ({effect_interp}), n_seeds = {stats['n_paired_seeds']}")
    
    # 证据强度
    evidence_strength = "adequate" if sample_sufficient else "preliminary" if sample_level == "preliminary" else "limited"
    
    print()
    print("Summary:")
    print(f"  intervention_active:      {intervention_active} (rate={i['mean']*100:.1f}%)")
    print(f"  pooled_d_significant:     {pooled_significant} (|d|={abs(cohens_d):.2f})")
    print(f"  paired_d_significant:     {paired_significant} (|d|={abs(paired_d):.2f})")
    print(f"  effect_detected:          {effect_detected} (both significant? {effect_detected})")
    print(f"  sample_level:             {sample_level} (n_seeds={stats['n_paired_seeds']}, n_ep={n_total_episodes})")
    print(f"  evidence_strength:        {evidence_strength}")
    print(f"  behavioral_shift:         {behavioral_shift_detected}")
    print(f"  verdict:                  {verdict}")
    
    print()
    print("P3D-gamma Status:")
    if verdict.startswith("SUPPORTED_SHIFT"):
        print("  🎯 COMPLETE: Measured Native A/B validated")
    elif verdict.startswith("PRELIMINARY_SHIFT"):
        print("  ⏳ PENDING: Effect detected, run full experiment (10+ seeds, 500+ episodes)")
    elif verdict.startswith("NO_SHIFT"):
        print("  ❌ NO SHIFT: Intervention not producing measurable behavioral change")
        print("      → Check: homeostasis thresholds, control parameter mapping, task difficulty")
    else:
        print("  ⏳ NEED MORE DATA")
    
    print("=" * 70)
    
    # 返回判定结果用于 JSON
    return {
        'verdict': verdict,
        'behavioral_shift_detected': behavioral_shift_detected,
        'intervention_active': intervention_active,
        'effect_detected': effect_detected,
        'pooled_significant': pooled_significant,
        'paired_significant': paired_significant,
        'cohens_d': cohens_d,
        'paired_d': paired_d,
        'effect_size_interpretation': effect_interp,
        'sample_level': sample_level,
        'evidence_strength': evidence_strength,
        'n_paired_seeds': stats['n_paired_seeds'],
        'total_episodes': n_total_episodes,
    }

def save_summary(stats, verdict_info, output_dir):
    """保存汇总 JSON（包含所有关键判定字段）"""
    if verdict_info is None:
        return
    
    summary = {
        "p3d_gamma_status": "measured_native_ab",
        "analysis_timestamp": datetime.now(timezone.utc).isoformat(),  # 修正：真实分析时间
        "paired_analysis": {
            "n_paired_seeds": stats['n_paired_seeds'],
            "paired_seeds": stats['paired_seeds'],
            "total_episodes_baseline": stats['total_episodes_baseline'],
            "total_episodes_p2on": stats['total_episodes_p2on'],
        },
        "baseline": {
            "survival_mean": stats['baseline']['mean'],
            "survival_std": stats['baseline']['std'],
            "n": stats['baseline']['n'],
        },
        "p2on": {
            "survival_mean": stats['p2on']['mean'],
            "survival_std": stats['p2on']['std'],
            "n": stats['p2on']['n'],
            "intervention_rate_mean": stats['intervention']['mean'],
            "intervention_rate_std": stats['intervention']['std'],
        },
        "paired_delta": {
            "mean": stats['delta']['mean'],
            "std": stats['delta']['std'],
            "min": stats['delta']['min'],
            "max": stats['delta']['max'],
        },
        "effect_size": {
            "cohens_d_pooled": stats['cohens_d_pooled'],
            "cohens_d_paired": stats['cohens_d_paired'],
            "pooled_significant": verdict_info.get('pooled_significant', False),
            "paired_significant": verdict_info.get('paired_significant', False),
            "interpretation": verdict_info['effect_size_interpretation'],
        },
        # 关键判定字段
        "verdict": verdict_info['verdict'],
        "behavioral_shift_detected": verdict_info['behavioral_shift_detected'],
        "intervention_active": verdict_info['intervention_active'],
        "effect_detected": verdict_info['effect_detected'],
        "pooled_significant": verdict_info.get('pooled_significant', False),
        "paired_significant": verdict_info.get('paired_significant', False),
        "sample_level": verdict_info['sample_level'],
        "evidence_strength": verdict_info['evidence_strength'],
    }
    
    output_path = os.path.join(output_dir, "summary_report.json")
    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"📁 Summary saved: {output_path}")
    return output_path

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
    
    print(f"  Baseline groups: {len(baseline)} seeds")
    print(f"  P2-ON groups:    {len(p2on)} seeds")
    
    # 检查配对
    paired_seeds = set(baseline.keys()) & set(p2on.keys())
    print(f"  Paired seeds:    {len(paired_seeds)}")
    print()
    
    if not baseline and not p2on:
        print("⚠️  No results found")
        sys.exit(1)
    
    # 分析
    stats, error = analyze_paired_results(baseline, p2on)
    
    # 打印报告并获取判定信息
    verdict_info = print_report(stats, error)
    
    # 保存汇总
    if stats:
        save_summary(stats, verdict_info, log_dir)

if __name__ == "__main__":
    main()
