# Memory Flow State Machine v1.0
## Event-Driven Transitions Between Memory Layers

**Version**: 1.0  
**Date**: 2026-03-09  
**Depends on**: THREE_LAYER_MEMORY_ARCHITECTURE_v1.md

---

## 1. State Definitions

### 1.1 States (Memory Layers)

```
S1: CELL_ACTIVE      (Cell Memory active)
S2: CELL_DYING       (Cell entering death process)
S3: CELL_DEAD        (Cell deceased, memory to be archived)

S4: LINEAGE_ACTIVE   (Lineage Memory propagating)
S5: LINEAGE_MUTATE   (Lineage Memory mutating)
S6: LINEAGE_EXTINCT  (Last member died, lineage ends)

S7: ARCHIVE_IDLE     (Causal Archive waiting)
S8: ARCHIVE_RECORD   (Writing to archive)
S9: ARCHIVE_SAMPLE   (Reading from archive)
```

### 1.2 Events (Triggers)

```
E1: TICK              (Time step)
E2: EXPERIENCE        (Significant event experienced)
E3: REPRODUCE         (Cell reproduction initiated)
E4: DEATH             (Cell death)
E5: MUTATION          (Random mutation)
E6: SIGNIFICANT       (System-significant event detected)
E7: SAMPLE_TRIGGER    (Probabilistic sampling)
E8: AUDIT_QUERY       (External audit request)
```

---

## 2. State Transition Diagram

### 2.1 Cell Memory Lifecycle

```
[BIRTH] → S1 (CELL_ACTIVE)
             ↓
       E1 (TICK) → Update Cell Memory
             ↓
       E2 (EXPERIENCE) → Write to Cell Memory
             ↓
       E3 (REPRODUCE) → Continue S1
             ↓
       E4 (DEATH) → S2 (CELL_DYING)
                        ↓
                  E6 (SIGNIFICANT?) → YES → S3 → Write to Archive
                                     NO → S3 → Discard
```

### 2.2 Lineage Memory Lifecycle

```
[REPRODUCTION] → S4 (LINEAGE_ACTIVE)
                      ↓
               Parent Lineage → Copy → Child Lineage
                      ↓
               E5 (MUTATION, p=0.05) → S5 (LINEAGE_MUTATE)
                      ↓
               S4 (back to active)
                      ↓
               Last member E4 (DEATH) → S6 (LINEAGE_EXTINCT)
                                              ↓
                                        Write final summary to Archive
```

### 2.3 Archive Lifecycle

```
[INIT] → S7 (ARCHIVE_IDLE)
            ↓
    E6 (SIGNIFICANT event) → S8 (ARCHIVE_RECORD)
                                ↓
                         Validate evidence chain
                                ↓
                         Append record
                                ↓
                         S7 (ARCHIVE_IDLE)
            ↓
    E7 (SAMPLE_TRIGGER, p=0.01) → S9 (ARCHIVE_SAMPLE)
                                      ↓
                               Random selection
                                      ↓
                               Return compressed prior
                                      ↓
                               S7 (ARCHIVE_IDLE)
            ↓
    E8 (AUDIT_QUERY) → S9 (ARCHIVE_SAMPLE)
                          ↓
                   Read specific record
                          ↓
                   Return full evidence
                          ↓
                   S7 (ARCHIVE_IDLE)
```

---

## 3. Detailed Transitions

### 3.1 Cell Memory Transitions

| Current | Event | Condition | Action | Next |
|---------|-------|-----------|--------|------|
| S1 | E1 (TICK) | Always | Decay old entries, update state | S1 |
| S1 | E2 (EXPERIENCE) | energy_change > threshold | Append to recent_energy_history | S1 |
| S1 | E2 (EXPERIENCE) | threat_detected | Append to recent_threat_history | S1 |
| S1 | E2 (EXPERIENCE) | collaboration_completed | Update neighbor_trust | S1 |
| S1 | E3 (REPRODUCE) | cell.energy > threshold | Continue operation | S1 |
| S1 | E4 (DEATH) | energy <= 0 or age > max | Initiate death process | S2 |
| S2 | E6 (SIGNIFICANT) | death_impact > threshold | Prepare archive record | S3 |
| S2 | NOT E6 | death_impact <= threshold | Discard memory | S3 |
| S3 | - | - | Memory destroyed / archived | [END] |

### 3.2 Lineage Memory Transitions

| Current | Event | Condition | Action | Next |
|---------|-------|-----------|--------|------|
| S4 | E3 (REPRODUCE) | parent exists | Copy lineage to child | S4 (parent), S4 (child) |
| S4 | E5 (MUTATION) | random() < μ=0.05 | Mutate one trait | S5 |
| S5 | - | mutation applied | Validate trait bounds | S4 |
| S4 | E4 (DEATH) | lineage.population == 1 | Last member dying | S6 |
| S6 | - | lineage extinct | Write lineage summary to archive | [END] |

### 3.3 Archive Transitions

| Current | Event | Condition | Action | Next |
|---------|-------|-----------|--------|------|
| S7 | E6 (SIGNIFICANT) | event.priority > threshold | Validate preconditions | S8 |
| S8 | - | evidence valid | Write record, update index | S7 |
| S8 | - | evidence invalid | Log error, reject write | S7 |
| S7 | E7 (SAMPLE) | random() < p=0.01 | Select random record | S9 |
| S9 | - | record selected | Compress, return prior | S7 |
| S7 | E8 (AUDIT) | query.valid == true | Retrieve specific record | S9 |
| S9 | - | audit complete | Return full evidence | S7 |

---

## 4. Event Definitions

### 4.1 E1: TICK
- **Trigger**: Every time step
- **Frequency**: 1/tick
- **Handler**: Cell Memory update
- **Data**: current_state, delta_t

### 4.2 E2: EXPERIENCE
- **Trigger**: Significant local event
- **Subtypes**:
  - E2a: Energy change > 10%
  - E2b: Threat detected (boss proximity)
  - E2c: Food consumed
  - E2d: Collaboration completed
  - E2e: Signal received
- **Handler**: Write to Cell Memory
- **Data**: event_type, magnitude, outcome

### 4.3 E3: REPRODUCE
- **Trigger**: Cell meets reproduction conditions
- **Handler**: Lineage inheritance
- **Data**: parent_id, child_id, inheritance_probability

### 4.4 E4: DEATH
- **Trigger**: Cell death conditions met
- **Subtypes**:
  - E4a: Starvation (energy <= 0)
  - E4b: Predation (boss kill)
  - E4c: Age (max_lifespan exceeded)
  - E4d: Cascade (extinction event)
- **Handler**: Death process, potential archive write
- **Data**: death_cause, final_state, generation

### 4.5 E5: MUTATION
- **Trigger**: Hereditary transmission
- **Probability**: μ = 0.05 per trait per generation
- **Handler**: Mutate Lineage Memory
- **Data**: trait, original_value, mutated_value

### 4.6 E6: SIGNIFICANT
- **Trigger**: System-level significant event
- **Criteria**:
  - Population drop > 20%
  - First extinction in universe
  - Innovation (new strategy emerges)
  - CDI critical threshold crossed
- **Handler**: Archive write preparation
- **Data**: event_classification, severity, scope

### 4.7 E7: SAMPLE_TRIGGER
- **Trigger**: Newborn initialization
- **Probability**: p = 0.01
- **Handler**: Archive weak sampling
- **Data**: sample_request, random_seed

### 4.8 E8: AUDIT_QUERY
- **Trigger**: External audit request
- **Authorization**: System-level only (not cell)
- **Handler**: Archive read for verification
- **Data**: query_parameters, requester_id

---

## 5. Information Flow Matrix

### 5.1 Allowed Flows

| Source | Destination | Trigger | Frequency | Data Type |
|--------|-------------|---------|-----------|-----------|
| Cell Memory | Cell Behavior | E1 (TICK) | 1/tick | Action decision |
| Cell Memory | Archive | E4+E6 (DEATH+SIGNIFICANT) | Rare | Death trace |
| Lineage Memory | Cell Memory | E3 (REPRODUCE) | 1/birth | Initial bias |
| Archive | Lineage Memory | E7 (SAMPLE) | 0.01/birth | Compressed prior |
| Archive | Audit | E8 (QUERY) | On demand | Full evidence |

### 5.2 Forbidden Flows (Hard Constraints)

| Source | Destination | Why Forbidden |
|--------|-------------|---------------|
| Archive | Cell Memory | Would enable god mode |
| Archive | Cell Behavior | Would bypass local decision |
| Lineage Memory | Archive | Would contaminate global with local |
| Cell Memory | Lineage Memory (runtime) | Would make lineage too volatile |
| Other Cell's Memory | Cell Memory | Would break isolation |

---

## 6. State Invariants

### 6.1 Cell Memory Invariants

```
Invariant C1: cell.memory.size <= MAX_CELL_MEMORY (100 entries)
Invariant C2: cell.memory.access_scope == SELF_ONLY
Invariant C3: cell.memory.persistence == EPHEMERAL (dies with cell)
Invariant C4: cell.memory.write_frequency <= 1/event
```

### 6.2 Lineage Memory Invariants

```
Invariant L1: lineage.traits.size <= MAX_TRAITS (10 traits)
Invariant L2: lineage.mutation_rate == μ (0.05 default)
Invariant L3: lineage.inheritance_probability <= 0.8
Invariant L4: lineage.persistence >= 5_generations (or extinct)
```

### 6.3 Archive Invariants

```
Invariant A1: archive.write_rate <= 1/100_generations
Invariant A2: archive.sample_rate <= 0.01/cell/lifetime
Invariant A3: archive.record.immutable == TRUE
Invariant A4: archive.evidence.required == TRUE
```

---

## 7. Error Handling

### 7.1 Invalid Transitions

| Invalid Attempt | Response | Log Level |
|-----------------|----------|-----------|
| Cell queries Archive directly | Reject, log security | WARNING |
| Archive overwrites Cell | Reject, log security | ERROR |
| Lineage mutation > μ | Clamp to μ, log correction | INFO |
| Archive write without evidence | Reject write | ERROR |
| Double inheritance (bug) | Take first, log anomaly | WARNING |

### 7.2 Recovery Procedures

- **Memory corruption**: Reset to empty, log event
- **Archive overflow**: Compress oldest records
- **Lineage loop (bug)**: Break at common ancestor
- **Race condition**: Last writer wins, log conflict

---

## 8. Validation Checklist

### 8.1 State Machine Correctness

- [ ] All valid transitions documented
- [ ] All invalid transitions rejected
- [ ] No deadlocks possible
- [ ] All states reachable from initial
- [ ] All states can reach terminal (via valid path)

### 8.2 Constraint Enforcement

- [ ] Cell cannot reach Archive state directly
- [ ] Archive sample probability enforced
- [ ] Mutation rate μ enforced
- [ ] Memory size limits enforced
- [ ] Write rate limits enforced

### 8.3 Audit Trail Completeness

- [ ] Every Archive write has evidence
- [ ] Every Lineage mutation logged
- [ ] Every Cell death categorized
- [ ] Every Significant event timestamped

---

## Appendix: Event Sequence Examples

### Example 1: Normal Cell Lifecycle

```
T=0:   [BIRTH] → S1 (Cell Memory initialized empty)
T=1:   E1 (TICK) → Update → S1
T=5:   E2 (EXPERIENCE: food) → Write → S1
T=50:  E2 (EXPERIENCE: threat) → Write → S1
T=100: E3 (REPRODUCE) → Continue S1, Create Child with Lineage
T=150: E4 (DEATH: age) → S2 → Check significance → NOT significant → S3 → Discard
```

### Example 2: Significant Death (Archive Write)

```
T=200: E4 (DEATH: boss_kill) → S2
       Check: First boss kill in this cluster? → YES
       → E6 (SIGNIFICANT) triggered
       → Collect evidence (location, CDI, cluster_state)
       → S8 (ARCHIVE_RECORD)
       → Write record with evidence chain
       → S3 (Cell destroyed)
```

### Example 3: Newborn with Archive Sample

```
T=300: [BIRTH] → Generate random() = 0.005 < 0.01
       → E7 (SAMPLE_TRIGGER)
       → S9 (ARCHIVE_SAMPLE)
       → Select random record (e.g., "boss weakness at high CDI")
       → Compress to Lesson
       → Inject into Lineage Memory (distilled_lessons)
       → S1 (Cell born with prior bias)
```

### Example 4: Lineage Mutation

```
T=400: E3 (REPRODUCE)
       Parent Lineage: strategy = "aggressive"
       E5 (MUTATION): random() = 0.03 < 0.05
       → S5 (LINEAGE_MUTATE)
       → Mutate to strategy = "balanced"
       → S4 (LINEAGE_ACTIVE)
       → Child inherits "balanced"
```

---

*Specification Version*: 1.0  
*Next Step*: Memory Data Schema (Instruction 3)  
*Dependencies*: THREE_LAYER_MEMORY_ARCHITECTURE_v1.md
