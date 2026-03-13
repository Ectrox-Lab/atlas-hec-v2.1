//! Synchronization Order Parameter (r)
//! 
//! Kuramoto order parameter: r = |Σ e^(iθ_j)| / N
//! 
//! Source: e1_critical_coupling/src/bin/e1_overnight_batch.rs

/// Compute synchronization order parameter
/// 
/// # Arguments
/// * `phases` - Agent phase angles θ_j
/// 
/// # Returns
/// * r ∈ [0, 1]: 0 = complete disorder, 1 = complete synchronization
pub fn compute_sync_order_parameter(phases: &[f64]) -> f64 {
    if phases.is_empty() {
        return 0.0;
    }
    
    let n = phases.len() as f64;
    let (sum_cos, sum_sin) = phases.iter()
        .fold((0.0, 0.0), |(c, s), &theta| {
            (c + theta.cos(), s + theta.sin())
        });
    
    ((sum_cos / n).powi(2) + (sum_sin / n).powi(2)).sqrt()
}

/// Compute order parameter with phase ψ
/// Returns (r, ψ) where ψ is the average phase
pub fn compute_order_parameter_with_phase(phases: &[f64]) -> (f64, f64) {
    if phases.is_empty() {
        return (0.0, 0.0);
    }
    
    let n = phases.len() as f64;
    let (sum_cos, sum_sin) = phases.iter()
        .fold((0.0, 0.0), |(c, s), &theta| {
            (c + theta.cos(), s + theta.sin())
        });
    
    let r = ((sum_cos / n).powi(2) + (sum_sin / n).powi(2)).sqrt();
    let psi = (sum_sin / n).atan2(sum_cos / n);
    
    (r, psi)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::f64::consts::PI;
    
    #[test]
    fn test_complete_sync() {
        // All phases same → r = 1
        let phases = vec![0.0; 100];
        let r = compute_sync_order_parameter(&phases);
        assert!((r - 1.0).abs() < 1e-10);
    }
    
    #[test]
    fn test_complete_disorder() {
        // Uniformly distributed → r ≈ 0
        let phases: Vec<f64> = (0..1000)
            .map(|i| 2.0 * PI * i as f64 / 1000.0)
            .collect();
        let r = compute_sync_order_parameter(&phases);
        assert!(r < 0.1);
    }
}
