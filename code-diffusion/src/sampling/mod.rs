use crate::data::{EditDNA, PatchCategory};
use crate::diffusion::Diffusion;
use crate::models::UNet;
use ndarray::{Array1, Array3};
use rand::distributions::{Distribution, StandardNormal};
use rand::thread_rng;

/// Generator for Code-DNA samples
pub struct CodeDNAGenerator {
    diffusion: Diffusion,
    unet: UNet,
}

impl CodeDNAGenerator {
    pub fn new(diffusion: Diffusion, unet: UNet) -> Self {
        Self { diffusion, unet }
    }
    
    /// Generate samples with classifier-free guidance
    /// 
    /// Args:
    ///   condition: Patch category condition
    ///   num_samples: Number of samples to generate
    ///   cond_weight: Guidance scale (1.0 = no guidance, higher = stronger condition)
    /// 
    /// Returns:
    ///   Generated EditDNA samples
    pub fn generate(
        &self,
        condition: PatchCategory,
        num_samples: usize,
        cond_weight: f64,
    ) -> Vec<EditDNA> {
        let timesteps = self.diffusion.timesteps();
        let mut rng = thread_rng();
        
        // Start from noise
        let mut x: Array3<f64> = Array3::from_shape_fn(
            (num_samples, EditDNA::NUM_CHANNELS, EditDNA::SEQ_LEN),
            |_| StandardNormal.sample(&mut rng),
        );
        
        // Class tensor
        let classes = Array1::from_elem(num_samples, condition as usize as f64);
        
        // Reverse diffusion process
        for t in (0..timesteps).rev() {
            let t_tensor = Array1::from_elem(num_samples, t as f64);
            
            if cond_weight > 1.0 {
                // Classifier-free guidance
                x = self.p_sample_guided(&x, &t_tensor, &classes, t, cond_weight);
            } else {
                // Unconditional sampling
                x = self.p_sample(&x, &t_tensor, t);
            }
        }
        
        // Convert tensors back to EditDNA
        (0..num_samples)
            .map(|i| {
                let sample = x.slice(ndarray::s![i, .., ..]);
                EditDNA::from_tensor(&sample.to_owned().insert_axis(ndarray::Axis(0)), condition)
            })
            .collect()
    }
    
    fn p_sample(&self, x: &Array3<f64>, t: &Array1<f64>, t_index: usize) -> Array3<f64> {
        // Predict noise
        let classes = Array1::zeros(x.shape()[0]);
        let noise_pred = self.unet.forward(x, t, &classes);
        
        // Apply reverse diffusion
        self.diffusion.p_sample(x, t_index, &noise_pred)
    }
    
    fn p_sample_guided(
        &self,
        x: &Array3<f64>,
        t: &Array1<f64>,
        classes: &Array1<f64>,
        t_index: usize,
        cond_weight: f64,
    ) -> Array3<f64> {
        let batch_size = x.shape()[0];
        
        // Conditional prediction
        let eps_cond = self.unet.forward(x, t, classes);
        
        // Unconditional prediction (classes = 0)
        let classes_uncond = Array1::zeros(batch_size);
        let eps_uncond = self.unet.forward(x, t, &classes_uncond);
        
        // Classifier-free guidance: eps = (1+w)*eps_cond - w*eps_uncond
        let eps = &eps_cond * (1.0 + cond_weight) - &eps_uncond * cond_weight;
        
        // Apply reverse diffusion
        self.diffusion.p_sample(x, t_index, &eps)
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
    use crate::models::UNetConfig;
    
    #[test]
    fn test_generator() {
        let diffusion = crate::diffusion::Diffusion::new(DiffusionConfig::default());
        let unet = crate::models::UNet::new(UNetConfig::default());
        let generator = CodeDNAGenerator::new(diffusion, unet);
        
        let samples = generator.generate(PatchCategory::BugFix, 5, 1.0);
        assert_eq!(samples.len(), 5);
    }
}
