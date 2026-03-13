#!/usr/bin/env python3
"""
Task-1 Simulator: Heterogeneous Executor Coordination Environment

Simulates a compute cluster with:
- 4 workload classes: CPU-light, GPU-parallel, memory-intensive, IO-intensive
- Dynamic task arrival (Poisson process)
- Node health degradation and recovery
- Fault injection
- Resource constraints
"""

import json
import random
import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import random


class TaskType(Enum):
    CPU_LIGHT = "cpu"
    GPU_PARALLEL = "gpu"
    MEMORY_INTENSIVE = "memory"
    IO_INTENSIVE = "io"


class NodeState(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    RECOVERING = "recovering"
    FAILED = "failed"


@dataclass
class Task:
    task_id: int
    task_type: TaskType
    deadline: float  # relative to arrival time
    priority: int
    arrival_time: float
    resource_demand: Dict[str, float]  # cpu, gpu, memory, io
    
    # Runtime tracking
    assigned_node: Optional[int] = None
    start_time: Optional[float] = None
    completion_time: Optional[float] = None
    missed_deadline: bool = False


@dataclass
class Node:
    node_id: int
    node_type: TaskType  # primary specialization
    capacity: Dict[str, float]
    state: NodeState = NodeState.HEALTHY
    trust_score: float = 1.0
    current_load: Dict[str, float] = field(default_factory=dict)
    task_history: List[Dict] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.current_load:
            self.current_load = {k: 0.0 for k in self.capacity.keys()}
    
    @property
    def available_capacity(self) -> Dict[str, float]:
        return {
            k: max(0, self.capacity[k] - self.current_load[k])
            for k in self.capacity.keys()
        }
    
    def can_accept(self, task: Task) -> bool:
        """Check if node has capacity for task"""
        avail = self.available_capacity
        for resource, demand in task.resource_demand.items():
            if avail.get(resource, 0) < demand:
                return False
        return True
    
    def assign_task(self, task: Task):
        """Assign task to this node"""
        for resource, demand in task.resource_demand.items():
            self.current_load[resource] += demand
    
    def complete_task(self, task: Task):
        """Remove completed task from node"""
        for resource, demand in task.resource_demand.items():
            self.current_load[resource] -= demand
            self.current_load[resource] = max(0, self.current_load[resource])
    
    def update_state(self, time_delta: float, fault_prob: float = 0.001):
        """Update node health state"""
        if self.state == NodeState.HEALTHY:
            if random.random() < fault_prob:
                self.state = NodeState.DEGRADED
                self.trust_score *= 0.8
        elif self.state == NodeState.DEGRADED:
            if random.random() < fault_prob * 2:  # Higher chance to fail
                self.state = NodeState.FAILED
                self.trust_score *= 0.5
            elif random.random() < 0.1:  # Recovery chance
                self.state = NodeState.RECOVERING
        elif self.state == NodeState.RECOVERING:
            if random.random() < 0.2:  # Complete recovery
                self.state = NodeState.HEALTHY
                self.trust_score = min(1.0, self.trust_score * 1.1)


class HeterogeneousCluster:
    """Simulated compute cluster with heterogeneous nodes"""
    
    def __init__(
        self,
        num_cpu_nodes: int = 2,
        num_gpu_nodes: int = 2,
        num_memory_nodes: int = 1,
        num_io_nodes: int = 1,
        seed: Optional[int] = None
    ):
        if seed is not None:
            random.seed(seed)
        
        self.nodes: Dict[int, Node] = {}
        self.node_id_counter = 0
        
        # Create nodes
        for _ in range(num_cpu_nodes):
            self._add_node(TaskType.CPU_LIGHT, {"cpu": 4.0, "gpu": 0.0, "memory": 8.0, "io": 2.0})
        for _ in range(num_gpu_nodes):
            self._add_node(TaskType.GPU_PARALLEL, {"cpu": 2.0, "gpu": 2.0, "memory": 16.0, "io": 1.0})
        for _ in range(num_memory_nodes):
            self._add_node(TaskType.MEMORY_INTENSIVE, {"cpu": 2.0, "gpu": 0.0, "memory": 32.0, "io": 4.0})
        for _ in range(num_io_nodes):
            self._add_node(TaskType.IO_INTENSIVE, {"cpu": 1.0, "gpu": 0.0, "memory": 4.0, "io": 8.0})
        
        self.current_time = 0.0
        self.completed_tasks: List[Task] = []
        self.missed_deadline_tasks: List[Task] = []
        self.failed_tasks: List[Task] = []
    
    def _add_node(self, node_type: TaskType, capacity: Dict[str, float]):
        node = Node(
            node_id=self.node_id_counter,
            node_type=node_type,
            capacity=capacity
        )
        self.nodes[self.node_id_counter] = node
        self.node_id_counter += 1
    
    def get_state_snapshot(self) -> Dict[str, Any]:
        """Get current cluster state for scheduler input"""
        queue_state = {"cpu_queue": 0, "gpu_queue": 0, "memory_queue": 0, "io_queue": 0}
        # Note: actual queue counts tracked by simulator
        
        node_health = {}
        historical_performance = {}
        
        for node_id, node in self.nodes.items():
            node_health[f"node_{node_id}"] = node.state.value
            
            # Calculate historical success rate
            if node.task_history:
                successes = sum(1 for t in node.task_history if not t.get("missed_deadline", False))
                historical_performance[f"node_{node_id}_success"] = successes / len(node.task_history)
            else:
                historical_performance[f"node_{node_id}_success"] = 1.0
        
        return {
            "queue_state": queue_state,
            "node_health": node_health,
            "incoming_tasks": [],  # Populated by simulator
            "historical_performance": historical_performance,
            "current_time": self.current_time
        }
    
    def step(self, time_delta: float = 1.0):
        """Advance simulation by time_delta"""
        self.current_time += time_delta
        
        # Update node states
        for node in self.nodes.values():
            node.update_state(time_delta)
        
        # Process running tasks
        for node in self.nodes.values():
            completed = []
            for task_record in node.task_history:
                if task_record.get("start_time") and not task_record.get("completion_time"):
                    # Simulate task execution
                    elapsed = self.current_time - task_record["start_time"]
                    if elapsed >= task_record.get("estimated_duration", 10.0):
                        task_record["completion_time"] = self.current_time
                        completed.append(task_record)
                        
                        # Check deadline
                        if self.current_time > task_record["deadline_absolute"]:
                            task_record["missed_deadline"] = True
                            self.missed_deadline_tasks.append(task_record)
                        else:
                            self.completed_tasks.append(task_record)
            
            for task_record in completed:
                node.complete_task(task_record.get("task_obj"))


class TaskGenerator:
    """Generate tasks according to stochastic arrival process"""
    
    def __init__(
        self,
        arrival_rate: float = 10.0,  # tasks per unit time
        task_type_distribution: Optional[Dict[TaskType, float]] = None,
        seed: Optional[int] = None
    ):
        if seed is not None:
            random.seed(seed)
        
        self.arrival_rate = arrival_rate
        self.task_counter = 0
        
        if task_type_distribution is None:
            self.task_type_dist = {
                TaskType.CPU_LIGHT: 0.4,
                TaskType.GPU_PARALLEL: 0.3,
                TaskType.MEMORY_INTENSIVE: 0.2,
                TaskType.IO_INTENSIVE: 0.1
            }
        else:
            self.task_type_dist = task_type_distribution
        
        self.next_arrival_time = 0.0
        self._schedule_next_arrival()
    
    def _schedule_next_arrival(self):
        """Schedule next task arrival using exponential distribution"""
        # Exponential distribution using inverse transform sampling
        u = random.random()
        inter_arrival = -math.log(1 - u) / self.arrival_rate
        self.next_arrival_time += inter_arrival
    
    def generate_task(self, current_time: float) -> Optional[Task]:
        """Generate next task if it's time"""
        if current_time < self.next_arrival_time:
            return None
        
        # Select task type
        task_type = random.choices(
            list(self.task_type_dist.keys()),
            weights=list(self.task_type_dist.values())
        )[0]
        
        # Task parameters based on type
        if task_type == TaskType.CPU_LIGHT:
            deadline = random.uniform(20, 60)
            priority = random.randint(1, 5)
            resources = {"cpu": random.uniform(1.0, 3.0), "gpu": 0.0, "memory": random.uniform(1.0, 4.0), "io": random.uniform(0.5, 1.5)}
        elif task_type == TaskType.GPU_PARALLEL:
            deadline = random.uniform(40, 120)
            priority = random.randint(2, 6)
            resources = {"cpu": random.uniform(0.5, 1.5), "gpu": random.uniform(1.0, 2.0), "memory": random.uniform(4.0, 12.0), "io": random.uniform(0.2, 0.8)}
        elif task_type == TaskType.MEMORY_INTENSIVE:
            deadline = random.uniform(60, 180)
            priority = random.randint(1, 4)
            resources = {"cpu": random.uniform(0.5, 1.5), "gpu": 0.0, "memory": random.uniform(8.0, 24.0), "io": random.uniform(1.0, 3.0)}
        else:  # IO_INTENSIVE
            deadline = random.uniform(30, 90)
            priority = random.randint(2, 5)
            resources = {"cpu": random.uniform(0.2, 0.8), "gpu": 0.0, "memory": random.uniform(1.0, 3.0), "io": random.uniform(2.0, 6.0)}
        
        task = Task(
            task_id=self.task_counter,
            task_type=task_type,
            deadline=deadline,
            priority=priority,
            arrival_time=current_time,
            resource_demand=resources
        )
        
        self.task_counter += 1
        self._schedule_next_arrival()
        
        return task


# Export key classes
__all__ = [
    'TaskType', 'NodeState', 'Task', 'Node',
    'HeterogeneousCluster', 'TaskGenerator'
]