"""
Step 5 Sample Generator
=======================
Generate 50-sample test set with proper bucketing
"""

import json
import random
from dataclasses import dataclass, asdict
from typing import List, Dict
from datetime import datetime


@dataclass
class Sample:
    """Single validation sample"""
    sample_id: str
    bucket: str  # live_auto, live_manual, replay_real
    source: str
    complexity: str  # simple, medium, complex
    
    # Ground truth (for validation)
    expected_action: str
    expected_deliberation_score: float
    
    # Metadata
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return asdict(self)


class SampleGenerator:
    """Generate 50-sample test set for Step 5"""
    
    # Distribution: ensure live_auto coverage
    BUCKET_DISTRIBUTION = {
        "live_auto": 0.50,    # 50% - ensure enough coverage
        "live_manual": 0.30,  # 30%
        "replay_real": 0.20,  # 20%
    }
    
    COMPLEXITY_DISTRIBUTION = {
        "simple": 0.30,
        "medium": 0.50,
        "complex": 0.20,
    }
    
    SOURCES = {
        "live_auto": ["auto_review_queue", "ci_trigger", "pre_submit"],
        "live_manual": ["manual_review_queue", "escalation", "audit"],
        "replay_real": ["prod_incident_1", "prod_incident_2", "prod_incident_3"],
    }
    
    ACTIONS = ["approve", "reject", "request_changes", "escalate"]
    
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.samples: List[Sample] = []
    
    def generate(self, n_samples: int = 50) -> List[Sample]:
        """Generate n samples with proper distribution"""
        
        # Calculate bucket sizes
        bucket_sizes = {}
        remaining = n_samples
        
        for bucket, ratio in self.BUCKET_DISTRIBUTION.items():
            if bucket == list(self.BUCKET_DISTRIBUTION.keys())[-1]:
                bucket_sizes[bucket] = remaining
            else:
                size = int(n_samples * ratio)
                bucket_sizes[bucket] = size
                remaining -= size
        
        # Generate samples per bucket
        sample_id = 0
        for bucket, size in bucket_sizes.items():
            for _ in range(size):
                sample = self._create_sample(sample_id, bucket)
                self.samples.append(sample)
                sample_id += 1
        
        # Shuffle
        self.rng.shuffle(self.samples)
        
        # Reassign IDs after shuffle
        for i, sample in enumerate(self.samples):
            sample.sample_id = f"S5-{i+1:03d}"
        
        return self.samples
    
    def _create_sample(self, idx: int, bucket: str) -> Sample:
        """Create a single sample"""
        
        complexity = self.rng.choices(
            list(self.COMPLEXITY_DISTRIBUTION.keys()),
            weights=list(self.COMPLEXITY_DISTRIBUTION.values())
        )[0]
        
        source = self.rng.choice(self.SOURCES[bucket])
        
        # Deliberation score varies by complexity
        if complexity == "simple":
            score = self.rng.uniform(75, 95)
        elif complexity == "medium":
            score = self.rng.uniform(60, 85)
        else:  # complex
            score = self.rng.uniform(40, 75)
        
        return Sample(
            sample_id=f"S5-{idx:03d}",
            bucket=bucket,
            source=source,
            complexity=complexity,
            expected_action=self.rng.choice(self.ACTIONS),
            expected_deliberation_score=round(score, 2),
        )
    
    def save(self, filepath: str):
        """Save samples to JSON"""
        data = {
            "metadata": {
                "total_samples": len(self.samples),
                "generated_at": datetime.now().isoformat(),
                "bucket_distribution": self._calculate_distribution(),
            },
            "samples": [s.to_dict() for s in self.samples]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _calculate_distribution(self) -> Dict:
        """Calculate actual bucket distribution"""
        dist = {}
        for sample in self.samples:
            dist[sample.bucket] = dist.get(sample.bucket, 0) + 1
        return dist
    
    def load(self, filepath: str) -> List[Sample]:
        """Load samples from JSON"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.samples = [
            Sample(**s) for s in data["samples"]
        ]
        return self.samples


def generate_test_set(output_path: str = "r17_validation/data/step5_samples.json"):
    """Generate and save 50-sample test set"""
    
    generator = SampleGenerator(seed=42)
    samples = generator.generate(50)
    generator.save(output_path)
    
    # Print summary
    print("=" * 60)
    print("Step 5 Sample Set Generated")
    print("=" * 60)
    
    dist = generator._calculate_distribution()
    print(f"\nBucket Distribution:")
    for bucket, count in sorted(dist.items()):
        pct = count / len(samples) * 100
        print(f"  {bucket:15s}: {count:2d} ({pct:4.1f}%)")
    
    print(f"\nTotal: {len(samples)} samples")
    print(f"Output: {output_path}")
    print("=" * 60)
    
    return samples


if __name__ == "__main__":
    generate_test_set()
