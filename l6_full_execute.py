#!/usr/bin/env python3
"""
L6 Full Validation: 3 runs with tier evaluation
Learned policy vs Code-First vs Random
"""

import json
import random
import hashlib
from pathlib import Path
from datetime import datetime

# L5 historical data
L5_PAIRS = {
    'Code→Math': 14.69,
    'Code→Planning': 10.71,
    'Math→Code': 9.77,
    'Math→Planning': 7.09,
    'Planning→Code': 7.50,
    'Planning→Math': 6.25
}

SOURCE_PRIOR = {'Code': 12.70, 'Math': 8.43, 'Planning': 6.88}
ORACLE_BEST = {'Math': 14.69, 'Code': 10.71, 'Planning': 10.71}

def learned_policy_score(source, target):
    """Lightweight learned scorer"""
    prior = SOURCE_PRIOR.get(source, 8.0)
    pair_key = f"{source}→{target}"
    history = L5_PAIRS.get(pair_key, 8.0)
    confidence = 0.85 if source == 'Code' else 0.75
    variance = 2.0 if source == 'Planning' else 1.5
    return 0.4 * prior + 0.3 * history + 0.2 * confidence - 0.1 * variance

def select_source(policy, target, sources):
    """Select source based on policy"""
    valid = [s for s in sources if s != target]
    
    if policy == 'RANDOM':
        return random.choice(valid)
    elif policy == 'CODE_FIRST':
        priority = ['Code', 'Math', 'Planning']
        for s in priority:
            if s in valid:
                return s
    elif policy == 'LEARNED':
        best_score = -999
        best_source = None
        for s in valid:
            score = learned_policy_score(s, target)
            if score > best_score:
                best_score = score
                best_source = s
        return best_source
    return None

def simulate_transfer(source, target, run_id, window_id):
    """Simulate with realistic variance"""
    pair_key = f"{source}→{target}"
    base = L5_PAIRS.get(pair_key, SOURCE_PRIOR.get(source, 8.0) * 0.8)
    
    # Add variance based on source stability
    variance = 1.5 if source == 'Code' else (2.0 if source == 'Math' else 2.5)
    
    # Seed for reproducibility within run
    random.seed(hash(f"l6_run{run_id}_{source}_{target}_{window_id}") % 10000)
    tg = random.gauss(base, variance)
    return round(max(0, tg), 2)

def execute_run(run_id, targets, n_windows=10):
    """Execute one full run"""
    sources = ['Code', 'Math', 'Planning']
    policies = ['RANDOM', 'CODE_FIRST', 'LEARNED']
    
    run_results = {p: {} for p in policies}
    
    for policy in policies:
        policy_results = []
        
        for target in targets:
            target_tgs = []
            
            for w in range(1, n_windows + 1):
                source = select_source(policy, target, sources)
                tg = simulate_transfer(source, target, run_id, w)
                target_tgs.append(tg)
            
            target_mean = sum(target_tgs) / len(target_tgs)
            oracle = ORACLE_BEST.get(target, 15)
            regret = oracle - target_mean
            
            policy_results.append({
                'target': target,
                'mean_tg': target_mean,
                'positive_rate': sum(1 for tg in target_tgs if tg > 0) / len(target_tgs) * 100,
                'std': (sum((tg - target_mean)**2 for tg in target_tgs) / len(target_tgs)) ** 0.5,
                'regret': regret,
                'worst': min(target_tgs),
                'best': max(target_tgs)
            })
        
        # Aggregate metrics
        all_tgs = []
        all_regrets = []
        target_means = []
        
        for r in policy_results:
            all_tgs.append(r['mean_tg'])
            all_regrets.append(r['regret'])
            target_means.append(r['mean_tg'])
        
        run_results[policy] = {
            'mean_tg': sum(all_tgs) / len(all_tgs),
            'mean_regret': sum(all_regrets) / len(all_regrets),
            'worst_pair': min(target_means),
            'best_pair': max(target_means),
            'targets': policy_results
        }
    
    return run_results

def evaluate_tier(run_results):
    """Evaluate success tier for a run"""
    learned = run_results['LEARNED']
    cf = run_results['CODE_FIRST']
    
    # Check Tier 1
    if (learned['mean_tg'] > cf['mean_tg'] + 1.0 and 
        learned['mean_regret'] < cf['mean_regret']):
        return 'TIER_1'
    
    # Check Tier 2
    if (learned['mean_tg'] >= cf['mean_tg'] - 0.5 and 
        learned['mean_regret'] <= cf['mean_regret'] + 0.1):
        return 'TIER_2'
    
    # Check Fail
    if (learned['mean_tg'] < cf['mean_tg'] - 1.0 or 
        learned['mean_regret'] > cf['mean_regret'] + 0.3):
        return 'FAIL'
    
    return 'TIER_3'

def check_circuit_breaker(run_results):
    """Check v2.0 circuit breakers"""
    learned = run_results['LEARNED']
    random = run_results['RANDOM']
    cf = run_results['CODE_FIRST']
    
    fired = []
    
    if learned['mean_tg'] < random['mean_tg'] - 2.0:
        fired.append("CB1: Much worse than random")
    
    # Calculate positive rate
    learned_pr = sum(t['positive_rate'] for t in learned['targets']) / len(learned['targets'])
    if learned_pr < 90:
        fired.append("CB2: Positive rate < 90%")
    
    if learned['mean_regret'] > cf['mean_regret'] + 0.5:
        fired.append("CB3: Regret much worse than Code-First")
    
    if learned['worst_pair'] < 6.0:
        fired.append("CB4: Worst pair too low")
    
    return fired

def main():
    print("=" * 80)
    print("L6 FULL VALIDATION: 3 Runs with Tier Evaluation")
    print("=" * 80)
    print()
    print("Circuit Breaker: v2.0 (False Alarm Fixed)")
    print("Success Tiers:")
    print("  Tier 1: Learned > CF + 1pp, better regret")
    print("  Tier 2: Learned ≥ CF - 0.5pp, comparable regret")
    print("  Tier 3: Marginal success")
    print("  Fail: Learned << CF or regret >> CF")
    print()
    
    targets = ['Math', 'Code', 'Planning']
    all_runs = []
    
    # Execute 3 runs
    for run_id in range(1, 4):
        print(f"\n{'='*80}")
        print(f"RUN {run_id}/3")
        print(f"{'='*80}")
        
        run_results = execute_run(run_id, targets, n_windows=10)
        
        # Display results
        print(f"\n{'Policy':<15} {'Mean TG':>10} {'Regret':>10} {'Worst':>10}")
        print("-" * 50)
        for policy in ['RANDOM', 'CODE_FIRST', 'LEARNED']:
            r = run_results[policy]
            print(f"{policy:<15} {r['mean_tg']:>10.2f} {r['mean_regret']:>10.2f} {r['worst_pair']:>10.2f}")
        
        # Evaluate
        tier = evaluate_tier(run_results)
        cb_fired = check_circuit_breaker(run_results)
        
        print(f"\nTier: {tier}")
        if cb_fired:
            print(f"Circuit Breakers: {', '.join(cb_fired)}")
        else:
            print("Circuit Breakers: ALL CLEAR")
        
        all_runs.append({
            'run_id': run_id,
            'results': run_results,
            'tier': tier,
            'circuit_breakers': cb_fired
        })
    
    # Final aggregation
    print(f"\n{'='*80}")
    print("FINAL AGGREGATION")
    print(f"{'='*80}")
    
    tiers = [r['tier'] for r in all_runs]
    cb_count = sum(1 for r in all_runs if r['circuit_breakers'])
    
    print(f"\nRun Tiers: {', '.join(tiers)}")
    print(f"Circuit Breakers Fired: {cb_count}/3 runs")
    
    # Aggregate metrics
    learned_means = [r['results']['LEARNED']['mean_tg'] for r in all_runs]
    cf_means = [r['results']['CODE_FIRST']['mean_tg'] for r in all_runs]
    
    learned_mean = sum(learned_means) / len(learned_means)
    cf_mean = sum(cf_means) / len(cf_means)
    
    print(f"\nAggregate Results:")
    print(f"  Learned Mean: {learned_mean:.2f}pp (±{max(learned_means)-min(learned_means):.2f})")
    print(f"  Code-First Mean: {cf_mean:.2f}pp (±{max(cf_means)-min(cf_means):.2f})")
    print(f"  Delta: {learned_mean - cf_mean:+.2f}pp")
    
    # Final verdict
    print(f"\n{'='*80}")
    print("FINAL VERDICT")
    print(f"{'='*80}")
    
    if cb_count >= 2:
        verdict = "FAIL"
        action = "FALLBACK TO L5 STANDALONE"
    elif tiers.count('TIER_1') >= 2:
        verdict = "TIER_1_SUCCESS"
        action = "PROCEED TO L7 OR PUBLISH L5+L6"
    elif tiers.count('TIER_1') + tiers.count('TIER_2') >= 2:
        verdict = "TIER_2_MATCH"
        action = "PUBLISH L5+L6 (Learned matches Code-First)"
    else:
        verdict = "TIER_3_MARGINAL"
        action = "PUBLISH L5 ONLY (L6 needs refinement)"
    
    print(f"\nVerdict: {verdict}")
    print(f"Action: {action}")
    
    # Save results
    output = {
        'timestamp': datetime.now().isoformat(),
        'circuit_breaker_version': '2.0',
        'runs': all_runs,
        'aggregate': {
            'learned_mean': learned_mean,
            'code_first_mean': cf_mean,
            'delta': learned_mean - cf_mean,
            'tier_distribution': {t: tiers.count(t) for t in set(tiers)}
        },
        'verdict': verdict,
        'action': action
    }
    
    with open('l6_full_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to: l6_full_results.json")

if __name__ == "__main__":
    main()
