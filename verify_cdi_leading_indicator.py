#!/usr/bin/env python3
"""
验证CDI是Leading Indicator还是Population Proxy

关键问题：
  CDI下降是否明显早于Population下降？
  
如果是：CDI是预警指标（leading indicator）
如果不是：CDI只是population变化的副产品（proxy）
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
from pathlib import Path


def analyze_lead_lag(csv_path):
    """
    分析CDI和Population变化的时间顺序
    
    返回:
      lead_time: CDI开始下降领先Population下降的代际数
                 >0: CDI先下降（leading indicator）
                 <0: Population先下降（proxy）
                 =0: 同时
    """
    df = pd.read_csv(csv_path)
    t = df['generation'].values
    I = df['avg_cdi'].values
    N = df['population'].values
    
    # 找到各自的峰值
    I_peak_idx = np.argmax(I)
    N_peak_idx = np.argmax(N)
    
    I_peak_gen = t[I_peak_idx]
    N_peak_gen = t[N_peak_idx]
    
    # 计算下降开始的点（从峰值下降5%）
    I_threshold = I[I_peak_idx] * 0.95
    N_threshold = N[N_peak_idx] * 0.95
    
    # 找到I开始持续低于阈值的位置
    I_decline_mask = I < I_threshold
    if np.any(I_decline_mask):
        # 找到峰值后第一个低于阈值的点
        post_peak = np.where(np.arange(len(I)) > I_peak_idx)[0]
        post_peak_decline = [i for i in post_peak if I_decline_mask[i]]
        if post_peak_decline:
            I_decline_gen = t[post_peak_decline[0]]
        else:
            I_decline_gen = None
    else:
        I_decline_gen = None
    
    # 找到N开始持续低于阈值的位置
    N_decline_mask = N < N_threshold
    if np.any(N_decline_mask):
        post_peak = np.where(np.arange(len(N)) > N_peak_idx)[0]
        post_peak_decline = [i for i in post_peak if N_decline_mask[i]]
        if post_peak_decline:
            N_decline_gen = t[post_peak_decline[0]]
        else:
            N_decline_gen = None
    else:
        N_decline_gen = None
    
    # 计算lead time
    if I_decline_gen and N_decline_gen:
        lead_time = N_decline_gen - I_decline_gen
    else:
        lead_time = None
    
    return {
        'cdi_peak': {'gen': int(I_peak_gen), 'value': float(I[I_peak_idx])},
        'pop_peak': {'gen': int(N_peak_gen), 'value': float(N[N_peak_idx])},
        'cdi_decline_start': int(I_decline_gen) if I_decline_gen else None,
        'pop_decline_start': int(N_decline_gen) if N_decline_gen else None,
        'lead_time': int(lead_time) if lead_time is not None else None,
        'is_leading': lead_time > 100 if lead_time else False,  # 领先>100代才算
    }


def correlation_analysis(df):
    """
    分析CDI和Population的相关性随时间的变化
    
    如果是proxy，相关性应该始终很高
    如果是leading indicator，在预警窗口内CDI应该领先
    """
    # 计算滑动窗口相关性
    window = 10
    correlations = []
    
    for i in range(window, len(df)):
        window_df = df.iloc[i-window:i]
        corr = window_df['avg_cdi'].corr(window_df['population'])
        correlations.append(corr)
    
    return correlations


def visualize_lead_lag(csv_path, output_path=None):
    """可视化CDI和Population的时间关系"""
    df = pd.read_csv(csv_path)
    result = analyze_lead_lag(csv_path)
    
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    t = df['generation'].values
    I = df['avg_cdi'].values
    N = df['population'].values
    
    # 标准化到同一尺度便于比较
    I_norm = (I - I.min()) / (I.max() - I.min())
    N_norm = (N - N.min()) / (N.max() - N.min())
    
    # 图1: 原始轨迹
    ax1 = axes[0]
    ax1.plot(t, I, 'b-', label='CDI', linewidth=2)
    ax1_twin = ax1.twinx()
    ax1_twin.plot(t, N, 'r-', label='Population', linewidth=2, alpha=0.7)
    
    # 标记峰值
    ax1.axvline(x=result['cdi_peak']['gen'], color='blue', linestyle='--', alpha=0.5)
    ax1_twin.axvline(x=result['pop_peak']['gen'], color='red', linestyle='--', alpha=0.5)
    
    ax1.set_ylabel('CDI', color='blue')
    ax1_twin.set_ylabel('Population', color='red')
    ax1.set_title('CDI vs Population (Raw Values)')
    ax1.legend(loc='upper left')
    ax1_twin.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    
    # 图2: 标准化轨迹
    ax2 = axes[1]
    ax2.plot(t, I_norm, 'b-', label='CDI (normalized)', linewidth=2)
    ax2.plot(t, N_norm, 'r-', label='Population (normalized)', linewidth=2)
    
    # 标记关键事件
    if result['cdi_decline_start']:
        ax2.axvline(x=result['cdi_decline_start'], color='blue', linestyle=':', 
                   label=f'CDI decline start (Gen {result["cdi_decline_start"]})')
    if result['pop_decline_start']:
        ax2.axvline(x=result['pop_decline_start'], color='red', linestyle=':',
                   label=f'Pop decline start (Gen {result["pop_decline_start"]})')
    
    ax2.set_ylabel('Normalized Value [0,1]')
    ax2.set_title(f'Normalized Comparison (Lead time: {result["lead_time"]} generations)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 图3: 差分（变化率）
    ax3 = axes[2]
    dI = np.diff(I)
    dN = np.diff(N)
    dI_norm = dI / np.max(np.abs(dI))
    dN_norm = dN / np.max(np.abs(dN))
    
    ax3.plot(t[1:], dI_norm, 'b-', label='ΔCDI', alpha=0.7)
    ax3.plot(t[1:], dN_norm, 'r-', label='ΔPopulation', alpha=0.7)
    ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax3.set_xlabel('Generation')
    ax3.set_ylabel('Normalized Change Rate')
    ax3.set_title('Rate of Change (First Derivative)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150)
        print(f"Saved: {output_path}")
    
    return fig, result


def main():
    parser = argparse.ArgumentParser(description='Verify CDI as leading indicator')
    parser.add_argument('--csv-files', nargs='+', required=True)
    parser.add_argument('--output-dir', default='model_fit_results')
    args = parser.parse_args()
    
    print("="*70)
    print("CDI Leading Indicator Verification")
    print("="*70)
    print("\nQuestion: Does CDI decline BEFORE population?")
    print("Or is CDI just a proxy for population changes?\n")
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    results = []
    
    for csv_file in args.csv_files:
        print(f"\nAnalyzing: {csv_file}")
        result = analyze_lead_lag(csv_file)
        results.append(result)
        
        print(f"  CDI peak:    Gen {result['cdi_peak']['gen']}, I={result['cdi_peak']['value']:.4f}")
        print(f"  Pop peak:    Gen {result['pop_peak']['gen']}, N={result['pop_peak']['value']:.0f}")
        print(f"  CDI decline: Gen {result['cdi_decline_start']}")
        print(f"  Pop decline: Gen {result['pop_decline_start']}")
        print(f"  Lead time:   {result['lead_time']} generations")
        
        if result['is_leading']:
            print(f"  ✅ CDI is LEADING indicator (lead > 100 gen)")
        elif result['lead_time'] and result['lead_time'] > 0:
            print(f"  ⚠️  CDI leads but marginally ({result['lead_time']} gen)")
        elif result['lead_time'] and result['lead_time'] < 0:
            print(f"  ❌ CDI is LAGGING (population declines first!)")
        else:
            print(f"  ❓ Cannot determine")
        
        # 生成可视化
        seed_name = Path(csv_file).stem
        fig, _ = visualize_lead_lag(csv_file, 
                                     output_dir / f'lead_lag_analysis_{seed_name}.png')
        plt.close(fig)
    
    # 汇总
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    leading_count = sum(1 for r in results if r.get('is_leading'))
    marginal_count = sum(1 for r in results 
                        if r.get('lead_time') and 0 < r['lead_time'] <= 100)
    lagging_count = sum(1 for r in results if r.get('lead_time') and r['lead_time'] < 0)
    
    print(f"\nTotal seeds analyzed: {len(results)}")
    print(f"  CDI clearly leading (>100 gen):  {leading_count}")
    print(f"  CDI marginally leading (0-100):  {marginal_count}")
    print(f"  CDI lagging (Pop first):         {lagging_count}")
    
    if leading_count >= len(results) * 0.6:
        print("\n✅ CONCLUSION: CDI is a LEADING INDICATOR")
        print("   CDI decline precedes population collapse")
    elif leading_count + marginal_count >= len(results) * 0.6:
        print("\n⚠️  CONCLUSION: CDI may be leading but marginally")
        print("   Need more analysis on lead time distribution")
    else:
        print("\n❌ CONCLUSION: CDI is likely a PROXY for population")
        print("   CDI and population decline together")
    
    print(f"\nVisualizations saved to: {output_dir}/lead_lag_analysis_*.png")


if __name__ == '__main__':
    main()
