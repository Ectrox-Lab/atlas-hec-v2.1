#!/usr/bin/env python3
"""
Task-1 Simulator: Heterogeneous Executor Coordination

First real validation task for Atlas-HEC / Superbrain.

This module provides:
- Environment simulation (cluster, nodes, tasks)
- Baseline scheduler (CONFIG_3-style rules-first)
- Adaptive scheduler (candidate for Fast Genesis)
- Simulation runner with metrics collection
"""

from .environment import (
    TaskType, NodeState, Task, Node,
    HeterogeneousCluster, TaskGenerator
)

from .schedulers import (
    SchedulerDecision, BaselineScheduler, AdaptiveScheduler,
    run_simulation
)

__version__ = "0.1.0"
__all__ = [
    'TaskType', 'NodeState', 'Task', 'Node',
    'HeterogeneousCluster', 'TaskGenerator',
    'SchedulerDecision', 'BaselineScheduler', 'AdaptiveScheduler',
    'run_simulation'
]