# Stage 3 Convergence Checklist

**Target**: T+6hr from Stage 3 launch  
**Current**: T+72min (interim)  
**Remaining**: ~4.5 hours  
**Purpose**: Validate interim findings before final report

---

## Checklist A: Configuration Stability

### A1: Config 3 Maintains Leadership
**Hypothesis**: P2T3M3D1 remains lowest drift configuration

**Check**:
```bash
cd /home/admin/atlas-hec-v2.1-repo/multiverse_sweep/stage_3_128
for r in $(seq 1 16); do tail -1 "universe_3_${r}/g1_output/g1_timeseries.csv" | cut -d',' -f4; done | awk '{sum+=$1} END {print sum/NR}'
```

**Criteria**:
- [ ] Mean drift < 0.22 (maintains #1 rank)
- [ ] Variance across 16 repeats < 15% CV
- [ ] No individual universe drift > 0.30

**Decision Gate**:
- ✅ PASS: Config 3 confirmed as stable baseline
- ⚠️ MARGINAL: Need extended testing
- ❌ FAIL: Re-evaluate "sweet spot" hypothesis

---

### A2: Config 6 Remains Critical
**Hypothesis**: P3T4M3D1 remains highest drift / most unstable

**Check**:
```bash
for r in $(seq 1 16); do tail -1 "universe_6_${r}/g1_output/g1_timeseries.csv" | cut -d',' -f4; done | awk '{sum+=$1} END {print sum/NR}'
```

**Criteria**:
- [ ] Mean drift > 0.40 (confirms critical status)
- [ ] Rollback count > 1,800/universe
- [ ] All 16 repeats show drift > 0.35

**Decision Gate**:
- ✅ PASS: Failure archetype confirmed
- ⚠️ MARGINAL: Borderline behavior
- ❌ FAIL: Critical threshold lower than expected

---

### A3: D1 Advantage Stabilizes
**Hypothesis**: Strict delegation drift reduction holds at 25-35%

**Check**:
Compare Config 1 (D1) vs Config 2 (D2) means:
```bash
# D1 mean
for r in $(seq 1 16); do tail -1 "universe_1_${r}/g1_output/g1_timeseries.csv" | cut -d',' -f4; done | awk '{sum+=$1} END {print sum/NR}'

# D2 mean
for r in $(seq 1 16); do tail -1 "universe_2_${r}/g1_output/g1_timeseries.csv" | cut -d',' -f4; done | awk '{sum+=$1} END {print sum/NR}'
```

**Criteria**:
- [ ] D1 advantage 25-40% range maintained
- [ ] Consistent across all pressure zones
- [ ] Statistically significant (p < 0.05 if calculable)

**Decision Gate**:
- ✅ PASS: D1_DEFAULT policy ready for promotion
- ⚠️ MARGINAL: Need more samples or qualification
- ❌ FAIL: Effect not as robust as interim suggests

---

### A4: M3 P2/P3 Divergence Confirms
**Hypothesis**: M3 beneficial under P2, harmful under P3

**Check**:
| Zone | Config | Expected Drift | Tolerance |
|------|--------|----------------|-----------|
| P2 | M3 vs M1 | M3 lower | ±0.03 |
| P3 | M3 vs M1 | M3 higher | ±0.05 |

**Criteria**:
- [ ] P2: M3 drift < M1 drift (confirms benefit)
- [ ] P3: M3 drift > M1 drift × 1.15 (confirms harm)
- [ ] Effect size stable across repeats

**Decision Gate**:
- ✅ PASS: M3_CONDITIONAL policy validated
- ⚠️ MARGINAL: Context more complex than binary
- ❌ FAIL: Pattern not reproducible

---

## Checklist B: Statistical Convergence

### B1: Within-Config Variance
**Target**: Coefficient of variation < 15% for all configs

**Check**:
```bash
for cfg in 1 2 3 4 5 6 7 8; do
  drifts=$(for r in $(seq 1 16); do tail -1 "universe_${cfg}_${r}/g1_output/g1_timeseries.csv" | cut -d',' -f4; done)
  # Calculate mean and std dev
  mean=$(echo "$drifts" | awk '{sum+=$1; count++} END {print sum/count}')
  variance=$(echo "$drifts" | awk -v m="$mean" '{sum+=($1-m)^2} END {print sum/NR}')
  std=$(echo "sqrt($variance)" | bc)
  cv=$(echo "scale=2; $std / $mean" | bc)
  echo "Config $cfg: CV = $cv"
done
```

**Criteria**:
- [ ] All configs CV < 0.15
- [ ] No outlier universes (>2σ from config mean)
- [ ] Variance decreases or stabilizes vs T+72min

---

### B2: Between-Config Separation
**Target**: Config means separated by >2×pooled std dev

**Check**:
Adjacent configs in ranking should be statistically distinct.

**Criteria**:
- [ ] Config 3 vs Config 1: separation clear
- [ ] Config 1 vs Config 5: separation clear
- [ ] Config 6 vs Config 8: separation maintained

---

### B3: Sample Size Adequacy
**Target**: 16 repeats sufficient for directionality

**Check**:
If we had 8 repeats instead of 16, would rankings change?

**Method**:
- Subsample: Use only repeats 1-8
- Compare rankings to full 16-repeat
- Check consistency

**Criteria**:
- [ ] Rankings stable across subsamples
- [ ] Top 3 / Bottom 3 unchanged
- [ ] Conclusion: 16 repeats adequate

---

## Checklist C: Data Quality

### C1: No Data Corruption
**Check**:
- [ ] All 128 CSV files parseable
- [ ] No missing columns
- [ ] Timestamps monotonic
- [ ] No NaN or Inf values

**Command**:
```bash
find . -name "g1_timeseries.csv" -exec python3 -c "import csv; list(csv.reader(open('{}')))" \; 2>&1 | head
```

---

### C2: Continuity Verified
**Check**:
- [ ] No gaps > 60 seconds in any universe
- [ ] Data rate stable (rows/min consistent)

**Method**:
Sample 5 random universes, check timestamp deltas.

---

### C3: E1 Data Integrity
**Check**:
- [ ] All 128 JSONL files parseable
- [ ] Accuracy calculations reproducible
- [ ] No duplicate batch numbers

---

## Checklist D: Archetype Validation

### D1: Critical Archetype Reproducible
**Target**: Config 6 consistently shows failure pattern

**Validation**:
- [ ] Drift > 0.40 in all 16 repeats
- [ ] Recovery events > 1,700 in all repeats
- [ ] Drift trajectory: increasing or sustained high

---

### D2: Stable Archetype Reproducible
**Target**: Config 3 consistently shows optimal pattern

**Validation**:
- [ ] Drift < 0.22 in >12/16 repeats
- [ ] Low variance across repeats
- [ ] Drift trajectory: stable or decreasing

---

### D3: Policy Effects Consistent
**Target**: D1 and M3 effects reproducible

**Validation**:
- [ ] D1 benefit: reproduced in all 4 comparisons
- [ ] M3 P2 benefit: reproduced
- [ ] M3 P3 harm: reproduced

---

## Convergence Decision Matrix

| Checklist | Items | Pass Threshold | Action if Pass | Action if Fail |
|-----------|-------|----------------|----------------|----------------|
| A: Config Stability | 4 | 3/4 | Proceed to final | Extended runtime |
| B: Statistical | 3 | 2/3 | Proceed to final | Add repeats |
| C: Data Quality | 3 | 3/3 | Proceed to final | Data recovery |
| D: Archetypes | 3 | 3/3 | Write final report | Re-evaluate |

**Overall**:
- ✅ **ALL PASS**: T+6hr → Final Report (T+24hr target)
- ⚠️ **MIXED**: T+6hr → Extended monitoring (T+12hr)
- ❌ **MULTIPLE FAIL**: Investigate methodology

---

## Execution Schedule

```
Current:  T+72min  (Interim review complete)
          ↓
Target:   T+6hr    (Run convergence checklist)
          ↓
Branch:   If PASS  → T+24hr Final Report
          If MIXED → T+12hr Extended check
          If FAIL  → Investigation + redesign
```

---

**Document Status**: CHECKLIST v1.0  
**Execution Authority**: Auto-trigger at T+6hr  
**Report Destination**: STAGE3_FINAL_REPORT.md
