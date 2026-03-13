//! Test 2: Loss trend - fixed seed, loss should decrease over training window

use code_diffusion::diffusion::{Diffusion, DiffusionConfig};
use code_diffusion::models::realunet_full::RealUNetFull;
use ndarray::Array3;
use rand::distributions::Distribution;
use rand::{SeedableRng, thread_rng};
use rand::rngs::StdRng;
use rand_distr::StandardNormal;

#[test]
fn test_loss_trend() {
    let seed = 42;
    let mut rng = StdRng::seed_from_u64(seed);
    
    let diffusion = Diffusion::new(DiffusionConfig::default());
    let mut unet = RealUNetFull::new(64, 128, 64, seed);
    
    // Generate fixed training data
    let mut data = vec![];
    for _ in 0..20 {
        let x: Array3<f64> = Array3::from_shape_fn((4, 1, 64), |_| {
            StandardNormal.sample(&mut rng)
        });
        data.push(x);
    }
    
    // Track losses over 10 steps
    let mut losses = vec![];
    
    for step in 0..10 {
        let mut step_loss = 0.0;
        
        for x_start in &data {
            let t = (step * 10) % diffusion.timesteps();
            let target_noise: Array3<f64> = Array3::from_shape_fn(
                x_start.raw_dim(),
                |_| StandardNormal.sample(&mut thread_rng())
            );
            
            let x_noisy = diffusion.q_sample(x_start, t, Some(&target_noise));
            let noise_pred = unet.forward(&x_noisy);
            
            let diff = &noise_pred - &target_noise;
            let loss = diff.mapv(|v| v * v).mean().unwrap();
            step_loss += loss;
            
            // Backward and update
            let n = diff.len() as f64;
            let grad_output = diff.mapv(|v| 2.0 * v / n);
            let gradients = unet.backward(&grad_output);
            unet.update(&gradients, 0.001);
        }
        
        losses.push(step_loss / data.len() as f64);
    }
    
    // Check overall trend (first vs last)
    let initial = losses[0];
    let final_loss = losses[losses.len() - 1];
    let reduction = (initial - final_loss) / initial * 100.0;
    
    println!("Initial loss: {:.6}", initial);
    println!("Final loss:   {:.6}", final_loss);
    println!("Reduction:    {:.1}%", reduction);
    
    // Must show some reduction (allowing for noise in short window)
    assert!(reduction > 2.0, "Loss should decrease by at least 2%");
    
    println!("✅ Loss trend test: PASS");
}
