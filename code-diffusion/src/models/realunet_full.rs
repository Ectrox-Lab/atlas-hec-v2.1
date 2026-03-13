//! Round 20: RealUNet with Full Gradient Support
//!
//! Complete 4-layer network with backpropagation:
//! input → Linear → ReLU → Linear → ReLU → Linear → output

use ndarray::{Array1, Array2, Array3, Axis};
use rand::distributions::Distribution;
use rand::SeedableRng;
use rand::rngs::StdRng;
use rand_distr::StandardNormal;

/// RealUNet with full gradient tracking (all layers trainable)
pub struct RealUNetFull {
    // Layer 1: input → hidden
    pub w1: Array2<f64>,
    pub b1: Array1<f64>,
    
    // Layer 2: hidden → hidden
    pub w2: Array2<f64>,
    pub b2: Array1<f64>,
    
    // Layer 3: hidden → output
    pub w3: Array2<f64>,
    pub b3: Array1<f64>,
    
    // Dimensions
    input_dim: usize,
    hidden_dim: usize,
    output_dim: usize,
    
    // Forward cache for backward
    cache_x: Option<Array2<f64>>,
    cache_z1: Option<Array2<f64>>,  // pre-activation layer 1
    cache_a1: Option<Array2<f64>>,  // post-ReLU layer 1
    cache_z2: Option<Array2<f64>>,  // pre-activation layer 2
    cache_a2: Option<Array2<f64>>,  // post-ReLU layer 2
}

/// Full gradient for all layers
#[derive(Debug, Clone)]
pub struct FullGradient {
    pub d_w1: Array2<f64>,
    pub d_b1: Array1<f64>,
    pub d_w2: Array2<f64>,
    pub d_b2: Array1<f64>,
    pub d_w3: Array2<f64>,
    pub d_b3: Array1<f64>,
    pub total_norm: f64,
}

impl RealUNetFull {
    pub fn new(input_dim: usize, hidden_dim: usize, output_dim: usize, seed: u64) -> Self {
        let mut rng = StdRng::seed_from_u64(seed);
        
        let scale1 = (2.0 / (input_dim + hidden_dim) as f64).sqrt();
        let scale2 = (2.0 / (hidden_dim + hidden_dim) as f64).sqrt();
        let scale3 = (2.0 / (hidden_dim + output_dim) as f64).sqrt();
        
        Self {
            w1: Self::init_matrix(&mut rng, hidden_dim, input_dim, scale1),
            b1: Array1::zeros(hidden_dim),
            
            w2: Self::init_matrix(&mut rng, hidden_dim, hidden_dim, scale2),
            b2: Array1::zeros(hidden_dim),
            
            w3: Self::init_matrix(&mut rng, output_dim, hidden_dim, scale3),
            b3: Array1::zeros(output_dim),
            
            input_dim,
            hidden_dim,
            output_dim,
            
            cache_x: None,
            cache_z1: None,
            cache_a1: None,
            cache_z2: None,
            cache_a2: None,
        }
    }
    
    fn init_matrix<R: rand::Rng>(rng: &mut R, rows: usize, cols: usize, scale: f64) -> Array2<f64> {
        Array2::from_shape_fn((rows, cols), |_| {
            let noise: f64 = StandardNormal.sample(rng);
            noise * scale
        })
    }
    
    /// Forward pass for 3D tensor (batch, channel, seq)
    pub fn forward(&mut self, x: &Array3<f64>) -> Array3<f64> {
        let batch_size = x.shape()[0];
        let mut output = Array3::zeros((batch_size, 1, self.output_dim));
        
        // Flatten batch for matrix ops
        let x_flat: Array2<f64> = Array2::from_shape_fn(
            (batch_size, self.input_dim),
            |(i, j)| x[[i, 0, j]]
        );
        
        // Layer 1
        let z1 = x_flat.dot(&self.w1.t()) + &self.b1;
        let a1 = relu(&z1);
        
        // Layer 2
        let z2 = a1.dot(&self.w2.t()) + &self.b2;
        let a2 = relu(&z2);
        
        // Layer 3 (output)
        let y = a2.dot(&self.w3.t()) + &self.b3;
        
        // Store in output
        for b in 0..batch_size {
            for j in 0..self.output_dim {
                output[[b, 0, j]] = y[[b, j]];
            }
        }
        
        // Cache for backward
        self.cache_x = Some(x_flat);
        self.cache_z1 = Some(z1);
        self.cache_a1 = Some(a1);
        self.cache_z2 = Some(z2);
        self.cache_a2 = Some(a2);
        
        output
    }
    
    /// COMPLETE backward pass with chain rule through all layers
    pub fn backward(&self, grad_output_3d: &Array3<f64>) -> FullGradient {
        let batch_size = grad_output_3d.shape()[0];
        
        // Convert 3D gradient to 2D
        let grad_output: Array2<f64> = Array2::from_shape_fn(
            (batch_size, self.output_dim),
            |(i, j)| grad_output_3d[[i, 0, j]]
        );
        
        // Retrieve cached values
        let x = self.cache_x.as_ref().expect("Forward first");
        let z1 = self.cache_z1.as_ref().expect("Forward first");
        let a1 = self.cache_a1.as_ref().expect("Forward first");
        let z2 = self.cache_z2.as_ref().expect("Forward first");
        let a2 = self.cache_a2.as_ref().expect("Forward first");
        
        // ===== LAYER 3 (Output) =====
        // Forward: y = a2 @ w3.T + b3
        // dL/dw3 = grad_output.T @ a2  [w3 shape: (output_dim, hidden_dim)]
        let d_w3 = grad_output.t().dot(a2);
        let d_b3 = grad_output.sum_axis(Axis(0));
        
        // Backprop to layer 2: dL/da2 = grad_output @ w3
        let grad_a2 = grad_output.dot(&self.w3);
        
        // ===== LAYER 2 =====
        // ReLU derivative
        let relu_deriv_z2 = z2.mapv(|v| if v > 0.0 { 1.0 } else { 0.0 });
        let grad_z2 = &grad_a2 * &relu_deriv_z2;
        
        // dL/dw2 = a1.T @ grad_z2
        let d_w2 = a1.t().dot(&grad_z2);
        let d_b2 = grad_z2.sum_axis(Axis(0));
        
        // Backprop to layer 1: dL/da1 = grad_z2 @ w2
        let grad_a1 = grad_z2.dot(&self.w2);
        
        // ===== LAYER 1 =====
        // ReLU derivative
        let relu_deriv_z1 = z1.mapv(|v| if v > 0.0 { 1.0 } else { 0.0 });
        let grad_z1 = &grad_a1 * &relu_deriv_z1;
        
        // dL/dw1 = grad_z1.T @ x  [w1 shape: (hidden_dim, input_dim)]
        let d_w1 = grad_z1.t().dot(x);
        let d_b1 = grad_z1.sum_axis(Axis(0));
        
        // Total gradient norm
        let total_norm = (
            d_w1.mapv(|v| v * v).sum() +
            d_b1.mapv(|v| v * v).sum() +
            d_w2.mapv(|v| v * v).sum() +
            d_b2.mapv(|v| v * v).sum() +
            d_w3.mapv(|v| v * v).sum() +
            d_b3.mapv(|v| v * v).sum()
        ).sqrt();
        
        FullGradient {
            d_w1, d_b1, d_w2, d_b2, d_w3, d_b3, total_norm
        }
    }
    
    /// SGD update for all layers
    pub fn update(&mut self, grad: &FullGradient, lr: f64) {
        self.w1 = &self.w1 - lr * &grad.d_w1;
        self.b1 = &self.b1 - lr * &grad.d_b1;
        self.w2 = &self.w2 - lr * &grad.d_w2;
        self.b2 = &self.b2 - lr * &grad.d_b2;
        self.w3 = &self.w3 - lr * &grad.d_w3;
        self.b3 = &self.b3 - lr * &grad.d_b3;
    }
    
    /// Get full parameter hash
    pub fn param_hash(&self) -> u64 {
        let mut hash: u64 = 0xcbf29ce484222325;
        
        for &v in self.w1.iter().chain(self.b1.iter())
            .chain(self.w2.iter()).chain(self.b2.iter())
            .chain(self.w3.iter()).chain(self.b3.iter()) {
            hash ^= v.to_bits();
            hash = hash.wrapping_mul(0x100000001b3);
        }
        
        hash
    }
    
    /// Get parameter count
    pub fn param_count(&self) -> usize {
        self.w1.len() + self.b1.len() +
        self.w2.len() + self.b2.len() +
        self.w3.len() + self.b3.len()
    }
}

fn relu(x: &Array2<f64>) -> Array2<f64> {
    x.mapv(|v| v.max(0.0))
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_forward_backward() {
        let mut net = RealUNetFull::new(16, 32, 8, 42);
        
        let x = Array3::from_shape_fn((4, 1, 16), |_| 0.5);
        let y = net.forward(&x);
        
        assert_eq!(y.shape(), &[4, 1, 8]);
        
        // Backward
        let grad_output = Array3::from_shape_fn((4, 1, 8), |_| 0.1);
        let grad = net.backward(&grad_output);
        
        assert!(grad.total_norm > 0.0);
    }
    
    #[test]
    fn test_param_change() {
        let mut net = RealUNetFull::new(16, 32, 8, 42);
        let hash_before = net.param_hash();
        
        // One update step
        let x = Array3::from_shape_fn((4, 1, 16), |_| 0.5);
        let _ = net.forward(&x);
        
        let grad_output = Array3::from_shape_fn((4, 1, 8), |_| 0.1);
        let grad = net.backward(&grad_output);
        net.update(&grad, 0.01);
        
        let hash_after = net.param_hash();
        assert_ne!(hash_before, hash_after);
    }
}
