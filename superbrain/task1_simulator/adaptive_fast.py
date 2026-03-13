#!/usr/bin/env python3
"""
Fast Adaptive Scheduler for Task-1

Tests if adaptive scheduling with trust updates can improve over baseline.
"""

import random
import math
from dataclasses import dataclass
from typing import Dict, List, Optional
from baseline_fast import Task, measure_baseline


def run_adaptive_scheduling(num_tasks: int = 1000, num_nodes: int = 6,
                            arrival_rate: float = 8.0, seed: Optional[int] = None,
                            trust_decay: float = 0.1, trust_recovery: float = 0.05) -> dict:
    """
    Run adaptive scheduling with trust updates.
    """
    if seed is not None:
        random.seed(seed)
    
    # Initialize nodes with trust scores
    nodes = {i: {'load': 0.0, 'failed': False, 'trust': 1.0, 'history': []} 
             for i in range(num_nodes)}
    
    # Generate tasks (same as baseline)
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
    
    # Run simulation with adaptive scheduling
    task_queue = []
    task_idx = 0
    running: Dict[int, Task] = {}
    completed = []
    current_time = 0.0
    time_step = 0.5
    max_time = tasks[-1].arrival_time + 500 if tasks else 1000
    
    recovery_events = []
    migrations = 0
    
    while len(completed) < num_tasks and current_time < max_time:
        # Add new arrivals
        while task_idx < len(tasks) and tasks[task_idx].arrival_time <= current_time:
            task_queue.append(tasks[task_idx])
            task_idx += 1
        
        # ADAPTIVE: Sort by weighted priority (deadline + trust-adjusted capacity)
        def task_priority(task):
            # Calculate effective capacity considering node trusts
            effective_capacity = sum(
                nodes[n]['trust'] * (1 - nodes[n]['load'] / 25) 
                for n in nodes if not nodes[n]['failed']
            )
            urgency = 1.0 / (task.deadline - current_time + 1)
            return urgency - task.duration / max(effective_capacity, 0.1)
        
        task_queue.sort(key=task_priority, reverse=True)
        
        # ADAPTIVE: Assign considering trust scores and load balancing
        assigned = []
        for task in task_queue:
            # Score each available node
            best_node = None
            best_score = float('-inf')
            
            for node_id, node in nodes.items():
                if node['failed'] or node['load'] > 0:
                    continue
                
                # Score = trust - load_penalty + type_affinity
                score = node['trust'] * 10
                
                # Type affinity bonus
                if (task.task_type == 'cpu' and node_id < 2) or \
                   (task.task_type == 'gpu' and 2 <= node_id < 4):
                    score += 5
                
                if score > best_score:
                    best_score = score
                    best_node = node_id
            
            if best_node is not None:
                running[best_node] = task
                nodes[best_node]['load'] = task.duration
                task.assigned_node = best_node
                assigned.append(task)
        
        for task in assigned:
            task_queue.remove(task)
        
        # Process running tasks
        for node_id in list(running.keys()):
            task = running[node_id]
            nodes[node_id]['load'] -= time_step
            
            if nodes[node_id]['load'] <= 0:
                task.completed = True
                task.completion_time = current_time
                task.missed_deadline = current_time > task.deadline
                completed.append(task)
                nodes[node_id]['load'] = 0
                nodes[node_id]['history'].append({'success': not task.missed_deadline})
                del running[node_id]
        
        # Node failures and trust updates
        for node_id, node in nodes.items():
            # Update trust based on recent history
            if len(node['history']) >= 5:
                recent_success = sum(1 for h in node['history'][-5:] if h['success']) / 5
                if recent_success < 0.5:
                    node['trust'] = max(0.1, node['trust'] - trust_decay)
                else:
                    node['trust'] = min(1.0, node['trust'] + trust_recovery)
            
            # Failure with trust-based resistance
            failure_prob = 0.0005 * (2 - node['trust'])  # Trusted nodes fail less
            if not node['failed'] and random.random() < failure_prob:
                node['failed'] = True
                recovery_events.append({'time': current_time, 'node': node_id})
                
                # Penalize trust on failure
                node['trust'] = max(0.1, node['trust'] - trust_decay * 2)
                
                # Migrate tasks if possible
                if node_id in running:
                    task = running[node_id]
                    del running[node_id]
                    # Try to find another node
                    for alt_id, alt_node in nodes.items():
                        if not alt_node['failed'] and alt_node['load'] == 0:
                            running[alt_id] = task
                            alt_node['load'] = task.duration
                            task.assigned_node = alt_id
                            migrations += 1
                            break
                    else:
                        # No alternative, task fails
                        task.completion_time = current_time
                        completed.append(task)
        
        # Recovery
        for node_id, node in nodes.items():
            if node['failed'] and random.random() < 0.01:
                node['failed'] = False
                # Slight trust boost on recovery
                node['trust'] = min(1.0, node['trust'] + trust_recovery * 0.5)
        
        current_time += time_step
    
    # Calculate metrics
    import statistics
    
    if completed:
        throughput = sum(1 for t in completed if not t.missed_deadline) / num_tasks
        latencies = [t.completion_time - t.arrival_time for t in completed if t.completion_time]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        missed = sum(1 for t in completed if t.missed_deadline)
        missed_rate = missed / len(completed)
        
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
    
    avg_recovery_time = sum(e['time'] for e in recovery_events) / len(recovery_events) if recovery_events else 0
    unnecessary_switches = migrations / max(num_tasks, 1)
    
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


def compare_schedulers(num_tasks: int = 1000, num_seeds: int = 5):
    """Compare baseline vs adaptive"""
    print("="*70)
    print("TASK-1 SCHEDULER COMPARISON")
    print("="*70)
    
    print(f"\nRunning {num_seeds} seeds with {num_tasks} tasks each...\n")
    
    baseline_results = []
    adaptive_results = []
    
    for seed in range(num_seeds):
        base = run_adaptive_scheduling(num_tasks=num_tasks, seed=seed, 
                                       trust_decay=0.0, trust_recovery=0.0)  # No adaptation
        base['scheduler'] = 'baseline'
        baseline_results.append(base)
        
        adaptive = run_adaptive_scheduling(num_tasks=num_tasks, seed=seed,
                                          trust_decay=0.1, trust_recovery=0.05)
        adaptive['scheduler'] = 'adaptive'
        adaptive_results.append(adaptive)
        
        print(f"Seed {seed}:")
        print(f"  Baseline:  throughput={base['throughput']:5.1%}, "
              f"latency={base['avg_latency']:6.1f}, "
              f"missed={base['missed_deadline_rate']:5.1%}")
        print(f"  Adaptive:  throughput={adaptive['throughput']:5.1%}, "
              f"latency={adaptive['avg_latency']:6.1f}, "
              f"missed={adaptive['missed_deadline_rate']:5.1%}, "
              f"Δ={adaptive['throughput']-base['throughput']:+.1%}")
    
    # Summary
    import statistics
    
    def summarize(results):
        return {
            'throughput': statistics.mean([r['throughput'] for r in results]),
            'latency': statistics.mean([r['avg_latency'] for r in results]),
            'missed': statistics.mean([r['missed_deadline_rate'] for r in results])
        }
    
    base_sum = summarize(baseline_results)
    adap_sum = summarize(adaptive_results)
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"{'Metric':<20} {'Baseline':>12} {'Adaptive':>12} {'Improvement':>12}")
    print("-"*70)
    print(f"{'Throughput':<20} {base_sum['throughput']:>11.2%} {adap_sum['throughput']:>11.2%} "
          f"{adap_sum['throughput']-base_sum['throughput']:>+11.2%}")
    print(f"{'Avg Latency':<20} {base_sum['latency']:>12.1f} {adap_sum['latency']:>12.1f} "
          f"{adap_sum['latency']-base_sum['latency']:>+12.1f}")
    print(f"{'Missed Deadline':<20} {base_sum['missed']:>11.2%} {adap_sum['missed']:>11.2%} "
          f"{adap_sum['missed']-base_sum['missed']:>+11.2%}")
    
    improvement = adap_sum['throughput'] - base_sum['throughput']
    print(f"\nAdaptive improvement: {improvement:+.2%}")
    
    if improvement > 0:
        print("✓ Adaptive scheduler shows improvement over baseline")
    else:
        print("⚠ Adaptive scheduler does not improve over baseline")
    
    return baseline_results, adaptive_results


if __name__ == "__main__":
    compare_schedulers(num_tasks=1000, num_seeds=5)