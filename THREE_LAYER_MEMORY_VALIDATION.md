# Three-Layer Memory Validation Protocol

**Date**: 2026-03-09  
**Status**: Ready for Execution (5 Validation Experiments)

---

## Architecture

```
CellMemory ←→ LineageMemory ←→ CausalArchive
     ↑            ↑                ↓
   (p=0.01)   (inheritance)   (weak sampling)
```

**Hard Constraints**:
- Cell cannot directly access Archive
- Archive cannot inject strategy to Cell
- Only Archive → Lineage weak sampling (p=0.01)

---

## 5 Validation Experiments

### V1: Memory Persistence
**Hypothesis**: Cell state persists across perturbations

**Setup**:
- Induce perturbation at t=100
- Measure recovery at t=200
- Check if memory state correlates with recovery speed

**Pass**: Recovery time < 50 ticks, correlation > 0.6

---

### V2: Lineage Inheritance  
**Hypothesis**: Child agents inherit parent memory bias

**Setup**:
- Parent trained on condition A
- Child tested on condition A vs B
- Measure behavior similarity

**Pass**: Child-parent correlation > 0.5

---

### V3: Archive Weak Influence
**Hypothesis**: p=0.01 sampling provides guidance without control

**Setup**:
- Archive contains successful patterns
- Measure if lineage gradually shifts toward patterns
- Verify no direct cell access

**Pass**: Lineage shift > 10% over 1000 generations, no cell-archive direct coupling

---

### V4: Memory-Behavior Coupling
**Hypothesis**: Memory state predicts behavior choice

**Setup**:
- Record memory state before decision
- Correlate with action taken
- Test across different regimes

**Pass**: Prediction accuracy > 65%

---

### V5: Cross-Layer Information Flow
**Hypothesis**: Information flows Cell→Lineage→Archive only

**Setup**:
- Inject marker at Cell layer
- Track appearance in Lineage and Archive
- Verify no reverse flow

**Pass**: Forward propagation confirmed, no backward leakage

---

## Success Criteria

**Gate**: 3/5 experiments PASS → Three-Layer Memory validated

---

## Current Status

| Component | Status | File |
|-----------|--------|------|
| CellMemory | ✅ Ready | `bio_superbrain_interface/cell_adapter.rs` |
| LineageMemory | ✅ Ready | `bio_superbrain_interface/lineage_adapter.rs` |
| CausalArchive | ⚠️ Stub | Need implementation |
| Weak Sampling (p=0.01) | ✅ Ready | Matches PriorChannel |
| MemoryAccessGuard | ⚠️ Need impl | Access control layer |

---

## Next Steps

1. **Implement CausalArchive** (if not exists)
2. **Implement MemoryAccessGuard** 
3. **Run V1-V5 validation**
4. **Count passes: need 3/5**

---

## Integration with v19

Three-Layer Memory feeds into v19 state vector:

```
Memory coherence → Agent behavior → Network structure → [CDI, CI, r]
```

Once 3/5 pass, we have:
- EXP-1/2/3: ✅ Network/structure dynamics
- Three-Layer: ✅ Memory-behavior coupling

**Complete v19 × Memory integration achieved**.
