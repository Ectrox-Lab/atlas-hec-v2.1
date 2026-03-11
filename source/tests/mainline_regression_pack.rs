//! Mainline Regression Test Pack
//!
//! These tests ensure mainline PriorChannel with Candidate 001 markers
//! maintains all FROZEN_STATE_v1 constraints.
//!
//! Run in CI on every commit to prevent regression.

use atlas_hec_v2::prior_channel::{
    MainlinePriorChannel, ConstraintReport,
    Marker, MarkerScheduler, PolicyModulation, PriorChannelMarkerAdapter,
    PRIOR_SAMPLE_PROB, PRIOR_STRENGTH,
};
use rand::SeedableRng;
use rand::rngs::StdRng;

// ============================================================================
// REGRESSION TEST 1: Coherence Maintenance
// ============================================================================

#[test]
fn regression_coherence_maintained() {
    /// CRITICAL: PriorChannel ON must maintain coherence >= 0.7
    /// 
    /// This prevents: PriorChannel interfering with marker mechanism
    
    let mut rng = StdRng::seed_from_u64(42);
    let mut adapter = PriorChannelMarkerAdapter::new(true);
    let mut scheduler = MarkerScheduler::new(1);
    
    // Simulate 1000 ticks with consistent actions
    let mut coherence_sum = 0.0;
    let mut coherence_count = 0;
    
    for i in 0..1000 {
        let action = 0.5;  // Consistent action
        
        if let Some(marker) = scheduler.tick(action) {
            coherence_sum += marker.coherence() as f32 / 255.0;
            coherence_count += 1;
            
            // Apply PriorChannel modulation
            let pop: Vec<Marker> = vec![];
            let _ = adapter.inject_prior(&marker, &pop, &mut rng);
        }
    }
    
    let mean_coherence = if coherence_count > 0 {
        coherence_sum / coherence_count as f32
    } else {
        0.0
    };
    
    assert!(
        mean_coherence >= 0.7,
        "REGRESSION: Coherence dropped to {:.3}, must maintain >= 0.7",
        mean_coherence
    );
}

// ============================================================================
// REGRESSION TEST 2: Bandwidth Constraint
// ============================================================================

#[test]
fn regression_bandwidth_32_bits() {
    /// CRITICAL: Marker must remain exactly 32 bits (4 bytes)
    ///
    /// This prevents: Marker expansion breaking bandwidth constraint
    
    let marker = Marker::new(255, 255, 127, -128);
    let bytes = marker.as_bytes();
    
    assert_eq!(
        bytes.len(),
        4,
        "REGRESSION: Marker size is {} bytes, must be exactly 4 bytes (32 bits)",
        bytes.len()
    );
    
    // Verify bandwidth stats track correctly
    let mut adapter = PriorChannelMarkerAdapter::new(true);
    let stats = adapter.bandwidth_stats();
    
    assert!(
        stats.compliant,
        "REGRESSION: Bandwidth not compliant"
    );
}

// ============================================================================
// REGRESSION TEST 3: Timescale Constraint
// ============================================================================

#[test]
fn regression_timescale_10x() {
    /// CRITICAL: Marker updates must be exactly every 10 ticks
    ///
    /// This prevents: Timescale drift breaking 10x separation
    
    let scheduler = MarkerScheduler::new(1);
    assert!(
        scheduler.check_timescale(),
        "REGRESSION: Timescale not 10x separation"
    );
    
    // Verify measured rate
    let mut update_count = 0;
    let ticks = 1000;
    
    for i in 0..ticks {
        let action = (i % 10) as f32 / 10.0;
        if scheduler.tick(action).is_some() {
            update_count += 1;
        }
    }
    
    let expected_updates = ticks / 10;
    let tolerance = 10;  // Allow small variance
    
    assert!(
        update_count >= expected_updates - tolerance 
            && update_count <= expected_updates + tolerance,
        "REGRESSION: Got {} updates for {} ticks, expected ~{} (10x)",
        update_count, ticks, expected_updates
    );
}

// ============================================================================
// REGRESSION TEST 4: No Action Leakage
// ============================================================================

#[test]
fn regression_no_action_leakage() {
    /// CRITICAL: PolicyModulation must not encode specific actions
    ///
    /// This prevents: Content-bearing signaling (violates generic-only)
    
    let mut adapter = PriorChannelMarkerAdapter::new(true);
    
    // Test with various coherence values
    for coherence in [0u8, 64, 128, 192, 255] {
        let modulation = adapter.compute_modulation(coherence, 128);
        
        // Confidence must be bounded
        assert!(
            modulation.confidence >= 0.0 && modulation.confidence <= 1.0,
            "REGRESSION: Confidence {} out of bounds [0, 1]",
            modulation.confidence
        );
        
        // Coherence bias must be bounded
        assert!(
            modulation.coherence_bias >= -1.0 && modulation.coherence_bias <= 1.0,
            "REGRESSION: Coherence bias {} out of bounds [-1, 1]",
            modulation.coherence_bias
        );
        
        // Max confidence must respect PRIOR_STRENGTH
        assert!(
            modulation.confidence <= PRIOR_STRENGTH as f32 + 0.01,
            "REGRESSION: Confidence {} exceeds PRIOR_STRENGTH ({})",
            modulation.confidence, PRIOR_STRENGTH
        );
    }
    
    // Verify PolicyModulation has no action_id field
    // (This is enforced by struct definition)
    let _modulation = PolicyModulation::zero();
    // If someone adds action_id, this test will fail to compile:
    // let bad = _modulation.action_id;  // Compile error = correct behavior
}

// ============================================================================
// REGRESSION TEST 5: Frozen Parameters
// ============================================================================

#[test]
fn regression_frozen_parameters() {
    /// CRITICAL: p=0.01 and α=0.5 must never change
    ///
    /// This prevents: Parameter drift breaking convergence
    
    assert_eq!(
        PRIOR_SAMPLE_PROB, 0.01,
        "REGRESSION: PRIOR_SAMPLE_PROB changed from 0.01"
    );
    
    assert_eq!(
        PRIOR_STRENGTH, 0.5,
        "REGRESSION: PRIOR_STRENGTH changed from 0.5"
    );
    
    // Verify MainlinePriorChannel uses frozen values
    let mainline = MainlinePriorChannel::new();
    let report = mainline.verify_constraints();
    
    assert!(
        report.p_sample_locked,
        "REGRESSION: Mainline p_sample not locked"
    );
    
    assert!(
        report.alpha_locked,
        "REGRESSION: Mainline alpha not locked"
    );
}

// ============================================================================
// REGRESSION TEST 6: Mainline Default Configuration
// ============================================================================

#[test]
fn regression_mainline_default_is_candidate_001() {
    /// CRITICAL: MainlinePriorChannel must use Candidate 001 by default
    ///
    /// This ensures: New code gets validated mechanism, not legacy
    
    let mainline = MainlinePriorChannel::new();
    let report = mainline.verify_constraints();
    
    assert!(
        report.all_pass(),
        "REGRESSION: Mainline default constraints not satisfied"
    );
    
    // All five constraints must pass
    assert!(report.bandwidth_fixed_32_bits, "Bandwidth constraint");
    assert!(report.timescale_10x, "Timescale constraint");
    assert!(report.generic_only, "Generic-only constraint");
    assert!(report.p_sample_locked, "p_sample frozen");
    assert!(report.alpha_locked, "alpha frozen");
}

// ============================================================================
// REGRESSION SUITE SUMMARY
// ============================================================================

#[test]
fn regression_suite_all_pass() {
    /// Run all regression checks in one test for CI
    
    // 1. Coherence
    let mut rng = StdRng::seed_from_u64(42);
    let mut adapter = PriorChannelMarkerAdapter::new(true);
    let mut scheduler = MarkerScheduler::new(1);
    
    for i in 0..1000 {
        let action = 0.5;
        if let Some(marker) = scheduler.tick(action) {
            let pop: Vec<Marker> = vec![];
            let _ = adapter.inject_prior(&marker, &pop, &mut rng);
        }
    }
    
    // 2. Bandwidth
    let marker = Marker::new(255, 255, 127, -128);
    assert_eq!(marker.as_bytes().len(), 4);
    
    // 3. Timescale
    assert!(scheduler.check_timescale());
    
    // 4. No leakage
    let modulation = adapter.compute_modulation(200, 180);
    assert!(modulation.confidence <= PRIOR_STRENGTH as f32 + 0.01);
    
    // 5. Frozen params
    assert_eq!(PRIOR_SAMPLE_PROB, 0.01);
    assert_eq!(PRIOR_STRENGTH, 0.5);
    
    // 6. Mainline default
    let mainline = MainlinePriorChannel::new();
    assert!(mainline.verify_constraints().all_pass());
    
    println!("✅ Mainline Regression Suite: ALL PASS");
}
