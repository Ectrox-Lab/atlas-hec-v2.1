//! P0-5 Final Validation: Extended training with optimal hyperparameters
//!
//! Based on sweep results:
//! - Best config: LR=0.01, Steps=3000, Dim=512 → 4.67% improvement
//! - Target: >5% improvement with 3/3 seeds positive
//! - Extended config: LR=0.01, Steps=5000, Dim=512

use code_diffusion::models::realunet_full::RealUNetFull;
use code_diffusion::diffusion::{Diffusion, DiffusionConfig};
use ndarray::Array3;
use rand::{SeedableRng, Rng};
use rand::rngs::StdRng;
use rand_distr::{Distribution, StandardNormal};
use serde::{Deserialize, Serialize};
use std::fs;

const SEEDS: [u64; 3] = [42, 123, 999];
const LEARNING_RATE: f64 = 0.01;
const WARMUP_STEPS: usize = 100;
const TRAIN_STEPS: usize = 7500;  // Extended further to reach >5%
const BATCH_SIZE: usize = 8;
const INPUT_DIM: usize = 512;
const HIDDEN_DIM: usize = 64;
const TIMESTEPS: usize = 1000;
const SEQ_LEN: usize = 128;

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ValidationResult {
    seed: u64,
    initial_loss: f64,
    final_loss: f64,
    improvement_pct: f64,
    denoising_error_untrained: f64,
    denoising_error_trained: f64,
    denoising_improvement_pct: f64,
    reload_delta: f64,
    loss_curve: Vec<f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct FinalSummary {
    timestamp: String,
    config: serde_json::Value,
    results: Vec<ValidationResult>,
    mean_improvement: f64,
    min_improvement: f64,
    seeds_positive: usize,
    all_seeds_positive: bool,
    mean_denoising_improvement: f64,
    passed: bool,
}

fn generate_batch(rng: &mut StdRng, batch_size: usize, channels: usize, seq_len: usize) -> (Array3<f64>, Array3<f64>) {
    let mut x = Array3::zeros((batch_size, channels, seq_len));
    
    for b in 0..batch_size {
        for c in 0..channels {
            for s in 0..seq_len {
                let pattern = (s as f64 * 0.1 + c as f64 * 0.2).sin() * 0.5 
                    + (s as f64 * 0.05).cos() * 0.3;
                let noise: f64 = rng.gen_range(-0.1..0.1);
                x[[b, c, s]] = pattern + noise;
            }
        }
    }
    
    let mut target = Array3::zeros((batch_size, channels, seq_len));
    let normal = StandardNormal;
    for b in 0..batch_size {
        for c in 0..channels {
            for s in 0..seq_len {
                target[[b, c, s]] = normal.sample(rng);
            }
        }
    }
    
    (x, target)
}

fn train_step(
    unet: &mut RealUNetFull,
    diffusion: &Diffusion,
    batch_size: usize,
    channels: usize,
    seq_len: usize,
    lr: f64,
    rng: &mut StdRng,
) -> f64 {
    let (x_start, target_noise) = generate_batch(rng, batch_size, channels, seq_len);
    
    let t = rng.gen_range(0..TIMESTEPS);
    let x_noisy = diffusion.q_sample(&x_start, t, Some(&target_noise));
    let noise_pred = unet.forward(&x_noisy);
    
    let target_flat = target_noise.view().into_shape((batch_size, 1, INPUT_DIM)).unwrap();
    let diff = &noise_pred - &target_flat;
    let loss = diff.mapv(|v| v * v).mean().unwrap();
    
    let grad_output = 2.0 * diff.clone() / (diff.len() as f64);
    let grad = unet.backward(&grad_output);
    unet.update(&grad, lr);
    
    loss
}

fn evaluate(
    unet: &mut RealUNetFull,
    diffusion: &Diffusion,
    validation_batches: &[(Array3<f64>, Array3<f64>)],
    channels: usize,
    rng: &mut StdRng,
) -> (f64, f64) {
    let mut total_loss = 0.0;
    let mut total_noise_error = 0.0;
    
    for (x_start, target_noise) in validation_batches {
        let t = rng.gen_range(0..TIMESTEPS);
        let x_noisy = diffusion.q_sample(x_start, t, Some(target_noise));
        let noise_pred = unet.forward(&x_noisy);
        
        let noise_pred_reshaped = noise_pred.view()
            .into_shape((x_start.shape()[0], channels, SEQ_LEN))
            .unwrap();
        
        let diff = &noise_pred_reshaped - target_noise;
        total_loss += diff.mapv(|v| v * v).mean().unwrap();
        total_noise_error += diff.mapv(|v| v.abs()).mean().unwrap();
    }
    
    let n = validation_batches.len() as f64;
    (total_loss / n, total_noise_error / n)
}

fn run_validation(seed: u64, diffusion: &Diffusion, val_batches: &[(Array3<f64>, Array3<f64>)], channels: usize) -> ValidationResult {
    println!("\nSeed {}:", seed);
    
    let mut rng = StdRng::seed_from_u64(seed);
    let mut unet = RealUNetFull::new(INPUT_DIM, HIDDEN_DIM, INPUT_DIM, seed);
    
    // Evaluate untrained
    let (initial_loss, denoising_untrained) = evaluate(&mut unet, diffusion, val_batches, channels, &mut rng);
    println!("  Untrained: loss={:.4}, denoise_err={:.4}", initial_loss, denoising_untrained);
    
    // Training
    let mut loss_curve = Vec::new();
    
    print!("  Training [");
    for step in 0..(WARMUP_STEPS + TRAIN_STEPS) {
        let loss = train_step(&mut unet, diffusion, BATCH_SIZE, channels, SEQ_LEN, LEARNING_RATE, &mut rng);
        loss_curve.push(loss);
        
        if step % 500 == 0 {
            print!(".");
        }
    }
    println!("]");
    
    // Evaluate trained
    let (final_loss, denoising_trained) = evaluate(&mut unet, diffusion, val_batches, channels, &mut rng);
    println!("  Trained:   loss={:.4}, denoise_err={:.4}", final_loss, denoising_trained);
    
    // Reload test
    let save_path = format!("/tmp/p0_5_final_{}.bin", seed);
    unet.save(&save_path).expect("Failed to save");
    
    let mut unet_reload = RealUNetFull::load(&save_path).expect("Failed to load");
    let mut rng_reload = StdRng::seed_from_u64(seed + 100000);
    let mut rng_ref = StdRng::seed_from_u64(seed + 100000);
    
    let mut reload_curve = Vec::new();
    for _ in 0..100 {
        let loss = train_step(&mut unet_reload, diffusion, BATCH_SIZE, channels, SEQ_LEN, LEARNING_RATE, &mut rng_reload);
        reload_curve.push(loss);
    }
    
    let mut ref_curve = Vec::new();
    for _ in 0..100 {
        let loss = train_step(&mut unet, diffusion, BATCH_SIZE, channels, SEQ_LEN, LEARNING_RATE, &mut rng_ref);
        ref_curve.push(loss);
    }
    
    let reload_delta = reload_curve.iter().zip(ref_curve.iter())
        .map(|(a, b)| (a - b).abs())
        .sum::<f64>() / reload_curve.len() as f64;
    
    let _ = fs::remove_file(&save_path);
    
    let improvement = (initial_loss - final_loss) / initial_loss * 100.0;
    println!("  Improvement: {:.2}%, Reload Δ: {:.6}", improvement, reload_delta);
    
    ValidationResult {
        seed,
        initial_loss,
        final_loss,
        improvement_pct: improvement,
        denoising_error_untrained: denoising_untrained,
        denoising_error_trained: denoising_trained,
        denoising_improvement_pct: (denoising_untrained - denoising_trained) / denoising_untrained * 100.0,
        reload_delta,
        loss_curve,
    }
}

fn main() {
    println!("╔════════════════════════════════════════════════════════════╗");
    println!("║   P0-5 Final Validation: Extended Optimal Config           ║");
    println!("╚════════════════════════════════════════════════════════════╝");
    println!("Config: LR={}, Steps={}, Dim={}", LEARNING_RATE, TRAIN_STEPS, INPUT_DIM);
    
    let diff_config = DiffusionConfig {
        timesteps: TIMESTEPS,
        beta_start: 1e-4,
        beta_end: 0.02,
        loss_type: "l2".to_string(),
        p_uncond: 0.1,
    };
    let diffusion = Diffusion::new(diff_config);
    
    let channels = INPUT_DIM / SEQ_LEN;  // 4
    
    // Validation set
    let mut val_rng = StdRng::seed_from_u64(7777);
    let val_batches: Vec<_> = (0..10)
        .map(|_| generate_batch(&mut val_rng, BATCH_SIZE, channels, SEQ_LEN))
        .collect();
    
    let mut results = Vec::new();
    
    for seed in &SEEDS {
        let result = run_validation(*seed, &diffusion, &val_batches, channels);
        results.push(result);
    }
    
    // Aggregate
    let improvements: Vec<f64> = results.iter().map(|r| r.improvement_pct).collect();
    let mean_improvement = improvements.iter().sum::<f64>() / improvements.len() as f64;
    let min_improvement = improvements.iter().cloned().fold(f64::INFINITY, f64::min);
    let seeds_positive = improvements.iter().filter(|&&v| v > 0.0).count();
    
    let denoise_improvements: Vec<f64> = results.iter().map(|r| r.denoising_improvement_pct).collect();
    let mean_denoising_improvement = denoise_improvements.iter().sum::<f64>() / denoise_improvements.len() as f64;
    
    let passed = seeds_positive == SEEDS.len() && mean_improvement > 5.0;
    
    let summary = FinalSummary {
        timestamp: chrono::Local::now().to_rfc3339(),
        config: serde_json::json!({
            "lr": LEARNING_RATE,
            "train_steps": TRAIN_STEPS,
            "warmup_steps": WARMUP_STEPS,
            "batch_size": BATCH_SIZE,
            "input_dim": INPUT_DIM,
            "hidden_dim": HIDDEN_DIM,
        }),
        results,
        mean_improvement,
        min_improvement,
        seeds_positive,
        all_seeds_positive: seeds_positive == SEEDS.len(),
        mean_denoising_improvement,
        passed,
    };
    
    // Save
    let output_dir = "../benchmark_results/p0_5_final_validation";
    fs::create_dir_all(output_dir).expect("Failed to create dir");
    
    let json_path = format!("{}/final_results.json", output_dir);
    fs::write(&json_path, serde_json::to_string_pretty(&summary).unwrap())
        .expect("Failed to write JSON");
    
    // Print summary
    println!("\n============================================================");
    println!("FINAL VALIDATION SUMMARY");
    println!("============================================================");
    println!("Mean Improvement: {:.2}%", mean_improvement);
    println!("Min Improvement:  {:.2}%", min_improvement);
    println!("Seeds Positive:   {}/3", seeds_positive);
    println!("Denoising Δ:      {:.2}%", mean_denoising_improvement);
    println!("Status:           {}", if passed { "✅ PASS" } else { "❌ FAIL" });
    
    if !passed {
        if mean_improvement <= 5.0 {
            println!("\n⚠️  Mean improvement below 5% threshold");
        }
        if seeds_positive < 3 {
            println!("⚠️  Not all seeds positive");
        }
    }
    
    println!("\n✓ Results saved to: {}", json_path);
    
    std::process::exit(if passed { 0 } else { 1 });
}
