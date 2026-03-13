#!/usr/bin/env python3
"""Simple test of Task-1 simulator"""

import random
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class TaskType(Enum):
    CPU_LIGHT = "cpu"
    GPU_PARALLEL = "gpu"


@dataclass
class SimpleTask:
    task_id: int
    task_type: TaskType
    deadline: float
    arrival_time: float
    duration: float
    completed: bool = False
    completion_time: Optional[float] = None
    missed_deadline: bool = False


@dataclass
class SimpleNode:
    node_id: int
    capacity: float = 1.0
    current_load: float = 0.0
    failed: bool = False


class SimpleSimulator:
    """Simplified simulator for testing"""
    
    def __init__(self, num_nodes: int = 4, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        
        self.nodes = {i: SimpleNode(i) for i in range(num_nodes)}
        self.current_time = 0.0
        self.tasks: List[SimpleTask] = []
        self.completed_tasks: List[SimpleTask] = []
        
    def generate_tasks(self, num_tasks: int, arrival_rate: float = 10.0):
        """Generate task arrival schedule"""
        current_time = 0.0
        for i in range(num_tasks):
            # Exponential inter-arrival
            u = random.random()
            inter_arrival = -math.log(1 - u) / arrival_rate
            current_time += inter_arrival
            
            task_type = random.choice([TaskType.CPU_LIGHT, TaskType.GPU_PARALLEL])
            duration = random.uniform(5, 20)
            deadline = current_time + duration + random.uniform(10, 30)
            
            task = SimpleTask(
                task_id=i,
                task_type=task_type,
                deadline=deadline,
                arrival_time=current_time,
                duration=duration
            )
            self.tasks.append(task)
    
    def run_baseline(self, time_step: float = 1.0, max_time: float = 5000.0):
        """Run simple baseline scheduler"""
        task_idx = 0
        running_tasks: Dict[int, SimpleTask] = {}  # node_id -> task
        
        while (len(self.completed_tasks) < len(self.tasks) and 
               self.current_time < max_time):
            
            # Add newly arrived tasks to queue
            pending = []
            while task_idx < len(self.tasks) and self.tasks[task_idx].arrival_time <= self.current_time:
                pending.append(self.tasks[task_idx])
                task_idx += 1
            
            # Assign pending tasks to available nodes (simple round-robin)
            for task in pending:
                assigned = False
                for node_id, node in self.nodes.items():
                    if not node.failed and node.current_load == 0:
                        running_tasks[node_id] = task
                        node.current_load = task.duration
                        assigned = True
                        break
                
                if not assigned:
                    # Re-queue (simplified)
                    pass
            
            # Advance running tasks
            completed_now = []
            for node_id, task in list(running_tasks.items()):
                node = self.nodes[node_id]
                node.current_load -= time_step
                
                if node.current_load <= 0:
                    # Task completed
                    task.completed = True
                    task.completion_time = self.current_time
                    if task.completion_time > task.deadline:
                        task.missed_deadline = True
                    self.completed_tasks.append(task)
                    completed_now.append(node_id)
                    node.current_load = 0
            
            for node_id in completed_now:
                del running_tasks[node_id]
            
            self.current_time += time_step
        
        # Calculate metrics
        if self.completed_tasks:
            throughput = len(self.completed_tasks) / len(self.tasks)
            latencies = [t.completion_time - t.arrival_time for t in self.completed_tasks]
            avg_latency = sum(latencies) / len(latencies)
            missed = sum(1 for t in self.completed_tasks if t.missed_deadline)
            missed_rate = missed / len(self.completed_tasks)
        else:
            throughput = 0.0
            avg_latency = 0.0
            missed_rate = 0.0
        
        return {
            'throughput': throughput,
            'avg_latency': avg_latency,
            'missed_rate': missed_rate,
            'completed': len(self.completed_tasks),
            'total': len(self.tasks)
        }


def test_simulator():
    """Quick test"""
    print("Testing simplified Task-1 simulator")
    
    for seed in range(3):
        sim = SimpleSimulator(num_nodes=4, seed=seed)
        sim.generate_tasks(num_tasks=1000, arrival_rate=10.0)
        results = sim.run_baseline()
        
        print(f"\nSeed {seed}:")
        print(f"  Throughput: {results['throughput']:.2%}")
        print(f"  Avg Latency: {results['avg_latency']:.2f}")
        print(f"  Missed Rate: {results['missed_rate']:.2%}")
        print(f"  Completed: {results['completed']}/{results['total']}")


if __name__ == "__main__":
    test_simulator()