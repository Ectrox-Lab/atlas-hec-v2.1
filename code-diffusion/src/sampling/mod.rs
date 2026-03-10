use crate::data::{EditDNA, PatchCategory};
use crate::diffusion::Diffusion;
use crate::models::RealUNet;
use ndarray::{Array1, Array3};
use rand::distributions::Distribution;
use rand::{SeedableRng};
use rand::rngs::StdRng;
use rand_distr::StandardNormal;

/// Generator for Code-DNA samples
pub struct CodeDNAGenerator {
    diffusion: Diffusion,
    unet: RealUNet,
}

impl CodeDNAGenerator {
    pub fn new(diffusion: Diffusion, unet: RealUNet) -> Self {
        Self { diffusion, unet }
    }
    
    /// Generate samples with classifier-free guidance
    pub fn generate(
        &self,
        condition: PatchCategory,
        num_samples: usize,
        cond_weight: f64,
    ) -> Vec<EditDNA> {
        self.generate_with_seed(condition, num_samples, cond_weight, None)
    }
    
    /// Generate with explicit seed for P0-4 reproducibility testing
    /// 
    /// Full deterministic chain:
    /// 1. Initial noise from seeded RNG
    /// 2. Each reverse step uses the same seeded RNG for posterior noise
    /// 3. Output is 100% reproducible given same seed
    pub fn generate_with_seed(
        &self,
        condition: PatchCategory,
        num_samples: usize,
        cond_weight: f64,
        seed: Option<u64>,
    ) -> Vec<EditDNA> {
        let timesteps = self.diffusion.timesteps();
        let mut rng: StdRng = match seed {
            Some(s) => StdRng::seed_from_u64(s),
            None => StdRng::from_entropy(),
        };
        
        // Start from noise (deterministic if seed provided)
        let mut x: Array3<f64> = Array3::from_shape_fn(
            (num_samples, EditDNA::NUM_CHANNELS, EditDNA::SEQ_LEN),
            |_| StandardNormal.sample(&mut rng),
        );
        
        // Class tensor
        let classes = Array1::from_elem(num_samples, condition as usize as f64);
        
        // Reverse diffusion process with DETERMINISTIC RNG
        for t in (0..timesteps).rev() {
            let t_tensor = Array1::from_elem(num_samples, t as f64);
            
            if cond_weight > 1.0 {
                // Classifier-free guidance with seeded RNG
                x = self.p_sample_guided(&x, &t_tensor, &classes, t, cond_weight, &mut rng);
            } else {
                // Unconditional sampling with seeded RNG
                x = self.p_sample(&x, &t_tensor, t, &mut rng);
            }
        }
        
        // Convert tensors back to EditDNA
        (0..num_samples)
            .map(|i| {
                let sample: ndarray::Array2<f64> = x.slice(ndarray::s![i, .., ..]).to_owned();
                EditDNA::from_tensor(&sample, condition)
            })
            .collect()
    }
    
    /// Deterministic p_sample using provided RNG
    fn p_sample<R: rand::Rng>(
        &self, 
        x: &Array3<f64>, 
        t: &Array1<f64>, 
        t_index: usize,
        rng: &mut R,
    ) -> Array3<f64> {
        // Predict noise using REAL model
        let classes = Array1::zeros(x.shape()[0]);
        let noise_pred = self.unet.forward(x, t, &classes);
        
        // Apply reverse diffusion with DETERMINISTIC RNG
        self.diffusion.p_sample(x, t_index, &noise_pred, rng)
    }
    
    /// Deterministic guided sampling using provided RNG
    fn p_sample_guided<R: rand::Rng>(
        &self,
        x: &Array3<f64>,
        t: &Array1<f64>,
        classes: &Array1<f64>,
        t_index: usize,
        cond_weight: f64,
        rng: &mut R,
    ) -> Array3<f64> {
        let batch_size = x.shape()[0];
        
        // Conditional prediction using REAL model
        let eps_cond = self.unet.forward(x, t, classes);
        
        // Unconditional prediction (classes = 0)
        let classes_uncond = Array1::zeros(batch_size);
        let eps_uncond = self.unet.forward(x, t, &classes_uncond);
        
        // Classifier-free guidance: eps = (1+w)*eps_cond - w*eps_uncond
        let eps = &eps_cond * (1.0 + cond_weight) - &eps_uncond * cond_weight;
        
        // Apply reverse diffusion with DETERMINISTIC RNG
        self.diffusion.p_sample(x, t_index, &eps, rng)
    }
}

/// Batch generator for high-throughput candidate generation
pub struct BatchGenerator {
    generator: CodeDNAGenerator,
    batch_size: usize,
}

impl BatchGenerator {
    pub fn new(generator: CodeDNAGenerator, batch_size: usize) -> Self {
        Self {
            generator,
            batch_size,
        }
    }
    
    /// Generate large number of candidates in batches
    pub fn generate_batch(
        &self,
        condition: PatchCategory,
        total_samples: usize,
        cond_weight: f64,
    ) -> Vec<EditDNA> {
        let num_batches = (total_samples + self.batch_size - 1) / self.batch_size;
        let mut all_samples = vec![];
        
        for i in 0..num_batches {
            let batch_samples = total_samples.min((i + 1) * self.batch_size) - i * self.batch_size;
            let samples = self.generator.generate(condition, batch_samples, cond_weight);
            all_samples.extend(samples);
        }
        
        all_samples
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::diffusion::DiffusionConfig;
    
    #[test]
    fn test_generator() {
        let diffusion = Diffusion::new(DiffusionConfig::default());
        let unet = RealUNet::new(64, 128, 64, 8);
        let generator = CodeDNAGenerator::new(diffusion, unet);
        
        let samples = generator.generate(PatchCategory::BugFix, 5, 1.0);
        assert_eq!(samples.len(), 5);
    }
    
    #[test]
    fn test_deterministic_generation() {
        let diffusion = Diffusion::new(DiffusionConfig::default());
        let unet = RealUNet::new(64, 128, 64, 8);
        let generator = CodeDNAGenerator::new(diffusion, unet);
        
        // Same seed should produce identical outputs
        let samples1 = generator.generate_with_seed(PatchCategory::BugFix, 5, 2.0, Some(42));
        let samples2 = generator.generate_with_seed(PatchCategory::BugFix, 5, 2.0, Some(42));
        
        assert_eq!(samples1.len(), samples2.len());
        for (s1, s2) in samples1.iter().zip(samples2.iter()) {
            assert_eq!(s1.tokens, s2.tokens, "Same seed should produce identical tokens");
        }
    }
    
    #[test]
    fn test_different_seeds_produce_different_results() {
        let diffusion = Diffusion::new(DiffusionConfig::default());
        let unet = RealUNet::new(64, 128, 64, 8);
        let generator = CodeDNAGenerator::new(diffusion, unet);
        
        // Different seeds should produce different outputs
        let samples1 = generator.generate_with_seed(PatchCategory::BugFix, 5, 2.0, Some(42));
        let samples2 = generator.generate_with_seed(PatchCategory::BugFix, 5, 2.0, Some(43));
        
        let all_same: bool = samples1.iter().zip(samples2.iter())
            .all(|(s1, s2)| s1.tokens == s2.tokens);
        assert!(!all_same, "Different seeds should produce different results");
    }
}
