#!/usr/bin/env python3
"""
Akashic Region Summary Writer
P2.6 Specialist Routing Lane

Writes region mapping to Akashic memory.
"""

import argparse
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AkashicWriter:
    """Writes region summaries to Akashic memory"""
    
    def __init__(self):
        self.regions_data: Dict = {}
        
    def load_regions(self, regions_path: Path) -> None:
        """Load region clustering data"""
        logger.info(f"Loading regions from {regions_path}")
        
        with open(regions_path / "regions_v1.json", 'r') as f:
            self.regions_data = json.load(f)
        
        logger.info(f"Loaded {self.regions_data['statistics']['num_clusters']} regions")
    
    def generate_region_summary(self) -> str:
        """Generate Markdown summary for Akashic"""
        lines = []
        
        lines.append("# Akashic Region Summary")
        lines.append(f"\n**Generated**: {datetime.now().isoformat()}")
        lines.append(f"**Schema Version**: 1.0")
        lines.append(f"**Source**: P2.6 Specialist Routing Lane")
        lines.append("\n---\n")
        
        # Statistics
        stats = self.regions_data.get("statistics", {})
        lines.append("## Overview\n")
        lines.append(f"- **Total Candidates**: {stats.get('total_candidates', 0)}")
        lines.append(f"- **Regions Identified**: {stats.get('num_clusters', 0)}")
        lines.append(f"- **Noise Points**: {stats.get('noise_points', 0)}")
        lines.append(f"- **Embedding Dimension**: {stats.get('embedding_dim', 0)}")
        lines.append("")
        
        # Region details
        lines.append("## Region Atlas\n")
        
        clusters = self.regions_data.get("clusters", {})
        region_labels = self.regions_data.get("region_labels", {})
        candidates = self.regions_data.get("candidates", [])
        
        for cluster_id_str, cluster_info in sorted(clusters.items(), key=lambda x: int(x[0])):
            cluster_id = int(cluster_id_str)
            label = region_labels.get(str(cluster_id), f"region_{cluster_id}")
            
            lines.append(f"### {label.upper()} (Cluster {cluster_id})\n")
            lines.append(f"**Size**: {cluster_info['size']} candidates\n")
            
            # Get candidate details
            cluster_candidates = [
                c for c in candidates 
                if c.get("cluster_id") == cluster_id
            ]
            
            if cluster_candidates:
                lines.append("**Members**:")
                for c in cluster_candidates:
                    name = c.get("candidate_name", c["candidate_id"])
                    risk = c.get("risk_score", 0)
                    lines.append(f"- `{name}` (risk: {risk:.2f})")
                lines.append("")
            
            # Region characterization
            if label == "stable_region":
                lines.append(
                    "**Characteristics**: High scale retention, low variance, "
                    "consistent performance. Suitable for production deployment.\n"
                )
            elif label == "seed_spike_zone":
                lines.append(
                    "**Characteristics**: High seed variance, unstable performance. "
                    "Likely false positives. Require additional validation.\n"
                )
            elif label == "high_variance_region":
                lines.append(
                    "**Characteristics**: Inconsistent performance across seeds. "
                    "May need architectural refinement.\n"
                )
            elif label == "noise":
                lines.append(
                    "**Characteristics**: Outliers that don't fit any cluster. "
                    "May be unique architectures or measurement errors.\n"
                )
            else:
                lines.append(f"**Characteristics**: Standard region with mixed properties.\n")
            
            lines.append("---\n")
        
        # Stress-performance mapping
        lines.append("## Stress-Region Mapping\n")
        lines.append("Based on candidate properties, regions show preferences for stress scenarios:\n")
        
        # Infer from candidate data
        for label in set(region_labels.values()):
            region_candidates = [
                c for c in candidates 
                if region_labels.get(str(c.get("cluster_id"))) == label
            ]
            
            if not region_candidates:
                continue
                
            lines.append(f"### {label}\n")
            
            # Calculate average metrics
            avg_risk = sum(c.get("risk_score", 0) for c in region_candidates) / len(region_candidates)
            
            lines.append(f"- **Average Risk Score**: {avg_risk:.3f}")
            lines.append(f"- **Recommended For**: ")
            
            if label == "stable_region":
                lines.append("All scenarios (general purpose)")
            elif label == "seed_spike_zone":
                lines.append("None (requires further validation)")
            elif avg_risk < 0.3:
                lines.append("Low-risk, stable environments")
            else:
                lines.append("Specific scenarios (see individual candidates)")
            lines.append("")
        
        # Recommendations
        lines.append("## Recommendations\n")
        
        stable = [c for c in candidates if region_labels.get(str(c.get("cluster_id"))) == "stable_region"]
        seed_spike = [c for c in candidates if region_labels.get(str(c.get("cluster_id"))) == "seed_spike_zone"]
        
        lines.append("### For Mainline (OctopusLike)\n")
        if stable:
            mainline = stable[0]  # Assuming first stable is mainline
            lines.append(
                f"- **Current Status**: Located in `{region_labels.get(str(mainline.get('cluster_id')))}`\n"
            )
            lines.append(
                f"- **Assessment**: {'✅ Stable' if mainline.get('risk_score', 1) < 0.3 else '⚠️ Review needed'}\n"
            )
        
        lines.append("### For Surprise Lane\n")
        lines.append(f"- **High-risk candidates**: {len(seed_spike)} in seed-spike zone\n")
        lines.append("- **Action**: Require additional seed testing before promotion\n")
        
        lines.append("### For OQS Line\n")
        oqs_candidates = [c for c in candidates if "oqs" in c.get("candidate_name", "").lower()]
        if oqs_candidates:
            oqs = oqs_candidates[0]
            lines.append(
                f"- **Location**: `{region_labels.get(str(oqs.get('cluster_id')), 'unknown')}`\n"
            )
            lines.append(f"- **Distance to Mainline**: (see embedding analysis)\n")
        
        return "\n".join(lines)
    
    def write_akashic_summary(self, output_dir: Path) -> None:
        """Write summary to Akashic directory"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write Markdown summary
        summary = self.generate_region_summary()
        summary_path = output_dir / "region_summary_v1.md"
        with open(summary_path, 'w') as f:
            f.write(summary)
        logger.info(f"Written: {summary_path}")
        
        # Write JSON mapping for programmatic access
        mapping = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "candidate_regions": {
                c["candidate_id"]: {
                    "cluster_id": c.get("cluster_id"),
                    "region_label": self.regions_data.get("region_labels", {}).get(
                        str(c.get("cluster_id")), "unknown"
                    ),
                    "risk_score": c.get("risk_score", 0),
                    "embedding": c.get("embedding", [])
                }
                for c in self.regions_data.get("candidates", [])
            },
            "region_definitions": {
                k: {
                    "size": v["size"],
                    "label": self.regions_data.get("region_labels", {}).get(k, f"region_{k}"),
                    "members": v["candidates"]
                }
                for k, v in self.regions_data.get("clusters", {}).items()
            }
        }
        
        json_path = output_dir / "region_mapping_v1.json"
        with open(json_path, 'w') as f:
            json.dump(mapping, f, indent=2)
        logger.info(f"Written: {json_path}")
        
        # Write promotion candidates list
        candidates = self.regions_data.get("candidates", [])
        region_labels = self.regions_data.get("region_labels", {})
        
        promotions = []
        for c in candidates:
            risk = c.get("risk_score", 1)
            label = region_labels.get(str(c.get("cluster_id")), "unknown")
            
            if risk < 0.4 and label == "stable_region":
                promotions.append({
                    "candidate_id": c["candidate_id"],
                    "candidate_name": c.get("candidate_name", c["candidate_id"]),
                    "region": label,
                    "risk_score": risk,
                    "recommendation": "promote_to_challenger"
                })
        
        promo_path = output_dir / "promotion_candidates_v1.json"
        with open(promo_path, 'w') as f:
            json.dump(promotions, f, indent=2)
        logger.info(f"Written: {promo_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Write Akashic region summary"
    )
    parser.add_argument(
        "--regions", "-r",
        type=Path,
        required=True,
        help="Path to clustered regions directory"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        required=True,
        help="Output directory for Akashic summaries"
    )
    
    args = parser.parse_args()
    
    if not args.regions.exists():
        logger.error(f"Regions directory does not exist: {args.regions}")
        return
    
    writer = AkashicWriter()
    writer.load_regions(args.regions)
    writer.write_akashic_summary(args.output)
    
    logger.info("Akashic region summary complete")


if __name__ == "__main__":
    main()
