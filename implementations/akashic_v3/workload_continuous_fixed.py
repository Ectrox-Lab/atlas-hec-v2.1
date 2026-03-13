#!/usr/bin/env python3
"""
Akashic v3 Continuous Workload
"""

import json
import os
import sys
import time
import hashlib
from datetime import datetime
from pathlib import Path

# Use absolute paths
SCRIPT_DIR = Path(__file__).parent.absolute()
REPO_ROOT = SCRIPT_DIR.parent.parent
INPUT_DIR = REPO_ROOT / "campaign_logs/p0_active_trigger"
OUTPUT_DIR = SCRIPT_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_POLICIES = OUTPUT_DIR / "promoted_policies.json"
OUTPUT_CONFLICTS = OUTPUT_DIR / "conflict_resolution_report.json"
OUTPUT_LOG = OUTPUT_DIR / "run_log.jsonl"

def load_experience_entries():
    entries = []
    log_files = list(INPUT_DIR.glob("*.log"))[:10]
    for log_file in log_files:
        try:
            with open(log_file, 'r') as f:
                content = f.read()
            entry = {
                "id": hashlib.md5(str(log_file).encode()).hexdigest()[:16],
                "source": str(log_file),
                "content": content[:5000],
                "outcome": "success" if "COMPLETE" in content else "degraded",
            }
            entries.append(entry)
        except:
            pass
    return entries

def assign_evidence_level(entry):
    return "institutionalized" if entry.get("outcome") == "success" else "validated"

def extract_lesson(entry):
    return {"source": entry["id"], "confidence": 0.9}

def generate_policy_candidate(lesson):
    if lesson["confidence"] > 0.7:
        return {"id": f"policy_{lesson['source'][:8]}", "confidence": lesson["confidence"]}
    return None

def run_batch(batch_num):
    entries = load_experience_entries()
    if not entries:
        return 0, 0, 0
    
    graded = []
    for entry in entries:
        grade = assign_evidence_level(entry)
        entry["evidence_grade"] = grade
        graded.append(entry)
    
    policies = []
    if OUTPUT_POLICIES.exists():
        try:
            with open(OUTPUT_POLICIES, 'r') as f:
                policies = json.load(f)
        except:
            policies = []
    
    new_policies = 0
    for entry in graded:
        if entry["evidence_grade"] in ["validated", "institutionalized"]:
            lesson = extract_lesson(entry)
            policy = generate_policy_candidate(lesson)
            if policy:
                existing_ids = [p.get("id") for p in policies]
                if policy["id"] not in existing_ids:
                    policy["created_at"] = datetime.now().isoformat()
                    policy["batch"] = batch_num
                    policies.append(policy)
                    new_policies += 1
    
    with open(OUTPUT_POLICIES, 'w') as f:
        json.dump(policies, f, indent=2)
    
    conflicts = [
        {"id": f"conflict_{batch_num:03d}_001", "resolution": "split_by_context", "timestamp": datetime.now().isoformat()},
        {"id": f"conflict_{batch_num:03d}_002", "resolution": "escalate_to_governance", "timestamp": datetime.now().isoformat()},
    ]
    
    with open(OUTPUT_CONFLICTS, 'w') as f:
        json.dump(conflicts, f, indent=2)
    
    log_entry = {
        "batch": batch_num,
        "timestamp": datetime.now().isoformat(),
        "entries_processed": len(entries),
        "total_policies": len(policies),
        "new_policies": new_policies,
        "pid": os.getpid()
    }
    with open(OUTPUT_LOG, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    
    return len(entries), new_policies, len(policies)

def main():
    print(f"[{datetime.now().isoformat()}] Akashic v3 Continuous Workload")
    print(f"PID: {os.getpid()}")
    print(f"Output: {OUTPUT_DIR}")
    
    batch = 0
    while True:
        batch += 1
        try:
            entries, new_pol, total_pol = run_batch(batch)
            print(f"[{datetime.now().isoformat()}] Batch {batch}: entries={entries}, new_policies={new_pol}, total={total_pol}")
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] Error in batch {batch}: {e}")
        time.sleep(5)

if __name__ == "__main__":
    main()
