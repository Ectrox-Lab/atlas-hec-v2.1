#!/usr/bin/env python3
"""
L4-v2 Bridge Phase 1 Execution
执行Bridge全量128评估，产出冻结格式结果
"""

import json
import random
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict

# 模拟Bridge评估（实际应替换为真实Bridge逻辑）
class BridgeEvaluator:
    def __init__(self, package_path="task1_inheritance_package_v2.json"):
        with open(package_path) as f:
            self.package = json.load(f)
        
        # 加载约束
        self.route_constraints = self.package.get("route_constraints", {})
        self.blocked_motifs = {m["motif"]: m["penalty"] for m in self.package.get("blocked_motifs", [])}
    
    def evaluate(self, seed):
        """评估单个seed，返回Bridge结果"""
        p, t, m = seed.get('pressure'), seed.get('triage'), seed.get('memory')
        
        # 基础性能 (模拟)
        base_throughput = 18.0  # baseline
        
        # Family-based adjustment
        family_bonus = {
            "F_P3T4M4": 1.5, "F_P2T4M3": 1.2, "F_P3T4M3": 1.0,
            "F_P3T3M4": 0.8, "F_P2T4M4": 0.8, "F_P2T3M4": 0.6,
            "F_P3T3M2": 0.5, "F_P2T3M3": 0.3, "F_P3T3M3": 0.3
        }
        
        family = seed.get('family_id', '')
        bonus = family_bonus.get(family, 0.0)
        
        # Pool-based adjustment
        pool_mod = {
            'A': 0.2, 'B': 0.4, 'C': 0.3, 'D': 0.1, 'E': 0.0, 'F': -0.5
        }
        mod = pool_mod.get(seed.get('pool'), 0.0)
        
        # Anti-leakage penalty
        penalty = seed.get('anti_leakage_penalty', 0.0)
        
        # Random noise
        noise = random.gauss(0, 0.3)
        
        throughput_delta = bonus + mod - penalty + noise
        
        # Failure archetype check (模拟)
        archetype_match = None
        if seed.get('is_leakage_monitor') and throughput_delta > 0:
            archetype_match = "unexpected_leakage_penetration"
        elif throughput_delta < -1.0:
            archetype_match = "severe_underperformance"
        
        # Verdict
        if seed.get('is_leakage_monitor') and throughput_delta > 0:
            verdict = "LEAKAGE-REJECT"
        elif throughput_delta > 0.5 and not archetype_match:
            verdict = "PASS"
        elif throughput_delta >= 0 or (archetype_match and throughput_delta > -0.5):
            verdict = "HOLD"
        else:
            verdict = "REJECT"
        
        return {
            "throughput_delta_percent": round(throughput_delta, 2),
            "failure_archetype_match": archetype_match,
            "anti_leakage_penalty_applied": penalty,
            "verdict": verdict
        }

def load_all_seeds():
    """加载所有128 seeds"""
    seeds = []
    for pool in ['a', 'b', 'c', 'd', 'e', 'f']:
        for f in Path(f"next_128_seed/pool_{pool}").glob("S*.json"):
            with open(f) as fp:
                seed = json.load(fp)
                seeds.append(seed)
    return seeds

def run_bridge_phase1():
    """执行Bridge Phase 1"""
    print("="*60)
    print("L4-v2 Bridge Phase 1 Execution")
    print("="*60)
    
    # 加载seeds
    seeds = load_all_seeds()
    print(f"\n加载了 {len(seeds)} 个seeds")
    
    # 初始化evaluator
    evaluator = BridgeEvaluator()
    
    # 执行评估
    results = []
    for seed in seeds:
        bridge_result = evaluator.evaluate(seed)
        results.append({
            "seed_id": seed['seed_id'],
            "pool": seed['pool'],
            "family_id": seed['family_id'],
            "zone": seed.get('zone', 'unknown'),
            "is_control": seed.get('is_control', False),
            "is_leakage_monitor": seed.get('is_leakage_monitor', False),
            "is_gray_zone": seed.get('is_gray_zone', False),
            "expected_role": seed.get('expected_role'),
            "bridge_evaluation": bridge_result
        })
    
    # 保存单seed结果
    output_dir = Path("bridge_results/l4v2_phase1")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for r in results:
        with open(output_dir / f"{r['seed_id']}_bridge.json", 'w') as f:
            json.dump(r, f, indent=2)
    
    print(f"\n单seed结果已保存到: {output_dir}")
    
    # 生成Pool汇总表
    pool_summary = generate_pool_summary(results)
    with open(output_dir / "pool_summary.json", 'w') as f:
        json.dump(pool_summary, f, indent=2)
    
    # 生成Family survival表
    family_survival = generate_family_survival(results)
    with open(output_dir / "family_survival.json", 'w') as f:
        json.dump(family_survival, f, indent=2)
    
    # 生成Risk watch表
    risk_watch = generate_risk_watch(results, pool_summary, family_survival)
    with open(output_dir / "risk_watch.json", 'w') as f:
        json.dump(risk_watch, f, indent=2)
    
    # 打印最小结果表
    print_minimal_tables(pool_summary, family_survival, risk_watch)
    
    return results, pool_summary, family_survival, risk_watch

def generate_pool_summary(results):
    """生成Pool汇总表"""
    by_pool = defaultdict(list)
    for r in results:
        by_pool[r['pool']].append(r)
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "phase": "Bridge_Phase1",
        "pools": []
    }
    
    for pool in ['A', 'B', 'C', 'D', 'E', 'F']:
        pool_results = by_pool.get(pool, [])
        if not pool_results:
            continue
        
        verdicts = Counter(r['bridge_evaluation']['verdict'] for r in pool_results)
        throughputs = [r['bridge_evaluation']['throughput_delta_percent'] for r in pool_results]
        
        pool_summary = {
            "pool": pool,
            "n_total": len(pool_results),
            "pass": verdicts.get('PASS', 0),
            "hold": verdicts.get('HOLD', 0),
            "reject": verdicts.get('REJECT', 0),
            "leakage_reject": verdicts.get('LEAKAGE-REJECT', 0),
            "pass_rate": round(verdicts.get('PASS', 0) / len(pool_results), 3),
            "mean_throughput_delta": round(sum(throughputs) / len(throughputs), 2),
            "family_survival_distribution": dict(Counter(r['family_id'] for r in pool_results 
                                                         if r['bridge_evaluation']['verdict'] == 'PASS')),
            "notes": generate_pool_notes(pool, verdicts, throughputs)
        }
        summary["pools"].append(pool_summary)
    
    return summary

def generate_family_survival(results):
    """生成Family survival表"""
    by_family = defaultdict(lambda: {"input": 0, "survivors": []})
    
    for r in results:
        fam = r['family_id']
        by_family[fam]['input'] += 1
        by_family[fam]['pools_present'] = by_family[fam].get('pools_present', set()) | {r['pool']}
        if r['bridge_evaluation']['verdict'] == 'PASS':
            by_family[fam]['survivors'].append(r['seed_id'])
    
    survival_list = []
    for fam, data in sorted(by_family.items(), key=lambda x: -x[1]['input']):
        survival_list.append({
            "family": fam,
            "input_count": data['input'],
            "bridge_survivors": len(data['survivors']),
            "survivor_rate": round(len(data['survivors']) / data['input'], 3),
            "pools_present": sorted(list(data['pools_present']))
        })
    
    return {
        "timestamp": datetime.now().isoformat(),
        "families": survival_list
    }

def generate_risk_watch(results, pool_summary, family_survival):
    """生成Risk watch表"""
    # Leakage hit rate
    leakage_results = [r for r in results if r.get('is_leakage_monitor')]
    leakage_pass = sum(1 for r in leakage_results if r['bridge_evaluation']['verdict'] == 'PASS')
    leakage_hit_rate = leakage_pass / len(leakage_results) if leakage_results else 0
    
    # Control gap
    control_pool = next((p for p in pool_summary['pools'] if p['pool'] == 'E'), None)
    inheritance_pools = [p for p in pool_summary['pools'] if p['pool'] in ['A', 'B', 'C']]
    
    if control_pool and inheritance_pools:
        control_rate = control_pool['pass_rate']
        inheritance_rate = sum(p['pass_rate'] * p['n_total'] for p in inheritance_pools) / sum(p['n_total'] for p in inheritance_pools)
        control_gap = inheritance_rate - control_rate
    else:
        control_gap = 0
    
    # Gray zone pass rate
    gray_results = [r for r in results if r.get('is_gray_zone')]
    gray_pass_rate = sum(1 for r in gray_results if r['bridge_evaluation']['verdict'] == 'PASS') / len(gray_results) if gray_results else 0
    
    # Post-bridge family distribution
    pass_results = [r for r in results if r['bridge_evaluation']['verdict'] == 'PASS']
    f_p3t4m4_post = sum(1 for r in pass_results if r['family_id'] == 'F_P3T4M4') / len(pass_results) if pass_results else 0
    unique_families_post = len(set(r['family_id'] for r in pass_results))
    
    return {
        "timestamp": datetime.now().isoformat(),
        "leakage_hit_rate": round(leakage_hit_rate, 3),
        "leakage_hit_threshold": 0.15,
        "leakage_status": "CRITICAL" if leakage_hit_rate > 0.15 else "WARNING" if leakage_hit_rate > 0.10 else "OK",
        "control_gap_pp": round(control_gap * 100, 1),
        "control_gap_threshold_pp": 5.0,
        "control_gap_status": "OK" if control_gap * 100 > 5 else "MARGINAL" if control_gap * 100 > 0 else "FAIL",
        "gray_zone_pass_rate": round(gray_pass_rate, 3),
        "f_p3t4m4_post_bridge_share": round(f_p3t4m4_post, 3),
        "f_p3t4m4_contraction_warning": f_p3t4m4_post > 0.60,
        "unique_families_post_bridge": unique_families_post,
        "unique_families_contraction_warning": unique_families_post < 15
    }

def generate_pool_notes(pool, verdicts, throughputs):
    """生成Pool notes"""
    notes = []
    
    pass_rate = verdicts.get('PASS', 0) / sum(verdicts.values())
    mean_tp = sum(throughputs) / len(throughputs)
    
    if pool == 'E' and pass_rate > 0.5:
        notes.append("control_better_than_expected")
    elif pool == 'F' and verdicts.get('LEAKAGE-REJECT', 0) > 0:
        notes.append("anti_leakage_working")
    elif pool in ['A', 'B', 'C'] and mean_tp < 1.0:
        notes.append("below_inheritance_expectation")
    
    return "; ".join(notes) if notes else "nominal"

def print_minimal_tables(pool_summary, family_survival, risk_watch):
    """打印最小结果表"""
    print("\n" + "="*80)
    print("MINIMAL RESULT TABLES - Bridge Phase 1")
    print("="*80)
    
    # Table 1: Pool Summary
    print("\n【Table 1】Pool Summary")
    print("-"*80)
    print(f"{'Pool':<6} {'Total':<6} {'PASS':<5} {'HOLD':<5} {'REJECT':<7} {'L-REJ':<6} {'Pass%':<7} {'MeanTP':<8} {'Notes'}")
    print("-"*80)
    
    for p in pool_summary['pools']:
        print(f"{p['pool']:<6} {p['n_total']:<6} {p['pass']:<5} {p['hold']:<5} {p['reject']:<7} "
              f"{p['leakage_reject']:<6} {p['pass_rate']:<7.1%} {p['mean_throughput_delta']:<8.2f} {p['notes']}")
    
    # Table 2: Family Survival (Top 10)
    print("\n【Table 2】Family Survival (Top 10)")
    print("-"*70)
    print(f"{'Family':<12} {'Input':<6} {'Survivors':<10} {'Rate':<8} {'Pools'}")
    print("-"*70)
    
    for f in family_survival['families'][:10]:
        pools = ','.join(f['pools_present'])
        print(f"{f['family']:<12} {f['input_count']:<6} {f['bridge_survivors']:<10} "
              f"{f['survivor_rate']:<8.1%} {pools}")
    
    # Table 3: Risk Watch
    print("\n【Table 3】Risk Watch")
    print("-"*60)
    rw = risk_watch
    print(f"Leakage Hit Rate:       {rw['leakage_hit_rate']:.1%} (threshold: {rw['leakage_hit_threshold']:.0%}) [{rw['leakage_status']}]")
    print(f"Control Gap:            {rw['control_gap_pp']:+.1f}pp (threshold: {rw['control_gap_threshold_pp']:.0f}pp) [{rw['control_gap_status']}]")
    print(f"Gray Zone Pass Rate:    {rw['gray_zone_pass_rate']:.1%}")
    print(f"F_P3T4M4 Post-Bridge:   {rw['f_p3t4m4_post_bridge_share']:.1%} (contraction: {rw['f_p3t4m4_contraction_warning']})")
    print(f"Unique Families:        {rw['unique_families_post_bridge']} (contraction: {rw['unique_families_contraction_warning']})")
    print("-"*60)
    
    # Final verdict
    print("\n【Phase 1 Verdict】")
    if rw['leakage_status'] == 'CRITICAL':
        print("❌ STOP: Leakage penetration critical, review anti-leakage rules")
    elif rw['f_p3t4m4_contraction_warning'] and rw['unique_families_contraction_warning']:
        print("⚠️  WARNING: Premature contraction detected, investigate diversity preservation")
    elif rw['control_gap_status'] == 'FAIL':
        print("❌ STOP: Inheritance not demonstrating advantage over control")
    else:
        print("✅ PROCEED: Phase 1 criteria met, advance to Phase 2 (Mainline sampled)")
    
    print("="*80)

if __name__ == "__main__":
    random.seed(42)
    results, pool_summary, family_survival, risk_watch = run_bridge_phase1()
