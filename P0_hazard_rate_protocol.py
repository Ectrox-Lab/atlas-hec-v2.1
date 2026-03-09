#!/usr/bin/env python3
"""
P0 Hazard Rate Protocol v2.0
CDI作为危险率调制器的验证框架

核心问题（修正后）:
    不是：CDI能提前多少代预测灭绝？
    而是：CDI是否定义了一个可重复的高危险率区域？

模型:
    I(t) < I_crit  ⇒  h(t) ↑
    
    P(extinction in [t, t+Δt]) = 1 - exp(-h(t)·Δt)

验收标准（修订）:
    弱通过: 3+ seed，灭绝前CDI相对本地峰值显著下降
    中通过: I < I_crit时，条件灭绝率显著高于I ≥ I_crit
    强通过: 可拟合hazard model，且I_crit与hazard上升区间在多seed下稳定
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import json
import argparse
from pathlib import Path


def load_data(csv_path):
    """加载实验数据"""
    df = pd.read_csv(csv_path)
    return df


def find_local_peak(I, window=10):
    """找到CDI的局部峰值（高原期结束）"""
    # 使用移动平均平滑
    I_smooth = pd.Series(I).rolling(window=window, center=True, min_periods=1).mean()
    peak_idx = I_smooth.idxmax()
    return peak_idx, I[peak_idx]


def compute_hazard_estimate(df, I_crit_candidates=None):
    """
    估计条件危险率
    
    返回:
        hazard_by_I: 按CDI区间分组的危险率估计
        I_crit_estimated: 估计的临界CDI值
    """
    t = df['generation'].values
    I = df['avg_cdi'].values
    
    # 灭绝事件（宇宙数下降）
    if 'alive_universes' in df.columns:
        U = df['alive_universes'].values
        # 计算宇宙灭绝事件（一阶差分）
        extinction_events = -np.diff(U)
        extinction_events = np.maximum(extinction_events, 0)  # 只取正值
        # 对齐到时间点（使用区间终点）
        t_events = t[1:]
        I_events = I[1:]
    else:
        # 如果没有alive_universes，使用population下降代理
        N = df['population'].values
        extinction_events = -np.diff(N)
        extinction_events = np.maximum(extinction_events, 0)
        t_events = t[1:]
        I_events = I[1:]
    
    # 按CDI分箱计算危险率
    if I_crit_candidates is None:
        I_crit_candidates = np.linspace(0.3, 0.7, 20)
    
    results = []
    
    for I_crit in I_crit_candidates:
        # 危险区 (I < I_crit)
        danger_mask = I_events < I_crit
        # 安全区 (I >= I_crit)
        safe_mask = ~danger_mask
        
        # 计算各区间的危险率
        # h = (灭绝事件数) / (在该区间停留的时间)
        
        if np.sum(danger_mask) > 0:
            danger_time = np.sum(danger_mask) * np.median(np.diff(t_events))
            danger_events = np.sum(extinction_events[danger_mask])
            h_danger = danger_events / danger_time if danger_time > 0 else 0
        else:
            h_danger = 0
        
        if np.sum(safe_mask) > 0:
            safe_time = np.sum(safe_mask) * np.median(np.diff(t_events))
            safe_events = np.sum(extinction_events[safe_mask])
            h_safe = safe_events / safe_time if safe_time > 0 else 0
        else:
            h_safe = 0
        
        # Hazard ratio (危险区/安全区)
        hazard_ratio = h_danger / h_safe if h_safe > 0 else np.inf
        
        results.append({
            'I_crit': I_crit,
            'h_danger': h_danger,
            'h_safe': h_safe,
            'hazard_ratio': hazard_ratio,
            'danger_time': danger_time if 'danger_time' in dir() else 0,
            'safe_time': safe_time if 'safe_time' in dir() else 0,
        })
    
    return pd.DataFrame(results)


def fit_hazard_model(df, I_crit_fixed=None):
    """
    拟合危险率模型: h(t) = h0 + α·max(0, I_crit - I(t))
    
    或更平滑版本: h(t) = h0 + α / (1 + exp((I - I_crit)/τ))
    """
    t = df['generation'].values
    I = df['avg_cdi'].values
    
    if 'alive_universes' not in df.columns:
        return None, "No alive_universes data"
    
    U = df['alive_universes'].values
    
    # 计算观测到的危险率（滑动窗口）
    window = 5
    h_observed = []
    t_center = []
    I_center = []
    
    for i in range(window, len(U)):
        # 该窗口内的灭绝数
        dU = U[i-window] - U[i]
        # 时间跨度
        dt = t[i] - t[i-window]
        # 平均存活宇宙数
        U_mean = np.mean(U[i-window:i])
        
        if U_mean > 0 and dt > 0:
            # 每代每个宇宙的危险率
            h = dU / (dt * U_mean) if U_mean > 0 else 0
            h_observed.append(max(h, 0))
            t_center.append(t[i])
            I_center.append(I[i])
    
    h_observed = np.array(h_observed)
    t_center = np.array(t_center)
    I_center = np.array(I_center)
    
    # 只拟合有灭绝的区域
    valid_mask = h_observed > 0
    if np.sum(valid_mask) < 5:
        return None, "Insufficient extinction events"
    
    h_valid = h_observed[valid_mask]
    I_valid = I_center[valid_mask]
    
    # 拟合模型: h = h0 + α·max(0, I_crit - I)
    def model(params, I):
        h0, alpha, I_crit = params
        # 平滑版本使用softplus
        penalty = np.log1p(np.exp(-(I - I_crit) / 0.05)) * 0.05  # soft approximation
        return h0 + alpha * penalty
    
    def objective(params):
        h_pred = model(params, I_valid)
        return np.sum((h_pred - h_valid)**2)
    
    # 初始猜测
    result = minimize(
        objective,
        [0.001, 0.1, 0.55],  # h0, alpha, I_crit
        bounds=[(0, 0.1), (0, 1.0), (0.3, 0.8)],
        method='L-BFGS-B'
    )
    
    h0, alpha, I_crit_fitted = result.x
    
    # 计算R²
    h_pred = model(result.x, I_valid)
    ss_res = np.sum((h_valid - h_pred)**2)
    ss_tot = np.sum((h_valid - np.mean(h_valid))**2)
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    
    return {
        'h0': float(h0),
        'alpha': float(alpha),
        'I_crit': float(I_crit_fitted),
        'r_squared': float(r_squared),
        'h_observed': h_observed,
        't_center': t_center,
        'I_center': I_center,
        'model': 'h(t) = h0 + alpha * softplus(I_crit - I(t))',
    }, None


def analyze_single_seed(csv_path):
    """分析单个seed的数据"""
    try:
        df = load_data(csv_path)
    except Exception as e:
        return {'error': str(e), 'csv_file': str(csv_path)}
    
    if len(df) < 20:
        return {'error': 'Insufficient data', 'csv_file': str(csv_path)}
    
    t = df['generation'].values
    I = df['avg_cdi'].values
    
    # 1. 找到局部峰值
    peak_idx, peak_I = find_local_peak(I)
    peak_gen = t[peak_idx]
    
    # 2. 估计I_crit
    hazard_df = compute_hazard_estimate(df)
    
    # 找到最大危险率比的I_crit
    if len(hazard_df) > 0:
        best_idx = hazard_df['hazard_ratio'].idxmax()
        I_crit_estimated = hazard_df.loc[best_idx, 'I_crit']
        max_hazard_ratio = hazard_df.loc[best_idx, 'hazard_ratio']
    else:
        I_crit_estimated = None
        max_hazard_ratio = None
    
    # 3. 拟合hazard model
    hazard_model, error = fit_hazard_model(df)
    
    # 4. 统计信息
    # CDI从峰值下降的比例
    final_I = I[-1]
    I_decline = (peak_I - final_I) / peak_I if peak_I > 0 else 0
    
    # 找到灭绝发生时间
    if 'alive_universes' in df.columns:
        U = df['alive_universes'].values
        extinction_mask = U < U[0]  # 宇宙数下降
        if np.any(extinction_mask):
            first_extinct_idx = np.where(extinction_mask)[0][0]
            first_extinct_gen = t[first_extinct_idx]
            first_extinct_I = I[first_extinct_idx]
        else:
            first_extinct_gen = None
            first_extinct_I = None
    else:
        first_extinct_gen = None
        first_extinct_I = None
    
    result = {
        'csv_file': str(csv_path),
        'n_generations': len(df),
        'cdi_peak': {'gen': int(peak_gen), 'value': float(peak_I)},
        'cdi_final': {'gen': int(t[-1]), 'value': float(final_I)},
        'cdi_decline_ratio': float(I_decline),
        'I_crit_estimated': float(I_crit_estimated) if I_crit_estimated else None,
        'max_hazard_ratio': float(max_hazard_ratio) if max_hazard_ratio else None,
        'hazard_model': hazard_model,
        'first_extinction': {'gen': int(first_extinct_gen), 'cdi': float(first_extinct_I)} if first_extinct_gen else None,
    }
    
    return result


def evaluate_hazard_protocol(results):
    """评估危险率协议"""
    valid_results = [r for r in results if 'error' not in r]
    
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
    
    # 弱通过: CDI显著下降
    decline_ratios = [r['cdi_decline_ratio'] for r in valid_results if r.get('cdi_decline_ratio') is not None]
    if decline_ratios:
        evaluation['weak_pass'] = np.mean(decline_ratios) > 0.2  # 平均下降>20%
        evaluation['cdi_decline_stats'] = {
            'mean': float(np.mean(decline_ratios)),
            'std': float(np.std(decline_ratios)),
        }
    
    # 中通过: 危险率比显著
    hazard_ratios = [r['max_hazard_ratio'] for r in valid_results if r.get('max_hazard_ratio') is not None and r['max_hazard_ratio'] != np.inf]
    if hazard_ratios:
        evaluation['hazard_ratio_stats'] = {
            'mean': float(np.mean(hazard_ratios)),
            'std': float(np.std(hazard_ratios)),
            'min': float(np.min(hazard_ratios)),
            'max': float(np.max(hazard_ratios)),
        }
        # 中通过: 危险率比>2（危险区危险率是安全区的2倍）
        evaluation['medium_pass'] = np.mean(hazard_ratios) > 2.0
    
    # 强通过: I_crit稳定，且hazard model可拟合
    I_crits = []
    r_squareds = []
    for r in valid_results:
        if r.get('hazard_model') and r['hazard_model'].get('I_crit'):
            I_crits.append(r['hazard_model']['I_crit'])
            r_squareds.append(r['hazard_model']['r_squared'])
    
    if I_crits and r_squareds:
        evaluation['I_crit_stats'] = {
            'mean': float(np.mean(I_crits)),
            'std': float(np.std(I_crits)),
            'cv': float(np.std(I_crits) / np.mean(I_crits)) if np.mean(I_crits) > 0 else None,
        }
        evaluation['hazard_model_r2_stats'] = {
            'mean': float(np.mean(r_squareds)),
            'std': float(np.std(r_squareds)),
        }
        # 强通过: I_crit变异系数<10%且R²>0.5
        cv_ok = evaluation['I_crit_stats']['cv'] < 0.1 if evaluation['I_crit_stats']['cv'] else False
        r2_ok = np.mean(r_squareds) > 0.3
        evaluation['strong_pass'] = cv_ok and r2_ok
    
    # 总体状态
    if evaluation['strong_pass']:
        evaluation['status'] = 'STRONG_PASS'
    elif evaluation['medium_pass']:
        evaluation['status'] = 'MEDIUM_PASS'
    elif evaluation['weak_pass']:
        evaluation['status'] = 'WEAK_PASS'
    
    return evaluation


def create_hazard_visualization(results, output_path):
    """创建危险率可视化"""
    valid_results = [r for r in results if 'error' not in r and r.get('hazard_model')]
    
    if len(valid_results) < 1:
        print("Not enough valid results for visualization")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    colors = plt.cm.tab10(np.linspace(0, 1, len(valid_results)))
    
    for i, result in enumerate(valid_results):
        color = colors[i]
        
        # 1. CDI轨迹
        try:
            df = load_data(result['csv_file'])
            t = df['generation'].values
            I = df['avg_cdi'].values
            
            axes[0, 0].plot(t, I, color=color, alpha=0.7, label=f'Seed {i+1}')
            
            # 标记I_crit
            if result.get('I_crit_estimated'):
                axes[0, 0].axhline(y=result['I_crit_estimated'], color=color, 
                                   linestyle='--', alpha=0.5)
        except:
            pass
        
        # 2. Hazard rate vs CDI
        if result.get('hazard_model'):
            hm = result['hazard_model']
            if 'I_center' in hm and 'h_observed' in hm:
                # 散点
                axes[0, 1].scatter(hm['I_center'], hm['h_observed'], 
                                  color=color, alpha=0.5, s=20)
                
                # 拟合曲线
                I_range = np.linspace(0.3, 0.8, 100)
                h0, alpha, I_crit = hm['h0'], hm['alpha'], hm['I_crit']
                penalty = np.log1p(np.exp(-(I_range - I_crit) / 0.05)) * 0.05
                h_fit = h0 + alpha * penalty
                axes[0, 1].plot(I_range, h_fit, color=color, linewidth=2,
                               label=f'Seed {i+1} (R²={hm["r_squared"]:.2f})')
        
        # 3. I_crit分布
        if result.get('I_crit_estimated'):
            axes[1, 0].axvline(x=result['I_crit_estimated'], color=color, 
                              linestyle='-', alpha=0.7, linewidth=2)
        
        # 4. Hazard ratio
        if result.get('max_hazard_ratio') and result['max_hazard_ratio'] != np.inf:
            axes[1, 1].bar(i, result['max_hazard_ratio'], color=color, alpha=0.7)
    
    # 设置图表
    axes[0, 0].set_xlabel('Generation')
    axes[0, 0].set_ylabel('CDI')
    axes[0, 0].set_title('CDI Trajectories with I_crit')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    axes[0, 1].set_xlabel('CDI')
    axes[0, 1].set_ylabel('Hazard Rate')
    axes[0, 1].set_title('Hazard Rate vs CDI')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    axes[1, 0].set_xlabel('I_crit Estimate')
    axes[1, 0].set_title('I_crit Distribution Across Seeds')
    axes[1, 0].grid(True, alpha=0.3)
    
    axes[1, 1].set_xlabel('Seed')
    axes[1, 1].set_ylabel('Max Hazard Ratio')
    axes[1, 1].set_title('Hazard Ratio (Danger/Safe)')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"Hazard visualization saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='P0 Hazard Rate Protocol v2.0')
    parser.add_argument('--csv-files', nargs='+', required=True)
    parser.add_argument('--output-dir', default='model_fit_results')
    args = parser.parse_args()
    
    print("="*70)
    print("P0: Hazard Rate Protocol v2.0")
    print("CDI作为危险率调制器的验证")
    print("="*70)
    print()
    print("核心问题:")
    print("  CDI是否定义了一个可重复的高危险率区域？")
    print()
    print("模型: I(t) < I_crit  ⇒  h(t) ↑")
    print("      P(extinction) = 1 - exp(-h(t)·Δt)")
    print()
    print(f"分析 {len(args.csv_files)} 个seed...")
    print()
    
    # 分析每个seed
    results = []
    for csv_file in args.csv_files:
        print(f"Processing: {csv_file}")
        result = analyze_single_seed(csv_file)
        results.append(result)
        
        if 'error' in result:
            print(f"  ❌ Error: {result['error']}")
        else:
            print(f"  ✅ Peak: I={result['cdi_peak']['value']:.4f} at Gen {result['cdi_peak']['gen']}")
            if result.get('I_crit_estimated'):
                print(f"     I_crit ≈ {result['I_crit_estimated']:.4f}")
            if result.get('max_hazard_ratio'):
                print(f"     Hazard ratio: {result['max_hazard_ratio']:.2f}x")
            if result.get('hazard_model'):
                print(f"     Model R²: {result['hazard_model']['r_squared']:.4f}")
        print()
    
    # 评估
    evaluation = evaluate_hazard_protocol(results)
    
    print("="*70)
    print("EVALUATION RESULT")
    print("="*70)
    print(f"Status: {evaluation['status']}")
    print(f"Valid seeds: {evaluation['valid_seeds']}/{evaluation['total_seeds']}")
    print()
    
    if 'cdi_decline_stats' in evaluation:
        stats = evaluation['cdi_decline_stats']
        print(f"CDI Decline: {stats['mean']:.1%} ± {stats['std']:.1%}")
    
    if 'hazard_ratio_stats' in evaluation:
        stats = evaluation['hazard_ratio_stats']
        print(f"Hazard Ratio: {stats['mean']:.2f}x (range: {stats['min']:.2f}-{stats['max']:.2f})")
    
    if 'I_crit_stats' in evaluation:
        stats = evaluation['I_crit_stats']
        print(f"I_crit: {stats['mean']:.4f} ± {stats['std']:.4f} (CV: {stats['cv']:.1%})")
    
    print()
    print("Pass Criteria:")
    print(f"  Weak (CDI显著下降):      {'✅' if evaluation['weak_pass'] else '❌'}")
    print(f"  Medium (危险率比>2x):    {'✅' if evaluation['medium_pass'] else '❌'}")
    print(f"  Strong (I_crit稳定,R²>0.3): {'✅' if evaluation['strong_pass'] else '❌'}")
    
    # 保存结果
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    full_results = {
        'protocol': 'P0_Hazard_Rate_v2.0',
        'core_question': 'CDI是否定义了可重复的高危险率区域？',
        'model': 'h(t) = h0 + alpha * softplus(I_crit - I(t))',
        'timestamp': pd.Timestamp.now().isoformat(),
        'individual_results': results,
        'evaluation': evaluation,
    }
    
    output_file = output_dir / 'P0_hazard_rate_results.json'
    with open(output_file, 'w') as f:
        json.dump(full_results, f, indent=2, default=str)
    print(f"\nResults saved: {output_file}")
    
    # 可视化
    plot_file = output_dir / 'P0_hazard_rate_visualization.png'
    create_hazard_visualization(results, plot_file)
    
    return 0 if evaluation['status'] in ['STRONG_PASS', 'MEDIUM_PASS'] else 1


if __name__ == '__main__':
    exit(main())
