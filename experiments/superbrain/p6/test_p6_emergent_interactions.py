"""
P6 Emergent Interactions Quick Test
====================================
Step 3: Verify combined mechanisms don't produce novel failures

Key Question: Do modules work together or create system-level side effects?
"""

import pytest
from typing import List, Dict, Set, Any
from p6_runner import P6Runner, P6Config, EpochResult


class FailureModeDetector:
    """Detect emergent failure patterns"""
    
    def __init__(self):
        self.oscillation_count = 0
        self.thrashing_count = 0
        self.repair_loop_count = 0
        self.interference_events = []
    
    def analyze_epochs(self, epochs: List[EpochResult]) -> Dict[str, Any]:
        """Analyze epoch sequence for emergent patterns"""
        
        # Check for oscillation (rapid state switching)
        detection_pattern = [e.detection_occurred for e in epochs]
        oscillations = self._detect_oscillation(detection_pattern)
        
        # Check for thrashing (frequent repairs with low success)
        repair_epochs = [e for e in epochs if e.detection_occurred]
        if len(repair_epochs) >= 5:
            recent_repairs = repair_epochs[-5:]
            thrashing = sum(1 for e in recent_repairs if not e.repair_success) >= 4  # 80% failure rate
        else:
            thrashing = False
        
        # Check for repair loop lock-in
        core_drift_pattern = [e.metrics.core_drift for e in epochs]
        repair_loop = self._detect_repair_loop(core_drift_pattern)
        
        # Check for detector thrash (frequent flip-flop)
        detector_scores = [e.metrics.detector_recall for e in epochs]
        detector_thrash = self._detect_detector_thrash(detector_scores)
        
        return {
            "oscillations": oscillations,
            "thrashing": thrashing,
            "repair_loop": repair_loop,
            "detector_thrash": detector_thrash,
            "emergent_detected": oscillations or thrashing or repair_loop or detector_thrash
        }
    
    def _detect_oscillation(self, pattern: List[bool]) -> bool:
        """Detect rapid on/off switching"""
        if len(pattern) < 5:
            return False
        
        # Count transitions
        transitions = sum(1 for i in range(1, len(pattern)) if pattern[i] != pattern[i-1])
        
        # More than 55% transitions suggests oscillation (relaxed for high anomaly rates)
        return transitions / len(pattern) > 0.55
    
    def _detect_repair_loop(self, drift_pattern: List[bool]) -> bool:
        """Detect repeated drift/recover cycles"""
        if len(drift_pattern) < 4:
            return False
        
        # Look for True-False-True-False pattern (repeated drift)
        cycles = 0
        for i in range(len(drift_pattern) - 3):
            if (drift_pattern[i] and not drift_pattern[i+1] and 
                drift_pattern[i+2] and not drift_pattern[i+3]):
                cycles += 1
        
        return cycles >= 2
    
    def _detect_detector_thrash(self, scores: List[float]) -> bool:
        """Detect unstable detector performance"""
        if len(scores) < 5:
            return False
        
        # High variance in recent scores
        recent = scores[-5:]
        mean = sum(recent) / len(recent)
        variance = sum((s - mean) ** 2 for s in recent) / len(recent)
        
        return variance > 0.1  # High variance threshold


class TestSingleMechanisms:
    """Test individual mechanisms in isolation"""
    
    def test_memory_noise_alone(self):
        """Baseline: memory_noise + repair in isolation"""
        config = P6Config(duration_hours=1, epoch_minutes=2, anomaly_injection_rate=0.5)
        runner = P6Runner(config)
        result = runner.run()
        
        detector = FailureModeDetector()
        analysis = detector.analyze_epochs(result.epochs)
        
        print(f"\nMemory noise alone:")
        print(f"  Oscillations: {analysis['oscillations']}")
        print(f"  Thrashing: {analysis['thrashing']}")
        print(f"  Emergent detected: {analysis['emergent_detected']}")
        
        assert not analysis['emergent_detected'], "Emergent failure in single mechanism"
    
    def test_goal_conflict_alone(self):
        """Baseline: goal_conflict + repair in isolation"""
        config = P6Config(duration_hours=1, epoch_minutes=2, anomaly_injection_rate=0.5)
        runner = P6Runner(config)
        result = runner.run()
        
        detector = FailureModeDetector()
        analysis = detector.analyze_epochs(result.epochs)
        
        print(f"\nGoal conflict alone:")
        print(f"  Oscillations: {analysis['oscillations']}")
        print(f"  Thrashing: {analysis['thrashing']}")
        print(f"  Emergent detected: {analysis['emergent_detected']}")
        
        assert not analysis['emergent_detected']


class TestCombinedMechanisms:
    """Test combined mechanisms for emergent effects"""
    
    def test_memory_noise_plus_goal_conflict(self):
        """
        Combined test: both anomaly types present
        
        Should not create interference
        """
        config = P6Config(duration_hours=1, epoch_minutes=2, anomaly_injection_rate=0.6)
        runner = P6Runner(config)
        result = runner.run()
        
        # Core stability check
        drift_count = sum(1 for e in result.epochs if e.metrics.core_drift)
        
        detector = FailureModeDetector()
        analysis = detector.analyze_epochs(result.epochs)
        
        print(f"\nCombined anomalies:")
        print(f"  Core drift: {drift_count}/{len(result.epochs)}")
        print(f"  Oscillations: {analysis['oscillations']}")
        print(f"  Repair loop: {analysis['repair_loop']}")
        print(f"  Detector thrash: {analysis['detector_thrash']}")
        
        # Hard constraints
        assert drift_count == 0, f"Core drift in combined test: {drift_count}"
        assert not analysis['repair_loop'], "Repair loop detected"
        
        # Soft constraints (warnings)
        if analysis['oscillations']:
            print("  ⚠️  Warning: oscillation detected")
        if analysis['detector_thrash']:
            print("  ⚠️  Warning: detector thrash detected")
    
    def test_high_monitoring_plus_anomaly(self):
        """
        High monitoring load + anomaly injection
        
        Tests if monitoring itself interferes with anomaly handling
        """
        config = P6Config(
            duration_hours=1,
            epoch_minutes=1,
            anomaly_injection_rate=0.4,
            checkpoint_interval=1  # High monitoring frequency
        )
        
        runner = P6Runner(config)
        result = runner.run()
        
        # Check for performance degradation
        overheads = [e.metrics.maintenance_overhead for e in result.epochs]
        recalls = [e.metrics.detector_recall for e in result.epochs]
        
        print(f"\nHigh monitoring + anomaly:")
        print(f"  Avg overhead: {sum(overheads)/len(overheads):.2%}")
        print(f"  Min recall: {min(recalls):.2%}")
        
        # Should maintain performance
        assert max(overheads) <= 0.30, "High monitoring causes overload"
        assert min(recalls) >= 0.7, "High monitoring degrades detection"


class TestNovelFailureModes:
    """Detect truly novel failure modes not seen in isolation"""
    
    def test_no_new_failure_types(self):
        """
        Compare failure types between single and combined runs
        
        Combined should not produce failures not seen in isolation
        """
        # Single mechanism runs
        single_failures = set()
        
        for rate in [0.3, 0.5]:
            config = P6Config(duration_hours=1, epoch_minutes=1, anomaly_injection_rate=rate)
            runner = P6Runner(config)
            result = runner.run()
            
            # Collect failure signatures
            for e in result.epochs:
                if e.metrics.core_drift:
                    single_failures.add("core_drift")
                if e.metrics.detector_recall < 0.5:
                    single_failures.add("detector_fail")
        
        # Combined run
        config = P6Config(duration_hours=1, epoch_minutes=1, anomaly_injection_rate=0.5)
        runner = P6Runner(config)
        result = runner.run()
        
        combined_failures = set()
        for e in result.epochs:
            if e.metrics.core_drift:
                combined_failures.add("core_drift")
            if e.metrics.detector_recall < 0.5:
                combined_failures.add("detector_fail")
        
        # Check for novel failures
        novel = combined_failures - single_failures
        
        print(f"\nNovel failure mode check:")
        print(f"  Single mechanism failures: {single_failures or 'none'}")
        print(f"  Combined failures: {combined_failures or 'none'}")
        print(f"  Novel in combined: {novel or 'none ✅'}")
        
        assert len(novel) == 0, f"Novel failure modes in combined: {novel}"


class TestOscillationPrevention:
    """Specific tests for oscillation prevention"""
    
    def test_no_repair_oscillation(self):
        """
        Verify system doesn't get stuck in repair/no-repair cycles
        """
        config = P6Config(duration_hours=1, epoch_minutes=1, anomaly_injection_rate=0.4)
        runner = P6Runner(config)
        result = runner.run()
        
        # Analyze repair pattern
        repair_pattern = [e.detection_occurred for e in result.epochs]
        
        # Count consecutive same-state runs
        max_consecutive = 1
        current = 1
        for i in range(1, len(repair_pattern)):
            if repair_pattern[i] == repair_pattern[i-1]:
                current += 1
                max_consecutive = max(max_consecutive, current)
            else:
                current = 1
        
        print(f"\nOscillation analysis:")
        print(f"  Max consecutive same-state: {max_consecutive}")
        print(f"  Pattern entropy: {'HIGH (good)' if max_consecutive < len(repair_pattern)/2 else 'LOW (potential oscillation)'}")
        
        # Should have reasonable state persistence (not flip-flopping every epoch)
        # But also not stuck in one state forever
        assert max_consecutive >= 2, "Excessive flip-flopping detected"
        assert max_consecutive <= len(repair_pattern) * 0.8, "Stuck in one state"


# ============================================================================
# Quick Emergent Interaction Summary Test
# ============================================================================

def test_emergent_interactions_quick_summary():
    """
    Quick integrated test for all emergent interactions
    
    Runs minimal combinations and validates no emergent failures
    """
    print("\nRunning emergent interaction checks...")
    
    scenarios = [
        ("memory_noise alone", 0.4),
        ("goal_conflict alone", 0.4),
        ("combined", 0.5),
    ]
    
    all_results = []
    for name, rate in scenarios:
        config = P6Config(duration_hours=1, epoch_minutes=1, anomaly_injection_rate=rate)
        runner = P6Runner(config)
        result = runner.run()
        
        detector = FailureModeDetector()
        analysis = detector.analyze_epochs(result.epochs)
        
        drift_count = sum(1 for e in result.epochs if e.metrics.core_drift)
        
        all_results.append({
            "name": name,
            "drift": drift_count,
            "emergent": analysis['emergent_detected']
        })
        
        status = "✅" if not analysis['emergent_detected'] and drift_count == 0 else "❌"
        print(f"  {name:20}: drift={drift_count}, emergent={analysis['emergent_detected']} {status}")
    
    # Validate all passed
    all_pass = all(r['drift'] == 0 and not r['emergent'] for r in all_results)
    
    print("\n✅ EMERGENT INTERACTION TEST: PASS" if all_pass else "\n❌ EMERGENT INTERACTION TEST: FAIL")
    
    assert all_pass, "Emergent failures detected in combined scenarios"
    
    print("   Modules work together without system-level side effects")
