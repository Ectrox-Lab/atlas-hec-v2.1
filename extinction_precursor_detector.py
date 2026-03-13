#!/usr/bin/env python3
"""
灭绝连锁前兆检测器 v1
Extinction Cascade Precursor Detector

目标：从CDI、population、alive_universes时间序列中
      检测灭绝连锁的早期预警信号

关键信号（按重要性）：
1. CDI降至临界值 (~0.54)
2. dI/dt 持续负值
3. d²I/dt² 拐点（减速下降→加速下降）
4. population variance 上升
5. alive_universes 相关性结构变化
"""

import pandas as pd
import numpy as np
from scipy.signal import savgol_filter, find_peaks
from scipy.stats import linregress
import matplotlib.pyplot as plt
import json
from pathlib import Path
from datetime import datetime


def load_data(csv_path):
    """加载数据"""
    df = pd.read_csv(csv_path)
    print(f"数据加载: {len(df)} 代")
    print(f"时间跨度: Gen {df['generation'].min()} - {df['generation'].max()}")
    return df


def compute_derivatives(t, y, window=7):
    """计算一阶和二阶导数（使用Savitzky-Golay平滑）"""
    if len(y) < window:
        window = len(y) if len(y) % 2 == 1 else len(y) - 1
    
    # 一阶导数
    dy_dt = savgol_filter(y, window, 3, deriv=1, delta=np.median(np.diff(t)))
    # 二阶导数
    d2y_dt2 = savgol_filter(y, window, 3, deriv=2, delta=np.median(np.diff(t)))
    
    return dy_dt, d2y_dt2


def detect_critical_transitions(df):
    """检测临界转变信号"""
    t = df['generation'].values
    I = df['avg_cdi'].values
    N = df['population'].values
    U = df['alive_universes'].values if 'alive_universes' in df.columns else np.ones(len(t)) * 128
    
    # 计算导数
    dI_dt, d2I_dt2 = compute_derivatives(t, I)
    dN_dt, d2N_dt2 = compute_derivatives(t, N)
    
    results = {
        'cdi_signals': {},
        'population_signals': {},
        'universes_signals': {},
        'critical_events': [],
    }
    
    # ═══════════════════════════════════════════════════════════════
    # CDI信号分析
    # ═══════════════════════════════════════════════════════════════
    
    # 1. 找到CDI峰值（高原期结束）
    peak_idx = np.argmax(I)
    peak_gen = t[peak_idx]
    peak_I = I[peak_idx]
    
    # 2. 找到CDI临界值 (~0.54) - 只在峰值之后检测
    I_crit = 0.54
    # 只在峰值之后寻找低于阈值的点
    post_peak_mask = np.arange(len(I)) > peak_idx
    crit_candidates = (I < I_crit) & post_peak_mask
    if np.any(crit_candidates):
        crit_idx = np.where(crit_candidates)[0][0]
        crit_gen = t[crit_idx]
        crit_I = I[crit_idx]
    else:
        crit_idx = None
        crit_gen = None
        crit_I = None
    
    # 3. 找到首次灭绝
    if 'extinct_count' in df.columns:
        E = df['extinct_count'].values
        extinction_mask = E > 0
        if np.any(extinction_mask):
            first_extinct_idx = np.where(extinction_mask)[0][0]
            first_extinct_gen = t[first_extinct_idx]
            first_extinct_E = E[first_extinct_idx]
        else:
            first_extinct_idx = None
            first_extinct_gen = None
            first_extinct_E = 0
    else:
        first_extinct_idx = None
        first_extinct_gen = None
        first_extinct_E = 0
    
    # 4. 拐点检测（d²I/dt² 极值）
    inflection_indices, _ = find_peaks(np.abs(d2I_dt2), height=np.std(d2I_dt2))
    if len(inflection_indices) > 0:
        # 找到最显著的拐点（在峰值之后）
        post_peak_inflections = [i for i in inflection_indices if i > peak_idx]
        if post_peak_inflections:
            main_inflection_idx = post_peak_inflections[0]
            inflection_gen = t[main_inflection_idx]
            inflection_I = I[main_inflection_idx]
        else:
            main_inflection_idx = inflection_indices[0]
            inflection_gen = t[main_inflection_idx]
            inflection_I = I[main_inflection_idx]
    else:
        main_inflection_idx = None
        inflection_gen = None
        inflection_I = None
    
    # 5. 减速区域检测（dI/dt 从接近0变为负值）
    # 找到dI/dt开始持续负值的点
    negative_dI = dI_dt < -0.001  # 显著负增长
    if np.any(negative_dI):
        sustained_negative = []
        for i in range(len(negative_dI) - 5):
            if np.all(negative_dI[i:i+5]):  # 连续5个点负增长
                sustained_negative.append(i)
        if sustained_negative:
            degradation_start_idx = sustained_negative[0]
            degradation_start_gen = t[degradation_start_idx]
        else:
            degradation_start_idx = None
            degradation_start_gen = None
    else:
        degradation_start_idx = None
        degradation_start_gen = None
    
    results['cdi_signals'] = {
        'peak': {'gen': int(peak_gen), 'value': float(peak_I)},
        'critical_threshold': {'gen': int(crit_gen) if crit_gen else None, 
                               'value': float(crit_I) if crit_I else None,
                               'threshold_used': I_crit},
        'inflection': {'gen': int(inflection_gen) if inflection_gen else None,
                       'value': float(inflection_I) if inflection_I else None},
        'degradation_start': {'gen': int(degradation_start_gen) if degradation_start_gen else None},
    }
    
    # 计算时间窗口
    if crit_gen and first_extinct_gen:
        warning_window = first_extinct_gen - crit_gen
    else:
        warning_window = None
    
    if peak_gen and first_extinct_gen:
        total_degradation_time = first_extinct_gen - peak_gen
    else:
        total_degradation_time = None
    
    results['timing'] = {
        'peak_to_extinction': int(total_degradation_time) if total_degradation_time else None,
        'critical_to_extinction': int(warning_window) if warning_window else None,
        'early_warning_window': int(warning_window) if warning_window else None,
    }
    
    # ═══════════════════════════════════════════════════════════════
    # 临界事件序列
    # ═══════════════════════════════════════════════════════════════
    
    events = []
    
    if degradation_start_gen:
        events.append({
            'generation': int(degradation_start_gen),
            'type': 'cdi_degradation_start',
            'description': 'CDI开始持续下降',
            'value': float(I[degradation_start_idx]) if degradation_start_idx else None,
        })
    
    events.append({
        'generation': int(peak_gen),
        'type': 'cdi_peak',
        'description': 'CDI达到峰值（高原期结束）',
        'value': float(peak_I),
    })
    
    if inflection_gen:
        events.append({
            'generation': int(inflection_gen),
            'type': 'cdi_inflection',
            'description': 'CDI下降加速（拐点）',
            'value': float(inflection_I),
        })
    
    if crit_gen:
        events.append({
            'generation': int(crit_gen),
            'type': 'critical_threshold',
            'description': f'CDI降至临界值以下 ({I_crit})',
            'value': float(crit_I),
        })
    
    if first_extinct_gen:
        events.append({
            'generation': int(first_extinct_gen),
            'type': 'first_extinction',
            'description': '首次宇宙灭绝',
            'value': int(first_extinct_E),
        })
    
    # 找到连锁完成点（灭绝数接近最大）
    if 'extinct_count' in df.columns:
        E = df['extinct_count'].values
        max_E = E.max()
        cascade_complete_mask = E > max_E * 0.9
        if np.any(cascade_complete_mask):
            cascade_idx = np.where(cascade_complete_mask)[0][0]
            cascade_gen = t[cascade_idx]
            events.append({
                'generation': int(cascade_gen),
                'type': 'cascade_complete',
                'description': '灭绝连锁基本完成',
                'value': int(E[cascade_idx]),
            })
    
    results['critical_events'] = sorted(events, key=lambda x: x['generation'])
    
    return results, t, I, N, U, dI_dt, d2I_dt2


def analyze_cascade_speed(df):
    """分析灭绝连锁速度"""
    if 'extinct_count' not in df.columns:
        return None
    
    t = df['generation'].values
    E = df['extinct_count'].values
    
    # 找到连锁活跃期（E从1到接近最大）
    active_mask = (E > 0) & (E < E.max() * 0.95)
    if np.sum(active_mask) < 2:
        return None
    
    active_t = t[active_mask]
    active_E = E[active_mask]
    
    # 计算连锁速度
    dE_dt = np.diff(active_E) / np.diff(active_t)
    avg_speed = np.mean(dE_dt)
    max_speed = np.max(dE_dt)
    
    return {
        'active_period': {'start': int(active_t[0]), 'end': int(active_t[-1])},
        'duration': int(active_t[-1] - active_t[0]),
        'avg_speed': float(avg_speed),
        'max_speed': float(max_speed),
        'total_extinct': int(E.max()),
    }


def generate_report(csv_path):
    """生成完整的前兆检测报告"""
    print("="*70)
    print("灭绝连锁前兆检测器 v1")
    print("Extinction Cascade Precursor Detector")
    print("="*70)
    
    df = load_data(csv_path)
    results, t, I, N, U, dI_dt, d2I_dt2 = detect_critical_transitions(df)
    
    # 连锁速度分析
    cascade_info = analyze_cascade_speed(df)
    if cascade_info:
        results['cascade_dynamics'] = cascade_info
    
    # 打印报告
    print("\n" + "="*70)
    print("CDI 关键信号")
    print("="*70)
    cdi_signals = results['cdi_signals']
    print(f"  CDI峰值:           Gen {cdi_signals['peak']['gen']}, I = {cdi_signals['peak']['value']:.4f}")
    if cdi_signals['degradation_start']['gen']:
        print(f"  下降开始:          Gen {cdi_signals['degradation_start']['gen']}")
    if cdi_signals['inflection']['gen']:
        print(f"  拐点（加速下降）:  Gen {cdi_signals['inflection']['gen']}, I = {cdi_signals['inflection']['value']:.4f}")
    if cdi_signals['critical_threshold']['gen']:
        print(f"  临界阈值:          Gen {cdi_signals['critical_threshold']['gen']}, I = {cdi_signals['critical_threshold']['value']:.4f}")
        print(f"  (阈值设定: I < {cdi_signals['critical_threshold']['threshold_used']})")
    
    print("\n" + "="*70)
    print("时间窗口分析")
    print("="*70)
    timing = results['timing']
    if timing['peak_to_extinction']:
        print(f"  峰值→首次灭绝:    {timing['peak_to_extinction']} 代")
    if timing['early_warning_window']:
        print(f"  临界阈值→灭绝:    {timing['early_warning_window']} 代 ⚠️ 预警窗口")
    
    print("\n" + "="*70)
    print("临界事件序列")
    print("="*70)
    for event in results['critical_events']:
        print(f"  Gen {event['generation']:4d}: {event['type']:20s} | {event['description']}")
    
    if cascade_info:
        print("\n" + "="*70)
        print("灭绝连锁动力学")
        print("="*70)
        print(f"  活跃期:   Gen {cascade_info['active_period']['start']} - {cascade_info['active_period']['end']}")
        print(f"  持续时间: {cascade_info['duration']} 代")
        print(f"  平均速度: {cascade_info['avg_speed']:.2f} 宇宙/代")
        print(f"  最大速度: {cascade_info['max_speed']:.2f} 宇宙/代")
        print(f"  总灭绝:   {cascade_info['total_extinct']} 宇宙")
    
    # 保存结果
    output_dir = Path('model_fit_results')
    output_dir.mkdir(exist_ok=True)
    
    # 清理numpy类型以便JSON序列化
    def convert_types(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj
    
    results_json = json.loads(json.dumps(results, default=convert_types))
    
    with open(output_dir / 'extinction_precursor_analysis.json', 'w') as f:
        json.dump(results_json, f, indent=2)
    
    # 绘图
    fig, axes = plt.subplots(4, 1, figsize=(14, 12))
    
    # 图1: CDI时间序列 + 关键标记
    ax1 = axes[0]
    ax1.plot(t, I, 'b-', linewidth=2, label='CDI')
    
    # 标记关键事件
    cdi_signals = results['cdi_signals']
    colors = {'cdi_peak': 'green', 'critical_threshold': 'red', 
              'first_extinction': 'black', 'cdi_inflection': 'orange'}
    
    for event in results['critical_events']:
        if event['type'] in colors:
            ax1.axvline(x=event['generation'], color=colors[event['type']], 
                       linestyle='--', alpha=0.7, label=event['type'])
    
    ax1.axhline(y=0.54, color='red', linestyle=':', alpha=0.5, label='I_crit = 0.54')
    ax1.set_ylabel('CDI')
    ax1.set_title('CDI Trajectory with Critical Events')
    ax1.legend(loc='upper left', fontsize=8)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 1)
    
    # 图2: CDI导数
    ax2 = axes[1]
    ax2.plot(t, dI_dt, 'g-', linewidth=1.5, label='dI/dt')
    ax2.plot(t, d2I_dt2, 'r-', linewidth=1.5, label='d²I/dt²')
    ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax2.set_ylabel('Derivative')
    ax2.set_title('CDI Derivatives (Early Warning Signals)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 图3: Population + Universes
    ax3 = axes[2]
    ax3.plot(t, N, 'b-', linewidth=2, label='Population')
    ax3_twin = ax3.twinx()
    ax3_twin.plot(t, U, 'r-', linewidth=2, label='Alive Universes', alpha=0.7)
    
    for event in results['critical_events']:
        if event['type'] == 'first_extinction':
            ax3.axvline(x=event['generation'], color='black', linestyle='--', alpha=0.7)
    
    ax3.set_ylabel('Population', color='blue')
    ax3_twin.set_ylabel('Alive Universes', color='red')
    ax3.set_title('Population vs Universe Count')
    ax3.grid(True, alpha=0.3)
    
    # 图4: 灭绝连锁
    if 'extinct_count' in df.columns:
        ax4 = axes[3]
        E = df['extinct_count'].values
        ax4.fill_between(t, E, alpha=0.3, color='red')
        ax4.plot(t, E, 'r-', linewidth=2)
        ax4.set_xlabel('Generation')
        ax4.set_ylabel('Extinct Count')
        ax4.set_title('Extinction Cascade')
        ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'extinction_precursor_analysis.png', dpi=150)
    print(f"\n✅ 报告已保存: {output_dir}/extinction_precursor_analysis.json")
    print(f"✅ 图表已保存: {output_dir}/extinction_precursor_analysis.png")
    
    return results


if __name__ == '__main__':
    import sys, glob
    
    csv_file = None
    patterns = ['/home/admin/zeroclaw-labs/v18_1_experiments/*/evolution.csv']
    for p in patterns:
        matches = glob.glob(p)
        if matches:
            csv_file = matches[0]
            break
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    
    if not csv_file or not Path(csv_file).exists():
        print("Error: No CSV file found.")
        sys.exit(1)
    
    generate_report(csv_file)
