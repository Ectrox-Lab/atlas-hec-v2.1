# Layer 4: Architecture Edit Proposal

**Proposal ID**: L4-001  
**Status**: PENDING_REVIEW  
**Priority**: P0 (blocks smoke test credibility)  
**Submitted**: 2024-03-12

---

## 1. Change Summary

Add `hazard_simulation_mode: bool` flag to distinguish simulated vs real metrics.

## 2. Target Files

```
src/
├── evaluation.rs       (TickSnapshot struct)
├── consciousness_index.rs (CWCI evaluation)
└── universe_runner.rs  (SocsRuntime::snapshot)
```

## 3. Detailed Change

### 3.1 evaluation.rs
```rust
#[derive(Clone, Debug, Default)]
pub struct TickSnapshot {
    pub tick: usize,
    pub alive_units: usize,
    // ... other fields ...
    pub hazard: f32,
    pub recovery_event: bool,
    
    // NEW FIELD
    /// Indicates if metrics are from simulation or real SOCS
    pub simulation_mode: bool,  // true = simulation, false = real
}
```

### 3.2 consciousness_index.rs
```rust
pub struct CWCIEvaluation {
    pub capabilities: ConsciousnessCapabilities,
    pub level: ConsciousnessLevel,
    pub cwei_score: f32,
    pub open_world_survived: bool,
    pub multi_universe_tested: bool,
    
    // NEW FIELD
    pub simulation_limited: bool,  // propagated from TickSnapshot
}
```

### 3.3 universe_runner.rs
```rust
impl SocsRuntime {
    pub fn snapshot(&self, cfg: &UniverseConfig) -> TickSnapshot {
        // ... existing code ...
        
        TickSnapshot {
            tick: self.tick,
            // ... other fields ...
            hazard,  // currently simulated
            recovery_event,
            
            // NEW: Mark as simulation until real SOCS integration
            simulation_mode: true,  // TODO: Set false when real bridge available
        }
    }
}
```

## 4. Justification

### Why This Change

**Current Problem**:
- Smoke test results mix simulated and (future) real metrics
- Cannot distinguish which conclusions are SIMULATION-LIMITED
- Risk of over-claiming based on simulation artifacts

**After Change**:
- All metrics carry provenance flag
- Reports can automatically include limitation warnings
- Future real-SOCS integration only needs to flip flag

### Alignment with Goals

- ✅ Supports "strict constraint" on conclusion types
- ✅ Enables automatic SIMULATION-LIMITED tagging
- ✅ Prepares for real SOCS integration
- ❌ Does not add new capabilities (just provenance)

## 5. Risk Assessment

| Risk | Level | Mitigation |
|------|-------|-----------|
| Breaking existing code | LOW | Additive only, default true |
| Performance impact | NONE | Single bool field |
| Semantic confusion | MEDIUM | Document clearly in code |
| Future compatibility | LOW | Flag designed for flip to false |

## 6. Rollback Plan

```bash
# If needed, revert with:
git revert <commit>
# Or manually remove 3 lines added to each file
```

Rollback complexity: **VERY LOW** (additive changes only)

## 7. Test Plan

### 7.1 Unit Tests
```rust
#[test]
fn test_simulation_flag_propagation() {
    let snapshot = runtime.snapshot(&config);
    assert_eq!(snapshot.simulation_mode, true);
}
```

### 7.2 Integration Tests
- Run existing Gate 1/2 scripts
- Verify reports include simulation warning
- Check no performance regression

### 7.3 Smoke Test Impact
- Reports will now auto-include: "⚠️ SIMULATION-LIMITED"
- Conclusions remain valid but properly qualified

## 8. Alternatives Considered

| Alternative | Rejected Because |
|------------|-----------------|
| Separate real/sim structs | Too invasive, duplicates code |
| Feature flag at compile | Too coarse, runtime flag needed |
| Documentation only | Not enforced, easy to forget |

## 9. Human Decision Required

**[ ] APPROVE** - Proceed with implementation  
**[ ] REJECT** - Abandon proposal, seek alternative  
**[ ] MODIFY** - Request changes to proposal

If APPROVE:
- Estimated implementation time: 30 minutes
- Can be done by Layer 1 autonomously

If REJECT:
- Alternative: Add limitation notes in documentation only
- Risk: Less rigorous, easier to overlook

## 10. Related Items

- Blocks: Smoke test credibility
- Related to: GLOBAL-001 blocker (no open-world bridge)
- Precedes: Real SOCS integration Phase 2

---

**Submitted by**: Research Ops System (Layer 3 → 4 escalation)  
**Review deadline**: 2024-03-13  
**Auto-expire**: If no response, stays PENDING and blocks dependent tasks
