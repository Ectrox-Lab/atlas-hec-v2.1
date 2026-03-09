# Contract Delta for Bio-World Implementation

**To**: Codex (Bio-World maintainer)  
**From**: Atlas-HEC v2.1 Audit  
**Date**: 2026-03-09  
**Priority**: High

---

## TL;DR

Atlas-HEC audit complete. Need Bio-World to add **8 metrics** to CSV export and **implement JSONL stream**. No algorithm changes, no control flow changes, just enhanced observability.

---

## Required Changes

### 1. CSV Logger Enhancement

**File**: `bioworld_mvp/src/bio_world/output/csv_logger.rs`

**Add columns to population.csv**:
```rust
writeln!(
    log.population,
    "{},{},{},{},{:.4},{},{:.5},{},{},{},{},{:.5},{:.5},{:.5},{}",
    tick,
    pop,
    births,
    deaths,
    avg_energy,
    lineage.len(),
    avg_stress_level,
    memory_archive.record_count(),
    // NEW COLUMNS BELOW
    archive_sample_attempts,      // u32: times cells tried to sample archive
    archive_sample_successes,     // u32: times sampling succeeded
    archive_influenced_births,    // u32: newborns with archive lessons
    lineage_diversity,            // u32: count of unique lineage_id
    top1_lineage_share,           // f32: largest lineage / total pop
    strategy_entropy,             // f32: entropy of strategy distribution
    collapse_event_count          // u32: extinctions in last 100 gens
).unwrap();
```

### 2. Metrics Computation

**File**: `bioworld_mvp/src/bio_world/engine/world.rs`

Add computation in tick loop:

```rust
// After cell processing, before logging:

// Count archive sampling
let archive_sample_attempts = cells.iter()
    .map(|c| c.archive_samples_taken)
    .sum::<u32>();

let archive_sample_successes = // track successful retrievals

let archive_influenced_births = // track births with lessons

// Lineage diversity
let mut lineage_counts: HashMap<u64, u32> = HashMap::new();
for c in &cells {
    *lineage_counts.entry(c.lineage_id).or_insert(0) += 1;
}
let lineage_diversity = lineage_counts.len() as u32;

let top1_lineage_share = lineage_counts.values()
    .max()
    .copied()
    .unwrap_or(0) as f32 / pop.max(1) as f32;

// Strategy entropy (Shannon)
let strategy_counts = cells.iter()
    .map(|c| &c.lineage_memory.preferred_strategy)
    .fold(HashMap::new(), |mut acc, s| {
        *acc.entry(s.clone()).or_insert(0) += 1;
        acc
    });
let strategy_entropy = strategy_counts.values()
    .map(|&c| {
        let p = c as f32 / pop.max(1) as f32;
        -p * p.ln()
    })
    .sum::<f32>();

// Collapse events (rolling window)
static mut COLLAPSE_HISTORY: Vec<u32> = Vec::new(); // or use proper state
let collapse_event_count = // count extinctions in last 100 generations
```

### 3. JSONL Export (Optional but Recommended)

**New file**: `bioworld_mvp/src/bio_world/output/jsonl_exporter.rs`

```rust
use serde_json;
use std::fs::File;
use std::io::Write;

pub struct JsonlExporter {
    file: File,
}

impl JsonlExporter {
    pub fn new(path: &str) -> Self {
        Self {
            file: File::create(path).unwrap(),
        }
    }
    
    pub fn write_generation(&mut self, state: &GenerationState) {
        let json = serde_json::json!({
            "timestamp": chrono::Utc::now().to_rfc3339(),
            "generation": state.tick,
            "seed": state.seed,
            "universe_id": state.universe_id,
            "metrics": {
                "cdi": state.cdi,
                "ci": state.ci,
                "r": state.r,
                "n": state.pop,
                "archive_sample_attempts": state.archive_sample_attempts,
                "archive_sample_successes": state.archive_sample_successes,
                "archive_influenced_births": state.archive_influenced_births,
                "lineage_diversity": state.lineage_diversity,
                "top1_lineage_share": state.top1_lineage_share,
                "strategy_entropy": state.strategy_entropy,
                "collapse_event_count": state.collapse_event_count,
            },
            "memory_state": {
                "l1_health": state.l1_health,
                "l2_health": state.l2_health,
                "l3_health": state.l3_health,
            }
        });
        writeln!(self.file, "{}", json).unwrap();
    }
}
```

### 4. Anti-God-Mode Verification

**File**: Any (verification script)

```bash
# Run this to verify no Atlas influence on cell decisions:
grep -r "cell.*action.*atlas" bioworld_mvp/src/ || echo "✓ No Atlas control"
grep -r "archive.*override" bioworld_mvp/src/ || echo "✓ No archive override"
grep -r "global.*teacher" bioworld_mvp/src/ || echo "✓ No global teacher"
```

Expected: All should return no matches.

---

## Acceptance Criteria

- [ ] CSV contains all 8 new columns
- [ ] Values are computed correctly (sanity check: lineage_diversity >= 1)
- [ ] JSONL export works (if implemented)
- [ ] No performance regression (>5%)
- [ ] Anti-god-mode constraints still enforced

---

## Timeline

- **Day 1**: CSV column additions
- **Day 2**: JSONL export (optional)
- **Day 3**: Integration test with Atlas-HEC

---

## Questions?

See: `docs/integration/open-questions.md`

Contact: Atlas-HEC team via GitHub issues

---

**Ready for Implementation**: Yes  
**Blocking Issues**: None  
**Estimated Effort**: 1-2 days
