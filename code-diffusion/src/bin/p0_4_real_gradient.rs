//! P0-4 Verification with Real Gradient Training

use code_diffusion::diffusion::{Diffusion, DiffusionConfig};
use code_diffusion::models::realunet_full::RealUNetFull;
use code_diffusion::training::real_gradient::RealGradientTrainer;
use ndarray::Array3;
use rand::distributions::Distribution;
use rand::thread_rng;
use rand_distr::StandardNormal;

fn main() {
    println!("========================================");
    println!("P0-4 Real Gradient Verification");
    println!("========================================\n");
    
    // Setup - RealUNetFull expects (batch, 1, input_dim)
    let input_dim = 64;
    let hidden_dim = 128;
    let output_dim = 64;
    
    let diffusion = Diffusion::new(DiffusionConfig::default());
    let unet = RealUNetFull::new(input_dim, hidden_dim, output_dim, 42);
    let mut trainer = RealGradientTrainer::new(diffusion, unet, 0.001);
    
    // Generate synthetic training data with correct shape
    println!("[Setup] Generating synthetic training data...");
    let batch_size = 4;
    let mut data = vec![];
    for _ in 0..100 {
        // Shape: (batch, 1, input_dim)
        let x: Array3<f64> = Array3::from_shape_fn((batch_size, 1, input_dim), |_| {
            StandardNormal.sample(&mut thread_rng())
        });
        data.push(x);
    }
    println!("  Generated {} samples (shape: {:?})\n", data.len(), data[0].shape());
    
    // Train for multiple epochs
    println!("[Training] Real gradient training...");
    let initial_loss = trainer.train_epoch(&data);
    println!("  Epoch 0 (initial): loss = {:.6}", initial_loss);
    
    let mut losses = vec![initial_loss];
    for epoch in 1..=20 {
        let loss = trainer.train_epoch(&data);
        losses.push(loss);
        if epoch % 5 == 0 {
            println!("  Epoch {}: loss = {:.6}", epoch, loss);
        }
    }
    
    // P0-4 Metrics
    println!("\n========================================");
    println!("P0-4 Metrics");
    println!("========================================");
    
    let initial = losses[0];
    let final_loss = losses[losses.len() - 1];
    let reduction = (initial - final_loss) / initial * 100.0;
    
    println!("Initial loss:  {:.6}", initial);
    println!("Final loss:    {:.6}", final_loss);
    println!("Reduction:     {:.1}%", reduction);
    
    let decreasing = losses.windows(2).all(|w| w[0] >= w[1] * 0.99);
    println!("Loss trend:    {}", if decreasing { "✅ Decreasing" } else { "⚠️  Not monotonic" });
    
    let p04_pass = reduction > 5.0;
    println!("\nP0-4 Result:   {}", if p04_pass { "✅ PASS" } else { "❌ FAIL" });
    
    if p04_pass {
        println!("\n🎯 Real gradient training WORKS!");
        println!("   Loss reduced by {:.1}%", reduction);
        println!("   P0-4 UNBLOCKED!");
    } else {
        println!("\n⚠️  Loss reduction: {:.1}% (need >5%)", reduction);
    }
    
    println!("\n========================================");
}
