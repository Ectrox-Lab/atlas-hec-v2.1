#!/usr/bin/env python3
"""
Layer B: CDI Dynamics 拟合脚本 v2
使用差分形式，避免ODE数值问题

模型 (RyanX Innovation Law):
ΔI/Δt = (α·L + β·T)(1 - I/K_I) - γ·σ²

其中:
- L(t): 突触学习密度 (Synaptic learning density)
- T(t): 转录激活 (Transcriptional activity)
- K_I: CDI饱和上限 (K_I = f(K_space, K_resource, K_synaptic))
- σ²(t): 能量方差

测试超线性假设: dI/dt > a + b·I (b > 0)
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import json
from pathlib import Path


def load_data(csv_path):
    """加载CSV数据"""
    return pd.read_csv(csv_path)


def model_predict(df, params, include_saturation=True):
    """
    预测CDI演化
    params: [alpha, beta, K_I, gamma]
    """
    alpha, beta, K_I, gamma = params
    
    I_observed = df['avg_cdi'].values
    t = df['generation'].values
    
    # 代理变量
    # L(t): 突触学习密度 - 用population和collaboration代理
    # 突触密度 ∝ population / max_population
    max_pop = 500  # hardcoded max in main.rs
    pop = df['population'].values if 'population' in df.columns else np.ones(len(df)) * 1000
    L = np.clip(pop / max_pop, 0, 1)
    
    # T(t): 转录激活 - 用collaboration代理（协作时转录活跃）
    T = df['avg_collaboration'].values if 'avg_collaboration' in df.columns else np.zeros(len(df))
    T = np.clip(T, 0, 1)
    
    # σ²(t): 能量方差代理
    sigma2 = 1.0 - I_observed  # CDI越高，方差越低
    
    # 差分预测
    I_pred = np.zeros_like(I_observed, dtype=float)
    I_pred[0] = I_observed[0]
    
    for i in range(1, len(t)):
        dt = t[i] - t[i-1]
        
        # dI/dt = (α·L + β·T)(1 - I/K_I) - γ·σ²
        if include_saturation:
            growth = (alpha * L[i] + beta * T[i]) * (1 - I_pred[i-1] / K_I)
        else:
            # 无饱和版本：测试超线性
            growth = (alpha * L[i] + beta * T[i]) * I_pred[i-1]
        
        penalty = gamma * sigma2[i]
        dI = (growth - penalty) * dt
        
        I_pred[i] = I_pred[i-1] + dI
        # 边界约束
        I_pred[i] = np.clip(I_pred[i], 0, 1)
    
    return I_pred


def objective(params, df):
    """计算RMSE"""
    I_observed = df['avg_cdi'].values
    I_pred = model_predict(df, params)
    rmse = np.sqrt(np.mean((I_pred - I_observed)**2))
    return rmse


def test_superlinear(df):
    """测试超线性假设: dI/dt > a + b·I (b > 0)"""
    I = df['avg_cdi'].values
    t = df['generation'].values
    
    # 计算dI/dt
    dI_dt = np.diff(I) / np.diff(t)
    I_mid = (I[:-1] + I[1:]) / 2
    
    # 线性回归: dI/dt = a + b·I
    from scipy.stats import linregress
    slope, intercept, r_value, p_value, std_err = linregress(I_mid, dI_dt)
    
    return {
        'b': float(slope),
        'a': float(intercept),
        'r_squared': float(r_value**2),
        'p_value': float(p_value),
        'superlinear_supported': bool(slope > 0 and p_value < 0.05)
    }


def fit_model(csv_path):
    """拟合CDI模型"""
    print(f"Loading data from: {csv_path}")
    df = load_data(csv_path)
    
    print(f"Data range: {len(df)} points")
    print(f"CDI range: {df['avg_cdi'].min():.4f} - {df['avg_cdi'].max():.4f}")
    
    # 初始猜测
    initial_guess = [0.1, 0.05, 0.8, 0.02]
    
    # 边界
    bounds = [
        (0.0, 1.0),   # alpha
        (0.0, 1.0),   # beta
        (0.3, 1.5),   # K_I: CDI上限（在0.3-1.5之间）
        (0.0, 0.5),   # gamma
    ]
    
    print("Fitting CDI model (v2 - difference form)...")
    result = minimize(
        objective,
        initial_guess,
        args=(df,),
        method='L-BFGS-B',
        bounds=bounds,
        options={'maxiter': 1000}
    )
    
    alpha, beta, K_I, gamma = result.x
    
    # 计算拟合质量
    I_observed = df['avg_cdi'].values
    I_pred = model_predict(df, result.x)
    
    rmse = np.sqrt(np.mean((I_pred - I_observed)**2))
    ss_res = np.sum((I_observed - I_pred)**2)
    ss_tot = np.sum((I_observed - np.mean(I_observed))**2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    
    # 超线性测试
    superlinear = test_superlinear(df)
    
    # 计算K_I分解（估算）
    # K_I = f(K_space, K_resource, K_synaptic)
    max_pop = 500
    syn_per_cell = 15
    
    K_synaptic_est = min(K_I, 1.0)  # 突触层面的上限
    K_resource_eff = K_synaptic_est * (pop := df['population'].values).mean() / max_pop
    
    results = {
        'model': 'CDI Dynamics (Layer B) v2',
        'equation': 'dI/dt = (α·L + β·T)(1 - I/K_I) - γ·σ²',
        'parameters': {
            'alpha': {'value': float(alpha), 'description': '突触学习系数 (Synaptic learning)'},
            'beta': {'value': float(beta), 'description': '转录激活系数 (Transcriptional)'},
            'K_I': {'value': float(K_I), 'description': 'CDI饱和上限 (Innovation capacity)'},
            'gamma': {'value': float(gamma), 'description': '能量方差惩罚系数'},
        },
        'K_decomposition': {
            'K_I_emergent': float(K_I),
            'K_synaptic_hardcoded': syn_per_cell,
            'K_population_hardcoded': max_pop,
            'K_synaptic_contribution': float(K_synaptic_est),
            'K_resource_contribution': float(K_resource_eff),
        },
        'fit_quality': {
            'RMSE': float(rmse),
            'R_squared': float(r_squared),
            'n_points': len(df),
        },
        'superlinear_test': superlinear,
        'success': result.success,
    }
    
    print("\n" + "="*60)
    print("CDI MODEL FIT RESULTS (v2)")
    print("="*60)
    print(f"α (突触学习):        {alpha:.6f}")
    print(f"β (转录激活):        {beta:.6f}")
    print(f"K_I (CDI上限):       {K_I:.4f}")
    print(f"γ (方差惩罚):        {gamma:.6f}")
    print("-"*60)
    print(f"K_I 分解:")
    print(f"  涌现值: {K_I:.4f}")
    print(f"  Hardcoded突触: {syn_per_cell}/cell")
    print(f"  Hardcoded种群: {max_pop}")
    print("-"*60)
    print(f"超线性测试:")
    print(f"  b = {superlinear['b']:.6f} (b>0 表示超线性)")
    print(f"  R² = {superlinear['r_squared']:.4f}")
    print(f"  p = {superlinear['p_value']:.6f}")
    print(f"  超线性支持: {'✅ YES' if superlinear['superlinear_supported'] else '❌ NO'}")
    print("-"*60)
    print(f"RMSE: {rmse:.6f}")
    print(f"R²:   {r_squared:.4f}")
    print("="*60)
    
    # 保存结果
    output_dir = Path('model_fit_results')
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / 'cdi_model_fit.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ Results saved to: {output_dir}/cdi_model_fit.json")
    
    # 绘图
    t = df['generation'].values
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # 上图：CDI拟合
    ax1 = axes[0]
    ax1.plot(t, I_observed, 'b-', label='Observed CDI', linewidth=2)
    ax1.plot(t, I_pred, 'r--', label='Model', linewidth=2)
    ax1.axhline(y=K_I, color='g', linestyle=':', label=f'K_I = {K_I:.3f}')
    ax1.set_xlabel('Generation')
    ax1.set_ylabel('CDI (avg_cdi)')
    ax1.set_title(f'CDI Model Fit (R² = {r_squared:.4f})')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 1)
    
    # 下图：dI/dt vs I (超线性测试)
    ax2 = axes[1]
    dI_dt = np.diff(I_observed) / np.diff(t)
    I_mid = (I_observed[:-1] + I_observed[1:]) / 2
    ax2.scatter(I_mid, dI_dt, alpha=0.5, s=30)
    
    # 拟合线
    x_fit = np.linspace(I_mid.min(), I_mid.max(), 100)
    y_fit = superlinear['a'] + superlinear['b'] * x_fit
    ax2.plot(x_fit, y_fit, 'r-', linewidth=2, 
             label=f'dI/dt = {superlinear["a"]:.4f} + {superlinear["b"]:.4f}·I')
    ax2.axhline(y=0, color='gray', linestyle=':', alpha=0.5)
    ax2.set_xlabel('CDI (I)')
    ax2.set_ylabel('dI/dt')
    ax2.set_title('Superlinearity Test: dI/dt vs I')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'cdi_model_fit.png', dpi=150)
    print(f"✅ Plot saved to: {output_dir}/cdi_model_fit.png")
    
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
