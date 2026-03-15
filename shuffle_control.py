#!/usr/bin/env python3
"""
Control 1: Shuffled Trajectory
Tests whether L5 effect requires temporal/structural order
"""

import json
import random
from pathlib import Path

def shuffle_control(batch_dir, n_shuffles=1000):
    """Shuffle window order and recalculate mean"""
    path = Path(batch_dir)
    
    # Load original values
    original_values = []
    for window_file in sorted(path.glob('window_*/metrics.json')):
        with open(window_file) as f:
            data = json.load(f)
            original_values.append(data.get('transfer_gap_pp', 0))
    
    for hour_file in sorted(path.glob('hour_*/metrics.json')):
        with open(hour_file) as f:
            data = json.load(f)
            original_values.append(data.get('transfer_gap_pp', 0))
    
    original_mean = sum(original_values) / len(original_values)
    
    # Shuffle and recalculate
    shuffled_means = []
    random.seed(123)
    
    for _ in range(n_shuffles):
        shuffled = original_values.copy()
        random.shuffle(shuffled)
        shuffled_mean = sum(shuffled) / len(shuffled)
        shuffled_means.append(shuffled_mean)
    
    # Analysis
    shuffled_means.sort()
    ci_95_lower = shuffled_means[int(0.025 * n_shuffles)]
    ci_95_upper = shuffled_means[int(0.975 * n_shuffles)]
    
    return {
        'original_mean': original_mean,
        'shuffled_mean': sum(shuffled_means) / len(shuffled_means),
        'shuffled_std': (sum((x - sum(shuffled_means)/len(shuffled_means))**2 for x in shuffled_means) / len(shuffled_means)) ** 0.5,
        'ci_95': [ci_95_lower, ci_95_upper],
        'original_in_ci': ci_95_lower <= original_mean <= ci_95_upper,
        'n_shuffles': n_shuffles
    }

def main():
    print("=" * 70)
    print("CONTROL 1: SHUFFLED TRAJECTORY")
    print("=" * 70)
    print()
    print("Hypothesis: If L5 effect is genuine, shuffling window order")
    print("should NOT change the effect (windows are independent).")
    print("If effect depends on temporal structure, shuffling may matter.")
    print()
    
    batches = [
        ('Code→Math (Batch-1)', 'ralph_runs/l5_batch1'),
        ('Code→Planning (Batch-4)', 'ralph_runs/l5_batch4_code2planning'),
        ('Planning→Math (Batch-7)', 'ralph_runs/l5_batch7_planning2math'),
    ]
    
    results = {}
    
    for name, batch_dir in batches:
        print(f"\n{name}:")
        print("-" * 50)
        
        result = shuffle_control(batch_dir)
        results[name] = result
        
        print(f"  Original Mean: {result['original_mean']:.2f}pp")
        print(f"  Shuffled Mean: {result['shuffled_mean']:.2f}pp")
        print(f"  Shuffled SD:   {result['shuffled_std']:.3f}pp")
        print(f"  95% CI:        [{result['ci_95'][0]:.2f}, {result['ci_95'][1]:.2f}]")
        print(f"  Original in CI: {result['original_in_ci']}")
        
        if result['original_in_ci']:
            print(f"  ✓ Result: Shuffling doesn't affect mean (windows independent)")
        else:
            print(f"  ⚠ Result: Original outside CI (temporal structure may matter)")
    
    # Save
    with open('control1_shuffled.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n\nSaved to: control1_shuffled.json")
    print()
    print("=" * 70)
    print("INTERPRETATION:")
    print("=" * 70)
    print()
    print("If shuffling doesn't change mean significantly:")
    print("  → Windows are effectively independent")
    print("  → Effect is not artifact of temporal order")
    print("  → L5 effect is genuine (or at least not structure-only)")
    print()
    print("If shuffling changes mean significantly:")
    print("  → Temporal/window order matters")
    print("  → Need to investigate what structural property drives effect")

if __name__ == "__main__":
    main()
