#!/usr/bin/env python3
"""
Mainline Phase 2 Sampling - Stratified + Control Families

Sampling rules:
1. Per family: top 2 by Shadow throughput
2. High-frequency families: up to top 3
3. Mandatory inclusion:
   - F_P3T4M4 (target approved family) + extra +1
   - P2/P3-T4 families (gained in Round B)
   - Round A stable families as control
   - At least 1 "suspicious new" family (P1, P4, T5) for leakage test
4. Per seed: minimum 8 representatives
5. Target: 30 candidates per round
"""

import json
import argparse
from pathlib import Path
from collections import defaultdict
import random

# Set seed for reproducibility
random.seed(42)

# Sampling configuration
TARGET_PER_ROUND = 30
MIN_PER_SEED = 8
TOP_PER_FAMILY = 2
TOP_HIGHFREQ_FAMILY = 3

# Mandatory family categories
TARGET_FAMILY = "F_P3T4M4"  # The convergence family
ROUND_B_GAINED = ["F_P2T4M3", "F_P3T4M3", "F_P4T4M3"]  # P2/P3-T4 families
ROUND_A_STABLE = ["F_P3T3M2", "F_P3T3M4", "F_P2T3M4", "F_P2T4M2"]  # Control
SUSPICIOUS_NEW = ["F_P1T3M3", "F_P4T4M3", "F_P3T5M5", "F_P2T5M4"]  # Leakage test


def load_bridge_candidates(round_name: str) -> list:
    """Load candidates from Bridge ultra-fast results"""
    path = Path(f"/home/admin/atlas-hec-v2.1-repo/benchmark_results/task1_inheritance/bridge_uf_{round_name}/bridge_uf_passed_candidates.json")
    with open(path) as f:
        data = json.load(f)
    return data["candidates"]


def organize_by_family_seed(candidates: list) -> dict:
    """Organize candidates by family and seed"""
    by_family = defaultdict(lambda: defaultdict(list))
    
    for c in candidates:
        fam = c["candidate"].get("family_id", "unknown")
        seed = c["candidate"].get("_source_seed", 0)
        tp = c["bridge_result"].get("throughput", 0)
        
        by_family[fam][seed].append({
            "id": c["candidate"]["id"],
            "seed": seed,
            "family": fam,
            "throughput": tp,
            "candidate": c["candidate"],
            "bridge_result": c["bridge_result"]
        })
    
    return by_family


def sample_candidates(round_name: str, candidates: list) -> list:
    """Apply stratified sampling with control families"""
    print(f"\n{'='*60}")
    print(f"SAMPLING - Round {round_name.upper()}")
    print(f"{'='*60}")
    
    by_family = organize_by_family_seed(candidates)
    selected = []
    selected_ids = set()
    seed_counts = defaultdict(int)
    
    # Helper to add candidate
    def add_candidate(c, reason):
        if c["id"] not in selected_ids:
            selected.append({
                **c,
                "selection_reason": reason
            })
            selected_ids.add(c["id"])
            seed_counts[c["seed"]] += 1
            return True
        return False
    
    # Helper to get top N from family across all seeds
    def get_top_from_family(fam, n, reason_prefix):
        all_in_family = []
        for seed in [1000, 1001, 1002]:
            all_in_family.extend(by_family.get(fam, {}).get(seed, []))
        
        # Sort by throughput descending
        all_in_family.sort(key=lambda x: x["throughput"], reverse=True)
        
        added = 0
        for c in all_in_family[:n]:
            if add_candidate(c, f"{reason_prefix}:{fam}"):
                added += 1
        return added
    
    # 1. Mandatory: Target family F_P3T4M4 (+1 extra)
    print(f"\n1. Target family {TARGET_FAMILY}:")
    n = get_top_from_family(TARGET_FAMILY, TOP_PER_FAMILY + 1, "target")
    print(f"   Selected: {n}")
    
    # 2. Mandatory: Round B gained families
    print(f"\n2. Round B gained families:")
    for fam in ROUND_B_GAINED:
        if fam in by_family:
            n = get_top_from_family(fam, TOP_PER_FAMILY, "round_b_gained")
            print(f"   {fam}: {n}")
    
    # 3. Mandatory: Round A stable control families
    print(f"\n3. Round A stable control families:")
    for fam in ROUND_A_STABLE:
        if fam in by_family:
            n = get_top_from_family(fam, TOP_PER_FAMILY, "control_stable")
            print(f"   {fam}: {n}")
    
    # 4. Mandatory: At least 1 suspicious new family (leakage test)
    print(f"\n4. Suspicious new families (leakage test):")
    leakage_selected = 0
    for fam in SUSPICIOUS_NEW:
        if fam in by_family and leakage_selected < 2:
            n = get_top_from_family(fam, 1, "suspicious_new")
            if n > 0:
                leakage_selected += n
                print(f"   {fam}: {n} (LEAKAGE TEST)")
    
    # 5. Fill remaining slots with other families, ensuring seed diversity
    print(f"\n5. Filling remaining slots (target: {TARGET_PER_ROUND}):")
    remaining_families = [f for f in by_family.keys() if f not in 
                         [TARGET_FAMILY] + ROUND_B_GAINED + ROUND_A_STABLE + SUSPICIOUS_NEW]
    
    # Sort by total count (high frequency first)
    remaining_families.sort(key=lambda f: sum(len(by_family[f][s]) for s in [1000, 1001, 1002]), reverse=True)
    
    for fam in remaining_families:
        if len(selected) >= TARGET_PER_ROUND:
            break
        
        # For high-frequency families, take up to 3
        limit = TOP_HIGHFREQ_FAMILY if sum(len(by_family[fam][s]) for s in [1000, 1001, 1002]) > 10 else TOP_PER_FAMILY
        n = get_top_from_family(fam, limit, "fill")
        if n > 0:
            print(f"   {fam}: {n}")
    
    # 6. Ensure minimum per seed
    print(f"\n6. Ensuring minimum {MIN_PER_SEED} per seed:")
    for seed in [1000, 1001, 1002]:
        current = seed_counts[seed]
        if current < MIN_PER_SEED:
            needed = MIN_PER_SEED - current
            print(f"   Seed {seed}: has {current}, need {needed} more")
            
            # Get candidates from this seed not yet selected
            available = []
            for fam in by_family:
                for c in by_family[fam].get(seed, []):
                    if c["id"] not in selected_ids:
                        available.append(c)
            
            # Sort by throughput
            available.sort(key=lambda x: x["throughput"], reverse=True)
            
            for c in available[:needed]:
                if add_candidate(c, f"seed_balance:{seed}"):
                    print(f"      Added {c['id']}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"SAMPLING COMPLETE - Round {round_name.upper()}")
    print(f"{'='*60}")
    print(f"Total selected: {len(selected)}")
    print(f"By seed: {dict(seed_counts)}")
    
    # Family distribution
    fam_dist = defaultdict(int)
    for c in selected:
        fam_dist[c["family"]] += 1
    print(f"\nFamily distribution:")
    for fam, count in sorted(fam_dist.items(), key=lambda x: x[1], reverse=True):
        print(f"   {fam}: {count}")
    
    return selected


def save_sample(round_name: str, sample: list):
    """Save sampled candidates for Mainline execution"""
    output_dir = Path(f"/home/admin/atlas-hec-v2.1-repo/benchmark_results/task1_inheritance/mainline_input_{round_name}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save as JSON
    output = {
        "round": round_name,
        "sample_size": len(sample),
        "selection_criteria": "stratified_family_with_controls",
        "candidates": [
            {
                "id": c["id"],
                "family": c["family"],
                "seed": c["seed"],
                "throughput": c["throughput"],
                "selection_reason": c["selection_reason"],
                "candidate_config": c["candidate"]
            }
            for c in sample
        ]
    }
    
    with open(output_dir / "mainline_sample.json", 'w') as f:
        json.dump(output, f, indent=2)
    
    # Save candidate IDs list for quick reference
    with open(output_dir / "candidate_ids.txt", 'w') as f:
        for c in sample:
            f.write(f"{c['id']}\t{c['family']}\tseed:{c['seed']}\t{c['selection_reason']}\n")
    
    print(f"\nSaved to: {output_dir}")
    return output_dir


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--round", choices=["a", "b", "ablation"], required=True)
    args = parser.parse_args()
    
    # Load candidates
    candidates = load_bridge_candidates(args.round)
    print(f"Loaded {len(candidates)} Bridge-passed candidates for Round {args.round.upper()}")
    
    # Sample
    sample = sample_candidates(args.round, candidates)
    
    # Save
    output_dir = save_sample(args.round, sample)
    
    print(f"\n✓ Round {args.round.upper()} sampling complete: {len(sample)} candidates")
    print(f"  Output: {output_dir}/mainline_sample.json")


if __name__ == "__main__":
    main()
