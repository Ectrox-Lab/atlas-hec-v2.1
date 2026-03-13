//! Beta schedules for diffusion process

use ndarray::Array1;

/// Linear beta schedule
pub fn linear_beta_schedule(timesteps: usize, beta_start: f64, beta_end: f64) -> Array1<f64> {
    Array1::linspace(beta_start, beta_end, timesteps)
}

/// Cosine beta schedule (improved for small timesteps)
pub fn cosine_beta_schedule(timesteps: usize, s: f64) -> Array1<f64> {
    let steps = timesteps + 1;
    let x: Vec<f64> = (0..steps).map(|i| i as f64 / steps as f64).collect();
    
    let alphas_cumprod: Vec<f64> = x.iter()
        .map(|&t| ((std::f64::consts::PI / 2.0 * (t + s) / (1.0 + s)).cos()).powi(2))
        .collect();
    
    let mut betas = Vec::with_capacity(timesteps);
    for i in 0..timesteps {
        let beta = (1.0 - alphas_cumprod[i + 1] / alphas_cumprod[i]).min(0.999);
        betas.push(beta);
    }
    
    Array1::from(betas)
}

/// Quadratic beta schedule
pub fn quadratic_beta_schedule(timesteps: usize, beta_start: f64, beta_end: f64) -> Array1<f64> {
    Array1::linspace(beta_start.sqrt(), beta_end.sqrt(), timesteps)
        .mapv(|v| v * v)
}

/// Sigmoid beta schedule
pub fn sigmoid_beta_schedule(timesteps: usize, beta_start: f64, beta_end: f64) -> Array1<f64> {
    let betas: Vec<f64> = (0..timesteps)
        .map(|i| {
            let t = -6.0 + 12.0 * i as f64 / (timesteps - 1) as f64;
            beta_start + (beta_end - beta_start) * sigmoid(t)
        })
        .collect();
    Array1::from(betas)
}

fn sigmoid(x: f64) -> f64 {
    1.0 / (1.0 + (-x).exp())
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_linear_schedule() {
        let betas = linear_beta_schedule(1000, 1e-4, 0.02);
        assert_eq!(betas.len(), 1000);
        assert!((betas[0] - 1e-4).abs() < 1e-6);
        assert!((betas[999] - 0.02).abs() < 1e-6);
    }
    
    #[test]
    fn test_cosine_schedule() {
        let betas = cosine_beta_schedule(1000, 0.008);
        assert_eq!(betas.len(), 1000);
        // Cosine schedule starts small and increases
        assert!(betas[0] < betas[500]);
    }
}
