//! Bio-World v19 Real Simulation Runner
//! 
//! Replaces stub simulation with actual GridWorld + PopulationDynamics

use crate::bio_world_v19::{
    GridWorld, Agent, Position, PopulationDynamics, PopulationParams,
    HazardRateTracker, MultiUniverseHazard,
    compute_sync_order_parameter, compute_condensation_index,
    StateVector, GRID_X, GRID_Y, GRID_Z,
};
use super::{ExperimentAtoE, RunConfig, ExperimentResult};

use std::collections::HashMap;

/// v19 Experiment with real simulation
pub struct V19Experiment {
    pub exp_type: ExperimentAtoE,
    pub world: GridWorld,
    pub population_dynamics: PopulationDynamics,
    pub hazard_tracker: HazardRateTracker,
    pub state_history: Vec<StateVector>,
}

impl V19Experiment {
    pub fn new(exp_type: ExperimentAtoE, seed: u64) -> Self {
        let mut world = GridWorld::new();
        
        // Genesis population based on experiment type
        let genesis_count = match exp_type {
            ExperimentAtoE::Survival => 100,
            ExperimentAtoE::Evolution => 80,
            ExperimentAtoE::Stress => 120,
            ExperimentAtoE::Collaboration => 90,
            ExperimentAtoE::Akashic => 100,
        };
        
        // Spawn genesis agents
        for i in 0..genesis_count {
            let x = (i * 7) % GRID_X;  // Pseudo-random spread
            let y = (i * 13) % GRID_Y;
            let z = (i * 3) % GRID_Z;
            world.spawn_agent(x, y, z);
        }
        
        // Spawn initial food
        world.spawn_food_random(50, 30.0);
        
        // Configure population params based on experiment
        let params = match exp_type {
            ExperimentAtoE::Stress => PopulationParams {
                reproduction_cost: 50.0,  // Higher cost
                food_energy: 20.0,        // Less food
                food_regen_interval: 150, // Slower regen
                carrying_capacity: 2,     // Lower capacity
                random_death_prob: 0.005,
            },
            ExperimentAtoE::Collaboration => PopulationParams {
                reproduction_cost: 30.0,  // Lower cost
                food_energy: 40.0,        // More food
                food_regen_interval: 80,
                carrying_capacity: 6,     // Higher capacity
                random_death_prob: 0.001,
            },
            _ => PopulationParams::default(),
        };
        
        Self {
            exp_type,
            world,
            population_dynamics: PopulationDynamics::new(params),
            hazard_tracker: HazardRateTracker::new(1000),
            state_history: Vec::new(),
        }
    }
    
    /// Run simulation for N ticks
    pub fn run(&mut self, ticks: usize) -> ExperimentResult {
        use fastrand::Rng;
        let mut rng = Rng::new();
        
        for tick in 0..ticks {
            // 1. Population dynamics
            self.population_dynamics.step(&mut self.world);
            
            // 2. Track deaths for hazard rate
            let deaths = self.population_dynamics.deaths_this_tick;
            for _ in 0..deaths {
                self.hazard_tracker.record_death(tick);
            }
            
            // 3. Agent movement and interaction
            self.agent_step(&mut rng);
            
            // 4. Collect state vector every 100 ticks
            if tick % 100 == 0 {
                let state = self.collect_state_vector();
                self.state_history.push(state);
            }
            
            // 5. Advance world tick
            self.world.step();
        }
        
        // Generate result
        self.generate_result()
    }
    
    fn agent_step(&mut self, rng: &mut fastrand::Rng) {
        // Simple random movement for now
        let agent_ids: Vec<usize> = self.world.agents.iter()
            .filter(|a| a.alive)
            .map(|a| a.id)
            .collect();
        
        for id in agent_ids {
            if let Some(agent) = self.world.agents.get(id) {
                if !agent.alive { continue; }
                
                // Random walk with 20% probability
                if rng.u32(0..100) < 20 {
                    let dx = rng.i32(-1..2) as isize;
                    let dy = rng.i32(-1..2) as isize;
                    let dz = rng.i32(-1..2) as isize;
                    
                    let current = agent.pos;
                    let new_x = ((current.x as isize + dx).max(0).min(GRID_X as isize - 1)) as usize;
                    let new_y = ((current.y as isize + dy).max(0).min(GRID_Y as isize - 1)) as usize;
                    let new_z = ((current.z as isize + dz).max(0).min(GRID_Z as isize - 1)) as usize;
                    
                    let new_pos = Position::new(new_x, new_y, new_z);
                    self.world.move_agent(id, new_pos);
                }
            }
        }
    }
    
    fn collect_state_vector(&self) -> StateVector {
        let alive_agents: Vec<&Agent> = self.world.agents.iter()
            .filter(|a| a.alive)
            .collect();
        
        // N = population
        let n = alive_agents.len();
        
        // CDI = average of agent CDI contributions
        let cdi = if n > 0 {
            alive_agents.iter().map(|a| a.cdi_contribution() as f64).sum::<f64>() / n as f64
        } else {
            0.0
        };
        
        // r, CI from agent phases
        let phases: Vec<f64> = alive_agents.iter().map(|a| a.phase).collect();
        let r = compute_sync_order_parameter(&phases);
        let ci = compute_condensation_index(&phases);
        
        // E = average energy
        let e = if n > 0 {
            alive_agents.iter().map(|a| a.energy as f64).sum::<f64>() / n as f64
        } else {
            0.0
        };
        
        // h = hazard rate
        let h = self.hazard_tracker.hazard_rate();
        
        StateVector { cdi, ci, r, n, e, h }
    }
    
    fn generate_result(&self) -> ExperimentResult {
        let final_pop = self.world.population();
        let genesis_count = match self.exp_type {
            ExperimentAtoE::Survival => 100,
            ExperimentAtoE::Evolution => 80,
            ExperimentAtoE::Stress => 120,
            ExperimentAtoE::Collaboration => 90,
            ExperimentAtoE::Akashic => 100,
        };
        
        let survival_rate = final_pop as f32 / genesis_count as f32;
        
        // Get final CDI
        let cdi_final = if let Some(last) = self.state_history.last() {
            last.cdi as f32
        } else {
            0.0
        };
        
        // Success criteria varies by experiment
        let success = match self.exp_type {
            ExperimentAtoE::Survival => final_pop > genesis_count / 3,
            ExperimentAtoE::Evolution => survival_rate > 0.8,
            ExperimentAtoE::Stress => final_pop > 0, // Any survival under stress
            ExperimentAtoE::Collaboration => survival_rate > 1.0, // Growth
            ExperimentAtoE::Akashic => final_pop > genesis_count / 3,
        };
        
        ExperimentResult {
            experiment: self.exp_type.name().to_string(),
            seed: 0, // TODO: track seed
            success,
            final_population: final_pop,
            survival_rate,
            cdi_final,
            notes: format!("v19 real simulation, {} state vectors collected", self.state_history.len()),
        }
    }
    
    /// Export state history to CSV
    pub fn export_csv(&self, path: &str) -> std::io::Result<()> {
        use std::io::Write;
        let mut file = std::fs::File::create(path)?;
        
        writeln!(file, "tick,{}", StateVector::csv_header())?;
        for (i, state) in self.state_history.iter().enumerate() {
            writeln!(file, "{},{}", i * 100, state.to_csv())?;
        }
        
        Ok(())
    }
}

/// Run A-E matrix with real v19 simulation
pub fn run_matrix_v19(config: &RunConfig) -> Vec<ExperimentResult> {
    let experiments = vec![
        ExperimentAtoE::Survival,
        ExperimentAtoE::Evolution,
        ExperimentAtoE::Stress,
        ExperimentAtoE::Collaboration,
        ExperimentAtoE::Akashic,
    ];
    
    let mut results = Vec::new();
    
    for (idx, exp) in experiments.iter().enumerate() {
        println!("Running {} (v19 real)...", exp.name());
        
        let seed = config.seeds.get(idx).copied().unwrap_or(42 + idx as u64);
        let mut experiment = V19Experiment::new(*exp, seed);
        
        // Run shorter simulation for faster testing
        let ticks = if config.is_research_scale() { 10000 } else { 1000 };
        let result = experiment.run(ticks);
        
        println!("  Result: {} (pop={}, CDI={:.3})", 
            if result.success { "PASS" } else { "FAIL" },
            result.final_population,
            result.cdi_final);
        
        // Export state history
        let csv_path = format!("/tmp/{}_state.csv", exp.name());
        let _ = experiment.export_csv(&csv_path);
        
        results.push(result);
    }
    
    results
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_v19_survival() {
        let mut exp = V19Experiment::new(ExperimentAtoE::Survival, 42);
        let result = exp.run(100);
        
        println!("Survival: pop={}, CDI={:.3}", result.final_population, result.cdi_final);
        assert!(result.final_population > 0);
    }
    
    #[test]
    fn test_v19_collaboration() {
        let mut exp = V19Experiment::new(ExperimentAtoE::Collaboration, 42);
        let result = exp.run(100);
        
        println!("Collaboration: pop={}, rate={:.2}", result.final_population, result.survival_rate);
        // Collaboration should have higher survival due to better params
    }
    
    #[test]
    fn test_state_vector_collection() {
        let mut exp = V19Experiment::new(ExperimentAtoE::Survival, 42);
        exp.run(500); // 5 state vectors (every 100 ticks)
        
        assert!(!exp.state_history.is_empty());
        
        let state = &exp.state_history[0];
        assert!(state.n > 0); // Has population
        assert!(state.cdi >= 0.0 && state.cdi <= 1.0);
        assert!(state.r >= 0.0 && state.r <= 1.0);
    }
}
