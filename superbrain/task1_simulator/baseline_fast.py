#!/usr/bin/env python3
"""
Fast Task-1 Baseline Measurement

Simplified but working implementation for quick baseline establishment.
"""

import random
import math
import json
import statistics
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path


@dataclass
class Task:
    task_id: int
    task_type: str
    deadline: float
    arrival_time: float
    duration: float
    completed: bool = False
    completion_time: Optional[float] = None
    missed_deadline: bool = False
    assigned_node: Optional[int] = None


class Cluster:
    def __init__(self, num_nodes: int = 6, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        self.nodes = {i: {'load': 0.0, 'failed': False, 'trust': 1.0} for i in range(num_nodes)}
        self.current_time = 0.0


def run_baseline_scheduling(num_tasks: int = 1000, num_nodes: int = 6, 
                            arrival_rate: float = 8.0, seed: Optional[int] = None) -> dict:
    """
    Run baseline shortest-job-first scheduling simulation.
    
    Returns metrics dict.
    """
    if seed is not None:
        random.seed(seed)
    
    cluster = Cluster(num_nodes=num_nodes, seed=seed)
    
    # Generate tasks
    tasks = []
    current_time = 0.0
    for i in range(num_tasks):
        u = random.random()
        inter_arrival = -math.log(1 - u) / arrival_rate if u < 0.999 else 0.1
        current_time += inter_arrival
        
        task_type = random.choice(['cpu', 'gpu', 'memory', 'io'])
        duration = random.uniform(8, 25)
        deadline = current_time + duration + random.uniform(15, 40)
        
        tasks.append(Task(
            task_id=i,
            task_type=task_type,
            deadline=deadline,
            arrival_time=current_time,
            duration=duration
        ))
    
    # Run simulation
    task_queue = []
    task_idx = 0
    running: Dict[int, Task] = {}  # node_id -> task
    completed = []
    current_time = 0.0
    time_step = 0.5
    max_time = tasks[-1].arrival_time + 500 if tasks else 1000
    
    recovery_events = []
    
    while len(completed) < num_tasks and current_time < max_time:
        # Add new arrivals to queue
        while task_idx < len(tasks) and tasks[task_idx].arrival_time <= current_time:
            task_queue.append(tasks[task_idx])
            task_idx += 1
        
        # Sort queue by deadline (shortest job first)
        task_queue.sort(key=lambda t: t.deadline)
        
        # Assign tasks to available nodes
        assigned = []
        for task in task_queue:
            for node_id, node in cluster.nodes.items():
                if not node['failed'] and node['load'] == 0:
                    running[node_id] = task
                    node['load'] = task.duration
                    task.assigned_node = node_id
                    assigned.append(task)
                    break
        
        for task in assigned:
            task_queue.remove(task)
        
        # Process running tasks
        for node_id in list(running.keys()):
            task = running[node_id]
            cluster.nodes[node_id]['load'] -= time_step
            
            if cluster.nodes[node_id]['load'] <= 0:
                # Task completed
                task.completed = True
                task.completion_time = current_time
                task.missed_deadline = current_time > task.deadline
                completed.append(task)
                cluster.nodes[node_id]['load'] = 0
                del running[node_id]
        
        # Random node failures
        for node_id, node in cluster.nodes.items():
            if not node['failed'] and random.random() < 0.0005:
                node['failed'] = True
                recovery_events.append({
                    'time': current_time,
                    'node': node_id
                })
                # Fail any running task on this node
                if node_id in running:
                    failed_task = running[node_id]
                    failed_task.completion_time = current_time
                    completed.append(failed_task)
                    del running[node_id]
        
        # Recovery
        for node_id, node in cluster.nodes.items():
            if node['failed'] and random.random() < 0.01:
                node['failed'] = False
        
        current_time += time_step
    
    # Calculate metrics
    if completed:
        throughput = sum(1 for t in completed if not t.missed_deadline) / num_tasks
        latencies = [t.completion_time - t.arrival_time for t in completed if t.completion_time]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        missed = sum(1 for t in completed if t.missed_deadline)
        missed_rate = missed / len(completed)
        
        # Stability (coefficient of variation of completion times)
        if len(latencies) > 1:
            mean_lat = statistics.mean(latencies)
            std_lat = statistics.stdev(latencies)
            stability = std_lat / mean_lat if mean_lat > 0 else 0
        else:
            stability = 0
    else:
        throughput = 0
        avg_latency = 0
        missed_rate = 0
        stability = 0
    
    # Recovery time metric
    avg_recovery_time = sum(e['time'] for e in recovery_events) / len(recovery_events) if recovery_events else 0
    
    # Unnecessary switches (migrations due to failures)
    unnecessary_switches = len(recovery_events) / max(num_tasks, 1)
    
    return {
        'throughput': throughput,
        'avg_latency': avg_latency,
        'recovery_time': avg_recovery_time,
        'unnecessary_switches': unnecessary_switches,
        'missed_deadline_rate': missed_rate,
        'stability_cv': stability,
        'completed': len(completed),
        'total': num_tasks,
        'seed': seed
    }


def measure_baseline(num_tasks: int = 1000, num_seeds: int = 10, 
                     output_path: Optional[str] = None) -> dict:
    """Measure baseline across multiple seeds"""
    print(f"Task-1 Baseline Measurement")
    print(f"  Tasks: {num_tasks}, Seeds: {num_seeds}")
    print()
    
    results = []
    for seed in range(num_seeds):
        result = run_baseline_scheduling(num_tasks=num_tasks, seed=seed)
        results.append(result)
        print(f"  Seed {seed}: throughput={result['throughput']:.1%}, "
              f"latency={result['avg_latency']:.1f}, "
              f"missed={result['missed_deadline_rate']:.1%}")
    
    # Aggregate
    metrics = ['throughput', 'avg_latency', 'recovery_time', 
               'unnecessary_switches', 'missed_deadline_rate', 'stability_cv']
    
    aggregated = {}
    for metric in metrics:
        values = [r[metric] for r in results]
        aggregated[metric] = {
            'mean': statistics.mean(values),
            'std': statistics.stdev(values) if len(values) > 1 else 0.0,
            'min': min(values),
            'max': max(values),
            'values': values
        }
    
    # Print summary
    print("\n" + "="*60)
    print("BASELINE SUMMARY")
    print("="*60)
    
    for metric in metrics:
        agg = aggregated[metric]
        print(f"{metric:25s}: {agg['mean']:8.4f} ± {agg['std']:6.4f} "
              f"[{agg['min']:.4f}, {agg['max']:.4f}]")
    
    # Save
    baseline_data = {
        'task_family': 'heterogeneous_executor_coordination',
        'scheduler': 'baseline_sjf_v2',
        'num_tasks': num_tasks,
        'num_seeds': num_seeds,
        'metrics': aggregated
    }
    
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(baseline_data, f, indent=2)
        print(f"\n✓ Saved to: {output_path}")
    
    return baseline_data


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--tasks', type=int, default=1000)
    parser.add_argument('--seeds', type=int, default=10)
    parser.add_argument('--output', type=str,
                       default='../../benchmark_results/task1_baseline/baseline_v2.json')
    
    args = parser.parse_args()
    
    measure_baseline(
        num_tasks=args.tasks,
        num_seeds=args.seeds,
        output_path=args.output
    )