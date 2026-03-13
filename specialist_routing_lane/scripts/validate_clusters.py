#!/usr/bin/env python3
"""
Cluster Validation Script
P2.6 Specialist Routing Lane - Gate SR1

Validates clustering quality and generates acceptance report.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ClusterValidator:
    """Validates clustering results against Gate SR1 criteria"""
    
    def __init__(self):
        self.regions_data: Dict = {}
        self.embeddings: np.ndarray = np.array([])
        self.clusters: np.ndarray = np.array([])
        self.results: Dict = {}
        
    def load_data(self, regions_dir: Path) -> None:
        """Load clustering results"""
        logger.info(f"Loading data from {regions_dir}")
        
        # Load regions JSON
        with open(regions_dir / "regions_v1.json", 'r') as f:
            self.regions_data = json.load(f)
        
        # Load embeddings
        self.embeddings = np.load(regions_dir / "embedding_v1.npy")
        
        # Load cluster labels
        self.clusters = np.load(regions_dir / "clusters_v1.npy")
        
        logger.info(f"Loaded {len(self.clusters)} samples")
    
    def calculate_silhouette_score(self) -> float:
        """Calculate silhouette score for clustering quality"""
        from sklearn.metrics import silhouette_score
        
        # Exclude noise points (-1)
        mask = self.clusters != -1
        if mask.sum() < 3:
            logger.warning("Too few non-noise points for silhouette")
            return 0.0
        
        score = silhouette_score(
            self.embeddings[mask], 
            self.clusters[mask]
        )
        return score
    
    def calculate_davies_bouldin(self) -> float:
        """Calculate Davies-Bouldin index"""
        from sklearn.metrics import davies_bouldin_score
        
        mask = self.clusters != -1
        if mask.sum() < 3:
            return float('inf')
        
        score = davies_bouldin_score(
            self.embeddings[mask],
            self.clusters[mask]
        )
        return score
    
    def calculate_calinski_harabasz(self) -> float:
        """Calculate Calinski-Harabasz index"""
        from sklearn.metrics import calinski_harabasz_score
        
        mask = self.clusters != -1
        if mask.sum() < 3:
            return 0.0
        
        score = calinski_harabasz_score(
            self.embeddings[mask],
            self.clusters[mask]
        )
        return score
    
    def check_family_separation(self) -> Dict:
        """Check separation between OctopusLike and OQS"""
        candidates = self.regions_data.get("candidates", [])
        
        # Find OctopusLike and OQS candidates
        octopus_ids = []
        oqs_ids = []
        
        for c in candidates:
            name = c.get("candidate_name", "").lower()
            if "octopus" in name or "mainline" in name or name == "o1":
                octopus_ids.append(c["candidate_id"])
            elif "oqs" in name or "challenger" in name:
                oqs_ids.append(c["candidate_id"])
        
        if not octopus_ids or not oqs_ids:
            logger.warning("Could not identify both families")
            return {"found_octopus": len(octopus_ids), "found_oqs": len(oqs_ids), "separation": 0}
        
        # Get embeddings
        octopus_idx = [i for i, c in enumerate(candidates) if c["candidate_id"] in octopus_ids]
        oqs_idx = [i for i, c in enumerate(candidates) if c["candidate_id"] in oqs_ids]
        
        octopus_emb = self.embeddings[octopus_idx]
        oqs_emb = self.embeddings[oqs_idx]
        
        # Calculate centroids
        octopus_centroid = octopus_emb.mean(axis=0)
        oqs_centroid = oqs_emb.mean(axis=0)
        
        # Calculate separation (normalized distance)
        distance = np.linalg.norm(octopus_centroid - oqs_centroid)
        
        # Calculate within-cluster spread
        octopus_spread = np.mean([np.linalg.norm(e - octopus_centroid) for e in octopus_emb])
        oqs_spread = np.mean([np.linalg.norm(e - oqs_centroid) for e in oqs_emb])
        
        normalized_separation = distance / (octopus_spread + oqs_spread + 1e-6)
        
        return {
            "found_octopus": len(octopus_ids),
            "found_oqs": len(oqs_ids),
            "centroid_distance": float(distance),
            "normalized_separation": float(normalized_separation),
            "pass": normalized_separation > 0.5
        }
    
    def check_seed_spike_detection(self) -> Dict:
        """Check if seed-spike candidates are clustered together"""
        candidates = self.regions_data.get("candidates", [])
        region_labels = self.regions_data.get("region_labels", {})
        
        # Find seed-spike region
        seed_spike_region = None
        for cluster_id, label in region_labels.items():
            if "seed_spike" in label.lower():
                seed_spike_region = int(cluster_id)
                break
        
        if seed_spike_region is None:
            logger.warning("No seed-spike region identified")
            return {"found_region": False, "precision": 0}
        
        # Get candidates in seed-spike region
        region_candidates = [
            c for c in candidates 
            if c.get("cluster_id") == seed_spike_region
        ]
        
        # Check how many are actually high risk
        high_risk_count = sum(1 for c in region_candidates if c.get("risk_score", 0) > 0.7)
        
        precision = high_risk_count / len(region_candidates) if region_candidates else 0
        
        return {
            "found_region": True,
            "region_id": seed_spike_region,
            "candidates_in_region": len(region_candidates),
            "high_risk_in_region": high_risk_count,
            "precision": float(precision),
            "pass": precision >= 0.8
        }
    
    def check_mainline_stability(self) -> Dict:
        """Check if mainline candidates are in stable region"""
        candidates = self.regions_data.get("candidates", [])
        region_labels = self.regions_data.get("region_labels", {})
        
        # Find mainline candidates
        mainline_candidates = [
            c for c in candidates 
            if any(x in c.get("candidate_name", "").lower() 
                   for x in ["octopus", "mainline", "o1"])
        ]
        
        if not mainline_candidates:
            logger.warning("No mainline candidates found")
            return {"found": False}
        
        # Check cluster assignments
        in_stable = 0
        near_noise = 0
        
        for c in mainline_candidates:
            cluster_id = c.get("cluster_id")
            label = region_labels.get(str(cluster_id), "unknown")
            
            if label == "stable_region":
                in_stable += 1
            elif cluster_id == -1:
                near_noise += 1
        
        return {
            "found": True,
            "count": len(mainline_candidates),
            "in_stable_region": in_stable,
            "in_noise": near_noise,
            "stability_ratio": in_stable / len(mainline_candidates),
            "pass": near_noise == 0 and in_stable == len(mainline_candidates)
        }
    
    def validate_all(self) -> Dict:
        """Run all validation checks"""
        logger.info("Running Gate SR1 validation...")
        
        results = {
            "gate": "SR1",
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "metrics": {},
            "checks": {},
            "overall_pass": True
        }
        
        # Calculate clustering metrics
        try:
            results["metrics"]["silhouette_score"] = self.calculate_silhouette_score()
        except Exception as e:
            logger.error(f"Silhouette calculation failed: {e}")
            results["metrics"]["silhouette_score"] = 0.0
        
        try:
            results["metrics"]["davies_bouldin_index"] = self.calculate_davies_bouldin()
        except Exception as e:
            results["metrics"]["davies_bouldin_index"] = float('inf')
        
        try:
            results["metrics"]["calinski_harabasz_index"] = self.calculate_calinski_harabasz()
        except Exception as e:
            results["metrics"]["calinski_harabasz_index"] = 0.0
        
        # Run specific checks
        results["checks"]["family_separation"] = self.check_family_separation()
        results["checks"]["seed_spike_detection"] = self.check_seed_spike_detection()
        results["checks"]["mainline_stability"] = self.check_mainline_stability()
        
        # Determine overall pass/fail
        criteria = [
            results["metrics"]["silhouette_score"] > 0.5,
            results["metrics"]["davies_bouldin_index"] < 1.0,
            results["checks"]["family_separation"].get("pass", False),
            results["checks"]["seed_spike_detection"].get("pass", False),
            results["checks"]["mainline_stability"].get("pass", False)
        ]
        
        results["criteria_passed"] = sum(criteria)
        results["criteria_total"] = len(criteria)
        results["overall_pass"] = all(criteria)
        
        return results
    
    def generate_report(self, results: Dict) -> str:
        """Generate Markdown validation report"""
        lines = []
        
        lines.append("# Gate SR1 Validation Report")
        lines.append(f"\n**Date**: {results['timestamp']}")
        lines.append(f"**Status**: {'✅ PASS' if results['overall_pass'] else '❌ FAIL'}")
        lines.append(f"**Criteria**: {results['criteria_passed']}/{results['criteria_total']} passed")
        lines.append("\n---\n")
        
        # Clustering Metrics
        lines.append("## Clustering Metrics\n")
        metrics = results["metrics"]
        lines.append(f"| Metric | Value | Threshold | Status |")
        lines.append(f"|--------|-------|-----------|--------|")
        
        silhouette = metrics.get("silhouette_score", 0)
        sil_pass = silhouette > 0.5
        lines.append(
            f"| Silhouette Score | {silhouette:.3f} | > 0.5 | "
            f"{'✅' if sil_pass else '❌'} |"
        )
        
        dbi = metrics.get("davies_bouldin_index", float('inf'))
        dbi_pass = dbi < 1.0
        lines.append(
            f"| Davies-Bouldin | {dbi:.3f} | < 1.0 | "
            f"{'✅' if dbi_pass else '❌'} |"
        )
        
        chi = metrics.get("calinski_harabasz_index", 0)
        lines.append(f"| Calinski-Harabasz | {chi:.1f} | - | ℹ️ |")
        lines.append("")
        
        # Specific Checks
        lines.append("## Validation Checks\n")
        
        # Family separation
        sep = results["checks"]["family_separation"]
        lines.append("### 1. Inter-Family Separation\n")
        lines.append(f"- OctopusLike found: {sep.get('found_octopus', 0)}")
        lines.append(f"- OQS found: {sep.get('found_oqs', 0)}")
        lines.append(f"- Normalized separation: {sep.get('normalized_separation', 0):.3f}")
        lines.append(f"- **Status**: {'✅ PASS' if sep.get('pass') else '❌ FAIL'}")
        lines.append("")
        
        # Seed-spike detection
        ssd = results["checks"]["seed_spike_detection"]
        lines.append("### 2. Seed-Spike Detection\n")
        lines.append(f"- Seed-spike region found: {ssd.get('found_region', False)}")
        lines.append(f"- Candidates in region: {ssd.get('candidates_in_region', 0)}")
        lines.append(f"- Precision: {ssd.get('precision', 0):.1%}")
        lines.append(f"- **Status**: {'✅ PASS' if ssd.get('pass') else '❌ FAIL'}")
        lines.append("")
        
        # Mainline stability
        ms = results["checks"]["mainline_stability"]
        lines.append("### 3. Mainline Stability\n")
        lines.append(f"- Mainline candidates: {ms.get('count', 0)}")
        lines.append(f"- In stable region: {ms.get('in_stable_region', 0)}")
        lines.append(f"- In noise: {ms.get('in_noise', 0)}")
        lines.append(f"- Stability ratio: {ms.get('stability_ratio', 0):.1%}")
        lines.append(f"- **Status**: {'✅ PASS' if ms.get('pass') else '❌ FAIL'}")
        lines.append("")
        
        # Conclusion
        lines.append("## Conclusion\n")
        if results["overall_pass"]:
            lines.append(
                "✅ **Gate SR1 PASSED**: Structure fingerprints successfully distinguish "
                "architecture families, identify seed-spike candidates, and locate "
                "mainline candidates in stable regions.\n"
            )
            lines.append("**Next Step**: Proceed to Gate SR2 (Routing Usefulness).")
        else:
            lines.append(
                "❌ **Gate SR1 FAILED**: Some criteria not met. Review the specific "
                "failures above and consider:\n"
            )
            lines.append("- Refining fingerprint dimensions")
            lines.append("- Collecting more candidate data")
            lines.append("- Adjusting clustering parameters")
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Validate clustering results for Gate SR1"
    )
    parser.add_argument(
        "--clusters", "-c",
        type=Path,
        required=True,
        help="Path to clustered regions directory"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output file for validation report"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of Markdown"
    )
    
    args = parser.parse_args()
    
    if not args.clusters.exists():
        logger.error(f"Clusters directory does not exist: {args.clusters}")
        sys.exit(1)
    
    # Run validation
    validator = ClusterValidator()
    validator.load_data(args.clusters)
    results = validator.validate_all()
    
    # Generate output
    if args.json:
        output = json.dumps(results, indent=2)
    else:
        output = validator.generate_report(results)
    
    # Write or print
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w') as f:
            f.write(output)
        logger.info(f"Report saved to {args.output}")
    else:
        print(output)
    
    # Exit with appropriate code
    sys.exit(0 if results["overall_pass"] else 1)


if __name__ == "__main__":
    main()
