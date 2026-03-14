#!/usr/bin/env python3
"""
Task-2: Multi-Stage Pipeline Simulator

Multi-stage task processing with:
- Stage handoff coordination
- Failure recovery
- Pipeline-wide metrics

Based on Task-1 heterogeneous executor coordination,
extended to multi-stage pipeline semantics.
"""

import random
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import statistics


@dataclass
class PipelineTask:
    """Task flowing through pipeline stages"""
    task_id: int
    arrival_time: float
    stage_requirements: List[float]  # Processing time needed per stage
    current_stage: int = 0
    completion_time: Optional[float] = None
    stage_start_times: List[float] = field(default_factory=list)
    stage_completion_times: List[float] = field(default_factory=list)
    failed: bool = False
    rerouted: int = 0


@dataclass 
class PipelineStage:
    """Single stage in pipeline"""
    stage_id: int
    capacity: float
    executors: Dict[int, dict]  # executor_id -> {load, trust, failed}
    
    def __init__(self, stage_id: int, num_executors: int = 4, capacity: float = 25.0):
        self.stage_id = stage_id
        self.capacity = capacity
        self.executors = {
            i: {'load': 0.0, 'trust': 1.0, 'failed': False, 'history': []}
            for i in range(num_executors)
        }


class PipelineSimulator:
    """
    Multi-stage pipeline simulator for Task-2
    
    Parameters (mapped from P/T/M/D):
    - pressure: Task injection rate multiplier
    - triage: Stage priority granularity  
    - memory: Pipeline state history length
    - delegation: Stage assignment strictness
    """
    
    def __init__(self, 
                 num_stages: int = 4,
                 executors_per_stage: int = 4,
                 seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        
        self.num_stages = num_stages
        self.stages = [
            PipelineStage(i, executors_per_stage)
            for i in range(num_stages)
        ]
        self.tasks: List[PipelineTask] = []
        self.completed_tasks: List[PipelineTask] = []
        self.failed_tasks: List[PipelineTask] = []
        
        # Metrics
        self.stage_handoffs = 0
        self.reroutes = 0
        self.stage_failures = 0
        self.recovery_successes = 0
        
    def generate_tasks(self, num_tasks: int, arrival_rate: float = 8.0, 
                       base_work: float = 20.0):
        """Generate task arrival stream"""
        current_time = 0.0
        
        for i in range(num_tasks):
            # Exponential inter-arrival
            u = random.random()
            inter_arrival = -math.log(1 - u) / arrival_rate if u < 0.999 else 0.1
            current_time += inter_arrival
            
            # Each task needs processing at each stage
            stage_work = [
                base_work * random.uniform(0.8, 1.2)
                for _ in range(self.num_stages)
            ]
            
            task = PipelineTask(
                task_id=i,
                arrival_time=current_time,
                stage_requirements=stage_work
            )
            self.tasks.append(task)
    
    def run_pipeline_simple(self, scheduler_config: Dict) -> Dict:
        """Simplified pipeline simulation"""
        trust_decay = scheduler_config.get('trust_decay', 0.1)
        trust_recovery = scheduler_config.get('trust_recovery', 0.05)
        pressure = scheduler_config.get('pressure', 2)
        triage = scheduler_config.get('triage', 3)
        memory = scheduler_config.get('memory', 3)
        
        # Adjust parameters by pressure
        stage_capacity = 25.0 / (1 + (pressure - 2) * 0.2)  # Higher pressure = lower effective capacity
        
        for task in self.tasks:
            # Simulate pipeline traversal
            current_time = task.arrival_time
            completed_stages = 0
            failed = False
            
            for stage_id in range(self.num_stages):
                # Base processing time
                process_time = task.stage_requirements[stage_id]
                
                # Adjust by capacity and random factors
                effective_time = process_time * random.uniform(0.9, 1.1) / (stage_capacity / 25.0)
                
                # Deadline pressure (triage effect)
                if triage >= 4:
                    effective_time *= 0.9  # Better scheduling = faster
                elif triage <= 2:
                    effective_time *= 1.2  # Poor scheduling = slower
                
                current_time += effective_time
                
                # Stage failure chance (pressure-dependent, higher for realism)
                base_failure = 0.03 if pressure <= 2 else 0.08 if pressure == 3 else 0.18
                stage_failed = random.random() < base_failure
                
                if stage_failed:
                    # Recovery chance depends on memory
                    recovery_prob = 0.25 if memory <= 2 else 0.55 if memory == 3 else 0.80
                    if random.random() < recovery_prob:
                        self.recovery_successes += 1
                        # Add recovery overhead
                        current_time += process_time * 0.3
                    else:
                        failed = True
                        self.stage_failures += 1
                        break
                
                completed_stages += 1
            
            if failed:
                task.failed = True
                self.failed_tasks.append(task)
            elif completed_stages == self.num_stages:
                task.completion_time = current_time
                self.completed_tasks.append(task)
        
        return self._calculate_metrics()
    
    def run_pipeline(self, 
                     scheduler_config: Dict,
                     time_step: float = 0.5,
                     max_time: float = 5000.0) -> Dict:
        """
        Run pipeline simulation
        
        scheduler_config: {
            'trust_decay': float,
            'trust_recovery': float,
            'pressure': int,  # 1-4
            'triage': int,    # 1-5
            'memory': int,    # 1-5
            'delegation': int # 1-2
        }
        """
        # Extract config
        trust_decay = scheduler_config.get('trust_decay', 0.1)
        trust_recovery = scheduler_config.get('trust_recovery', 0.05)
        pressure = scheduler_config.get('pressure', 2)
        triage = scheduler_config.get('triage', 3)
        memory = scheduler_config.get('memory', 3)
        delegation = scheduler_config.get('delegation', 1)
        
        # Adjust arrival rate by pressure
        effective_arrival = 8.0 * (1 + (pressure - 2) * 0.3)
        
        task_idx = 0
        current_time = 0.0
        
        # Running tasks at each stage
        stage_tasks: Dict[int, Dict[int, PipelineTask]] = {
            s: {} for s in range(self.num_stages)
        }
        
        # Task queue at each stage
        stage_queues: Dict[int, List[PipelineTask]] = {
            s: [] for s in range(self.num_stages)
        }
        
        max_sim_time = max(t.arrival_time for t in self.tasks) + 1000 if self.tasks else 1000
        
        while (len(self.completed_tasks) + len(self.failed_tasks) < len(self.tasks) and 
               current_time < max_sim_time):
            
            # Inject new tasks at stage 0
            while (task_idx < len(self.tasks) and 
                   self.tasks[task_idx].arrival_time <= current_time):
                stage_queues[0].append(self.tasks[task_idx])
                task_idx += 1
            
            # Process each stage
            for stage_id in range(self.num_stages):
                stage = self.stages[stage_id]
                
                # Triage: sort queue by priority (based on triage granularity)
                if triage >= 4:  # High triage = better prioritization
                    stage_queues[stage_id].sort(
                        key=lambda t: sum(t.stage_requirements[stage_id:]),
                        reverse=True
                    )
                
                # Assign tasks to executors
                assigned = []
                for task in stage_queues[stage_id]:
                    # Find best executor (trust-based if delegation=1)
                    best_executor = None
                    best_score = -float('inf')
                    
                    for exec_id, exec_state in stage.executors.items():
                        if exec_state['failed']:
                            continue
                        
                        if delegation == 1:  # Strict trust-based
                            score = exec_state['trust'] * (1 - exec_state['load'] / stage.capacity)
                        else:  # Flexible load-based
                            score = 1 - exec_state['load'] / stage.capacity
                        
                        if score > best_score:
                            best_score = score
                            best_executor = exec_id
                    
                    if best_executor is not None and best_score > 0.1:
                        stage_tasks[stage_id][best_executor] = task
                        stage.executors[best_executor]['load'] += task.stage_requirements[stage_id]
                        if not task.stage_start_times:
                            task.stage_start_times = [0.0] * self.num_stages
                        task.stage_start_times[stage_id] = current_time
                        assigned.append(task)
                
                # Remove assigned from queue
                for task in assigned:
                    stage_queues[stage_id].remove(task)
                
                # Advance tasks in stage
                completed_execs = []
                for exec_id, task in list(stage_tasks[stage_id].items()):
                    exec_state = stage.executors[exec_id]
                    work_needed = task.stage_requirements[stage_id]
                    
                    # Progress work
                    exec_state['load'] = max(0, exec_state['load'] - time_step)
                    
                    if exec_state['load'] <= 0:
                        # Stage complete
                        if not task.stage_completion_times:
                            task.stage_completion_times = [0.0] * self.num_stages
                        task.stage_completion_times[stage_id] = current_time
                        completed_execs.append(exec_id)
                        
                        # Update trust (success)
                        exec_state['trust'] = min(1.0, exec_state['trust'] + trust_recovery)
                        exec_state['history'].append(('success', current_time))
                        
                        # Handoff to next stage or complete
                        if stage_id + 1 < self.num_stages:
                            stage_queues[stage_id + 1].append(task)
                            self.stage_handoffs += 1
                            task.current_stage = stage_id + 1
                        else:
                            # Pipeline complete
                            task.completion_time = current_time
                            self.completed_tasks.append(task)
                
                for exec_id in completed_execs:
                    del stage_tasks[stage_id][exec_id]
                
                # Random failures based on pressure
                failure_prob = 0.001 * pressure
                for exec_id, exec_state in stage.executors.items():
                    if not exec_state['failed'] and random.random() < failure_prob:
                        exec_state['failed'] = True
                        self.stage_failures += 1
                        
                        # Fail any running task
                        if exec_id in stage_tasks[stage_id]:
                            task = stage_tasks[stage_id][exec_id]
                            
                            # Recovery attempt based on memory
                            if memory >= 3 and random.random() < 0.7:
                                # Recovery successful - reroute
                                stage_queues[stage_id].append(task)
                                task.rerouted += 1
                                self.reroutes += 1
                                self.recovery_successes += 1
                                del stage_tasks[stage_id][exec_id]
                            else:
                                # Recovery failed
                                task.failed = True
                                self.failed_tasks.append(task)
                                del stage_tasks[stage_id][exec_id]
                        
                        # Penalize trust
                        exec_state['trust'] = max(0.0, exec_state['trust'] - trust_decay)
                        exec_state['history'].append(('failure', current_time))
                
                # Recovery of failed executors
                for exec_state in stage.executors.values():
                    if exec_state['failed'] and random.random() < 0.05:
                        exec_state['failed'] = False
            
            current_time += time_step
        
        # Calculate metrics
        return self._calculate_metrics()
    
    def _calculate_metrics(self) -> Dict:
        """Calculate pipeline performance metrics"""
        total_tasks = len(self.tasks)
        completed = len(self.completed_tasks)
        failed = len(self.failed_tasks)
        
        # Pipeline completion rate
        completion_rate = completed / total_tasks if total_tasks > 0 else 0.0
        
        # Stage throughput (tasks per unit time)
        if self.completed_tasks:
            total_time = max(t.completion_time for t in self.completed_tasks)
            throughput = completed / total_time if total_time > 0 else 0.0
        else:
            throughput = 0.0
        
        # Handoff latency (average time between stage completions)
        handoff_latencies = []
        for task in self.completed_tasks:
            for i in range(1, self.num_stages):
                if i < len(task.stage_completion_times) and (i-1) < len(task.stage_completion_times):
                    latency = task.stage_start_times[i] - task.stage_completion_times[i-1]
                    handoff_latencies.append(latency)
        avg_handoff_latency = statistics.mean(handoff_latencies) if handoff_latencies else 0.0
        
        # Failover success rate
        total_failures = self.stage_failures
        failover_success = self.recovery_successes / total_failures if total_failures > 0 else 1.0
        
        # Unnecessary rerouting (reroutes per completed task)
        total_reroutes = sum(t.rerouted for t in self.completed_tasks)
        reroute_rate = total_reroutes / completed if completed > 0 else 0.0
        
        return {
            'pipeline_completion_rate': round(completion_rate, 4),
            'stage_throughput': round(throughput, 6),
            'avg_handoff_latency': round(avg_handoff_latency, 2),
            'failover_success_rate': round(failover_success, 4),
            'reroute_rate': round(reroute_rate, 4),
            'completed': completed,
            'failed': failed,
            'total': total_tasks,
            'stage_failures': self.stage_failures,
            'stage_handoffs': self.stage_handoffs
        }


def run_pipeline_simulation(num_tasks: int = 500,
                           pressure: int = 2,
                           triage: int = 3,
                           memory: int = 3,
                           delegation: int = 1,
                           trust_decay: float = 0.1,
                           trust_recovery: float = 0.05,
                           seed: Optional[int] = None) -> Dict:
    """Convenience function to run pipeline simulation"""
    sim = PipelineSimulator(num_stages=4, executors_per_stage=4, seed=seed)
    sim.generate_tasks(num_tasks=num_tasks, arrival_rate=8.0 * (1 + (pressure - 2) * 0.3))
    
    config = {
        'pressure': pressure,
        'triage': triage,
        'memory': memory,
        'delegation': delegation,
        'trust_decay': trust_decay,
        'trust_recovery': trust_recovery
    }
    
    # Use simplified version for now
    return sim.run_pipeline_simple(config)


def measure_baseline(num_tasks: int = 500, num_seeds: int = 5) -> Dict:
    """Measure baseline performance"""
    print("Task-2 Pipeline Baseline Measurement")
    print(f"  Tasks: {num_tasks}, Seeds: {num_seeds}")
    print()
    
    results = []
    for seed in range(num_seeds):
        metrics = run_pipeline_simulation(
            num_tasks=num_tasks,
            pressure=2,  # Baseline pressure
            triage=3,
            memory=3,
            delegation=1,
            seed=seed
        )
        results.append(metrics)
        print(f"  Seed {seed}: completion={metrics['pipeline_completion_rate']:.1%}, "
              f"throughput={metrics['stage_throughput']:.4f}")
    
    # Aggregate
    completion_rates = [r['pipeline_completion_rate'] for r in results]
    throughputs = [r['stage_throughput'] for r in results]
    
    print()
    print("=" * 60)
    print("BASELINE SUMMARY")
    print("=" * 60)
    print(f"Pipeline completion: {statistics.mean(completion_rates):.1%} ± {statistics.stdev(completion_rates):.1%}")
    print(f"Stage throughput: {statistics.mean(throughputs):.4f} ± {statistics.stdev(throughputs):.4f}")
    print(f"Failover success: {statistics.mean([r['failover_success_rate'] for r in results]):.1%}")
    print()
    
    return {
        'pipeline_completion_rate': {
            'mean': statistics.mean(completion_rates),
            'std': statistics.stdev(completion_rates),
            'min': min(completion_rates),
            'max': max(completion_rates)
        },
        'stage_throughput': {
            'mean': statistics.mean(throughputs),
            'std': statistics.stdev(throughputs)
        }
    }


if __name__ == "__main__":
    # Quick test
    print("Testing Task-2 Pipeline Simulator")
    print()
    
    # Baseline
    baseline = measure_baseline(num_tasks=200, num_seeds=3)
    
    # Test different configurations
    configs = [
        {"name": "P2T3M3", "pressure": 2, "triage": 3, "memory": 3},
        {"name": "P3T4M4", "pressure": 3, "triage": 4, "memory": 4},
        {"name": "P2T4M4", "pressure": 2, "triage": 4, "memory": 4},
    ]
    
    print("\nConfiguration Comparison:")
    print("-" * 60)
    for cfg in configs:
        result = run_pipeline_simulation(
            num_tasks=200,
            pressure=cfg['pressure'],
            triage=cfg['triage'],
            memory=cfg['memory'],
            seed=42
        )
        print(f"{cfg['name']}: completion={result['pipeline_completion_rate']:.1%}, "
              f"handoff={result['avg_handoff_latency']:.1f}, "
              f"failover={result['failover_success_rate']:.1%}")
