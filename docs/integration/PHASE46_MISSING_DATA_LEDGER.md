# Phase 4.6 Missing Data Ledger

**Role**: Missing-Data Closure Lead  
**Date**: 2026-03-09  
**Status**: AUDIT_COMPLETE  

---

## 1. Missing Conditions

| Condition | File/Location | Status | Blocking | Owner | Minimal Fix | Rerun? |
|-----------|--------------|--------|----------|-------|-------------|--------|
| **L3_shuffled_p001** | `experiment_e_akashic_shuffled.csv` | ❌ MISSING | **YES** - Blocks R1 validation | bio-world | Add shuffle flag to archive retrieval | **YES** - 8 universes × 5000 ticks |
| **no_L2** | `experiment_no_L2.csv` | ❌ MISSING | **YES** - Blocks R3 validation | bio-world | Set `L2_enabled=false` | **YES** - 8 universes × 5000 ticks |
| no_L1 | `experiment_no_L1.csv` | ❌ MISSING | NO - Optional sentinel | bio-world | Set `L1_enabled=false` | Optional |
| L3_overpowered_direct | `experiment_L3_overpowered.csv` | ❌ MISSING | NO - Optional stress test | bio-world | Set `archive_retrieval_prob=0.1` | Optional |

### Blocking Analysis

**CRITICAL BLOCKERS (2)**:
1. **L3_shuffled_p001**: Without this, cannot validate falsification rule R1 (L3 content irrelevance). If L3_real ≈ L3_shuffled, hypothesis fails.
2. **no_L2**: Without this, cannot validate R3 (L2 degeneration). Weakens lineage mechanism evidence.

---

## 2. Missing CSV Columns

| Column | Required By | Status | Blocking | Owner | Minimal Fix | Rerun? |
|--------|-------------|--------|----------|-------|-------------|--------|
| **archive_sample_attempts** | Atlas contract v0.1.0 | ❌ MISSING | **YES** - Blocks archive engagement metrics | bio-world | Add counter in CDI.read_archive() | NO - Can add to existing runs via re-export |
| **archive_sample_successes** | Atlas contract v0.1.0 | ❌ MISSING | **YES** - Paired with attempts | bio-world | Add counter for non-null returns | NO - Re-export only |
| **archive_influenced_births** | Atlas contract v0.1.0 | ❌ MISSING | **YES** - Key outcome metric | bio-world | Track birth strategy source | NO - Re-export only |
| **lineage_diversity** | Atlas contract v0.1.0 | ❌ MISSING | **YES** - Better than lineage_count | bio-world | Calculate 1/Σ(p²) | NO - Can compute from existing data |
| **top1_lineage_share** | Atlas contract v0.1.0 | ❌ MISSING | **YES** - Dominance metric | bio-world | Track max lineage proportion | NO - Can compute from existing |
| **strategy_entropy** | Atlas contract v0.1.0 | ❌ MISSING | NO - Nice to have | bio-world | Calculate Shannon entropy | NO - Optional |
| collapse_event_count | Atlas contract v0.1.0 | ⚠️ PROXY | NO - Use extinction_events | bio-world | Threshold detection | NO - Optional |

### Blocking Analysis

**FIELD BLOCKERS (5)**:
- archive_sample_attempts / successes / influenced_births: Core archive mechanism metrics
- lineage_diversity / top1_lineage_share: Better lineage structure metrics than raw count

**Note**: These can be added via **re-export** from existing simulation logs without re-running.

---

## 3. Missing Comparison Results

| Comparison | Required For | Status | Blocking | Owner | Minimal Fix | Rerun? |
|------------|--------------|--------|----------|-------|-------------|--------|
| **L3_real vs L3_shuffled** | R1 validation | ❌ MISSING | **YES** - Core falsification test | atlas-hec | Run shuffled condition | **YES** |
| **baseline vs no_L2** | R3 validation | ❌ MISSING | **YES** - L2 necessity proof | atlas-hec | Run no_L2 condition | **YES** |
| no_L1 vs baseline | Optional analysis | ❌ MISSING | NO - Optional | atlas-hec | Run no_L1 if time permits | Optional |
| L3_overpowered vs L3_real | Stress test | ❌ MISSING | NO - Optional | atlas-hec | Run overpowered variant | Optional |
| GitHub vs Local data merge | Unified analysis | ⚠️ PARTIAL | NO - Can use separately | atlas-hec | Reconcile schemas | NO |

---

## 4. Missing Anti-God-Mode Evidence

| Evidence Type | Required For | Status | Blocking | Owner | Minimal Fix | Rerun? |
|---------------|--------------|--------|----------|-------|-------------|--------|
| **L3_shuffled ≈ L3_off** | Prove content matters | ❌ MISSING | **YES** - Strong evidence | bio-world | Run both, compare | **YES** |
| No L3 = no improvement | Control validation | ⚠️ PARTIAL | NO - L3_off available | - | Use existing E_OFF | NO |
| L3_real > L3_shuffled > L3_off | Ordered effects | ❌ MISSING | **YES** - Strongest evidence | atlas-hec | All 3 conditions | **YES** |
| Archive bandwidth < 1% | Low bandwidth proof | ✅ PRESENT | NO - p=0.001 documented | - | Already satisfied | NO |
| Archive read-only | No cell control proof | ✅ PRESENT | NO - CDI design verified | - | Already satisfied | NO |

---

## 5. Minimal Rerun Requirements

### Must Run (Blocking)

```yaml
conditions:
  - name: L3_shuffled_p001
    universes: 8
    ticks: 5000
    config:
      L3_enabled: true
      archive_retrieval_prob: 0.001
      archive_shuffle: true
    purpose: Validate R1 (content relevance)
    blocking: YES
    
  - name: no_L2
    universes: 8
    ticks: 5000
    config:
      L2_enabled: false
      L1_enabled: true
      L3_enabled: true
    purpose: Validate R3 (lineage necessity)
    blocking: YES
```

### Optional (Non-Blocking)

```yaml
conditions:
  - name: no_L1
    universes: 8
    ticks: 5000
    optional: true
    
  - name: L3_overpowered_direct
    universes: 8
    ticks: 5000
    optional: true
```

---

## 6. Ledger Summary

### Blocking Items (Must Fix)

| Category | Count | Items |
|----------|-------|-------|
| Conditions | 2 | L3_shuffled_p001, no_L2 |
| CSV Columns | 5 | archive_sample_attempts, successes, influenced_births, lineage_diversity, top1_lineage_share |
| Comparisons | 2 | L3_real vs shuffled, baseline vs no_L2 |
| Anti-god-mode | 1 | L3_shuffled ≈ L3_off comparison |

**Total Blocking**: 10 items

### Non-Blocking Items (Can Defer)

| Category | Count | Items |
|----------|-------|-------|
| Conditions | 2 | no_L1, L3_overpowered_direct |
| CSV Columns | 2 | strategy_entropy, collapse_event_count |
| Comparisons | 2 | GitHub/local merge, optional stress tests |

**Total Non-Blocking**: 6 items

---

## 7. Resolution Priority

### P0 (Critical Path)

1. Run L3_shuffled_p001 (8 universes × 5000 ticks)
2. Run no_L2 (8 universes × 5000 ticks)
3. Validate R1 and R3
4. Make GO/HOLD/NO-GO decision

### P1 (Should Have)

5. Add archive_sample_attempts/successes to CSV export
6. Calculate lineage_diversity from existing data
7. Calculate top1_lineage_share from existing data

### P2 (Nice to Have)

8. Run no_L1 (optional)
9. Run L3_overpowered_direct (optional)
10. Add strategy_entropy calculation

---

## 8. Ledger Sign-off

| Role | Name | Date | Status |
|------|------|------|--------|
| Missing-Data Lead | Atlas-HEC | 2026-03-09 | Complete |
| Bio-World Dev | (pending) | - | Awaiting rerun request |

**Next Action**: Execute P0 minimal rerun (L3_shuffled + no_L2)
