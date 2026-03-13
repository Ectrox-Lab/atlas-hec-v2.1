//! Test 1: Single-step update - parameters must change after backward+update

use code_diffusion::diffusion::{Diffusion, DiffusionConfig};
use code_diffusion::models::realunet_full::RealUNetFull;
use ndarray::Array3;
use rand::distributions::Distribution;
use rand::thread_rng;
use rand_distr::StandardNormal;

#[test]
fn test_single_step_update() {
    let diffusion = Diffusion::new(DiffusionConfig::default());
    let mut unet = RealUNetFull::new(64, 128, 64, 42);
    
    // Record initial hash
    let hash_before = unet.param_hash();
    
    // Single training step
    let mut rng = thread_rng();
    let x_start: Array3<f64> = Array3::from_shape_fn((4, 1, 64), |_| {
        StandardNormal.sample(&mut rng)
    });
    let target_noise: Array3<f64> = Array3::from_shape_fn((4, 1, 64), |_| {
        StandardNormal.sample(&mut rng)
    });
    
    let x_noisy = diffusion.q_sample(&x_start, 100, Some(&target_noise));
    let noise_pred = unet.forward(&x_noisy);
    
    // Compute loss and gradient
    let diff = &noise_pred - &target_noise;
    let n = diff.len() as f64;
    let grad_output = diff.mapv(|v| 2.0 * v / n);
    let gradients = unet.backward(&grad_output);
    
    // Update
    unet.update(&gradients, 0.001);
    
    // Verify parameters changed
    let hash_after = unet.param_hash();
    assert_ne!(hash_before, hash_after, "Parameters must change after update");
    
    println!("✅ Single-step update test: PASS");
    println!("   Hash before: {:x}", hash_before);
    println!("   Hash after:  {:x}", hash_after);
}
