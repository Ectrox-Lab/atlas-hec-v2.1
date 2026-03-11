//! Cell Adapter - PriorChannel in Bio-World Cell (Simplified v0)
//!
//! Maps Candidate 001's 32-bit generic prior carrier to Bio-World cell's local_signal_state.

use crate::prior_channel::{Marker, MarkerScheduler};

/// Cell-local signal state with PriorChannel integration
pub struct LocalSignal {
    /// Marker scheduler (10x timescale)
    scheduler: MarkerScheduler,
    /// Current marker
    current_marker: Marker,
    /// Tick counter for 10x timescale
    tick_counter: usize,
    /// Signal coherence [0, 1]
    coherence: f32,
}

impl LocalSignal {
    pub fn new(cell_id: u8) -> Self {
        Self {
            scheduler: MarkerScheduler::new(cell_id),
            current_marker: Marker::new(cell_id, 128, 0, 0),
            tick_counter: 0,
            coherence: 0.5,
        }
    }
    
    /// Update signal from cell action (10x timescale)
    pub fn tick(&mut self, action: f32) -> Option<Marker> {
        self.tick_counter += 1;
        
        // Update coherence based on action consistency
        self.coherence = 0.9 * self.coherence + 0.1 * (1.0 - (action - 0.5).abs() * 2.0);
        
        // Update marker every 10 ticks (10x timescale)
        if self.tick_counter % 10 == 0 {
            let coherence_byte = (self.coherence * 255.0) as u8;
            self.current_marker = Marker::new(
                self.current_marker.agent_id(),
                coherence_byte,
                0, 0
            );
            
            // Tick scheduler
            let _ = self.scheduler.tick(action);
            
            return Some(self.current_marker);
        }
        
        None
    }
    
    /// Get current marker for population observation
    pub fn marker(&self) -> &Marker {
        &self.current_marker
    }
    
    /// Get coherence for Bio-World state vector
    pub fn coherence(&self) -> f32 {
        self.coherence
    }
}

/// Prior carrier integrated into Bio-World cell
pub struct PriorInCell {
    /// Local signal state (32-bit carrier)
    pub signal: LocalSignal,
    /// Cell ID for marker attribution
    cell_id: u8,
}

impl PriorInCell {
    pub fn new(cell_id: u8) -> Self {
        Self {
            signal: LocalSignal::new(cell_id),
            cell_id,
        }
    }
    
    /// Cell action cycle with prior integration
    pub fn act(&mut self, _population_markers: &[Marker]) -> f32 {
        // Get marker update if available
        let marker = self.signal.tick(0.5); // Default neutral action
        
        // Use coherence to modulate decision
        let action = if let Some(_m) = marker {
            // Prior injection: use coherence
            self.signal.coherence()
        } else {
            // No marker update: default behavior
            0.5
        };
        
        // Update signal with actual action
        let _ = self.signal.tick(action);
        
        action
    }
    
    pub fn cell_id(&self) -> u8 {
        self.cell_id
    }
}

/// Cell adapter connecting Bio-World cell to Superbrain mechanisms
pub struct CellAdapter {
    /// Prior carrier (32-bit, generic only)
    pub prior: PriorInCell,
    /// Cell state for Bio-World
    pub energy: f32,
    pub age: usize,
}

impl CellAdapter {
    pub fn new(cell_id: u8, initial_energy: f32) -> Self {
        Self {
            prior: PriorInCell::new(cell_id),
            energy: initial_energy,
            age: 0,
        }
    }
    
    /// Full cell cycle: sense → decide → act → update
    pub fn cycle(&mut self, neighborhood: &NeighborhoodContext) -> CellAction {
        self.age += 1;
        
        // 1. Sense: collect population markers
        let markers: Vec<Marker> = neighborhood.neighbor_markers.clone();
        
        // 2. Decide: use coherence as cooperation probability
        let coop_prob = self.prior.signal.coherence();
        
        // 3. Act: Execute with prior integration
        let action = if neighborhood.coop_threshold < coop_prob {
            CellAction::Cooperate
        } else {
            CellAction::Defect
        };
        
        // 4. Update: PriorChannel tick
        let action_val = match action {
            CellAction::Cooperate => 0.0,
            CellAction::Defect => 1.0,
        };
        let _ = self.prior.signal.tick(action_val);
        
        action
    }
    
    /// Get cell state for Bio-World CDI computation
    pub fn state_vector(&self) -> CellStateVector {
        CellStateVector {
            coherence: self.prior.signal.coherence(),
            energy: self.energy,
            age: self.age,
        }
    }
}

#[derive(Clone, Debug)]
pub struct NeighborhoodContext {
    pub neighbor_markers: Vec<Marker>,
    pub neighbor_count: usize,
    pub local_density: f32,
    pub coop_threshold: f32,
}

impl NeighborhoodContext {
    pub fn new(neighbor_count: usize, density: f32) -> Self {
        Self {
            neighbor_markers: Vec::new(),
            neighbor_count,
            local_density: density,
            coop_threshold: 0.5,
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum CellAction {
    Cooperate,
    Defect,
}

#[derive(Clone, Debug)]
pub struct CellStateVector {
    pub coherence: f32,
    pub energy: f32,
    pub age: usize,
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn local_signal_10x_timescale() {
        let mut signal = LocalSignal::new(1);
        
        // 9 ticks: no marker update yet
        for i in 0..9 {
            signal.tick(0.5);
            assert_eq!(signal.tick_counter, i + 1);
        }
        assert_eq!(signal.tick_counter, 9);
    }
    
    #[test]
    fn cell_adapter_creation() {
        let adapter = CellAdapter::new(1, 100.0);
        assert_eq!(adapter.energy, 100.0);
        assert_eq!(adapter.age, 0);
    }
}
