#!/usr/bin/env python3
"""
Bootstrap Confidence Interval Analysis for L5 Transfer Matrix
Pure Python implementation (no numpy dependency)
"""

import json
import random
import math
from pathlib import Path
from collections import defaultdict

def mean(data):
    return sum(data) / len(data)

def std(data):
    n = len(data)
    if n < 2:
        return 0
    m = mean(data)
    variance = sum((x - m) ** 2 for x in data) / (n - 1)
    return math.sqrt(variance)

def percentile(data, p):
    """Calculate percentile"""
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * p / 100
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_data[int(k)]
    return sorted_data[f] * (c - k) + sorted_data[c] * (k - f)

def bootstrap_ci(data, n_bootstrap=10000, ci=0.95):
    """Calculate bootstrap confidence interval"""
    n = len(data)
    bootstrap_means = []
    
    random.seed(42)
    for _ in range(n_bootstrap):
        sample = [random.choice(data) for _ in range(n)]
        bootstrap_means.append(mean(sample))
    
    alpha = (1 - ci) / 2
    ci_lower = percentile(bootstrap_means, alpha * 100)
    ci_upper = percentile(bootstrap_means, (1 - alpha) * 100)
    
    m = mean(data)
    s = std(data)
    
    return {
        'mean': m,
        'std': s,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'ci_width': ci_upper - ci_lower,
        'se': std(bootstrap_means),
        'cv': s / m if m != 0 else 0
    }

def load_all_batches():
    """Load all batch metrics"""
    base_path = Path('ralph_runs')
    
    batch_configs = [
        ('Code→Math', 'l5_batch1'),
        ('Code→Planning', 'l5_batch2'),
        ('Math→Code', 'l5_batch3_b2a'),
        ('Code→Planning', 'l5_batch4_code2planning'),
        ('Planning→Code', 'l5_batch5_planning2code'),
        ('Math→Planning', 'l5_batch6_math2planning'),
        ('Planning→Math', 'l5_batch7_planning2math'),
    ]
    
    results = {}
    for pair_name, batch_dir in batch_configs:
        path = base_path / batch_dir
        tg_values = []
        
        for window_file in sorted(path.glob('window_*/metrics.json')):
            with open(window_file) as f:
                data = json.load(f)
                tg_values.append(data.get('transfer_gap_pp', 0))
        
        for hour_file in sorted(path.glob('hour_*/metrics.json')):
            with open(hour_file) as f:
                data = json.load(f)
                tg_values.append(data.get('transfer_gap_pp', 0))
        
        if tg_values:
            if pair_name not in results or len(tg_values) > len(results[pair_name]['values']):
                results[pair_name] = {
                    'values': tg_values,
                    'n': len(tg_values)
                }
    
    return results

def main():
    print("=" * 70)
    print("L5 BOOTSTRAP CONFIDENCE INTERVAL ANALYSIS")
    print("=" * 70)
    print()
    
    # Load data
    results = load_all_batches()
    
    print(f"Loaded {len(results)} unique task pairs")
    print("-" * 70)
    
    pair_stats = {}
    for pair_name in sorted(results.keys()):
        data = results[pair_name]
        values = data['values']
        
        stats = bootstrap_ci(values)
        pair_stats[pair_name] = stats
        
        print(f"\n{pair_name}:")
        print(f"  n = {data['n']}")
        print(f"  Mean = {stats['mean']:.2f}pp")
        print(f"  SD = {stats['std']:.2f}pp")
        print(f"  CV = {stats['cv']:.3f}")
        print(f"  95% CI = [{stats['ci_lower']:.2f}, {stats['ci_upper']:.2f}]")
        print(f"  CI Width = {stats['ci_width']:.2f}pp")
    
    # Source suitability with CI
    print("\n" + "=" * 70)
    print("SOURCE SUITABILITY (with 95% CI)")
    print("=" * 70)
    
    source_effects = defaultdict(list)
    for pair_name, data in results.items():
        source = pair_name.split('→')[0]
        source_effects[source].extend(data['values'])
    
    source_stats = {}
    for source in ['Code', 'Math', 'Planning']:
        if source in source_effects:
            values = source_effects[source]
            stats = bootstrap_ci(values)
            source_stats[source] = stats
            
            print(f"\n{source} as Source:")
            print(f"  n_windows = {len(values)}")
            print(f"  Mean = {stats['mean']:.2f}pp")
            print(f"  95% CI = [{stats['ci_lower']:.2f}, {stats['ci_upper']:.2f}]")
            print(f"  CV = {stats['cv']:.3f}")
    
    # Save results
    output = {
        'pair_statistics': {k: {kk: float(vv) for kk, vv in v.items()} for k, v in pair_stats.items()},
        'source_suitability': {k: {kk: float(vv) for kk, vv in v.items()} for k, v in source_stats.items()},
        'method': 'bootstrap',
        'n_bootstrap': 10000,
        'confidence_level': 0.95
    }
    
    output_path = Path('bootstrap_analysis.json')
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n\n{'=' * 70}")
    print(f"Saved to: {output_path}")
    print("=" * 70)

if __name__ == "__main__":
    main()
