use ndarray::{Array1, Array2, Array3};
use rand::distributions::Distribution;
use rand::{Rng, SeedableRng};
use rand::rngs::StdRng;
use rand_distr::StandardNormal;

pub mod schedule;
pub use schedule::*;

/// Diffusion model configuration
#[derive(Debug, Clone)]
pub struct DiffusionConfig {
    /// Number of diffusion timesteps
    pub timesteps: usize,
    /// Beta schedule start
    pub beta_start: f64,
    /// Beta schedule end
    pub beta_end: f64,
    /// Loss type: "l1", "l2", or "huber"
    pub loss_type: String,
    /// Probability of unconditional sampling during training
    pub p_uncond: f64,
}

impl Default for DiffusionConfig {
    fn default() -> Self {
        Self {
            timesteps: 1000,
            beta_start: 1e-4,
            beta_end: 0.02,
            loss_type: "huber".to_string(),
            p_uncond: 0.1,
        }
    }
}

/// Core diffusion process
pub struct Diffusion {
    config: DiffusionConfig,
    betas: Array1<f64>,
    #[allow(dead_code)]
    alphas: Array1<f64>,
    #[allow(dead_code)]
    alphas_cumprod: Array1<f64>,
    sqrt_alphas_cumprod: Array1<f64>,
    sqrt_one_minus_alphas_cumprod: Array1<f64>,
    sqrt_recip_alphas: Array1<f64>,
    posterior_variance: Array1<f64>,
}

impl Diffusion {
    pub fn new(config: DiffusionConfig) -> Self {
        let betas = linear_beta_schedule(config.timesteps, config.beta_start, config.beta_end);
        let alphas = betas.mapv(|b| 1.0 - b);
        
        let mut alphas_cumprod = Array1::zeros(config.timesteps);
        let mut cumprod = 1.0;
        for i in 0..config.timesteps {
            cumprod *= alphas[i];
            alphas_cumprod[i] = cumprod;
        }
        
        let alphas_cumprod_prev = Self::shift_right(&alphas_cumprod, 1.0);
        
        let sqrt_alphas_cumprod = alphas_cumprod.mapv(|a| a.sqrt());
        let sqrt_one_minus_alphas_cumprod = alphas_cumprod.mapv(|a| (1.0 - a).sqrt());
        let sqrt_recip_alphas = alphas.mapv(|a| 1.0 / a.sqrt());
        
        let posterior_variance = &betas * (1.0 - &alphas_cumprod_prev) / (1.0 - &alphas_cumprod);
        
        Self {
            config,
            betas,
            alphas,
            alphas_cumprod,
            sqrt_alphas_cumprod,
            sqrt_one_minus_alphas_cumprod,
            sqrt_recip_alphas,
            posterior_variance,
        }
    }
    
    /// Forward diffusion: q(x_t | x_0)
    pub fn q_sample(&self, x_start: &Array3<f64>, t: usize, noise: Option<&Array3<f64>>) -> Array3<f64> {
        let noise = match noise {
            Some(n) => n.clone(),
            None => {
                // Fallback to thread_rng only when no noise provided
                // In deterministic mode, caller must provide noise
                let mut rng = rand::thread_rng();
                Array3::from_shape_fn(x_start.raw_dim(), |_| StandardNormal.sample(&mut rng))
            }
        };
        
        let sqrt_alpha_t = self.sqrt_alphas_cumprod[t];
        let sqrt_one_minus_alpha_t = self.sqrt_one_minus_alphas_cumprod[t];
        
        x_start * sqrt_alpha_t + noise * sqrt_one_minus_alpha_t
    }
    
    /// Reverse diffusion step: p(x_{t-1} | x_t)
    /// 
    /// Uses provided RNG for deterministic sampling when seed is set
    pub fn p_sample<R: Rng>(
        &self, 
        x: &Array3<f64>, 
        t: usize, 
        noise_pred: &Array3<f64>,
        rng: &mut R,
    ) -> Array3<f64> {
        let betas_t = self.betas[t];
        let sqrt_one_minus_alpha_t = self.sqrt_one_minus_alphas_cumprod[t];
        let sqrt_recip_alpha_t = self.sqrt_recip_alphas[t];
        
        // Model mean
        let model_mean = sqrt_recip_alpha_t * (x - &(noise_pred * betas_t / sqrt_one_minus_alpha_t));
        
        if t == 0 {
            model_mean
        } else {
            let posterior_variance_t = self.posterior_variance[t];
            let noise: Array3<f64> = Array3::from_shape_fn(x.raw_dim(), |_| {
                StandardNormal.sample(rng)
            });
            &model_mean + noise * posterior_variance_t.sqrt()
        }
    }
    
    /// Classifier-free guidance sampling with deterministic RNG
    pub fn p_sample_guided<R: Rng>(
        &self,
        x: &Array3<f64>,
        t: usize,
        eps_cond: &Array3<f64>,
        eps_uncond: &Array3<f64>,
        cond_weight: f64,
        rng: &mut R,
    ) -> Array3<f64> {
        // eps = (1 + w) * eps_cond - w * eps_uncond
        let eps = eps_cond * (1.0 + cond_weight) - eps_uncond * cond_weight;
        self.p_sample(x, t, &eps, rng)
    }
    
    /// Compute loss (training only, doesn't affect determinism)
    pub fn p_losses(&self, x_start: &Array3<f64>, t: usize, noise_pred: &Array3<f64>) -> f64 {
        let target: Array3<f64> = {
            let mut rng = rand::thread_rng();
            Array3::from_shape_fn(x_start.raw_dim(), |_| StandardNormal.sample(&mut rng))
        };
        
        let _x_noisy = self.q_sample(x_start, t, Some(&target));
        
        match self.config.loss_type.as_str() {
            "l1" => (&target - noise_pred).mapv(|v| v.abs()).mean().unwrap(),
            "l2" => (&target - noise_pred).mapv(|v| v * v).mean().unwrap(),
            "huber" => Self::huber_loss(&target, noise_pred, 1.0),
            _ => panic!("Unknown loss type"),
        }
    }
    
    fn huber_loss(target: &Array3<f64>, pred: &Array3<f64>, delta: f64) -> f64 {
        (target - pred)
            .mapv(|v| {
                let abs_v = v.abs();
                if abs_v < delta {
                    0.5 * v * v
                } else {
                    delta * (abs_v - 0.5 * delta)
                }
            })
            .mean()
            .unwrap()
    }
    
    fn shift_right(arr: &Array1<f64>, fill_value: f64) -> Array1<f64> {
        let mut result = Array1::from_elem(arr.len(), fill_value);
        for i in 1..arr.len() {
            result[i] = arr[i - 1];
        }
        result
    }
    
    pub fn timesteps(&self) -> usize {
        self.config.timesteps
    }
}

/// Deterministic diffusion sampler
pub struct DeterministicSampler {
    diffusion: Diffusion,
    rng: StdRng,
}

impl DeterministicSampler {
    pub fn new(diffusion: Diffusion, seed: u64) -> Self {
        Self {
            diffusion,
            rng: StdRng::seed_from_u64(seed),
        }
    }
    
    pub fn sample_step(
        &mut self,
        x: &Array3<f64>,
        t: usize,
        noise_pred: &Array3<f64>,
    ) -> Array3<f64> {
        self.diffusion.p_sample(x, t, noise_pred, &mut self.rng)
    }
    
    pub fn reset(&mut self, seed: u64) {
        self.rng = StdRng::seed_from_u64(seed);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_deterministic_p_sample() {
        let diffusion = Diffusion::new(DiffusionConfig::default());
        let x = Array3::zeros((2, 1, 64));
        let noise_pred = Array3::ones((2, 1, 64)) * 0.1;
        
        let mut rng1 = StdRng::seed_from_u64(42);
        let out1 = diffusion.p_sample(&x, 500, &noise_pred, &mut rng1);
        
        let mut rng2 = StdRng::seed_from_u64(42);
        let out2 = diffusion.p_sample(&x, 500, &noise_pred, &mut rng2);
        
        assert!((&out1 - &out2).mapv(|v| v.abs()).sum() < 1e-10, 
            "Same seed should produce identical output");
    }
    
    #[test]
    fn test_different_seeds_produce_different_output() {
        let diffusion = Diffusion::new(DiffusionConfig::default());
        let x = Array3::zeros((2, 1, 64));
        let noise_pred = Array3::ones((2, 1, 64)) * 0.1;
        
        let mut rng1 = StdRng::seed_from_u64(42);
        let out1 = diffusion.p_sample(&x, 500, &noise_pred, &mut rng1);
        
        let mut rng2 = StdRng::seed_from_u64(43);
        let out2 = diffusion.p_sample(&x, 500, &noise_pred, &mut rng2);
        
        assert!((&out1 - &out2).mapv(|v| v.abs()).sum() > 1e-6,
            "Different seeds should produce different output");
    }
}
