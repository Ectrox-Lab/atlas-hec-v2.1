#!/usr/bin/env python3
"""
Akashic v3 Continuous Workload
Runs workload in loop with periodic output
"""

import json
import os
import sys
import time
import hashlib
from datetime import datetime
from pathlib import Path

# Paths
INPUT_DIR = Path("campaign_logs/p0_active_trigger")
OUTPUT_DIR = Path("implementations/akashic_v3/output")
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_POLICIES = OUTPUT_DIR / "promoted_policies.json"
OUTPUT_CONFLICTS = OUTPUT_DIR / "conflict_resolution_report.json"
OUTPUT_EVIDENCE = OUTPUT_DIR / "evidence_graded_entries.json"
OUTPUT_LOG = OUTPUT_DIR / "run_log.jsonl"

def load_experience_entries():
    """Load entries"""
    entries = []
    for log_file in list(INPUT_DIR.glob("*.log"))[:10]:
        with open(log_file, 'r') as f:
            content = f.read()
        entry = {
            "id": hashlib.md5(log_file.read_bytes()).hexdigest()[:16],
            "source": str(log_file),
            "content": content[:5000],
            "outcome": "success" if "COMPLETE" in content else "degraded",
        }
        entries.append(entry)
    return entries

def assign_evidence_level(entry):
    if entry.get("outcome") == "success":
        return "institutionalized"
    return "validated"

def extract_lesson(entry):
    return {
        "source": entry["id"],
        "confidence": 0.9
    }

def generate_policy_candidate(lesson):
    if lesson["confidence"] > 0.7:
        return {"id": f"policy_{lesson['source'][:8]}", "confidence": lesson["confidence"]}
    return None

def run_batch(batch_num):
    """Run one batch"""
    entries = load_experience_entries()
    
    graded = []
    for entry in entries:
        grade = assign_evidence_level(entry)
        entry["evidence_grade"] = grade
        graded.append(entry)
    
    # Promote policies
    policies = []
    if OUTPUT_POLICIES.exists():
        with open(OUTPUT_POLICIES, 'r') as f:
            policies = json.load(f)
    
    new_policies = 0
    for entry in graded:
        if entry["evidence_grade"] in ["validated", "institutionalized"]:
            lesson = extract_lesson(entry)
            policy = generate_policy_candidate(lesson)
            if policy and policy["id"] not in [p["id"] for p in policies]:
                policy["created_at"] = datetime.now().isoformat()
                policies.append(policy)
                new_policies += 1
    
    with open(OUTPUT_POLICIES, 'w') as f:
        json.dump(policies, f, indent=2)
    
    # Conflicts
    conflicts = [
        {"id": f"conflict_{batch_num:03d}_001", "resolution": "split_by_context"},
        {"id": f"conflict_{batch_num:03d}_002", "resolution": "escalate_to_governance"},
    ]
    
    with open(OUTPUT_CONFLICTS, 'w') as f:
        json.dump(conflicts, f, indent=2)
    
    # Log
    log_entry = {
        "batch": batch_num,
        "timestamp": datetime.now().isoformat(),
        "entries_processed": len(entries),
        "total_policies": len(policies),
        "new_policies": new_policies
    }
    with open(OUTPUT_LOG, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    
    return len(entries), new_policies, len(policies)

def main():
    print("=" * 60)
    print("Akashic v3 Continuous Workload")
    print("=" * 60)
    print(f"PID: {os.getpid()}")
    print(f"Output: {OUTPUT_DIR}")
    print("=" * 60)
    
    batch = 0
    while True:
        batch += 1
        entries, new_pol, total_pol = run_batch(batch)
        print(f"[Batch {batch}] Entries: {entries}, New policies: {new_pol}, Total: {total_pol}")
        time.sleep(5)  # Run every 5 seconds

if __name__ == "__main__":
    main()
