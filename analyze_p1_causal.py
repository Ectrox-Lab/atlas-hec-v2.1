#!/usr/bin/env python3
"""
P1 Causal Analysis Script
Analyzes CTRL vs P1-A/B/C experiments for causal evidence
"""

import pandas as pd
import numpy as np
import json
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
from scipy import stats


def load_group_data(csv_files, group_name):
    """Load all CSVs for a group"""
    data = []
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            df['group'] = group_name
            df['source_file'] = str(csv_file)
            data.append(df)
        except Exception as e:
            print(f"Error loading {csv_file}: {e}")
    return data


def extract_key_metrics(df):
    """Extract key metrics from a single run"""
    t = df['generation'].values
    I = df['avg_cdi'].values
    N = df['population'].values
    
    # CDI peak
    peak_idx = np.argmax(I)
    peak_cdi = I[peak_idx]
    peak_gen = t[peak_idx]
    
    # CDI decline onset (5% drop from peak)
    decline_threshold = peak_cdi * 0.95
    post_peak = np.where(t > peak_gen)[0]
    if len(post_peak) > 0:
        decline_candidates = [i for i in post_peak if I[i] < decline_threshold]
        if decline_candidates:
            decline_gen = t[decline_candidates[0]]
            decline_cdi = I[decline_candidates[0]]
        else:
            decline_gen = None
            decline_cdi = None
    else:
        decline_gen = None
        decline_cdi = None
    
    # Population decline onset
    N_peak_idx = np.argmax(N)
    N_decline_threshold = N[N_peak_idx] * 0.95
    post_peak_N = np.where(t > t[N_peak_idx])[0]
    if len(post_peak_N) > 0:
        N_decline_candidates = [i for i in post_peak_N if N[i] < N_decline_threshold]
        if N_decline_candidates:
            N_decline_gen = t[N_decline_candidates[0]]
        else:
            N_decline_gen = None
    else:
        N_decline_gen = None
    
    # First extinction
    if 'extinct_count' in df.columns:
        E = df['extinct_count'].values
        extinct_mask = E > 0
        if np.any(extinct_mask):
            first_extinct_idx = np.where(extinct_mask)[0][0]
            first_extinct_gen = t[first_extinct_idx]
            first_extinct_cdi = I[first_extinct_idx]
        else:
            first_extinct_gen = None
            first_extinct_cdi = None
    else:
        first_extinct_gen = None
        first_extinct_cdi = None
    
    # CDI final
    final_cdi = I[-1]
    final_gen = t[-1]
    
    # Lead times
    if decline_gen and N_decline_gen:
        lead_pop = N_decline_gen - decline_gen
    else:
        lead_pop = None
    
    if decline_gen and first_extinct_gen:
        lead_extinct = first_extinct_gen - decline_gen
    else:
        lead_extinct = None
    
    return {
        'peak_cdi': float(peak_cdi),
        'peak_gen': int(peak_gen),
        'decline_gen': int(decline_gen) if decline_gen else None,
        'decline_cdi': float(decline_cdi) if decline_cdi else None,
        'N_decline_gen': int(N_decline_gen) if N_decline_gen else None,
        'first_extinct_gen': int(first_extinct_gen) if first_extinct_gen else None,
        'first_extinct_cdi': float(first_extinct_cdi) if first_extinct_cdi else None,
        'final_cdi': float(final_cdi),
        'final_gen': int(final_gen),
        'lead_pop': int(lead_pop) if lead_pop else None,
        'lead_extinct': int(lead_extinct) if lead_extinct else None,
        'cdi_decline_pct': float((peak_cdi - final_cdi) / peak_cdi * 100) if peak_cdi > 0 else 0,
    }


def paired_comparison(ctrl_metrics, treatment_metrics, metric_name):
    """Compare treatment vs control for same seeds"""
    # Extract values
    ctrl_values = [m[metric_name] for m in ctrl_metrics if m[metric_name] is not None]
    treat_values = [m[metric_name] for m in treatment_metrics if m[metric_name] is not None]
    
    if len(ctrl_values) < 2 or len(treat_values) < 2:
        return None
    
    # Paired differences (assume same order)
    min_len = min(len(ctrl_values), len(treat_values))
    diffs = [treat_values[i] - ctrl_values[i] for i in range(min_len)]
    
    # Effect size (Cohen's d for paired)
    mean_diff = np.mean(diffs)
    std_diff = np.std(diffs, ddof=1)
    cohens_d = mean_diff / std_diff if std_diff > 0 else 0
    
    # Permutation test (small sample)
    n_perm = 10000
    observed_stat = np.mean(diffs)
    perm_stats = []
    for _ in range(n_perm):
        # Randomly flip signs
        flipped = [d * np.random.choice([-1, 1]) for d in diffs]
        perm_stats.append(np.mean(flipped))
    
    # Two-tailed p-value
    p_value = np.mean(np.abs(perm_stats) >= np.abs(observed_stat))
    
    return {
        'ctrl_mean': float(np.mean(ctrl_values)),
        'treat_mean': float(np.mean(treat_values)),
        'mean_diff': float(mean_diff),
        'cohens_d': float(cohens_d),
        'p_value': float(p_value),
        'n_pairs': min_len,
    }


def analyze_group(ctrl_data, treatment_data, group_name):
    """Analyze treatment group vs control"""
    print(f"\n{'='*60}")
    print(f"Analyzing {group_name} vs CTRL")
    print(f"{'='*60}")
    
    # Extract metrics
    ctrl_metrics = [extract_key_metrics(df) for df in ctrl_data]
    treat_metrics = [extract_key_metrics(df) for df in treatment_data]
    
    results = {
        'group': group_name,
        'ctrl_n': len(ctrl_metrics),
        'treat_n': len(treat_metrics),
    }
    
    # Comparisons
    comparisons = {}
    
    for metric in ['decline_gen', 'first_extinct_gen', 'cdi_decline_pct']:
        comp = paired_comparison(ctrl_metrics, treat_metrics, metric)
        if comp:
            comparisons[metric] = comp
            
            print(f"\n{metric}:")
            print(f"  CTRL:   {comp['ctrl_mean']:.1f}")
            print(f"  {group_name}: {comp['treat_mean']:.1f}")
            print(f"  Diff:   {comp['mean_diff']:+.1f}")
            print(f"  Cohen's d: {comp['cohens_d']:.2f}")
            print(f"  p-value:   {comp['p_value']:.4f}")
            
            # Direction check
            if metric == 'decline_gen' or metric == 'first_extinct_gen':
                # Earlier is lower value
                if comp['mean_diff'] < 0:
                    print(f"  → {group_name} EARLIER (expected for P1-A/B)")
                else:
                    print(f"  → {group_name} LATER (unexpected)")
            elif metric == 'cdi_decline_pct':
                # Higher percentage means more decline
                if comp['mean_diff'] > 0:
                    print(f"  → {group_name} MORE decline (expected)")
                else:
                    print(f"  → {group_name} LESS decline (unexpected)")
    
    results['comparisons'] = comparisons
    results['ctrl_metrics'] = ctrl_metrics
    results['treat_metrics'] = treat_metrics
    
    return results


def create_visualizations(all_results, output_dir):
    """Create summary visualizations"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Plot 1: CDI decline onset comparison
    ax = axes[0, 0]
    groups = ['CTRL', 'P1-A', 'P1-B', 'P1-C']
    colors = ['gray', 'red', 'blue', 'green']
    
    for group, color in zip(groups, colors):
        if group in all_results:
            metrics = all_results[group]['treat_metrics'] if group != 'CTRL' else all_results[group]['ctrl_metrics']
            values = [m['decline_gen'] for m in metrics if m['decline_gen']]
            if values:
                ax.scatter([group]*len(values), values, color=color, s=100, alpha=0.6)
                ax.scatter(group, np.mean(values), color=color, s=200, marker='_', linewidth=3)
    
    ax.set_ylabel('CDI Decline Onset (Generation)')
    ax.set_title('CDI Decline Timing by Group')
    ax.axhline(y=all_results['CTRL']['ctrl_metrics'][0]['decline_gen'] if all_results['CTRL']['ctrl_metrics'] else 0, 
               color='gray', linestyle='--', alpha=0.3, label='CTRL mean')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 2: First extinction comparison
    ax = axes[0, 1]
    for group, color in zip(groups, colors):
        if group in all_results:
            metrics = all_results[group]['treat_metrics'] if group != 'CTRL' else all_results[group]['ctrl_metrics']
            values = [m['first_extinct_gen'] for m in metrics if m['first_extinct_gen']]
            if values:
                ax.scatter([group]*len(values), values, color=color, s=100, alpha=0.6)
                ax.scatter(group, np.mean(values), color=color, s=200, marker='_', linewidth=3)
    
    ax.set_ylabel('First Extinction (Generation)')
    ax.set_title('Extinction Timing by Group')
    ax.grid(True, alpha=0.3)
    
    # Plot 3: CDI decline percentage
    ax = axes[1, 0]
    for group, color in zip(groups, colors):
        if group in all_results:
            metrics = all_results[group]['treat_metrics'] if group != 'CTRL' else all_results[group]['ctrl_metrics']
            values = [m['cdi_decline_pct'] for m in metrics]
            if values:
                ax.scatter([group]*len(values), values, color=color, s=100, alpha=0.6)
                ax.scatter(group, np.mean(values), color=color, s=200, marker='_', linewidth=3)
    
    ax.set_ylabel('CDI Decline (%)')
    ax.set_title('CDI Decline Magnitude by Group')
    ax.grid(True, alpha=0.3)
    
    # Plot 4: Lead time consistency
    ax = axes[1, 1]
    for group, color in zip(['P1-A', 'P1-B', 'P1-C'], colors[1:]):
        if group in all_results:
            metrics = all_results[group]['treat_metrics']
            values = [m['lead_extinct'] for m in metrics if m['lead_extinct']]
            if values:
                ax.scatter([group]*len(values), values, color=color, s=100, alpha=0.6)
    
    ax.set_ylabel('CDI Lead Time to Extinction (generations)')
    ax.set_title('Leading Indicator Property by Group')
    ax.axhline(y=0, color='black', linestyle='--', alpha=0.3)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'P1_group_comparisons.png', dpi=150)
    print(f"\nVisualization saved: {output_dir / 'P1_group_comparisons.png'}")


def generate_summary_report(all_results, output_dir):
    """Generate P1_RESULTS_SUMMARY.md"""
    output_dir = Path(output_dir)
    
    report = []
    report.append("# P1 Causal Experiment Results\n")
    report.append("## Executive Summary\n")
    
    # Pass/fail assessment
    passes = []
    for group in ['P1-A', 'P1-B', 'P1-C']:
        if group in all_results and 'comparisons' in all_results[group]:
            comps = all_results[group]['comparisons']
            
            # Check if effect direction is correct
            if 'decline_gen' in comps and comps['decline_gen']['mean_diff'] < 0:
                passes.append(group)
    
    report.append(f"**Groups showing expected effect direction**: {', '.join(passes) if passes else 'None'}\n")
    
    # Detailed results
    report.append("## Detailed Results\n")
    
    for group in ['P1-A', 'P1-B', 'P1-C']:
        if group in all_results:
            report.append(f"\n### {group} vs CTRL\n")
            
            if 'comparisons' in all_results[group]:
                comps = all_results[group]['comparisons']
                
                for metric, comp in comps.items():
                    report.append(f"- **{metric}**:\n")
                    report.append(f"  - CTRL: {comp['ctrl_mean']:.1f}\n")
                    report.append(f"  - {group}: {comp['treat_mean']:.1f}\n")
                    report.append(f"  - Effect size (Cohen's d): {comp['cohens_d']:.2f}\n")
                    report.append(f"  - p-value: {comp['p_value']:.4f}\n")
                    
                    # Causal interpretation
                    if comp['p_value'] < 0.05 and abs(comp['cohens_d']) > 0.5:
                        report.append(f"  - **Status: Significant effect** ✓\n")
                    else:
                        report.append(f"  - Status: No significant effect\n")
    
    # Conclusion
    report.append("\n## Causal Conclusion\n")
    
    if len(passes) >= 2:
        report.append(
            "> Intervening on memory or cooperation causally alters CDI trajectories "
            "and extinction dynamics, supporting CDI as a causal state variable "
            "rather than merely a leading indicator.\n"
        )
    elif len(passes) == 1:
        report.append(
            "> Limited evidence supports causal manipulation of CDI. "
            "Further validation with larger samples recommended.\n"
        )
    else:
        report.append(
            "> Current interventions do not provide conclusive evidence "
            "for CDI as causal state variable. Design refinement needed.\n"
        )
    
    # Write report
    report_path = output_dir / 'P1_RESULTS_SUMMARY.md'
    with open(report_path, 'w') as f:
        f.write('\n'.join(report))
    
    print(f"Report saved: {report_path}")


def main():
    parser = argparse.ArgumentParser(description='P1 Causal Analysis')
    parser.add_argument('--ctrl', nargs='+', required=True)
    parser.add_argument('--p1a', nargs='+', required=True)
    parser.add_argument('--p1b', nargs='+', required=True)
    parser.add_argument('--p1c', nargs='+', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    print("="*60)
    print("P1 Causal Analysis")
    print("="*60)
    
    # Load data
    print("\nLoading CTRL data...")
    ctrl_data = load_group_data(args.ctrl, 'CTRL')
    print(f"  Loaded {len(ctrl_data)} runs")
    
    print("\nLoading P1-A data...")
    p1a_data = load_group_data(args.p1a, 'P1-A')
    print(f"  Loaded {len(p1a_data)} runs")
    
    print("\nLoading P1-B data...")
    p1b_data = load_group_data(args.p1b, 'P1-B')
    print(f"  Loaded {len(p1b_data)} runs")
    
    print("\nLoading P1-C data...")
    p1c_data = load_group_data(args.p1c, 'P1-C')
    print(f"  Loaded {len(p1c_data)} runs")
    
    # Analyze
    all_results = {'CTRL': {'ctrl_metrics': [extract_key_metrics(df) for df in ctrl_data]}}
    
    if len(ctrl_data) >= 2 and len(p1a_data) >= 2:
        all_results['P1-A'] = analyze_group(ctrl_data, p1a_data, 'P1-A')
    
    if len(ctrl_data) >= 2 and len(p1b_data) >= 2:
        all_results['P1-B'] = analyze_group(ctrl_data, p1b_data, 'P1-B')
    
    if len(ctrl_data) >= 2 and len(p1c_data) >= 2:
        all_results['P1-C'] = analyze_group(ctrl_data, p1c_data, 'P1-C')
    
    # Create outputs
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Visualizations
    create_visualizations(all_results, output_dir)
    
    # Summary report
    generate_summary_report(all_results, output_dir)
    
    # JSON results
    with open(output_dir / 'P1_EFFECT_SIZES.json', 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\n{'='*60}")
    print("Analysis complete")
    print(f"Output: {output_dir}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
