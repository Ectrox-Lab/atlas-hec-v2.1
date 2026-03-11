//! Lineage Adapter - Identity Inheritance in Bio-World (Simplified v0)

/// Lineage memory with identity preservation
#[derive(Clone, Debug)]
pub struct LineageMemory {
    /// Lineage ID (immutable after creation)
    pub lineage_id: u64,
    /// Parent lineage (None for genesis)
    pub parent: Option<u64>,
    /// Generation counter
    pub generation: usize,
    /// Inherited coherence baseline
    pub coherence_baseline: f32,
    /// Mutation rate (Bio-World μ=0.05)
    pub mutation_rate: f32,
    /// Death count in lineage
    pub death_count: usize,
}

impl LineageMemory {
    pub fn genesis(lineage_id: u64) -> Self {
        Self {
            lineage_id,
            parent: None,
            generation: 0,
            coherence_baseline: 0.5,
            mutation_rate: 0.05,
            death_count: 0,
        }
    }
    
    /// Inherit from parent with mutation
    pub fn inherit(parent: &LineageMemory, new_id: u64) -> Self {
        // Simple mutation: small random change
        let coherence_mutation = 0.0; // Simplified: no mutation for MVP
        
        Self {
            lineage_id: new_id,
            parent: Some(parent.lineage_id),
            generation: parent.generation + 1,
            coherence_baseline: (parent.coherence_baseline + coherence_mutation).clamp(0.0, 1.0),
            mutation_rate: parent.mutation_rate,
            death_count: 0,
        }
    }
    
    /// Record death in lineage
    pub fn record_death(&mut self, _cause: DeathCause) {
        self.death_count += 1;
    }
    
    /// Get CDI contribution from lineage (Bio-World state vector)
    pub fn cdi_contribution(&self) -> f32 {
        // Higher generation + stable coherence = higher CDI
        let generation_factor = (self.generation as f32 / 100.0).min(1.0);
        let stability_factor = 1.0 - (self.death_count as f32 / 10.0).min(1.0);
        
        (generation_factor * 0.5 + stability_factor * 0.5) * self.coherence_baseline
    }
}

#[derive(Clone, Copy, Debug)]
pub enum DeathCause {
    Starvation,
    Predation,
    Age,
}

/// Identity inheritance preserving Superbrain continuity
pub struct IdentityInheritance {
    /// Current lineage
    pub lineage: LineageMemory,
    /// Cell ID within lineage
    pub cell_id: u8,
    /// Identity continuity score [0, 1]
    pub continuity: f32,
}

impl IdentityInheritance {
    pub fn genesis(lineage_id: u64, cell_id: u8) -> Self {
        Self {
            lineage: LineageMemory::genesis(lineage_id),
            cell_id,
            continuity: 1.0,
        }
    }
    
    /// Reproduce with identity preservation
    pub fn reproduce(&self, new_cell_id: u8) -> Self {
        let new_lineage_id = self.lineage.lineage_id + 1; // Simplified
        
        Self {
            lineage: LineageMemory::inherit(&self.lineage, new_lineage_id),
            cell_id: new_cell_id,
            continuity: self.continuity * 0.95, // Slight decay per generation
        }
    }
}

/// Lineage adapter for Bio-World integration
pub struct LineageAdapter {
    /// Active lineages in universe
    pub active_lineages: Vec<LineageMemory>,
    /// Next lineage ID
    next_lineage_id: u64,
}

impl LineageAdapter {
    pub fn new() -> Self {
        Self {
            active_lineages: Vec::new(),
            next_lineage_id: 1,
        }
    }
    
    /// Create genesis lineage
    pub fn create_genesis(&mut self) -> IdentityInheritance {
        let id = self.next_lineage_id;
        self.next_lineage_id += 1;
        
        let inheritance = IdentityInheritance::genesis(id, 0);
        self.active_lineages.push(inheritance.lineage.clone());
        
        inheritance
    }
    
    /// Get CDI for universe (Bio-World state vector component)
    pub fn universe_cdi(&self) -> f32 {
        if self.active_lineages.is_empty() {
            return 0.0;
        }
        
        let total: f32 = self.active_lineages.iter()
            .map(|l| l.cdi_contribution())
            .sum();
        
        total / self.active_lineages.len() as f32
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn lineage_genesis() {
        let lineage = LineageMemory::genesis(1);
        assert_eq!(lineage.lineage_id, 1);
        assert!(lineage.parent.is_none());
        assert_eq!(lineage.generation, 0);
    }
    
    #[test]
    fn lineage_inheritance() {
        let parent = LineageMemory::genesis(1);
        let child = LineageMemory::inherit(&parent, 2);
        
        assert_eq!(child.parent, Some(1));
        assert_eq!(child.generation, 1);
    }
    
    #[test]
    fn identity_continuity_decay() {
        let id1 = IdentityInheritance::genesis(1, 0);
        let id2 = id1.reproduce(1);
        
        assert!(id2.continuity < id1.continuity);
    }
}
