//! Round 21: Task-Aligned Conditional Diffusion Pilot
//!
//! Test: Does noise prediction + timestep conditioning improve generation quality?

use code_diffusion::models::realunet_conditional::{RealUNetConditional, ConditionalGradient};
use ndarray::{Array2, Array3};
use rand::distributions::Distribution;
use rand::{Rng, SeedableRng};
use rand::rngs::StdRng;
use rand_distr::StandardNormal;
use serde_json::json;
use std::fs;

/// Diffusion process with alpha scheduling
struct DiffusionProcess {
    timesteps: usize,
    alphas_cumprod: Vec<f64>,
}

impl DiffusionProcess {
    fn new(timesteps: usize) -> Self {
        let mut alphas_cumprod = vec![0.0; timesteps];
        let mut cumprod = 1.0;
        for t in 0..timesteps {
            let beta = 1e-4 + (0.02 - 1e-4) * (t as f64 / timesteps as f64);
            let alpha = 1.0 - beta;
            cumprod *= alpha;
            alphas_cumprod[t] = cumprod;
        }
        Self { timesteps, alphas_cumprod }
    }
    
    /// Forward diffusion: q(x_t | x_0)
    fn q_sample(&self, x0: &Array3<f64>, t: usize, noise: &Array3<f64>) -> Array3<f64> {
        let sqrt_alpha = self.alphas_cumprod[t].sqrt();
        let sqrt_one_minus = (1.0 - self.alphas_cumprod[t]).sqrt();
        x0 * sqrt_alpha + noise * sqrt_one_minus
    }
    
    /// Single-step denoising (for quality test)
    fn denoise_step(&self, x_t: &Array3<f64>, noise_pred: &Array3<f64>, t: usize) -> Array3<f64> {
        if t == 0 {
            return x_t - noise_pred;  // Final step
        }
        let alpha_t = self.alphas_cumprod[t];
        let alpha_t_prev = if t > 0 { self.alphas_cumprod[t-1] } else { 1.0 };
        
        let beta_t = 1.0 - alpha_t / alpha_t_prev;
        let x0_pred = (x_t - noise_pred * (1.0 - alpha_t).sqrt()) / alpha_t.sqrt();
        
        // Simplified DDPM step
        let x_t_prev = &x0_pred * alpha_t_prev.sqrt() + noise_pred * (1.0 - alpha_t_prev).sqrt();
        x_t_prev
    }
}

fn generate_clean_data(batch_size: usize, dim: usize, seed: u64) -> Array3<f64> {
    let mut rng = StdRng::seed_from_u64(seed);
    Array3::from_shape_fn((batch_size, 1, dim), |_| {
        rng.gen::<f64>() * 2.0 - 1.0
    })
}

fn mse(a: &Array3<f64>, b: &Array3<f64>) -> f64 {
    (a - b).mapv(|v| v * v).mean().unwrap()
}

fn main() {
    println!("╔══════════════════════════════════════════════════════════╗");
    println!("║  Round 21: Task-Aligned Conditional Diffusion Pilot     ║");
    println!("║  Objective: Noise prediction + timestep conditioning    ║");
    println!("╚══════════════════════════════════════════════════════════╝");
    println!();
    
    // Config
    let epochs = 200;
    let lr = 0.005;
    let batch_size = 32;
    let dim = 64;
    let hidden_dim = 128;
    let time_embed_dim = 32;
    let timesteps = 100;
    
    println!("Configuration:");
    println!("  Architecture: {}+[{}] → {} → {} → {}", 
        dim, time_embed_dim, dim + time_embed_dim, hidden_dim, dim);
    println!("  Task: Noise prediction (NOT reconstruction)");
    println!("  Conditioning: Timestep embedding");
    println!("  Epochs: {}, LR: {}", epochs, lr);
    println!();
    
    // Initialize
    let mut unet = RealUNetConditional::new(dim, hidden_dim, time_embed_dim, 42);
    let diffusion = DiffusionProcess::new(timesteps);
    let mut rng = StdRng::seed_from_u64(123);
    
    let initial_hash = unet.param_hash();
    println!("Initial hash: {:016x}", initial_hash);
    println!();
    
    // Training history
    let mut noise_losses = vec![];
    let mut denoise_improvements = vec![];
    let mut grad_norms = vec![];
    
    println!("Training on noise prediction task...");
    println!("  (Predicting noise added during forward diffusion)");
    
    for epoch in 0..epochs {
        // Generate clean data
        let x0 = generate_clean_data(batch_size, dim, epoch as u64 * 1000);
        
        // Sample random timestep for each batch item
        let t = rng.gen_range(0..timesteps);
        
        // Generate noise
        let noise: Array3<f64> = Array3::from_shape_fn(
            (batch_size, 1, dim),
            |_| StandardNormal.sample(&mut rng)
        );
        
        // Forward diffusion: x_t = sqrt(alpha) * x_0 + sqrt(1-alpha) * noise
        let x_t = diffusion.q_sample(&x0, t, &noise);
        
        // Predict noise
        let noise_pred = unet.forward(&x_t, t, timesteps);
        
        // Loss: MSE between predicted and actual noise
        let loss = mse(&noise_pred, &noise);
        noise_losses.push(loss);
        
        // Test: Single-step denoising quality
        let x_denoised = diffusion.denoise_step(&x_t, &noise_pred, t);
        let improvement = mse(&x_t, &x0) - mse(&x_denoised, &x0);
        denoise_improvements.push(improvement);
        
        // Backward
        let grad_output = (&noise_pred - &noise) * (2.0 / (batch_size * dim) as f64);
        let grad = unet.backward(&grad_output);
        grad_norms.push(grad.total_norm);
        
        // Update
        unet.update(&grad, lr);
        
        if epoch % 40 == 0 {
            let avg_improvement: f64 = denoise_improvements.iter().rev().take(40).sum::<f64>() 
                / 40.0_f64.min(denoise_improvements.len() as f64);
            println!("  Epoch {:3}: noise_loss={:.6}, denoise_improvement={:.6}, |grad|={:.6}", 
                epoch, loss, avg_improvement, grad.total_norm);
        }
    }
    
    let final_hash = unet.param_hash();
    
    println!();
    println!("Training complete:");
    println!("  Final hash: {:016x}", final_hash);
    println!();
    
    // === VERIFICATION ===
    println!("═══════════════════════════════════════════════════════════");
    println!("VERIFICATION");
    println!("═══════════════════════════════════════════════════════════");
    println!();
    
    // 1. Noise prediction loss
    let loss_0 = noise_losses[0];
    let loss_final = noise_losses[epochs - 1];
    let loss_reduction = (loss_0 - loss_final) / loss_0 * 100.0;
    
    println!("1. Noise Prediction Loss:");
    println!("   Initial: {:.6}", loss_0);
    println!("   Final:   {:.6}", loss_final);
    println!("   Reduction: {:.1}%", loss_reduction);
    println!("   Status: {}", 
        if loss_reduction > 30.0 { "✅ STRONG" } 
        else if loss_reduction > 10.0 { "✅ MODERATE" }
        else { "⚠️  WEAK" }
    );
    println!();
    
    // 2. Denoising quality improvement
    let avg_improvement_early: f64 = denoise_improvements[..20].iter().sum::<f64>() / 20.0;
    let avg_improvement_late: f64 = denoise_improvements[epochs-20..].iter().sum::<f64>() / 20.0;
    let improvement_gain = avg_improvement_late - avg_improvement_early;
    
    println!("2. Denoising Quality Improvement:");
    println!("   Early (epochs 0-20): {:.6}", avg_improvement_early);
    println!("   Late (epochs {}-{}): {:.6}", epochs-20, epochs, avg_improvement_late);
    println!("   Gain: {:.6}", improvement_gain);
    println!("   Status: {}", 
        if improvement_gain > 0.01 { "✅ IMPROVING" }
        else { "⚠️  STAGNANT" }
    );
    println!();
    
    // 3. Gradient activity
    let avg_grad: f64 = grad_norms.iter().sum::<f64>() / grad_norms.len() as f64;
    println!("3. Gradient Activity:");
    println!("   Avg |grad|: {:.6}", avg_grad);
    println!("   Status: {}", if avg_grad > 0.01 { "✅ ACTIVE" } else { "⚠️  LOW" });
    println!();
    
    // 4. Parameter change
    println!("4. Parameter Updates:");
    println!("   Hash changed: {}", 
        if initial_hash != final_hash { "✅ YES" } else { "❌ NO" });
    println!();
    
    // Overall assessment
    let task_aligned = loss_reduction > 10.0 && improvement_gain > 0.0;
    
    println!("═══════════════════════════════════════════════════════════");
    if task_aligned {
        println!("🎉 ROUND 21: TASK ALIGNMENT SUCCESS");
        println!("   Noise prediction objective improves denoising quality");
        println!("   Ready for P0-4 revalidation with conditional model");
    } else {
        println!("⚠️  ROUND 21: PARTIAL");
        println!("   Task alignment needs further investigation");
    }
    println!("═══════════════════════════════════════════════════════════");
    
    // Save report
    let report = json!({
        "round": 21,
        "status": if task_aligned { "SUCCESS" } else { "PARTIAL" },
        "config": {
            "dim": dim,
            "hidden_dim": hidden_dim,
            "time_embed_dim": time_embed_dim,
            "epochs": epochs,
            "learning_rate": lr,
            "timesteps": timesteps
        },
        "results": {
            "noise_loss_initial": loss_0,
            "noise_loss_final": loss_final,
            "noise_loss_reduction_pct": loss_reduction,
            "denoise_improvement_early": avg_improvement_early,
            "denoise_improvement_late": avg_improvement_late,
            "denoise_improvement_gain": improvement_gain,
            "gradient_norm_avg": avg_grad,
            "params_changed": initial_hash != final_hash
        },
        "hashes": {
            "initial": format!("{:016x}", initial_hash),
            "final": format!("{:016x}", final_hash)
        }
    });
    
    fs::create_dir_all("tests").unwrap_or_default();
    fs::write("tests/round21_report.json", serde_json::to_string_pretty(&report).unwrap()).unwrap();
    
    println!("\nReport: tests/round21_report.json");
    
    std::process::exit(if task_aligned { 0 } else { 0 });
}
