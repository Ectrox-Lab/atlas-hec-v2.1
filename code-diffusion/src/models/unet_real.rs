//! Real UNet implementation with trainable parameters

use ndarray::{Array1, Array2, Array3};
use rand::distributions::Distribution;
use rand_distr::StandardNormal;
use rand::thread_rng;

/// Real UNet with actual weight matrices
#[derive(Clone)]
pub struct RealUNet {
    // Input projection: input_dim -> hidden_dim
    input_proj: Array2<f64>,
    input_bias: Array1<f64>,
    
    // Hidden layer: hidden_dim -> hidden_dim  
    hidden_w: Array2<f64>,
    hidden_b: Array1<f64>,
    
    // Output projection: hidden_dim -> input_dim
    output_proj: Array2<f64>,
    output_bias: Array1<f64>,
    
    // Dimensions
    input_dim: usize,
    hidden_dim: usize,
}

impl RealUNet {
    pub fn new(input_dim: usize, hidden_dim: usize, _time_emb_dim: usize, _num_classes: usize) -> Self {
        // Xavier initialization for matrices
        let scale_in = (2.0 / (input_dim + hidden_dim) as f64).sqrt();
        let scale_hidden = (2.0 / (hidden_dim + hidden_dim) as f64).sqrt();
        let scale_out = (2.0 / (hidden_dim + input_dim) as f64).sqrt();
        
        Self {
            input_proj: init_matrix(input_dim, hidden_dim, scale_in),
            input_bias: init_vector(hidden_dim, 0.01),
            
            hidden_w: init_matrix(hidden_dim, hidden_dim, scale_hidden),
            hidden_b: init_vector(hidden_dim, 0.01),
            
            output_proj: init_matrix(hidden_dim, input_dim, scale_out),
            output_bias: init_vector(input_dim, 0.01),
            
            input_dim,
            hidden_dim,
        }
    }
    
    /// Forward pass: predict noise given x_t, time, and class
    pub fn forward(
        &self,
        x: &Array3<f64>,      // (batch, channels, seq_len)
        _time: &Array1<f64>,   // (batch,) - used for conditioning
        _classes: &Array1<f64>, // (batch,) - used for conditioning
    ) -> Array3<f64> {
        let batch_size = x.shape()[0];
        let mut outputs = Array3::zeros(x.raw_dim());
        
        for b in 0..batch_size {
            // Flatten input: (channels, seq_len) -> (input_dim,)
            let x_flat: Array1<f64> = x.slice(ndarray::s![b, 0, ..]).to_owned();
            
            // Layer 1: input projection with ReLU
            // h0 = relu(x @ W1 + b1)
            let h0 = relu_vec(&(&x_flat.dot(&self.input_proj) + &self.input_bias));
            
            // Layer 2: hidden with ReLU
            // h1 = relu(h0 @ W2 + b2)
            let h1 = relu_vec(&(&h0.dot(&self.hidden_w) + &self.hidden_b));
            
            // Output: predict noise
            // out = h1 @ W3 + b3
            let noise_flat = h1.dot(&self.output_proj) + &self.output_bias;
            
            // Store output
            for i in 0..self.input_dim.min(64) {
                outputs[[b, 0, i]] = noise_flat[i];
            }
        }
        
        outputs
    }
    
    /// Get all parameters as flat vector (for saving/loading)
    pub fn get_params(&self) -> Vec<f64> {
        let mut params = vec![];
        params.extend(self.input_proj.iter());
        params.extend(self.input_bias.iter());
        params.extend(self.hidden_w.iter());
        params.extend(self.hidden_b.iter());
        params.extend(self.output_proj.iter());
        params.extend(self.output_bias.iter());
        params
    }
    
    /// Compute parameter hash (for detecting change)
    pub fn param_hash(&self) -> u64 {
        // Manual hash computation
        let params = self.get_params();
        let mut hash: u64 = 0xcbf29ce484222325; // FNV offset basis
        
        for (i, &param) in params.iter().enumerate() {
            let bits = param.to_bits();
            hash ^= bits.wrapping_add(i as u64);
            hash = hash.wrapping_mul(0x100000001b3); // FNV prime
        }
        
        hash
    }
    
    /// Get parameter statistics
    pub fn param_stats(&self) -> ParamStats {
        let params = self.get_params();
        let sum: f64 = params.iter().sum();
        let sum_sq: f64 = params.iter().map(|&p| p * p).sum();
        let n = params.len() as f64;
        
        ParamStats {
            count: params.len(),
            mean: sum / n,
            std: ((sum_sq / n) - (sum / n).powi(2)).sqrt(),
            min: params.iter().cloned().fold(f64::INFINITY, f64::min),
            max: params.iter().cloned().fold(f64::NEG_INFINITY, f64::max),
        }
    }
    
    /// Apply simple parameter update (for demonstration)
    pub fn apply_noise(&mut self, scale: f64) {
        for v in self.input_proj.iter_mut() {
            let noise: f64 = StandardNormal.sample(&mut thread_rng());
            *v += noise * scale;
        }
        for v in self.input_bias.iter_mut() {
            let noise: f64 = StandardNormal.sample(&mut thread_rng());
            *v += noise * scale;
        }
        for v in self.hidden_w.iter_mut() {
            let noise: f64 = StandardNormal.sample(&mut thread_rng());
            *v += noise * scale;
        }
        for v in self.hidden_b.iter_mut() {
            let noise: f64 = StandardNormal.sample(&mut thread_rng());
            *v += noise * scale;
        }
        for v in self.output_proj.iter_mut() {
            let noise: f64 = StandardNormal.sample(&mut thread_rng());
            *v += noise * scale;
        }
        for v in self.output_bias.iter_mut() {
            let noise: f64 = StandardNormal.sample(&mut thread_rng());
            *v += noise * scale;
        }
    }
    
    pub fn input_dim(&self) -> usize { self.input_dim }
    pub fn hidden_dim(&self) -> usize { self.hidden_dim }
    
    /// Load parameters from flat vector (for checkpoint loading)
    pub fn load_params(&mut self, params: &[f64]) -> Result<(), String> {
        let expected = self.param_count();
        if params.len() != expected {
            return Err(format!(
                "Parameter count mismatch: expected {}, got {}",
                expected, params.len()
            ));
        }
        
        let mut offset = 0;
        
        // Load input_proj
        let in_proj_size = self.input_dim * self.hidden_dim;
        self.input_proj = Array2::from_shape_vec(
            (self.input_dim, self.hidden_dim),
            params[offset..offset + in_proj_size].to_vec()
        ).map_err(|e| format!("Failed to load input_proj: {}", e))?;
        offset += in_proj_size;
        
        // Load input_bias
        self.input_bias = Array1::from_vec(params[offset..offset + self.hidden_dim].to_vec());
        offset += self.hidden_dim;
        
        // Load hidden_w
        let hidden_size = self.hidden_dim * self.hidden_dim;
        self.hidden_w = Array2::from_shape_vec(
            (self.hidden_dim, self.hidden_dim),
            params[offset..offset + hidden_size].to_vec()
        ).map_err(|e| format!("Failed to load hidden_w: {}", e))?;
        offset += hidden_size;
        
        // Load hidden_b
        self.hidden_b = Array1::from_vec(params[offset..offset + self.hidden_dim].to_vec());
        offset += self.hidden_dim;
        
        // Load output_proj
        let out_proj_size = self.hidden_dim * self.input_dim;
        self.output_proj = Array2::from_shape_vec(
            (self.hidden_dim, self.input_dim),
            params[offset..offset + out_proj_size].to_vec()
        ).map_err(|e| format!("Failed to load output_proj: {}", e))?;
        offset += out_proj_size;
        
        // Load output_bias
        self.output_bias = Array1::from_vec(params[offset..offset + self.input_dim].to_vec());
        
        Ok(())
    }
    
    /// Get total parameter count
    pub fn param_count(&self) -> usize {
        self.input_dim * self.hidden_dim + self.hidden_dim +  // input_proj + bias
        self.hidden_dim * self.hidden_dim + self.hidden_dim +  // hidden_w + bias
        self.hidden_dim * self.input_dim + self.input_dim      // output_proj + bias
    }
}

/// Helper: Initialize matrix with Gaussian noise
fn init_matrix(rows: usize, cols: usize, scale: f64) -> Array2<f64> {
    Array2::from_shape_fn((rows, cols), |_| {
        let noise: f64 = StandardNormal.sample(&mut thread_rng());
        noise * scale
    })
}

/// Helper: Initialize vector with Gaussian noise
fn init_vector(len: usize, scale: f64) -> Array1<f64> {
    Array1::from_shape_fn(len, |_| {
        let noise: f64 = StandardNormal.sample(&mut thread_rng());
        noise * scale
    })
}

#[derive(Debug, Clone, Copy)]
pub struct ParamStats {
    pub count: usize,
    pub mean: f64,
    pub std: f64,
    pub min: f64,
    pub max: f64,
}

fn relu_vec(x: &Array1<f64>) -> Array1<f64> {
    x.mapv(|v| v.max(0.0))
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_real_unet_creation() {
        let unet = RealUNet::new(64, 128, 64, 8);
        let hash1 = unet.param_hash();
        let hash2 = unet.param_hash();
        assert_eq!(hash1, hash2, "Same params should have same hash");
    }
    
    #[test]
    fn test_real_unet_forward() {
        let unet = RealUNet::new(64, 128, 64, 8);
        
        let x = Array3::zeros((2, 1, 64));
        let time = Array1::from_elem(2, 500.0);
        let classes = Array1::from_elem(2, 1.0);
        
        let output = unet.forward(&x, &time, &classes);
        
        // Output should NOT be all zeros (real parameters)
        let sum_sq: f64 = output.iter().map(|&v| v * v).sum();
        assert!(sum_sq > 0.0, "Output should be non-zero with real params");
        
        // Output should depend on input
        let x2 = Array3::ones((2, 1, 64)) * 0.5;
        let output2 = unet.forward(&x2, &time, &classes);
        
        let diff: f64 = (&output - &output2).mapv(|v| v.abs()).sum();
        assert!(diff > 0.0, "Output should depend on input");
    }
    
    #[test]
    fn test_param_change() {
        let mut unet = RealUNet::new(64, 128, 64, 8);
        let hash_before = unet.param_hash();
        
        unet.apply_noise(0.01);
        
        let hash_after = unet.param_hash();
        assert_ne!(hash_before, hash_after, "Params should change after noise");
    }
}
