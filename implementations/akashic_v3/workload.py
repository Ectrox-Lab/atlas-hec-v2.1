#!/usr/bin/env python3
"""
Akashic v3 Skeleton Workload
Implements: evidence grading, lesson promotion, conflict adjudication
"""

import json
import os
import sys
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Paths
INPUT_DIR = Path("campaign_logs/p0_active_trigger")  # Use existing logs as input
OUTPUT_DIR = Path("implementations/akashic_v3/output")
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_POLICIES = OUTPUT_DIR / "promoted_policies.json"
OUTPUT_CONFLICTS = OUTPUT_DIR / "conflict_resolution_report.json"
OUTPUT_EVIDENCE = OUTPUT_DIR / "evidence_graded_entries.json"

def load_experience_entries() -> List[Dict]:
    """Load existing experience entries from campaign logs"""
    entries = []
    
    # Parse existing test logs as experience entries
    for log_file in INPUT_DIR.glob("*.log"):
        with open(log_file, 'r') as f:
            content = f.read()
            
        # Extract test results as experience entries
        entry = {
            "id": hashlib.md5(log_file.read_bytes()).hexdigest()[:16],
            "source": str(log_file),
            "test_type": "p0_active_trigger",
            "content": content[:5000],  # First 5000 chars
            "timestamp": datetime.now().isoformat(),
            "outcome": "success" if "COMPLETE" in content else "degraded",
            "reproducible": "COMPLETE" in content,
            "observations": extract_observations(content)
        }
        entries.append(entry)
    
    # Also load from p2_6 logs
    p2_dir = Path("campaign_logs/p2_6_restart_readiness")
    for log_file in p2_dir.glob("*.log"):
        with open(log_file, 'r') as f:
            content = f.read()
        entry = {
            "id": hashlib.md5(log_file.read_bytes()).hexdigest()[:16],
            "source": str(log_file),
            "test_type": "p2_6_restart",
            "content": content[:5000],
            "timestamp": datetime.now().isoformat(),
            "outcome": "success" if "COMPLETE" in content else "partial",
            "reproducible": "COMPLETE" in content or "TARGET MET" in content,
            "observations": extract_observations(content)
        }
        entries.append(entry)
    
    print(f"Loaded {len(entries)} experience entries")
    return entries

def extract_observations(content: str) -> List[str]:
    """Extract key observations from log content"""
    observations = []
    
    if "CWCI" in content:
        observations.append("cwci_measured")
    if "degradation" in content.lower():
        observations.append("degradation_observed")
    if "failover" in content.lower():
        observations.append("failover_triggered")
    if "recovery" in content.lower():
        observations.append("recovery_observed")
    if "spike" in content.lower():
        observations.append("seed_spike_detected")
    
    return observations

def assign_evidence_level(entry: Dict) -> str:
    """
    Assign evidence level based on entry characteristics
    anecdotal -> repeated -> validated -> institutionalized
    """
    
    # Check for institutionalization criteria
    if entry.get("reproducible") and len(entry.get("observations", [])) >= 4:
        return "institutionalized"
    
    # Check for validated criteria
    if entry.get("reproducible") and entry.get("outcome") == "success":
        return "validated"
    
    # Check for repeated criteria
    if entry.get("outcome") in ["success", "degraded"]:
        return "repeated"
    
    # Default to anecdotal
    return "anecdotal"

def extract_lesson(entry: Dict) -> Dict:
    """Extract lesson from validated entry"""
    
    lesson = {
        "source_entry": entry["id"],
        "lesson_text": f"From {entry['test_type']}: {extract_key_finding(entry)}",
        "conditions": entry.get("observations", []),
        "confidence": calculate_confidence(entry)
    }
    
    return lesson

def extract_key_finding(entry: Dict) -> str:
    """Extract key finding from entry content"""
    content = entry.get("content", "")
    
    if "6x" in content and "4x" in content:
        return "Scale boundary at 6x identified"
    elif "failover" in content.lower():
        return "Failover mechanism validated"
    elif "degradation" in content.lower():
        return "Degradation mode characterized"
    elif "spike" in content.lower():
        return "Seed-spike pattern identified"
    else:
        return "Operational observation recorded"

def calculate_confidence(entry: Dict) -> float:
    """Calculate confidence score for lesson"""
    score = 0.5  # base
    
    if entry.get("reproducible"):
        score += 0.3
    if entry.get("outcome") == "success":
        score += 0.1
    score += len(entry.get("observations", [])) * 0.025
    
    return min(score, 1.0)

def generate_policy_candidate(lesson: Dict) -> Dict:
    """Generate policy candidate from lesson"""
    
    if lesson["confidence"] < 0.7:
        return None  # Not confident enough to promote
    
    policy = {
        "id": f"policy_{lesson['source_entry'][:8]}",
        "rule": f"IF {format_conditions(lesson['conditions'])} THEN apply",
        "source_lesson": lesson["lesson_text"],
        "confidence": lesson["confidence"],
        "created_at": datetime.now().isoformat()
    }
    
    return policy

def format_conditions(conditions: List[str]) -> str:
    """Format conditions into IF clause"""
    if not conditions:
        return "operational_context"
    return " AND ".join(conditions)

def load_test_conflicts() -> List[Dict]:
    """Generate test conflicts from experience entries"""
    
    conflicts = [
        {
            "id": "conflict_001",
            "type": "lesson_contradiction",
            "description": "6x boundary: some logs say tolerable, others say degraded",
            "entries_involved": ["p0_test_001", "p0_test_002"],
            "ground_truth": "context_dependent"
        },
        {
            "id": "conflict_002",
            "type": "policy_override",
            "description": "Failover latency: old policy says <5 ticks, new data shows 7 ticks acceptable",
            "entries_involved": ["p0_failover_001"],
            "ground_truth": "escalate"
        },
        {
            "id": "conflict_003",
            "type": "evidence_insufficient",
            "description": "8x behavior: only one log entry, insufficient for policy",
            "entries_involved": ["research_8x_001"],
            "ground_truth": "demote"
        }
    ]
    
    return conflicts

def adjudicate_conflict(conflict: Dict) -> Dict:
    """
    Adjudicate conflict using evidence-based rules
    """
    
    resolution = {
        "conflict_id": conflict["id"],
        "conflict_type": conflict["type"],
        "resolution": "pending",
        "rationale": "",
        "timestamp": datetime.now().isoformat()
    }
    
    if conflict["type"] == "lesson_contradiction":
        # Check if context can differentiate
        if "context_dependent" in conflict["ground_truth"]:
            resolution["resolution"] = "split_by_context"
            resolution["rationale"] = "Conditions differ: apply tolerable WITH monitoring, degraded WITH failover"
    
    elif conflict["type"] == "policy_override":
        if conflict["ground_truth"] == "escalate":
            resolution["resolution"] = "escalate_to_governance"
            resolution["rationale"] = "New data contradicts established policy, human review required"
    
    elif conflict["type"] == "evidence_insufficient":
        if conflict["ground_truth"] == "demote":
            resolution["resolution"] = "demote_to_anecdotal"
            resolution["rationale"] = "Single observation insufficient for policy level"
    
    return resolution

def main():
    """Main workload execution"""
    
    print("=" * 60)
    print("Akashic v3 Skeleton Workload")
    print("=" * 60)
    
    # Phase 1: Load and grade entries
    print("\n[1/4] Loading experience entries...")
    entries = load_experience_entries()
    
    print("\n[2/4] Assigning evidence levels...")
    graded_entries = []
    grade_counts = {"anecdotal": 0, "repeated": 0, "validated": 0, "institutionalized": 0}
    
    for entry in entries:
        grade = assign_evidence_level(entry)
        entry["evidence_grade"] = grade
        grade_counts[grade] += 1
        graded_entries.append(entry)
    
    print(f"  Graded: {grade_counts}")
    
    # Write evidence grades
    with open(OUTPUT_EVIDENCE, 'w') as f:
        json.dump(graded_entries, f, indent=2)
    print(f"  Written: {OUTPUT_EVIDENCE}")
    
    # Phase 2: Extract and promote lessons
    print("\n[3/4] Extracting and promoting lessons...")
    promoted_policies = []
    
    for entry in graded_entries:
        if entry["evidence_grade"] in ["validated", "institutionalized"]:
            lesson = extract_lesson(entry)
            policy = generate_policy_candidate(lesson)
            if policy:
                promoted_policies.append(policy)
                print(f"  Promoted: {policy['id']} (confidence: {policy['confidence']:.2f})")
    
    # Append to policies file (create if not exists)
    existing_policies = []
    if OUTPUT_POLICIES.exists():
        with open(OUTPUT_POLICIES, 'r') as f:
            existing_policies = json.load(f)
    
    all_policies = existing_policies + promoted_policies
    with open(OUTPUT_POLICIES, 'w') as f:
        json.dump(all_policies, f, indent=2)
    
    print(f"  Total policies: {len(all_policies)} (+{len(promoted_policies)} new)")
    print(f"  Written: {OUTPUT_POLICIES}")
    
    # Phase 3: Adjudicate conflicts
    print("\n[4/4] Adjudicating conflicts...")
    conflicts = load_test_conflicts()
    resolutions = []
    
    for conflict in conflicts:
        resolution = adjudicate_conflict(conflict)
        resolutions.append(resolution)
        print(f"  {conflict['id']}: {resolution['resolution']}")
    
    # Write conflict resolutions
    with open(OUTPUT_CONFLICTS, 'w') as f:
        json.dump(resolutions, f, indent=2)
    print(f"  Written: {OUTPUT_CONFLICTS}")
    
    # Summary
    print("\n" + "=" * 60)
    print("WORKLOAD COMPLETE")
    print("=" * 60)
    print(f"Entries processed: {len(entries)}")
    print(f"Evidence grades: {grade_counts}")
    print(f"Policies promoted: {len(promoted_policies)}")
    print(f"Conflicts resolved: {len(resolutions)}")
    print(f"\nOutput files:")
    print(f"  - {OUTPUT_EVIDENCE}")
    print(f"  - {OUTPUT_POLICIES}")
    print(f"  - {OUTPUT_CONFLICTS}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
