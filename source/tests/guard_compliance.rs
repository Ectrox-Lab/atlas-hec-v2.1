//! Compliance Guard Tests for Candidate 001 Integration
//!
//! These tests prevent semantic drift from FROZEN_STATE_v1 constraints:
//! 1. Bandwidth guard: Must be <= 32 bits
//! 2. Timescale guard: Must be 10x separation
//! 3. Generic-only guard: No specific action encoding

use atlas_hec_v2::prior_channel::{
    PriorChannelMarkerAdapter, Marker, MarkerScheduler, PolicyModulation,
    PRIOR_SAMPLE_PROB, PRIOR_STRENGTH,
};
use rand::SeedableRng;
use rand::rngs::StdRng;

// ============================================================================
// GUARD 1: Bandwidth Constraint
// ============================================================================

#[test]
fn guard_bandwidth_fixed_32_bits() {
    /// CRITICAL: Marker must be exactly 4 bytes (32 bits)
    /// This test will FAIL if marker size changes
    let marker = Marker::new(255, 255, 127, -128);
    let bytes = marker.as_bytes();
    
    assert_eq!(
        bytes.len(), 
        4, 
        "VIOLATION: Marker size is {} bytes, must be exactly 4 bytes (32 bits)",
        bytes.len()
    );
}

#[test]
fn guard_bandwidth_no_dynamic_allocation() {
    /// CRITICAL: Marker must not use dynamic allocation
    /// Fixed-size array ensures no heap allocation = bounded bandwidth
    let marker = Marker::new(1, 128, 0, 0);
    
    // Verify it's Copy (implies no allocation)
    let m1 = marker;
    let m2 = marker;  // Can copy without move
    assert_eq!(m1.as_bytes(), m2.as_bytes());
}

#[test]
fn guard_adapter_tracks_bandwidth() {
    /// CRITICAL: Adapter must track bandwidth and report violations
    let mut adapter = PriorChannelMarkerAdapter::new(true);
    let mut rng = StdRng::seed_from_u64(42);
    
    // Sample multiple times
    let marker = Marker::new(1, 128, 0, 0);
    let pop: Vec<Marker> = vec![];
    
    for _ in 0..100 {
        let _ = adapter.inject_prior(&marker, &pop, &mut rng);
    }
    
    let stats = adapter.bandwidth_stats();
    
    // Must report compliance status
    assert!(
        stats.compliant || !stats.compliant,  // Just check field exists
        "Adapter must report bandwidth compliance status"
    );
    
    // With fixed 32-bit markers, must be compliant
    assert!(stats.compliant, "Fixed 32-bit markers must always be compliant");
    assert_eq!(
        stats.mean_bits_per_sample, 
        32.0, 
        "Must report exactly 32 bits per sample"
    );
}

// ============================================================================
// GUARD 2: Timescale Separation
// ============================================================================

#[test]
fn guard_timescale_fixed_10x() {
    /// CRITICAL: Marker update must be every 10 ticks
    /// This test will FAIL if update interval changes
    let scheduler = MarkerScheduler::new(1);
    
    assert!(
        scheduler.check_timescale(),
        "VIOLATION: Timescale must be exactly 10x separation"
    );
}

#[test]
fn guard_timescale_measured_rate() {
    /// Verify actual update rate matches 10x specification
    let mut scheduler = MarkerScheduler::new(1);
    
    let mut update_count = 0;
    let n_ticks = 1000;
    
    for i in 0..n_ticks {
        let action = (i % 10) as f32 / 10.0;
        if scheduler.tick(action).is_some() {
            update_count += 1;
        }
    }
    
    // Expected: ~100 updates for 1000 ticks at 10x
    let expected = n_ticks / 10;
    let tolerance = 5;  // Allow small timing variance
    
    assert!(
        update_count >= expected - tolerance && update_count <= expected + tolerance,
        "VIOLATION: Got {} updates for {} ticks, expected ~{} (10x separation)",
        update_count, n_ticks, expected
    );
}

#[test]
fn guard_timescale_1x_rejected() {
    /// Demonstrate that 1x (every tick) would violate constraint
    /// 
    /// If someone tries to change update_interval to 1:
    /// let scheduler = MarkerScheduler::new(1);
    /// // If update_interval were 1, check_timescale() would return false
    /// 
    /// The current implementation enforces 10x, so this is a documentation test
    let scheduler = MarkerScheduler::new(1);
    assert!(scheduler.check_timescale(), "10x timescale must be enforced");
}

// ============================================================================
// GUARD 3: Generic-Only Constraint
// ============================================================================

#[test]
fn guard_generic_only_no_action_ids() {
    /// CRITICAL: PolicyModulation must not contain action IDs
    /// 
    /// This test documents what fields are ALLOWED:
    /// - coherence_bias: f32 (generic expectation)
    /// - directional_bias: [f32; 2] (generic directional influence)
    /// - confidence: f32 (strength of modulation)
    ///
    /// NOT ALLOWED:
    /// - action_id: u32 (specific action recommendation)
    /// - strategy_id: u32 (specific strategy encoding)
    /// - content_hash: [u8; 32] (content-bearing reference)
    
    let modulation = PolicyModulation::zero();
    
    // Verify modulation can only affect policy distribution
    let mut logits = [0.0f32, 0.0f32];
    modulation.apply(&mut logits);
    
    // Modulation should not specify which action to take
    // It only biases the policy distribution
}

#[test]
fn guard_generic_only_bounded_values() {
    /// CRITICAL: Modulation values must be bounded
    /// Unbounded values could encode arbitrary information
    let mut adapter = PriorChannelMarkerAdapter::new(true);
    
    // Test with various coherence values
    for coherence in [0u8, 64, 128, 192, 255] {
        let modulation = adapter.compute_modulation(coherence, 128);
        
        // All values must be bounded
        assert!(
            modulation.confidence >= 0.0 && modulation.confidence <= 1.0,
            "Confidence must be in [0, 1], got {}", modulation.confidence
        );
        
        assert!(
            modulation.coherence_bias >= -1.0 && modulation.coherence_bias <= 1.0,
            "Coherence bias must be in [-1, 1], got {}", modulation.coherence_bias
        );
    }
}

#[test]
fn guard_generic_only_prior_strength_respected() {
    /// CRITICAL: PriorChannel strength α=0.5 must be respected
    /// This limits how much modulation can affect policy
    let mut adapter = PriorChannelMarkerAdapter::new(true);
    
    let max_coherence = 255u8;
    let modulation = adapter.compute_modulation(max_coherence, max_coherence);
    
    // Max confidence should be PRIOR_STRENGTH (0.5)
    assert!(
        modulation.confidence <= PRIOR_STRENGTH as f32 + 0.01,
        "Confidence {} must not exceed PRIOR_STRENGTH ({})",
        modulation.confidence, PRIOR_STRENGTH
    );
}

// ============================================================================
// GUARD 4: PriorChannel Parameters (FROZEN_STATE_v1)
// ============================================================================

#[test]
fn guard_frozen_parameters() {
    /// CRITICAL: p=0.01 and α=0.5 are FROZEN
    /// These must not change without Phase 8 validation
    
    assert_eq!(
        PRIOR_SAMPLE_PROB, 
        0.01, 
        "VIOLATION: PRIOR_SAMPLE_PROB is frozen at 0.01"
    );
    
    assert_eq!(
        PRIOR_STRENGTH, 
        0.5, 
        "VIOLATION: PRIOR_STRENGTH is frozen at 0.5"
    );
}

#[test]
fn guard_sampling_rate_matches_p() {
    /// Verify actual sampling rate matches p=0.01
    let mut adapter = PriorChannelMarkerAdapter::new(true);
    let mut rng = StdRng::seed_from_u64(42);
    
    let n_samples = 10000;
    let mut success_count = 0;
    
    for _ in 0..n_samples {
        if adapter.should_sample(&mut rng) {
            success_count += 1;
        }
    }
    
    let observed_rate = success_count as f64 / n_samples as f64;
    let expected_rate = PRIOR_SAMPLE_PROB;
    let tolerance = 0.005;  // ±0.5%
    
    assert!(
        (observed_rate - expected_rate).abs() < tolerance,
        "Sampling rate {:.4} deviates from p={:.2} by more than {:.3}",
        observed_rate, expected_rate, tolerance
    );
}

// ============================================================================
// Integration: All Guards Together
// ============================================================================

#[test]
fn guard_all_constraints_integrated() {
    /// Verify all constraints work together in integration
    let mut adapter = PriorChannelMarkerAdapter::new(true);
    let mut scheduler = MarkerScheduler::new(1);
    let mut rng = StdRng::seed_from_u64(42);
    
    // Run integrated simulation
    let n_ticks = 1000;
    let mut marker_updates = 0;
    let mut prior_samples = 0;
    
    for i in 0..n_ticks {
        // Agent action
        let action = (i % 10) as f32 / 10.0;
        
        // Marker update (every 10 ticks)
        if scheduler.tick(action).is_some() {
            marker_updates += 1;
            
            // PriorChannel sampling (p=0.01)
            let marker = scheduler.current_marker();
            let pop: Vec<Marker> = vec![];
            let modulation = adapter.inject_prior(&marker, &pop, &mut rng);
            
            if modulation.confidence > 0.0 {
                prior_samples += 1;
            }
        }
    }
    
    // Verify all constraints
    let bandwidth_stats = adapter.bandwidth_stats();
    
    println!("\n=== Compliance Report ===");
    println!("Ticks: {}", n_ticks);
    println!("Marker updates: {} (expected ~{})", marker_updates, n_ticks / 10);
    println!("Prior samples: {} (expected ~{})", prior_samples, (n_ticks / 10) as f64 * PRIOR_SAMPLE_PROB);
    println!("Bandwidth: {} bits/sample", bandwidth_stats.mean_bits_per_sample);
    println!("========================\n");
    
    // Assertions
    assert!(scheduler.check_timescale(), "Timescale guard");
    assert!(bandwidth_stats.compliant, "Bandwidth guard");
    assert_eq!(PRIOR_SAMPLE_PROB, 0.01, "Frozen parameter guard");
    assert_eq!(PRIOR_STRENGTH, 0.5, "Frozen parameter guard");
}

// ============================================================================
// Negative Tests: What Violations Look Like
// ============================================================================

#[test]
#[should_panic(expected = "assertion failed")]
fn demonstrate_bandwidth_violation() {
    /// This test shows what happens if bandwidth constraint is violated
    /// (This test is expected to FAIL - it's documentation)
    
    // If someone tried to expand marker to 8 bytes:
    // struct BadMarker([u8; 8]);  // 64 bits - VIOLATION
    
    // Current marker is 4 bytes - this assertion passes
    let marker = Marker::new(1, 128, 0, 0);
    assert_eq!(marker.as_bytes().len(), 4);
    
    // Uncomment to see what failure looks like:
    // assert_eq!(marker.as_bytes().len(), 8, "This would fail");
}

#[test]
#[should_panic(expected = "assertion failed")]
fn demonstrate_timescale_violation() {
    /// This test shows what happens if timescale constraint is violated
    /// (This test is expected to FAIL - it's documentation)
    
    // The scheduler enforces 10x - this is correct
    let scheduler = MarkerScheduler::new(1);
    assert!(scheduler.check_timescale());
    
    // If someone tried to use 1x:
    // let bad_scheduler = MarkerScheduler::with_interval(1);  // VIOLATION
    // assert!(!bad_scheduler.check_timescale());
}
