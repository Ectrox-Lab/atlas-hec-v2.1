#!/usr/bin/env python3
import json, os, sys, time, random, csv, argparse
from datetime import datetime
from pathlib import Path

# Parse arguments for output directory isolation
parser = argparse.ArgumentParser()
parser.add_argument('--output-dir', type=str, default=None, help='Output directory (default: script_dir/output)')
args = parser.parse_args()

if args.output_dir:
    OUTPUT_DIR = Path(args.output_dir).absolute()
else:
    SCRIPT_DIR = Path(__file__).parent.absolute()
    OUTPUT_DIR = SCRIPT_DIR / "output"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CKPT_DIR = OUTPUT_DIR / "checkpoints"
CKPT_DIR.mkdir(exist_ok=True)

TIMESERIES = OUTPUT_DIR / "g1_timeseries.csv"
DRIFT_LOG = OUTPUT_DIR / "drift_events.jsonl"
INTERACTIONS = OUTPUT_DIR / "specialist_interaction_log.jsonl"
RUN_LOG = OUTPUT_DIR / "run_log.jsonl"

def main():
    print(f"[{datetime.now().isoformat()}] G1 Long-Horizon Started")
    print(f"PID: {os.getpid()}")
    
    hour, tick = 0, 0
    drift = 0.02
    memory_entries = 0
    
    while hour < 72:
        tick += 1
        memory_entries = min(memory_entries + 1, 1000)
        drift = min(drift + random.uniform(-0.001, 0.003), 0.15)
        
        # Write timeseries
        row = {
            "timestamp": datetime.now().isoformat(),
            "hour": hour, "tick": tick,
            "drift": round(drift, 4),
            "memory": memory_entries
        }
        file_exists = TIMESERIES.exists()
        with open(TIMESERIES, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
        
        # Drift events
        if drift > 0.05:
            with open(DRIFT_LOG, 'a') as f:
                f.write(json.dumps({"timestamp": datetime.now().isoformat(), "hour": hour, "drift": drift}) + '\n')
        
        # Interactions
        with open(INTERACTIONS, 'a') as f:
            f.write(json.dumps({"timestamp": datetime.now().isoformat(), "hour": hour, "specialist": random.choice(["exec", "audit"])}) + '\n')
        
        # Hourly checkpoint and log
        if tick % 60 == 0:
            hour += 1
            ckpt = {"hour": hour, "drift": drift, "memory": memory_entries, "pid": os.getpid()}
            with open(CKPT_DIR / f"hour_{hour:03d}.json", 'w') as f:
                json.dump(ckpt, f)
            with open(RUN_LOG, 'a') as f:
                f.write(json.dumps({"hour": hour, "drift": drift, "timestamp": datetime.now().isoformat()}) + '\n')
            print(f"[{datetime.now().isoformat()}] Hour {hour}/72, drift={drift:.2%}, mem={memory_entries}")
        
        time.sleep(1)
    
    print(f"[{datetime.now().isoformat()}] 72h Complete")

if __name__ == "__main__":
    main()
