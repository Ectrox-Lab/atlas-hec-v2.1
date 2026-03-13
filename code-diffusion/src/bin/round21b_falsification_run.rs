//! Round 21b: Bounded Falsification Run
//!
//! Purpose: Test if training insufficiency is the bottleneck
//! Max: 1000 epochs, 2 hours
//! Stop rules predefined - no scope creep

use code_diffusion::models::realunet_conditional::RealUNetConditional;
use ndarray::Array3;
use rand::distributions::Distribution;
use rand::{Rng, SeedableRng};
use rand::rngs::StdRng;
use rand_distr::StandardNormal;
use serde_json::json;
use std::fs;
use std::time::{Instant, Duration};

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
    
    fn q_sample(&self, x0: &Array3<f64>, t: usize, noise: &Array3<f64>) -> Array3<f64> {
        let sqrt_alpha = self.alphas_cumprod[t].sqrt();
        let sqrt_one_minus = (1.0 - self.alphas_cumprod[t]).sqrt();
        x0 * sqrt_alpha + noise * sqrt_one_minus
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
    let start_time = Instant::now();
    let max_duration = Duration::from_secs(7200); // 2 hours max
    
    println!("╔══════════════════════════════════════════════════════════╗");
    println!("║  Round 21b: Bounded Falsification Run                   ║");
    println!("║  Purpose: Test if training insufficiency is bottleneck  ║");
    println!("╚══════════════════════════════════════════════════════════╝");
    println!();
    println!("STOP RULES (predefined - no scope creep):");
    println!("  1. Max epochs: 1000");
    println!("  2. Max time: 2 hours");
    println!("  3. If noise_loss_improvement < 10% at epoch 500 → STOP, document");
    println!("  4. If noise_loss > 20% BUT denoise_proxy < 0.005 → STOP, transfer weak");
    println!("  5. Only continue beyond 1000 if BOTH metrics improve");
    println!();
    
    // Config
    let max_epochs = 1000;
    let batch_size = 32;
    let dim = 64;
    let hidden_dim = 128;
    let time_embed_dim = 32;
    let timesteps = 100;
    let lr = 0.005;
    
    let mut unet = RealUNetConditional::new(dim, hidden_dim, time_embed_dim, 42);
    let diffusion = DiffusionProcess::new(timesteps);
    let mut rng = StdRng::seed_from_u64(123);
    
    let _initial_hash = unet.param_hash();
    let mut loss_0: f64 = 0.0;
    
    // Training
    let mut noise_losses: Vec<f64> = vec![];
    let mut denoise_proxies: Vec<f64> = vec![];
    
    println!("Training (max {} epochs, 2 hours)...", max_epochs);
    
    let mut epoch = 0;
    while epoch < max_epochs {
        // Time check
        if start_time.elapsed() > max_duration {
            println!("  TIME LIMIT REACHED at epoch {}", epoch);
            break;
        }
        
        // Training step
        let x0 = generate_clean_data(batch_size, dim, epoch as u64 * 1000);
        let t = rng.gen_range(0..timesteps);
        let noise: Array3<f64> = Array3::from_shape_fn((batch_size, 1, dim), |_| {
            StandardNormal.sample(&mut rng)
        });
        let x_t = diffusion.q_sample(&x0, t, &noise);
        let noise_pred = unet.forward(&x_t, t, timesteps);
        let loss = mse(&noise_pred, &noise);
        noise_losses.push(loss);
        
        if epoch == 0 { loss_0 = loss; }
        
        // Denoise proxy: how close is (x_t - predicted_noise) to x0?
        let x0_estimated = &x_t - &noise_pred;
        let denoise_quality = -mse(&x0_estimated, &x0); // negative MSE (higher is better)
        denoise_proxies.push(denoise_quality);
        
        // Backward
        let grad_output = (&noise_pred - &noise) * (2.0 / (batch_size * dim) as f64);
        let grad = unet.backward(&grad_output);
        unet.update(&grad, lr);
        
        // Progress log
        if epoch % 100 == 99 {
            let recent_loss: f64 = noise_losses[epoch-99..=epoch].iter().sum::<f64>() / 100.0;
            let recent_proxy: f64 = denoise_proxies[epoch-99..=epoch].iter().sum::<f64>() / 100.0;
            let loss_improvement = (loss_0 - recent_loss) / loss_0 * 100.0;
            println!("  Epoch {}: loss={:.6} ({:.1}% ↓), proxy={:.6}, |grad|={:.6}", 
                epoch + 1, recent_loss, loss_improvement, recent_proxy, grad.total_norm);
        }
        
        // STOP RULE 3: Check at epoch 500
        if epoch == 499 {
            let loss_500: f64 = noise_losses[400..500].iter().sum::<f64>() / 100.0;
            let improvement_500 = (loss_0 - loss_500) / loss_0 * 100.0;
            if improvement_500 < 10.0 {
                println!("\n  ⚠️  STOP RULE 3 TRIGGERED at epoch 500");
                println!("      Loss improvement: {:.1}% < 10%", improvement_500);
                println!("      Conclusion: Training insufficiency is NOT the main bottleneck");
                break;
            }
        }
        
        // STOP RULE 4: Check transfer at epoch 800
        if epoch == 799 {
            let loss_800: f64 = noise_losses[700..800].iter().sum::<f64>() / 100.0;
            let proxy_800: f64 = denoise_proxies[700..800].iter().sum::<f64>() / 100.0;
            let proxy_200: f64 = denoise_proxies[100..200].iter().sum::<f64>() / 100.0;
            let improvement_800 = (loss_0 - loss_800) / loss_0 * 100.0;
            let proxy_gain = proxy_800 - proxy_200;
            
            if improvement_800 > 20.0 && proxy_gain < 0.005 {
                println!("\n  ⚠️  STOP RULE 4 TRIGGERED at epoch 800");
                println!("      Loss improvement: {:.1}% > 20%", improvement_800);
                println!("      Proxy gain: {:.6} < 0.005", proxy_gain);
                println!("      Conclusion: Objective-to-output transfer is WEAK");
                break;
            }
        }
        
        epoch += 1;
    }
    
    let _final_hash = unet.param_hash();
    let actual_epochs = epoch + 1;
    
    // Results
    let loss_final: f64 = noise_losses[noise_losses.len()-100..].iter().sum::<f64>() / 100.0;
    let loss_improvement = (loss_0 - loss_final) / loss_0 * 100.0;
    let proxy_final: f64 = denoise_proxies[denoise_proxies.len()-100..].iter().sum::<f64>() / 100.0;
    let proxy_initial: f64 = denoise_proxies[0..100].iter().sum::<f64>() / 100.0;
    let proxy_gain = proxy_final - proxy_initial;
    
    println!();
    println!("═══════════════════════════════════════════════════════════");
    println!("ROUND 21b RESULTS");
    println!("═══════════════════════════════════════════════════════════");
    println!();
    println!("Execution:");
    println!("  Epochs completed: {}/{}", actual_epochs, max_epochs);
    println!("  Time elapsed: {:.1} minutes", start_time.elapsed().as_secs_f64() / 60.0);
    println!();
    println!("Metrics:");
    println!("  Noise loss improvement: {:.1}%", loss_improvement);
    println!("  Denoise proxy gain: {:.6}", proxy_gain);
    println!();
    
    // Verdict
    let verdict = if loss_improvement > 30.0 && proxy_gain > 0.01 {
        "TRAINING_INSUFFICIENCY_CONFIRMED"
    } else if loss_improvement < 10.0 {
        "ARCHITECTURE_LIMITATION"
    } else if loss_improvement > 20.0 && proxy_gain < 0.005 {
        "TRANSFER_WEAKNESS"
    } else {
        "AMBIGUOUS"
    };
    
    println!("Verdict: {}", match verdict {
        "TRAINING_INSUFFICIENCY_CONFIRMED" => "🎉 Training was the bottleneck - extend further",
        "ARCHITECTURE_LIMITATION" => "⚠️  Architecture/task definition needs revision",
        "TRANSFER_WEAKNESS" => "⚠️  Objective-to-output transfer weak",
        _ => "❓ Results ambiguous - needs more analysis"
    });
    println!();
    
    // Save report
    let report = json!({
        "round": "21b",
        "purpose": "bounded_falsification",
        "verdict": verdict,
        "execution": {
            "epochs_completed": actual_epochs,
            "max_epochs": max_epochs,
            "time_minutes": start_time.elapsed().as_secs_f64() / 60.0
        },
        "results": {
            "noise_loss_initial": loss_0,
            "noise_loss_final": loss_final,
            "noise_loss_improvement_pct": loss_improvement,
            "denoise_proxy_initial": proxy_initial,
            "denoise_proxy_final": proxy_final,
            "denoise_proxy_gain": proxy_gain
        },
        "interpretation": match verdict {
            "TRAINING_INSUFFICIENCY_CONFIRMED" => "More training helps - consider 5000+ epochs",
            "ARCHITECTURE_LIMITATION" => "Current architecture insufficient for task",
            "TRANSFER_WEAKNESS" => "Task alignment needs architectural revision",
            _ => "Unclear - manual review needed"
        }
    });
    
    fs::create_dir_all("tests").unwrap_or_default();
    fs::write("tests/round21b_falsification_report.json", 
        serde_json::to_string_pretty(&report).unwrap()).unwrap();
    
    println!("Report: tests/round21b_falsification_report.json");
}
