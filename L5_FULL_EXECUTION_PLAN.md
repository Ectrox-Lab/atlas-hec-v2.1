# L5 Full Execution Plan - Directionality-Aware

> **Status**: IN PROGRESS  
> **Current Phase**: Batch-3 Completed, Directionality Discovered  
> **Next Priority**: Validate Code Source Advantage Generalization

---

## Completed Batches

| Batch | Pair | Mean TG | Windows | Status | Key Finding |
|:-----:|:----:|:-------:|:-------:|:------:|:------------|
| 1 | Code→Math | 14.69pp | 10/10 | ✅ | Strong baseline established |
| 2 | Code→Planning | 6.8pp | 8/10 | ✅ | Domain gap effect (smaller TG) |
| 3 | Math→Code | 9.77pp | 10/10 | ✅ | **Directionality discovered** |

### Directionality Discovery

```
Code→Math: 14.69pp
Math→Code: 9.77pp
Ratio: 0.665 (Near Symmetric but Direction-Biased)

Finding: Transfer is bidirectionally viable but not directionally neutral.
Code appears to be a stronger source task than Math for this pair.
```

---

## Remaining Batches (Prioritized)

### Critical Priority (Theory Validation)

#### Batch-4: Code→Planning (Full Scale)
- **Purpose**: Test if Code source advantage generalizes
- **Expected**: 10-14pp (stronger than A→C 6.8pp due to larger scale)
- **Scientific Question**: Is Code universally a stronger source?
- **If Successful**: Supports abstraction-level hypothesis
- **Execution**: 
  ```bash
  python3 ralph_window_gate.py --config L5_BATCH4_CODE2PLANNING.json
  ```

#### Batch-5: Planning→Code
- **Purpose**: Test if Planning can be a source (vs only target)
- **Expected**: 5-8pp (if Planning is weak source)
- **Scientific Question**: Can concrete task structures transfer out?
- **If Successful**: Planning can serve as source
- **If Failed**: Planning is target-only
- **Execution**:
  ```bash
  python3 ralph_window_gate.py --config L5_BATCH5_PLANNING2CODE.json
  ```

### Matrix Completion (Filling Gaps)

#### Batch-6: Math→Planning
- **Purpose**: Complete middle-abstraction source test
- **Expected**: 6-9pp (Math as source, similar to reverse)
- **Scientific Question**: Is Math consistently moderate source?

#### Batch-7: Planning→Math
- **Purpose**: Lowest priority; test weakest potential pair
- **Expected**: 4-7pp (lowest of all, if pattern holds)
- **Scientific Question**: Concrete→Abstract transfer limit?

---

## Decision Tree

### After Batch-4 (Code→Planning)

```
if Code→Planning TG >= 10pp:
    → Code is universally strong source ✅
    → Proceed with Code-centric multi-task strategies
    
elif Code→Planning TG >= 6pp:
    → Code source advantage exists but domain gap matters
    → Need task-specific source selection strategy
    
else:
    → Code source advantage is pair-specific
    → Abstraction-level theory needs refinement
```

### After Batch-5 (Planning→Code)

```
if Planning→Code TG >= 8pp:
    → Planning can be strong source
    → Directionality is task-dependent, not universal hierarchy
    
elif Planning→Code TG >= 5pp:
    → Planning is moderate source
    → Source suitability is gradient, not binary
    
else:
    → Planning is target-only
    → Establish "source task whitelist"
```

---

## Theoretical Outcomes

### Scenario A: Code Universally Strongest

```yaml
source_suitability_ranking:
  1: Code      (universal strong source)
  2: Math      (moderate source)
  3: Planning  (target-only or weak source)
  
strategy: "Always use Code as source when possible"
implication: "Prioritize Code training in early phases"
```

### Scenario B: Task-Pair Specific

```yaml
finding: "No universal source ranking; suitability is pair-dependent"

example_pattern:
  Code→Math: strong
  Code→Planning: weak
  Math→Planning: moderate
  Planning→Math: none
  
strategy: "Learn source→target suitability matrix"
implication: "Need more sophisticated task routing"
```

### Scenario C: Abstraction Level Theory

```yaml
hypothesis: "Higher abstraction tasks make better sources"

abstraction_hierarchy:
  Code: high      (formal logic, universal syntax)
  Math: medium    (domain-specific formalism)
  Planning: low   (concrete heuristics)
  
prediction: "Source advantage ∝ Abstraction level"
validation: "Requires complete matrix + additional tasks"
```

---

## Execution Timeline

| Phase | Batches | Est. Time | Goal |
|:-----:|:-------:|:---------:|:-----|
| 1 | 1-3 | Done | Directionality discovery ✅ |
| 2 | 4-5 | ~2-3h | Validate Code universality |
| 3 | 6-7 | ~2h | Complete matrix |
| 4 | Analysis | ~1h | Source Suitability Index v1.0 |
| 5 | Publication | - | Citable L5 findings |

**Total Remaining**: ~5-6 hours for complete L5 validation

---

## Success Criteria

### L5 Full Success Definition

```yaml
minimum_viable:
  positive_pairs: ">= 4/6"
  strong_transfer_pairs: ">= 2/6 (TG >= 10pp)"
  
optimal:
  positive_pairs: ">= 5/6"
  source_suitability_model: "validated and ranked"
  directionality_theory: "supported by evidence"
  
citable_findings:
  - "Cross-task inheritance is bidirectionally viable"
  - "Transfer strength depends on source→target ordering"
  - "Code demonstrates superior source suitability (ratio=0.665)"
  - "Domain gap affects transfer magnitude but not directionality"
```

---

## Immediate Next Action

```bash
# Execute Batch-4: Code→Planning
# Validate if Code source advantage generalizes

cd /home/admin/atlas-hec-v2.1-repo
python3 ralph_window_gate.py --config L5_BATCH4_CODE2PLANNING.json

# Expected: ~30-40min, 10 windows
# Target: TG >= 10pp (to confirm Code as universal strong source)
# Minimum: TG >= 6pp (to maintain positive finding)
```

**Decision Point**: After Batch-4, update source_suitability_model.yaml evidence strength from MODERATE to STRONG (if successful) or revise hypothesis (if failed).

---

*L5 Full Execution Plan v1.0 - Directionality-Aware*
