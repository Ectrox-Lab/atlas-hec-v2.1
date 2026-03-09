# FROZEN STATE v1 - Post Phase 7

**Date**: 2026-03-10  
**Status**: RESEARCH COMPLETE → ENGINEERING CONVERGENCE  
**Scope**: L3/PriorChannel Architecture  

---

## 🧊 Frozen Research Conclusions

### DEFINITELY FALSE (Do Not Revisit)

| Old Hypothesis | Status | Evidence |
|----------------|--------|----------|
| Content-bearing archive | ❌ FALSIFIED | Phase 5: L3_real ≈ L3_shuffled (δ=-1.7%, p=0.72) |
| Compressed content utility | ❌ FALSIFIED | Phase 5-6: Content shape irrelevant |
| Historical inheritance | ❌ FALSIFIED | No history transfer mechanism found |
| Ancestral wisdom | ❌ FALSIFIED | No wisdom, no ancestry |

**Action**: Remove from all docs, narratives, implementations.

### DEFINITELY TRUE (Lock In)

| New Understanding | Status | Evidence |
|-------------------|--------|----------|
| Generic prior channel | ✅ PROVEN | Phase 6 H1: constant ≈ random ≈ real ≠ off |
| Weak regularizer | ✅ PROVEN | +82-94% diversity gain, d=3.4-5.3 |
| Stabilization mechanism | ✅ PROVEN | Reduced dominance, no extinction |

**Action**: Base all future work on these mechanisms.

---

## 🧊 Frozen Default Parameters

### LOCKED Configuration

```yaml
# DO NOT CHANGE without Phase 8 validation study
prior_channel:
  sample_probability: 0.01    # p=0.01 from Phase 7 center axis
  prior_strength: 0.5         # α=medium
  
# Rationale: 
# - p=0.01 showed +93.9% diversity gain (optimal)
# - p=0.001 and p=0.05 also effective but suboptimal
# - No overdriven symptoms at p=0.01
# - Robust across α range
```

### Valid Ranges (For Experimentation Only)

```yaml
# If modification absolutely necessary
sample_probability:
  absolute_min: 0.001   # Still effective but weak
  default: 0.01         # ★ LOCKED ★
  absolute_max: 0.05    # Risk of overdriven beyond this
  
prior_strength:
  weak: 0.1             # Minimal effect
  medium: 0.5           # ★ LOCKED ★
  strong: 0.9           # Risk of over-constraint
```

**Policy**: Default parameters require council approval to change.

---

## 🧊 Frozen Terminology

### REQUIRED Terms (Use These)

| Context | Term | Rationale |
|---------|------|-----------|
| L3 mechanism | "PriorChannel" | Accurate description of function |
| L3 mechanism | "generic prior" | Content-agnostic bias |
| L3 mechanism | "weak regularizer" | Strength characterization |
| L3 mechanism | "stabilization channel" | Effect on system |
| Architecture | "three-layer control" | L3 is not memory |
| Event type | "prior injection" | Not "archive access" |
| Event type | "prior sampling" | Not "memory retrieval" |
| Variable | "prior_sample_attempts" | Not "archive_sample_attempts" |
| Variable | "prior_influenced_births" | Not "archive_influenced_births" |

### FORBIDDEN Terms (Never Use)

| Forbidden Term | Why Forbidden | Replacement |
|----------------|---------------|-------------|
| "Archive" | Implies storage | "PriorChannel" |
| "Memory" | Implies retention | "Control" |
| "Content-bearing" | Proven false | "Generic" |
| "Historical" | No history transfer | "Prior" |
| "Ancestral" | No ancestry | "Channel" |
| "Wisdom" | No knowledge accumulation | "Regularization" |
| "Inheritance" | No information transfer | "Injection" |
| "Compressed" | Irrelevant mechanism | "Weak" |
| "Lessons" | Pedagogical metaphor | "Priors" |
| "Distilled" | Content processing | "Generated" |

### Architecture Rename

```diff
- Three-Layer Memory System
+ Three-Layer Control Architecture

  L1: Intrinsic mortality control
  L2: Lineage tracking control
- L3: Archive layer (content storage)
+ L3: PriorChannel (generic prior injection)
```

---

## 🧊 Frozen Narratives (DISABLED)

### These Storylines Are BANNED

| Banned Narrative | Why | What Happens If Used |
|------------------|-----|---------------------|
| "Agents inherit strategies from ancestors" | False | Reverts to falsified model |
| "Archive preserves historical wisdom" | False | Wrong abstraction |
| "Content compression enables transfer" | False | Irrelevant complexity |
| "L3 is a memory layer" | False | Misleading design decisions |
| "Ancestral knowledge guides descendants" | False | Anthropomorphic error |
| "The system remembers its history" | False | Observer bias |

### Allowed Narratives

| Correct Narrative | Usage |
|-------------------|-------|
| "Low-bandwidth generic prior stabilizes population" | Accurate description |
| "Sampling frequency modulates regularization strength" | Mechanistic |
| "Prior injection reduces dominance extinction" | Observable effect |
| "Weak channel provides behavioral bias" | Content-agnostic |

---

## 🧊 Frozen Implementation Decisions

### TO DELETE (Immediately)

```rust
// Content storage
pub records: Vec<CausalArchiveRecord>
pub fn queue_record(&mut self, record: CausalArchiveRecord)
pub fn process_queue(&mut self)

// Historical retrieval
pub fn random_sample(&self, ...) -> Option<&CausalArchiveRecord>
pub fn compress_to_lesson(record: &CausalArchiveRecord) -> DistilledLesson

// Write management
writes_this_window: u32
MAX_ARCHIVE_WRITE_RATE: u32
```

### TO PRESERVE (Simplify)

```rust
// Core sampling
pub fn sample_prior(&mut self, rng: &mut Rng) -> Option<PriorValue>

// Prior generation (distribution-based, not history-based)
pub fn generate_prior(&self, rng: &mut Rng) -> PriorValue

// Prior injection
pub fn push_prior(&mut self, prior: PriorValue)
pub fn apply_prior_to_strategy(&self, base: Strategy) -> Strategy
```

### TO LOCK (Parameters)

```rust
pub const DEFAULT_PRIOR_SAMPLE_PROB: f32 = 0.01;  // ★ FROZEN ★
pub const DEFAULT_PRIOR_STRENGTH: f32 = 0.5;       // ★ FROZEN ★
```

---

## 🧊 Frozen Documentation State

### Documents to Update

| Document | Changes Required |
|----------|------------------|
| `README.md` | "Memory" → "Control" |
| `ARCHITECTURE.md` | Rename L3, remove content descriptions |
| `EXPERIMENTS.md` | Update all experiment descriptions |
| `PHASE*.md` | Keep for history, add note about terminology evolution |
| Code comments | Replace all "archive", "memory", "content" references |

### Documents to Create

| Document | Purpose |
|----------|---------|
| `FROZEN_STATE_v1.md` | This file - locks all conclusions |
| `TERMINOLOGY_GUIDE.md` | Migration guide for team |
| `IMPLEMENTATION_LOG.md` | Track refactor progress |

---

## 🧊 Frozen Verification Criteria

### Sanity Rerun Success

```yaml
must_pass:
  lineage_diversity_gain: "> 80% vs baseline"
  top1_lineage_share_reduction: "> 20% vs baseline"
  no_overdriven: true
  effect_size: "d > 3.0"
  
must_not_have:
  content_logic: "any remaining"
  archive_references: "in code or docs"
  old_terminology: "in user-facing text"
```

### Fail Conditions (Block Release)

| Fail | Action |
|------|--------|
| Effect size < 50% of Phase 7 | Debug refactor |
| Overdriven symptoms | Check prior strength |
| No effect | Verify sampling probability |
| Content logic remaining | Complete deletion |
| Old terminology in UI | Global replace |

---

## 🧊 Change Control

### What Requires Approval

| Change | Approval Required |
|--------|-------------------|
| Default parameters (p, α) | Research lead + Engineering lead |
| Terminology additions | Documentation lead |
| Re-enable content logic | Full council (unlikely) |
| Architecture changes | All stakeholders |

### What Does NOT Require Approval

| Change | Authority |
|--------|-----------|
| Bug fixes | Developer |
| Performance optimization | Developer |
| Additional metrics | Research lead |
| Visualization improvements | Designer |

---

## Sign-off

| Role | Name | Date | Status |
|------|------|------|--------|
| Research Lead | Atlas-HEC | 2026-03-10 | ✅ Research complete |
| Engineering Lead | (pending) | - | Awaiting refactor |
| Documentation Lead | (pending) | - | Awaiting terminology guide |

---

**Frozen State Version**: 1.0  
**Frozen Until**: Phase 8 validation (if ever)  
**Next Action**: Execute PRIOR_CHANNEL_REFACTOR_SPEC  
**Emergency Thaw**: Council unanimous vote only
