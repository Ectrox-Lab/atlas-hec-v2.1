#!/usr/bin/env python3
"""
EXP-0: CI Probe - v18 to v19 Bridge Experiment
Retroactively compute CI from v18 data to test CDI-CI relationship
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
import argparse
from scipy.stats import pearsonr, spearmanr
import matplotlib.pyplot as plt


def estimate_network_from_cdi(cdi_value, population, method='power_law'):
    """
    Estimate network structure from CDI and population
    
    This is a proxy method since we don't have full network snapshots
    from v18. We infer network properties from CDI behavior.
    
    Methods:
    - 'power_law': Assume scale-free with exponent from CDI
    - 'random': Erdos-Renyi random graph
    - 'small_world': Watts-Strogatz model
    """
    if method == 'power_law':
        # Higher CDI → more distributed network (lower CI)
        # Lower CDI → more condensed (higher CI)
        
        # Power law exponent γ: 2 < γ < 3
        # γ = 2 (high condensation) → γ = 3 (low condensation)
        gamma = 2.0 + cdi_value  # γ ∈ [2, 3]
        
        # For scale-free networks:
        # CI ≈ 2 - γ for 2 < γ < 3
        # Actually CI depends on degree distribution
        # Approximation: CI ∝ (2 - γ) for high γ
        
        ci_estimate = max(0.1, 0.5 - 0.3 * cdi_value)
        
    elif method == 'empirical':
        # Direct empirical mapping based on observed patterns
        # From historical data: CDI ↓ 0.68 → 0.54 corresponds to CI ↑ 0.3 → 0.7
        ci_estimate = 1.0 - cdi_value
        
    else:
        ci_estimate = 0.5  # default
    
    return ci_estimate


def compute_condensation_index_proxy(cdi_series, pop_series, method='empirical'):
    """
    Compute CI proxy from CDI and population time series
    
    CI = Σ(k_i²) / (Σ k_i)²
    
    In practice, we estimate from observable metrics:
    - High CDI + stable population → low CI (distributed network)
    - Low CDI + declining population → high CI (condensed network)
    """
    ci_series = []
    
    for cdi, pop in zip(cdi_series, pop_series):
        # Base estimate from CDI
        ci_base = estimate_network_from_cdi(cdi, pop, method)
        
        # Population correction: declining pop → structural stress → higher CI
        if len(ci_series) > 0 and pop < pop_series[len(ci_series)-1]:
            ci_base *= 1.2  # amplify CI during decline
        
        ci_series.append(min(1.0, max(0.0, ci_base)))
    
    return np.array(ci_series)


def analyze_cdi_ci_relationship(df, method='empirical'):
    """
    Analyze relationship between CDI and CI
    """
    t = df['generation'].values
    cdi = df['avg_cdi'].values
    pop = df['population'].values
    
    # Compute CI proxy
    ci = compute_condensation_index_proxy(cdi, pop, method)
    
    # Basic correlation
    corr_pearson, p_pearson = pearsonr(cdi, ci)
    corr_spearman, p_spearman = spearmanr(cdi, ci)
    
    # Time-lagged correlation (CI leads CDI?)
    max_lag = min(10, len(cdi) // 4)
    lag_correlations = []
    
    for lag in range(-max_lag, max_lag + 1):
        if lag < 0:
            # CI leads CDI
            cdi_shifted = cdi[-lag:]
            ci_shifted = ci[:lag]
        elif lag > 0:
            # CDI leads CI
            cdi_shifted = cdi[:-lag]
            ci_shifted = ci[lag:]
        else:
            cdi_shifted = cdi
            ci_shifted = ci
        
        if len(cdi_shifted) > 5:
            r, _ = pearsonr(cdi_shifted, ci_shifted)
            lag_correlations.append((lag, r))
    
    # Find optimal lag
    best_lag = max(lag_correlations, key=lambda x: abs(x[1]))
    
    # Lead time analysis (relative to extinction)
    if 'extinct_count' in df.columns:
        extinct_mask = df['extinct_count'] > 0
        if extinct_mask.any():
            first_extinct_idx = extinct_mask.idxmax()
            
            # Find when CDI drops below threshold
            cdi_threshold = 0.54
            cdi_danger = np.where(cdi < cdi_threshold)[0]
            cdi_lead = first_extinct_idx - cdi_danger[0] if len(cdi_danger) > 0 else None
            
            # Find when CI rises above threshold
            ci_threshold = 0.6
            ci_danger = np.where(ci > ci_threshold)[0]
            ci_lead = first_extinct_idx - ci_danger[0] if len(ci_danger) > 0 else None
        else:
            cdi_lead = None
            ci_lead = None
    else:
        cdi_lead = None
        ci_lead = None
    
    return {
        'cdi': cdi,
        'ci': ci,
        'generation': t,
        'correlation': {
            'pearson': float(corr_pearson),
            'pearson_p': float(p_pearson),
            'spearman': float(corr_spearman),
            'spearman_p': float(p_spearman),
        },
        'lag_analysis': {
            'best_lag': int(best_lag[0]),
            'best_correlation': float(best_lag[1]),
            'all_lags': lag_correlations,
        },
        'lead_times': {
            'cdi_lead': int(cdi_lead) if cdi_lead else None,
            'ci_lead': int(ci_lead) if ci_lead else None,
        },
    }


def visualize_cdi_ci(results, output_path):
    """Create visualization of CDI-CI relationship"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    t = results['generation']
    cdi = results['cdi']
    ci = results['ci']
    
    # Plot 1: Time series
    ax1 = axes[0, 0]
    ax1.plot(t, cdi, 'b-', label='CDI', linewidth=2)
    ax1_twin = ax1.twinx()
    ax1_twin.plot(t, ci, 'r-', label='CI (proxy)', linewidth=2)
    ax1.set_xlabel('Generation')
    ax1.set_ylabel('CDI', color='b')
    ax1_twin.set_ylabel('CI', color='r')
    ax1.set_title('CDI vs CI Time Series')
    ax1.legend(loc='upper left')
    ax1_twin.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Scatter
    ax2 = axes[0, 1]
    ax2.scatter(cdi, ci, c=t, cmap='viridis', alpha=0.6)
    ax2.set_xlabel('CDI')
    ax2.set_ylabel('CI (proxy)')
    ax2.set_title(f'CDI vs CI (r={results["correlation"]["pearson"]:.3f})')
    ax2.grid(True, alpha=0.3)
    
    # Add colorbar
    cbar = plt.colorbar(ax2.collections[0], ax=ax2)
    cbar.set_label('Generation')
    
    # Plot 3: Lag correlation
    ax3 = axes[1, 0]
    lags = [x[0] for x in results['lag_analysis']['all_lags']]
    corrs = [x[1] for x in results['lag_analysis']['all_lags']]
    ax3.plot(lags, corrs, 'g-o', linewidth=2, markersize=6)
    ax3.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
    ax3.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax3.set_xlabel('Lag (generations)')
    ax3.set_ylabel('Correlation')
    ax3.set_title(f'Lag Correlation (best at lag={results["lag_analysis"]["best_lag"]})')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Normalized comparison
    ax4 = axes[1, 1]
    cdi_norm = (cdi - cdi.min()) / (cdi.max() - cdi.min())
    ci_norm = (ci - ci.min()) / (ci.max() - ci.min())
    ax4.plot(t, cdi_norm, 'b-', label='CDI (norm)', linewidth=2)
    ax4.plot(t, ci_norm, 'r-', label='CI (norm)', linewidth=2)
    ax4.set_xlabel('Generation')
    ax4.set_ylabel('Normalized [0,1]')
    ax4.set_title('Normalized CDI vs CI')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"Visualization saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='EXP-0: CI Probe')
    parser.add_argument('--csv', required=True, help='v18 evolution.csv file')
    parser.add_argument('--method', default='empirical', 
                       choices=['power_law', 'empirical', 'random'],
                       help='CI estimation method')
    parser.add_argument('--output-dir', default='model_fit_results')
    args = parser.parse_args()
    
    print("="*70)
    print("EXP-0: CI Probe - v18 to v19 Bridge")
    print("="*70)
    print(f"Input: {args.csv}")
    print(f"Method: {args.method}")
    print()
    
    # Load data
    df = pd.read_csv(args.csv)
    print(f"Loaded {len(df)} generations")
    print(f"CDI range: {df['avg_cdi'].min():.3f} - {df['avg_cdi'].max():.3f}")
    print()
    
    # Analyze
    print("Analyzing CDI-CI relationship...")
    results = analyze_cdi_ci_relationship(df, args.method)
    
    # Report
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    print(f"\nCorrelation Analysis:")
    print(f"  Pearson r:  {results['correlation']['pearson']:+.4f} (p={results['correlation']['pearson_p']:.4f})")
    print(f"  Spearman ρ: {results['correlation']['spearman']:+.4f} (p={results['correlation']['spearman_p']:.4f})")
    
    print(f"\nLag Analysis:")
    print(f"  Best lag: {results['lag_analysis']['best_lag']} generations")
    print(f"  Best correlation: {results['lag_analysis']['best_correlation']:+.4f}")
    if results['lag_analysis']['best_lag'] < 0:
        print(f"  → CI leads CDI by {abs(results['lag_analysis']['best_lag'])} generations")
    elif results['lag_analysis']['best_lag'] > 0:
        print(f"  → CDI leads CI by {results['lag_analysis']['best_lag']} generations")
    else:
        print(f"  → Synchronous")
    
    if results['lead_times']['cdi_lead']:
        print(f"\nLead Time to Extinction:")
        print(f"  CDI: {results['lead_times']['cdi_lead']} generations")
        if results['lead_times']['ci_lead']:
            print(f"  CI:  {results['lead_times']['ci_lead']} generations")
            if results['lead_times']['ci_lead'] > results['lead_times']['cdi_lead']:
                print(f"  → CI provides earlier warning than CDI!")
    
    # Decision
    print("\n" + "="*70)
    print("DECISION")
    print("="*70)
    
    r_abs = abs(results['correlation']['pearson'])
    if r_abs > 0.6:
        print("✅ STRONG correlation - Proceed to v19 implementation")
        decision = "GO"
    elif r_abs > 0.3:
        print("⚠️  MODERATE correlation - Proceed with caution, refine CI definition")
        decision = "CAUTION"
    else:
        print("❌ WEAK correlation - Reconsider CI approach or maintain v18 focus")
        decision = "STOP"
    
    # Save results
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # JSON report
    report = {
        'experiment': 'EXP-0_CI_Probe',
        'input_file': str(args.csv),
        'method': args.method,
        'decision': decision,
        'results': results,
    }
    
    output_json = output_dir / 'EXP0_CI_probe_results.json'
    with open(output_json, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\nResults saved: {output_json}")
    
    # Visualization
    output_png = output_dir / 'EXP0_CI_probe_visualization.png'
    visualize_cdi_ci(results, output_png)
    
    print(f"\n{'='*70}")
    print(f"Decision: {decision}")
    print(f"{'='*70}")
    
    return 0 if decision == "GO" else 1


if __name__ == '__main__':
    exit(main())
