#!/usr/bin/env python3
"""
Stress-Based Routing
P2.6 Specialist Routing Lane

Routes architecture candidates based on stress scenario requirements.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional
import yaml

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StressRouter:
    """Routes candidates based on stress scenario"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.candidates: List[Dict] = []
        self.regions: Dict = {}
        
    def _load_config(self, path: Optional[str]) -> Dict:
        """Load routing configuration"""
        if path is None:
            path = Path(__file__).parent.parent / "configs" / "routing_thresholds.yaml"
        
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Could not load config: {e}. Using defaults.")
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """Default routing configuration"""
        return {
            "stress_scenarios": {
                "ResourceScarcity": {
                    "routing_weights": {
                        "energy_stability": 0.4,
                        "scale_retention": 0.3,
                        "autonomy_strength": 0.3
                    }
                }
            },
            "routing": {
                "min_eligible_score": 0.3,
                "default_top_k": 5
            }
        }
    
    def load_index(self, index_dir: Path) -> None:
        """Load structure index"""
        logger.info(f"Loading index from {index_dir}")
        
        # Load regions
        regions_file = index_dir / "regions_v1.json"
        with open(regions_file, 'r') as f:
            data = json.load(f)
            self.candidates = data.get("candidates", [])
            self.regions = data.get("clusters", {})
        
        logger.info(f"Loaded {len(self.candidates)} candidates")
    
    def score_candidate(self, candidate: Dict, stress: str) -> float:
        """Score a candidate for a specific stress scenario"""
        stress_config = self.config.get("stress_scenarios", {}).get(stress, {})
        weights = stress_config.get("routing_weights", {})
        
        if not weights:
            logger.warning(f"No weights defined for stress: {stress}")
            return 0.0
        
        score = 0.0
        total_weight = 0.0
        
        # Get fingerprint data - need to reload from original
        # For now, use available fields
        for metric, weight in weights.items():
            value = self._get_metric_value(candidate, metric)
            score += value * weight
            total_weight += weight
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def _get_metric_value(self, candidate: Dict, metric: str) -> float:
        """Extract metric value from candidate data"""
        # Map metric names to candidate fields
        metric_map = {
            "energy_stability": ["behavioral", "energy_stability"],
            "scale_retention": ["robustness", "scale_retention"],
            "autonomy_strength": ["organizational", "autonomy_strength"],
            "recovery_time": ["behavioral", "recovery_time"],
            "stress_coverage": ["robustness", "stress_coverage"],
            "coordination_score": ["behavioral", "coordination_score"],
            "integration": ["organizational", "integration"],
            "broadcast": ["organizational", "broadcast"],
            "seed_variance": ["robustness", "seed_variance"],
            "seed_spike_risk": ["failure", "seed_spike_risk"],
            "specialization": ["organizational", "specialization"],
            "risk_score": ["derived", "risk_score"],
            "stability_index": ["derived", "stability_index"],
        }
        
        path = metric_map.get(metric, [metric])
        value = candidate
        for key in path:
            if isinstance(value, dict):
                value = value.get(key, 0.0)
            else:
                return 0.0
        
        # Invert metrics where lower is better
        invert_metrics = ["recovery_time", "seed_variance", "communication_cost", "risk_score"]
        if metric in invert_metrics:
            value = 1.0 - float(value)
        
        return float(value)
    
    def route(self, stress: str, top_k: int = 5, exclude_high_risk: bool = True) -> List[Dict]:
        """Get top-k candidates for a stress scenario"""
        logger.info(f"Routing for stress: {stress} (top_k={top_k})")
        
        min_score = self.config.get("routing", {}).get("min_eligible_score", 0.3)
        
        scored_candidates = []
        for candidate in self.candidates:
            # Skip high-risk candidates if requested
            if exclude_high_risk:
                risk = self._get_metric_value(candidate, "risk_score")
                if risk > 0.7:
                    continue
            
            score = self.score_candidate(candidate, stress)
            if score >= min_score:
                scored_candidates.append({
                    **candidate,
                    "routing_score": score,
                    "stress_scenario": stress
                })
        
        # Sort by score
        scored_candidates.sort(key=lambda x: x["routing_score"], reverse=True)
        
        return scored_candidates[:top_k]
    
    def get_promotion_candidates(self, min_cwci: float = 0.7) -> List[Dict]:
        """Identify candidates worthy of promotion"""
        promotion_config = self.config.get("promotion", {}).get("challenger", {})
        
        candidates = []
        for c in self.candidates:
            # Check criteria
            cwci = self._get_metric_value(c, "cwci_total")
            retention = self._get_metric_value(c, "scale_retention")
            variance = self._get_metric_value(c, "seed_variance")
            risk = self._get_metric_value(c, "risk_score")
            
            meets_criteria = (
                cwci >= promotion_config.get("min_cwci_total", min_cwci) and
                retention >= promotion_config.get("min_scale_retention", 0.75) and
                variance <= promotion_config.get("max_seed_variance", 0.25) and
                risk <= 0.5
            )
            
            if meets_criteria:
                candidates.append({
                    **c,
                    "promotion_recommendation": "challenger",
                    "rationale": f"CWCI={cwci:.2f}, Retention={retention:.2f}, Var={variance:.2f}"
                })
        
        return candidates
    
    def generate_report(self, stress: Optional[str] = None, top_k: int = 5) -> str:
        """Generate routing report"""
        lines = []
        lines.append("# Routing Report")
        lines.append(f"\nGenerated: {__import__('datetime').datetime.now().isoformat()}")
        lines.append("\n---\n")
        
        # Top candidates by stress
        if stress:
            lines.append(f"## Stress Scenario: {stress}\n")
            recommendations = self.route(stress, top_k)
            
            lines.append("| Rank | Candidate | Score | Region | Risk |")
            lines.append("|------|-----------|-------|--------|------|")
            for i, rec in enumerate(recommendations, 1):
                lines.append(
                    f"| {i} | {rec.get('candidate_name', rec['candidate_id'])} | "
                    f"{rec['routing_score']:.3f} | {rec.get('region_label', 'unknown')} | "
                    f"{rec.get('risk_score', 'N/A'):.2f} |"
                )
        else:
            # Report for all stress scenarios
            scenarios = self.config.get("stress_scenarios", {}).keys()
            for scenario in scenarios:
                lines.append(f"## {scenario}\n")
                recommendations = self.route(scenario, top_k)
                
                if recommendations:
                    lines.append("| Rank | Candidate | Score | Region |")
                    lines.append("|------|-----------|-------|--------|")
                    for i, rec in enumerate(recommendations, 1):
                        lines.append(
                            f"| {i} | {rec.get('candidate_name', rec['candidate_id'])} | "
                            f"{rec['routing_score']:.3f} | {rec.get('region_label', 'unknown')} |"
                        )
                else:
                    lines.append("*No eligible candidates found*")
                lines.append("")
        
        # Promotion candidates
        lines.append("\n## Promotion Candidates\n")
        promotions = self.get_promotion_candidates()
        
        if promotions:
            lines.append("| Candidate | CWCI | Retention | Variance | Risk |")
            lines.append("|-----------|------|-----------|----------|------|")
            for p in promotions:
                cwci = self._get_metric_value(p, "cwci_total")
                retention = self._get_metric_value(p, "scale_retention")
                variance = self._get_metric_value(p, "seed_variance")
                risk = self._get_metric_value(p, "risk_score")
                lines.append(
                    f"| {p.get('candidate_name', p['candidate_id'])} | "
                    f"{cwci:.2f} | {retention:.2f} | {variance:.2f} | {risk:.2f} |"
                )
        else:
            lines.append("*No candidates meet promotion criteria*")
        
        # Region summary
        lines.append("\n## Region Summary\n")
        lines.append("| Region | Count | Description |")
        lines.append("|--------|-------|-------------|")
        for region_id, info in self.regions.items():
            lines.append(f"| {info.get('region_label', region_id)} | {info['size']} | Cluster {region_id} |")
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Route candidates by stress scenario"
    )
    parser.add_argument(
        "--index", "-i",
        type=Path,
        required=True,
        help="Path to structure index directory"
    )
    parser.add_argument(
        "--stress", "-s",
        type=str,
        help="Stress scenario to route for"
    )
    parser.add_argument(
        "--top-k", "-k",
        type=int,
        default=5,
        help="Number of top candidates to return"
    )
    parser.add_argument(
        "--config", "-c",
        type=Path,
        help="Path to routing config YAML"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output file for report"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of Markdown"
    )
    
    args = parser.parse_args()
    
    if not args.index.exists():
        logger.error(f"Index directory does not exist: {args.index}")
        sys.exit(1)
    
    # Initialize router
    router = StressRouter(args.config)
    router.load_index(args.index)
    
    # Generate report
    if args.json:
        # Output recommendations as JSON
        if args.stress:
            recommendations = router.route(args.stress, args.top_k)
            output = {
                "stress_scenario": args.stress,
                "recommendations": recommendations
            }
        else:
            output = {
                "all_scenarios": {
                    stress: router.route(stress, args.top_k)
                    for stress in router.config.get("stress_scenarios", {}).keys()
                }
            }
        
        result = json.dumps(output, indent=2)
    else:
        result = router.generate_report(args.stress, args.top_k)
    
    # Output
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w') as f:
            f.write(result)
        logger.info(f"Report saved to {args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()
