//! 3D Grid World: 50×50×16
//! 
//! Multi-agent spatial environment with:
//! - 3D positions (x, y, z)
//! - Food sources
//! - Obstacles
//! - Neighbor queries

use super::agent::Agent;

pub const GRID_X: usize = 50;
pub const GRID_Y: usize = 50;
pub const GRID_Z: usize = 16;

/// 3D position
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct Position {
    pub x: usize,
    pub y: usize,
    pub z: usize,
}

impl Position {
    pub fn new(x: usize, y: usize, z: usize) -> Self {
        Self {
            x: x.min(GRID_X - 1),
            y: y.min(GRID_Y - 1),
            z: z.min(GRID_Z - 1),
        }
    }
    
    /// Manhattan distance
    pub fn manhattan(&self, other: &Position) -> usize {
        self.x.abs_diff(other.x) + 
        self.y.abs_diff(other.y) + 
        self.z.abs_diff(other.z)
    }
    
    /// Euclidean distance squared
    pub fn distance_sq(&self, other: &Position) -> f64 {
        let dx = self.x as f64 - other.x as f64;
        let dy = self.y as f64 - other.y as f64;
        let dz = self.z as f64 - other.z as f64;
        dx * dx + dy * dy + dz * dz
    }
}

/// Food source
#[derive(Clone, Copy, Debug)]
pub struct Food {
    pub pos: Position,
    pub energy: f32,
    pub regrow_tick: usize,
}

impl Food {
    pub fn new(x: usize, y: usize, z: usize, energy: f32) -> Self {
        Self {
            pos: Position::new(x, y, z),
            energy,
            regrow_tick: 0,
        }
    }
}

/// 3D Grid World
pub struct GridWorld {
    /// Agent positions (index in agents vector)
    pub grid: [[[Option<usize>; GRID_Z]; GRID_Y]; GRID_X],
    /// Agents
    pub agents: Vec<Agent>,
    /// Food sources
    pub food: Vec<Food>,
    /// Current tick
    pub tick: usize,
    /// Max ticks
    pub max_ticks: usize,
}

impl GridWorld {
    pub fn new() -> Self {
        Self {
            grid: [[[None; GRID_Z]; GRID_Y]; GRID_X],
            agents: Vec::new(),
            food: Vec::new(),
            tick: 0,
            max_ticks: 100_000,
        }
    }
    
    /// Spawn agent at position
    pub fn spawn_agent(&mut self, x: usize, y: usize, z: usize) -> usize {
        let agent_id = self.agents.len();
        let pos = Position::new(x, y, z);
        
        if self.grid[pos.x][pos.y][pos.z].is_none() {
            self.grid[pos.x][pos.y][pos.z] = Some(agent_id);
            self.agents.push(Agent::new(agent_id, pos));
            agent_id
        } else {
            // Position occupied, return existing
            self.grid[pos.x][pos.y][pos.z].unwrap()
        }
    }
    
    /// Remove agent
    pub fn remove_agent(&mut self, agent_id: usize) {
        if let Some(agent) = self.agents.get(agent_id) {
            let pos = agent.pos;
            if let Some(id) = self.grid[pos.x][pos.y][pos.z] {
                if id == agent_id {
                    self.grid[pos.x][pos.y][pos.z] = None;
                }
            }
            // Mark as dead
            if let Some(agent) = self.agents.get_mut(agent_id) {
                agent.alive = false;
            }
        }
    }
    
    /// Move agent
    pub fn move_agent(&mut self, agent_id: usize, new_pos: Position) -> bool {
        if let Some(agent) = self.agents.get(agent_id) {
            if !agent.alive {
                return false;
            }
            
            let old_pos = agent.pos;
            
            // Check if new position is empty
            if self.grid[new_pos.x][new_pos.y][new_pos.z].is_some() {
                return false;
            }
            
            // Update grid
            self.grid[old_pos.x][old_pos.y][old_pos.z] = None;
            self.grid[new_pos.x][new_pos.y][new_pos.z] = Some(agent_id);
            
            // Update agent
            if let Some(agent) = self.agents.get_mut(agent_id) {
                agent.pos = new_pos;
            }
            
            true
        } else {
            false
        }
    }
    
    /// Get agent at position
    pub fn agent_at(&self, pos: Position) -> Option<&Agent> {
        self.grid[pos.x][pos.y][pos.z]
            .and_then(|id| self.agents.get(id))
    }
    
    /// Get mutable agent at position
    pub fn agent_at_mut(&mut self, pos: Position) -> Option<&mut Agent> {
        let id = self.grid[pos.x][pos.y][pos.z]?;
        self.agents.get_mut(id)
    }
    
    /// Find neighbors within radius
    pub fn neighbors(&self, pos: Position, radius: usize) -> Vec<&Agent> {
        let mut result = Vec::new();
        
        let x_min = pos.x.saturating_sub(radius);
        let x_max = (pos.x + radius).min(GRID_X - 1);
        let y_min = pos.y.saturating_sub(radius);
        let y_max = (pos.y + radius).min(GRID_Y - 1);
        let z_min = pos.z.saturating_sub(radius);
        let z_max = (pos.z + radius).min(GRID_Z - 1);
        
        for x in x_min..=x_max {
            for y in y_min..=y_max {
                for z in z_min..=z_max {
                    if x == pos.x && y == pos.y && z == pos.z {
                        continue;
                    }
                    if let Some(id) = self.grid[x][y][z] {
                        if let Some(agent) = self.agents.get(id) {
                            if agent.alive {
                                result.push(agent);
                            }
                        }
                    }
                }
            }
        }
        
        result
    }
    
    /// Spawn food randomly
    pub fn spawn_food_random(&mut self, count: usize, energy: f32) {
        use fastrand::Rng;
        let mut rng = Rng::new();
        
        for _ in 0..count {
            let x = rng.usize(0..GRID_X);
            let y = rng.usize(0..GRID_Y);
            let z = rng.usize(0..GRID_Z);
            self.food.push(Food::new(x, y, z, energy));
        }
    }
    
    /// Get food at position
    pub fn food_at(&self, pos: Position) -> Option<&Food> {
        self.food.iter().find(|f| f.pos == pos)
    }
    
    /// Remove food at position
    pub fn remove_food(&mut self, pos: Position) {
        if let Some(idx) = self.food.iter().position(|f| f.pos == pos) {
            self.food.remove(idx);
        }
    }
    
    /// Population count (alive agents)
    pub fn population(&self) -> usize {
        self.agents.iter().filter(|a| a.alive).count()
    }
    
    /// Advance tick
    pub fn step(&mut self) {
        self.tick += 1;
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_grid_dimensions() {
        assert_eq!(GRID_X, 50);
        assert_eq!(GRID_Y, 50);
        assert_eq!(GRID_Z, 16);
    }
    
    #[test]
    fn test_spawn_agent() {
        let mut world = GridWorld::new();
        let id = world.spawn_agent(25, 25, 8);
        assert_eq!(world.population(), 1);
        assert!(world.agents[id].alive);
    }
    
    #[test]
    fn test_move_agent() {
        let mut world = GridWorld::new();
        let id = world.spawn_agent(25, 25, 8);
        let new_pos = Position::new(26, 25, 8);
        
        assert!(world.move_agent(id, new_pos));
        assert_eq!(world.agents[id].pos, new_pos);
    }
    
    #[test]
    fn test_neighbors() {
        let mut world = GridWorld::new();
        let center = Position::new(25, 25, 8);
        world.spawn_agent(25, 25, 8);
        world.spawn_agent(26, 25, 8);
        world.spawn_agent(27, 25, 8);
        
        let neighbors = world.neighbors(center, 2);
        assert_eq!(neighbors.len(), 2);
    }
}
