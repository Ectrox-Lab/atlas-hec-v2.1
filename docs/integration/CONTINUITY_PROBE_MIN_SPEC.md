# CollectiveContinuityProbe - Minimal Specification

**Version**: v0.1.0-minimal  
**Date**: 2026-03-09  
**Status**: Design Ready for Implementation

---

## Design Principle

> **Read-only observation. No control. No influence. Pure aggregation.**

The Probe is a **macroscope**, not a **microscope**. It observes population-level patterns, not individual cell decisions.

---

## Core Responsibility

Monitor cross-lineage continuity and emit early warning signals when:

1. **Strategy convergence** detected (entropy drop)
2. **Lineage monopoly** forming (top1 share increase)
3. **Archive over-exposure** (sampling rate anomaly)
4. **Memory layer imbalance** (L1/L2/L3 health divergence)

**Not responsible for**:
- Individual cell decisions
- Direct archive manipulation
- Lineage inheritance override
- Real-time intervention

---

## Data Structure (Minimal)

```rust
/// Probe state - minimal, read-only
pub struct CollectiveContinuityProbe {
    /// Temporal observation window (last N generations)
    window_size: usize,  // Fixed: 100 generations
    
    /// Observed state history
    history: RingBuffer<SystemSnapshot>,
    
    /// Computed trends (updated every 100 gens)
    trends: TrendMetrics,
    
    /// Current alerts
    alerts: Vec<Alert>,
}

/// Snapshot of system state at one generation
#[derive(Clone, Debug)]
pub struct SystemSnapshot {
    pub generation: u32,
    pub timestamp: u64,  // Unix timestamp
    
    // Population metrics
    pub population: u32,
    pub cdi: f32,
    pub ci: f32,
    pub r: f32,
    
    // Memory layer health (0.0 - 1.0)
    pub l1_health: f32,  // Cell memory utilization
    pub l2_health: f32,  // Lineage diversity normalized
    pub l3_health: f32,  // Archive write/read ratio
    
    // Continuity metrics
    pub lineage_diversity: u32,
    pub top1_lineage_share: f32,
    pub strategy_entropy: f32,
    
    // Archive interaction
    pub archive_sample_attempts: u32,
    pub archive_sample_successes: u32,
    pub archive_influenced_births: u32,
}

/// Trend computation results
#[derive(Default, Clone, Debug)]
pub struct TrendMetrics {
    pub lineage_diversity_slope: f32,
    pub lineage_diversity_r2: f32,
    
    pub strategy_entropy_slope: f32,
    pub strategy_entropy_r2: f32,
    
    pub top1_share_slope: f32,
    pub top1_share_r2: f32,
    
    pub archive_exposure_rate: f32,  // samples per birth
}

/// Alert level
#[derive(Clone, Debug)]
pub struct Alert {
    pub generation: u32,
    pub level: AlertLevel,
    pub metric: String,
    pub message: String,
    pub value: f32,
    pub threshold: f32,
}

#[derive(Clone, Debug, PartialEq)]
pub enum AlertLevel {
    Info,      // Observation noted
    Warning,   // Trend concerning
    Critical,  // Immediate attention
}
```

---

## Update Frequency

| Operation | Frequency | Latency |
|-----------|-----------|---------|
| State observation | Per-generation | < 1 second |
| Trend computation | Every 100 generations | Batch |
| Alert generation | Every 100 generations | Batch |
| CSV output | Every 100 generations | Async |

**Total bandwidth**: ~100 bytes per generation (extremely low)

---

## Input/Output

### Input (Read-Only)

```rust
/// Called every generation
pub fn observe(&mut self, state: &SystemSnapshot) {
    // Store snapshot
    self.history.push(state.clone());
    
    // Compute trends every 100 generations
    if state.generation % 100 == 0 {
        self.compute_trends();
        self.check_alerts();
        self.write_csv();
    }
}
```

**Input sources**:
1. Bio-World CSV export (read-only file access)
2. No direct memory access
3. No real-time streaming required

### Output (Log/CSV Only)

```rust
/// CSV output format
pub fn write_csv(&self) {
    // File: continuity_probe_log.csv
    // Columns:
    // generation,timestamp,
    // lineage_diversity,top1_share,strategy_entropy,
    // l1_health,l2_health,l3_health,
    // diversity_slope,entropy_slope,top1_slope,
    // archive_exposure_rate,
    // alert_level,alert_message
}
```

**No control outputs**:
- ✗ No signals back to Bio-World
- ✗ No parameter adjustments
- ✗ No cell instruction
- ✗ No archive modification

---

## Relationship to L1/L2/L3

### L1 Cell Memory

| Aspect | Relationship |
|--------|--------------|
| Read access | Via CSV aggregate (avg_stress_level) |
| Write access | **FORBIDDEN** |
| Influence | None - observation only |
| Health metric | `l1_health = avg_stress_level` |

### L2 Lineage Memory

| Aspect | Relationship |
|--------|--------------|
| Read access | Via CSV (lineage_diversity, top1_share) |
| Write access | **FORBIDDEN** |
| Influence | None - observation only |
| Health metric | `l2_health = diversity / max_diversity` |

### L3 Causal Archive

| Aspect | Relationship |
|--------|--------------|
| Read access | Via CSV (archive_* fields) |
| Write access | **FORBIDDEN** |
| Influence | None - observation only |
| Health metric | `l3_health = write_rate / max_rate` |

---

## Anti-Cheat Boundaries

### Hard Constraints

```rust
impl CollectiveContinuityProbe {
    /// Verify probe cannot influence simulation
    pub fn verify_read_only(&self) -> bool {
        // These must ALL be true
        checks = [
            !self.has_write_access_to_bio_world(),
            !self.can_modify_cell_state(),
            !self.can_modify_lineage_memory(),
            !self.can_modify_archive(),
            !self.can_send_control_signals(),
        ];
        checks.iter().all(|&c| c)
    }
}
```

### Verification Tests

```rust
#[test]
fn test_probe_read_only() {
    let probe = CollectiveContinuityProbe::new();
    
    // Try to write - should fail or be no-op
    let result = probe.attempt_write_to_bio_world();
    assert!(result.is_err() || result.is_noop());
}

#[test]
fn test_probe_no_cell_control() {
    let probe = CollectiveContinuityProbe::new();
    
    // Verify no cell control methods exist
    assert!(!probe.has_method("control_cell"));
    assert!(!probe.has_method("override_action"));
}
```

---

## Algorithm (Minimal)

### Trend Computation

```rust
impl CollectiveContinuityProbe {
    fn compute_trends(&mut self) {
        let window = self.history.last_n(self.window_size);
        
        // Simple linear regression for each metric
        self.trends.lineage_diversity_slope = linear_slope(
            window.generations(),
            window.lineage_diversities()
        );
        
        self.trends.lineage_diversity_r2 = r_squared(
            window.generations(),
            window.lineage_diversities()
        );
        
        // Strategy entropy trend
        self.trends.strategy_entropy_slope = linear_slope(
            window.generations(),
            window.strategy_entropies()
        );
        
        // Top1 share trend
        self.trends.top1_share_slope = linear_slope(
            window.generations(),
            window.top1_shares()
        );
        
        // Archive exposure rate
        let total_attempts: u32 = window.archive_sample_attempts().sum();
        let total_births: u32 = window.births().sum();
        self.trends.archive_exposure_rate = 
            total_attempts as f32 / total_births.max(1) as f32;
    }
}
```

### Alert Detection

```rust
impl CollectiveContinuityProbe {
    fn check_alerts(&mut self) {
        // Alert: Lineage diversity declining
        if self.trends.lineage_diversity_slope < -0.1 
            && self.trends.lineage_diversity_r2 > 0.7 {
            self.alerts.push(Alert {
                generation: self.current_generation(),
                level: AlertLevel::Warning,
                metric: "lineage_diversity".to_string(),
                message: "Lineage diversity declining".to_string(),
                value: self.trends.lineage_diversity_slope,
                threshold: -0.1,
            });
        }
        
        // Alert: Strategy convergence
        if self.trends.strategy_entropy_slope < -0.05
            && self.trends.strategy_entropy_r2 > 0.7 {
            self.alerts.push(Alert {
                generation: self.current_generation(),
                level: AlertLevel::Warning,
                metric: "strategy_entropy".to_string(),
                message: "Strategy convergence detected".to_string(),
                value: self.trends.strategy_entropy_slope,
                threshold: -0.05,
            });
        }
        
        // Alert: Lineage monopoly
        let current_top1 = self.history.last().top1_lineage_share;
        if current_top1 > 0.5 && self.trends.top1_share_slope > 0.01 {
            self.alerts.push(Alert {
                generation: self.current_generation(),
                level: AlertLevel::Critical,
                metric: "top1_lineage_share".to_string(),
                message: "Lineage monopoly forming".to_string(),
                value: current_top1,
                threshold: 0.5,
            });
        }
    }
}
```

---

## First Version (MVP)

**Scope**: Log/csv output only, NO control

```rust
// Main loop
fn main() {
    let mut probe = CollectiveContinuityProbe::new(Config {
        window_size: 100,
        output_path: "continuity_probe_log.csv",
    });
    
    // Watch Bio-World output directory
    let watcher = FileWatcher::new("bio_world_outputs/");
    
    loop {
        // Wait for new generation CSV
        if let Some(csv_path) = watcher.detect_new_generation() {
            let snapshot = parse_snapshot(&csv_path);
            probe.observe(&snapshot);
        }
        
        // Sleep to avoid busy-wait
        std::thread::sleep(Duration::from_secs(1));
    }
}
```

---

## Output Example

```csv
generation,timestamp,lineage_diversity,top1_share,strategy_entropy,l1_health,l2_health,l3_health,diversity_slope,entropy_slope,top1_slope,archive_exposure_rate,alert_level,alert_message
100,1710000000,45,0.15,1.2,0.76,0.82,0.45,0.0,0.0,0.0,0.01,INFO,
200,1710000100,43,0.18,1.15,0.75,0.80,0.46,-0.02,-0.005,0.003,0.01,WARNING,lineage_diversity_declining
300,1710000200,38,0.25,1.05,0.73,0.75,0.48,-0.05,-0.015,0.008,0.01,WARNING,strategy_convergence
400,1710000300,25,0.45,0.85,0.70,0.65,0.50,-0.13,-0.035,0.025,0.01,CRITICAL,lineage_monopoly_forming
```

---

## Implementation Checklist

- [ ] `SystemSnapshot` struct defined
- [ ] `CollectiveContinuityProbe` struct defined
- [ ] CSV parser for Bio-World output
- [ ] Linear regression for trends
- [ ] Alert detection rules
- [ ] CSV output writer
- [ ] Read-only verification tests
- [ ] No control capability verification
- [ ] Integration test with Bio-World

---

## Success Criteria

1. Probe runs without crashing
2. CSV output contains all trend columns
3. Alerts generated when thresholds crossed
4. No write access to Bio-World detected
5. Performance < 1% CPU overhead

---

**Next**: Implement Probe, integrate with Bio-World, run falsification experiments
