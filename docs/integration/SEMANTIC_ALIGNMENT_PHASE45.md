# Semantic Alignment: Bio-World ↔ Atlas-HEC

**Version**: v0.1.0  
**Date**: 2026-03-09  
**Status**: CLOSED - Equivalence mappings established

---

## 1. Purpose

Close the semantic gap between Bio-World's terminology (ticks, universes) and Atlas-HEC's terminology (generations, seeds) to enable data exchange and comparison.

---

## 2. Core Mappings

### 2.1 Time Units: ticks ↔ generations

| Aspect | Bio-World | Atlas-HEC | Equivalence |
|--------|-----------|-----------|-------------|
| **Term** | `tick` | `generation` | ☑ **EXACT EQUIVALENT** |
| **Start value** | 0 | 0 (or 1) | ☑ Match |
| **Increment** | +1 per step | +1 per step | ☑ Match |
| **Total count** | ~1500-2100 | ~1500-2100 | ☑ Match |

**Mapping**: `tick == generation`

**Evidence**:
```python
# From population.csv
# tick column starts at 0, increments by 1
# Represents discrete time steps in simulation
```

**Conclusion**: [Closed] No semantic gap. Direct 1:1 mapping.

---

### 2.2 Randomization: seeds ↔ seeds

| Aspect | Bio-World | Atlas-HEC | Equivalence |
|--------|-----------|-----------|-------------|
| **Term** | `seed` (in path) | `seed` | ☑ **EXACT EQUIVALENT** |
| **Values** | 101, 102, 103 | 1, 2, 3 | ☑ Semantically equivalent |
| **Purpose** | RNG initialization | RNG initialization | ☑ Match |

**Mapping**: `seed_XXX == seed_X`

**Evidence**:
```
Directory structure: p1_experiments/ctrl/seed_101/
```

**Conclusion**: [Closed] No semantic gap. Both use seed for reproducible randomness.

---

### 2.3 Parallel Instances: universes ↔ runs

| Aspect | Bio-World | Atlas-HEC | Equivalence |
|--------|-----------|-----------|-------------|
| **Term** | `universe` (u0, u1...) | `run` | ☑ **EQUIVALENT** |
| **Count per seed** | 8 (u0-u7) | Variable | ☑ Configurable |
| **Independence** | Isolated | Isolated | ☑ Match |

**Mapping**: `(seed, universe) → run`

**Evidence**:
```
Each universe directory contains independent simulation:
p1_experiments/ctrl/seed_101/u0/  ← Run 1
p1_experiments/ctrl/seed_101/u1/  ← Run 2
...
p1_experiments/ctrl/seed_103/u7/  ← Run 24
```

**Total runs calculation**:
```
3 seeds × 8 universes = 24 runs per condition
```

**Conclusion**: [Closed] Universe is Bio-World's term for independent parallel instance (run).

---

## 3. Field Mappings

### 3.1 Direct Equivalents

| Bio-World Field | Atlas Field | Status | Notes |
|----------------|-------------|--------|-------|
| `tick` | `generation` | ☑ Direct | 1:1 mapping |
| `population` | `population_size` | ☑ Direct | Same meaning |
| `births` | `birth_count` | ☑ Direct | Same meaning |
| `deaths` | `death_count` | ☑ Direct | Same meaning |

### 3.2 Approximate Equivalents

| Bio-World Field | Atlas Field | Status | Relationship |
|----------------|-------------|--------|--------------|
| `lineage_count` | `lineage_diversity` | ⚠️ Proxy | Related but not equivalent |
| `archive_record_count` | `archive_sample_successes` | ⚠️ Proxy | Different metrics |

### 3.3 Missing in Bio-World

| Atlas Field | Bio-World Equivalent | Status | Action Needed |
|-------------|---------------------|--------|---------------|
| `archive_sample_attempts` | None | ☗ Missing | Add to CSV export |
| `archive_sample_successes` | None | ☗ Missing | Add to CSV export |
| `archive_influenced_births` | None | ☗ Missing | Add to CSV export |
| `lineage_diversity` | None (has count) | ☗ Missing | Calculate from lineages |
| `top1_lineage_share` | None | ☗ Missing | Calculate from lineages |
| `strategy_entropy` | None | ☗ Missing | Calculate from strategies |
| `collapse_event_count` | None | ☗ Missing | Track collapses |

---

## 4. Critical Distinctions

### 4.1 lineage_count vs lineage_diversity

**lineage_count** (Bio-World current):
- Number of unique lineage_id values
- Simple count: `len(set(lineage_ids))`
- Range observed: 4-30

**lineage_diversity** (Atlas required):
- Effective number of lineages
- Formula: `1 / Σ(p_i²)` where `p_i = lineage_size / total`
- Range expected: 1 to N (lineage_count)

**Relationship**:
```
lineage_diversity ≤ lineage_count
Equality when all lineages equal size
Diversity = 1 when one lineage dominates
```

**Example**:
```
Population: 3000 cells
Lineage sizes: [1500, 1000, 500]
lineage_count = 3
lineage_diversity = 1 / (0.5² + 0.33² + 0.17²) = 1 / 0.39 = 2.56
```

**Conclusion**: [Action Required] Bio-World must add `lineage_diversity` field.

---

### 4.2 archive_record_count vs archive_sample_successes

**archive_record_count** (Bio-World current):
- Total records written to archive
- Cumulative over time
- Not directly comparable

**archive_sample_successes** (Atlas required):
- Successful CDI reads from archive
- Per-tick metric
- Measures archive utilization

**Relationship**: None direct. Different metrics.

**Conclusion**: [Action Required] Bio-World must add archive instrumentation.

---

## 5. Condition Naming

### 5.1 Mapping Atlas → Bio-World

| Atlas Condition | Bio-World Path | Status |
|----------------|----------------|--------|
| `baseline_full` | `p1_experiments/ctrl/` | ☑ Found |
| `no_L2` | `p1_experiments/p1a/` | ☑ Found |
| `P1B` | `p1_experiments/p1b/` | ☑ Found |
| `P1C` | `p1_experiments/p1c/` | ☑ Found |
| `L3_off` | `p1_experiments/L3_off/` | ☗ Missing |
| `L3_real_p001` | `p1_experiments/L3_real/` | ☗ Missing |
| `L3_shuffled_p001` | `p1_experiments/L3_shuffled/` | ☗ Missing |

### 5.2 Configuration Mapping

```python
# Atlas specification → Bio-World config
atlas_conditions = {
    "baseline_full": {
        "L1_enabled": True,
        "L2_enabled": True, 
        "L3_enabled": True,
        "archive_retrieval_prob": 0.001,
        "boss_enabled": False
    },
    "no_L2": {
        "L1_enabled": True,
        "L2_enabled": False,  # ← Key difference
        "L3_enabled": True,
        "archive_retrieval_prob": 0.001,
        "boss_enabled": False
    },
    "L3_off": {
        "L1_enabled": True,
        "L2_enabled": True,
        "L3_enabled": False,  # ← Key difference
        "boss_enabled": False
    },
    "L3_real_p001": {
        "L1_enabled": True,
        "L2_enabled": True,
        "L3_enabled": True,
        "archive_retrieval_prob": 0.001,
        "boss_enabled": False
    },
    "L3_shuffled_p001": {
        "L1_enabled": True,
        "L2_enabled": True,
        "L3_enabled": True,
        "archive_retrieval_prob": 0.001,
        "archive_shuffle": True,  # ← Key difference
        "boss_enabled": False
    }
}
```

---

## 6. Data Structure Alignment

### 6.1 File Organization

```
# Bio-World structure
p1_experiments/
  {condition}/
    seed_{seed_id}/
      u{universe_id}/
        population.csv
        cdi.csv
        extinction.csv

# Atlas expected structure (same)
{condition}/
  seed_{seed_id}/
    u{universe_id}/
      population.csv  ← Must have 15 fields
```

### 6.2 CSV Column Alignment

**Current (8 columns)**:
```csv
tick,population,births,deaths,avg_energy,lineage_count,avg_stress_level,archive_record_count
```

**Required (15 columns)**:
```csv
tick,population,births,deaths,avg_energy,lineage_count,avg_stress_level,archive_record_count,
archive_sample_attempts,archive_sample_successes,archive_influenced_births,lineage_diversity,
top1_lineage_share,strategy_entropy,collapse_event_count
```

---

## 7. Resolution Summary

### 7.1 Closed Issues

| Issue | Resolution | Evidence |
|-------|------------|----------|
| ticks vs generations | EXACT EQUIVALENT | Column mapping verified |
| seeds vs seeds | EXACT EQUIVALENT | Both use seed for RNG |
| universes vs runs | EQUIVALENT | (seed, universe) = run |

### 7.2 Open Issues

| Issue | Action | Owner | Priority |
|-------|--------|-------|----------|
| Add 7 new fields | Implement in export_csv | Bio-World | CRITICAL |
| Add L3_off runs | Create condition config | Bio-World | CRITICAL |
| Add L3_shuffled runs | Create condition config | Bio-World | CRITICAL |
| lineage_count vs diversity | Document distinction | Atlas | MEDIUM |

---

## 8. Implementation Checklist

### For Bio-World

- [ ] Add `archive_sample_attempts` to CSV export
- [ ] Add `archive_sample_successes` to CSV export
- [ ] Add `archive_influenced_births` to CSV export
- [ ] Add `lineage_diversity` calculation and export
- [ ] Add `top1_lineage_share` calculation and export
- [ ] Add `strategy_entropy` calculation and export
- [ ] Add `collapse_event_count` tracking and export
- [ ] Create `L3_off` experiment configuration
- [ ] Create `L3_real_p001` experiment configuration
- [ ] Create `L3_shuffled_p001` experiment configuration
- [ ] Run 72 new experiments (3 conditions × 3 seeds × 8 universes)

### For Atlas-HEC

- [ ] Verify CSV column order matches specification
- [ ] Update data loader to handle new fields
- [ ] Document `lineage_count` vs `lineage_diversity` distinction
- [ ] Prepare triage re-analysis scripts

---

## 9. Conclusion

**Semantic Closure Status**: ☑ CLOSED (with action items)

**Summary**:
1. Core terminology differences resolved (ticks=generations, universes=runs)
2. Field gaps identified (7 missing fields)
3. Condition gaps identified (3 missing conditions)
4. Clear implementation path defined

**Next Step**: Execute minimal rerun with complete field set.

---

**Document Status**: COMPLETE  
**Alignment Confidence**: HIGH  
**Blockers Resolved**: Yes (terminology)  
**New Blockers**: Implementation needed (fields and conditions)
