#!/usr/bin/env python3
"""
Layer A: Population模型比较
测试三种候选模型：

A1: 指数增长
    dN/dt = r·N

A2: 广义Logistic (Richards)
    dN/dt = r·N·(1 - (N/K)^ν)

A3: 带外驱动
    dN/dt = r·N - m·B_t·N + u·E_t

使用AIC/BIC选择最佳模型
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
from scipy.stats import linregress
import matplotlib.pyplot as plt
import json
from pathlib import Path


def load_data(csv_path):
    return pd.read_csv(csv_path)


def aic_bic(n, rss, k):
    """计算AIC和BIC
    n: 样本数
    rss: 残差平方和
    k: 参数个数
    """
    sigma2 = rss / n
    log_likelihood = -n/2 * (np.log(2*np.pi) + np.log(sigma2) + 1)
    aic = 2*k - 2*log_likelihood
    bic = np.log(n)*k - 2*log_likelihood
    return aic, bic


# ═══════════════════════════════════════════════════════════════
# Model A1: 指数增长
# ═══════════════════════════════════════════════════════════════

def model_a1_predict(df, r):
    """指数增长模型"""
    N0 = df['population'].values[0]
    t = df['generation'].values
    N_pred = N0 * np.exp(r * (t - t[0]))
    return N_pred


def fit_model_a1(df):
    """拟合指数增长模型"""
    N_obs = df['population'].values
    
    def objective(r):
        N_pred = model_a1_predict(df, r[0])
        return np.sum((N_pred - N_obs)**2)
    
    result = minimize(objective, [0.1], bounds=[(0.001, 2.0)], method='L-BFGS-B')
    r = result.x[0]
    
    N_pred = model_a1_predict(df, r)
    rss = np.sum((N_pred - N_obs)**2)
    rmse = np.sqrt(rss / len(N_obs))
    r2 = 1 - rss / np.sum((N_obs - np.mean(N_obs))**2)
    
    aic, bic = aic_bic(len(N_obs), rss, 1)
    
    return {
        'name': 'A1_Exponential',
        'equation': 'dN/dt = r·N',
        'params': {'r': float(r)},
        'rss': float(rss),
        'rmse': float(rmse),
        'r2': float(r2),
        'aic': float(aic),
        'bic': float(bic),
        'k': 1,
        'N_pred': N_pred,
    }


# ═══════════════════════════════════════════════════════════════
# Model A2: 广义Logistic (Richards)
# ═══════════════════════════════════════════════════════════════

def model_a2_predict(df, r, K, nu):
    """广义Logistic模型"""
    N0 = df['population'].values[0]
    t = df['generation'].values
    t0 = t[0]
    
    # 数值积分
    N_pred = np.zeros(len(t))
    N_pred[0] = N0
    
    for i in range(1, len(t)):
        dt = t[i] - t[i-1]
        # dN/dt = r·N·(1 - (N/K)^nu)
        dN = r * N_pred[i-1] * (1 - (N_pred[i-1] / K)**nu) * dt
        N_pred[i] = N_pred[i-1] + dN
        if N_pred[i] < 0:
            N_pred[i] = 0.01
    
    return N_pred


def fit_model_a2(df):
    """拟合广义Logistic模型"""
    N_obs = df['population'].values
    N_max = N_obs.max()
    
    def objective(params):
        r, K, nu = params
        if K <= 0 or nu <= 0:
            return 1e10
        try:
            N_pred = model_a2_predict(df, r, K, nu)
            return np.sum((N_pred - N_obs)**2)
        except:
            return 1e10
    
    # 初始猜测
    N_obs = df['population'].values
    result = minimize(
        objective,
        [0.1, N_max * 1.5, 0.5],  # r, K, nu
        bounds=[(0.001, 2.0), (N_max * 0.5, N_max * 10), (0.01, 5.0)],
        method='L-BFGS-B'
    )
    
    r, K, nu = result.x
    N_pred = model_a2_predict(df, r, K, nu)
    rss = np.sum((N_pred - N_obs)**2)
    rmse = np.sqrt(rss / len(N_obs))
    r2 = 1 - rss / np.sum((N_obs - np.mean(N_obs))**2)
    
    aic, bic = aic_bic(len(N_obs), rss, 3)
    
    return {
        'name': 'A2_Richards',
        'equation': 'dN/dt = r·N·(1 - (N/K)^ν)',
        'params': {'r': float(r), 'K': float(K), 'nu': float(nu)},
        'rss': float(rss),
        'rmse': float(rmse),
        'r2': float(r2),
        'aic': float(aic),
        'bic': float(bic),
        'k': 3,
        'N_pred': N_pred,
    }


# ═══════════════════════════════════════════════════════════════
# Model A3: 带外驱动
# ═══════════════════════════════════════════════════════════════

def model_a3_predict(df, r, m, u):
    """带外驱动模型"""
    N0 = df['population'].values[0]
    t = df['generation'].values
    
    # 代理变量
    if 'extinct_count' in df.columns:
        B = df['extinct_count'].values / 128.0
    else:
        B = np.zeros(len(t))
    
    # E_t: 外部资源代理 - 用alive_universes
    if 'alive_universes' in df.columns:
        E = df['alive_universes'].values / 128.0
    else:
        E = np.ones(len(t)) * 0.5
    
    # 数值积分
    N_pred = np.zeros(len(t))
    N_pred[0] = N0
    
    for i in range(1, len(t)):
        dt = t[i] - t[i-1]
        # dN/dt = r·N - m·B_t·N + u·E_t
        dN = (r * N_pred[i-1] - m * B[i] * N_pred[i-1] + u * E[i]) * dt
        N_pred[i] = N_pred[i-1] + dN
        if N_pred[i] < 0:
            N_pred[i] = 0.01
    
    return N_pred


def fit_model_a3(df):
    """拟合带外驱动模型"""
    N_obs = df['population'].values
    
    def objective(params):
        r, m, u = params
        try:
            N_pred = model_a3_predict(df, r, m, u)
            return np.sum((N_pred - N_obs)**2)
        except:
            return 1e10
    
    result = minimize(
        objective,
        [0.1, 0.01, 10.0],  # r, m, u
        bounds=[(0.001, 2.0), (0.0, 1.0), (0.0, 1000.0)],
        method='L-BFGS-B'
    )
    
    r, m, u = result.x
    N_pred = model_a3_predict(df, r, m, u)
    rss = np.sum((N_pred - N_obs)**2)
    rmse = np.sqrt(rss / len(N_obs))
    r2 = 1 - rss / np.sum((N_obs - np.mean(N_obs))**2)
    
    aic, bic = aic_bic(len(N_obs), rss, 3)
    
    return {
        'name': 'A3_External_Drive',
        'equation': 'dN/dt = r·N - m·B_t·N + u·E_t',
        'params': {'r': float(r), 'm': float(m), 'u': float(u)},
        'rss': float(rss),
        'rmse': float(rmse),
        'r2': float(r2),
        'aic': float(aic),
        'bic': float(bic),
        'k': 3,
        'N_pred': N_pred,
    }


# ═══════════════════════════════════════════════════════════════
# 主程序
# ═══════════════════════════════════════════════════════════════

def fit_all_models(csv_path):
    print(f"Loading data: {csv_path}")
    df = load_data(csv_path)
    
    print(f"\nData: {len(df)} points")
    print(f"Population: {df['population'].min():.0f} → {df['population'].max():.0f}")
    print("="*70)
    
    # 拟合所有模型
    print("\n[1/3] Fitting Model A1: Exponential...")
    a1 = fit_model_a1(df)
    
    print("[2/3] Fitting Model A2: Richards (Generalized Logistic)...")
    a2 = fit_model_a2(df)
    
    print("[3/3] Fitting Model A3: External Drive...")
    a3 = fit_model_a3(df)
    
    results = [a1, a2, a3]
    
    # 按AIC排序
    results_sorted = sorted(results, key=lambda x: x['aic'])
    
    # 打印比较表
    print("\n" + "="*70)
    print("MODEL COMPARISON RESULTS")
    print("="*70)
    print(f"{'Model':<20} {'k':<4} {'R²':<10} {'RMSE':<12} {'AIC':<12} {'BIC':<12}")
    print("-"*70)
    for r in results_sorted:
        print(f"{r['name']:<20} {r['k']:<4} {r['r2']:<10.4f} {r['rmse']:<12.2f} {r['aic']:<12.2f} {r['bic']:<12.2f}")
    
    best = results_sorted[0]
    print("="*70)
    print(f"\n🏆 BEST MODEL: {best['name']}")
    print(f"    Equation: {best['equation']}")
    print(f"    Parameters:")
    for k, v in best['params'].items():
        print(f"      {k} = {v:.6f}")
    print(f"    R² = {best['r2']:.4f}, RMSE = {best['rmse']:.2f}")
    
    # 保存结果
    output_dir = Path('model_fit_results')
    output_dir.mkdir(exist_ok=True)
    
    comparison = {
        'best_model': best['name'],
        'all_models': [
            {
                'name': r['name'],
                'equation': r['equation'],
                'params': r['params'],
                'r2': r['r2'],
                'rmse': r['rmse'],
                'aic': r['aic'],
                'bic': r['bic'],
                'k': r['k'],
            }
            for r in results
        ]
    }
    
    with open(output_dir / 'population_model_comparison.json', 'w') as f:
        json.dump(comparison, f, indent=2)
    
    # 绘图
    t = df['generation'].values
    N_obs = df['population'].values
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 主图：所有模型比较
    ax = axes[0, 0]
    ax.plot(t, N_obs, 'ko-', label='Observed', linewidth=2, markersize=4)
    colors = ['blue', 'green', 'red']
    for r, color in zip(results, colors):
        ax.plot(t, r['N_pred'], '--', color=color, label=f"{r['name']} (R²={r['r2']:.3f})", linewidth=1.5)
    ax.set_xlabel('Generation')
    ax.set_ylabel('Population')
    ax.set_title('Population Model Comparison')
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    # 残差图
    ax = axes[0, 1]
    for r, color in zip(results, colors):
        resid = N_obs - r['N_pred']
        ax.plot(t, resid, 'o-', color=color, label=r['name'], alpha=0.7, markersize=3)
    ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax.set_xlabel('Generation')
    ax.set_ylabel('Residuals (Obs - Pred)')
    ax.set_title('Residuals')
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    # AIC/BIC比较
    ax = axes[1, 0]
    names = [r['name'].replace('A1_', '').replace('A2_', '').replace('A3_', '') for r in results]
    aics = [r['aic'] for r in results]
    bics = [r['bic'] for r in results]
    x = np.arange(len(names))
    width = 0.35
    ax.bar(x - width/2, aics, width, label='AIC', color='skyblue')
    ax.bar(x + width/2, bics, width, label='BIC', color='lightcoral')
    ax.set_ylabel('Information Criterion')
    ax.set_title('AIC/BIC Comparison (lower is better)')
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=15)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # 最佳模型特写
    ax = axes[1, 1]
    ax.plot(t, N_obs, 'ko-', label='Observed', linewidth=2, markersize=5)
    ax.plot(t, best['N_pred'], 'r--', label=f"{best['name']} (Best)", linewidth=2)
    ax.fill_between(t, best['N_pred'], alpha=0.2, color='red')
    ax.set_xlabel('Generation')
    ax.set_ylabel('Population')
    ax.set_title(f'Best Model: {best["name"]} (R² = {best["r2"]:.4f})')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'population_model_comparison.png', dpi=150)
    print(f"\n✅ Plot saved: {output_dir}/population_model_comparison.png")
    print(f"✅ Results saved: {output_dir}/population_model_comparison.json")
    
    return comparison


if __name__ == '__main__':
    import sys, glob
    
    csv_file = None
    patterns = ['logs/p3d/evolution.csv', '/home/admin/zeroclaw-labs/v18_1_experiments/*/evolution.csv']
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
    
    fit_all_models(csv_file)
