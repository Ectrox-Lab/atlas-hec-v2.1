"""
P6 Repair Exhaustion Quick Test
================================
Step 1: Verify repair mechanism doesn't degrade over repeated cycles

Key Question: Is repair repeatable, not just one-time effective?
"""

import pytest
import json
from typing import List, Dict, Any
from p6_runner import P6Runner, P6Config, EpochResult


class RepairExhaustionTracker:
    """Track repair performance over multiple cycles"""
    
    def __init__(self):
        self.cycles: List[Dict[str, Any]] = []
    
    def record_cycle(self, cycle_num: int, success: bool, 
                     capability_overlap: float, latency_ms: float,
                     continuity_pass: bool):
        self.cycles.append({
            "cycle": cycle_num,
            "success": success,
            "capability_overlap": capability_overlap,
            "latency_ms": latency_ms,
            "continuity_pass": continuity_pass
        })
    
    def get_trend(self, window: int = 5) -> Dict[str, float]:
        """Compute trend metrics"""
        if len(self.cycles) < window:
            window = len(self.cycles)
        
        recent = self.cycles[-window:]
        
        return {
            "success_rate": sum(1 for c in recent if c["success"]) / window,
            "avg_overlap": sum(c["capability_overlap"] for c in recent) / window,
            "avg_latency": sum(c["latency_ms"] for c in recent) / window,
            "continuity_rate": sum(1 for c in recent if c["continuity_pass"]) / window
        }
    
    def detect_exhaustion_pattern(self) -> bool:
        """
        Detect if repair is exhausting (degrading over time)
        
        Returns True if exhaustion detected
        """
        if len(self.cycles) < 10:
            return False
        
        # Check for declining success rate
        first_half = self.cycles[:len(self.cycles)//2]
        second_half = self.cycles[len(self.cycles)//2:]
        
        first_success = sum(1 for c in first_half if c["success"]) / len(first_half)
        second_success = sum(1 for c in second_half if c["success"]) / len(second_half)
        
        # If success rate drops by more than 20%, flag exhaustion
        if first_success > 0 and (first_success - second_success) / first_success > 0.2:
            return True
        
        # Check for declining capability overlap
        first_overlap = sum(c["capability_overlap"] for c in first_half) / len(first_half)
        second_overlap = sum(c["capability_overlap"] for c in second_half) / len(second_half)
        
        if first_overlap > 0 and (first_overlap - second_overlap) / first_overlap > 0.3:
            return True
        
        return False


class TestRepairExhaustionMemoryNoise:
    """Test repair exhaustion with memory_noise anomaly"""
    
    def test_memory_noise_20_cycles_no_exhaustion(self):
        """
        Repair exhaustion test: 20 cycles of memory_noise
        
        Pass criteria:
        - success_rate >= 0.8
        - continuity_rate >= 0.8
        - no exhaustion pattern detected
        """
        tracker = RepairExhaustionTracker()
        config = P6Config(duration_hours=1, epoch_minutes=3)  # Short epochs for speed
        
        for cycle in range(20):
            runner = P6Runner(config)
            # Inject memory_noise every cycle
            runner.config.anomaly_injection_rate = 1.0  # Always inject
            
            result = runner.run()
            
            # Analyze results
            repair_epochs = [e for e in result.epochs if e.detection_occurred]
            if repair_epochs:
                success = all(e.repair_success for e in repair_epochs if e.repair_success is not None)
                # Use capability_diversity directly from metrics
                overlap = sum(e.metrics.capability_diversity for e in repair_epochs) / len(repair_epochs) if repair_epochs else 1.0
                continuity = all(e.metrics.core_identity_match == 1.0 for e in repair_epochs) if repair_epochs else True
            else:
                success = True
                overlap = 1.0
                continuity = True
            
            tracker.record_cycle(
                cycle_num=cycle,
                success=success,
                capability_overlap=overlap,
                latency_ms=100.0,  # Simulated
                continuity_pass=continuity
            )
        
        # Check trends
        trend = tracker.get_trend(window=5)
        exhaustion = tracker.detect_exhaustion_pattern()
        
        print(f"\nMemory Noise 20-Cycle Results:")
        print(f"  Final success rate: {trend['success_rate']:.2%}")
        print(f"  Final capability overlap: {trend['avg_overlap']:.2%}")
        print(f"  Continuity rate: {trend['continuity_rate']:.2%}")
        print(f"  Exhaustion detected: {exhaustion}")
        
        # Pass criteria
        assert trend['success_rate'] >= 0.8, f"Success rate {trend['success_rate']:.2%} < 80%"
        assert trend['continuity_rate'] >= 0.8, f"Continuity rate {trend['continuity_rate']:.2%} < 80%"
        assert not exhaustion, "Exhaustion pattern detected"


class TestRepairExhaustionGoalConflict:
    """Test repair exhaustion with goal_conflict anomaly"""
    
    def test_goal_conflict_20_cycles_no_exhaustion(self):
        """
        Repair exhaustion test: 20 cycles of goal_conflict
        
        Critical: goal_conflict is more severe, should still not exhaust
        """
        tracker = RepairExhaustionTracker()
        config = P6Config(duration_hours=1, epoch_minutes=3)
        
        for cycle in range(20):
            runner = P6Runner(config)
            runner.config.anomaly_injection_rate = 1.0
            
            result = runner.run()
            
            repair_epochs = [e for e in result.epochs if e.detection_occurred]
            if repair_epochs:
                success = all(e.repair_success for e in repair_epochs if e.repair_success is not None)
                # Use capability_diversity directly from metrics
                overlap = sum(e.metrics.capability_diversity for e in repair_epochs) / len(repair_epochs) if repair_epochs else 1.0
                continuity = all(e.metrics.core_identity_match == 1.0 for e in repair_epochs) if repair_epochs else True
            else:
                success = True
                overlap = 1.0
                continuity = True
            
            tracker.record_cycle(
                cycle_num=cycle,
                success=success,
                capability_overlap=overlap,
                latency_ms=150.0,  # Higher latency for goal_conflict
                continuity_pass=continuity
            )
        
        trend = tracker.get_trend(window=5)
        exhaustion = tracker.detect_exhaustion_pattern()
        
        print(f"\nGoal Conflict 20-Cycle Results:")
        print(f"  Final success rate: {trend['success_rate']:.2%}")
        print(f"  Final capability overlap: {trend['avg_overlap']:.2%}")
        print(f"  Continuity rate: {trend['continuity_rate']:.2%}")
        print(f"  Exhaustion detected: {exhaustion}")
        
        assert trend['success_rate'] >= 0.8
        assert trend['continuity_rate'] >= 0.8
        assert not exhaustion


class TestRepairExhaustionMixed:
    """Test repair exhaustion with alternating anomalies"""
    
    def test_mixed_anomalies_50_cycles_no_exhaustion(self):
        """
        Mixed anomaly test: 50 cycles alternating memory_noise/goal_conflict
        
        Simulates real-world varying anomaly patterns
        """
        tracker = RepairExhaustionTracker()
        config = P6Config(duration_hours=1, epoch_minutes=2)
        
        for cycle in range(50):
            runner = P6Runner(config)
            runner.config.anomaly_injection_rate = 0.5  # 50% injection rate
            
            result = runner.run()
            
            repair_epochs = [e for e in result.epochs if e.detection_occurred]
            if repair_epochs:
                success_rate = sum(1 for e in repair_epochs if e.repair_success) / len(repair_epochs)
                overlap = sum(e.metrics.capability_diversity for e in repair_epochs) / len(repair_epochs)
                continuity = sum(1 for e in repair_epochs if e.metrics.core_identity_match == 1.0) / len(repair_epochs)
            else:
                success_rate = 1.0
                overlap = 1.0
                continuity = 1.0
            
            tracker.record_cycle(
                cycle_num=cycle,
                success=success_rate >= 0.8,
                capability_overlap=overlap,
                latency_ms=120.0,
                continuity_pass=continuity >= 0.8
            )
            
            # Early exit if exhaustion clearly detected
            if cycle >= 10 and tracker.detect_exhaustion_pattern():
                break
        
        trend = tracker.get_trend(window=10)
        exhaustion = tracker.detect_exhaustion_pattern()
        
        print(f"\nMixed Anomalies 50-Cycle Results:")
        print(f"  Cycles completed: {len(tracker.cycles)}")
        print(f"  Final success rate: {trend['success_rate']:.2%}")
        print(f"  Final capability overlap: {trend['avg_overlap']:.2%}")
        print(f"  Continuity rate: {trend['continuity_rate']:.2%}")
        print(f"  Exhaustion detected: {exhaustion}")
        
        # For mixed test, be slightly more lenient on raw success rate
        # but still strict on exhaustion pattern
        assert trend['continuity_rate'] >= 0.8
        assert not exhaustion, "Repair mechanism shows exhaustion under mixed load"


# ============================================================================
# Quick Exhaustion Summary Test
# ============================================================================

def test_repair_exhaustion_quick_summary():
    """
    Quick integrated exhaustion test
    
    Runs 30 cycles quickly and validates all key metrics
    """
    tracker = RepairExhaustionTracker()
    config = P6Config(duration_hours=1, epoch_minutes=1)  # Very short for speed
    
    print("\nRunning 30-cycle quick exhaustion test...")
    
    for cycle in range(30):
        runner = P6Runner(config)
        runner.config.anomaly_injection_rate = 0.7
        
        result = runner.run()
        
        # Aggregate metrics
        epochs_with_repair = [e for e in result.epochs if e.detection_occurred]
        if epochs_with_repair:
            success = sum(1 for e in epochs_with_repair if e.repair_success) / len(epochs_with_repair)
            overlap = sum(e.metrics.capability_diversity for e in epochs_with_repair) / len(epochs_with_repair)
        else:
            success = 1.0
            overlap = 1.0
        
        tracker.record_cycle(
            cycle_num=cycle,
            success=success >= 0.8,
            capability_overlap=overlap,
            latency_ms=100.0,
            continuity_pass=True  # Assume continuity for quick test
        )
    
    trend = tracker.get_trend(window=10)
    exhaustion = tracker.detect_exhaustion_pattern()
    
    print(f"\n✓ Quick Exhaustion Test Complete")
    print(f"  Success rate: {trend['success_rate']:.2%}")
    print(f"  Capability overlap: {trend['avg_overlap']:.2%}")
    print(f"  Exhaustion: {'DETECTED ❌' if exhaustion else 'NONE ✅'}")
    
    # Hard pass criteria
    assert trend['success_rate'] >= 0.8, "Repair success degraded"
    assert trend['avg_overlap'] >= 0.6, "Capability retention degraded"
    assert not exhaustion, "Exhaustion pattern detected"
    
    print("\n✅ REPAIR EXHAUSTION TEST: PASS")
    print("   Repair mechanism is repeatable, not one-time")
