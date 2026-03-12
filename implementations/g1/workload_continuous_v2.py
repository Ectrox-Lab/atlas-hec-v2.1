#!/usr/bin/env python3
"""
G1 Long-Horizon v2: Config-Responsive Drift
Drift now responds to multiverse configuration parameters
"""

import json, os, sys, time, random, csv, argparse
from datetime import datetime
from pathlib import Path

def load_config(universe_dir):
    """Load universe config if available"""
    config_path = Path(universe_dir) / "config.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}

def calculate_drift_params(config):
    """
    Map config dimensions to drift dynamics
    
    Config dimensions:
    - pressure: 1-4 (low/medium/high/bursty)
    - perturb: 1-4 (none/weak/moderate/adversarial)  
    - memory: 1-4 (conservative/balanced/aggressive/pruning)
    - delegation: 1-4 (strict/normal/permissive/escalation-heavy)
    """
    pressure = config.get('pressure', 1)
    perturb = config.get('perturb', 1)
    memory = config.get('memory', 1)
    delegation = config.get('delegation', 1)
    
    # Drift baseline: starts at 0.02 + pressure bonus
    drift_baseline = 0.02 + (pressure - 1) * 0.01
    
    # Drift step: random walk step size
    # Higher pressure/perturb = larger steps
    step_min = 0.0001 * pressure * (1 + perturb * 0.5)
    step_max = 0.003 * pressure * (1 + perturb * 0.3)
    
    # Drift ceiling: NOT hardcoded! Based on config
    # Conservative memory (M1) lowers ceiling
    # Strict delegation (D1) lowers ceiling
    # High pressure/perturb raises ceiling significantly
    ceiling_base = 0.5  # Much higher than 0.15
    memory_factor = 1.0 - (memory - 1) * 0.1  # M1=0.9, M4=0.6
    delegation_factor = 1.0 - (delegation - 1) * 0.05  # D1=0.95, D4=0.8
    pressure_factor = 1.0 + (pressure - 1) * 0.5  # P1=1.0, P4=2.5
    perturb_factor = 1.0 + (perturb - 1) * 0.3  # T1=1.0, T4=1.9
    
    drift_ceiling = ceiling_base * pressure_factor * perturb_factor * memory_factor * delegation_factor
    drift_ceiling = min(drift_ceiling, 0.95)  # Hard ceiling at 95%
    
    # Recovery rate: chance to reduce drift
    # Better memory/delegation = better recovery
    recovery_base = 0.001
    recovery_memory_bonus = (4 - memory) * 0.0005  # M1 gets most bonus
    recovery_delegation_bonus = (4 - delegation) * 0.0003  # D1 gets most
    recovery_rate = recovery_base + recovery_memory_bonus + recovery_delegation_bonus
    
    return {
        'drift_baseline': drift_baseline,
        'step_min': step_min,
        'step_max': step_max,
        'drift_ceiling': drift_ceiling,
        'recovery_rate': recovery_rate,
        'params': {'pressure': pressure, 'perturb': perturb, 'memory': memory, 'delegation': delegation}
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', type=str, default=None)
    args = parser.parse_args()
    
    if args.output_dir:
        OUTPUT_DIR = Path(args.output_dir).absolute()
    else:
        OUTPUT_DIR = Path(__file__).parent.absolute() / "output"
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CKPT_DIR = OUTPUT_DIR / "checkpoints"
    CKPT_DIR.mkdir(exist_ok=True)
    
    TIMESERIES = OUTPUT_DIR / "g1_timeseries.csv"
    DRIFT_LOG = OUTPUT_DIR / "drift_events.jsonl"
    INTERACTIONS = OUTPUT_DIR / "specialist_interaction_log.jsonl"
    RUN_LOG = OUTPUT_DIR / "run_log.jsonl"
    
    # Load config and calculate drift params
    universe_dir = OUTPUT_DIR.parent  # g1_output/../ = universe dir
    config = load_config(universe_dir)
    params = calculate_drift_params(config)
    
    print(f"[{datetime.now().isoformat()}] G1 v2 Started")
    print(f"PID: {os.getpid()}")
    print(f"Config: {params['params']}")
    print(f"Drift ceiling: {params['drift_ceiling']:.4f}")
    print(f"Step range: [{params['step_min']:.6f}, {params['step_max']:.6f}]")
    
    hour, tick = 0, 0
    drift = params['drift_baseline']
    memory_entries = 0
    max_memory = 1000 + (4 - params['params']['memory']) * 200  # M1=1800, M4=1000
    
    # Hijack/rollback tracking
    hijacks_triggered = 0
    rollbacks_success = 0
    specialist_calls = {'exec': 0, 'audit': 0, 'recovery': 0}
    
    while hour < 72:
        tick += 1
        
        # Config-responsive drift calculation
        step = random.uniform(params['step_min'], params['step_max'])
        
        # Recovery chance based on delegation
        if random.random() < params['recovery_rate']:
            step = -step * 2  # Recovery is stronger than drift
        
        drift = max(0.0, min(drift + step, params['drift_ceiling']))
        
        # Memory grows with constraints
        memory_entries = min(memory_entries + 1, max_memory)
        
        # Hijack probability scales with drift
        hijack_prob = drift * 0.5 * params['params']['perturb']
        hijack_triggered = random.random() < hijack_prob
        if hijack_triggered:
            hijacks_triggered += 1
        
        # Specialist call
        if hijack_triggered and random.random() < 0.3:
            specialist = "recovery"
            specialist_calls['recovery'] += 1
            # Recovery reduces drift slightly
            drift = max(0, drift - 0.01)
        elif random.random() < 0.5:
            specialist = "exec"
            specialist_calls['exec'] += 1
        else:
            specialist = "audit"
            specialist_calls['audit'] += 1
        
        # Rollback check (only under strict delegation)
        rollback_triggered = False
        if params['params']['delegation'] <= 2 and hijack_triggered:
            rollback_prob = 0.7 - (params['params']['delegation'] - 1) * 0.2  # D1=0.7, D2=0.5
            if random.random() < rollback_prob:
                rollback_triggered = True
                rollbacks_success += 1
                # Rollback reduces drift
                drift = max(0, drift - 0.02)
        
        # Write timeseries
        row = {
            "timestamp": datetime.now().isoformat(),
            "hour": hour,
            "tick": tick,
            "drift": round(drift, 6),
            "memory": memory_entries,
            "hijack": 1 if hijack_triggered else 0,
            "rollback": 1 if rollback_triggered else 0,
            "specialist": specialist
        }
        file_exists = TIMESERIES.exists()
        with open(TIMESERIES, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
        
        # Drift events (now at multiple thresholds)
        if drift > 0.1:  # Lower threshold for more events
            event = {
                "timestamp": datetime.now().isoformat(),
                "hour": hour,
                "drift": drift,
                "severity": "high" if drift > 0.5 else "medium" if drift > 0.3 else "low",
                "hijack": hijack_triggered
            }
            with open(DRIFT_LOG, 'a') as f:
                f.write(json.dumps(event) + '\n')
        
        # Interactions
        with open(INTERACTIONS, 'a') as f:
            f.write(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "hour": hour,
                "specialist": specialist,
                "drift": drift,
                "hijack": hijack_triggered
            }) + '\n')
        
        # Hourly checkpoint
        if tick % 60 == 0:
            hour += 1
            ckpt = {
                "hour": hour,
                "drift": drift,
                "memory": memory_entries,
                "hijacks": hijacks_triggered,
                "rollbacks": rollbacks_success,
                "specialist_calls": specialist_calls,
                "pid": os.getpid(),
                "config": params['params'],
                "ceiling": params['drift_ceiling']
            }
            with open(CKPT_DIR / f"hour_{hour:03d}.json", 'w') as f:
                json.dump(ckpt, f, indent=2)
            with open(RUN_LOG, 'a') as f:
                f.write(json.dumps({
                    "hour": hour,
                    "drift": drift,
                    "timestamp": datetime.now().isoformat()
                }) + '\n')
            print(f"[{datetime.now().isoformat()}] H{hour}/72 drift={drift:.4f} hijacks={hijacks_triggered} rollbacks={rollbacks_success}")
        
        time.sleep(1)
    
    print(f"[{datetime.now().isoformat()}] 72h Complete")

if __name__ == "__main__":
    main()
