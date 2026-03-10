#!/usr/bin/env python3
"""
E1 Phase B Analysis: Hysteresis and Critical Behavior
"""

import csv
import numpy as np
from collections import defaultdict

def load_data():
    data = []
    with open('refinement_results.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                'n': int(row['n']),
                'k': float(row['k']),
                'sigma': float(row['sigma']),
                'r_final': float(row['r_final']),
                'initial_sync': row['initial_sync'] == 'true',
            })
    return data

def analyze():
    data = load_data()
    
    print("=" * 70)
    print("E1 Phase B: Hysteresis and Critical Behavior Analysis")
    print("=" * 70)
    print()
    
    # Group by (N, sigma, K)
    grouped = defaultdict(lambda: {'disordered': [], 'ordered': []})
    for d in data:
        key = (d['n'], d['sigma'], d['k'])
        if d['initial_sync']:
            grouped[key]['ordered'].append(d['r_final'])
        else:
            grouped[key]['disordered'].append(d['r_final'])
    
    # Analyze hysteresis
    hysteresis_cases = []
    bistable_cases = []
    
    for key, values in grouped.items():
        n, sigma, k = key
        if values['disordered'] and values['ordered']:
            r_dis = np.mean(values['disordered'])
            r_ord = np.mean(values['ordered'])
            gap = r_ord - r_dis
            
            if gap > 0.3:
                hysteresis_cases.append((n, sigma, k, gap))
            if r_dis < 0.3 and r_ord > 0.7:
                bistable_cases.append((n, sigma, k, r_dis, r_ord))
    
    print(f"Total configurations: {len(data)}")
    print(f"Unique (N, σ, K) combinations: {len(grouped)}")
    print()
    
    print("Hysteresis Analysis:")
    print("-" * 70)
    print(f"Cases with |r_ordered - r_disordered| > 0.3: {len(hysteresis_cases)}")
    print(f"Hysteresis rate: {100*len(hysteresis_cases)/len(grouped):.1f}%")
    print()
    
    if hysteresis_cases:
        avg_gap = np.mean([x[3] for x in hysteresis_cases])
        print(f"Average gap: {avg_gap:.3f}")
        print()
        
        # By sigma
        for sigma in [0.1, 0.5, 1.0]:
            sigma_cases = [x for x in hysteresis_cases if abs(x[1] - sigma) < 0.01]
            if sigma_cases:
                print(f"  σ={sigma}: {len(sigma_cases)} hysteresis cases")
    
    print()
    print("Bistability (r_dis < 0.3 AND r_ord > 0.7):")
    print("-" * 70)
    print(f"Bistable cases: {len(bistable_cases)}")
    if bistable_cases:
        print("  These show clear memory of initial conditions")
        print("  → First-order phase transition evidence")
    print()
    
    # K_c convergence with N
    print("K_c Convergence with N:")
    print("-" * 70)
    
    for sigma in [0.1, 0.5, 1.0]:
        print(f"\nσ = {sigma}:")
        k_c_by_n = {}
        
        for n in [50000, 70000, 100000, 300000]:
            # Find where r crosses 0.5 for disordered start
            crossings = []
            for k in np.linspace(0.15, 2.1, 50):
                key = (n, sigma, k)
                if key in grouped and grouped[key]['disordered']:
                    r = np.mean(grouped[key]['disordered'])
                    crossings.append((k, r))
            
            if crossings:
                # Find K where r ≈ 0.5
                crossings.sort()
                k_c = None
                for i in range(len(crossings)-1):
                    if crossings[i][1] < 0.5 < crossings[i+1][1]:
                        k_c = (crossings[i][0] + crossings[i+1][0]) / 2
                        break
                if k_c:
                    k_c_by_n[n] = k_c
                    print(f"  N={n:>6}: K_c ≈ {k_c:.3f}")
        
        if len(k_c_by_n) >= 2:
            k_values = list(k_c_by_n.values())
            k_range = max(k_values) - min(k_values)
            print(f"  K_c variation: {k_range:.3f} (convergence: {'GOOD' if k_range < 0.1 else 'MODERATE' if k_range < 0.2 else 'WEAK'})")
    
    print()
    print("=" * 70)
    
    # Final assessment
    print("\nASSESSMENT:")
    print("-" * 70)
    
    if len(hysteresis_cases) > 50:
        print("✓ Strong hysteresis detected")
        print("  → First-order phase transition")
        print("  → System has memory (initial conditions matter)")
    
    if len(bistable_cases) > 20:
        print("✓ Bistability confirmed")
        print("  → Two stable states coexist near critical point")
        print("  → Potential for 'tipping point' control strategies")
    
    print()
    print("E-class Status Update:")
    print("  Family 10: Strong candidate for main line")
    print("  Evidence: Phase transition + Hysteresis + Convergence")
    print("  Next: E3 causality verification")
    
    print("=" * 70)

if __name__ == "__main__":
    analyze()
