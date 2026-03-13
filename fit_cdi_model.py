#!/usr/bin/env python3
"""
Layer B: CDI Dynamics 拟合脚本

模型:
dI/dt = (λ₁·M + λ₂·S + λ₃·C) × (1 - I/K_I) - λ₄·V_E - λ₅·B

这是 RyanX 创新定律（资源受限版）的正式化。
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
    return df


def cdi_model(I, t, params, M_func, S_func, C_func, V_E_func, B_func):
    """
    CDI dynamics ODE
    
    dI/dt = (λ₁·M + λ₂·S + λ₃·C) × (1 - I/K_I) - λ₄·V_E - λ₅·B
    """
    lambda_1, lambda_2, lambda_3, lambda_4, lambda_5, K_I = params
    
    # 获取时变参数
    M = M_func(t)
    S = S_func(t)
    C = C_func(t)
    V_E = V_E_func(t)
    B = B_func(t)
    
    # 防止K_I为0
    if K_I < 0.01:
        K_I = 0.01
    
    # 计算dI/dt
    growth_term = (lambda_1 * M + lambda_2 * S + lambda_3 * C) * (1 - I / K_I)
    penalty_term = lambda_4 * V_E + lambda_5 * B
    
    dIdt = growth_term - penalty_term
    
    # 限制I在[0, 1]范围内
    if I <= 0 and dIdt < 0:
        dIdt = 0
    if I >= 1 and dIdt > 0:
        dIdt = 0
    
    return dIdt


def interpolate_functions(df):
    """创建从CSV数据的插值函数"""
    from scipy.interpolate import interp1d
    
    t = df['generation'].values
    
    # M(t): 记忆深度 - 使用CDI自身作为代理（或mem_ret如果存在）
    if 'mem_ret' in df.columns:
        M_values = df['mem_ret'].values
    else:
        # 用CDI的累积平滑版本作为记忆代理
        M_values = np.convolve(df['avg_cdi'].values, np.ones(10)/10, mode='same')
    M_func = interp1d(t, M_values, kind='linear', fill_value='extrapolate')
    
    # S(t): 同步质量 - 使用coherence或pha_coh
    if 'coherence' in df.columns:
        S_values = df['coherence'].values
    elif 'pha_coh' in df.columns:
        S_values = df['pha_coh'].values
    else:
        # 用population的变异系数倒数作为同步代理
        S_values = np.ones_like(t) * 0.5
    S_func = interp1d(t, S_values, kind='linear', fill_value='extrapolate')
    
    # C(t): 协作强度
    if 'avg_collaboration' in df.columns:
        C_values = df['avg_collaboration'].values
    else:
        C_values = np.zeros_like(t)
    C_func = interp1d(t, C_values, kind='linear', fill_value='extrapolate')
    
    # V_E(t): 能量方差代理
    if 'energy_var' in df.columns:
        V_E_values = df['energy_var'].values
    elif 'coherence' in df.columns:
        # 相干越低，方差越高
        V_E_values = 1.0 - df['coherence'].values
    else:
        V_E_values = np.zeros_like(t)
    V_E_func = interp1d(t, V_E_values, kind='linear', fill_value='extrapolate')
    
    # B(t): Boss扰动
    if 'boss_disturbance' in df.columns:
        B_values = df['boss_disturbance'].values
    elif 'extinct_count' in df.columns:
        B_values = df['extinct_count'].values / 128.0
    else:
        B_values = np.zeros_like(t)
    B_func = interp1d(t, B_values, kind='linear', fill_value='extrapolate')
    
    return M_func, S_func, C_func, V_E_func, B_func


def objective(params, df, M_func, S_func, C_func, V_E_func, B_func):
    """计算模型与观测的RMSE"""
    t = df['generation'].values
    I_observed = df['avg_cdi'].values
    
    # 数值积分
    I0 = I_observed[0]
    t_span = t - t[0]
    
    I_model = odeint(cdi_model, I0, t_span,
                     args=(params, M_func, S_func, C_func, V_E_func, B_func))
    I_model = np.clip(I_model.flatten(), 0, 1)
    
    # 计算RMSE
    rmse = np.sqrt(np.mean((I_model - I_observed)**2))
    return rmse


def check_superlinear(df, I_observed):
    """检查是否出现超线性增长"""
    # 计算 dI/dt
    dI = np.diff(I_observed)
    dt = np.diff(df['generation'].values)
    dIdt = dI / dt
    
    # 检查 dI/dt > a + b*I (b > 0)
    # 线性回归: dIdt = a + b*I
    I_mid = (I_observed[:-1] + I_observed[1:]) / 2
    
    # 只取正增长部分
    positive_mask = dIdt > 0
    if np.sum(positive_mask) < 10:
        return None, "Insufficient positive growth data"
    
    I_pos = I_mid[positive_mask]
    dIdt_pos = dIdt[positive_mask]
    
    # 线性回归
    A = np.vstack([np.ones_like(I_pos), I_pos]).T
    a, b = np.linalg.lstsq(A, dIdt_pos, rcond=None)[0]
    
    # R²
    ss_res = np.sum((dIdt_pos - (a + b * I_pos))**2)
    ss_tot = np.sum((dIdt_pos - np.mean(dIdt_pos))**2)
    r_squared = 1 - (ss_res / ss_tot)
    
    return {'a': a, 'b': b, 'R_squared': r_squared, 'is_superlinear': b > 0 and r_squared > 0.5}, None


def fit_model(csv_path):
    """拟合CDI模型"""
    print(f"Loading data from: {csv_path}")
    df = load_data(csv_path)
    
    # 创建插值函数
    M_func, S_func, C_func, V_E_func, B_func = interpolate_functions(df)
    
    # 初始参数猜测
    # [lambda_1, lambda_2, lambda_3, lambda_4, lambda_5, K_I]
    initial_guess = [0.1, 0.1, 0.1, 0.05, 0.05, 0.8]
    
    # 参数边界
    bounds = [
        (0.0, 1.0),    # lambda_1: 记忆贡献
        (0.0, 1.0),    # lambda_2: 同步贡献
        (0.0, 1.0),    # lambda_3: 协作贡献
        (0.0, 1.0),    # lambda_4: 方差惩罚
        (0.0, 1.0),    # lambda_5: Boss惩罚
        (0.1, 1.0),    # K_I: CDI上限
    ]
    
    print("Fitting CDI model...")
    result = minimize(
        objective,
        initial_guess,
        args=(df, M_func, S_func, C_func, V_E_func, B_func),
        method='L-BFGS-B',
        bounds=bounds,
        options={'maxiter': 1000}
    )
    
    if result.success:
        print("✅ Fitting successful!")
    else:
        print(f"⚠️ Fitting warning: {result.message}")
    
    # 提取拟合参数
    lambda_1, lambda_2, lambda_3, lambda_4, lambda_5, K_I = result.x
    
    # 计算最终RMSE和R²
    t = df['generation'].values
    I_observed = df['avg_cdi'].values
    t_span = t - t[0]
    
    I_model = odeint(cdi_model, I_observed[0], t_span,
                     args=(result.x, M_func, S_func, C_func, V_E_func, B_func))
    I_model = np.clip(I_model.flatten(), 0, 1)
    
    rmse = np.sqrt(np.mean((I_model - I_observed)**2))
    ss_res = np.sum((I_observed - I_model)**2)
    ss_tot = np.sum((I_observed - np.mean(I_observed))**2)
    r_squared = 1 - (ss_res / ss_tot)
    
    # 检查超线性
    superlinear_result, error = check_superlinear(df, I_observed)
    
    # 输出结果
    results = {
        'model': 'CDI Dynamics (Layer B)',
        'equation': 'dI/dt = (λ₁·M + λ₂·S + λ₃·C) × (1 - I/K_I) - λ₄·V_E - λ₅·B',
        'parameters': {
            'lambda_1': {'value': float(lambda_1), 'description': '记忆对CDI的贡献'},
            'lambda_2': {'value': float(lambda_2), 'description': '同步对CDI的贡献'},
            'lambda_3': {'value': float(lambda_3), 'description': '协作对CDI的贡献'},
            'lambda_4': {'value': float(lambda_4), 'description': '能量方差惩罚'},
            'lambda_5': {'value': float(lambda_5), 'description': 'Boss扰动惩罚'},
            'K_I': {'value': float(K_I), 'description': 'CDI承载上限（预期~0.8）'},
        },
        'fit_quality': {
            'RMSE': float(rmse),
            'R_squared': float(r_squared),
            'n_points': len(df),
        },
        'superlinear_check': superlinear_result if superlinear_result else {'error': error},
        'success': result.success,
        'message': result.message,
    }
    
    print("\n" + "="*60)
    print("CDI MODEL FIT RESULTS")
    print("="*60)
    print(f"λ₁ (记忆贡献):     {lambda_1:.6f}")
    print(f"λ₂ (同步贡献):     {lambda_2:.6f}")
    print(f"λ₃ (协作贡献):     {lambda_3:.6f}")
    print(f"λ₄ (方差惩罚):     {lambda_4:.6f}")
    print(f"λ₅ (Boss惩罚):     {lambda_5:.6f}")
    print(f"K_I (CDI上限):     {K_I:.6f}")
    print("-"*60)
    print(f"RMSE: {rmse:.4f}")
    print(f"R²:   {r_squared:.4f}")
    if superlinear_result:
        print(f"超线性检查: b={superlinear_result['b']:.6f}, R²={superlinear_result['R_squared']:.4f}")
        print(f"是否超线性: {'是' if superlinear_result['is_superlinear'] else '否'}")
    print("="*60)
    
    # 保存结果
    output_dir = Path('model_fit_results')
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / 'cdi_model_fit.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ Results saved to: {output_dir}/cdi_model_fit.json")
    
    # 绘制拟合图
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    # 上图：拟合曲线
    ax1 = axes[0]
    ax1.plot(t, I_observed, 'b-', label='Observed CDI', linewidth=2)
    ax1.plot(t, I_model, 'r--', label='Model CDI', linewidth=2)
    ax1.axhline(y=K_I, color='g', linestyle=':', label=f'K_I = {K_I:.3f}')
    ax1.set_xlabel('Generation')
    ax1.set_ylabel('CDI')
    ax1.set_title(f'CDI Model Fit (R² = {r_squared:.4f})')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 1)
    
    # 中图：残差
    ax2 = axes[1]
    residuals = I_observed - I_model
    ax2.plot(t, residuals, 'g-', linewidth=1)
    ax2.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Generation')
    ax2.set_ylabel('Residuals')
    ax2.set_title('Residuals')
    ax2.grid(True, alpha=0.3)
    
    # 下图：增长速率分析
    ax3 = axes[2]
    if len(I_observed) > 1:
        dI = np.diff(I_observed)
        dt = np.diff(t)
        dIdt = dI / dt
        ax3.plot(t[:-1], dIdt, 'purple', label='dI/dt observed', linewidth=1)
        if superlinear_result:
            I_mid = (I_observed[:-1] + I_observed[1:]) / 2
            ax3.plot(I_mid, superlinear_result['a'] + superlinear_result['b'] * I_mid, 
                    'orange', linestyle='--', label=f"Fit: dI/dt = {superlinear_result['a']:.4f} + {superlinear_result['b']:.4f}·I")
        ax3.set_xlabel('Generation')
        ax3.set_ylabel('dI/dt')
        ax3.set_title('CDI Growth Rate Analysis')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'cdi_model_fit.png', dpi=150)
    print(f"✅ Plot saved to: {output_dir}/cdi_model_fit.png")
    
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
        print("Usage: python fit_cdi_model.py <path/to/evolution.csv>")
        sys.exit(1)
    
    results = fit_model(csv_file)
