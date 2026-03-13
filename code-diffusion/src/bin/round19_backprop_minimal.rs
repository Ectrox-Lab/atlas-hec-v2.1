//! Round 19: Minimal RealUNet Backprop Implementation
//!
//! Two-layer network with COMPLETE chain rule:
//! input → Linear → ReLU → Linear → output
//! Trainable: layer 1 | Frozen: layer 2

use ndarray::{Array1, Array2, Axis};
use rand::distributions::Distribution;
use rand::{Rng, SeedableRng};
use rand::rngs::StdRng;
use rand_distr::StandardNormal;
use serde_json::json;
use std::fs;

/// Minimal two-layer net with full backprop
struct MinimalBackpropNet {
    // Layer 1: trainable
    w1: Array2<f64>,
    b1: Array1<f64>,
    
    // Layer 2: frozen (no update)
    w2: Array2<f64>,
    b2: Array1<f64>,
    
    // Forward cache for backward
    cache_x: Option<Array2<f64>>,
    cache_z1: Option<Array2<f64>>,  // pre-activation
    cache_a1: Option<Array2<f64>>,  // post-ReLU
}

#[derive(Debug)]
struct Gradient {
    d_w1: Array2<f64>,
    d_b1: Array1<f64>,
    norm: f64,
}

impl MinimalBackpropNet {
    fn new(input_dim: usize, hidden_dim: usize, output_dim: usize, seed: u64) -> Self {
        let mut rng = StdRng::seed_from_u64(seed);
        
        let scale1 = (2.0 / (input_dim + hidden_dim) as f64).sqrt();
        let scale2 = (2.0 / (hidden_dim + output_dim) as f64).sqrt();
        
        Self {
            w1: Self::init_matrix(&mut rng, hidden_dim, input_dim, scale1),
            b1: Array1::zeros(hidden_dim),
            
            w2: Self::init_matrix(&mut rng, output_dim, hidden_dim, scale2),
            b2: Array1::zeros(output_dim),
            
            cache_x: None,
            cache_z1: None,
            cache_a1: None,
        }
    }
    
    fn init_matrix<R: rand::Rng>(rng: &mut R, rows: usize, cols: usize, scale: f64) -> Array2<f64> {
        Array2::from_shape_fn((rows, cols), |_| {
            let noise: f64 = StandardNormal.sample(rng);
            noise * scale
        })
    }
    
    /// Forward with caching
    fn forward(&mut self, x: &Array2<f64>) -> Array2<f64> {
        // Layer 1: z1 = x @ w1.T + b1
        let z1 = x.dot(&self.w1.t()) + &self.b1;
        
        // ReLU: a1 = max(z1, 0)
        let a1 = z1.mapv(|v| v.max(0.0));
        
        // Layer 2: y = a1 @ w2.T + b2
        let y = a1.dot(&self.w2.t()) + &self.b2;
        
        // Cache for backward
        self.cache_x = Some(x.clone());
        self.cache_z1 = Some(z1);
        self.cache_a1 = Some(a1);
        
        y
    }
    
    /// COMPLETE backward with chain rule
    fn backward(&self, grad_output: &Array2<f64>) -> Gradient {
        let x = self.cache_x.as_ref().expect("Forward first");
        let z1 = self.cache_z1.as_ref().expect("Forward first");
        let a1 = self.cache_a1.as_ref().expect("Forward first");
        
        // Step 1: Gradient from output to a1 (through layer 2)
        // dL/da1 = dL/dy @ w2
        let grad_a1 = grad_output.dot(&self.w2);
        
        // Step 2: ReLU derivative
        // dL/dz1 = dL/da1 * I(z1 > 0)
        let relu_deriv = z1.mapv(|v| if v > 0.0 { 1.0 } else { 0.0 });
        let grad_z1 = &grad_a1 * &relu_deriv;
        
        // Step 3: Gradient for layer 1 parameters
        // dL/dw1 = grad_z1.T @ x
        let d_w1 = grad_z1.t().dot(x);
        
        // dL/db1 = sum(grad_z1, axis=0)
        let d_b1 = grad_z1.sum_axis(Axis(0));
        
        let norm = (d_w1.mapv(|v| v * v).sum() + d_b1.mapv(|v| v * v).sum()).sqrt();
        
        Gradient { d_w1, d_b1, norm }
    }
    
    /// SGD update (layer 1 only)
    fn update(&mut self, grad: &Gradient, lr: f64) {
        self.w1 = &self.w1 - lr * &grad.d_w1;
        self.b1 = &self.b1 - lr * &grad.d_b1;
    }
    
    /// Get trainable hash
    fn trainable_hash(&self) -> u64 {
        let mut hash: u64 = 0xcbf29ce484222325;
        for &v in self.w1.iter().chain(self.b1.iter()) {
            hash ^= v.to_bits();
            hash = hash.wrapping_mul(0x100000001b3);
        }
        hash
    }
    
    /// Get frozen hash
    fn frozen_hash(&self) -> u64 {
        let mut hash: u64 = 0xcbf29ce484222325;
        for &v in self.w2.iter().chain(self.b2.iter()) {
            hash ^= v.to_bits();
            hash = hash.wrapping_mul(0x100000001b3);
        }
        hash
    }
}

fn mse(pred: &Array2<f64>, target: &Array2<f64>) -> f64 {
    let diff = pred - target;
    diff.mapv(|v| v * v).mean().unwrap()
}

fn generate_data(n: usize, input_dim: usize, output_dim: usize, seed: u64) -> (Array2<f64>, Array2<f64>) {
    let mut rng = StdRng::seed_from_u64(seed);
    
    let x: Array2<f64> = Array2::from_shape_fn((n, input_dim), |_| {
        rng.gen::<f64>() * 2.0 - 1.0
    });
    
    // Target: simple linear transform (identity with small noise)
    let mut y = Array2::zeros((n, output_dim));
    for i in 0..n.min(output_dim) {
        let noise: f64 = StandardNormal.sample(&mut rng);
        y[[i, i]] = x[[i, 0]] + noise * 0.05;
    }
    
    (x, y)
}

fn main() {
    println!("╔══════════════════════════════════════════════════════════╗");
    println!("║  Round 19: Minimal Backprop Implementation              ║");
    println!("║  Trainable: Layer 1  |  Frozen: Layer 2                 ║");
    println!("╚══════════════════════════════════════════════════════════╝");
    println!();
    
    // Config
    let epochs = 200;
    let lr = 0.05;
    let batch_size = 32;
    let input_dim = 16;
    let hidden_dim = 32;
    let output_dim = 8;
    
    // Create models
    let mut model = MinimalBackpropNet::new(input_dim, hidden_dim, output_dim, 42);
    let frozen_baseline = MinimalBackpropNet::new(input_dim, hidden_dim, output_dim, 42);
    
    let initial_trainable_hash = model.trainable_hash();
    let initial_frozen_hash = model.frozen_hash();
    
    println!("Configuration:");
    println!("  Architecture: {} → {} → {}", input_dim, hidden_dim, output_dim);
    println!("  Trainable: w1, b1 ({} params)", input_dim * hidden_dim + hidden_dim);
    println!("  Frozen: w2, b2 ({} params)", hidden_dim * output_dim + output_dim);
    println!("  Epochs: {}, LR: {}", epochs, lr);
    println!();
    
    // Training
    let mut losses = vec![];
    let mut grad_norms = vec![];
    
    println!("Training...");
    
    for epoch in 0..epochs {
        let (x, y_target) = generate_data(batch_size, input_dim, output_dim, 1000 + epoch as u64);
        
        // Forward
        let y_pred = model.forward(&x);
        
        // Loss
        let loss = mse(&y_pred, &y_target);
        losses.push(loss);
        
        // Backward
        let grad_output = 2.0 * (&y_pred - &y_target) / (batch_size * output_dim) as f64;
        let grad = model.backward(&grad_output);
        grad_norms.push(grad.norm);
        
        // Update
        model.update(&grad, lr);
        
        if epoch % 40 == 0 {
            println!("  Epoch {:3}: loss={:.6}, |grad|={:.6}", epoch, loss, grad.norm);
        }
    }
    
    let final_trainable_hash = model.trainable_hash();
    let final_frozen_hash = model.frozen_hash();
    
    println!();
    
    // === VERIFICATION ===
    println!("═══════════════════════════════════════════════════════════");
    println!("VERIFICATION");
    println!("═══════════════════════════════════════════════════════════");
    println!();
    
    // 1. Loss curve
    let loss_0 = losses[0];
    let loss_mid = losses[epochs / 2];
    let loss_final = losses[epochs - 1];
    let loss_reduction = (loss_0 - loss_final) / loss_0 * 100.0;
    let loss_decreasing = loss_0 > loss_mid && loss_mid > loss_final;
    
    println!("1. Loss Curve:");
    println!("   Initial:  {:.6}", loss_0);
    println!("   Middle:   {:.6}", loss_mid);
    println!("   Final:    {:.6}", loss_final);
    println!("   Reduction: {:.1}%", loss_reduction);
    println!("   Status: {}", if loss_reduction > 50.0 { "✅ PASS (>50%)" } else { "❌ FAIL" });
    println!();
    
    // 2. Gradient evidence
    let avg_grad: f64 = grad_norms.iter().sum::<f64>() / grad_norms.len() as f64;
    let gradient_active = avg_grad > 0.01;
    
    println!("2. Gradient Evidence:");
    println!("   Avg |grad|: {:.6}", avg_grad);
    println!("   Status: {}", if gradient_active { "✅ PASS" } else { "❌ FAIL" });
    println!();
    
    // 3. Frozen layers unchanged
    let frozen_unchanged = initial_frozen_hash == final_frozen_hash;
    
    println!("3. Frozen Layers (w2, b2):");
    println!("   Initial hash: {:016x}", initial_frozen_hash);
    println!("   Final hash:   {:016x}", final_frozen_hash);
    println!("   Status: {}", if frozen_unchanged { "✅ UNCHANGED" } else { "❌ MODIFIED" });
    println!();
    
    // 4. Trainable layer changed
    let trainable_changed = initial_trainable_hash != final_trainable_hash;
    
    println!("4. Trainable Layers (w1, b1):");
    println!("   Initial hash: {:016x}", initial_trainable_hash);
    println!("   Final hash:   {:016x}", final_trainable_hash);
    println!("   Status: {}", if trainable_changed { "✅ CHANGED" } else { "❌ UNCHANGED" });
    println!();
    
    // 5. Reload determinism
    let mut model2 = MinimalBackpropNet::new(input_dim, hidden_dim, output_dim, 42);
    for epoch in 0..epochs {
        let (x, y_target) = generate_data(batch_size, input_dim, output_dim, 1000 + epoch as u64);
        let y_pred = model2.forward(&x);
        let grad_output = 2.0 * (&y_pred - &y_target) / (batch_size * output_dim) as f64;
        let grad = model2.backward(&grad_output);
        model2.update(&grad, lr);
    }
    let reload_match = model.trainable_hash() == model2.trainable_hash();
    
    println!("5. Reload Determinism:");
    println!("   Status: {}", if reload_match { "✅ PASS" } else { "❌ FAIL" });
    println!();
    
    // Overall
    let all_pass = loss_reduction > 50.0 
        && gradient_active 
        && frozen_unchanged 
        && trainable_changed 
        && reload_match;
    
    println!("═══════════════════════════════════════════════════════════");
    if all_pass {
        println!("🎉 ROUND 19: PASS");
        println!("   Complete backprop with gradient-connected learning!");
    } else {
        println!("❌ ROUND 19: FAIL");
        println!("   Backprop needs debugging.");
    }
    println!("═══════════════════════════════════════════════════════════");
    
    // Save report
    let report = json!({
        "round": 19,
        "status": if all_pass { "PASS" } else { "FAIL" },
        "config": {
            "input_dim": input_dim,
            "hidden_dim": hidden_dim,
            "output_dim": output_dim,
            "epochs": epochs,
            "learning_rate": lr,
            "batch_size": batch_size
        },
        "results": {
            "loss_initial": loss_0,
            "loss_final": loss_final,
            "loss_reduction_pct": loss_reduction,
            "loss_decreasing": loss_decreasing,
            "gradient_norm_avg": avg_grad,
            "gradient_active": gradient_active,
            "frozen_unchanged": frozen_unchanged,
            "trainable_changed": trainable_changed,
            "reload_deterministic": reload_match
        }
    });
    
    fs::create_dir_all("tests").unwrap_or_default();
    fs::write("tests/round19_report.json", serde_json::to_string_pretty(&report).unwrap()).unwrap();
    
    println!("\nReport: tests/round19_report.json");
    
    std::process::exit(if all_pass { 0 } else { 1 });
}
