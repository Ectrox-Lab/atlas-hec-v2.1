#!/usr/bin/env python3
"""
E1 Phase A Analysis: Critical Coupling Detection
Find K_c where r transitions from <0.2 to >0.8
"""

import csv
import numpy as np
from collections import defaultdict

def load_data():
    data = []
    with open('sweep_results.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                'n': int(row['n']),
                'k': float(row['k']),
                'sigma': float(row['sigma']),
                'r_final': float(row['r_final']),
            })
    return data

def find_transition_point(k_values, r_values, threshold_low=0.2, threshold_high=0.8):
    """Find K where r crosses from low to high"""
    # Sort by K
    sorted_pairs = sorted(zip(k_values, r_values))
    k_sorted, r_sorted = zip(*sorted_pairs)
    
    # Find first point where r > threshold_high after being < threshold_low
    for i in range(len(r_sorted) - 1):
        if r_sorted[i] < threshold_low and r_sorted[i+1] > threshold_high:
            return k_sorted[i+1], r_sorted[i+1]
        # Also detect gradual transition
        if r_sorted[i] < threshold_low and r_sorted[i+1] > threshold_low:
            return k_sorted[i+1], r_sorted[i+1]
    
    return None, None

def analyze():
    data = load_data()
    
    # Group by N and sigma
    grouped = defaultdict(list)
    for d in data:
        key = (d['n'], d['sigma'])
        grouped[key].append((d['k'], d['r_final']))
    
    print("=" * 60)
    print("E1 Phase A: Critical Coupling Analysis")
    print("=" * 60)
    print()
    
    print("Transition Detection (r < 0.2 → r > 0.8):")
    print("-" * 60)
    
    transitions_found = 0
    for (n, sigma), points in sorted(grouped.items()):
        k_vals, r_vals = zip(*points)
        k_c, r_c = find_transition_point(k_vals, r_vals)
        
        r_low = min(r_vals)
        r_high = max(r_vals)
        
        if k_c:
            transitions_found += 1
            status = "✓ TRANSITION"
        else:
            status = "✗ No clear transition"
            if r_high < 0.5:
                status = "✗ Always disordered"
            elif r_low > 0.5:
                status = "✗ Always ordered"
        
        print(f"N={n:>6}, σ={sigma:.1f}: K_c ≈ {k_c if k_c else 'N/A':>6.3f}, "
              f"r ∈ [{r_low:.3f}, {r_high:.3f}] {status}")
    
    print()
    print("-" * 60)
    print(f"Transitions detected: {transitions_found}/15 configurations")
    print()
    
    # Overall statistics
    r_values = [d['r_final'] for d in data]
    print("Overall Statistics:")
    print(f"  r_final range: [{min(r_values):.3f}, {max(r_values):.3f}]")
    print(f"  r_final mean: {np.mean(r_values):.3f}")
    print(f"  r_final std: {np.std(r_values):.3f}")
    print()
    
    low_sync = sum(1 for r in r_values if r < 0.2)
    high_sync = sum(1 for r in r_values if r > 0.8)
    mid_sync = len(r_values) - low_sync - high_sync
    
    print("Synchronization Distribution:")
    print(f"  Low sync (r < 0.2): {low_sync} ({100*low_sync/len(r_values):.1f}%)")
    print(f"  Mid sync (0.2-0.8): {mid_sync} ({100*mid_sync/len(r_values):.1f}%)")
    print(f"  High sync (r > 0.8): {high_sync} ({100*high_sync/len(r_values):.1f}%)")
    print()
    
    # Conclusion
    print("=" * 60)
    if high_sync > 50 and low_sync > 50:
        print("✓ CRITICAL TRANSITION DETECTED")
        print("  Both high-sync and low-sync regimes observed.")
        print("  E1 Phase B (refinement) RECOMMENDED.")
    else:
        print("✗ No clear critical transition")
        print("  System may be always ordered or always disordered.")
    print("=" * 60)

if __name__ == "__main__":
    analyze()
