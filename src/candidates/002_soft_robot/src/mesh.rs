//! 2D Deformable Mesh for Soft Robot
//! 
//! Implements a simple mass-spring system representing a soft body.
//! Used to study proprioceptive feedback and self-boundary discrimination.

use nalgebra::{Vector2, DVector};
use std::f32::consts::PI;

/// 2D Node with position, velocity, mass
#[derive(Clone, Debug, Copy)]
pub struct Node {
    pub pos: Vector2<f32>,
    pub vel: Vector2<f32>,
    pub mass: f32,
    pub fixed: bool,  // boundary constraint
}

impl Node {
    pub fn new(pos: Vector2<f32>, mass: f32) -> Self {
        Self {
            pos,
            vel: Vector2::zeros(),
            mass,
            fixed: false,
        }
    }
}

/// Spring connecting two nodes
#[derive(Clone, Debug, Copy)]
pub struct Spring {
    pub node_a: usize,
    pub node_b: usize,
    pub rest_length: f32,
    pub stiffness: f32,
    pub damping: f32,
}

impl Spring {
    pub fn new(a: usize, b: usize, rest_length: f32, stiffness: f32, damping: f32) -> Self {
        Self {
            node_a: a,
            node_b: b,
            rest_length,
            stiffness,
            damping,
        }
    }
    
    /// Compute force on node_a (opposite on node_b)
    pub fn compute_force(&self, nodes: &[Node]) -> Vector2<f32> {
        let node_a = &nodes[self.node_a];
        let node_b = &nodes[self.node_b];
        
        let delta = node_b.pos - node_a.pos;
        let dist = delta.norm();
        
        if dist < 1e-6 {
            return Vector2::zeros();
        }
        
        let direction = delta / dist;
        let stretch = dist - self.rest_length;
        
        // Spring force (Hooke's law)
        let spring_force = direction * stretch * self.stiffness;
        
        // Damping force
        let rel_vel = node_b.vel - node_a.vel;
        let damping_force = direction * rel_vel.dot(&direction) * self.damping;
        
        spring_force + damping_force
    }
}

/// Pressure force for soft body inflation
#[derive(Clone, Copy)]
pub struct PressureForce {
    pub pressure: f32,  // internal pressure
}

impl PressureForce {
    /// Compute pressure forces on all nodes
    /// Pressure acts perpendicular to surface edges
    pub fn apply(&self, nodes: &mut [Node], surface_edges: &[(usize, usize)]) {
        for (i, j) in surface_edges {
            let pos_i = nodes[*i].pos;
            let pos_j = nodes[*j].pos;
            
            // Edge vector
            let edge = pos_j - pos_i;
            // Normal (perpendicular, outward)
            let normal = Vector2::new(-edge.y, edge.x).normalize();
            
            // Pressure force proportional to edge length
            let force = normal * self.pressure * edge.norm() * 0.5;
            
            nodes[*i].vel += force / nodes[*i].mass;
            nodes[*j].vel += force / nodes[*j].mass;
        }
    }
}

/// 2D Soft Body Mesh
#[derive(Clone)]
pub struct SoftMesh {
    pub nodes: Vec<Node>,
    pub springs: Vec<Spring>,
    pub surface_edges: Vec<(usize, usize)>,
    pub pressure: PressureForce,
    pub gravity: Vector2<f32>,
    pub bounds: (Vector2<f32>, Vector2<f32>),  // (min, max)
    pub feedback_enabled: bool,
}

impl SoftMesh {
    /// Create a 4x4 grid mesh
    pub fn new_grid(
        center: Vector2<f32>,
        width: f32,
        height: f32,
        cols: usize,
        rows: usize,
    ) -> Self {
        let mut nodes = Vec::new();
        let mut springs = Vec::new();
        
        // Create nodes
        for row in 0..rows {
            for col in 0..cols {
                let x = center.x - width/2.0 + (col as f32 / (cols-1) as f32) * width;
                let y = center.y - height/2.0 + (row as f32 / (rows-1) as f32) * height;
                nodes.push(Node::new(Vector2::new(x, y), 1.0));
            }
        }
        
        // Create structural springs (horizontal and vertical)
        for row in 0..rows {
            for col in 0..cols {
                let idx = row * cols + col;
                
                // Horizontal spring
                if col < cols - 1 {
                    let right_idx = idx + 1;
                    let rest_length = width / (cols - 1) as f32;
                    springs.push(Spring::new(idx, right_idx, rest_length, 100.0, 2.0));
                }
                
                // Vertical spring
                if row < rows - 1 {
                    let below_idx = idx + cols;
                    let rest_length = height / (rows - 1) as f32;
                    springs.push(Spring::new(idx, below_idx, rest_length, 100.0, 2.0));
                }
            }
        }
        
        // Create surface edges for pressure
        let mut surface_edges = Vec::new();
        // Top and bottom edges
        for col in 0..cols-1 {
            surface_edges.push((col, col+1));  // top
            surface_edges.push(((rows-1)*cols+col, (rows-1)*cols+col+1));  // bottom
        }
        // Left and right edges
        for row in 0..rows-1 {
            surface_edges.push((row*cols, (row+1)*cols));  // left
            surface_edges.push((row*cols+cols-1, (row+1)*cols+cols-1));  // right
        }
        
        Self {
            nodes,
            springs,
            surface_edges,
            pressure: PressureForce { pressure: 50.0 },
            gravity: Vector2::new(0.0, -9.8),
            bounds: (
                Vector2::new(center.x - width, center.y - height),
                Vector2::new(center.x + width, center.y + height),
            ),
            feedback_enabled: true,
        }
    }
    
    /// One physics step using symplectic Euler
    pub fn step(&mut self, dt: f32) {
        // Apply gravity
        for node in &mut self.nodes {
            if !node.fixed {
                node.vel += self.gravity * dt;
            }
        }
        
        // Apply spring forces
        for spring in &self.springs {
            let force = spring.compute_force(&self.nodes);
            let inv_mass_a = 1.0 / self.nodes[spring.node_a].mass;
            let inv_mass_b = 1.0 / self.nodes[spring.node_b].mass;
            
            if !self.nodes[spring.node_a].fixed {
                self.nodes[spring.node_a].vel += force * inv_mass_a * dt;
            }
            if !self.nodes[spring.node_b].fixed {
                self.nodes[spring.node_b].vel -= force * inv_mass_b * dt;
            }
        }
        
        // Apply pressure
        self.pressure.apply(&mut self.nodes, &self.surface_edges);
        
        // Apply damping to all velocities
        for node in &mut self.nodes {
            if !node.fixed {
                node.vel *= 0.99;  // Global damping
            }
        }
        
        // Update positions
        for node in &mut self.nodes {
            if !node.fixed {
                node.pos += node.vel * dt;
                
                // Boundary constraints
                node.pos.x = node.pos.x.clamp(self.bounds.0.x, self.bounds.1.x);
                node.pos.y = node.pos.y.clamp(self.bounds.0.y, self.bounds.1.y);
                
                // Bounce off walls
                if node.pos.x <= self.bounds.0.x || node.pos.x >= self.bounds.1.x {
                    node.vel.x *= -0.5;
                }
                if node.pos.y <= self.bounds.0.y || node.pos.y >= self.bounds.1.y {
                    node.vel.y *= -0.5;
                }
            }
        }
    }
    
    /// Compute strain at each node (deformation measure)
    pub fn compute_strain(&self) -> Vec<f32> {
        self.nodes.iter().enumerate().map(|(idx, node)| {
            // Find connected springs
            let mut total_stretch = 0.0;
            let mut count = 0;
            
            for spring in &self.springs {
                if spring.node_a == idx || spring.node_b == idx {
                    let other = if spring.node_a == idx { spring.node_b } else { spring.node_a };
                    let dist = (self.nodes[other].pos - node.pos).norm();
                    let stretch = if spring.rest_length > 1e-3 {
                        ((dist - spring.rest_length) / spring.rest_length).abs()
                    } else {
                        0.0
                    };
                    total_stretch += stretch;
                    count += 1;
                }
            }
            
            if count > 0 { total_stretch / count as f32 } else { 0.0 }
        }).collect()
    }
    
    /// Get centroid of mesh
    pub fn centroid(&self) -> Vector2<f32> {
        let sum: Vector2<f32> = self.nodes.iter().map(|n| n.pos).sum();
        sum / self.nodes.len() as f32
    }
    
    /// Get bounding box
    pub fn bounding_box(&self) -> (Vector2<f32>, Vector2<f32>) {
        let mut min = self.nodes[0].pos;
        let mut max = self.nodes[0].pos;
        
        for node in &self.nodes {
            min = min.inf(&node.pos);
            max = max.sup(&node.pos);
        }
        
        (min, max)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_mesh_creation() {
        let mesh = SoftMesh::new_grid(Vector2::new(0.0, 0.0), 1.0, 1.0, 4, 4);
        assert_eq!(mesh.nodes.len(), 16);
        assert!(mesh.springs.len() > 0);
    }
    
    #[test]
    fn test_mesh_stability() {
        let mut mesh = SoftMesh::new_grid(Vector2::new(0.0, 0.0), 1.0, 1.0, 4, 4);
        let initial_centroid = mesh.centroid();
        
        // Run 100 steps
        for _ in 0..100 {
            mesh.step(0.01);
        }
        
        // Centroid shouldn't drift too far
        let final_centroid = mesh.centroid();
        let drift = (final_centroid - initial_centroid).norm();
        assert!(drift < 1.0, "Mesh drifted too far: {}", drift);
    }
}
