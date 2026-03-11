# P6 Implementation Plan

**Status:** Design Complete → Implementation Ready  
**Goal:** 72-hour continuous operation with automatic stop conditions  
**Entry:** P5b complete (✅)  
**Exit:** P6 PASS/FAIL verdict with full audit trail

---

## Implementation Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     P6 EXPERIMENT RUNNER                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │ Epoch Loop  │───→│  Anomaly    │───→│   Repair + Validate │  │
│  │ (60 min)    │    │  Injection  │    │   (P5b reuse)       │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
│         │                                            │           │
│         ↓                                            ↓           │
│  ┌─────────────┐                            ┌─────────────────┐ │
│  │  Metrics    │                            │  Stop Condition │ │
│  │  Collector  │                            │  Checker        │ │
│  └─────────────┘                            └─────────────────┘ │
│         │                                            │           │
│         └──────────────────┬─────────────────────────┘           │
│                            ↓                                    │
│                   ┌─────────────────┐                           │
│                   │  State Machine  │                           │
│                   │  RUN/STOP/HALT  │                           │
│                   └─────────────────┘                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Module Breakdown

### Module 1: `p6_runner.py` (Core Orchestrator)

```python
class P6Runner:
    """
    72-hour experiment orchestrator
    
    Responsibilities:
    - Epoch lifecycle management
    - State machine (INIT → RUN → [STOP|HALT] → ARCHIVE)
    - Coordination between components
    """
    
    def __init__(self, config: P6Config):
        self.config = config
        self.state = RunnerState.INIT
        self.current_epoch = 0
        self.epochs: List[EpochResult] = []
        self.stop_checker = StopConditionChecker()
        self.metrics_collector = MetricsCollector()
    
    def run(self) -> P6Result:
        """
        Main entry point. Runs until:
        - 72 hours complete (PASS)
        - Stop condition triggered (FAIL)
        - Manual interrupt (INCONCLUSIVE)
        """
        self.state = RunnerState.RUNNING
        
        for epoch_num in range(self.config.total_epochs):
            self.current_epoch = epoch_num
            
            # Run single epoch
            epoch_result = self._run_epoch(epoch_num)
            self.epochs.append(epoch_result)
            
            # Check stop conditions
            if self.stop_checker.check(self.epochs):
                self.state = RunnerState.HALTED
                return self._create_result(verdict=P6Verdict.FAIL)
            
            # Checkpoint every N epochs
            if epoch_num % self.config.checkpoint_interval == 0:
                self._save_checkpoint()
        
        self.state = RunnerState.COMPLETE
        return self._create_result(verdict=P6Verdict.PASS)
    
    def _run_epoch(self, epoch_num: int) -> EpochResult:
        """Execute one 60-minute epoch"""
        start_time = time.time()
        
        # Phase 1: Normal operation (50 min)
        state = self._simulate_normal_operation(duration_minutes=50)
        
        # Phase 2: Anomaly injection (decision point)
        if self._should_inject_anomaly():
            state = self._inject_anomaly(state)
            
            # Phase 3: Detect + Repair (P5b reuse)
            detection_result = self._detect_and_repair(state)
        else:
            detection_result = None
        
        # Phase 4: Validate and collect metrics
        metrics = self._collect_epoch_metrics(state, detection_result)
        
        return EpochResult(
            epoch_num=epoch_num,
            timestamp=start_time,
            metrics=metrics,
            core_hash=self._compute_core_hash(state),
            detection_occurred=detection_result is not None
        )
```

### Module 2: `stop_conditions.py` (Safety System)

```python
@dataclass
class StopCondition:
    """Individual stop condition configuration"""
    name: str
    check_fn: Callable[[List[EpochResult]], bool]
    severity: str  # "immediate" | "warning" | "info"
    description: str


class StopConditionChecker:
    """
    Automatic stop condition monitoring
    
    Hard stops (immediate halt):
    - Core drift detected
    - 3 consecutive epochs with detector recall < 0.6
    - Capability diversity < 20%
    - Maintenance overhead > 30%
    """
    
    STOP_CONDITIONS = [
        StopCondition(
            name="core_drift",
            check_fn=lambda epochs: _check_core_drift(epochs),
            severity="immediate",
            description="Any core hash change detected"
        ),
        StopCondition(
            name="detector_degradation",
            check_fn=lambda epochs: _check_detector_degradation(epochs, window=3, threshold=0.6),
            severity="immediate",
            description="3 consecutive epochs with recall < 0.6"
        ),
        StopCondition(
            name="capability_exhaustion",
            check_fn=lambda epochs: _check_capability_diversity(epochs, threshold=0.2),
            severity="immediate",
            description="Capability diversity below 20%"
        ),
        StopCondition(
            name="maintenance_overload",
            check_fn=lambda epochs: _check_maintenance_overhead(epochs, threshold=0.3),
            severity="immediate",
            description="Maintenance overhead above 30%"
        ),
    ]
    
    def check(self, epochs: List[EpochResult]) -> Optional[str]:
        """
        Check all stop conditions
        
        Returns:
            condition_name if stop triggered, None otherwise
        """
        for condition in self.STOP_CONDITIONS:
            if condition.check_fn(epochs):
                self._log_stop_triggered(condition, epochs[-1])
                return condition.name
        return None
```

### Module 3: `metrics_collector.py` (Long-horizon Metrics)

```python
class MetricsCollector:
    """
    Collect and aggregate metrics over 72-hour run
    
    Key metrics:
    - Per-epoch: core hash, detector performance, capability diversity, overhead
    - Rolling: 10-epoch window recall
    - Cumulative: total anomalies, repairs, failures
    """
    
    def __init__(self):
        self.epoch_metrics: List[EpochMetrics] = []
        self.baseline_capabilities: Optional[Set[str]] = None
    
    def record_epoch(self, epoch: EpochResult):
        """Record metrics from completed epoch"""
        metrics = EpochMetrics(
            epoch_num=epoch.epoch_num,
            core_hash=epoch.core_hash,
            core_drift=self._check_drift(epoch),
            detector_recall=self._compute_rolling_recall(window=10),
            capability_diversity=self._compute_diversity(epoch),
            maintenance_overhead=epoch.metrics.maintenance_time / epoch.metrics.total_time,
            repair_success_rate=self._compute_repair_success(window=10)
        )
        self.epoch_metrics.append(metrics)
    
    def get_summary(self) -> MetricsSummary:
        """Generate final summary statistics"""
        return MetricsSummary(
            total_epochs=len(self.epoch_metrics),
            core_drift_epochs=sum(1 for m in self.epoch_metrics if m.core_drift),
            min_detector_recall=min(m.detector_recall for m in self.epoch_metrics),
            avg_capability_diversity=sum(m.capability_diversity for m in self.epoch_metrics) / len(self.epoch_metrics),
            max_maintenance_overhead=max(m.maintenance_overhead for m in self.epoch_metrics),
            final_verdict=self._compute_verdict()
        )
```

### Module 4: `emergent_failure_detector.py` (Novel Failure Modes)

```python
class EmergentFailureDetector:
    """
    Detect failure modes not predictable from single-epoch analysis
    
    Checks:
    - Correlation between consecutive failures
    - Unusual patterns in repair success rates
    - Interaction between maintenance cycles
    """
    
    def detect_emergent_patterns(self, epochs: List[EpochResult]) -> List[EmergentPattern]:
        """
        Analyze epoch history for emergent patterns
        
        Returns:
            List of detected emergent patterns (empty if none)
        """
        patterns = []
        
        # Pattern 1: Cascading failures
        cascading = self._detect_cascading_failures(epochs)
        if cascading:
            patterns.append(cascading)
        
        # Pattern 2: Repair strategy失效
        strategy_failure = self._detect_strategy_degradation(epochs)
        if strategy_failure:
            patterns.append(strategy_failure)
        
        # Pattern 3: Phase locking (failures always at same epoch offset)
        phase_lock = self._detect_phase_locking(epochs)
        if phase_lock:
            patterns.append(phase_lock)
        
        return patterns
    
    def _detect_cascading_failures(self, epochs: List[EpochResult]) -> Optional[EmergentPattern]:
        """Detect if failures cluster more than expected"""
        # Statistical test for clustering
        failure_epochs = [e.epoch_num for e in epochs if e.detection_occurred and not e.repair_success]
        if len(failure_epochs) < 3:
            return None
        
        # Check if gaps between failures are unusually small
        gaps = [failure_epochs[i+1] - failure_epochs[i] for i in range(len(failure_epochs)-1)]
        avg_gap = sum(gaps) / len(gaps)
        
        if avg_gap < 5:  # Failures within 5 epochs
            return EmergentPattern(
                type="cascading_failures",
                description=f"Failures cluster with avg gap {avg_gap:.1f} epochs",
                severity="high"
            )
        return None
```

---

## Implementation Phases

### Phase 1: Core Runner (2 days)

**Deliverables:**
- [ ] `p6_runner.py` with basic epoch loop
- [ ] `P6Config` with 24h/72h modes
- [ ] State machine (INIT → RUN → STOP)
- [ ] Checkpoint persistence every N epochs

**Test:**
```python
def test_runner_1hour_smoke():
    config = P6Config(duration_hours=1, epoch_minutes=5)
    runner = P6Runner(config)
    result = runner.run()
    assert result.state == RunnerState.COMPLETE
    assert len(result.epochs) == 12  # 60 min / 5 min epochs
```

### Phase 2: Stop Conditions (1 day)

**Deliverables:**
- [ ] `stop_conditions.py` with all 4 hard stops
- [ ] Unit tests for each condition
- [ ] Integration with runner

**Test:**
```python
def test_stop_on_core_drift():
    runner = P6Runner(test_config)
    # Inject artificial core drift
    runner.epochs[10].core_hash = "modified_hash"
    assert runner.stop_checker.check(runner.epochs) == "core_drift"
```

### Phase 3: Metrics Pipeline (2 days)

**Deliverables:**
- [ ] `metrics_collector.py` with all 5 P6 criteria
- [ ] Rolling window computations
- [ ] JSON serialization
- [ ] Real-time dashboard (optional)

**Test:**
```python
def test_rolling_recall_computation():
    collector = MetricsCollector()
    # Simulate 15 epochs with known detection results
    # Verify 10-epoch window recall
```

### Phase 4: Emergent Detection (1 day)

**Deliverables:**
- [ ] `emergent_failure_detector.py`
- [ ] Pattern detection algorithms
- [ ] Correlation analysis

**Test:**
```python
def test_cascading_failure_detection():
    epochs = generate_cascading_failure_pattern()
    detector = EmergentFailureDetector()
    patterns = detector.detect_emergent_patterns(epochs)
    assert any(p.type == "cascading_failures" for p in patterns)
```

### Phase 5: Integration & 24h Smoke (2 days)

**Deliverables:**
- [ ] End-to-end integration
- [ ] 24-hour smoke test execution
- [ ] Bug fixes and tuning

**Success:** 24h run completes with all criteria met

### Phase 6: 72h Primary Run (3 days)

**Deliverables:**
- [ ] Full 72-hour experiment
- [ ] Complete audit trail
- [ ] Final report generation

---

## File Structure

```
experiments/superbrain/p6/
├── P6_LONG_HORIZON_ROBUSTNESS.md    # Design document
├── P6_IMPLEMENTATION_PLAN.md        # This file
├── p6_runner.py                     # Core orchestrator
├── stop_conditions.py               # Safety system
├── metrics_collector.py             # Long-horizon metrics
├── emergent_failure_detector.py     # Novel failure detection
├── test_p6_runner.py               # Unit tests
├── test_p6_stop_conditions.py      # Safety tests
├── test_p6_integration.py          # End-to-end tests
├── run_p6_24h_smoke.sh             # 24h smoke script
├── run_p6_72h_primary.sh           # 72h primary script
└── results/                         # Output directory
    ├── P6_24H_SMOKe_RESULTS.json
    ├── P6_72H_PRIMARY_RESULTS.json
    ├── epoch_metrics.csv
    ├── core_hash_timeline.csv
    └── visualizations/
```

---

## Entry Criteria Checklist

Before starting P6 implementation:

- [x] P5b Week 1 PASSED (core protection)
- [x] P5b Week 2 PASSED (anomaly loop)
- [ ] P6 runner skeleton implemented
- [ ] 1-hour integration test passing
- [ ] Stop condition framework working
- [ ] Metrics collection pipeline validated

---

## Success Criteria Recap

| Criterion | Metric | Threshold |
|-----------|--------|-----------|
| 1. Cumulative drift | Core hash changes | 0 |
| 2. Detector stability | Rolling 10-epoch recall | ≥0.8 |
| 3. Capability persistence | Diversity vs baseline | ≥50% |
| 4. Overhead bound | Maintenance time % | ≤10% |
| 5. No emergent failures | Pattern detection | None |

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| 72h run crashes | Checkpoint every hour, resume capability |
| Metrics overflow | Rotating log files, compression |
| False stop triggers | Configurable thresholds, warning before halt |
| Resource exhaustion | Memory profiling, automatic GC |

---

## Minimal First PR

**Title:** `P6 Phase 1: Core runner with 1h smoke test`

**Contents:**
- `p6_runner.py`: Basic epoch loop, 1h mode
- `test_p6_runner.py`: Unit tests
- `run_p6_1h_smoke.sh`: Quick validation script

**Success:** `pytest test_p6_runner.py -v` passes

---

## Implementation Start Command

```bash
cd experiments/superbrain/p6

# Phase 1
touch p6_runner.py
# Implement P6Runner class

# Test
pytest test_p6_runner.py::test_runner_1hour_smoke -v

# On pass
git add -A
git commit -m "P6 Phase 1: Core runner with 1h smoke test"
```

---

**Status:** Ready for implementation  
**Est. Timeline:** 9 days to 72h run (2+1+2+1+2+3)  
**Next Action:** Create `p6_runner.py` skeleton

*Draft: 2026-03-08*  
*Depends on: P5b complete (✅)*
