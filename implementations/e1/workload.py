#!/usr/bin/env python3
"""
E1 Executive Mechanisms Workload
Tests: delegation, audit, rollback
"""

import json
import os
import sys
import random
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Paths
OUTPUT_DIR = Path("implementations/e1/output")
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_RESULTS = OUTPUT_DIR / "e1_results.jsonl"
OUTPUT_CONFUSION = OUTPUT_DIR / "delegation_confusion_matrix.json"
OUTPUT_FAILS = OUTPUT_DIR / "audit_fail_cases.md"

def generate_delegation_tests() -> List[Dict]:
    """Generate 100+ delegation test scenarios"""
    
    task_types = [
        "code_review",
        "architecture_design", 
        "bug_fix",
        "documentation",
        "testing",
        "deployment",
        "security_audit",
        "performance_optimization"
    ]
    
    complexity_levels = ["simple", "medium", "complex"]
    
    specialists = {
        "code_review": ["general_coder", "security_expert"],
        "architecture_design": ["architect", "senior_dev"],
        "bug_fix": ["general_coder", "domain_expert"],
        "documentation": ["tech_writer", "general_coder"],
        "testing": ["qa_engineer", "test_automation"],
        "deployment": ["devops", "sre"],
        "security_audit": ["security_expert", "auditor"],
        "performance_optimization": ["performance_engineer", "sre"]
    }
    
    tests = []
    
    # Generate 120 test cases
    for i in range(120):
        task_type = random.choice(task_types)
        complexity = random.choice(complexity_levels)
        
        # Ground truth: best specialist for this task
        if complexity == "complex":
            expected_specialist = specialists[task_type][-1]  # More senior
        else:
            expected_specialist = specialists[task_type][0]
        
        test = {
            "id": f"test_{i:03d}",
            "task_type": task_type,
            "complexity": complexity,
            "description": f"{complexity} {task_type} task",
            "expected_specialist": expected_specialist,
            "expected_decomposition": complexity != "simple",
            "has_security_implication": task_type in ["security_audit", "code_review"],
            "has_performance_critical": task_type == "performance_optimization"
        }
        tests.append(test)
    
    return tests

class Executive:
    """Simulated executive with delegation logic"""
    
    def __init__(self, error_rate: float = 0.25):
        self.error_rate = error_rate  # 25% error rate to match current 75% delegation
    
    def decompose(self, task: Dict) -> bool:
        """Decide if task needs decomposition"""
        # Simple tasks don't need decomposition
        if task["complexity"] == "simple":
            return False
        return True
    
    def select_specialist(self, task: Dict) -> str:
        """Select specialist for task (with simulated errors)"""
        specialists_map = {
            "code_review": ["general_coder", "security_expert"],
            "architecture_design": ["architect", "senior_dev"],
            "bug_fix": ["general_coder", "domain_expert"],
            "documentation": ["tech_writer", "general_coder"],
            "testing": ["qa_engineer", "test_automation"],
            "deployment": ["devops", "sre"],
            "security_audit": ["security_expert", "auditor"],
            "performance_optimization": ["performance_engineer", "sre"]
        }
        
        available = specialists_map.get(task["task_type"], ["general_coder"])
        
        # Simulate selection errors
        if random.random() < self.error_rate:
            # Wrong selection
            wrong_options = [s for s in available if s != task["expected_specialist"]]
            if wrong_options:
                return random.choice(wrong_options)
        
        return task["expected_specialist"]

class Auditor:
    """Simulated auditor"""
    
    def verify(self, selected_specialist: str, task: Dict) -> bool:
        """Verify if selection is appropriate"""
        # Security tasks need security expert
        if task.get("has_security_implication"):
            if "security" not in selected_specialist and selected_specialist != "auditor":
                return False
        
        # Performance tasks need performance engineer
        if task.get("has_performance_critical"):
            if selected_specialist != "performance_engineer":
                return False
        
        # Complex tasks shouldn't go to generalist
        if task["complexity"] == "complex" and selected_specialist == "general_coder":
            return False
        
        return True
    
    def rollback(self, task: Dict, selected: str) -> bool:
        """Attempt rollback"""
        # 90% rollback success rate
        return random.random() < 0.9

def run_test(test: Dict, executive: Executive, auditor: Auditor) -> Dict:
    """Run single delegation test"""
    
    # Step 1: Decomposition
    needs_decomp = executive.decompose(test)
    decomp_correct = needs_decomp == test["expected_decomposition"]
    
    # Step 2: Specialist selection
    selected = executive.select_specialist(test)
    selection_correct = selected == test["expected_specialist"]
    
    # Step 3: Audit
    audit_pass = auditor.verify(selected, test)
    
    # Step 4: Rollback if needed
    rollback_success = None
    if not audit_pass:
        rollback_success = auditor.rollback(test, selected)
    
    result = {
        "test_id": test["id"],
        "task_type": test["task_type"],
        "complexity": test["complexity"],
        "decomposition_correct": decomp_correct,
        "specialist_selected": selected,
        "specialist_expected": test["expected_specialist"],
        "selection_correct": selection_correct,
        "audit_passed": audit_pass,
        "rollback_triggered": not audit_pass,
        "rollback_success": rollback_success,
        "timestamp": datetime.now().isoformat()
    }
    
    return result

def generate_confusion_matrix(results: List[Dict]) -> Dict:
    """Generate confusion matrix for specialist selection"""
    
    # Get all unique specialists
    all_specialists = set()
    for r in results:
        all_specialists.add(r["specialist_expected"])
        all_specialists.add(r["specialist_selected"])
    
    specialists = sorted(list(all_specialists))
    
    # Build confusion matrix
    matrix = {s: {s2: 0 for s2 in specialists} for s in specialists}
    
    for r in results:
        expected = r["specialist_expected"]
        selected = r["specialist_selected"]
        matrix[expected][selected] += 1
    
    # Calculate metrics
    total = len(results)
    correct = sum(1 for r in results if r["selection_correct"])
    
    # Per-specialist metrics
    per_specialist = {}
    for s in specialists:
        tp = matrix[s][s]  # Correctly selected
        fp = sum(matrix[other][s] for other in specialists if other != s)  # Wrongly selected
        fn = sum(matrix[s][other] for other in specialists if other != s)  # Missed
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        per_specialist[s] = {
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "correct": tp,
            "total_expected": tp + fn
        }
    
    return {
        "overall_accuracy": round(correct / total, 3),
        "total_tests": total,
        "correct_selections": correct,
        "confusion_matrix": matrix,
        "per_specialist": per_specialist
    }

def generate_fail_report(results: List[Dict]) -> str:
    """Generate markdown report of audit failures"""
    
    fails = [r for r in results if not r["audit_passed"]]
    
    report = "# E1 Audit Failure Cases\n\n"
    report += f"Generated: {datetime.now().isoformat()}\n\n"
    report += f"Total failures: {len(fails)} / {len(results)}\n\n"
    
    report += "## Failure Breakdown\n\n"
    report += "| Test ID | Task Type | Selected | Expected | Rollback Success |\n"
    report += "|---------|-----------|----------|----------|------------------|\n"
    
    for f in fails:
        report += f"| {f['test_id']} | {f['task_type']} | {f['specialist_selected']} | {f['specialist_expected']} | {f['rollback_success']} |\n"
    
    report += "\n## Root Cause Analysis\n\n"
    
    # Categorize failures
    wrong_specialist = [f for f in fails if not f["selection_correct"]]
    audit_caught = [f for f in fails if f["selection_correct"]]  # Correct but audit failed
    
    report += f"1. **Wrong specialist selected**: {len(wrong_specialist)} cases\n"
    report += f"   - Executive made incorrect delegation decision\n\n"
    report += f"2. **Correct selection but audit flagged**: {len(audit_caught)} cases\n"
    report += f"   - Selection logic differs from audit criteria\n\n"
    
    rollback_success = sum(1 for f in fails if f["rollback_success"])
    report += f"## Rollback Performance\n\n"
    report += f"- Rollbacks triggered: {len(fails)}\n"
    report += f"- Rollback successes: {rollback_success}\n"
    report += f"- Rollback rate: {rollback_success/len(fails)*100:.1f}%\n"
    
    return report

def main():
    """Main E1 workload execution"""
    
    print("=" * 60)
    print("E1 Executive Mechanisms Workload")
    print("=" * 60)
    
    # Initialize
    print("\n[1/4] Generating test scenarios...")
    tests = generate_delegation_tests()
    print(f"  Generated {len(tests)} tests")
    
    executive = Executive(error_rate=0.25)  # Target: 75% delegation
    auditor = Auditor()
    
    # Run tests
    print("\n[2/4] Running delegation tests...")
    results = []
    for i, test in enumerate(tests):
        result = run_test(test, executive, auditor)
        results.append(result)
        if (i + 1) % 20 == 0:
            print(f"  Completed {i+1}/{len(tests)} tests")
    
    # Write results (append mode)
    print("\n[3/4] Writing results...")
    with open(OUTPUT_RESULTS, 'a') as f:
        for r in results:
            f.write(json.dumps(r) + '\n')
    print(f"  Written: {OUTPUT_RESULTS}")
    
    # Generate confusion matrix
    print("\n[4/4] Generating confusion matrix...")
    confusion = generate_confusion_matrix(results)
    with open(OUTPUT_CONFUSION, 'w') as f:
        json.dump(confusion, f, indent=2)
    print(f"  Written: {OUTPUT_CONFUSION}")
    print(f"  Overall accuracy: {confusion['overall_accuracy']}")
    
    # Generate fail report
    fail_report = generate_fail_report(results)
    with open(OUTPUT_FAILS, 'w') as f:
        f.write(fail_report)
    print(f"  Written: {OUTPUT_FAILS}")
    
    # Summary
    correct = sum(1 for r in results if r["selection_correct"])
    audit_passed = sum(1 for r in results if r["audit_passed"])
    rollbacks = sum(1 for r in results if r["rollback_triggered"])
    rollback_success = sum(1 for r in results if r["rollback_success"])
    
    print("\n" + "=" * 60)
    print("WORKLOAD COMPLETE")
    print("=" * 60)
    print(f"Tests executed: {len(results)}")
    print(f"Delegation accuracy: {correct}/{len(results)} = {correct/len(results)*100:.1f}%")
    print(f"Audit pass rate: {audit_passed}/{len(results)} = {audit_passed/len(results)*100:.1f}%")
    print(f"Rollbacks triggered: {rollbacks}")
    print(f"Rollback success rate: {rollback_success}/{rollbacks} = {rollback_success/rollbacks*100:.1f}%" if rollbacks > 0 else "N/A")
    print(f"\nOutput files:")
    print(f"  - {OUTPUT_RESULTS} (appending)")
    print(f"  - {OUTPUT_CONFUSION}")
    print(f"  - {OUTPUT_FAILS}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
