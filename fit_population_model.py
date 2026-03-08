#!/usr/bin/env python3
"""
Layer A: Population / Survival Dynamics 拟合脚本

模型:
dN/dt = N(t) × (r_eff(t) - m_eff(t))

r_eff(t) = r₀ + r_D·D(t) + r_A·A(t) + r_C·C(t)
m_eff(t) = m₀ + m_B·B(t) + m_V·V_E(t)
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
from scipy.integrate import odeint
import matplotlib.pyplot as plt
import json
from pathlib import Path


def load_data(csv_path):
    """加载并预处理CSV数据"""
    df = pd.read_csv(csv_path)
    
    # 需要的列
    required_cols = ['generation', 'population', 'avg_cdi', 'avg_collaboration', 
                     'alive_universes', 'coherence']
    
    # 检查列存在
    for col in required_cols:
        if col not in df.columns:
            print(f"Warning: Column '{col}' not found in CSV")
    
    return df


def population_model(N, t, params, D_func, A_func, C_func, B_func, V_E_func):
    """
    Population dynamics ODE
    
    dN/dt = N × (r_eff - m_eff)
    """
    r0, r_D, r_A, r_C, m0, m_B, m_V = params
    
    # 获取时变参数
    D = D_func(t)
    A = A_func(t)
    C = C_func(t)
    B = B_func(t)
    V_E = V_E_func(t)
    
    r_eff = r0 + r_D * D + r_A * A + r_C * C
    m_eff = m0 + m_B * B + m_V * V_E
    
    dNdt = N * (r_eff - m_eff)
    return dNdt


def interpolate_functions(df):
    """创建从CSV数据的插值函数"""
    from scipy.interpolate import interp1d
    
    t = df['generation'].values
    
    # DNA适应度代理：使用avg_cdi作为代理
    D_func = interp1d(t, df['avg_cdi'].values, kind='linear', fill_value='extrapolate')
    
    # 阿卡西boost代理：使用alive_universes / max_universes
    max_univ = 128  # 从代码中得知
    akashic_proxy = df['alive_universes'].values / max_univ
    A_func = interp1d(t, akashic_proxy, kind='linear', fill_value='extrapolate')
    
    # 协作强度
    C_func = interp1d(t, df['avg_collaboration'].values, kind='linear', fill_value='extrapolate')
    
    # Boss压力代理：使用extinct_count或能量方差
    if 'extinct_count' in df.columns:
        B_proxy = df['extinct_count'].values / max_univ
    else:
        B_proxy = np.zeros_like(t)
    B_func = interp1d(t, B_proxy, kind='linear', fill_value='extrapolate')
    
    # 能量方差代理：使用coherence的逆（相干越低，方差越高）
    if 'coherence' in df.columns:
        V_E_proxy = 1.0 - df['coherence'].values
    else:
        V_E_proxy = np.zeros_like(t)
    V_E_func = interp1d(t, V_E_proxy, kind='linear', fill_value='extrapolate')
    
    return D_func, A_func, C_func, B_func, V_E_func


def objective(params, df, D_func, A_func, C_func, B_func, V_E_func):
    """计算模型与观测的RMSE"""
    t = df['generation'].values
    N_observed = df['population'].values
    
    # 数值积分
    N0 = N_observed[0]
    t_span = t - t[0]  # 从0开始
    
    N_model = odeint(population_model, N0, t_span, 
                     args=(params, D_func, A_func, C_func, B_func, V_E_func))
    N_model = N_model.flatten()
    
    # 计算RMSE
    rmse = np.sqrt(np.mean((N_model - N_observed)**2))
    return rmse


def fit_model(csv_path):
    """拟合Population模型"""
    print(f"Loading data from: {csv_path}")
    df = load_data(csv_path)
    
    # 创建插值函数
    D_func, A_func, C_func, B_func, V_E_func = interpolate_functions(df)
    
    # 初始参数猜测
    # [r0, r_D, r_A, r_C, m0, m_B, m_V]
    initial_guess = [0.01, 0.1, 0.1, 0.1, 0.01, 0.1, 0.1]
    
    # 参数边界（防止发散）
    bounds = [
        (0.0, 0.5),    # r0
        (0.0, 1.0),    # r_D
        (0.0, 1.0),    # r_A
        (0.0, 1.0),    # r_C
        (0.0, 0.5),    # m0
        (0.0, 1.0),    # m_B
        (0.0, 1.0),    # m_V
    ]
    
    print("Fitting population model...")
    result = minimize(
        objective,
        initial_guess,
        args=(df, D_func, A_func, C_func, B_func, V_E_func),
        method='L-BFGS-B',
        bounds=bounds,
        options={'maxiter': 1000}
    )
    
    if result.success:
        print("✅ Fitting successful!")
    else:
        print(f"⚠️ Fitting warning: {result.message}")
    
    # 提取拟合参数
    r0, r_D, r_A, r_C, m0, m_B, m_V = result.x
    
    # 计算最终RMSE和R²
    t = df['generation'].values
    N_observed = df['population'].values
    t_span = t - t[0]
    N_model = odeint(population_model, N_observed[0], t_span,
                     args=(result.x, D_func, A_func, C_func, B_func, V_E_func))
    N_model = N_model.flatten()
    
    rmse = np.sqrt(np.mean((N_model - N_observed)**2))
    ss_res = np.sum((N_observed - N_model)**2)
    ss_tot = np.sum((N_observed - np.mean(N_observed))**2)
    r_squared = 1 - (ss_res / ss_tot)
    
    # 输出结果
    results = {
        'model': 'Population Dynamics (Layer A)',
        'parameters': {
            'r0': {'value': float(r0), 'description': '基础出生率'},
            'r_D': {'value': float(r_D), 'description': 'DNA适应增益系数'},
            'r_A': {'value': float(r_A), 'description': '阿卡西增益系数'},
            'r_C': {'value': float(r_C), 'description': '协作增益系数'},
            'm0': {'value': float(m0), 'description': '基础死亡率'},
            'm_B': {'value': float(m_B), 'description': 'Boss压力系数'},
            'm_V': {'value': float(m_V), 'description': '能量方差惩罚系数'},
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
    print("POPULATION MODEL FIT RESULTS")
    print("="*60)
    print(f"r0 (基础出生率):     {r0:.6f}")
    print(f"r_D (DNA增益):       {r_D:.6f}")
    print(f"r_A (阿卡西增益):    {r_A:.6f}")
    print(f"r_C (协作增益):      {r_C:.6f}")
    print(f"m0 (基础死亡率):     {m0:.6f}")
    print(f"m_B (Boss压力):      {m_B:.6f}")
    print(f"m_V (方差惩罚):      {m_V:.6f}")
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
    ax1.plot(t, N_model, 'r--', label='Model', linewidth=2)
    ax1.set_xlabel('Generation')
    ax1.set_ylabel('Population')
    ax1.set_title(f'Population Model Fit (R² = {r_squared:.4f})')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 下图：残差
    ax2 = axes[1]
    residuals = N_observed - N_model
    ax2.plot(t, residuals, 'g-', linewidth=1)
    ax2.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Generation')
    ax2.set_ylabel('Residuals (Observed - Model)')
    ax2.set_title('Residuals')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'population_model_fit.png', dpi=150)
    print(f"✅ Plot saved to: {output_dir}/population_model_fit.png")
    
    return results


if __name__ == '__main__':
    import sys
    
    # 查找CSV文件
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
        print("Usage: python fit_population_model.py <path/to/evolution.csv>")
        sys.exit(1)
    
    results = fit_model(csv_file)
