#!/usr/bin/env python3
"""
Layer C: Cooperation Gate 拟合脚本

模型:
C(t) = σ((G(t) - θ(t)) / τ)

其中:
G(t) = w₁·boss_reward + w₂·neighbor_support - w₃·signal_cost - w₄·movement_cost
θ(t) = θ₀ - θ_D·dna_collab - θ_A·akashic_prior

这是一个门控函数，不是主方程。
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit  # sigmoid function
import matplotlib.pyplot as plt
import json
from pathlib import Path


def sigmoid(x):
    """Sigmoid function"""
    return expit(x)


def load_data(csv_path):
    """加载并预处理CSV数据"""
    df = pd.read_csv(csv_path)
    return df


def cooperation_gate(t, params, boss_reward_func, neighbor_support_func, 
                     signal_cost_func, movement_cost_func, 
                     dna_collab_func, akashic_prior_func):
    """
    Cooperation gate model
    
    C(t) = σ((G(t) - θ(t)) / τ)
    """
    w1, w2, w3, w4, theta_0, theta_D, theta_A, tau = params
    
    # 计算协作净收益 G(t)
    boss_reward = boss_reward_func(t)
    neighbor_support = neighbor_support_func(t)
    signal_cost = signal_cost_func(t)
    movement_cost = movement_cost_func(t)
    
    G = w1 * boss_reward + w2 * neighbor_support - w3 * signal_cost - w4 * movement_cost
    
    # 计算门槛 θ(t)
    dna_collab = dna_collab_func(t)
    akashic_prior = akashic_prior_func(t)
    
    theta = theta_0 - theta_D * dna_collab - theta_A * akashic_prior
    
    # 计算协作概率
    if tau < 0.001:
        tau = 0.001
    
    C = sigmoid((G - theta) / tau)
    
    return C


def interpolate_functions(df):
    """创建从CSV数据的插值函数"""
    from scipy.interpolate import interp1d
    
    t = df['generation'].values
    
    # Boss奖励代理：使用boss难度或击败计数
    if 'boss_difficulty' in df.columns:
        boss_reward = df['boss_difficulty'].values / 10.0  # 归一化到[0,1]
    elif 'extinct_count' in df.columns:
        boss_reward = 1.0 - (df['extinct_count'].values / 128.0)
    else:
        boss_reward = np.zeros_like(t)
    boss_reward_func = interp1d(t, boss_reward, kind='linear', fill_value='extrapolate')
    
    # 邻居支持代理：使用collaboration_index或population_density
    if 'avg_collaboration' in df.columns:
        neighbor_support = df['avg_collaboration'].values
    elif 'population' in df.columns:
        # 假设中等密度最有利于协作
        pop = df['population'].values
        neighbor_support = np.exp(-((pop - 250) / 100) ** 2)  # 高斯函数，250最优
    else:
        neighbor_support = np.zeros_like(t)
    neighbor_support_func = interp1d(t, neighbor_support, kind='linear', fill_value='extrapolate')
    
    # 信号成本代理：使用coherence的逆（信号需要能量）
    if 'coherence' in df.columns:
        signal_cost = 1.0 - df['coherence'].values
    else:
        signal_cost = np.ones_like(t) * 0.5
    signal_cost_func = interp1d(t, signal_cost, kind='linear', fill_value='extrapolate')
    
    # 移动成本代理：假设随时间累积
    movement_cost = np.minimum(t / 10000, 1.0)  # 线性增长，饱和于1
    movement_cost_func = interp1d(t, movement_cost, kind='linear', fill_value='extrapolate')
    
    # DNA协作倾向代理：使用collaboration_index的变化率
    if 'avg_collaboration' in df.columns:
        dna_collab = df['avg_collaboration'].values
    else:
        dna_collab = np.ones_like(t) * 0.5
    dna_collab_func = interp1d(t, dna_collab, kind='linear', fill_value='extrapolate')
    
    # 阿卡西经验代理：使用generation作为累积代理
    if 'akashic_shares' in df.columns:
        akashic_prior = df['akashic_shares'].values
    else:
        akashic_prior = np.minimum(t / 50000, 1.0)  # 累积效应
    akashic_prior_func = interp1d(t, akashic_prior, kind='linear', fill_value='extrapolate')
    
    return (boss_reward_func, neighbor_support_func, signal_cost_func, 
            movement_cost_func, dna_collab_func, akashic_prior_func)


def objective(params, df, funcs):
    """计算模型与观测的负对数似然"""
    boss_reward_func, neighbor_support_func, signal_cost_func, \
    movement_cost_func, dna_collab_func, akashic_prior_func = funcs
    
    t = df['generation'].values
    
    # 观测到的协作强度
    if 'avg_collaboration' in df.columns:
        C_observed = df['avg_collaboration'].values
    else:
        # 用CDI作为协作代理
        C_observed = df['avg_cdi'].values * 0.5
    
    # 计算模型预测
    C_model = np.array([cooperation_gate(ti, params, boss_reward_func, 
                                        neighbor_support_func, signal_cost_func, 
                                        movement_cost_func, dna_collab_func, 
                                        akashic_prior_func) for ti in t])
    
    # 计算误差（MSE）
    mse = np.mean((C_model - C_observed)**2)
    return mse


def fit_model(csv_path):
    """拟合Cooperation Gate模型"""
    print(f"Loading data from: {csv_path}")
    df = load_data(csv_path)
    
    # 创建插值函数
    funcs = interpolate_functions(df)
    boss_reward_func, neighbor_support_func, signal_cost_func, \
    movement_cost_func, dna_collab_func, akashic_prior_func = funcs
    
    # 初始参数猜测
    # [w1, w2, w3, w4, theta_0, theta_D, theta_A, tau]
    initial_guess = [0.5, 0.5, 0.3, 0.2, 0.5, 0.3, 0.3, 0.1]
    
    # 参数边界
    bounds = [
        (0.0, 2.0),    # w1: Boss奖励权重
        (0.0, 2.0),    # w2: 邻居支持权重
        (0.0, 2.0),    # w3: 信号成本权重
        (0.0, 2.0),    # w4: 移动成本权重
        (0.0, 1.0),    # theta_0: 基础门槛
        (0.0, 1.0),    # theta_D: DNA降低门槛系数
        (0.0, 1.0),    # theta_A: 阿卡西降低门槛系数
        (0.01, 1.0),   # tau: 温度参数
    ]
    
    print("Fitting cooperation gate model...")
    result = minimize(
        objective,
        initial_guess,
        args=(df, funcs),
        method='L-BFGS-B',
        bounds=bounds,
        options={'maxiter': 1000}
    )
    
    if result.success:
        print("✅ Fitting successful!")
    else:
        print(f"⚠️ Fitting warning: {result.message}")
    
    # 提取拟合参数
    w1, w2, w3, w4, theta_0, theta_D, theta_A, tau = result.x
    
    # 计算最终拟合质量
    t = df['generation'].values
    if 'avg_collaboration' in df.columns:
        C_observed = df['avg_collaboration'].values
    else:
        C_observed = df['avg_cdi'].values * 0.5
    
    C_model = np.array([cooperation_gate(ti, result.x, *funcs) for ti in t])
    
    rmse = np.sqrt(np.mean((C_model - C_observed)**2))
    ss_res = np.sum((C_observed - C_model)**2)
    ss_tot = np.sum((C_observed - np.mean(C_observed))**2)
    r_squared = 1 - (ss_res / ss_tot)
    
    # 输出结果
    results = {
        'model': 'Cooperation Gate (Layer C)',
        'equation': 'C(t) = σ((G(t) - θ(t)) / τ)',
        'G_definition': 'G = w₁·boss_reward + w₂·neighbor_support - w₃·signal_cost - w₄·movement_cost',
        'theta_definition': 'θ = θ₀ - θ_D·dna_collab - θ_A·akashic_prior',
        'parameters': {
            'w1': {'value': float(w1), 'description': 'Boss奖励权重'},
            'w2': {'value': float(w2), 'description': '邻居支持权重'},
            'w3': {'value': float(w3), 'description': '信号成本权重'},
            'w4': {'value': float(w4), 'description': '移动成本权重'},
            'theta_0': {'value': float(theta_0), 'description': '基础协作门槛'},
            'theta_D': {'value': float(theta_D), 'description': 'DNA协作降低门槛'},
            'theta_A': {'value': float(theta_A), 'description': '阿卡西经验降低门槛'},
            'tau': {'value': float(tau), 'description': '探索-利用温度'},
        },
        'fit_quality': {
            'RMSE': float(rmse),
            'R_squared': float(r_squared),
            'n_points': len(df),
        },
        'success': result.success,
        'message': result.message,
    }
    
    print("\n" + "="*60)
    print("COOPERATION GATE FIT RESULTS")
    print("="*60)
    print(f"w₁ (Boss奖励):     {w1:.6f}")
    print(f"w₂ (邻居支持):     {w2:.6f}")
    print(f"w₃ (信号成本):     {w3:.6f}")
    print(f"w₄ (移动成本):     {w4:.6f}")
    print(f"θ₀ (基础门槛):     {theta_0:.6f}")
    print(f"θ_D (DNA降低):     {theta_D:.6f}")
    print(f"θ_A (阿卡西降低):  {theta_A:.6f}")
    print(f"τ (温度):          {tau:.6f}")
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
    
    # 绘制拟合图
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 左上：拟合曲线
    ax1 = axes[0, 0]
    ax1.plot(t, C_observed, 'b-', label='Observed', linewidth=2)
    ax1.plot(t, C_model, 'r--', label='Model', linewidth=2)
    ax1.set_xlabel('Generation')
    ax1.set_ylabel('Cooperation Rate')
    ax1.set_title(f'Cooperation Gate Fit (R² = {r_squared:.4f})')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 1)
    
    # 右上：门槛θ(t)时间序列
    ax2 = axes[0, 1]
    theta_t = theta_0 - theta_D * dna_collab_func(t) - theta_A * akashic_prior_func(t)
    ax2.plot(t, theta_t, 'g-', linewidth=2)
    ax2.set_xlabel('Generation')
    ax2.set_ylabel('Threshold θ(t)')
    ax2.set_title('Collaboration Threshold Over Time')
    ax2.grid(True, alpha=0.3)
    
    # 左下：净收益G(t)
    ax3 = axes[1, 0]
    G_t = (w1 * boss_reward_func(t) + 
           w2 * neighbor_support_func(t) - 
           w3 * signal_cost_func(t) - 
           w4 * movement_cost_func(t))
    ax3.plot(t, G_t, 'purple', linewidth=2)
    ax3.axhline(y=theta_0, color='r', linestyle='--', label=f'θ₀ = {theta_0:.3f}')
    ax3.set_xlabel('Generation')
    ax3.set_ylabel('Net Benefit G(t)')
    ax3.set_title('Collaboration Net Benefit')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 右下：Sigmoid曲线（静态展示）
    ax4 = axes[1, 1]
    G_range = np.linspace(-2, 2, 100)
    C_range = sigmoid((G_range - theta_0) / tau)
    ax4.plot(G_range, C_range, 'orange', linewidth=2)
    ax4.axvline(x=theta_0, color='r', linestyle='--', label=f'θ₀ = {theta_0:.3f}')
    ax4.set_xlabel('G - θ')
    ax4.set_ylabel('Cooperation Probability C')
    ax4.set_title(f'Sigmoid Gate (τ = {tau:.3f})')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'cooperation_gate_fit.png', dpi=150)
    print(f"✅ Plot saved to: {output_dir}/cooperation_gate_fit.png")
    
    return results


if __name__ == '__main__':
    import sys
    
    csv_paths = [
        'logs/p3d/evolution.csv',
        '/home/admin/zeroclaw-labs/v18_1_experiments/*/evolution.csv',
    ]
    
    csv_file = None
    for pattern in csv_paths:
        import glob
        matches = glob.glob(pattern)
        if matches:
            csv_file = matches[0]
            break
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    
    if not csv_file or not Path(csv_file).exists():
        print("Error: No CSV file found.")
        print("Usage: python fit_cooperation_gate.py <path/to/evolution.csv>")
        sys.exit(1)
    
    results = fit_model(csv_file)
