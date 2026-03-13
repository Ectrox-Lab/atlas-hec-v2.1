//! Condensation Index (CI)
//! 
//! Measures network/phase concentration.
//! Higher CI = more condensed structure.
//! 
//! Two variants:
//! - Phase-based: bin phases, measure max_bin / n
//! - Network-based: Σ(k_i²) / (Σk_i)²
//! 
//! Source: e1_critical_coupling/src/bin/e1_overnight_batch.rs

/// Compute CI from phase distribution
/// 
/// # Arguments
/// * `phases` - Agent phase angles
/// * `n_bins` - Number of phase bins (default: 8)
/// 
/// # Returns
/// * CI ∈ [0, 1]: 0 = uniform, 1 = all in one bin
pub fn compute_condensation_index(phases: &[f64]) -> f64 {
    if phases.is_empty() {
        return 0.0;
    }
    
    const N_BINS: usize = 8;
    let n = phases.len();
    let mut bins = vec![0; N_BINS];
    
    for &theta in phases {
        let bin = ((theta / (2.0 * std::f64::consts::PI)) * N_BINS as f64) as usize % N_BINS;
        bins[bin] += 1;
    }
    
    let max_bin = *bins.iter().max().unwrap() as f64;
    max_bin / n as f64
}

/// Compute CI from network degrees
/// 
/// CI = Σ(k_i²) / (Σk_i)²
/// 
/// # Arguments
/// * `degrees` - Node degrees
/// 
/// # Returns
/// * CI ∈ [0, 1]
pub fn compute_condensation_index_from_degrees(degrees: &[usize]) -> f64 {
    if degrees.is_empty() {
        return 0.0;
    }
    
    let k_sum: usize = degrees.iter().sum();
    if k_sum == 0 {
        return 0.0;
    }
    
    let k_squared_sum: usize = degrees.iter().map(|&k| k * k).sum();
    k_squared_sum as f64 / (k_sum * k_sum) as f64
}

/// Alternative: hub concentration = k_max / Σk_i
pub fn compute_hub_concentration(degrees: &[usize]) -> f64 {
    if degrees.is_empty() {
        return 0.0;
    }
    
    let k_max = degrees.iter().copied().max().unwrap_or(0);
    let k_sum: usize = degrees.iter().sum();
    
    if k_sum == 0 {
        return 0.0;
    }
    
    k_max as f64 / k_sum as f64
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_phase_condensation() {
        // All phases in same bin → CI = 1
        let phases = vec![0.1, 0.2, 0.3, 0.4];
        let ci = compute_condensation_index(&phases);
        assert!((ci - 1.0).abs() < 0.1);
    }
    
    #[test]
    fn test_network_condensation() {
        // Star network: one hub with degree n-1, others degree 1
        // degrees = [9, 1, 1, ...]: Σk = 18, Σk² = 90, CI = 90/324 = 0.278
        let degrees = vec![9, 1, 1, 1, 1, 1, 1, 1, 1, 1];
        let ci = compute_condensation_index_from_degrees(&degrees);
        assert!(ci > 0.2 && ci < 0.4); // Should be moderate for star
        
        // Complete graph: all degrees n-1
        // degrees = [9, 9, 9, ...]: Σk = 90, Σk² = 810, CI = 810/8100 = 0.1 (low)
        let complete = vec![9; 10];
        let ci_complete = compute_condensation_index_from_degrees(&complete);
        assert!(ci_complete < 0.15); // Should be low for complete graph
    }
}
