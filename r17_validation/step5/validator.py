"""
Step 5 Automated Validation Script
==================================
Validate Patch A against 50-sample test set

Outputs:
- overall FB
- live_auto FB
- Alignment
- live_manual FB
- Redline trigger status
"""

import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

from validation_config import ValidationConfig, DEFAULT_CONFIG


@dataclass
class ValidationResult:
    """Result for a single sample"""
    sample_id: str
    bucket: str
    
    # Prediction
    predicted_action: str
    deliberation_score: float
    review_score: float
    
    # Correctness
    is_correct: bool
    false_positive: bool  # Predicted approve, should reject
    false_negative: bool  # Predicted reject, should approve
    
    # Metadata
    processing_time_ms: float = 0.0


@dataclass  
class CheckpointReport:
    """Report at checkpoint (10, 20, 30, 40, 50 samples)"""
    checkpoint_sample: int
    timestamp: str
    
    # Metrics
    overall_fb: float
    live_auto_fb: float
    live_manual_fb: float
    alignment: float
    
    # Redline status
    redlines_triggered: List[str]
    should_rollback: bool
    
    # Per-bucket breakdown
    bucket_stats: Dict[str, Dict]
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class FinalReport:
    """Final Step 5 validation report"""
    
    # Configuration
    config: Dict
    
    # Overall metrics
    total_samples: int
    overall_fb: float
    live_auto_fb: float
    live_manual_fb: float
    alignment: float
    
    # Target comparison
    targets_met: Dict[str, bool]
    
    # Redlines
    redlines_triggered: List[str]
    should_rollback: bool
    
    # Per-bucket breakdown
    bucket_stats: Dict[str, Dict]
    
    # Sample-level results
    results: List[Dict]
    
    # Checkpoints
    checkpoints: List[Dict]
    
    # Timestamp
    completed_at: str
    
    def to_dict(self) -> Dict:
        return {
            "config": self.config,
            "summary": {
                "total_samples": self.total_samples,
                "overall_fb": self.overall_fb,
                "live_auto_fb": self.live_auto_fb,
                "live_manual_fb": self.live_manual_fb,
                "alignment": self.alignment,
                "targets_met": self.targets_met,
                "redlines_triggered": self.redlines_triggered,
                "should_rollback": self.should_rollback,
            },
            "bucket_stats": self.bucket_stats,
            "checkpoints": self.checkpoints,
            "completed_at": self.completed_at,
            # Note: individual results omitted for brevity in main report
        }
    
    def save(self, filepath: str):
        """Save report to JSON"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def save_full(self, filepath: str):
        """Save full report with all sample results"""
        full = self.to_dict()
        full["results"] = self.results
        with open(filepath, 'w') as f:
            json.dump(full, f, indent=2)


class Step5Validator:
    """Step 5 validation runner"""
    
    def __init__(self, config: ValidationConfig = None):
        self.config = config or DEFAULT_CONFIG
        self.results: List[ValidationResult] = []
        self.checkpoints: List[CheckpointReport] = []
    
    def validate_sample(self, sample: Dict, patch_a_output: Dict) -> ValidationResult:
        """Validate a single sample against Patch A output"""
        
        # Check thresholds
        deliberation_pass = patch_a_output.get("deliberation_score", 0) >= self.config.thresholds.deliberation
        review_pass = patch_a_output.get("review_score", 0) >= self.config.thresholds.review
        
        # Determine prediction
        predicted = patch_a_output.get("action", "escalate")
        expected = sample.get("expected_action", "escalate")
        
        is_correct = predicted == expected
        false_positive = (predicted == "approve" and expected != "approve")
        false_negative = (predicted == "reject" and expected == "approve")
        
        return ValidationResult(
            sample_id=sample.get("sample_id", ""),
            bucket=sample.get("bucket", ""),
            predicted_action=predicted,
            deliberation_score=patch_a_output.get("deliberation_score", 0),
            review_score=patch_a_output.get("review_score", 0),
            is_correct=is_correct,
            false_positive=false_positive,
            false_negative=false_negative,
            processing_time_ms=patch_a_output.get("processing_time_ms", 0),
        )
    
    def run_validation(self, samples: List[Dict], patch_a_outputs: List[Dict]) -> FinalReport:
        """Run full validation on all samples"""
        
        self.results = []
        self.checkpoints = []
        
        for i, (sample, output) in enumerate(zip(samples, patch_a_outputs)):
            result = self.validate_sample(sample, output)
            self.results.append(result)
            
            # Check if we hit a checkpoint
            checkpoint_num = i + 1
            if checkpoint_num in self.config.checkpoint_samples:
                cp = self._generate_checkpoint(checkpoint_num)
                self.checkpoints.append(cp)
                self._print_checkpoint(cp)
        
        # Generate final report
        return self._generate_final_report()
    
    def _generate_checkpoint(self, n_samples: int) -> CheckpointReport:
        """Generate checkpoint report for first n samples"""
        
        results = self.results[:n_samples]
        
        # Calculate metrics
        overall_fb = self._calculate_fb_rate(results)
        live_auto_fb = self._calculate_fb_rate([r for r in results if r.bucket == "live_auto"])
        live_manual_fb = self._calculate_fb_rate([r for r in results if r.bucket == "live_manual"])
        alignment = self._calculate_alignment(results)
        
        # Check redlines
        redlines = []
        if alignment < self.config.redlines.alignment_min:
            redlines.append(f"alignment_below_threshold ({alignment:.3f} < {self.config.redlines.alignment_min})")
        if live_manual_fb > self.config.redlines.live_manual_fb_max:
            redlines.append(f"live_manual_fb_exceeded ({live_manual_fb:.3f} > {self.config.redlines.live_manual_fb_max})")
        if overall_fb > self.config.redlines.overall_fb_max:
            redlines.append(f"overall_fb_exceeded ({overall_fb:.3f} > {self.config.redlines.overall_fb_max})")
        
        return CheckpointReport(
            checkpoint_sample=n_samples,
            timestamp=datetime.now().isoformat(),
            overall_fb=overall_fb,
            live_auto_fb=live_auto_fb,
            live_manual_fb=live_manual_fb,
            alignment=alignment,
            redlines_triggered=redlines,
            should_rollback=len(redlines) > 0,
            bucket_stats=self._calculate_bucket_stats(results),
        )
    
    def _generate_final_report(self) -> FinalReport:
        """Generate final validation report"""
        
        overall_fb = self._calculate_fb_rate(self.results)
        live_auto_fb = self._calculate_fb_rate([r for r in self.results if r.bucket == "live_auto"])
        live_manual_fb = self._calculate_fb_rate([r for r in self.results if r.bucket == "live_manual"])
        alignment = self._calculate_alignment(self.results)
        
        # Check targets
        targets_met = {
            "overall_fb": overall_fb <= self.config.targets.overall_fb_max,
            "live_auto_fb": live_auto_fb <= self.config.targets.live_auto_fb_max,
            "alignment": alignment >= self.config.targets.alignment_min,
        }
        
        # Check redlines
        redlines = []
        if alignment < self.config.redlines.alignment_min:
            redlines.append(f"alignment_below_threshold ({alignment:.3f} < {self.config.redlines.alignment_min})")
        if live_manual_fb > self.config.redlines.live_manual_fb_max:
            redlines.append(f"live_manual_fb_exceeded ({live_manual_fb:.3f} > {self.config.redlines.live_manual_fb_max})")
        if overall_fb > self.config.redlines.overall_fb_max:
            redlines.append(f"overall_fb_exceeded ({overall_fb:.3f} > {self.config.redlines.overall_fb_max})")
        
        return FinalReport(
            config={
                "total_samples": self.config.total_samples,
                "thresholds": {
                    "deliberation": self.config.thresholds.deliberation,
                    "review": self.config.thresholds.review,
                },
                "targets": {
                    "overall_fb_max": self.config.targets.overall_fb_max,
                    "live_auto_fb_max": self.config.targets.live_auto_fb_max,
                    "alignment_min": self.config.targets.alignment_min,
                },
                "redlines": {
                    "alignment_min": self.config.redlines.alignment_min,
                    "live_manual_fb_max": self.config.redlines.live_manual_fb_max,
                    "overall_fb_max": self.config.redlines.overall_fb_max,
                },
            },
            total_samples=len(self.results),
            overall_fb=overall_fb,
            live_auto_fb=live_auto_fb,
            live_manual_fb=live_manual_fb,
            alignment=alignment,
            targets_met=targets_met,
            redlines_triggered=redlines,
            should_rollback=len(redlines) > 0,
            bucket_stats=self._calculate_bucket_stats(self.results),
            results=[asdict(r) for r in self.results],
            checkpoints=[cp.to_dict() for cp in self.checkpoints],
            completed_at=datetime.now().isoformat(),
        )
    
    def _calculate_fb_rate(self, results: List[ValidationResult]) -> float:
        """Calculate false bounce rate"""
        if not results:
            return 0.0
        
        # FB = (FP + FN) / total
        incorrect = sum(1 for r in results if not r.is_correct)
        return incorrect / len(results)
    
    def _calculate_alignment(self, results: List[ValidationResult]) -> float:
        """Calculate alignment score"""
        if not results:
            return 0.0
        
        # Alignment = correct / total
        correct = sum(1 for r in results if r.is_correct)
        return correct / len(results)
    
    def _calculate_bucket_stats(self, results: List[ValidationResult]) -> Dict:
        """Calculate per-bucket statistics"""
        
        stats = {}
        buckets = set(r.bucket for r in results)
        
        for bucket in buckets:
            bucket_results = [r for r in results if r.bucket == bucket]
            stats[bucket] = {
                "count": len(bucket_results),
                "fb_rate": self._calculate_fb_rate(bucket_results),
                "alignment": self._calculate_alignment(bucket_results),
                "avg_deliberation_score": sum(r.deliberation_score for r in bucket_results) / len(bucket_results),
            }
        
        return stats
    
    def _print_checkpoint(self, cp: CheckpointReport):
        """Print checkpoint summary"""
        print(f"\n{'='*60}")
        print(f"CHECKPOINT: {cp.checkpoint_sample} samples")
        print(f"{'='*60}")
        print(f"Overall FB:      {cp.overall_fb:6.2%} (target: ≤{self.config.targets.overall_fb_max:.0%})")
        print(f"Live Auto FB:    {cp.live_auto_fb:6.2%} (target: ≤{self.config.targets.live_auto_fb_max:.0%})")
        print(f"Live Manual FB:  {cp.live_manual_fb:6.2%} (redline: >{self.config.redlines.live_manual_fb_max:.0%})")
        print(f"Alignment:       {cp.alignment:6.2%} (target: ≥{self.config.targets.alignment_min:.0%})")
        
        if cp.redlines_triggered:
            print(f"\n⚠️  REDLINES TRIGGERED:")
            for rl in cp.redlines_triggered:
                print(f"   - {rl}")
            print(f"\n🚨 SHOULD ROLLBACK: YES")
        else:
            print(f"\n✅ All redlines clear")
        
        print(f"{'='*60}")


def run_mock_validation():
    """Run validation with mock data for testing"""
    
    from sample_generator import SampleGenerator
    
    # Generate samples
    generator = SampleGenerator(seed=42)
    samples = generator.generate(50)
    
    # Generate mock Patch A outputs
    patch_a_outputs = []
    for sample in samples:
        # Simulate Patch A behavior with some noise
        deliberation = sample.expected_deliberation_score + random.uniform(-10, 10)
        review = deliberation + random.uniform(-5, 5)
        
        # Add some errors to simulate FB
        is_error = random.random() < 0.12  # ~12% error rate
        if is_error:
            action = "reject" if sample.expected_action == "approve" else "approve"
        else:
            action = sample.expected_action
        
        patch_a_outputs.append({
            "action": action,
            "deliberation_score": max(0, min(100, deliberation)),
            "review_score": max(0, min(100, review)),
            "processing_time_ms": random.uniform(50, 200),
        })
    
    # Run validation
    validator = Step5Validator()
    report = validator.run_validation(
        [s.to_dict() for s in samples],
        patch_a_outputs
    )
    
    # Save reports
    Path("r17_validation/results").mkdir(parents=True, exist_ok=True)
    report.save("r17_validation/results/step5_report.json")
    report.save_full("r17_validation/results/step5_report_full.json")
    
    # Print final summary
    print(f"\n{'='*60}")
    print("FINAL REPORT")
    print(f"{'='*60}")
    print(f"Overall FB:      {report.overall_fb:6.2%}")
    print(f"Live Auto FB:    {report.live_auto_fb:6.2%}")
    print(f"Live Manual FB:  {report.live_manual_fb:6.2%}")
    print(f"Alignment:       {report.alignment:6.2%}")
    print(f"\nTargets Met:")
    for target, met in report.targets_met.items():
        status = "✅" if met else "❌"
        print(f"  {status} {target}")
    print(f"\nShould Rollback: {'YES 🚨' if report.should_rollback else 'NO ✅'}")
    print(f"{'='*60}")
    
    return report


if __name__ == "__main__":
    import random
    run_mock_validation()
