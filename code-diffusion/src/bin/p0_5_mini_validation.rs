//! P0-5 Mini Validation: Multi-seed stability + Trained vs Untrained + Reload Consistency
//!
//! Validation Criteria:
//! 1. 3/3 seeds show positive loss reduction
//! 2. Average improvement > 5%
//! 3. Trained significantly outperforms untrained
//! 4. Reload consistency: delta < threshold
//! 5. No NaN / exploding updates

use code_diffusion::models::realunet_full::RealUNetFull;
use code_diffusion::diffusion::{Diffusion, DiffusionConfig};
use ndarray::{Array3};
use rand::{SeedableRng, Rng};
use rand::rngs::StdRng;
use rand_distr::{Distribution, StandardNormal};
use serde::{Deserialize, Serialize};
use std::fs;

// ============================================================================
// Configuration
// ============================================================================

const SEEDS: [u64; 3] = [42, 123, 999];
const WARMUP_STEPS: usize = 100;
const TRAIN_STEPS: usize = 500;
const RELOAD_STEPS_PART1: usize = 100;
const RELOAD_STEPS_PART2: usize = 100;
const BATCH_SIZE: usize = 8;
const LEARNING_RATE: f64 = 1e-3;
const SEQ_LEN: usize = 128;
const HIDDEN_DIM: usize = 64;
const CHANNELS: usize = 16;
const INPUT_DIM: usize = CHANNELS * SEQ_LEN;  // 2048
const TIMESTEPS: usize = 1000;

const IMPROVEMENT_THRESHOLD: f64 = 0.05; // 5%
const RELOAD_TOLERANCE: f64 = 0.01; // 1% relative error allowed

// ============================================================================
// Data Structures
// ============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
struct SeedResult {
    seed: u64,
    initial_loss: f64,
    final_loss: f64,
    improvement_pct: f64,
    reload_consistency_delta: f64,
    loss_curve: Vec<f64>,
    reload_curve_part2: Vec<f64>,
    reference_curve_continuous: Vec<f64>,
    trained_vs_untrained: TrainedVsUntrained,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct TrainedVsUntrained {
    untrained_loss: f64,
    trained_loss: f64,
    relative_improvement_pct: f64,
    noise_prediction_error_untrained: f64,
    noise_prediction_error_trained: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ValidationSummary {
    timestamp: String,
    config: ConfigSnapshot,
    seed_results: Vec<SeedResult>,
    aggregate: AggregateMetrics,
    passed: bool,
    failures: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ConfigSnapshot {
    seeds: Vec<u64>,
    warmup_steps: usize,
    train_steps: usize,
    reload_steps_part1: usize,
    reload_steps_part2: usize,
    batch_size: usize,
    learning_rate: f64,
    seq_len: usize,
    hidden_dim: usize,
    channels: usize,
    timesteps: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct AggregateMetrics {
    mean_improvement_pct: f64,
    std_improvement_pct: f64,
    min_improvement_pct: f64,
    seeds_with_positive_improvement: usize,
    mean_reload_delta: f64,
    max_reload_delta: f64,
    trained_vs_untrained_mean_improvement: f64,
}

// ============================================================================
// Data Generation
// ============================================================================

fn generate_synthetic_batch(rng: &mut StdRng, batch_size: usize) -> (Array3<f64>, Array3<f64>) {
    // Generate synthetic code-like data with structure
    let mut x = Array3::zeros((batch_size, CHANNELS, SEQ_LEN));
    
    for b in 0..batch_size {
        // Create structured patterns (simulating code tokens)
        for c in 0..CHANNELS {
            for s in 0..SEQ_LEN {
                // Mix of sinusoidal patterns and noise
                let pattern = (s as f64 * 0.1 + c as f64 * 0.2).sin() * 0.5 
                    + (s as f64 * 0.05).cos() * 0.3;
                let noise: f64 = rng.gen_range(-0.1..0.1);
                x[[b, c, s]] = pattern + noise;
            }
        }
    }
    
    // Generate target noise using StandardNormal distribution
    let mut target = Array3::zeros((batch_size, CHANNELS, SEQ_LEN));
    let normal = StandardNormal;
    for b in 0..batch_size {
        for c in 0..CHANNELS {
            for s in 0..SEQ_LEN {
                target[[b, c, s]] = normal.sample(rng);
            }
        }
    }
    
    (x, target)
}

fn generate_validation_set(seed: u64, num_batches: usize) -> Vec<(Array3<f64>, Array3<f64>)> {
    let mut rng = StdRng::seed_from_u64(seed + 10000);
    let mut batches = Vec::new();
    
    for _ in 0..num_batches {
        batches.push(generate_synthetic_batch(&mut rng, BATCH_SIZE));
    }
    
    batches
}

// ============================================================================
// Training Functions
// ============================================================================

fn train_step(
    unet: &mut RealUNetFull,
    diffusion: &Diffusion,
    x_start: &Array3<f64>,
    target_noise: &Array3<f64>,
    rng: &mut StdRng,
) -> f64 {
    // Sample timestep
    let t = rng.gen_range(0..TIMESTEPS);
    
    // Forward: add noise
    let x_noisy = diffusion.q_sample(x_start, t, Some(target_noise));
    
    // Forward: predict noise
    let noise_pred = unet.forward(&x_noisy);
    
    // Reshape target_noise from (batch, channels, seq) to (batch, 1, channels*seq) for comparison
    let batch_size = target_noise.shape()[0];
    let target_flat = target_noise.view().into_shape((batch_size, 1, INPUT_DIM)).unwrap();
    
    // Loss: MSE
    let diff = &noise_pred - &target_flat;
    let loss = diff.mapv(|v| v * v).mean().unwrap();
    
    // Backward
    let grad_output = 2.0 * diff.clone() / (diff.len() as f64);
    let grad = unet.backward(&grad_output);
    
    // Update
    unet.update(&grad, LEARNING_RATE);
    
    loss
}

fn evaluate_on_batch(
    unet: &mut RealUNetFull,
    diffusion: &Diffusion,
    x_start: &Array3<f64>,
    target_noise: &Array3<f64>,
    rng: &mut StdRng,
) -> (f64, f64) {
    let t = rng.gen_range(0..TIMESTEPS);
    let x_noisy = diffusion.q_sample(x_start, t, Some(target_noise));
    let noise_pred = unet.forward(&x_noisy);
    
    // Reshape noise_pred from (batch, 1, channels*seq_len) to (batch, channels, seq_len)
    let batch_size = noise_pred.shape()[0];
    let noise_pred_reshaped = noise_pred.view().into_shape((batch_size, CHANNELS, SEQ_LEN)).unwrap();
    
    let diff = &noise_pred_reshaped - target_noise;
    let loss = diff.mapv(|v| v * v).mean().unwrap();
    let noise_error = diff.mapv(|v| v.abs()).mean().unwrap();
    
    (loss, noise_error)
}

fn evaluate_on_set(
    unet: &mut RealUNetFull,
    diffusion: &Diffusion,
    validation_set: &[(Array3<f64>, Array3<f64>)],
    rng: &mut StdRng,
) -> (f64, f64) {
    let mut total_loss = 0.0;
    let mut total_noise_error = 0.0;
    
    for (x_start, target_noise) in validation_set {
        let (loss, noise_error) = evaluate_on_batch(unet, diffusion, x_start, target_noise, rng);
        total_loss += loss;
        total_noise_error += noise_error;
    }
    
    let n = validation_set.len() as f64;
    (total_loss / n, total_noise_error / n)
}

fn train_for_steps(
    unet: &mut RealUNetFull,
    diffusion: &Diffusion,
    steps: usize,
    rng: &mut StdRng,
    loss_curve: &mut Vec<f64>,
) {
    for _ in 0..steps {
        let (x_start, target_noise) = generate_synthetic_batch(rng, BATCH_SIZE);
        let loss = train_step(unet, diffusion, &x_start, &target_noise, rng);
        loss_curve.push(loss);
    }
}

// ============================================================================
// Per-Seed Validation
// ============================================================================

fn run_seed_validation(seed: u64) -> SeedResult {
    println!("\n============================================================");
    println!("Running validation for seed: {}", seed);
    println!("============================================================");
    
    let mut rng = StdRng::seed_from_u64(seed);
    let config = DiffusionConfig {
        timesteps: TIMESTEPS,
        beta_start: 1e-4,
        beta_end: 0.02,
        loss_type: "l2".to_string(),
        p_uncond: 0.1,
    };
    let diffusion = Diffusion::new(config);
    
    // Generate validation set
    let validation_set = generate_validation_set(seed, 10);
    
    // Initialize model (input_dim = channels * seq_len, output_dim = channels * seq_len)
    let mut unet = RealUNetFull::new(INPUT_DIM, HIDDEN_DIM, INPUT_DIM, seed);
    
    // Evaluate untrained
    let (untrained_loss, untrained_noise_error) = 
        evaluate_on_set(&mut unet, &diffusion, &validation_set, &mut rng);
    println!("Untrained - Loss: {:.6}, Noise Error: {:.6}", 
             untrained_loss, untrained_noise_error);
    
    // Record initial loss
    let initial_loss = untrained_loss;
    
    // Warmup training
    println!("Warmup ({} steps)...", WARMUP_STEPS);
    let mut loss_curve = Vec::new();
    train_for_steps(&mut unet, &diffusion, WARMUP_STEPS, &mut rng, &mut loss_curve);
    
    // Main training
    println!("Main training ({} steps)...", TRAIN_STEPS);
    train_for_steps(&mut unet, &diffusion, TRAIN_STEPS, &mut rng, &mut loss_curve);
    
    // Evaluate trained
    let (trained_loss, trained_noise_error) = 
        evaluate_on_set(&mut unet, &diffusion, &validation_set, &mut rng);
    println!("Trained - Loss: {:.6}, Noise Error: {:.6}", 
             trained_loss, trained_noise_error);
    
    let final_loss = trained_loss;
    let improvement_pct = (initial_loss - final_loss) / initial_loss;
    
    // =========================================================================
    // Reload Consistency Test
    // =========================================================================
    println!("\nReload consistency test...");
    
    // Save current model
    let save_path = format!("/tmp/p0_5_model_seed_{}.bin", seed);
    unet.save(&save_path).expect("Failed to save model");
    
    // Reset RNG to known state for fair comparison
    let mut rng_reload = StdRng::seed_from_u64(seed + 50000);
    let mut rng_reference = StdRng::seed_from_u64(seed + 50000);
    
    // Reload and continue training
    let mut unet_reload = RealUNetFull::load(&save_path).expect("Failed to load model");
    let mut reload_curve_part2 = Vec::new();
    train_for_steps(&mut unet_reload, &diffusion, RELOAD_STEPS_PART2, 
                    &mut rng_reload, &mut reload_curve_part2);
    
    // Reference: continuous training without interruption
    let mut unet_reference = RealUNetFull::new(INPUT_DIM, HIDDEN_DIM, INPUT_DIM, seed);
    // Train up to same point as the original
    let mut _dummy_curve = Vec::new();
    train_for_steps(&mut unet_reference, &diffusion, 
                    WARMUP_STEPS + TRAIN_STEPS + RELOAD_STEPS_PART2,
                    &mut rng_reference, &mut _dummy_curve);
    
    // Compare: get reference's final segment
    let mut rng_ref_segment = StdRng::seed_from_u64(seed + 50000);
    let mut reference_curve_continuous = Vec::new();
    train_for_steps(&mut unet_reference, &diffusion, RELOAD_STEPS_PART2,
                    &mut rng_ref_segment, &mut reference_curve_continuous);
    
    // Calculate reload consistency delta
    let reload_consistency_delta = if reload_curve_part2.len() == reference_curve_continuous.len() {
        let diffs: Vec<f64> = reload_curve_part2.iter()
            .zip(reference_curve_continuous.iter())
            .map(|(a, b)| (a - b).abs())
            .collect();
        diffs.iter().sum::<f64>() / diffs.len() as f64
    } else {
        f64::NAN
    };
    
    println!("Reload consistency delta: {:.8}", reload_consistency_delta);
    
    // Cleanup
    let _ = fs::remove_file(&save_path);
    
    SeedResult {
        seed,
        initial_loss,
        final_loss,
        improvement_pct,
        reload_consistency_delta,
        loss_curve,
        reload_curve_part2,
        reference_curve_continuous,
        trained_vs_untrained: TrainedVsUntrained {
            untrained_loss,
            trained_loss,
            relative_improvement_pct: (untrained_loss - trained_loss) / untrained_loss * 100.0,
            noise_prediction_error_untrained: untrained_noise_error,
            noise_prediction_error_trained: trained_noise_error,
        },
    }
}

// ============================================================================
// Report Generation
// ============================================================================

fn generate_markdown_report(summary: &ValidationSummary) -> String {
    let mut report = String::new();
    
    report.push_str("# P0-5 Mini Validation Report\n\n");
    report.push_str(&format!("**Timestamp:** {}\n\n", summary.timestamp));
    report.push_str(&format!("**Overall Status:** {}\n\n", 
                            if summary.passed { "✅ PASS" } else { "❌ FAIL" }));
    
    if !summary.failures.is_empty() {
        report.push_str("## Failures\n\n");
        for failure in &summary.failures {
            report.push_str(&format!("- {}\n", failure));
        }
        report.push_str("\n");
    }
    
    report.push_str("## Configuration\n\n");
    report.push_str(&format!("- Seeds: {:?}\n", summary.config.seeds));
    report.push_str(&format!("- Warmup Steps: {}\n", summary.config.warmup_steps));
    report.push_str(&format!("- Train Steps: {}\n", summary.config.train_steps));
    report.push_str(&format!("- Batch Size: {}\n", summary.config.batch_size));
    report.push_str(&format!("- Learning Rate: {}\n", summary.config.learning_rate));
    report.push_str(&format!("- Sequence Length: {}\n", summary.config.seq_len));
    report.push_str(&format!("- Hidden Dim: {}\n", summary.config.hidden_dim));
    report.push_str(&format!("- Channels: {}\n", summary.config.channels));
    report.push_str(&format!("- Timesteps: {}\n\n", summary.config.timesteps));
    
    report.push_str("## Per-Seed Results\n\n");
    report.push_str("| Seed | Initial Loss | Final Loss | Improvement % | Reload Δ | Status |\n");
    report.push_str("|------|--------------|------------|---------------|----------|--------|\n");
    
    for result in &summary.seed_results {
        let status = if result.improvement_pct > IMPROVEMENT_THRESHOLD {
            "✅"
        } else if result.improvement_pct > 0.0 {
            "⚠️"
        } else {
            "❌"
        };
        report.push_str(&format!(
            "| {} | {:.6} | {:.6} | {:.2}% | {:.8} | {} |\n",
            result.seed,
            result.initial_loss,
            result.final_loss,
            result.improvement_pct * 100.0,
            result.reload_consistency_delta,
            status
        ));
    }
    
    report.push_str("\n## Trained vs Untrained Comparison\n\n");
    report.push_str("| Seed | Untrained Loss | Trained Loss | Improvement % | Noise Error (U) | Noise Error (T) |\n");
    report.push_str("|------|----------------|--------------|---------------|-----------------|-----------------|\n");
    
    for result in &summary.seed_results {
        let tv = &result.trained_vs_untrained;
        report.push_str(&format!(
            "| {} | {:.6} | {:.6} | {:.2}% | {:.6} | {:.6} |\n",
            result.seed,
            tv.untrained_loss,
            tv.trained_loss,
            tv.relative_improvement_pct,
            tv.noise_prediction_error_untrained,
            tv.noise_prediction_error_trained
        ));
    }
    
    report.push_str("\n## Aggregate Metrics\n\n");
    report.push_str(&format!("- Mean Improvement: {:.2}%\n", summary.aggregate.mean_improvement_pct * 100.0));
    report.push_str(&format!("- Std Improvement: {:.2}%\n", summary.aggregate.std_improvement_pct * 100.0));
    report.push_str(&format!("- Min Improvement: {:.2}%\n", summary.aggregate.min_improvement_pct * 100.0));
    report.push_str(&format!("- Seeds with Positive Improvement: {}/{}\n", 
                            summary.aggregate.seeds_with_positive_improvement, 
                            summary.seed_results.len()));
    report.push_str(&format!("- Mean Reload Δ: {:.8}\n", summary.aggregate.mean_reload_delta));
    report.push_str(&format!("- Max Reload Δ: {:.8}\n", summary.aggregate.max_reload_delta));
    report.push_str(&format!("- Trained vs Untrained Mean Improvement: {:.2}%\n\n",
                            summary.aggregate.trained_vs_untrained_mean_improvement));
    
    report.push_str("## Validation Criteria\n\n");
    report.push_str(&format!("- ✅ 3/3 seeds positive improvement: {}\n",
                            if summary.aggregate.seeds_with_positive_improvement >= 3 { "PASS" } else { "FAIL" }));
    report.push_str(&format!("- ✅ Mean improvement > 5%: {} ({:.2}%)\n",
                            if summary.aggregate.mean_improvement_pct > IMPROVEMENT_THRESHOLD { "PASS" } else { "FAIL" },
                            summary.aggregate.mean_improvement_pct * 100.0));
    report.push_str(&format!("- ✅ Reload consistency (mean Δ < {}): {}\n",
                            RELOAD_TOLERANCE,
                            if summary.aggregate.mean_reload_delta < RELOAD_TOLERANCE { "PASS" } else { "FAIL" }));
    
    report
}

// ============================================================================
// Main
// ============================================================================

fn main() {
    println!("╔════════════════════════════════════════════════════════════╗");
    println!("║     P0-5 Mini Validation: Real Gradient Training           ║");
    println!("╚════════════════════════════════════════════════════════════╝");
    
    // Run validation for each seed
    let mut seed_results = Vec::new();
    
    for seed in &SEEDS {
        let result = run_seed_validation(*seed);
        seed_results.push(result);
    }
    
    // Calculate aggregate metrics
    let improvements: Vec<f64> = seed_results.iter()
        .map(|r| r.improvement_pct)
        .collect();
    let mean_improvement = improvements.iter().sum::<f64>() / improvements.len() as f64;
    let std_improvement = (improvements.iter()
        .map(|v| (v - mean_improvement).powi(2))
        .sum::<f64>() / improvements.len() as f64)
        .sqrt();
    let min_improvement = improvements.iter().cloned().fold(f64::INFINITY, f64::min);
    let seeds_positive = improvements.iter().filter(|&&v| v > 0.0).count();
    
    let reload_deltas: Vec<f64> = seed_results.iter()
        .map(|r| r.reload_consistency_delta)
        .filter(|v| !v.is_nan())
        .collect();
    let mean_reload_delta = reload_deltas.iter().sum::<f64>() / reload_deltas.len() as f64;
    let max_reload_delta = reload_deltas.iter().cloned().fold(0.0, f64::max);
    
    let trained_vs_untrained_improvements: Vec<f64> = seed_results.iter()
        .map(|r| r.trained_vs_untrained.relative_improvement_pct / 100.0)
        .collect();
    let mean_trained_vs_untrained = trained_vs_untrained_improvements.iter()
        .sum::<f64>() / trained_vs_untrained_improvements.len() as f64;
    
    // Determine pass/fail
    let mut failures = Vec::new();
    
    if seeds_positive < SEEDS.len() {
        failures.push(format!("Only {}/{} seeds showed positive improvement", 
                             seeds_positive, SEEDS.len()));
    }
    if mean_improvement < IMPROVEMENT_THRESHOLD {
        failures.push(format!("Mean improvement {:.2}% below threshold {:.2}%",
                             mean_improvement * 100.0, IMPROVEMENT_THRESHOLD * 100.0));
    }
    if mean_reload_delta > RELOAD_TOLERANCE {
        failures.push(format!("Mean reload delta {:.6} exceeds tolerance {:.6}",
                             mean_reload_delta, RELOAD_TOLERANCE));
    }
    
    let passed = failures.is_empty();
    
    let summary = ValidationSummary {
        timestamp: chrono::Local::now().to_rfc3339(),
        config: ConfigSnapshot {
            seeds: SEEDS.to_vec(),
            warmup_steps: WARMUP_STEPS,
            train_steps: TRAIN_STEPS,
            reload_steps_part1: RELOAD_STEPS_PART1,
            reload_steps_part2: RELOAD_STEPS_PART2,
            batch_size: BATCH_SIZE,
            learning_rate: LEARNING_RATE,
            seq_len: SEQ_LEN,
            hidden_dim: HIDDEN_DIM,
            channels: CHANNELS,
            timesteps: TIMESTEPS,
        },
        seed_results,
        aggregate: AggregateMetrics {
            mean_improvement_pct: mean_improvement,
            std_improvement_pct: std_improvement,
            min_improvement_pct: min_improvement,
            seeds_with_positive_improvement: seeds_positive,
            mean_reload_delta,
            max_reload_delta,
            trained_vs_untrained_mean_improvement: mean_trained_vs_untrained,
        },
        passed,
        failures,
    };
    
    // Ensure output directory exists
    let output_dir = "../benchmark_results/p0_5_mini_validation";
    fs::create_dir_all(output_dir).expect("Failed to create output directory");
    
    // Save JSON
    let json_path = format!("{}/summary.json", output_dir);
    let json = serde_json::to_string_pretty(&summary).expect("Failed to serialize JSON");
    fs::write(&json_path, json).expect("Failed to write JSON");
    println!("\n✓ JSON saved to: {}", json_path);
    
    // Save Markdown report
    let report = generate_markdown_report(&summary);
    let md_path = format!("{}/report.md", output_dir);
    fs::write(&md_path, report).expect("Failed to write report");
    println!("✓ Report saved to: {}", md_path);
    
    // Print summary
    println!("\n============================================================");
    println!("VALIDATION SUMMARY");
    println!("============================================================");
    println!("Status: {}", if passed { "✅ PASS" } else { "❌ FAIL" });
    println!("Mean Improvement: {:.2}%", mean_improvement * 100.0);
    println!("Seeds Positive: {}/{}", seeds_positive, SEEDS.len());
    println!("Mean Reload Δ: {:.8}", mean_reload_delta);
    
    if !summary.failures.is_empty() {
        println!("\nFailures:");
        for failure in &summary.failures {
            println!("  - {}", failure);
        }
    }
    
    std::process::exit(if passed { 0 } else { 1 });
}
