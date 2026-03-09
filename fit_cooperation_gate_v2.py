#!/usr/bin/env python3
"""
Layer C: Cooperation Gate 拟合脚本 v2
使用Sigmoid阈值函数

模型:
C(t) = σ((G(t) - θ) / τ)

其中:
- G(t) = w1·B_reward + w2·N_support - w3·S_cost - w4·M_cost
- θ = θ0 - θD·dna_collab - θA·akashic_prior
- σ(x) = 1/(1 + e^-x)

测试: 协作是否显示阈值行为（vs连续线性增加）
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import json
from pathlib import Path


def sigmoid(x):
    """Sigmoid函数"""
    return 1 / (1 + np.exp(-np.clip(x, -500, 500)))


def load_data(csv_path):
    """加载CSV数据"""
    return pd.read_csv(csv_path)


def cooperation_gate(G, theta, tau):
    """Cooperation gate函数"""
    return sigmoid((G - theta) / tau)


def compute_G(df):
    """
    计算协作收益G(t)
    使用代理变量
    """
    # Boss reward: 使用extinct_count的负值（extinct越多，reward越低）
    if 'extinct_count' in df.columns:
        max_univ = 128
        B_reward = 1.0 - df['extinct_count'].values / max_univ
    else:
        B_reward = np.ones(len(df)) * 0.5
    
    # Neighbor support: 用alive_universes和collaboration代理
    if 'alive_universes' in df.columns:
        N_support = df['alive_universes'].values / 128
    else:
        N_support = np.ones(len(df)) * 0.5
    
    # Signal cost: 用CDI反代理（高CDI = 高信号成本）
    if 'avg_cdi' in df.columns:
        S_cost = df['avg_cdi'].values
    else:
        S_cost = np.ones(len(df)) * 0.5
    
    # Movement cost: 用population密度代理
    if 'population' in df.columns:
        max_pop = 500
        pop = df['population'].values
        M_cost = np.clip(pop / max_pop, 0, 1)
    else:
        M_cost = np.ones(len(df)) * 0.3
    
    return B_reward, N_support, S_cost, M_cost


def model_predict(df, params):
    """
    预测协作强度
    params: [w1, w2, w3, w4, theta0, tau]
    """
    w1, w2, w3, w4, theta0, tau = params
    
    B_reward, N_support, S_cost, M_cost = compute_G(df)
    
    # G(t) = w1·B_reward + w2·N_support - w3·S_cost - w4·M_cost
    G = w1 * B_reward + w2 * N_support - w3 * S_cost - w4 * M_cost
    
    # C(t) = σ((G - θ0) / τ)
    C_pred = cooperation_gate(G, theta0, tau)
    
    return C_pred, G


def objective(params, df):
    """计算RMSE"""
    if 'avg_collaboration' not in df.columns:
        return 1e10
    
    C_observed = df['avg_collaboration'].values
    C_pred, _ = model_predict(df, params)
    
    rmse = np.sqrt(np.mean((C_pred - C_observed)**2))
    return rmse


def fit_model(csv_path):
    """拟合Cooperation Gate模型"""
    print(f"Loading data from: {csv_path}")
    df = load_data(csv_path)
    
    if 'avg_collaboration' not in df.columns:
        print("Warning: avg_collaboration not found in CSV. Skipping cooperation gate fitting.")
        return None
    
    print(f"Data range: {len(df)} points")
    print(f"Collaboration range: {df['avg_collaboration'].min():.4f} - {df['avg_collaboration'].max():.4f}")
    
    # 初始猜测
    initial_guess = [0.5, 0.5, 0.3, 0.2, 0.0, 0.5]
    
    # 边界
    bounds = [
        (0.0, 2.0),   # w1
        (0.0, 2.0),   # w2
        (0.0, 2.0),   # w3
        (0.0, 2.0),   # w4
        (-1.0, 1.0),  # theta0
        (0.01, 2.0),  # tau (temperature, must be > 0)
    ]
    
    print("Fitting Cooperation Gate model (v2)...")
    result = minimize(
        objective,
        initial_guess,
        args=(df,),
        method='L-BFGS-B',
        bounds=bounds,
        options={'maxiter': 1000}
    )
    
    w1, w2, w3, w4, theta0, tau = result.x
    
    # 计算拟合
    C_observed = df['avg_collaboration'].values
    C_pred, G = model_predict(df, result.x)
    
    rmse = np.sqrt(np.mean((C_pred - C_observed)**2))
    ss_res = np.sum((C_observed - C_pred)**2)
    ss_tot = np.sum((C_observed - np.mean(C_observed))**2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    
    # 确定阈值位置
    threshold_location = theta0
    
    # 测试阈值行为 vs 线性
    # 计算线性拟合的R²
    from scipy.stats import linregress
    slope, intercept, r_lin, _, _ = linregress(G, C_observed)
    r2_linear = r_lin**2
    
    threshold_behavior = r_squared > r2_linear + 0.05  # Sigmoid显著更好
    
    results = {
        'model': 'Cooperation Gate (Layer C) v2',
        'equation': 'C(t) = σ((G(t) - θ)/τ)',
        'G_definition': 'G = w1·B_reward + w2·N_support - w3·S_cost - w4·M_cost',
        'parameters': {
            'w1': {'value': float(w1), 'description': 'Boss reward weight'},
            'w2': {'value': float(w2), 'description': 'Neighbor support weight'},
            'w3': {'value': float(w3), 'description': 'Signal cost weight'},
            'w4': {'value': float(w4), 'description': 'Movement cost weight'},
            'theta0': {'value': float(theta0), 'description': 'Base threshold'},
            'tau': {'value': float(tau), 'description': 'Temperature (steepness)'},
        },
        'derived': {
            'threshold_location': float(threshold_location),
            'threshold_steepness': float(1/tau),
        },
        'behavior_test': {
            'sigmoid_r2': float(r_squared),
            'linear_r2': float(r2_linear),
            'threshold_behavior': bool(threshold_behavior),
            'interpretation': 'Threshold behavior' if threshold_behavior else 'Gradual behavior',
        },
        'fit_quality': {
            'RMSE': float(rmse),
            'R_squared': float(r_squared),
            'n_points': len(df),
        },
        'success': result.success,
    }
    
    print("\n" + "="*60)
    print("COOPERATION GATE FIT RESULTS (v2)")
    print("="*60)
    print(f"w1 (Boss reward):    {w1:.4f}")
    print(f"w2 (Neighbor supp):  {w2:.4f}")
    print(f"w3 (Signal cost):    {w3:.4f}")
    print(f"w4 (Movement cost):  {w4:.4f}")
    print(f"θ0 (Base threshold): {theta0:.4f}")
    print(f"τ (Temperature):     {tau:.4f}")
    print("-"*60)
    print(f"阈值位置: {threshold_location:.4f}")
    print(f"阈值陡峭度: {1/tau:.4f}")
    print("-"*60)
    print(f"行为测试:")
    print(f"  Sigmoid R²: {r_squared:.4f}")
    print(f"  Linear R²:  {r2_linear:.4f}")
    print(f"  结论: {'阈值行为' if threshold_behavior else '渐进行为'}")
    print("-"*60)
    print(f"RMSE: {rmse:.4f}")
    print(f"R²:   {r_squared:.4f}")
    print("="*60)
    
    # 保存结果
    output_dir = Path('model_fit_results')
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / 'cooperation_gate_fit.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ Results saved to: {output_dir}/cooperation_gate_fit.json")
    
    # 绘图
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # 上图：时间序列
    ax1 = axes[0]
    t = df['generation'].values
    ax1.plot(t, C_observed, 'b-', label='Observed', linewidth=2)
    ax1.plot(t, C_pred, 'r--', label='Model', linewidth=2)
    ax1.axhline(y=0.5, color='g', linestyle=':', alpha=0.5, label='C=0.5')
    ax1.set_xlabel('Generation')
    ax1.set_ylabel('Collaboration')
    ax1.set_title(f'Cooperation Gate Fit (R² = {r_squared:.4f})')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(-0.05, 1.05)
    
    # 下图：Sigmoid曲线
    ax2 = axes[1]
    G_sorted = np.sort(G)
    C_sigmoid = cooperation_gate(G_sorted, theta0, tau)
    ax2.plot(G_sorted, C_sigmoid, 'r-', linewidth=2, label='Sigmoid fit')
    ax2.scatter(G, C_observed, alpha=0.5, s=30, label='Observed')
    ax2.axvline(x=theta0, color='g', linestyle=':', alpha=0.5, label=f'θ = {theta0:.3f}')
    ax2.set_xlabel('G(t) - Net Benefit')
    ax2.set_ylabel('C(t) - Collaboration')
    ax2.set_title(f'Cooperation Threshold (τ = {tau:.3f})')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(-0.05, 1.05)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'cooperation_gate_fit.png', dpi=150)
    print(f"✅ Plot saved to: {output_dir}/cooperation_gate_fit.png")
    
    return results


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
    
    fit_model(csv_file)
