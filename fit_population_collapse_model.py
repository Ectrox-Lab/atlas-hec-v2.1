#!/usr/bin/env python3
"""
Layer A: Population Collapse Model

数据真相：种群从16,901 → 2，是崩溃过程，不是增长！

模型：
阶段1 (Gen 0-30):  维持/微增    dN/dt ≈ 0
阶段2 (Gen 30-50): 快速崩溃     dN/dt = -α·B_t·N  (Boss压力驱动)
阶段3 (Gen 50+):   衰减至灭绝   dN/dt = -β·N       (指数衰减)

关键问题：什么触发了Gen 30后的崩溃？
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import json
from pathlib import Path


def load_data(csv_path):
    df = pd.read_csv(csv_path)
    print(f"Data loaded: {len(df)} generations")
    print(f"Population trajectory: {df['population'].iloc[0]:.0f} → {df['population'].iloc[len(df)//2]:.0f} → {df['population'].iloc[-1]:.0f}")
    return df


def identify_phases(df):
    """识别崩溃阶段"""
    N = df['population'].values
    t = df['generation'].values
    
    # 找到峰值
    peak_idx = np.argmax(N)
    peak_gen = t[peak_idx]
    peak_N = N[peak_idx]
    
    # 找到快速下降段 (dN/dt < threshold)
    dN = np.diff(N)
    dt = np.diff(t)
    growth_rate = dN / dt
    
    # 找到崩溃开始点（连续负增长）
    collapse_start = None
    for i in range(peak_idx, len(growth_rate)):
        if growth_rate[i] < -100:  # 显著负增长
            collapse_start = i
            break
    
    # 找到衰减阶段（低种群，慢速下降）
    low_threshold = N.max() * 0.1
    extinction_phase = np.where(N < low_threshold)[0]
    
    phases = {
        'maintenance': (0, peak_idx),
        'peak_gen': int(peak_gen),
        'peak_N': float(peak_N),
        'collapse_start_gen': int(t[collapse_start]) if collapse_start else None,
        'extinction_start': int(t[extinction_phase[0]]) if len(extinction_phase) > 0 else None,
    }
    
    return phases


def collapse_model_predict(df, alpha, beta, N_critical):
    """
    两阶段崩溃模型：
    - 当 N > N_critical: dN/dt = -alpha * B_t * N  (Boss压力驱动)
    - 当 N <= N_critical: dN/dt = -beta * N       (基础衰减)
    """
    N_obs = df['population'].values
    t = df['generation'].values
    
    # Boss压力代理
    if 'extinct_count' in df.columns:
        B = df['extinct_count'].values / 128.0
    else:
        B = np.zeros(len(t))
    
    # 数值积分
    N_pred = np.zeros(len(t))
    N_pred[0] = N_obs[0]
    
    for i in range(1, len(t)):
        dt = t[i] - t[i-1]
        
        if N_pred[i-1] > N_critical:
            # 高压阶段：Boss驱动崩溃
            dN = -alpha * B[i] * N_pred[i-1] * dt
        else:
            # 低种群衰减
            dN = -beta * N_pred[i-1] * dt
        
        N_pred[i] = N_pred[i-1] + dN
        if N_pred[i] < 0:
            N_pred[i] = 0.01
    
    return N_pred


def fit_collapse_model(df):
    """拟合崩溃模型"""
    N_obs = df['population'].values
    
    def objective(params):
        alpha, beta, N_critical = params
        if alpha <= 0 or beta <= 0 or N_critical <= 0:
            return 1e10
        try:
            N_pred = collapse_model_predict(df, alpha, beta, N_critical)
            return np.sum((N_pred - N_obs)**2)
        except:
            return 1e10
    
    N_max = N_obs.max()
    result = minimize(
        objective,
        [0.01, 0.001, N_max * 0.3],  # alpha, beta, N_critical
        bounds=[(0.0001, 1.0), (0.0001, 0.1), (N_max * 0.05, N_max * 0.8)],
        method='L-BFGS-B'
    )
    
    alpha, beta, N_critical = result.x
    N_pred = collapse_model_predict(df, alpha, beta, N_critical)
    
    rss = np.sum((N_pred - N_obs)**2)
    rmse = np.sqrt(rss / len(N_obs))
    r2 = 1 - rss / np.sum((N_obs - np.mean(N_obs))**2)
    
    return {
        'alpha': float(alpha),
        'beta': float(beta),
        'N_critical': float(N_critical),
        'rss': float(rss),
        'rmse': float(rmse),
        'r2': float(r2),
        'N_pred': N_pred,
    }


def analyze_triggers(df):
    """分析崩溃触发因素"""
    N = df['population'].values
    t = df['generation'].values
    
    # 找到峰值后的快速下降段
    peak_idx = np.argmax(N)
    
    analysis = {}
    
    # 检查各种因素在峰值前后的变化
    factors = {
        'population': N,
        'avg_cdi': df['avg_cdi'].values if 'avg_cdi' in df.columns else None,
        'avg_collaboration': df['avg_collaboration'].values if 'avg_collaboration' in df.columns else None,
        'extinct_count': df['extinct_count'].values if 'extinct_count' in df.columns else None,
        'alive_universes': df['alive_universes'].values if 'alive_universes' in df.columns else None,
    }
    
    for name, values in factors.items():
        if values is not None:
            before = np.mean(values[max(0, peak_idx-5):peak_idx])
            after = np.mean(values[peak_idx:min(len(values), peak_idx+10)])
            change = (after - before) / before if before != 0 else 0
            analysis[name] = {
                'before_peak': float(before),
                'after_peak': float(after),
                'change_pct': float(change * 100),
            }
    
    return analysis


def fit_model(csv_path):
    print("="*70)
    print("Layer A: Population Collapse Model")
    print("="*70)
    
    df = load_data(csv_path)
    
    # 识别阶段
    print("\n[Phase Identification]")
    phases = identify_phases(df)
    print(f"  Peak at Gen {phases['peak_gen']}: N = {phases['peak_N']:.0f}")
    print(f"  Maintenance phase: Gen 0-{phases['peak_gen']}")
    if phases['collapse_start_gen']:
        print(f"  Collapse starts: Gen {phases['collapse_start_gen']}")
    if phases['extinction_start']:
        print(f"  Extinction phase: Gen {phases['extinction_start']}+")
    
    # 拟合崩溃模型
    print("\n[Collapse Model Fitting]")
    fit = fit_collapse_model(df)
    
    print(f"\n  Parameters:")
    print(f"    α (Boss压力系数):  {fit['alpha']:.6f}")
    print(f"    β (基础衰减率):    {fit['beta']:.6f}")
    print(f"    N_critical:        {fit['N_critical']:.0f}")
    print(f"\n  Fit quality:")
    print(f"    R²:   {fit['r2']:.4f}")
    print(f"    RMSE: {fit['rmse']:.2f}")
    
    # 触发因素分析
    print("\n[Collapse Trigger Analysis]")
    triggers = analyze_triggers(df)
    for name, data in triggers.items():
        print(f"  {name}:")
        print(f"    Before peak: {data['before_peak']:.4f}")
        print(f"    After peak:  {data['after_peak']:.4f}")
        print(f"    Change:      {data['change_pct']:+.1f}%")
    
    # 保存结果
    output_dir = Path('model_fit_results')
    output_dir.mkdir(exist_ok=True)
    
    results = {
        'model': 'Population Collapse (Two-Phase)',
        'phases': phases,
        'parameters': {
            'alpha': fit['alpha'],
            'beta': fit['beta'],
            'N_critical': fit['N_critical'],
        },
        'fit_quality': {
            'R2': fit['r2'],
            'RMSE': fit['rmse'],
        },
        'triggers': triggers,
    }
    
    # Fix numpy types for JSON serialization
    def convert_types(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj
    
    results_json = json.loads(json.dumps(results, default=convert_types))
    
    with open(output_dir / 'population_collapse_model.json', 'w') as f:
        json.dump(results_json, f, indent=2)
    
    # 绘图
    t = df['generation'].values
    N_obs = df['population'].values
    N_pred = fit['N_pred']
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 主图：崩溃轨迹
    ax = axes[0, 0]
    ax.plot(t, N_obs, 'b-', label='Observed', linewidth=2)
    ax.plot(t, N_pred, 'r--', label='Collapse Model', linewidth=2)
    ax.axhline(y=fit['N_critical'], color='g', linestyle=':', alpha=0.7, 
               label=f'N_critical = {fit["N_critical"]:.0f}')
    ax.axvline(x=phases['peak_gen'], color='orange', linestyle=':', alpha=0.7,
               label=f'Peak Gen {phases["peak_gen"]}')
    ax.set_xlabel('Generation')
    ax.set_ylabel('Population')
    ax.set_title(f'Population Collapse (R² = {fit["r2"]:.4f})')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 对数尺度
    ax = axes[0, 1]
    ax.semilogy(t, N_obs, 'b-', label='Observed', linewidth=2)
    ax.semilogy(t, N_pred, 'r--', label='Model', linewidth=2)
    ax.axhline(y=fit['N_critical'], color='g', linestyle=':', alpha=0.7)
    ax.set_xlabel('Generation')
    ax.set_ylabel('Population (log)')
    ax.set_title('Log Scale')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 崩溃率
    ax = axes[1, 0]
    if len(N_obs) > 1:
        collapse_rate = -np.diff(N_obs) / np.diff(t) / N_obs[:-1]
        ax.plot(t[:-1], collapse_rate, 'b-', linewidth=1.5)
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax.set_xlabel('Generation')
        ax.set_ylabel('Collapse Rate (-dN/dt / N)')
        ax.set_title('Per-Capita Collapse Rate')
        ax.grid(True, alpha=0.3)
    
    # 残差
    ax = axes[1, 1]
    resid = N_obs - N_pred
    ax.plot(t, resid, 'g-', linewidth=1.5)
    ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax.set_xlabel('Generation')
    ax.set_ylabel('Residuals')
    ax.set_title('Model Residuals')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'population_collapse_model.png', dpi=150)
    print(f"\n✅ Plot saved: {output_dir}/population_collapse_model.png")
    print(f"✅ Results saved: {output_dir}/population_collapse_model.json")
    
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
    
    fit_model(csv_file)
