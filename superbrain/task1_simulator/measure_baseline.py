#!/usr/bin/env python3
"""
Measure Task-1 Baseline Performance

Runs baseline scheduler across multiple seeds to establish
approved baseline values for Mainline comparison.
"""

import json
import sys
import statistics
from pathlib import Path

try:
    from .schedulers import BaselineScheduler, run_simulation
except ImportError:
    from schedulers import BaselineScheduler, run_simulation
from typing import Optional


def measure_baseline(
    num_tasks: int = 10000,
    num_seeds: int = 10,
    output_path: Optional[str] = None
) -> dict:
    """
    Measure baseline performance across multiple seeds.
    
    Returns dict with mean, std, min, max for each metric.
    """
    print(f"Measuring Task-1 Baseline")
    print(f"  Tasks per run: {num_tasks}")
    print(f"  Seeds: {num_seeds}")
    print()
    
    all_results = []
    
    for seed in range(num_seeds):
        print(f"  Running seed {seed}...", end=" ", flush=True)
        scheduler = BaselineScheduler(seed=seed)
        result = run_simulation(scheduler, num_tasks=num_tasks, seed=seed)
        all_results.append(result)
        print(f"throughput={result['throughput']:.2%}")
    
    # Aggregate metrics
    metrics = [
        'throughput', 'avg_latency', 'recovery_time',
        'unnecessary_switches', 'missed_deadline_rate', 'stability_cv'
    ]
    
    aggregated = {}
    for metric in metrics:
        values = [r[metric] for r in all_results]
        aggregated[metric] = {
            'mean': statistics.mean(values),
            'std': statistics.stdev(values) if len(values) > 1 else 0.0,
            'min': min(values),
            'max': max(values),
            'values': values
        }
    
    # Print summary
    print("\n" + "="*60)
    print("BASELINE MEASUREMENT SUMMARY")
    print("="*60)
    
    for metric in metrics:
        agg = aggregated[metric]
        print(f"\n{metric}:")
        print(f"  Mean: {agg['mean']:.4f}")
        print(f"  Std:  {agg['std']:.4f}")
        print(f"  Min:  {agg['min']:.4f}")
        print(f"  Max:  {agg['max']:.4f}")
    
    # Baseline target values (from v0.2 spec)
    print("\n" + "="*60)
    print("COMPARISON TO PLANNING ANCHORS")
    print("="*60)
    
    anchors = {
        'throughput': 0.85,
        'avg_latency': 120.0,
        'recovery_time': 500.0,
        'unnecessary_switches': 0.15
    }
    
    for metric, anchor in anchors.items():
        if metric in aggregated:
            measured = aggregated[metric]['mean']
            diff_pct = ((measured - anchor) / anchor) * 100 if anchor != 0 else 0
            status = "✓" if abs(diff_pct) < 10 else "⚠"
            print(f"{status} {metric}: anchor={anchor:.2f}, measured={measured:.2f} ({diff_pct:+.1f}%)")
    
    # Save results
    baseline_data = {
        'task_family': 'heterogeneous_executor_coordination',
        'scheduler': 'baseline_sjf',
        'num_tasks': num_tasks,
        'num_seeds': num_seeds,
        'metrics': aggregated,
        'raw_results': all_results
    }
    
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(baseline_data, f, indent=2)
        print(f"\n✓ Baseline data saved to: {output_path}")
    
    return baseline_data


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Measure Task-1 baseline')
    parser.add_argument('--tasks', type=int, default=10000, help='Tasks per run')
    parser.add_argument('--seeds', type=int, default=10, help='Number of seeds')
    parser.add_argument('--output', type=str, 
                       default='../../benchmark_results/task1_baseline/baseline_measured.json',
                       help='Output path')
    
    args = parser.parse_args()
    
    measure_baseline(
        num_tasks=args.tasks,
        num_seeds=args.seeds,
        output_path=args.output
    )