//! Population Dynamics
//! 
//! Birth/death/food/regeneration loop

use super::grid::{GridWorld, Position, GRID_X, GRID_Y, GRID_Z};
use super::agent::Agent;

/// Population dynamics parameters
#[derive(Clone, Copy, Debug)]
pub struct PopulationParams {
    /// Energy cost to reproduce
    pub reproduction_cost: f32,
    /// Food energy value
    pub food_energy: f32,
    /// Food regeneration interval
    pub food_regen_interval: usize,
    /// Carrying capacity (per grid cell)
    pub carrying_capacity: usize,
    /// Random death probability
    pub random_death_prob: f32,
}

impl Default for PopulationParams {
    fn default() -> Self {
        Self {
            reproduction_cost: 40.0,
            food_energy: 30.0,
            food_regen_interval: 100,
            carrying_capacity: 4,
            random_death_prob: 0.001,
        }
    }
}

/// Population dynamics controller
pub struct PopulationDynamics {
    pub params: PopulationParams,
    pub births_this_tick: usize,
    pub deaths_this_tick: usize,
    pub total_births: usize,
    pub total_deaths: usize,
}

impl PopulationDynamics {
    pub fn new(params: PopulationParams) -> Self {
        Self {
            params,
            births_this_tick: 0,
            deaths_this_tick: 0,
            total_births: 0,
            total_deaths: 0,
        }
    }
    
    /// Execute one tick of population dynamics
    pub fn step(&mut self, world: &mut GridWorld) {
        self.births_this_tick = 0;
        self.deaths_this_tick = 0;
        
        // 1. All agents metabolize
        self.metabolize_all(world);
        
        // 2. Agents eat food
        self.feeding(world);
        
        // 3. Reproduction
        self.reproduction(world);
        
        // 4. Regenerate food
        self.regenerate_food(world);
        
        // 5. Cleanup dead agents
        self.cleanup_dead(world);
    }
    
    fn metabolize_all(&mut self, world: &mut GridWorld) {
        for agent in world.agents.iter_mut() {
            if agent.alive {
                agent.metabolize();
                if !agent.alive {
                    self.deaths_this_tick += 1;
                    self.total_deaths += 1;
                }
            }
        }
    }
    
    fn feeding(&mut self, world: &mut GridWorld) {
        let food_positions: Vec<Position> = world.food.iter()
            .map(|f| f.pos)
            .collect();
        
        for pos in food_positions {
            if let Some(agent) = world.agent_at_mut(pos) {
                if agent.alive {
                    agent.eat(self.params.food_energy);
                    world.remove_food(pos);
                }
            }
        }
    }
    
    fn reproduction(&mut self, world: &mut GridWorld) {
        use fastrand::Rng;
        let mut rng = Rng::new();
        
        // Collect reproducing agents
        let reproducers: Vec<(usize, Position)> = world.agents.iter()
            .filter(|a| a.alive && a.can_reproduce(self.params.reproduction_cost))
            .map(|a| (a.id, a.pos))
            .collect();
        
        for (parent_id, parent_pos) in reproducers {
            // Find empty neighbor cell
            let offsets = [
                (0, 1, 0), (0, -1, 0), (1, 0, 0), (-1, 0, 0),
                (0, 0, 1), (0, 0, -1),
            ];
            
            for (dx, dy, dz) in offsets.iter().copied() {
                let new_x = (parent_pos.x as isize + dx).max(0).min(GRID_X as isize - 1) as usize;
                let new_y = (parent_pos.y as isize + dy).max(0).min(GRID_Y as isize - 1) as usize;
                let new_z = (parent_pos.z as isize + dz).max(0).min(GRID_Z as isize - 1) as usize;
                
                let new_pos = Position::new(new_x, new_y, new_z);
                
                // Check carrying capacity in neighborhood
                let neighbor_count = world.neighbors(new_pos, 2).len();
                if neighbor_count < self.params.carrying_capacity && world.grid[new_x][new_y][new_z].is_none() {
                    // Spawn offspring
                    let offspring_id = world.agents.len();
                    let offspring = Agent::reproduce(
                        &world.agents[parent_id],
                        offspring_id,
                        new_pos
                    );
                    
                    world.grid[new_x][new_y][new_z] = Some(offspring_id);
                    world.agents.push(offspring);
                    
                    // Parent pays cost
                    if let Some(parent) = world.agents.get_mut(parent_id) {
                        parent.pay_reproduction_cost(self.params.reproduction_cost);
                    }
                    
                    self.births_this_tick += 1;
                    self.total_births += 1;
                    break; // One offspring per parent per tick
                }
            }
        }
    }
    
    fn regenerate_food(&mut self, world: &mut GridWorld) {
        use fastrand::Rng;
        let mut rng = Rng::new();
        
        if world.tick % self.params.food_regen_interval == 0 {
            // Spawn random food
            let spawn_count = world.population() / 10 + 5;
            for _ in 0..spawn_count {
                let x = rng.usize(0..GRID_X);
                let y = rng.usize(0..GRID_Y);
                let z = rng.usize(0..GRID_Z);
                
                // Only spawn if no food already there
                if world.food_at(Position::new(x, y, z)).is_none() {
                    world.food.push(super::grid::Food::new(x, y, z, self.params.food_energy));
                }
            }
        }
    }
    
    fn cleanup_dead(&mut self, world: &mut GridWorld) {
        // Remove dead agents from grid (already marked as !alive)
        // This is handled by not counting them in population()
        // Full cleanup can be done periodically
    }
    
    /// Get population statistics
    pub fn stats(&self, world: &GridWorld) -> PopulationStats {
        PopulationStats {
            population: world.population(),
            births_this_tick: self.births_this_tick,
            deaths_this_tick: self.deaths_this_tick,
            total_births: self.total_births,
            total_deaths: self.total_deaths,
            food_count: world.food.len(),
        }
    }
}

/// Population statistics
#[derive(Clone, Copy, Debug)]
pub struct PopulationStats {
    pub population: usize,
    pub births_this_tick: usize,
    pub deaths_this_tick: usize,
    pub total_births: usize,
    pub total_deaths: usize,
    pub food_count: usize,
}

impl PopulationStats {
    pub fn net_growth(&self) -> isize {
        self.births_this_tick as isize - self.deaths_this_tick as isize
    }
    
    pub fn growth_rate(&self) -> f32 {
        if self.population == 0 {
            return 0.0;
        }
        self.net_growth() as f32 / self.population as f32
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_population_params() {
        let params = PopulationParams::default();
        assert!(params.reproduction_cost > 0.0);
        assert!(params.food_energy > 0.0);
    }
    
    #[test]
    fn test_metabolism_causes_death() {
        let mut world = GridWorld::new();
        let id = world.spawn_agent(25, 25, 8);
        
        // Set low energy
        world.agents[id].energy = 0.1;
        world.agents[id].metabolic_rate = 0.5;
        
        let mut dynamics = PopulationDynamics::new(PopulationParams::default());
        dynamics.step(&mut world);
        
        assert!(!world.agents[id].alive);
    }
}
