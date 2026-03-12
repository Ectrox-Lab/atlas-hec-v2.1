#!/usr/bin/env python3
"""
Structure Fingerprint Extractor
P2.6 Specialist Routing Lane - Gate SR1

Extracts multi-dimensional fingerprints from candidate architecture data.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
import yaml

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class OrganizationalFingerprint:
    """A. 结构组织指纹"""
    cwci_total: float = 0.0
    specialization: float = 0.0
    integration: float = 0.0
    broadcast: float = 0.0
    hierarchy_depth: int = 1
    autonomy_strength: float = 0.0
    memory_partition_style: str = "distributed"


@dataclass
class RobustnessFingerprint:
    """B. 稳健性指纹"""
    scale_retention: float = 0.0
    seed_variance: float = 0.0
    cwci_min: float = 0.0
    cwci_max: float = 0.0
    stress_coverage: float = 0.0
    pass_rate: float = 0.0


@dataclass
class BehavioralFingerprint:
    """C. 行为指纹"""
    recovery_time: float = 0.0
    energy_stability: float = 0.0
    coordination_score: float = 0.0
    hazard_resistance: float = 0.0
    communication_cost: float = 0.0


@dataclass
class FailureFingerprint:
    """D. 失败指纹"""
    first_failure_mode: str = "unknown"
    seed_spike_risk: float = 0.0
    collapse_signature: str = ""
    bottleneck_type: str = "none"


@dataclass
class StructureFingerprint:
    """Complete structure fingerprint"""
    candidate_id: str
    candidate_name: str
    timestamp: str
    organizational: OrganizationalFingerprint
    robustness: RobustnessFingerprint
    behavioral: BehavioralFingerprint
    failure: FailureFingerprint
    
    # Derived metrics
    stability_index: float = 0.0
    consciousness_depth: float = 0.0
    robustness_score: float = 0.0
    risk_score: float = 0.0


class FingerprintExtractor:
    """Extracts structure fingerprints from experiment data"""
    
    def __init__(self, schema_path: Optional[str] = None):
        self.schema = self._load_schema(schema_path)
        
    def _load_schema(self, path: Optional[str]) -> Dict:
        """Load fingerprint schema from YAML"""
        if path is None:
            path = Path(__file__).parent.parent / "configs" / "fingerprint_schema.yaml"
        
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Could not load schema: {e}. Using defaults.")
            return {}
    
    def extract_from_gate_result(self, gate_data: Dict) -> StructureFingerprint:
        """Extract fingerprint from a Gate result file"""
        candidate_id = gate_data.get("candidate_id", "unknown")
        candidate_name = gate_data.get("candidate_name", candidate_id)
        
        # Extract organizational metrics
        org = OrganizationalFingerprint()
        cwci = gate_data.get("cwci", {})
        org.cwci_total = cwci.get("total", 0.0)
        org.specialization = cwci.get("specialization", 0.0)
        org.integration = cwci.get("integration", 0.0)
        org.broadcast = cwci.get("broadcast", 0.0)
        org.hierarchy_depth = gate_data.get("hierarchy_depth", 1)
        org.autonomy_strength = gate_data.get("autonomy_strength", 0.0)
        org.memory_partition_style = gate_data.get("memory_style", "distributed")
        
        # Extract robustness metrics
        rob = RobustnessFingerprint()
        rob.scale_retention = gate_data.get("scale_retention", 0.0)
        rob.seed_variance = gate_data.get("seed_variance", 0.0)
        rob.cwci_min = cwci.get("min", org.cwci_total)
        rob.cwci_max = cwci.get("max", org.cwci_total)
        rob.stress_coverage = gate_data.get("stress_coverage", 0.0)
        rob.pass_rate = gate_data.get("pass_rate", 0.0)
        
        # Extract behavioral metrics
        beh = BehavioralFingerprint()
        beh.recovery_time = gate_data.get("recovery_time", 0.0)
        beh.energy_stability = gate_data.get("energy_stability", 0.0)
        beh.coordination_score = gate_data.get("coordination_score", 0.0)
        beh.hazard_resistance = gate_data.get("hazard_resistance", 0.0)
        beh.communication_cost = gate_data.get("communication_cost", 0.0)
        
        # Extract failure metrics
        fail = FailureFingerprint()
        fail.first_failure_mode = gate_data.get("first_failure_mode", "unknown")
        fail.seed_spike_risk = self._calculate_seed_spike_risk(gate_data)
        fail.collapse_signature = gate_data.get("collapse_signature", "")
        fail.bottleneck_type = gate_data.get("bottleneck_type", "none")
        
        # Create fingerprint
        fp = StructureFingerprint(
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            timestamp=gate_data.get("timestamp", ""),
            organizational=org,
            robustness=rob,
            behavioral=beh,
            failure=fail
        )
        
        # Calculate derived metrics
        fp = self._calculate_derived_metrics(fp)
        
        return fp
    
    def _calculate_seed_spike_risk(self, data: Dict) -> float:
        """Calculate seed-spike risk score"""
        variance = data.get("seed_variance", 0.0)
        pass_rate = data.get("pass_rate", 0.0)
        cwci_max = data.get("cwci", {}).get("max", 0.0)
        cwci_min = data.get("cwci", {}).get("min", 0.0)
        
        # High variance + low pass rate = high risk
        risk = variance * 0.5
        
        if pass_rate < 0.3:
            risk += 0.3
        
        # Large gap between max and min performance
        if cwci_max - cwci_min > 0.5:
            risk += 0.2
            
        return min(risk, 1.0)
    
    def _calculate_derived_metrics(self, fp: StructureFingerprint) -> StructureFingerprint:
        """Calculate composite derived metrics"""
        org = fp.organizational
        rob = fp.robustness
        fail = fp.failure
        
        # Stability index
        fp.stability_index = (
            rob.scale_retention * 0.4 +
            (1 - rob.seed_variance) * 0.3 +
            rob.pass_rate * 0.3
        )
        
        # Consciousness depth
        fp.consciousness_depth = (
            org.specialization + org.integration + org.broadcast
        ) / 3
        
        # Robustness score
        fp.robustness_score = (rob.cwci_min + rob.scale_retention) / 2
        
        # Risk score
        fp.risk_score = (
            fail.seed_spike_risk * 0.5 +
            (1 - rob.stress_coverage) * 0.3 +
            rob.seed_variance * 0.2
        )
        
        return fp
    
    def extract_from_cwci_report(self, report_path: Path) -> Optional[StructureFingerprint]:
        """Extract fingerprint from CWCI report"""
        try:
            with open(report_path, 'r') as f:
                data = json.load(f)
            return self.extract_from_gate_result(data)
        except Exception as e:
            logger.error(f"Failed to extract from {report_path}: {e}")
            return None
    
    def batch_extract(self, input_dir: Path, pattern: str = "*.json") -> List[StructureFingerprint]:
        """Batch extract fingerprints from directory"""
        fingerprints = []
        
        for file_path in input_dir.rglob(pattern):
            logger.info(f"Processing {file_path}")
            fp = self.extract_from_cwci_report(file_path)
            if fp:
                fingerprints.append(fp)
                
        logger.info(f"Extracted {len(fingerprints)} fingerprints")
        return fingerprints


def save_fingerprints(fingerprints: List[StructureFingerprint], output_path: Path):
    """Save fingerprints to JSONL file"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        for fp in fingerprints:
            # Convert dataclass to dict
            data = {
                "candidate_id": fp.candidate_id,
                "candidate_name": fp.candidate_name,
                "timestamp": fp.timestamp,
                "organizational": asdict(fp.organizational),
                "robustness": asdict(fp.robustness),
                "behavioral": asdict(fp.behavioral),
                "failure": asdict(fp.failure),
                "derived": {
                    "stability_index": fp.stability_index,
                    "consciousness_depth": fp.consciousness_depth,
                    "robustness_score": fp.robustness_score,
                    "risk_score": fp.risk_score
                }
            }
            f.write(json.dumps(data) + "\n")
    
    logger.info(f"Saved {len(fingerprints)} fingerprints to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract structure fingerprints from experiment data"
    )
    parser.add_argument(
        "--input", "-i",
        type=Path,
        required=True,
        help="Input directory containing experiment results"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        required=True,
        help="Output file for fingerprints (JSONL)"
    )
    parser.add_argument(
        "--schema", "-s",
        type=Path,
        help="Path to fingerprint schema YAML"
    )
    parser.add_argument(
        "--pattern", "-p",
        type=str,
        default="*.json",
        help="File pattern to match"
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not args.input.exists():
        logger.error(f"Input directory does not exist: {args.input}")
        sys.exit(1)
    
    # Extract fingerprints
    extractor = FingerprintExtractor(args.schema)
    fingerprints = extractor.batch_extract(args.input, args.pattern)
    
    if not fingerprints:
        logger.warning("No fingerprints extracted!")
        sys.exit(0)
    
    # Save results
    save_fingerprints(fingerprints, args.output)
    
    # Print summary
    print("\n" + "="*60)
    print("EXTRACTION SUMMARY")
    print("="*60)
    print(f"Total fingerprints: {len(fingerprints)}")
    print(f"Output file: {args.output}")
    
    # Show statistics
    risk_scores = [fp.risk_score for fp in fingerprints]
    print(f"\nRisk Score Distribution:")
    print(f"  Mean: {sum(risk_scores)/len(risk_scores):.3f}")
    print(f"  Min:  {min(risk_scores):.3f}")
    print(f"  Max:  {max(risk_scores):.3f}")
    
    high_risk = sum(1 for r in risk_scores if r > 0.7)
    print(f"  High risk (>0.7): {high_risk}")


if __name__ == "__main__":
    main()
