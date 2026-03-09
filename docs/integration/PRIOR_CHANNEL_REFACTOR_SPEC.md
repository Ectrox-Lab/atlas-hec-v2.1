# PriorChannel Refactor Specification v0.1

**Status**: IMPLEMENTATION READY  
**Date**: 2026-03-10  
**Scope**: Archive → PriorChannel  
**Rationale**: Phase 5-7 complete, mechanism proven, time to converge  

---

## Executive Summary

**Research Phase**: COMPLETE  
- Phase 5: Content-bearing ❌ FALSIFIED  
- Phase 6 H1: Generic-prior ✅ SUPPORTED  
- Phase 7: Optimal point found (p=0.01, α=medium)  

**Engineering Phase**: BEGIN  
- Rename: Archive → PriorChannel  
- Simplify: Remove content-bearing logic  
- Lock: Default parameters (p=0.01, α=medium)  
- Verify: Minimal sanity check  

---

## 1. Terminology Migration Table

### 1.1 Code Entities

| Old Name | New Name | File Locations |
|----------|----------|----------------|
| `CausalArchive` | `PriorChannel` | `memory/causal_archive.rs` |
| `ArchiveRecord` | `PriorSample` | `memory/causal_archive.rs` |
| `archive` | `channel` / `prior` | All files |
| `sample_from_archive` | `sample_prior` | `engine/world.rs` |
| `archive_write` | `prior_inject` | `memory/` |
| `ARCHIVE_SAMPLE_PROB` | `PRIOR_SAMPLE_PROB` | `memory/constants.rs` |

### 1.2 Variables & Fields

| Old | New | Context |
|-----|-----|---------|
| `archive_sample_attempts` | `prior_sample_attempts` | Metrics CSV |
| `archive_sample_successes` | `prior_sample_successes` | Metrics CSV |
| `archive_influenced_births` | `prior_influenced_births` | Metrics CSV |
| `memory_archive` | `prior_channel` | `engine/world.rs` |
| `distilled_lessons` | `injected_priors` | `lineage_memory.rs` |

### 1.3 Documentation

| Old Term | New Term | Rationale |
|----------|----------|-----------|
| "Three-layer memory" | "Three-layer control" | L3 is not memory |
| "Content-bearing archive" | "Low-bandwidth prior channel" | Content irrelevant |
| "Historical inheritance" | "Generic stabilization" | No history transfer |
| "Compressed wisdom" | "Weak regularization" | No wisdom, just bias |
| "Ancestral strategy" | "Prior injection" | No ancestry |
| "Archive access" | "Prior sampling" | Sampling from distribution |

---

## 2. Logic to Delete

### 2.1 Content Storage (DELETED)

```rust
// REMOVE: Recording detailed history
pub fn queue_record(&mut self, record: CausalArchiveRecord) {
    // OLD: Store detailed event history
    self.write_queue.push_back(record);
}

// REMOVE: Maintaining record database
pub records: Vec<CausalArchiveRecord>,

// REMOVE: Compression of historical content
pub fn compress_to_lesson(record: &CausalArchiveRecord) -> DistilledLesson
```

**Why Delete**: Content not used, proven irrelevant in Phase 5-6.

### 2.2 Lineage-Indexed Retrieval (DELETED)

```rust
// REMOVE: Lineage-specific archive reads
if let Some(record) = memory_archive
    .random_sample(&mut rng, &ArchiveSamplingPolicy::default())
{
    // OLD: Look up lineage-specific content
    let lesson = CausalArchive::compress_to_lesson(record);
}
```

**Why Delete**: Content irrelevant, generic prior sufficient.

### 2.3 Complex Write Logic (DELETED)

```rust
// REMOVE: Write queue processing
pub fn process_queue(&mut self) {
    while self.writes_this_window < MAX_ARCHIVE_WRITE_RATE {
        // OLD: Process historical writes
    }
}

// REMOVE: Write rate limiting
writes_this_window: u32,
MAX_ARCHIVE_WRITE_RATE: u32,
```

**Why Delete**: No need to store content, no write rate to manage.

---

## 3. Mechanism to Preserve

### 3.1 Prior Sampling (RETAINED)

```rust
// KEEP: Sampling mechanism
pub fn sample_prior(&mut self, rng: &mut Rng, p: f32) -> Option<PriorValue> {
    if rng.bool(p) {
        Some(self.generate_prior(rng))
    } else {
        None
    }
}
```

**Why Keep**: Core mechanism for low-bandwidth injection.

### 3.2 Prior Generation (RETAINED, SIMPLIFIED)

```rust
// KEEP: Generate generic prior
pub fn generate_prior(&self, rng: &mut Rng) -> PriorValue {
    // NEW: Simple distribution, no content lookup
    PriorValue {
        strategy_bias: self.sample_strategy_bias(rng),
        strength: self.prior_strength,
    }
}

// SIMPLIFIED: No history lookup, just distribution sampling
fn sample_strategy_bias(&self, rng: &mut Rng) -> Strategy {
    // Sample from fixed prior distribution
    // Not from historical content
}
```

**Why Keep**: Generic prior effect proven in Phase 6-7.

### 3.3 Prior Injection (RETAINED)

```rust
// KEEP: Inject prior into agent state
pub fn push_prior(&mut self, prior: PriorValue) {
    self.current_prior = Some(prior);
    self.prior_history.push(prior);
}

// KEEP: Prior influence on behavior
fn apply_prior_to_strategy(&self, base_strategy: Strategy) -> Strategy {
    if let Some(prior) = self.current_prior {
        // Blend base strategy with prior bias
        // Strength controlled by prior_strength
        lerp(base_strategy, prior.strategy_bias, prior.strength)
    } else {
        base_strategy
    }
}
```

**Why Keep**: Mechanism for weak regularization effect.

### 3.4 Configuration (RETAINED, LOCKED)

```rust
// LOCKED: Default parameters from Phase 7
pub const DEFAULT_PRIOR_SAMPLE_PROB: f32 = 0.01;  // p=0.01 optimal
pub const DEFAULT_PRIOR_STRENGTH: f32 = 0.5;       // α=medium

// CONFIGURABLE: For experimentation
pub struct PriorChannelConfig {
    pub sample_probability: f32,  // p: [0.0, 1.0]
    pub prior_strength: f32,      // α: [0.0, 1.0]
    pub prior_distribution: PriorDistribution,
}
```

**Why Keep**: Proven parameters, but flexibility for future tuning.

---

## 4. Default Parameters (LOCKED)

### 4.1 Phase 7 Optimal (DEFAULT)

```yaml
# Default configuration - DO NOT CHANGE without Phase 8 validation
prior_channel:
  sample_probability: 0.01    # p=0.01 from Phase 7
  prior_strength: 0.5         # α=medium
  
# Effects observed at this setting:
# - lineage_diversity: +93.9% vs baseline
# - top1_lineage_share: -28.7% (reduced dominance)
# - no overdriven symptoms
# - robust across p range
```

### 4.2 Parameter Ranges (FOR EXPERIMENTATION)

```yaml
# Valid ranges if modification needed
sample_probability:
  min: 0.001    # Too weak but still effective
  max: 0.1      # Risk of overdriven
  
prior_strength:
  weak: 0.1     # Minimal effect
  medium: 0.5   # DEFAULT
  strong: 0.9   # Risk of over-constraint
```

---

## 5. Implementation Steps

### Step 1: File Rename

```bash
# Rename files
git mv src/bio_world/memory/causal_archive.rs \
       src/bio_world/memory/prior_channel.rs

# Update module declarations
# In src/bio_world/memory/mod.rs:
pub mod prior_channel;  // WAS: pub mod causal_archive;
```

### Step 2: Struct Rename

```rust
// In prior_channel.rs:
pub struct PriorChannel {  // WAS: CausalArchive
    // Simplified: Remove records, write_queue
    pub prior_distribution: PriorDistribution,
    pub config: PriorChannelConfig,
}

pub struct PriorValue {  // WAS: DistilledLesson / ArchiveRecord
    pub strategy_bias: Strategy,
    pub strength: f32,
}
```

### Step 3: Method Simplification

```rust
impl PriorChannel {
    // NEW: Simple prior generation
    pub fn sample_prior(&mut self, rng: &mut Rng) -> Option<PriorValue> {
        if rng.bool(self.config.sample_probability) {
            Some(self.generate_prior(rng))
        } else {
            None
        }
    }
    
    // NEW: Generate from distribution, not history
    fn generate_prior(&self, rng: &mut Rng) -> PriorValue {
        PriorValue {
            strategy_bias: self.config.prior_distribution.sample(rng),
            strength: self.config.prior_strength,
        }
    }
    
    // DELETED: queue_record, process_queue, compress_to_lesson
}
```

### Step 4: Usage Update

```rust
// In engine/world.rs:
// WAS: if let Some(record) = memory_archive.random_sample(...) {
//       let lesson = CausalArchive::compress_to_lesson(record);

// NEW:
if let Some(prior) = prior_channel.sample_prior(&mut rng) {
    child_lineage.push_prior(prior);
}
```

### Step 5: Metric Rename

```rust
// In experiment_runner.rs:
// WAS: "archive_sample_attempts,archive_sample_successes,..."
// NEW: "prior_sample_attempts,prior_sample_successes,..."

metrics: {
    prior_sample_attempts: u64,
    prior_sample_successes: u64,
    prior_influenced_births: u64,
}
```

### Step 6: Documentation Update

```markdown
# WAS: Three-Layer Memory System
# NEW: Three-Layer Control Architecture

L1: Intrinsic mortality control
L2: Lineage tracking control  
L3: Prior channel (weak regularization)  // WAS: Archive
```

---

## 6. Minimal Sanity Rerun

### 6.1 Purpose

Verify refactor maintains Phase 7 results.

### 6.2 Conditions

```yaml
sanity_check:
  baseline: true           # Control
  prior_channel_p0.01: true  # Refactored L3
  
parameters:
  ticks: 5000
  universes: 8
```

### 6.3 Success Criteria

| Metric | Baseline | PriorChannel | Required |
|--------|----------|--------------|----------|
| lineage_diversity | ~0.0077 | ~0.015 | +80% minimum |
| top1_lineage_share | ~0.73 | ~0.52 | -25% minimum |
| no overdriven | - | YES | Must pass |

### 6.4 Fail Conditions

| Fail | Action |
|------|--------|
| Effect size < 50% of Phase 7 | Debug refactor, check parameter passing |
| Overdriven symptoms | Check prior strength config |
| No effect | Verify sampling probability |

---

## 7. Files to Modify

### 7.1 Core Files

```
src/bio_world/memory/
  ├── mod.rs                    # Update module name
  ├── causal_archive.rs -> prior_channel.rs  # Rename + simplify
  
src/bio_world/engine/
  ├── world.rs                  # Update usage, variable names
  ├── experiment_runner.rs      # Update metrics, CSV headers
  
src/bio_world/
  ├── constants.rs              # Rename ARCHIVE_* to PRIOR_*
```

### 7.2 Documentation

```
docs/integration/
  ├── STATUS.md                 # Update terminology
  ├── ARCHITECTURE.md           # Rename three-layer memory → control
  ├── EXPERIMENTS.md            # Update all experiment descriptions
  
docs/candidates/
  ├── candidate_002_intake.md   # Update references (if any)
```

### 7.3 Tests

```
src/bio_world/memory/
  └── tests/                    # Update test names, assertions
```

---

## 8. Verification Checklist

### Pre-Refactor

- [ ] Phase 7 results backed up
- [ ] All tests passing
- [ ] Git commit: "[pre-refactor] Archive baseline"

### During Refactor

- [ ] Files renamed
- [ ] Structs renamed
- [ ] Content logic removed
- [ ] Prior logic implemented
- [ ] Compiles without errors

### Post-Refactor

- [ ] Sanity rerun executed
- [ ] Effect size comparable to Phase 7
- [ ] No overdriven symptoms
- [ ] Documentation updated
- [ ] Git commit: "[refactor] Archive→PriorChannel"

### Final

- [ ] All references to "archive" removed from docs
- [ ] All references to "memory" updated to "control"
- [ ] Architecture diagram updated
- [ ] Team aligned on new terminology

---

## Sign-off

| Item | Status |
|------|--------|
| Research complete | ✅ Phase 5-7 done |
| Mechanism proven | ✅ Generic prior validated |
| Optimal params found | ✅ p=0.01, α=medium |
| Ready to implement | ✅ This spec |

**Decision**: Begin refactor immediately  
**Estimated Duration**: 2-3 days  
**Risk**: Low (mechanism proven, just renaming/simplifying)

---

**Spec Version**: 0.1-FINAL  
**Next Step**: Execute refactor, run sanity check, lock configuration
