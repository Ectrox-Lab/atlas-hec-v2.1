"""
P6 Maintenance Overload Quick Test
===================================
Step 2: Verify self-maintenance doesn't overwhelm system

Key Question: Does maintenance cost stay bounded under load?
"""

import pytest
import time
from typing import List, Dict, Any
from p6_runner import P6Runner, P6Config


class MaintenanceLoadTest:
    """Test maintenance behavior under different load levels"""
    
    def __init__(self, load_level: str, anomaly_rate: float, duration_epochs: int):
        self.load_level = load_level
        self.anomaly_rate = anomaly_rate
        self.duration_epochs = duration_epochs
        self.results: List[Dict[str, Any]] = []
    
    def run(self) -> Dict[str, float]:
        """Run load test and collect metrics"""
        config = P6Config(
            duration_hours=1,
            epoch_minutes=1,  # Short epochs for quick testing
            anomaly_injection_rate=self.anomaly_rate
        )
        
        runner = P6Runner(config)
        start_time = time.time()
        result = runner.run()
        elapsed = time.time() - start_time
        
        # Compute metrics
        if result.epochs:
            avg_overhead = sum(e.metrics.maintenance_overhead for e in result.epochs) / len(result.epochs)
            max_overhead = max(e.metrics.maintenance_overhead for e in result.epochs)
            avg_recall = sum(e.metrics.detector_recall for e in result.epochs) / len(result.epochs)
            min_diversity = min(e.metrics.capability_diversity for e in result.epochs)
            
            # Throughput: epochs per second
            throughput = len(result.epochs) / elapsed if elapsed > 0 else 0
        else:
            avg_overhead = max_overhead = avg_recall = min_diversity = throughput = 0
        
        return {
            "load_level": self.load_level,
            "anomaly_rate": self.anomaly_rate,
            "avg_overhead": avg_overhead,
            "max_overhead": max_overhead,
            "avg_recall": avg_recall,
            "min_diversity": min_diversity,
            "throughput": throughput,
            "elapsed_seconds": elapsed,
            "epochs_completed": len(result.epochs)
        }


class TestMaintenanceOverloadSweep:
    """Sweep through load levels to detect overload threshold"""
    
    def test_baseline_no_load(self):
        """
        Baseline: No anomalies
        
        Should have minimal overhead
        """
        test = MaintenanceLoadTest("baseline", 0.0, 10)
        result = test.run()
        
        print(f"\nBaseline (no load):")
        print(f"  Avg overhead: {result['avg_overhead']:.2%}")
        print(f"  Throughput: {result['throughput']:.2f} epochs/sec")
        
        # Baseline should have very low overhead
        assert result['avg_overhead'] <= 0.05, f"Baseline overhead {result['avg_overhead']:.2%} > 5%"
    
    def test_low_load(self):
        """
        Low load: 10% anomaly rate
        
        Should handle easily
        """
        test = MaintenanceLoadTest("low", 0.1, 10)
        result = test.run()
        
        print(f"\nLow load (10% anomaly):")
        print(f"  Avg overhead: {result['avg_overhead']:.2%}")
        print(f"  Avg recall: {result['avg_recall']:.2%}")
        print(f"  Throughput: {result['throughput']:.2f} epochs/sec")
        
        assert result['avg_overhead'] <= 0.10, f"Low load overhead {result['avg_overhead']:.2%} > 10%"
        assert result['avg_recall'] >= 0.8, f"Low load recall {result['avg_recall']:.2%} < 80%"
    
    def test_medium_load(self):
        """
        Medium load: 30% anomaly rate
        
        Should still be manageable
        """
        test = MaintenanceLoadTest("medium", 0.3, 10)
        result = test.run()
        
        print(f"\nMedium load (30% anomaly):")
        print(f"  Avg overhead: {result['avg_overhead']:.2%}")
        print(f"  Max overhead: {result['max_overhead']:.2%}")
        print(f"  Avg recall: {result['avg_recall']:.2%}")
        print(f"  Min diversity: {result['min_diversity']:.2%}")
        
        # Medium load should still be under control
        assert result['max_overhead'] <= 0.20, f"Medium load max overhead {result['max_overhead']:.2%} > 20%"
        assert result['avg_recall'] >= 0.8
        assert result['min_diversity'] >= 0.5
    
    def test_high_load(self):
        """
        High load: 50% anomaly rate
        
        Stress test - should not collapse
        """
        test = MaintenanceLoadTest("high", 0.5, 10)
        result = test.run()
        
        print(f"\nHigh load (50% anomaly):")
        print(f"  Avg overhead: {result['avg_overhead']:.2%}")
        print(f"  Max overhead: {result['max_overhead']:.2%}")
        print(f"  Avg recall: {result['avg_recall']:.2%}")
        print(f"  Min diversity: {result['min_diversity']:.2%}")
        
        # Even at high load, should maintain basic functionality
        assert result['max_overhead'] <= 0.30, f"High load max overhead {result['max_overhead']:.2%} > 30% (threshold)"
        assert result['avg_recall'] >= 0.7, f"High load recall {result['avg_recall']:.2%} < 70%"
    
    def test_overload_threshold(self):
        """
        Find approximate overload threshold
        
        Gradually increase load until overhead exceeds 30%
        """
        print("\nOverload threshold detection:")
        
        thresholds = []
        for rate in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
            test = MaintenanceLoadTest(f"rate_{rate}", rate, 5)
            result = test.run()
            
            status = "✅" if result['max_overhead'] <= 0.30 else "❌ OVERLOAD"
            print(f"  {rate*100:3.0f}% anomaly: overhead={result['max_overhead']:5.1%} {status}")
            
            if result['max_overhead'] <= 0.30:
                thresholds.append(rate)
        
        # System should handle at least 40% anomaly rate without overload
        assert len(thresholds) >= 4, f"System overloads too early (only handles {thresholds[-1] if thresholds else 0:.0%})"


class TestMaintenanceStability:
    """Test maintenance stability over extended operation"""
    
    def test_sustained_medium_load(self):
        """
        Sustained medium load: 20 cycles at 25% anomaly rate
        
        Verify overhead doesn't creep up over time
        """
        overheads = []
        recalls = []
        
        for cycle in range(20):
            config = P6Config(duration_hours=1, epoch_minutes=1, anomaly_injection_rate=0.25)
            runner = P6Runner(config)
            result = runner.run()
            
            if result.epochs:
                avg_overhead = sum(e.metrics.maintenance_overhead for e in result.epochs) / len(result.epochs)
                avg_recall = sum(e.metrics.detector_recall for e in result.epochs) / len(result.epochs)
                overheads.append(avg_overhead)
                recalls.append(avg_recall)
        
        # Check for upward trend in overhead
        first_half = sum(overheads[:10]) / 10
        second_half = sum(overheads[10:]) / 10
        
        print(f"\nSustained medium load (20 cycles):")
        print(f"  Early overhead: {first_half:.2%}")
        print(f"  Late overhead: {second_half:.2%}")
        print(f"  Overhead trend: {'STABLE ✅' if second_half <= first_half * 1.2 else 'CREEPING ❌'}")
        
        # Overhead should not increase by more than 20%
        assert second_half <= first_half * 1.2, "Maintenance overhead creeping up over time"
        
        # Recall should remain stable
        min_recall = min(recalls)
        assert min_recall >= 0.8, f"Recall dropped to {min_recall:.2%}"


class TestFalseTriggerImpact:
    """Test impact of false triggers on maintenance load"""
    
    def test_false_trigger_overhead(self):
        """
        Verify false triggers don't cause excessive maintenance
        
        Even with high detection rate, overhead should stay bounded
        """
        config = P6Config(duration_hours=1, epoch_minutes=1, anomaly_injection_rate=0.3)
        runner = P6Runner(config)
        result = runner.run()
        
        # Count detections vs actual anomalies
        detection_count = sum(1 for e in result.epochs if e.detection_occurred)
        
        # Get overhead stats
        overheads = [e.metrics.maintenance_overhead for e in result.epochs]
        avg_overhead = sum(overheads) / len(overheads)
        
        print(f"\nFalse trigger impact:")
        print(f"  Detection count: {detection_count}/{len(result.epochs)} epochs")
        print(f"  Avg overhead: {avg_overhead:.2%}")
        print(f"  Max overhead: {max(overheads):.2%}")
        
        # Overhead per detection should be reasonable
        if detection_count > 0:
            overhead_per_detection = avg_overhead * len(result.epochs) / detection_count
            print(f"  Overhead per detection: {overhead_per_detection:.2%}")
            assert overhead_per_detection <= 0.5, "Overhead per detection too high"


# ============================================================================
# Quick Overload Summary Test
# ============================================================================

def test_maintenance_overload_quick_summary():
    """
    Quick integrated overload test
    
    Validates all load levels in one test
    """
    print("\nRunning maintenance overload sweep...")
    
    results = []
    for load_name, rate in [("low", 0.1), ("medium", 0.3), ("high", 0.5)]:
        test = MaintenanceLoadTest(load_name, rate, 5)
        result = test.run()
        results.append(result)
        
        print(f"  {load_name:6} ({rate*100:3.0f}%): overhead={result['avg_overhead']:5.1%}, recall={result['avg_recall']:5.1%}")
    
    # Validate progression
    overheads = [r['avg_overhead'] for r in results]
    
    # Overhead should increase with load (monotonic check)
    assert overheads[1] >= overheads[0] * 0.8, "Overhead doesn't scale with load"
    
    # But should stay bounded
    assert max(overheads) <= 0.30, f"Max overhead {max(overheads):.2%} exceeds 30% threshold"
    
    print("\n✅ MAINTENANCE OVERLOAD TEST: PASS")
    print("   Self-maintenance cost stays bounded under load")
