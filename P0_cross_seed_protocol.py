#!/usr/bin/env python3
"""
P0: Cross-Seed Validation Protocol
最小Cross-Seed验证协议

目标：验证CDI早期预警信号在不同seed下的稳定性

固定条件:
- 模型版本: Bio-World v18.1
- 参数: MAX_POP=500, syn_per_cell=15
- CDI定义: 不变
- Precursor detector: 不变
- 只变: seed

收集指标:
1. CDI turning point generation
2. Extinction onset generation  
3. Lead time = extinction_onset - turning_point
4. Turning CDI value

验收标准:
- 弱通过: 3+ seed都出现CDI先下降，灭绝后发生
- 中通过: lead time全部为正，且方差不离谱
- 强通过: turning CDI value聚集在0.54±ε
"""

import pandas as pd
import numpy as np
import json
import argparse
from pathlib import Path
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt


def find_turning_point(t, I):
    """找到CDI拐点（二阶导数极值）"""
    if len(I) < 7:
        return None, None
    
    # 计算导数
    dI_dt = savgol_filter(I, 7, 3, deriv=1, delta=np.median(np.diff(t)))
    d2I_dt2 = savgol_filter(I, 7, 3, deriv=2, delta=np.median(np.diff(t)))
    
    # 找到峰值后的最大二阶导数绝对值点
    peak_idx = np.argmax(I)
    post_peak = np.arange(peak_idx, len(d2I_dt2))
    
    if len(post_peak) < 3:
        return None, None
    
    # 找到二阶导数最负的点（下降加速）
    turning_idx = post_peak[np.argmin(d2I_dt2[post_peak])]
    
    return int(t[turning_idx]), float(I[turning_idx])


def find_extinction_onset(df):
    """找到灭绝开始点"""
    if 'extinct_count' not in df.columns:
        return None, None
    
    t = df['generation'].values
    E = df['extinct_count'].values
    
    extinct_mask = E > 0
    if not np.any(extinct_mask):
        return None, None
    
    first_extinct_idx = np.where(extinct_mask)[0][0]
    return int(t[first_extinct_idx]), int(E[first_extinct_idx])


def analyze_single_seed(csv_path):
    """分析单个seed的数据"""
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        return {'error': str(e)}
    
    if len(df) < 10:
        return {'error': 'Insufficient data points'}
    
    t = df['generation'].values
    I = df['avg_cdi'].values
    
    # 找到关键事件
    turning_gen, turning_I = find_turning_point(t, I)
    extinction_gen, _ = find_extinction_onset(df)
    
    result = {
        'csv_file': str(csv_path),
        'n_generations': len(df),
        'cdi_peak': {'gen': int(t[np.argmax(I)]), 'value': float(np.max(I))},
        'cdi_final': {'gen': int(t[-1]), 'value': float(I[-1])},
    }
    
    if turning_gen:
        result['turning_point'] = {'gen': turning_gen, 'cdi_value': turning_I}
    
    if extinction_gen:
        result['extinction_onset'] = {'gen': extinction_gen}
    
    if turning_gen and extinction_gen:
        lead_time = extinction_gen - turning_gen
        result['lead_time'] = int(lead_time)
        result['sequence_valid'] = lead_time > 0  # CDI下降先于灭绝
    else:
        result['lead_time'] = None
        result['sequence_valid'] = False
    
    return result


def evaluate_protocol(results):
    """评估是否通过验收标准"""
    valid_results = [r for r in results if 'error' not in r and r.get('sequence_valid')]
    
    # 初始化evaluation字典
    evaluation = {
        'valid_seeds': len(valid_results),
        'total_seeds': len(results),
        'weak_pass': False,
        'medium_pass': False,
        'strong_pass': False,
        'status': 'FAILED',
    }
    
    if len(valid_results) < 3:
        evaluation['reason'] = f'Only {len(valid_results)} valid results (need >= 3)'
        return evaluation
    
    # 收集指标
    lead_times = [r['lead_time'] for r in valid_results if r.get('lead_time') is not None]
    turning_values = [r['turning_point']['cdi_value'] for r in valid_results if r.get('turning_point')]
    
    # 弱通过: 3+ seed都出现CDI先下降，灭绝后发生
    evaluation['weak_pass'] = len(valid_results) >= 3
    
    # 中通过: lead time全部为正，且方差不离谱
    if lead_times:
        evaluation['lead_time_stats'] = {
            'mean': float(np.mean(lead_times)),
            'std': float(np.std(lead_times)),
            'min': int(np.min(lead_times)),
            'max': int(np.max(lead_times)),
            'all_positive': all(lt > 0 for lt in lead_times),
        }
        # 中通过: 全部为正且标准差 < 50%
        evaluation['medium_pass'] = (
            evaluation['lead_time_stats']['all_positive'] and
            evaluation['lead_time_stats']['std'] < evaluation['lead_time_stats']['mean'] * 0.5
        )
    else:
        evaluation['medium_pass'] = False
    
    # 强通过: turning CDI value聚集在0.54±0.05
    if turning_values:
        evaluation['turning_cdi_stats'] = {
            'mean': float(np.mean(turning_values)),
            'std': float(np.std(turning_values)),
            'min': float(np.min(turning_values)),
            'max': float(np.max(turning_values)),
        }
        # 强通过: 全部落在0.54±0.05且标准差<0.02
        evaluation['strong_pass'] = (
            all(0.49 <= tv <= 0.59 for tv in turning_values) and
            evaluation['turning_cdi_stats']['std'] < 0.02
        )
    else:
        evaluation['strong_pass'] = False
    
    # 总体状态
    if evaluation['strong_pass']:
        evaluation['status'] = 'STRONG_PASS'
    elif evaluation['medium_pass']:
        evaluation['status'] = 'MEDIUM_PASS'
    elif evaluation['weak_pass']:
        evaluation['status'] = 'WEAK_PASS'
    else:
        evaluation['status'] = 'FAILED'
    
    return evaluation


def create_alignment_plot(results, output_path):
    """创建跨seed对齐图"""
    valid_results = [r for r in results if 'error' not in r and 'turning_point' in r]
    
    if len(valid_results) < 2:
        print("Not enough valid results for alignment plot")
        return
    
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    colors = plt.cm.tab10(np.linspace(0, 1, len(valid_results)))
    
    for i, result in enumerate(valid_results):
        csv_path = result['csv_file']
        try:
            df = pd.read_csv(csv_path)
        except:
            continue
        
        t = df['generation'].values
        I = df['avg_cdi'].values
        U = df['alive_universes'].values if 'alive_universes' in df.columns else np.ones(len(t)) * 128
        
        # 对齐到turning point
        turning_gen = result['turning_point']['gen']
        t_aligned = t - turning_gen
        
        # 绘制CDI
        axes[0].plot(t_aligned, I, color=colors[i], alpha=0.7, linewidth=1.5, 
                    label=f"Seed {i+1}")
        
        # 标记turning point (现在都在t=0)
        axes[0].axvline(x=0, color=colors[i], linestyle='--', alpha=0.3)
        
        # 绘制alive universes
        axes[1].plot(t_aligned, U, color=colors[i], alpha=0.7, linewidth=1.5,
                    label=f"Seed {i+1}")
        
        # 标记extinction onset
        if 'extinction_onset' in result:
            extinction_gen = result['extinction_onset']['gen']
            lead_time = extinction_gen - turning_gen
            axes[1].axvline(x=lead_time, color=colors[i], linestyle=':', alpha=0.3)
    
    # CDI图
    axes[0].axvline(x=0, color='black', linestyle='-', linewidth=2, alpha=0.5, label='Turning Point')
    axes[0].axhline(y=0.54, color='red', linestyle='--', alpha=0.5, label='I ≈ 0.54')
    axes[0].set_ylabel('CDI')
    axes[0].set_title('Cross-Seed Alignment: CDI (aligned to turning point)')
    axes[0].legend(loc='upper left', fontsize=8)
    axes[0].grid(True, alpha=0.3)
    axes[0].set_ylim(0, 1)
    
    # Universes图
    axes[1].axvline(x=0, color='black', linestyle='-', linewidth=2, alpha=0.5)
    axes[1].set_xlabel('Generation (relative to turning point)')
    axes[1].set_ylabel('Alive Universes')
    axes[1].set_title('Cross-Seed Alignment: Alive Universes')
    axes[1].legend(loc='upper left', fontsize=8)
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"Alignment plot saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='P0 Cross-Seed Validation Protocol')
    parser.add_argument('--csv-files', nargs='+', required=True, help='List of evolution.csv files from different seeds')
    parser.add_argument('--output-dir', default='model_fit_results', help='Output directory')
    args = parser.parse_args()
    
    print("="*70)
    print("P0: Cross-Seed Validation Protocol")
    print("CDI Early-Warning Signal Stability Test")
    print("="*70)
    print(f"\nAnalyzing {len(args.csv_files)} seed(s)...\n")
    
    # 分析每个seed
    results = []
    for csv_file in args.csv_files:
        print(f"Processing: {csv_file}")
        result = analyze_single_seed(csv_file)
        results.append(result)
        
        if 'error' in result:
            print(f"  ❌ Error: {result['error']}")
        else:
            print(f"  ✅ Peak: Gen {result['cdi_peak']['gen']}, I={result['cdi_peak']['value']:.4f}")
            if 'turning_point' in result:
                print(f"     Turning: Gen {result['turning_point']['gen']}, I={result['turning_point']['cdi_value']:.4f}")
            if 'extinction_onset' in result:
                print(f"     Extinction: Gen {result['extinction_onset']['gen']}")
            if 'lead_time' in result and result['lead_time'] is not None:
                print(f"     Lead time: {result['lead_time']} generations")
        print()
    
    # 评估
    evaluation = evaluate_protocol(results)
    
    print("="*70)
    print("EVALUATION RESULT")
    print("="*70)
    print(f"Status: {evaluation['status']}")
    print(f"Valid seeds: {evaluation.get('valid_seeds', 0)}/{evaluation.get('total_seeds', 0)}")
    
    if 'lead_time_stats' in evaluation:
        stats = evaluation['lead_time_stats']
        print(f"\nLead Time Statistics:")
        print(f"  Mean: {stats['mean']:.1f} ± {stats['std']:.1f} generations")
        print(f"  Range: [{stats['min']}, {stats['max']}]")
        print(f"  All positive: {'✅' if stats['all_positive'] else '❌'}")
    
    if 'turning_cdi_stats' in evaluation:
        stats = evaluation['turning_cdi_stats']
        print(f"\nTurning CDI Statistics:")
        print(f"  Mean: {stats['mean']:.4f} ± {stats['std']:.4f}")
        print(f"  Range: [{stats['min']:.4f}, {stats['max']:.4f}]")
    
    print("\nPass Criteria:")
    print(f"  Weak (3+ valid, CDI before extinction):   {'✅' if evaluation['weak_pass'] else '❌'}")
    print(f"  Medium (positive lead time, low variance): {'✅' if evaluation.get('medium_pass') else '❌'}")
    print(f"  Strong (CDI ≈ 0.54 ± 0.05, tight cluster): {'✅' if evaluation.get('strong_pass') else '❌'}")
    
    # 保存结果
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    full_results = {
        'protocol': 'P0_Cross_Seed_Validation',
        'timestamp': pd.Timestamp.now().isoformat(),
        'individual_results': results,
        'evaluation': evaluation,
    }
    
    output_file = output_dir / 'P0_cross_seed_results.json'
    with open(output_file, 'w') as f:
        json.dump(full_results, f, indent=2, default=str)
    print(f"\nResults saved: {output_file}")
    
    # 创建对齐图
    plot_file = output_dir / 'P0_cross_seed_alignment.png'
    create_alignment_plot(results, plot_file)
    
    # 返回码
    if evaluation['status'] in ['STRONG_PASS', 'MEDIUM_PASS']:
        return 0
    else:
        return 1


if __name__ == '__main__':
    exit(main())
