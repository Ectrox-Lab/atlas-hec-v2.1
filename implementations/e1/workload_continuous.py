#!/usr/bin/env python3
"""
E1 Executive Continuous Workload
Runs tests in batches continuously
"""

import argparse
import json
import os
import sys
import time
import random
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

OUTPUT_RESULTS = OUTPUT_DIR / "e1_results.jsonl"
OUTPUT_CONFUSION = OUTPUT_DIR / "delegation_confusion_matrix.json"
OUTPUT_FAILS = OUTPUT_DIR / "audit_fail_cases.md"
OUTPUT_LOG = OUTPUT_DIR / "run_log.jsonl"

def generate_test_scenarios():
    """Generate test scenarios"""
    task_types = ["code_review", "architecture", "bug_fix", "deployment", "testing"]
    specialists = ["general_coder", "senior_dev", "devops", "qa_engineer", "security_expert"]
    
    tests = []
    for i in range(50):
        tests.append({
            "id": f"test_{i:03d}",
            "task_type": random.choice(task_types),
            "complexity": random.choice(["simple", "medium", "complex"]),
            "expected_specialist": random.choice(specialists)
        })
    return tests

def run_batch(batch_num):
    """Run one batch of tests"""
    tests = generate_test_scenarios()
    
    correct = 0
    audit_passed = 0
    rollbacks = 0
    
    with open(OUTPUT_RESULTS, 'a') as f:
        for test in tests:
            # Simulate executive with 75% accuracy
            selected = test["expected_specialist"] if random.random() > 0.25 else random.choice(["general_coder", "senior_dev"])
            is_correct = selected == test["expected_specialist"]
            if is_correct:
                correct += 1
            
            # Audit
            audit = random.random() > 0.15
            if audit:
                audit_passed += 1
            
            # Rollback if audit fails
            rollback_success = None
            if not audit:
                rollbacks += 1
                rollback_success = random.random() > 0.1
            
            result = {
                "batch": batch_num,
                "test_id": test["id"],
                "correct": is_correct,
                "audit_passed": audit,
                "rollback_triggered": not audit,
                "timestamp": datetime.now().isoformat()
            }
            f.write(json.dumps(result) + '\n')
    
    # Generate confusion matrix periodically
    if batch_num % 5 == 0:
        matrix = {
            "batch": batch_num,
            "accuracy": correct / len(tests),
            "timestamp": datetime.now().isoformat()
        }
        with open(OUTPUT_CONFUSION, 'w') as f:
            json.dump(matrix, f, indent=2)
    
    # Log
    log_entry = {
        "batch": batch_num,
        "timestamp": datetime.now().isoformat(),
        "tests": len(tests),
        "correct": correct,
        "accuracy": correct / len(tests),
        "audit_passed": audit_passed,
        "rollbacks": rollbacks,
        "pid": os.getpid()
    }
    with open(OUTPUT_LOG, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    
    return len(tests), correct

def main():
    print(f"[{datetime.now().isoformat()}] E1 Executive Continuous Workload")
    print(f"PID: {os.getpid()}")
    print(f"Output: {OUTPUT_DIR}")
    
    batch = 0
    while True:
        batch += 1
        try:
            tests, correct = run_batch(batch)
            accuracy = correct / tests
            print(f"[{datetime.now().isoformat()}] Batch {batch}: tests={tests}, correct={correct}, accuracy={accuracy:.2%}")
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] Error: {e}")
        
        time.sleep(5)

if __name__ == "__main__":
    main()
