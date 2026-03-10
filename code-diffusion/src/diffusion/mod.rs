use ndarray::{Array, Array1, Array2, Array3, Axis, Ix1, Ix2, Ix3};
use rand::distributions::Distribution;
use rand::thread_rng;
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
    alphas: Array1<f64>,
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
        let noise = noise.map(|n| n.clone()).unwrap_or_else(|| {
            let mut rng = thread_rng();
            Array3::from_shape_fn(x_start.raw_dim(), |_| StandardNormal.sample(&mut rng))
        });
        
        let sqrt_alpha_t = self.sqrt_alphas_cumprod[t];
        let sqrt_one_minus_alpha_t = self.sqrt_one_minus_alphas_cumprod[t];
        
        x_start * sqrt_alpha_t + noise * sqrt_one_minus_alpha_t
    }
    
    /// Predict noise from x_t
    pub fn predict_noise(&self, x_t: &Array3<f64>, t: usize, noise_pred: &Array3<f64>) -> Array3<f64> {
        let sqrt_recip_alpha_t = self.sqrt_recip_alphas[t];
        let sqrt_one_minus_alpha_t = self.sqrt_one_minus_alphas_cumprod[t];
        
        sqrt_recip_alpha_t * (x_t - noise_pred * sqrt_one_minus_alpha_t)
    }
    
    /// Reverse diffusion step: p(x_{t-1} | x_t)
    pub fn p_sample(&self, x: &Array3<f64>, t: usize, noise_pred: &Array3<f64>) -> Array3<f64> {
        let betas_t = self.betas[t];
        let sqrt_one_minus_alpha_t = self.sqrt_one_minus_alphas_cumprod[t];
        let sqrt_recip_alpha_t = self.sqrt_recip_alphas[t];
        
        // Model mean
        let model_mean = sqrt_recip_alpha_t * (x - &(noise_pred * betas_t / sqrt_one_minus_alpha_t));
        
        if t == 0 {
            model_mean
        } else {
            let posterior_variance_t = self.posterior_variance[t];
            let mut rng = thread_rng();
            let noise: Array3<f64> = Array3::from_shape_fn(x.raw_dim(), |_| {
                StandardNormal.sample(&mut rng)
            });
            model_mean + noise * posterior_variance_t.sqrt()
        }
    }
    
    /// Classifier-free guidance sampling
    pub fn p_sample_guided(
        &self,
        x: &Array3<f64>,
        t: usize,
        eps_cond: &Array3<f64>,
        eps_uncond: &Array3<f64>,
        cond_weight: f64,
    ) -> Array3<f64> {
        // eps = (1 + w) * eps_cond - w * eps_uncond
        let eps = eps_cond * (1.0 + cond_weight) - eps_uncond * cond_weight;
        self.p_sample(x, t, &eps)
    }
    
    /// Compute loss
    pub fn p_losses(&self, x_start: &Array3<f64>, t: usize, noise_pred: &Array3<f64>) -> f64 {
        let target: Array3<f64> = {
            let mut rng = thread_rng();
            Array3::from_shape_fn(x_start.raw_dim(), |_| StandardNormal.sample(&mut rng))
        };
        
        let x_noisy = self.q_sample(x_start, t, Some(&target));
        
        match self.config.loss_type.as_str() {
            "l1" => (&target - noise_pred).mapv(|v| v.abs()).mean().unwrap(),
            "l2" => (&target - noise_pred).mapv(|v| v * v).mean().unwrap(),
            "huber" => Self::huber_loss(&target, noise_pred, 1.0),
            _ => panic!("Unknown loss type"),
        }
    }
    
    fn huber_loss(target: &Array3<f64>, pred: &Array3<f64>, delta: f64) -> f64 {
        let diff = target - pred;
        diff.mapv(|v| {
            if v.abs() <= delta {
                0.5 * v * v
            } else {
                delta * (v.abs() - 0.5 * delta)
            }
        }).mean().unwrap()
    }
    
    fn shift_right(arr: &Array1<f64>, pad_value: f64) -> Array1<f64> {
        let n = arr.len();
        let mut result = Array1::from_elem(n, pad_value);
        result.slice_mut(ndarray::s![1..]).assign(&arr.slice(ndarray::s![..n-1]));
        result
    }
    
    pub fn timesteps(&self) -> usize {
        self.config.timesteps
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_diffusion_init() {
        let config = DiffusionConfig::default();
        let diffusion = Diffusion::new(config);
        assert_eq!(diffusion.timesteps(), 1000);
    }
    
    #[test]
    fn test_q_sample() {
        let config = DiffusionConfig::default();
        let diffusion = Diffusion::new(config);
        
        let x_start = Array3::zeros((2, 4, 64));
        let x_t = diffusion.q_sample(&x_start, 500, None);
        
        assert_eq!(x_t.shape(), &[2, 4, 64]);
    }
}
