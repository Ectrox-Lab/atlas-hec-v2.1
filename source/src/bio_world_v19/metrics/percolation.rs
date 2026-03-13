//! Percolation Ratio (P)
//! 
//! P = largest_component_size / N
//! 
//! Percolation transition when P jumps from ~0 to ~1
//! 
//! Sources:
//! - e1_critical_coupling/src/bin/e1_overnight_batch.rs
//! - e3_percolation/src/main.rs

use std::collections::HashSet;

/// Compute percolation ratio from phase clustering
/// 
/// Simplified: fraction of oscillators within π/4 of mean phase
/// 
/// # Arguments
/// * `phases` - Agent phase angles
/// 
/// # Returns
/// * P ∈ [0, 1]: fraction in giant cluster
pub fn compute_percolation_ratio(phases: &[f64]) -> f64 {
    if phases.is_empty() {
        return 0.0;
    }
    
    let n = phases.len();
    
    // Compute mean phase
    let (sum_cos, sum_sin) = phases.iter()
        .fold((0.0, 0.0), |(c, s), &theta| {
            (c + theta.cos(), s + theta.sin())
        });
    let mean_phase = (sum_sin / n as f64).atan2(sum_cos / n as f64);
    
    // Count oscillators within π/4 of mean
    let in_cluster = phases.iter()
        .filter(|&&theta| {
            let diff = (theta - mean_phase).abs()
                .min(2.0 * std::f64::consts::PI - (theta - mean_phase).abs());
            diff < std::f64::consts::PI / 4.0
        })
        .count();
    
    in_cluster as f64 / n as f64
}

/// Compute percolation from network using DFS
/// 
/// # Arguments
/// * `adjacency` - Adjacency list
/// * `n` - Number of nodes
/// 
/// # Returns
/// * P = largest_component / n
pub fn compute_percolation_from_network(adjacency: &[Vec<usize>], n: usize) -> f64 {
    if n == 0 {
        return 0.0;
    }
    
    let mut visited = vec![false; n];
    let mut max_component = 0;
    
    for start in 0..n {
        if !visited[start] {
            let component_size = dfs_component(start, adjacency, &mut visited);
            max_component = max_component.max(component_size);
        }
    }
    
    max_component as f64 / n as f64
}

fn dfs_component(start: usize, adjacency: &[Vec<usize>], visited: &mut [bool]) -> usize {
    let mut stack = vec![start];
    let mut count = 0;
    
    while let Some(node) = stack.pop() {
        if visited[node] {
            continue;
        }
        visited[node] = true;
        count += 1;
        
        for &neighbor in &adjacency[node] {
            if !visited[neighbor] {
                stack.push(neighbor);
            }
        }
    }
    
    count
}

/// Find connected components
/// 
/// Returns vector of component sizes
pub fn find_components(adjacency: &[Vec<usize>], n: usize) -> Vec<usize> {
    let mut visited = vec![false; n];
    let mut components = Vec::new();
    
    for start in 0..n {
        if !visited[start] {
            let size = dfs_component(start, adjacency, &mut visited);
            if size > 0 {
                components.push(size);
            }
        }
    }
    
    components
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::f64::consts::PI;
    
    #[test]
    fn test_phase_percolation() {
        // All phases clustered → high P
        let phases = vec![0.1, 0.2, 0.15, 0.25];
        let p = compute_percolation_ratio(&phases);
        assert!(p > 0.9);
    }
    
    #[test]
    fn test_network_percolation() {
        // Connected graph: one component
        let adjacency = vec![
            vec![1],      // 0 connects to 1
            vec![0, 2],   // 1 connects to 0, 2
            vec![1],      // 2 connects to 1
        ];
        let p = compute_percolation_from_network(&adjacency, 3);
        assert!((p - 1.0).abs() < 0.01);
        
        // Disconnected: two components
        let adjacency = vec![
            vec![1],
            vec![0],
            vec![],       // isolated
        ];
        let p = compute_percolation_from_network(&adjacency, 3);
        assert!((p - 2.0/3.0).abs() < 0.01);
    }
}
