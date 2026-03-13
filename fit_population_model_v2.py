#!/usr/bin/env python3
"""
Layer A: Population / Survival Dynamics 拟合脚本 v2
使用差分形式而非ODE，避免数值稳定性问题

模型:
ΔN/Δt = N(t) × (r_eff(t) - m_eff(t))

r_eff(t) = r₀ + r_D·D(t) + r_A·A(t) + r_C·C(t)
m_eff(t) = m₀ + m_B·B(t) + m_V·V_E(t)
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import json
from pathlib import Path


def load_data(csv_path):
    """加载并预处理CSV数据"""
    df = pd.read_csv(csv_path)
    return df


def model_predict(df, params):
    """
    使用差分形式预测种群变化
    返回预测的N(t)序列
    """
    r0, r_D, r_A, r_C, m0, m_B, m_V = params
    
    N_observed = df['population'].values
    t = df['generation'].values
    
    # 代理变量
    # D(t): DNA适应度 - 使用CDI
    D = df['avg_cdi'].values if 'avg_cdi' in df.columns else np.ones(len(df)) * 0.5
    
    # A(t): 阿卡西boost - 使用alive_universes / 128
    max_univ = 128
    A = df['alive_universes'].values / max_univ if 'alive_universes' in df.columns else np.ones(len(df))
    
    # C(t): 协作强度
    C = df['avg_collaboration'].values if 'avg_collaboration' in df.columns else np.zeros(len(df))
    
    # B(t): Boss压力
    if 'extinct_count' in df.columns:
        B = df['extinct_count'].values / max_univ
    else:
        B = np.zeros(len(df))
    
    # V_E(t): 能量方差代理
    V_E = 1.0 - D  # CDI越高，方差越低
    
    # 计算有效出生率和死亡率
    r_eff = r0 + r_D * D + r_A * A + r_C * C
    m_eff = m0 + m_B * B + m_V * V_E
    
    # 差分预测
    N_pred = np.zeros_like(N_observed, dtype=float)
    N_pred[0] = N_observed[0]
    
    for i in range(1, len(t)):
        dt = t[i] - t[i-1]
        # dN/dt = N * (r - m)
        dN = N_pred[i-1] * (r_eff[i] - m_eff[i]) * dt
        N_pred[i] = N_pred[i-1] + dN
        
        # 非负约束
        if N_pred[i] < 0:
            N_pred[i] = 0
    
    return N_pred


def objective(params, df):
    """计算模型与观测的RMSE"""
    N_observed = df['population'].values
    N_pred = model_predict(df, params)
    
    rmse = np.sqrt(np.mean((N_pred - N_observed)**2))
    return rmse


def fit_model(csv_path):
    """拟合Population模型"""
    print(f"Loading data from: {csv_path}")
    df = load_data(csv_path)
    
    print(f"Data range: {len(df)} points")
    print(f"Population range: {df['population'].min():.0f} - {df['population'].max():.0f}")
    
    # 初始参数猜测（基于数据尺度调整）
    # 种群约17000，变化缓慢，出生率和死亡率应该很小
    initial_guess = [0.001, 0.01, 0.01, 0.01, 0.001, 0.01, 0.01]
    
    # 参数边界
    bounds = [
        (0.0, 0.01),    # r0: 基础出生率（很小）
        (0.0, 0.1),     # r_D
        (0.0, 0.1),     # r_A
        (0.0, 0.1),     # r_C
        (0.0, 0.01),    # m0: 基础死亡率（很小）
        (0.0, 0.1),     # m_B
        (0.0, 0.1),     # m_V
    ]
    
    print("Fitting population model (v2 - difference form)...")
    result = minimize(
        objective,
        initial_guess,
        args=(df,),
        method='L-BFGS-B',
        bounds=bounds,
        options={'maxiter': 1000, 'ftol': 1e-8}
    )
    
    if result.success:
        print("✅ Fitting successful!")
    else:
        print(f"⚠️ Fitting warning: {result.message}")
    
    # 提取拟合参数
    r0, r_D, r_A, r_C, m0, m_B, m_V = result.x
    
    # 计算最终拟合
    N_observed = df['population'].values
    N_pred = model_predict(df, result.x)
    
    rmse = np.sqrt(np.mean((N_pred - N_observed)**2))
    ss_res = np.sum((N_observed - N_pred)**2)
    ss_tot = np.sum((N_observed - np.mean(N_observed))**2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    
    # 计算出生率和死亡率解释力
    t = df['generation'].values
    D = df['avg_cdi'].values if 'avg_cdi' in df.columns else np.ones(len(df)) * 0.5
    A = df['alive_universes'].values / 128 if 'alive_universes' in df.columns else np.ones(len(df))
    C = df['avg_collaboration'].values if 'avg_collaboration' in df.columns else np.zeros(len(df))
    B = df['extinct_count'].values / 128 if 'extinct_count' in df.columns else np.zeros(len(df))
    V_E = 1.0 - D
    
    r_eff = r0 + r_D * D + r_A * A + r_C * C
    m_eff = m0 + m_B * B + m_V * V_E
    
    # 输出结果
    results = {
        'model': 'Population Dynamics (Layer A) v2',
        'method': 'Difference form (not ODE)',
        'parameters': {
            'r0': {'value': float(r0), 'description': '基础出生率'},
            'r_D': {'value': float(r_D), 'description': 'DNA适应增益系数'},
            'r_A': {'value': float(r_A), 'description': '阿卡西增益系数'},
            'r_C': {'value': float(r_C), 'description': '协作增益系数'},
            'm0': {'value': float(m0), 'description': '基础死亡率'},
            'm_B': {'value': float(m_B), 'description': 'Boss压力系数'},
            'm_V': {'value': float(m_V), 'description': '能量方差惩罚系数'},
        },
        'derived': {
            'avg_r_eff': float(np.mean(r_eff)),
            'avg_m_eff': float(np.mean(m_eff)),
            'net_growth_rate': float(np.mean(r_eff - m_eff)),
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
    print("POPULATION MODEL FIT RESULTS (v2)")
    print("="*60)
    print(f"r0 (基础出生率):     {r0:.8f}")
    print(f"r_D (DNA增益):       {r_D:.6f}")
    print(f"r_A (阿卡西增益):    {r_A:.6f}")
    print(f"r_C (协作增益):      {r_C:.6f}")
    print(f"m0 (基础死亡率):     {m0:.8f}")
    print(f"m_B (Boss压力):      {m_B:.6f}")
    print(f"m_V (方差惩罚):      {m_V:.6f}")
    print("-"*60)
    print(f"平均有效出生率:      {np.mean(r_eff):.8f}")
    print(f"平均有效死亡率:      {np.mean(m_eff):.8f}")
    print(f"净增长率:            {np.mean(r_eff - m_eff):.8f}")
    print("-"*60)
    print(f"RMSE: {rmse:.2f}")
    print(f"R²:   {r_squared:.4f}")
    print("="*60)
    
    # 保存结果
    output_dir = Path('model_fit_results')
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / 'population_model_fit.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ Results saved to: {output_dir}/population_model_fit.json")
    
    # 绘制拟合图
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # 上图：拟合曲线
    ax1 = axes[0]
    ax1.plot(t, N_observed, 'b-', label='Observed', linewidth=2)
    ax1.plot(t, N_pred, 'r--', label='Model', linewidth=2)
    ax1.set_xlabel('Generation')
    ax1.set_ylabel('Population')
    ax1.set_title(f'Population Model Fit (R² = {r_squared:.4f})')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 下图：出生率vs死亡率
    ax2 = axes[1]
    ax2.plot(t, r_eff, 'g-', label='Birth rate (r_eff)', linewidth=1.5)
    ax2.plot(t, m_eff, 'r-', label='Death rate (m_eff)', linewidth=1.5)
    ax2.plot(t, r_eff - m_eff, 'k--', label='Net growth', linewidth=1)
    ax2.axhline(y=0, color='gray', linestyle=':', alpha=0.5)
    ax2.set_xlabel('Generation')
    ax2.set_ylabel('Rate')
    ax2.set_title('Birth vs Death Rates')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'population_model_fit.png', dpi=150)
    print(f"✅ Plot saved to: {output_dir}/population_model_fit.png")
    
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
        print("Usage: python fit_population_model_v2.py <path/to/evolution.csv>")
        sys.exit(1)
    
    results = fit_model(csv_file)
