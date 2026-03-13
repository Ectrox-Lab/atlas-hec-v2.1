#!/usr/bin/env python3
"""
Task-1 Schedulers: Baseline and candidate implementations
"""

import json
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

try:
    from .environment import (
        Task, TaskType, Node, NodeState,
        HeterogeneousCluster, TaskGenerator
    )
except ImportError:
    from environment import (
        Task, TaskType, Node, NodeState,
        HeterogeneousCluster, TaskGenerator
    )


@dataclass
class SchedulerDecision:
    """Output of scheduler decision"""
    delegation_map: Dict[int, int]  # task_id -> node_id
    recovery_actions: List[str]
    trust_updates: Dict[int, float]  # node_id -> delta


class BaselineScheduler:
    """
    CONFIG_3-style baseline scheduler.
    
    Rules:
    - Shortest-job-first preference (by deadline)
    - Fixed restart-on-failure
    - No dynamic trust update
    - No predictive migration
    """
    
    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        self.name = "baseline_sjf"
    
    def schedule(
        self,
        cluster: HeterogeneousCluster,
        pending_tasks: List[Task],
        current_time: float
    ) -> SchedulerDecision:
        """
        Make scheduling decisions based on current state.
        
        Returns:
            SchedulerDecision with delegation map, recovery actions, trust updates
        """
        delegation_map = {}
        recovery_actions = []
        trust_updates = {}
        
        # Sort pending tasks by deadline (shortest job first)
        sorted_tasks = sorted(pending_tasks, key=lambda t: (t.deadline, -t.priority))
        
        # Try to assign each task
        assigned_tasks = set()
        
        for task in sorted_tasks:
            if task.task_id in assigned_tasks:
                continue
            
            # Find best node (simple first-fit with type affinity)
            best_node = None
            best_score = float('-inf')
            
            for node_id, node in cluster.nodes.items():
                # Skip failed nodes
                if node.state == NodeState.FAILED:
                    continue
                
                # Check capacity
                if not node.can_accept(task):
                    continue
                
                # Score by type affinity + health
                score = 0.0
                
                # Type affinity
                if task.task_type == node.node_type:
                    score += 10.0
                elif task.task_type == TaskType.CPU_LIGHT and node.node_type == TaskType.MEMORY_INTENSIVE:
                    score += 5.0  # CPU can run on memory nodes
                
                # Health preference
                if node.state == NodeState.HEALTHY:
                    score += 5.0
                elif node.state == NodeState.DEGRADED:
                    score -= 5.0
                elif node.state == NodeState.RECOVERING:
                    score -= 2.0
                
                # Prefer less loaded nodes
                load_ratio = sum(node.current_load.values()) / max(sum(node.capacity.values()), 1)
                score -= load_ratio * 3.0
                
                if score > best_score:
                    best_score = score
                    best_node = node_id
            
            if best_node is not None:
                delegation_map[task.task_id] = best_node
                cluster.nodes[best_node].assign_task(task)
                assigned_tasks.add(task.task_id)
        
        # Recovery actions: restart degraded nodes with simple heuristic
        for node_id, node in cluster.nodes.items():
            if node.state == NodeState.FAILED:
                recovery_actions.append(f"restart_node_{node_id}")
                node.state = NodeState.RECOVERING
            elif node.state == NodeState.DEGRADED:
                # Randomly restart some degraded nodes
                if random.random() < 0.1:
                    recovery_actions.append(f"restart_node_{node_id}")
                    node.state = NodeState.RECOVERING
        
        # No trust updates in baseline
        
        return SchedulerDecision(
            delegation_map=delegation_map,
            recovery_actions=recovery_actions,
            trust_updates=trust_updates
        )


class AdaptiveScheduler:
    """
    Adaptive scheduler with trust updates and predictive migration.
    Candidate for Fast Genesis generation.
    """
    
    def __init__(
        self,
        trust_decay_rate: float = 0.1,
        trust_recovery_rate: float = 0.05,
        migration_threshold: float = 0.3,
        load_balance_factor: float = 1.0,
        seed: Optional[int] = None
    ):
        if seed is not None:
            random.seed(seed)
        
        self.name = "adaptive"
        self.trust_decay_rate = trust_decay_rate
        self.trust_recovery_rate = trust_recovery_rate
        self.migration_threshold = migration_threshold
        self.load_balance_factor = load_balance_factor
        
        # Track trust scores
        self.node_trust: Dict[int, float] = {}
    
    def schedule(
        self,
        cluster: HeterogeneousCluster,
        pending_tasks: List[Task],
        current_time: float
    ) -> SchedulerDecision:
        """Make adaptive scheduling decisions"""
        delegation_map = {}
        recovery_actions = []
        trust_updates = {}
        
        # Initialize trust scores
        for node_id in cluster.nodes:
            if node_id not in self.node_trust:
                self.node_trust[node_id] = 1.0
        
        # Update trust based on node states
        for node_id, node in cluster.nodes.items():
            if node.state == NodeState.FAILED:
                trust_updates[node_id] = -self.trust_decay_rate * 2
                self.node_trust[node_id] = max(0.1, self.node_trust[node_id] + trust_updates[node_id])
            elif node.state == NodeState.DEGRADED:
                trust_updates[node_id] = -self.trust_decay_rate
                self.node_trust[node_id] = max(0.1, self.node_trust[node_id] + trust_updates[node_id])
            elif node.state == NodeState.HEALTHY and self.node_trust[node_id] < 1.0:
                trust_updates[node_id] = self.trust_recovery_rate
                self.node_trust[node_id] = min(1.0, self.node_trust[node_id] + trust_updates[node_id])
        
        # Sort tasks by weighted priority and deadline
        sorted_tasks = sorted(
            pending_tasks,
            key=lambda t: (t.deadline / max(t.priority, 1), t.priority),
            reverse=False
        )
        
        # Assign tasks with trust-weighted scoring
        assigned_tasks = set()
        
        for task in sorted_tasks:
            if task.task_id in assigned_tasks:
                continue
            
            best_node = None
            best_score = float('-inf')
            
            for node_id, node in cluster.nodes.items():
                if node.state == NodeState.FAILED:
                    continue
                
                if not node.can_accept(task):
                    continue
                
                # Comprehensive scoring
                score = 0.0
                
                # Type affinity (stronger than baseline)
                if task.task_type == node.node_type:
                    score += 15.0
                elif task.task_type == TaskType.CPU_LIGHT:
                    score += 8.0  # CPU tasks more flexible
                
                # Trust score weighting
                score += self.node_trust.get(node_id, 1.0) * 10.0
                
                # Load balancing
                load_ratio = sum(node.current_load.values()) / max(sum(node.capacity.values()), 1)
                score -= load_ratio * self.load_balance_factor * 5.0
                
                # Health penalty
                if node.state == NodeState.DEGRADED:
                    score -= 10.0
                elif node.state == NodeState.RECOVERING:
                    score -= 3.0
                
                # Historical performance
                if node.task_history:
                    recent = node.task_history[-10:]
                    success_rate = sum(1 for t in recent if not t.get("missed_deadline")) / len(recent)
                    score += success_rate * 5.0
                
                if score > best_score:
                    best_score = score
                    best_node = node_id
            
            if best_node is not None:
                delegation_map[task.task_id] = best_node
                cluster.nodes[best_node].assign_task(task)
                assigned_tasks.add(task.task_id)
        
        # Intelligent recovery
        for node_id, node in cluster.nodes.items():
            if node.state == NodeState.FAILED:
                recovery_actions.append(f"restart_node_{node_id}")
                node.state = NodeState.RECOVERING
                trust_updates[node_id] = trust_updates.get(node_id, 0) + 0.05  # Slight trust boost on restart
            elif node.state == NodeState.DEGRADED:
                # Migrate tasks before restart if trust is very low
                if self.node_trust.get(node_id, 1.0) < self.migration_threshold:
                    recovery_actions.append(f"migrate_then_restart_node_{node_id}")
                    # Find tasks to migrate
                    for task_record in node.task_history:
                        if not task_record.get("completion_time"):
                            recovery_actions.append(f"migrate_task_{task_record['task_id']}")
                    node.state = NodeState.RECOVERING
                elif random.random() < 0.15:  # Higher restart probability than baseline
                    recovery_actions.append(f"restart_node_{node_id}")
                    node.state = NodeState.RECOVERING
        
        return SchedulerDecision(
            delegation_map=delegation_map,
            recovery_actions=recovery_actions,
            trust_updates=trust_updates
        )


def run_simulation(
    scheduler,
    num_tasks: int = 1000,
    seed: Optional[int] = None,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Run a full simulation with given scheduler.
    
    Returns:
        Dict with metrics:
        - throughput: fraction of tasks completed
        - avg_latency: average completion time
        - recovery_time: average time to recover from failures
        - unnecessary_switches: fraction of task migrations
        - missed_deadline_rate: fraction of tasks missing deadline
        - stability_score: coefficient of variation of throughput
    """
    if seed is not None:
        random.seed(seed)
    
    # Initialize
    cluster = HeterogeneousCluster(seed=seed)
    task_gen = TaskGenerator(arrival_rate=10.0, seed=seed)
    
    pending_tasks: List[Task] = []
    all_tasks: List[Task] = []
    
    current_time = 0.0
    time_step = 1.0
    max_time = num_tasks * 2.0  # Allow enough time
    
    recovery_events = []
    migration_count = 0
    total_switches = 0
    
    # Main simulation loop
    while len(cluster.completed_tasks) + len(cluster.missed_deadline_tasks) < num_tasks and current_time < max_time:
        # Generate new tasks
        while True:
            task = task_gen.generate_task(current_time)
            if task is None:
                break
            pending_tasks.append(task)
            all_tasks.append(task)
            if len(all_tasks) >= num_tasks:
                break
        
        if len(all_tasks) >= num_tasks:
            # Stop generating, just process remaining
            pass
        
        # Make scheduling decisions
        if pending_tasks:
            decision = scheduler.schedule(cluster, pending_tasks, current_time)
            
            # Record recovery events
            for action in decision.recovery_actions:
                if "restart" in action:
                    recovery_events.append({
                        "time": current_time,
                        "action": action
                    })
                if "migrate" in action and "task" in action:
                    migration_count += 1
            
            # Remove assigned tasks from pending
            assigned_ids = set(decision.delegation_map.keys())
            pending_tasks = [t for t in pending_tasks if t.task_id not in assigned_ids]
        
        # Advance simulation
        cluster.step(time_step)
        current_time += time_step
        
        # Count switches (tasks moved between nodes)
        # This is simplified - full tracking would require more state
        total_switches += migration_count
        migration_count = 0
    
    # Calculate metrics
    completed = len(cluster.completed_tasks)
    missed = len(cluster.missed_deadline_tasks)
    total_finished = completed + missed
    
    throughput = completed / num_tasks if num_tasks > 0 else 0.0
    missed_rate = missed / num_tasks if num_tasks > 0 else 0.0
    
    # Average latency
    if cluster.completed_tasks:
        latencies = [
            t.get("completion_time", 0) - t.get("arrival_time", 0)
            for t in cluster.completed_tasks
        ]
        avg_latency = sum(latencies) / len(latencies)
    else:
        avg_latency = 0.0
    
    # Recovery time
    if recovery_events:
        recovery_times = [e["time"] for e in recovery_events]
        avg_recovery_time = sum(recovery_times) / len(recovery_times)
    else:
        avg_recovery_time = 0.0
    
    # Unnecessary switches (simplified)
    unnecessary_switches = total_switches / max(num_tasks, 1)
    
    # Stability (coefficient of variation over time windows)
    # Simplified: use variance in completion times
    if cluster.completed_tasks:
        completion_times = [t.get("completion_time", 0) for t in cluster.completed_tasks]
        if len(completion_times) > 1:
            mean_time = sum(completion_times) / len(completion_times)
            variance = sum((t - mean_time) ** 2 for t in completion_times) / len(completion_times)
            std_dev = variance ** 0.5
            stability = std_dev / mean_time if mean_time > 0 else 0.0
        else:
            stability = 0.0
    else:
        stability = 0.0
    
    results = {
        "scheduler": scheduler.name,
        "num_tasks": num_tasks,
        "seed": seed,
        "throughput": throughput,
        "avg_latency": avg_latency,
        "recovery_time": avg_recovery_time,
        "unnecessary_switches": unnecessary_switches,
        "missed_deadline_rate": missed_rate,
        "stability_cv": stability,
        "completed": completed,
        "missed_deadline": missed,
        "total_time": current_time
    }
    
    if verbose:
        print(f"\nSimulation Results ({scheduler.name}):")
        print(f"  Throughput: {throughput:.2%}")
        print(f"  Avg Latency: {avg_latency:.2f}")
        print(f"  Recovery Time: {avg_recovery_time:.2f}")
        print(f"  Unnecessary Switches: {unnecessary_switches:.2%}")
        print(f"  Missed Deadline Rate: {missed_rate:.2%}")
        print(f"  Stability CV: {stability:.3f}")
    
    return results


__all__ = [
    'SchedulerDecision', 'BaselineScheduler', 'AdaptiveScheduler',
    'run_simulation'
]