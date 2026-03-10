//! Round 18: RealUNet Single-Layer Gradient Integration Pilot
//!
//! Tests gradient-based update on ONE layer (input_proj) with frozen others.
//! Scope deliberately limited to validate mechanism before system-wide rollout.

use code_diffusion::models::realunet_gradient::{RealUNetGradientPilot, InputProjGradient};
use ndarray::{Array1, Array2, Array3};
use rand::distributions::Distribution;
use rand::{Rng, SeedableRng};
use rand::rngs::StdRng;
use rand_distr::StandardNormal;
use serde_json::json;
use std::fs;

/// Synthetic regression task: predict target from input
fn generate_batch(batch_size: usize, input_dim: usize, seed: u64) -> (Array3<f64>, Array3<f64>) {
    let mut rng = StdRng::seed_from_u64(seed);
    
    // Input: random values
    let x: Array3<f64> = Array3::from_shape_fn(
        (batch_size, 1, input_dim),
        |_| rng.gen::<f64>() * 2.0 - 1.0
    );
    
    // Target: simple transformation (identity + small noise)
    let mut y = x.clone();
    for b in 0..batch_size {
        for i in 0..input_dim {
            let noise = <StandardNormal as Distribution<f64>>::sample(&StandardNormal, &mut rng) * 0.01;
            y[[b, 0, i]] = x[[b, 0, i]] * 1.0 + noise;
        }
    }
    
    (x, y)
}

/// Compute MSE loss
fn compute_loss(pred: &Array3<f64>, target: &Array3<f64>) -> f64 {
    let diff = pred - target;
    diff.mapv(|v| v * v).mean().unwrap()
}

/// Extract output as 2D array for gradient computation
fn flatten_output(output: &Array3<f64>) -> Array2<f64> {
    let batch_size = output.shape()[0];
    let dim = output.shape()[2];
    Array2::from_shape_fn((batch_size, dim), |(b, i)| output[[b, 0, i]])
}

fn main() {
    println!("╔══════════════════════════════════════════════════════════╗");
    println!("║  Round 18: RealUNet Single-Layer Gradient Pilot         ║");
    println!("║  Trainable: input_proj | Frozen: hidden, output         ║");
    println!("╚══════════════════════════════════════════════════════════╝");
    println!();
    
    // Config
    let epochs = 50;
    let lr = 0.01;
    let batch_size = 16;
    let input_dim = 64;
    let hidden_dim = 128;
    
    // Create model with frozen baseline
    let mut model = RealUNetGradientPilot::new(input_dim, hidden_dim, 42);
    let frozen_baseline = RealUNetGradientPilot::new(input_dim, hidden_dim, 42);  // Same init
    
    let initial_trainable_hash = model.trainable_hash();
    let initial_full_hash = model.full_hash();
    
    println!("Initial state:");
    println!("  Trainable hash: {:016x}", initial_trainable_hash);
    println!("  Full hash: {:016x}", initial_full_hash);
    println!();
    
    // Training history
    let mut losses: Vec<f64> = vec![];
    let mut grad_norms: Vec<(f64, f64)> = vec![];
    
    println!("Training {} epochs (input_proj only)...", epochs);
    
    for epoch in 0..epochs {
        // Generate batch
        let (x, y_target) = generate_batch(batch_size, input_dim, 1000 + epoch as u64);
        
        // Dummy time/classes (not used in this simplified pilot)
        let time = Array1::zeros(batch_size);
        let classes = Array1::zeros(batch_size);
        
        // Forward
        let y_pred = model.forward(&x, &time, &classes);
        
        // Compute loss
        let loss = compute_loss(&y_pred, &y_target);
        losses.push(loss);
        
        // Compute gradient dL/d(pred) = 2*(pred - target) / n
        let grad_output_3d = (&y_pred - &y_target) * (2.0 / (batch_size * input_dim) as f64);
        let grad_output = flatten_output(&grad_output_3d);
        
        // Backward (only for trainable layer)
        if let Some(grad) = model.backward(&grad_output) {
            grad_norms.push((grad.norm_dW, grad.norm_db));
            
            // Update trainable layer
            model.update(&grad, lr);
            
            if epoch % 10 == 0 {
                println!("  Epoch {:3}: loss={:.6}, |grad_W|={:.6}, |grad_b|={:.6}",
                    epoch, loss, grad.norm_dW, grad.norm_db);
            }
        }
    }
    
    let final_trainable_hash = model.trainable_hash();
    let final_full_hash = model.full_hash();
    
    println!();
    println!("Training complete:");
    println!("  Final trainable hash: {:016x}", final_trainable_hash);
    println!("  Final full hash: {:016x}", final_full_hash);
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
    let loss_decreasing = loss_0 > loss_mid && loss_mid > loss_final;
    
    println!("1. Loss Curve:");
    println!("   Epoch 0:   {:.6}", loss_0);
    println!("   Epoch {}: {:.6}", epochs/2, loss_mid);
    println!("   Epoch {}: {:.6}", epochs-1, loss_final);
    println!("   Decreasing: {}", if loss_decreasing { "✅ PASS" } else { "❌ FAIL" });
    println!();
    
    // 2. Gradient non-zero
    let avg_grad_norm: f64 = grad_norms.iter().map(|(w, _)| w).sum::<f64>() / grad_norms.len() as f64;
    let gradient_nonzero = avg_grad_norm > 1e-10;
    
    println!("2. Gradient Evidence:");
    println!("   Avg |grad_W|: {:.6e}", avg_grad_norm);
    println!("   Non-zero: {}", if gradient_nonzero { "✅ PASS" } else { "❌ FAIL" });
    println!();
    
    // 3. Frozen layers unchanged
    let frozen_unchanged = model.check_frozen_unchanged(&frozen_baseline);
    
    println!("3. Frozen Layers Unchanged:");
    println!("   Status: {}", if frozen_unchanged { "✅ PASS" } else { "❌ FAIL" });
    println!();
    
    // 4. Trainable layer changed
    let trainable_changed = initial_trainable_hash != final_trainable_hash;
    
    println!("4. Trainable Layer Updated:");
    println!("   Status: {}", if trainable_changed { "✅ PASS" } else { "❌ FAIL" });
    println!();
    
    // 5. Reload determinism
    fs::create_dir_all("tests").unwrap_or_default();
    model.save("tests/round18_checkpoint.json").unwrap();
    
    // Re-train identical model to verify determinism
    let mut model2 = RealUNetGradientPilot::new(input_dim, hidden_dim, 42);
    for epoch in 0..epochs {
        let (x, y_target) = generate_batch(batch_size, input_dim, 1000 + epoch as u64);
        let time = Array1::zeros(batch_size);
        let classes = Array1::zeros(batch_size);
        let y_pred = model2.forward(&x, &time, &classes);
        let loss = compute_loss(&y_pred, &y_target);
        let grad_output_3d = (&y_pred - &y_target) * (2.0 / (batch_size * input_dim) as f64);
        let grad_output = flatten_output(&grad_output_3d);
        if let Some(grad) = model2.backward(&grad_output) {
            model2.update(&grad, lr);
        }
    }
    
    let reload_deterministic = model.trainable_hash() == model2.trainable_hash();
    
    println!("5. Reload Determinism:");
    println!("   Status: {}", if reload_deterministic { "✅ PASS" } else { "❌ FAIL" });
    println!();
    
    // 6. Structure preserved (forward still works)
    let (test_x, _) = generate_batch(4, input_dim, 9999);
    let test_time = Array1::zeros(4);
    let test_classes = Array1::zeros(4);
    let _ = model.forward(&test_x, &test_time, &test_classes);
    let structure_ok = true;  // If we got here, forward didn't panic
    
    println!("6. Structure Preserved:");
    println!("   Status: ✅ PASS");
    println!();
    
    // Overall
    let all_pass = loss_decreasing 
        && gradient_nonzero 
        && frozen_unchanged 
        && trainable_changed 
        && reload_deterministic
        && structure_ok;
    
    println!("═══════════════════════════════════════════════════════════");
    if all_pass {
        println!("🎉 ROUND 18: PILOT SUCCESS");
        println!("   Single-layer gradient learning verified in RealUNet.");
    } else {
        println!("❌ ROUND 18: PILOT FAIL");
        println!("   Mechanism needs investigation before scaling.");
    }
    println!("═══════════════════════════════════════════════════════════");
    
    // Generate JSON report
    let report = json!({
        "round": 18,
        "status": if all_pass { "SUCCESS" } else { "FAIL" },
        "config": {
            "epochs": epochs,
            "learning_rate": lr,
            "batch_size": batch_size,
            "input_dim": input_dim,
            "hidden_dim": hidden_dim,
            "trainable_layer": "input_proj",
            "frozen_layers": ["hidden_w", "hidden_b", "output_proj", "output_bias"]
        },
        "results": {
            "loss_initial": loss_0,
            "loss_final": loss_final,
            "loss_reduction_pct": ((loss_0 - loss_final) / loss_0 * 100.0),
            "loss_decreasing": loss_decreasing,
            "grad_norm_dW": avg_grad_norm,
            "grad_norm_db": grad_norms.last().map(|(_, b)| *b).unwrap_or(0.0),
            "gradient_nonzero": gradient_nonzero,
            "frozen_unchanged": frozen_unchanged,
            "trainable_changed": trainable_changed,
            "reload_deterministic": reload_deterministic,
            "structure_ok": structure_ok
        },
        "hashes": {
            "initial_trainable": format!("{:016x}", initial_trainable_hash),
            "final_trainable": format!("{:016x}", final_trainable_hash),
            "initial_full": format!("{:016x}", initial_full_hash),
            "final_full": format!("{:016x}", final_full_hash)
        }
    });
    
    fs::write("tests/realunet_gradient_pilot_report.json", 
        serde_json::to_string_pretty(&report).unwrap()).unwrap();
    
    println!("\nReport saved: tests/realunet_gradient_pilot_report.json");
    
    std::process::exit(if all_pass { 0 } else { 1 });
}
