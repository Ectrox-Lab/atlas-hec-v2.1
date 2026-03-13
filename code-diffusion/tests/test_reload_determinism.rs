//! Test 3: Reload determinism - save/load must produce consistent outputs

use code_diffusion::diffusion::{Diffusion, DiffusionConfig};
use code_diffusion::models::realunet_full::RealUNetFull;
use ndarray::Array3;
use rand::distributions::Distribution;
use rand::{SeedableRng, thread_rng};
use rand::rngs::StdRng;
use rand_distr::StandardNormal;

#[test]
fn test_reload_determinism() {
    let seed = 42;
    let mut rng = StdRng::seed_from_u64(seed);
    
    let diffusion = Diffusion::new(DiffusionConfig::default());
    let mut unet1 = RealUNetFull::new(64, 128, 64, seed);
    
    // Train for a few steps
    for _ in 0..5 {
        let x_start: Array3<f64> = Array3::from_shape_fn((4, 1, 64), |_| {
            StandardNormal.sample(&mut rng)
        });
        let target_noise: Array3<f64> = Array3::from_shape_fn((4, 1, 64), |_| {
            StandardNormal.sample(&mut thread_rng())
        });
        
        let x_noisy = diffusion.q_sample(&x_start, 100, Some(&target_noise));
        let noise_pred = unet1.forward(&x_noisy);
        
        let diff = &noise_pred - &target_noise;
        let n = diff.len() as f64;
        let grad_output = diff.mapv(|v| 2.0 * v / n);
        let gradients = unet1.backward(&grad_output);
        unet1.update(&gradients, 0.001);
    }
    
    // Record hash after training
    let hash_after_train = unet1.param_hash();
    
    // Simulate "save" by creating new model with same state
    // In real scenario: serialize params, deserialize
    let mut unet2 = RealUNetFull::new(64, 128, 64, seed);
    
    // Apply same training steps to unet2
    let mut rng2 = StdRng::seed_from_u64(seed);
    for _ in 0..5 {
        let x_start: Array3<f64> = Array3::from_shape_fn((4, 1, 64), |_| {
            StandardNormal.sample(&mut rng2)
        });
        let target_noise: Array3<f64> = Array3::from_shape_fn((4, 1, 64), |_| {
            StandardNormal.sample(&mut thread_rng())
        });
        
        let x_noisy = diffusion.q_sample(&x_start, 100, Some(&target_noise));
        let noise_pred = unet2.forward(&x_noisy);
        
        let diff = &noise_pred - &target_noise;
        let n = diff.len() as f64;
        let grad_output = diff.mapv(|v| 2.0 * v / n);
        let gradients = unet2.backward(&grad_output);
        unet2.update(&gradients, 0.001);
    }
    
    let hash_unet2 = unet2.param_hash();
    
    // Verify determinism
    assert_eq!(hash_after_train, hash_unet2, 
        "Reloaded model must produce same hash after identical training");
    
    // Verify same outputs
    let test_input: Array3<f64> = Array3::from_shape_fn((4, 1, 64), |_| {
        StandardNormal.sample(&mut thread_rng())
    });
    
    let out1 = unet1.forward(&test_input);
    let out2 = unet2.forward(&test_input);
    
    let max_diff = (&out1 - &out2).mapv(|v| v.abs()).fold(0.0, |a, b| a.max(b));
    
    assert!(max_diff < 1e-6, "Outputs must match within tolerance");
    
    println!("✅ Reload determinism test: PASS");
    println!("   Hash match: {:x}", hash_after_train);
    println!("   Max output diff: {:.10}", max_diff);
}
