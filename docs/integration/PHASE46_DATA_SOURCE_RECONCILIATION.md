# Phase 4.6 Data Source Reconciliation

**Role**: Adjudication Finalizer  
**Date**: 2026-03-09  
**Status**: RECONCILIATION_COMPLETE  

---

## 1. Data Sources

### 1.1 Local Sentinel Outputs

**Location**: `/tmp/bio-world/p1_experiments/`

| Condition | Path | Status | Generations |
|-----------|------|--------|-------------|
| ctrl | `p1_experiments/ctrl/` | ✅ Available | 2100 |
| p1a | `p1_experiments/p1a/` | ✅ Available | 1500 |
| p1b | `p1_experiments/p1b/` | ✅ Available | 1500 |
| p1c | `p1_experiments/p1c/` | ✅ Available | 1500 |

**CSV Columns**: 8 (tick, population, births, deaths, avg_energy, lineage_count, avg_stress_level, archive_record_count)

**Schema Version**: V1 (Legacy)

---

### 1.2 GitHub Experiment CSVs

**Location**: `https://github.com/Ectrox-Lab/bio-world/tree/main/runs`

| Experiment | File | Condition | Generations |
|------------|------|-----------|-------------|
| A | `experiment_a_survival.csv` | baseline_full | 1000 |
| B | `experiment_b_evolution.csv` | evolution | 1000 |
| C_LOW | `experiment_c_pressure_low.csv` | low_pressure | 1000 |
| C_HIGH | `experiment_c_pressure_high.csv` | high_pressure | 1000 |
| D | `experiment_d_cooperation.csv` | cooperation | 1000 |
| E_OFF | `experiment_e_akashic_off.csv` | **L3_off** | 1000 |
| E_ON | `experiment_e_akashic_on.csv` | **L3_real** | 1000 |

**CSV Columns**: 19 (extended schema)

**Schema Version**: V2 (Current)

---

## 2. Schema Comparison

### 2.1 Common Columns

| Column | Local V1 | GitHub V2 | Compatible? |
|--------|----------|-----------|-------------|
| tick | ✅ | ✅ | Yes |
| population | ✅ | ✅ | Yes |
| births | ✅ | ✅ | Yes |
| deaths | ✅ | ✅ | Yes |
| lineage_count | ✅ | ✅ | Yes |

### 2.2 GitHub V2 Only

| Column | Status | Notes |
|--------|--------|-------|
| generation | ✅ Present | Redundant with tick |
| average_energy | ✅ Present | Renamed from avg_energy |
| dna_variance | ✅ Present | New metric |
| cooperation_rate | ✅ Present | New metric |
| mean_cluster_size | ✅ Present | New metric |
| multi_cell_boss_success_rate | ✅ Present | New metric |
| energy_transfer_count | ✅ Present | New metric |
| signal_synchrony | ✅ Present | New metric |
| mutation_count | ✅ Present | New metric |
| nonzero_mutation_generations | ✅ Present | New metric |
| elite_lineage_survival | ✅ Present | New metric |
| adaptation_gain | ✅ Present | Key outcome metric |
| extinction_events | ✅ Present | Proxy for collapse |
| cdi | ✅ Present | Collective Digital Intelligence |

### 2.3 Local V1 Only

| Column | Status | GitHub Equivalent |
|--------|--------|-------------------|
| avg_stress_level | ❌ Missing | None |
| archive_record_count | ❌ Missing | None directly |

---

## 3. Reconciliation Rules

### 3.1 Mergeable Data

| Data Type | Can Merge | How | Quality |
|-----------|-----------|-----|---------|
| Population dynamics | ✅ Yes | Common columns | High |
| Lineage counts | ✅ Yes | Direct mapping | High |
| Birth/death rates | ✅ Yes | Common columns | High |
| Energy metrics | ⚠️ Partial | avg_energy vs average_energy | Medium |

### 3.2 Non-Mergeable Data

| Data Type | Can Merge | Reason | Recommendation |
|-----------|-----------|--------|----------------|
| Adaptation gain | ❌ No | Only in GitHub | Use GitHub only |
| CDI | ❌ No | Only in GitHub | Use GitHub only |
| Cooperation rate | ❌ No | Only in GitHub | Use GitHub only |
| Stress level | ❌ No | Only in Local | Discard or re-export |

### 3.3 Semantic Conflicts

| Conflict | Risk | Resolution |
|----------|------|------------|
| tick vs generation | LOW | Both 0-indexed, equivalent |
| avg_energy vs average_energy | NONE | Same metric, different name |
| archive_record_count vs cdi | MEDIUM | Different concepts, don't mix |
| lineage_count semantics | LOW | Same calculation |

---

## 4. Source Quality Assessment

### 4.1 GitHub Data (Preferred)

**Strengths**:
- ✅ 19 CSV columns (rich metrics)
- ✅ Contains critical L3_off and L3_real
- ✅ Adaptation_gain metric (key outcome)
- ✅ CDI metric (diversity proxy)
- ✅ Consistent 1000 generations
- ✅ 8 universes per condition

**Weaknesses**:
- ❌ L3_shuffled missing
- ❌ no_L2 missing
- ❌ No archive instrumentation fields

**Verdict**: 🟢 **PRIMARY SOURCE**

### 4.2 Local Data (Secondary)

**Strengths**:
- ✅ ctrl condition available
- ✅ Longer generations (1500-2100)
- ✅ No network dependency

**Weaknesses**:
- ❌ Only 8 columns
- ❌ Missing key outcome metrics
- ❌ No L3_off, L3_real
- ❌ Different schema version
- ❌ Incompatible with GitHub metrics

**Verdict**: 🟡 **AUXILIARY ONLY - Do not merge**

---

## 5. Unified Data Strategy

### 5.1 Primary Analysis

**Use**: GitHub data only

**Rationale**:
- Contains all critical comparisons (L3_off vs L3_real)
- Rich metrics enable comprehensive analysis
- Consistent schema
- Verified outputs

### 5.2 Secondary Validation

**Use**: Local data for specific checks

**Allowed Uses**:
- Verify population stability trends
- Cross-check lineage count calculations
- Validate no crashes or anomalies

**Prohibited Uses**:
- Merge with GitHub metrics
- Compare adaptation_gain (not present)
- Compare CDI (not present)

### 5.3 Data Selection Matrix

| Analysis | Source | Reason |
|----------|--------|--------|
| L3 effect validation | GitHub | Has L3_off, L3_real |
| Baseline performance | GitHub | Has adaptation_gain |
| Pressure effects | GitHub | Has C_LOW, C_HIGH |
| Schema comparison | Local + GitHub | Document differences |
| Archive engagement | Neither | Missing instrumentation |

---

## 6. Conflicts and Resolutions

### 6.1 Identified Conflicts

| Conflict | Severity | Resolution |
|----------|----------|------------|
| Different tick counts | LOW | GitHub uses 1000, Local uses 1500-2100; normalize by percentage |
| Missing adaptation_gain in Local | MEDIUM | Cannot compare; don't merge |
| Column name differences | LOW | Map avg_energy ↔ average_energy |
| Archive metrics missing | HIGH | Cannot validate archive engagement |

### 6.2 No-Conflict Zones

| Zone | Status | Notes |
|------|--------|-------|
| Population dynamics | ✅ Clean | Same scale, same trends |
| Lineage counts | ✅ Clean | Same calculation method |
| Extinction events | ✅ Clean | Both track (different names) |

---

## 7. Recommendations

### 7.1 For Current Analysis

1. **Use GitHub data as primary source**
   - All key comparisons available
   - Rich metrics enable full analysis

2. **Do NOT merge with Local data**
   - Schema incompatibility
   - Missing key metrics in Local
   - Different time scales

3. **Reference Local data only for**
   - Methodology validation
   - Sanity checks
   - Not for quantitative comparison

### 7.2 For Future Data Collection

1. **Standardize on GitHub V2 schema**
   - 19 columns minimum
   - Include adaptation_gain
   - Include CDI

2. **Add missing instrumentation**
   - archive_sample_attempts
   - archive_sample_successes
   - lineage_diversity calculation

3. **Extend to 5000 ticks**
   - Better statistical power
   - Consistent with minimal rerun spec

---

## 8. Reconciliation Summary

### Final Verdict

| Aspect | Decision |
|--------|----------|
| Primary source | GitHub experiment CSVs |
| Merge Local + GitHub | ❌ NO - Do not merge |
| Use Local as auxiliary | ✅ YES - For validation only |
| Schema standard | GitHub V2 (19 columns) |
| Missing critical data | L3_shuffled, no_L2 |

### Action Items

| Item | Priority | Owner |
|------|----------|-------|
| Generate L3_shuffled | CRITICAL | bio-world |
| Generate no_L2 | HIGH | bio-world |
| Archive instrumentation | MEDIUM | bio-world |
| Discard Local V1 data | LOW | atlas-hec |

---

## 9. Data Source Inventory

### Available for Analysis

| Source | Conditions | Quality | Use |
|--------|------------|---------|-----|
| GitHub | 7 complete | HIGH | Primary |
| Local | 4 partial | MEDIUM | Auxiliary |

### Missing for Complete Analysis

| Data | Blocks | Priority |
|------|--------|----------|
| L3_shuffled | R1 validation | CRITICAL |
| no_L2 | R3 validation | HIGH |
| Archive fields | Engagement metrics | MEDIUM |

---

**Reconciliation Status**: COMPLETE  
**Recommendation**: Use GitHub exclusively, generate missing conditions  
**Analyst**: Atlas-HEC Phase 4.6 Lead
