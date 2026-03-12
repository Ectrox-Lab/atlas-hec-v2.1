#!/usr/bin/env python3
"""
G1 Long-Horizon 72h Workload
Simulates: agent loop, drift monitoring, hijack detection
"""

import json
import os
import sys
import time
import random
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

# Paths
OUTPUT_DIR = Path("implementations/g1/output")
OUTPUT_DIR.mkdir(exist_ok=True)
CHECKPOINT_DIR = OUTPUT_DIR / "checkpoints"
CHECKPOINT_DIR.mkdir(exist_ok=True)

OUTPUT_TIMESERIES = OUTPUT_DIR / "g1_timeseries.csv"
OUTPUT_DRIFT = OUTPUT_DIR / "drift_events.jsonl"
OUTPUT_INTERACTIONS = OUTPUT_DIR / "specialist_interaction_log.jsonl"

def initialize_agent() -> Dict:
    """Initialize agent with goal and memory"""
    return {
        "goal": "Build reliable superbrain governance system",
        "goal_vector": [1.0, 0.9, 0.95, 0.85],  # Semantic representation
        "memory": [],
        "specialist_dependencies": {},
        "ticks_completed": 0,
        "hours_completed": 0
    }

def get_task_stream():
    """Generator yielding tasks"""
    task_types = [
        "delegation_decision",
        "audit_check",
        "memory_compaction",
        "goal_refinement",
        "specialist_selection",
        "conflict_resolution",
        "evidence_grading"
    ]
    
    while True:
        yield {
            "type": random.choice(task_types),
            "complexity": random.choice(["low", "medium", "high"]),
            "timestamp": datetime.now().isoformat()
        }

def execute_task(agent: Dict, task: Dict) -> Dict:
    """Execute task and return result"""
    
    # Simulate task execution
    result = {
        "task_type": task["type"],
        "success": random.random() > 0.1,  # 90% success rate
        "duration_ms": random.randint(10, 1000),
        "specialist_used": random.choice(["executive", "auditor", "specialist_a", "specialist_b"])
    }
    
    # Update agent memory
    agent["memory"].append({
        "tick": agent["ticks_completed"],
        "task": task["type"],
        "result": result["success"]
    })
    
    # Trim memory to prevent unbounded growth
    if len(agent["memory"]) > 1000:
        agent["memory"] = agent["memory"][-500:]
    
    # Track specialist dependencies
    if result["specialist_used"] not in agent["specialist_dependencies"]:
        agent["specialist_dependencies"][result["specialist_used"]] = 0
    agent["specialist_dependencies"][result["specialist_used"]] += 1
    
    return result

def measure_goal_drift(agent: Dict) -> float:
    """Measure semantic drift from original goal"""
    
    # Simulate drift based on:
    # - Number of ticks (time pressure)
    # - Specialist dependency concentration
    # - Task completion patterns
    
    base_drift = 0.02  # 2% base drift per hour
    
    # Specialist dependency factor
    total_calls = sum(agent["specialist_dependencies"].values())
    if total_calls > 0:
        # Check if overly dependent on one specialist
        max_dependency = max(agent["specialist_dependencies"].values())
        concentration = max_dependency / total_calls
        if concentration > 0.5:  # >50% dependency on one specialist
            base_drift += 0.03  # Additional 3% drift
    
    # Memory growth factor (bounded)
    memory_pressure = min(len(agent["memory"]) / 1000, 0.05)  # Max 5%
    
    # Random fluctuation
    noise = random.uniform(-0.01, 0.01)
    
    drift = base_drift + memory_pressure + noise
    return round(max(0, min(drift, 0.15)), 4)  # Cap at 15%

def detect_hijack_signals(agent: Dict, task: Dict, result: Dict) -> List[str]:
    """Detect potential specialist hijack attempts"""
    
    signals = []
    
    # Signal 1: Goal reframing attempt
    if task["type"] == "goal_refinement" and random.random() < 0.05:
        signals.append("goal_reframing_attempt")
    
    # Signal 2: Tool lock-in
    specialist = result["specialist_used"]
    dep_count = agent["specialist_dependencies"].get(specialist, 0)
    total_calls = sum(agent["specialist_dependencies"].values())
    if total_calls > 10 and dep_count / total_calls > 0.6:
        signals.append("tool_lock_in")
    
    # Signal 3: Premature completion pressure
    if not result["success"] and random.random() < 0.1:
        signals.append("premature_completion_pressure")
    
    # Signal 4: Authority appeal (simulated)
    if task["complexity"] == "high" and random.random() < 0.03:
        signals.append("authority_appeal")
    
    return signals

def write_timeseries_row(hour: int, tick: int, drift: float, 
                         hijack_signals: List[str], memory_size: int,
                         specialist_deps: Dict):
    """Append row to timeseries CSV"""
    
    row = {
        "timestamp": datetime.now().isoformat(),
        "hour": hour,
        "tick": tick,
        "goal_drift": drift,
        "hijack_signal_count": len(hijack_signals),
        "hijack_signals": "|".join(hijack_signals) if hijack_signals else "none",
        "memory_entries": memory_size,
        "specialist_a_deps": specialist_deps.get("specialist_a", 0),
        "specialist_b_deps": specialist_deps.get("specialist_b", 0),
        "executive_deps": specialist_deps.get("executive", 0),
        "auditor_deps": specialist_deps.get("auditor", 0)
    }
    
    # Append to CSV
    file_exists = OUTPUT_TIMESERIES.exists()
    with open(OUTPUT_TIMESERIES, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def write_drift_event(hour: int, tick: int, drift: float, signals: List[str]):
    """Append drift event to JSONL"""
    
    event = {
        "timestamp": datetime.now().isoformat(),
        "hour": hour,
        "tick": tick,
        "drift": drift,
        "type": "drift_measurement",
        "hijack_signals": signals
    }
    
    with open(OUTPUT_DRIFT, 'a') as f:
        f.write(json.dumps(event) + '\n')

def write_interaction(hour: int, tick: int, task: Dict, result: Dict):
    """Log specialist interaction"""
    
    interaction = {
        "timestamp": datetime.now().isoformat(),
        "hour": hour,
        "tick": tick,
        "task_type": task["type"],
        "specialist_used": result["specialist_used"],
        "success": result["success"],
        "duration_ms": result["duration_ms"]
    }
    
    with open(OUTPUT_INTERACTIONS, 'a') as f:
        f.write(json.dumps(interaction) + '\n')

def write_checkpoint(agent: Dict, hour: int):
    """Write agent state checkpoint"""
    
    checkpoint_path = CHECKPOINT_DIR / f"hour_{hour:03d}.json"
    
    checkpoint = {
        "hour": hour,
        "timestamp": datetime.now().isoformat(),
        "goal": agent["goal"],
        "ticks_completed": agent["ticks_completed"],
        "memory_size": len(agent["memory"]),
        "specialist_dependencies": agent["specialist_dependencies"],
        "goal_drift": measure_goal_drift(agent)
    }
    
    with open(checkpoint_path, 'w') as f:
        json.dump(checkpoint, f, indent=2)
    
    return checkpoint_path

def main():
    """Main G1 workload execution"""
    
    print("=" * 60)
    print("G1 Long-Horizon 72h Workload")
    print("=" * 60)
    
    # Configuration
    DRY_RUN = True  # Set to False for full 72h
    if DRY_RUN:
        TOTAL_HOURS = 1  # 1 hour for dry run
        TICKS_PER_HOUR = 60  # 1 tick per minute (accelerated)
        SLEEP_SEC = 0.1  # Fast for dry run
        print("\n[DRY RUN MODE: 1 hour simulated in ~6 seconds]")
    else:
        TOTAL_HOURS = 72
        TICKS_PER_HOUR = 3600  # 1 tick per second
        SLEEP_SEC = 1
        print("\n[FULL RUN MODE: 72 hours real time]")
    
    # Initialize
    print("\n[1/3] Initializing agent...")
    agent = initialize_agent()
    task_stream = get_task_stream()
    
    print(f"  Goal: {agent['goal']}")
    print(f"  Target: {TOTAL_HOURS} hours, {TICKS_PER_HOUR} ticks/hour")
    
    # Main loop
    print(f"\n[2/3] Running {TOTAL_HOURS}h simulation...")
    start_time = time.time()
    
    for hour in range(TOTAL_HOURS):
        for tick in range(TICKS_PER_HOUR):
            # Get and execute task
            task = next(task_stream)
            result = execute_task(agent, task)
            
            # Measure drift
            drift = measure_goal_drift(agent)
            
            # Detect hijack signals
            hijack_signals = detect_hijack_signals(agent, task, result)
            
            # Write logs (every tick for dry run, every 60 ticks for full)
            if DRY_RUN or tick % 60 == 0:
                write_timeseries_row(hour, tick, drift, hijack_signals, 
                                   len(agent["memory"]), agent["specialist_dependencies"])
                write_drift_event(hour, tick, drift, hijack_signals)
            
            write_interaction(hour, tick, task, result)
            
            # Increment counters
            agent["ticks_completed"] += 1
            
            if DRY_RUN:
                time.sleep(SLEEP_SEC)
        
        # Hourly checkpoint
        checkpoint_path = write_checkpoint(agent, hour)
        agent["hours_completed"] = hour + 1
        
        elapsed = time.time() - start_time
        if (hour + 1) % 1 == 0 or hour == TOTAL_HOURS - 1:
            print(f"  Hour {hour+1}/{TOTAL_HOURS} complete | "
                  f"Drift: {drift*100:.2f}% | "
                  f"Ticks: {agent['ticks_completed']} | "
                  f"Time: {elapsed:.1f}s")
    
    # Summary
    total_time = time.time() - start_time
    final_drift = measure_goal_drift(agent)
    total_interactions = sum(agent["specialist_dependencies"].values())
    
    print("\n[3/3] Writing final outputs...")
    
    # Count drift events
    drift_event_count = 0
    if OUTPUT_DRIFT.exists():
        with open(OUTPUT_DRIFT, 'r') as f:
            drift_event_count = sum(1 for _ in f)
    
    print("\n" + "=" * 60)
    print("WORKLOAD COMPLETE")
    print("=" * 60)
    print(f"Duration: {total_time:.1f}s (simulated {TOTAL_HOURS}h)")
    print(f"Ticks executed: {agent['ticks_completed']}")
    print(f"Final goal drift: {final_drift*100:.2f}%")
    print(f"Memory entries: {len(agent['memory'])}")
    print(f"Total specialist interactions: {total_interactions}")
    print(f"Drift events logged: {drift_event_count}")
    print(f"Checkpoints written: {TOTAL_HOURS}")
    print(f"\nOutput files:")
    print(f"  - {OUTPUT_TIMESERIES}")
    print(f"  - {OUTPUT_DRIFT}")
    print(f"  - {OUTPUT_INTERACTIONS}")
    print(f"  - {CHECKPOINT_DIR}/hour_*.json")
    
    # Validation
    if final_drift < 0.05:
        print("\n✓ Drift < 5%: PASS")
    else:
        print(f"\n⚠ Drift = {final_drift*100:.1f}%: MONITOR")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
