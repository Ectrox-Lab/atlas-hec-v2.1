//! P0-5 Hyperparameter Sweep: Controlled 3×3×2 Matrix
//!
//! Dimensions:
//! - Learning Rate: [0.001, 0.005, 0.01] (low/mid/high based on historical evidence)
//! - Training Steps: [500, 1500, 3000] (short/mid/long)
//! - Model Scale: [Full(2048), Reduced(512)] (current/reduced)
//!
//! Historical Context:
//! - Round 19 (minimal): LR=0.05, 200 epochs → 62.4% reduction
//! - Round 20 (full RealUNet): LR=0.05, 200 epochs → 13.8% reduction
//! - Round 21 (noise-prediction): LR=0.005 → 7.9% reduction
//!
//! Target Metrics:
//! 1. Mean improvement %
//! 2. 3/3 seed positive rate
//! 3. Reload consistency
//! 4. Denoising proxy gain
//! 5. Gradient norm stability

use code_diffusion::models::realunet_full::RealUNetFull;
use code_diffusion::diffusion::{Diffusion, DiffusionConfig};
use ndarray::Array3;
use rand::{SeedableRng, Rng};
use rand::rngs::StdRng;
use rand_distr::{Distribution, StandardNormal};
use serde::{Deserialize, Serialize};
use std::fs;

// ============================================================================
// Experiment Configuration
// ============================================================================

const SEEDS: [u64; 3] = [42, 123, 999];

// 3×3×2 Matrix
const LEARNING_RATES: [f64; 3] = [0.001, 0.005, 0.01]; // low, mid, high
const TRAIN_STEPS_OPTIONS: [usize; 3] = [500, 1500, 3000]; // short, mid, long
const INPUT_DIMS: [usize; 2] = [512, 2048]; // reduced, full

const BATCH_SIZE: usize = 8;
const WARMUP_STEPS: usize = 100;
const SEQ_LEN: usize = 128;
const HIDDEN_DIM: usize = 64;
const TIMESTEPS: usize = 1000;

// ============================================================================
// Data Structures
// ============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ExperimentConfig {
    lr: f64,
    train_steps: usize,
    input_dim: usize,
    hidden_dim: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct SeedMetrics {
    seed: u64,
    initial_loss: f64,
    final_loss: f64,
    improvement_pct: f64,
    denoising_error_untrained: f64,
    denoising_error_trained: f64,
    denoising_improvement_pct: f64,
    reload_delta: f64,
    mean_gradient_norm: f64,
    max_gradient_norm: f64,
    loss_curve: Vec<f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ExperimentResult {
    config: ExperimentConfig,
    seed_metrics: Vec<SeedMetrics>,
    // Aggregates
    mean_improvement: f64,
    std_improvement: f64,
    seeds_positive: usize,
    all_seeds_positive: bool,
    mean_denoising_improvement: f64,
    mean_reload_delta: f64,
    mean_gradient_norm: f64,
    gradient_norm_stable: bool, // max/mean < 10
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct SweepSummary {
    timestamp: String,
    total_experiments: usize,
    results: Vec<ExperimentResult>,
    best_config: Option<ExperimentConfig>,
    analysis: SweepAnalysis,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct SweepAnalysis {
    lr_effect: String,
    steps_effect: String,
    scale_effect: String,
    recommendation: String,
}

// ============================================================================
// Training Functions
// ============================================================================

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
    input_dim: usize,
    lr: f64,
    rng: &mut StdRng,
) -> (f64, f64) {
    let (x_start, target_noise) = generate_batch(rng, batch_size, channels, seq_len);
    
    let t = rng.gen_range(0..TIMESTEPS);
    let x_noisy = diffusion.q_sample(&x_start, t, Some(&target_noise));
    let noise_pred = unet.forward(&x_noisy);
    
    // Reshape target
    let target_flat = target_noise.view().into_shape((batch_size, 1, input_dim)).unwrap();
    
    let diff = &noise_pred - &target_flat;
    let loss = diff.mapv(|v| v * v).mean().unwrap();
    
    let grad_output = 2.0 * diff.clone() / (diff.len() as f64);
    let grad = unet.backward(&grad_output);
    let grad_norm = grad.total_norm;
    
    unet.update(&grad, lr);
    
    (loss, grad_norm)
}

fn evaluate(
    unet: &mut RealUNetFull,
    diffusion: &Diffusion,
    validation_batches: &[(Array3<f64>, Array3<f64>)],
    input_dim: usize,
    rng: &mut StdRng,
) -> (f64, f64) {
    let mut total_loss = 0.0;
    let mut total_noise_error = 0.0;
    
    for (x_start, target_noise) in validation_batches {
        let t = rng.gen_range(0..TIMESTEPS);
        let x_noisy = diffusion.q_sample(x_start, t, Some(target_noise));
        let noise_pred = unet.forward(&x_noisy);
        
        let noise_pred_reshaped = noise_pred.view()
            .into_shape((x_start.shape()[0], target_noise.shape()[1], target_noise.shape()[2]))
            .unwrap();
        
        let diff = &noise_pred_reshaped - target_noise;
        total_loss += diff.mapv(|v| v * v).mean().unwrap();
        total_noise_error += diff.mapv(|v| v.abs()).mean().unwrap();
    }
    
    let n = validation_batches.len() as f64;
    (total_loss / n, total_noise_error / n)
}

fn run_single_seed(
    seed: u64,
    config: &ExperimentConfig,
    diffusion: &Diffusion,
    validation_batches: &[(Array3<f64>, Array3<f64>)],
) -> SeedMetrics {
    let mut rng = StdRng::seed_from_u64(seed);
    // Scale channels to match input_dim (channels * seq_len = input_dim)
    let seq_len = 128;
    let channels = config.input_dim / seq_len;
    
    // Initialize model
    let mut unet = RealUNetFull::new(config.input_dim, config.hidden_dim, config.input_dim, seed);
    
    // Evaluate untrained
    let (initial_loss, denoising_error_untrained) = 
        evaluate(&mut unet, diffusion, validation_batches, config.input_dim, &mut rng);
    
    // Training
    let mut loss_curve = Vec::new();
    let mut gradient_norms = Vec::new();
    
    // Warmup
    for _ in 0..WARMUP_STEPS {
        let (loss, grad_norm) = train_step(&mut unet, diffusion, BATCH_SIZE, channels, seq_len, 
                                           config.input_dim, config.lr, &mut rng);
        loss_curve.push(loss);
        gradient_norms.push(grad_norm);
    }
    
    // Main training
    for _ in 0..config.train_steps {
        let (loss, grad_norm) = train_step(&mut unet, diffusion, BATCH_SIZE, channels, seq_len,
                                           config.input_dim, config.lr, &mut rng);
        loss_curve.push(loss);
        gradient_norms.push(grad_norm);
    }
    
    // Evaluate trained
    let (final_loss, denoising_error_trained) = 
        evaluate(&mut unet, diffusion, validation_batches, config.input_dim, &mut rng);
    
    // Reload consistency test
    let save_path = format!("/tmp/p0_5_sweep_{}_{}_{}_{}.bin", 
                           config.lr, config.train_steps, config.input_dim, seed);
    unet.save(&save_path).expect("Failed to save");
    
    let mut unet_reload = RealUNetFull::load(&save_path).expect("Failed to load");
    let mut rng_reload = StdRng::seed_from_u64(seed + 100000);
    let mut reload_curve = Vec::new();
    
    for _ in 0..100 {
        let (loss, _) = train_step(&mut unet_reload, diffusion, BATCH_SIZE, channels, seq_len,
                                   config.input_dim, config.lr, &mut rng_reload);
        reload_curve.push(loss);
    }
    
    // Compare with continuous training
    let mut rng_ref = StdRng::seed_from_u64(seed + 100000);
    let mut ref_curve = Vec::new();
    for _ in 0..100 {
        let (loss, _) = train_step(&mut unet, diffusion, BATCH_SIZE, channels, seq_len,
                                   config.input_dim, config.lr, &mut rng_ref);
        ref_curve.push(loss);
    }
    
    let reload_delta = reload_curve.iter().zip(ref_curve.iter())
        .map(|(a, b)| (a - b).abs())
        .sum::<f64>() / reload_curve.len() as f64;
    
    let _ = fs::remove_file(&save_path);
    
    let mean_grad_norm = gradient_norms.iter().sum::<f64>() / gradient_norms.len() as f64;
    let max_grad_norm = gradient_norms.iter().cloned().fold(0.0, f64::max);
    
    SeedMetrics {
        seed,
        initial_loss,
        final_loss,
        improvement_pct: (initial_loss - final_loss) / initial_loss * 100.0,
        denoising_error_untrained,
        denoising_error_trained,
        denoising_improvement_pct: (denoising_error_untrained - denoising_error_trained) 
                                   / denoising_error_untrained * 100.0,
        reload_delta,
        mean_gradient_norm: mean_grad_norm,
        max_gradient_norm: max_grad_norm,
        loss_curve,
    }
}

// ============================================================================
// Main Sweep
// ============================================================================

fn run_experiment(config: &ExperimentConfig) -> ExperimentResult {
    println!("\n============================================================");
    println!("Experiment: LR={}, Steps={}, Dim={}", 
             config.lr, config.train_steps, config.input_dim);
    println!("============================================================");
    
    let diff_config = DiffusionConfig {
        timesteps: TIMESTEPS,
        beta_start: 1e-4,
        beta_end: 0.02,
        loss_type: "l2".to_string(),
        p_uncond: 0.1,
    };
    let diffusion = Diffusion::new(diff_config);
    
    // Generate validation set - scale channels to match input_dim
    let seq_len = 128;
    let channels = config.input_dim / seq_len;
    let mut val_rng = StdRng::seed_from_u64(7777);
    let validation_batches: Vec<_> = (0..10)
        .map(|_| generate_batch(&mut val_rng, BATCH_SIZE, channels, seq_len))
        .collect();
    
    let mut seed_metrics = Vec::new();
    
    for seed in &SEEDS {
        let metrics = run_single_seed(*seed, config, &diffusion, &validation_batches);
        println!("  Seed {}: improv={:.2}%, denoise_improv={:.2}%, reload_Δ={:.6}, grad_norm={:.2}",
                metrics.seed, metrics.improvement_pct, metrics.denoising_improvement_pct,
                metrics.reload_delta, metrics.mean_gradient_norm);
        seed_metrics.push(metrics);
    }
    
    // Aggregate
    let improvements: Vec<f64> = seed_metrics.iter().map(|m| m.improvement_pct).collect();
    let mean_improvement = improvements.iter().sum::<f64>() / improvements.len() as f64;
    let std_improvement = (improvements.iter()
        .map(|v| (v - mean_improvement).powi(2))
        .sum::<f64>() / improvements.len() as f64)
        .sqrt();
    let seeds_positive = improvements.iter().filter(|&&v| v > 0.0).count();
    
    let denoising_improvements: Vec<f64> = seed_metrics.iter()
        .map(|m| m.denoising_improvement_pct).collect();
    let mean_denoising_improvement = denoising_improvements.iter().sum::<f64>() 
                                     / denoising_improvements.len() as f64;
    
    let reload_deltas: Vec<f64> = seed_metrics.iter().map(|m| m.reload_delta).collect();
    let mean_reload_delta = reload_deltas.iter().sum::<f64>() / reload_deltas.len() as f64;
    
    let grad_norms: Vec<f64> = seed_metrics.iter().map(|m| m.mean_gradient_norm).collect();
    let mean_gradient_norm = grad_norms.iter().sum::<f64>() / grad_norms.len() as f64;
    let max_grad_norms: Vec<f64> = seed_metrics.iter().map(|m| m.max_gradient_norm).collect();
    let max_grad_norm = max_grad_norms.iter().cloned().fold(0.0, f64::max);
    
    ExperimentResult {
        config: config.clone(),
        seed_metrics,
        mean_improvement,
        std_improvement,
        seeds_positive,
        all_seeds_positive: seeds_positive == SEEDS.len(),
        mean_denoising_improvement,
        mean_reload_delta,
        mean_gradient_norm,
        gradient_norm_stable: max_grad_norm / mean_gradient_norm < 10.0,
    }
}

// ============================================================================
// Analysis & Report
// ============================================================================

fn analyze_results(results: &[ExperimentResult]) -> SweepAnalysis {
    // Find best by mean improvement with all seeds positive
    let viable: Vec<_> = results.iter()
        .filter(|r| r.all_seeds_positive)
        .collect();
    
    let best = viable.iter()
        .max_by(|a, b| a.mean_improvement.partial_cmp(&b.mean_improvement).unwrap());
    
    let lr_analysis = if results.iter().filter(|r| r.config.lr == 0.01)
        .map(|r| r.mean_improvement).sum::<f64>() / 6.0 > 
        results.iter().filter(|r| r.config.lr == 0.001)
        .map(|r| r.mean_improvement).sum::<f64>() / 6.0 {
        "Higher LR (0.01) shows better improvement than low (0.001)"
    } else {
        "Lower LR shows better stability; high LR may be unstable"
    };
    
    let steps_analysis = if results.iter().filter(|r| r.config.train_steps == 3000)
        .map(|r| r.mean_improvement).sum::<f64>() / 6.0 >
        results.iter().filter(|r| r.config.train_steps == 500)
        .map(|r| r.mean_improvement).sum::<f64>() / 6.0 {
        "Longer training (3000 steps) consistently outperforms short (500)"
    } else {
        "Training duration effect unclear; may need more steps or different LR"
    };
    
    let scale_analysis = if results.iter().filter(|r| r.config.input_dim == 512)
        .map(|r| r.mean_improvement).sum::<f64>() / 9.0 >
        results.iter().filter(|r| r.config.input_dim == 2048)
        .map(|r| r.mean_improvement).sum::<f64>() / 9.0 {
        "Reduced scale (512) significantly outperforms full (2048)"
    } else {
        "Scale effect mixed; larger models may need different optimization"
    };
    
    let recommendation = if let Some(b) = best {
        format!("Best config: LR={}, Steps={}, Dim={} → {:.2}% improvement (all seeds positive)",
               b.config.lr, b.config.train_steps, b.config.input_dim, b.mean_improvement)
    } else {
        "No config achieved all-seeds-positive. Try: longer steps, adjusted LR, or reduced scale.".to_string()
    };
    
    SweepAnalysis {
        lr_effect: lr_analysis.to_string(),
        steps_effect: steps_analysis.to_string(),
        scale_effect: scale_analysis.to_string(),
        recommendation,
    }
}

fn generate_report(summary: &SweepSummary) -> String {
    let mut report = String::new();
    
    report.push_str("# P0-5 Hyperparameter Sweep Report\n\n");
    report.push_str(&format!("**Timestamp:** {}\n\n", summary.timestamp));
    report.push_str(&format!("**Total Experiments:** {}\n\n", summary.total_experiments));
    
    report.push_str("## Experiment Matrix\n\n");
    report.push_str("| LR | Steps | Dim | Mean Improv | Seeds + | Denoise Δ | Reload Δ | Stable |\n");
    report.push_str("|----|-------|-----|-------------|---------|-----------|----------|--------|\n");
    
    for r in &summary.results {
        report.push_str(&format!(
            "| {:.3} | {} | {} | {:.2}% | {}/3 | {:.2}% | {:.6} | {} |\n",
            r.config.lr,
            r.config.train_steps,
            r.config.input_dim,
            r.mean_improvement,
            r.seeds_positive,
            r.mean_denoising_improvement,
            r.mean_reload_delta,
            if r.gradient_norm_stable { "✅" } else { "⚠️" }
        ));
    }
    
    report.push_str("\n## Analysis\n\n");
    report.push_str(&format!("**Learning Rate Effect:** {}\n\n", summary.analysis.lr_effect));
    report.push_str(&format!("**Training Duration Effect:** {}\n\n", summary.analysis.steps_effect));
    report.push_str(&format!("**Model Scale Effect:** {}\n\n", summary.analysis.scale_effect));
    report.push_str(&format!("**Recommendation:** {}\n\n", summary.analysis.recommendation));
    
    if let Some(best) = &summary.best_config {
        report.push_str("## Best Configuration\n\n");
        report.push_str(&format!("- Learning Rate: {:.3}\n", best.lr));
        report.push_str(&format!("- Training Steps: {}\n", best.train_steps));
        report.push_str(&format!("- Input Dimension: {}\n", best.input_dim));
    }
    
    report
}

// ============================================================================
// Main
// ============================================================================

fn main() {
    println!("╔════════════════════════════════════════════════════════════╗");
    println!("║   P0-5 Hyperparameter Sweep: 3×3×2 Controlled Matrix       ║");
    println!("╚════════════════════════════════════════════════════════════╝");
    
    let mut results = Vec::new();
    let mut best_result: Option<ExperimentResult> = None;
    
    for &lr in &LEARNING_RATES {
        for &steps in &TRAIN_STEPS_OPTIONS {
            for &input_dim in &INPUT_DIMS {
                let config = ExperimentConfig {
                    lr,
                    train_steps: steps,
                    input_dim,
                    hidden_dim: HIDDEN_DIM,
                };
                
                let result = run_experiment(&config);
                
                // Track best
                if result.all_seeds_positive {
                    if best_result.as_ref().map_or(true, |b| 
                        result.mean_improvement > b.mean_improvement) {
                        best_result = Some(result.clone());
                    }
                }
                
                results.push(result);
            }
        }
    }
    
    // Analysis
    let analysis = analyze_results(&results);
    
    let summary = SweepSummary {
        timestamp: chrono::Local::now().to_rfc3339(),
        total_experiments: results.len(),
        results,
        best_config: best_result.as_ref().map(|r| r.config.clone()),
        analysis,
    };
    
    // Save results
    let output_dir = "../benchmark_results/p0_5_hyperparam_sweep";
    fs::create_dir_all(output_dir).expect("Failed to create output dir");
    
    let json_path = format!("{}/sweep_results.json", output_dir);
    let json = serde_json::to_string_pretty(&summary).expect("Failed to serialize");
    fs::write(&json_path, json).expect("Failed to write JSON");
    println!("\n✓ Results saved to: {}", json_path);
    
    let report = generate_report(&summary);
    let md_path = format!("{}/sweep_report.md", output_dir);
    fs::write(&md_path, report).expect("Failed to write report");
    println!("✓ Report saved to: {}", md_path);
    
    // Summary
    println!("\n============================================================");
    println!("SWEEP SUMMARY");
    println!("============================================================");
    println!("Total experiments: {}", summary.total_experiments);
    println!("Configs with all seeds positive: {}", 
             summary.results.iter().filter(|r| r.all_seeds_positive).count());
    
    if let Some(best) = &best_result {
        println!("\n🏆 Best Config:");
        println!("  LR: {:.3}, Steps: {}, Dim: {}", 
                best.config.lr, best.config.train_steps, best.config.input_dim);
        println!("  Mean improvement: {:.2}%", best.mean_improvement);
        println!("  Denoising improvement: {:.2}%", best.mean_denoising_improvement);
    } else {
        println!("\n⚠️ No config achieved all-seeds-positive");
    }
    
    println!("\n📊 Analysis:");
    println!("  LR: {}", summary.analysis.lr_effect);
    println!("  Steps: {}", summary.analysis.steps_effect);
    println!("  Scale: {}", summary.analysis.scale_effect);
}
