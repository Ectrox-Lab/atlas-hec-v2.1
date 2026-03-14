#!/usr/bin/env python3
"""
Symmetry Check - Batch-3 (B→A) vs Batch-1 (A→B)
計算 Transfer Gap 對稱性比率
"""

import json
import sys
from pathlib import Path

def load_batch_metrics(batch_dir):
    """Load all window metrics from a batch directory"""
    batch_path = Path(batch_dir)
    metrics_list = []
    
    for window_dir in sorted(batch_path.glob("window_*")):
        metrics_file = window_dir / "metrics.json"
        if metrics_file.exists():
            with open(metrics_file) as f:
                data = json.load(f)
                metrics_list.append({
                    "window": window_dir.name,
                    "transfer_gap_pp": data.get("transfer_gap_pp", 0),
                    "checksum": data.get("data_checksum", "")
                })
    
    return metrics_list

def calculate_symmetry(batch_a2b_dir, batch_b2a_dir):
    """Calculate symmetry metrics between A→B and B→A"""
    
    # Load both batches
    a2b_metrics = load_batch_metrics(batch_a2b_dir)
    b2a_metrics = load_batch_metrics(batch_b2a_dir)
    
    if not a2b_metrics or not b2a_metrics:
        print("ERROR: Missing metrics data")
        return None
    
    # Calculate means
    a2b_mean = sum(m["transfer_gap_pp"] for m in a2b_metrics) / len(a2b_metrics)
    b2a_mean = sum(m["transfer_gap_pp"] for m in b2a_metrics) / len(b2a_metrics)
    
    # Calculate symmetry ratio
    if a2b_mean != 0:
        symmetry_ratio = b2a_mean / a2b_mean
    else:
        symmetry_ratio = 0
    
    # Determine symmetry status
    if 0.9 <= symmetry_ratio <= 1.1:
        symmetry_status = "完美對稱 (Perfect Symmetry)"
        scientific_meaning = "Transfer 是雙向普適，與方向無關"
    elif 0.5 <= symmetry_ratio <= 1.5:
        symmetry_status = "基本對稱 (Near Symmetry)"
        scientific_meaning = "Transfer 有一定對稱性，但存在方向偏好"
    else:
        symmetry_status = "明顯不對稱 (Asymmetric)"
        scientific_meaning = "Transfer 高度依賴 source→target 選擇"
    
    return {
        "A_to_B": {
            "mean_tg_pp": round(a2b_mean, 2),
            "windows": len(a2b_metrics),
            "checksums": [m["checksum"][:16] + "..." for m in a2b_metrics[:3]]
        },
        "B_to_A": {
            "mean_tg_pp": round(b2a_mean, 2),
            "windows": len(b2a_metrics),
            "checksums": [m["checksum"][:16] + "..." for m in b2a_metrics[:3]]
        },
        "symmetry": {
            "ratio": round(symmetry_ratio, 3),
            "status": symmetry_status,
            "scientific_meaning": scientific_meaning
        }
    }

def main():
    # Default paths
    batch_a2b = "ralph_runs/l5_batch1"  # Batch-1: A→B
    batch_b2a = "ralph_runs/l5_batch3_b2a"  # Batch-3: B→A
    
    print("=" * 70)
    print("SYMMETRY CHECK: B→A vs A→B")
    print("=" * 70)
    print()
    
    # Check if directories exist
    if not Path(batch_a2b).exists():
        print(f"ERROR: Batch A→B not found: {batch_a2b}")
        print("Run Batch-1 first")
        sys.exit(1)
    
    if not Path(batch_b2a).exists():
        print(f"WAITING: Batch B→A not ready: {batch_b2a}")
        print("Run Batch-3 and retry")
        sys.exit(0)
    
    # Calculate symmetry
    result = calculate_symmetry(batch_a2b, batch_b2a)
    
    if result:
        print(f"A→B (Code→Math):")
        print(f"  Mean Transfer Gap: {result['A_to_B']['mean_tg_pp']}pp")
        print(f"  Windows: {result['A_to_B']['windows']}")
        print()
        
        print(f"B→A (Math→Code):")
        print(f"  Mean Transfer Gap: {result['B_to_A']['mean_tg_pp']}pp")
        print(f"  Windows: {result['B_to_A']['windows']}")
        print()
        
        print(f"Symmetry Ratio: {result['symmetry']['ratio']}")
        print(f"Status: {result['symmetry']['status']}")
        print(f"Scientific Meaning: {result['symmetry']['scientific_meaning']}")
        print()
        
        # Output YAML for trajectory report
        print("-" * 70)
        print("YAML for Trajectory Report:")
        print("-" * 70)
        print(f"""symmetry_check:
  A_to_B_mean_tg: {result['A_to_B']['mean_tg_pp']}pp
  B_to_A_mean_tg: {result['B_to_A']['mean_tg_pp']}pp
  gap_symmetry_ratio: {result['symmetry']['ratio']}
  symmetry_status: {result['symmetry']['status']}
  scientific_meaning: {result['symmetry']['scientific_meaning']}
  shared_family_shift: null  # To be filled after lineage analysis
  shared_inheritance_consumption_patterns: null  # To be filled
  asymmetry_explanation: null  # To be filled if ratio < 0.5 or > 2.0
""")
        
        # Save to file
        output_file = Path(batch_b2a) / "symmetry_report.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Saved to: {output_file}")

if __name__ == "__main__":
    main()
