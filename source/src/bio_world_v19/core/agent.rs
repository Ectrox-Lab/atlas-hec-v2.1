//! Agent with energy metabolism
//! 
//! Core properties:
//! - Position in 3D grid
//! - Energy (for survival and reproduction)
//! - Phase (for synchronization dynamics)
//! - Lineage ID (for inheritance)

use super::grid::Position;

/// Agent state
#[derive(Clone, Debug)]
pub struct Agent {
    pub id: usize,
    pub pos: Position,
    pub alive: bool,
    
    // Energy
    pub energy: f32,
    pub max_energy: f32,
    pub metabolic_rate: f32,  // Energy consumed per tick
    
    // Synchronization
    pub phase: f64,
    pub natural_frequency: f64,
    
    // Lineage
    pub lineage_id: u64,
    pub generation: usize,
    
    // Age
    pub age: usize,
    pub max_age: usize,
    
    // Behavior
    pub coherence_score: f32,  // For CDI contribution
}

impl Agent {
    pub fn new(id: usize, pos: Position) -> Self {
        use fastrand::Rng;
        let mut rng = Rng::new();
        
        Self {
            id,
            pos,
            alive: true,
            energy: 100.0,
            max_energy: 200.0,
            metabolic_rate: 0.5,
            phase: rng.f64() * 2.0 * std::f64::consts::PI,
            natural_frequency: 1.0 + rng.f64() * 0.2 - 0.1, // 1.0 ± 0.1
            lineage_id: id as u64,
            generation: 0,
            age: 0,
            max_age: 1000,
            coherence_score: 0.5,
        }
    }
    
    /// Create offspring from parent
    pub fn reproduce(parent: &Agent, new_id: usize, new_pos: Position) -> Self {
        use fastrand::Rng;
        let mut rng = Rng::new();
        
        // Mutation
        let freq_mutation = rng.f64() * 0.02 - 0.01; // ±1%
        
        Self {
            id: new_id,
            pos: new_pos,
            alive: true,
            energy: 50.0,  // Initial energy
            max_energy: parent.max_energy,
            metabolic_rate: parent.metabolic_rate,
            phase: rng.f64() * 2.0 * std::f64::consts::PI,
            natural_frequency: (parent.natural_frequency + freq_mutation).max(0.1),
            lineage_id: parent.lineage_id,
            generation: parent.generation + 1,
            age: 0,
            max_age: parent.max_age,
            coherence_score: parent.coherence_score,
        }
    }
    
    /// Consume energy
    pub fn metabolize(&mut self) {
        self.energy -= self.metabolic_rate;
        self.age += 1;
        
        if self.energy <= 0.0 || self.age >= self.max_age {
            self.alive = false;
        }
    }
    
    /// Consume food
    pub fn eat(&mut self, food_energy: f32) {
        self.energy = (self.energy + food_energy).min(self.max_energy);
    }
    
    /// Check if can reproduce
    pub fn can_reproduce(&self, reproduction_cost: f32) -> bool {
        self.alive && self.energy > reproduction_cost * 2.0
    }
    
    /// Pay reproduction cost
    pub fn pay_reproduction_cost(&mut self, cost: f32) {
        self.energy -= cost;
    }
    
    /// Update phase (Kuramoto dynamics)
    pub fn update_phase(&mut self, coupling: f64, dt: f64) {
        self.phase += (self.natural_frequency + coupling) * dt;
        self.phase = self.phase.rem_euclid(2.0 * std::f64::consts::PI);
    }
    
    /// CDI contribution
    pub fn cdi_contribution(&self) -> f32 {
        if !self.alive {
            return 0.0;
        }
        
        // Higher generation + stable coherence = higher CDI
        let generation_factor = (self.generation as f32 / 100.0).min(1.0);
        let energy_factor = self.energy / self.max_energy;
        let age_factor = 1.0 - (self.age as f32 / self.max_age as f32);
        
        (generation_factor * 0.3 + energy_factor * 0.4 + age_factor * 0.3) 
            * self.coherence_score
    }
    
    /// Get parent lineage ID
    pub fn parent_id(&self) -> u64 {
        self.lineage_id
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use super::super::grid::Position;
    
    #[test]
    fn test_agent_creation() {
        let pos = Position::new(25, 25, 8);
        let agent = Agent::new(0, pos);
        
        assert_eq!(agent.id, 0);
        assert!(agent.alive);
        assert_eq!(agent.energy, 100.0);
    }
    
    #[test]
    fn test_metabolism() {
        let pos = Position::new(25, 25, 8);
        let mut agent = Agent::new(0, pos);
        
        let initial_energy = agent.energy;
        agent.metabolize();
        
        assert!(agent.energy < initial_energy);
        assert_eq!(agent.age, 1);
    }
    
    #[test]
    fn test_death() {
        let pos = Position::new(25, 25, 8);
        let mut agent = Agent::new(0, pos);
        
        agent.energy = 0.1;
        agent.metabolize();
        
        assert!(!agent.alive);
    }
    
    #[test]
    fn test_reproduction() {
        let pos = Position::new(25, 25, 8);
        let parent = Agent::new(0, pos);
        let child_pos = Position::new(26, 25, 8);
        
        let child = Agent::reproduce(&parent, 1, child_pos);
        
        assert_eq!(child.parent_id(), parent.lineage_id);
        assert_eq!(child.generation, 1);
    }
}
