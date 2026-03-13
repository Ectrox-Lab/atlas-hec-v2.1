#!/usr/bin/env python3
"""
5-Seed实验结果分析器
自动生成P0 Final Report所需的所有统计数据
"""

import pandas as pd
import numpy as np
from scipy import stats
import json
import argparse
from pathlib import Path
import sys


def load_all_seeds(csv_files):
    """加载所有seed的数据"""
    data = {}
    for csv_file in csv_files:
        seed_name = Path(csv_file).stem
        try:
            df = pd.read_csv(csv_file)
            data[seed_name] = df
        except Exception as e:
            print(f"Error loading {csv_file}: {e}")
    return data


def compute_hazard_rate(df, window=5):
    """计算滑动窗口危险率"""
    if 'alive_universes' not in df.columns:
        return None, None, None
    
    t = df['generation'].values
    U = df['alive_universes'].values
    I = df['avg_cdi'].values
    
    h_list = []
    t_list = []
    I_list = []
    
    for i in range(window, len(U)):
        dU = U[i-window] - U[i]  # 灭绝数
        dt = t[i] - t[i-window]   # 时间跨度
        U_mean = np.mean(U[i-window:i])  # 平均存活数
        
        if U_mean > 0 and dt > 0:
            h = dU / (dt * U_mean)  # 每代每个宇宙的危险率
            h_list.append(max(h, 0))
            t_list.append(t[i])
            I_list.append(I[i])
    
    return np.array(h_list), np.array(t_list), np.array(I_list)


def fit_hazard_model(I, h):
    """拟合hazard model: h = h0 + alpha * max(0, I_crit - I)"""
    # 使用平滑近似
    def softplus(x, tau=0.05):
        return np.log1p(np.exp(x/tau)) * tau
    
    def model(params, I):
        h0, alpha, I_crit = params
        return h0 + alpha * softplus(I_crit - I)
    
    def objective(params):
        h_pred = model(params, I)
        return np.sum((h_pred - h)**2)
    
    # 初始猜测和边界
    result = None
    best_r2 = -np.inf
    
    for I_crit_init in np.linspace(0.45, 0.60, 10):
        try:
            from scipy.optimize import minimize
            res = minimize(
                objective,
                [0.001, 0.01, I_crit_init],
                bounds=[(0, 0.1), (0, 1.0), (0.40, 0.70)],
                method='L-BFGS-B'
            )
            
            h_pred = model(res.x, I)
            ss_res = np.sum((h - h_pred)**2)
            ss_tot = np.sum((h - np.mean(h))**2)
            r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
            
            if r2 > best_r2:
                best_r2 = r2
                result = res
        except:
            continue
    
    if result is None:
        return None
    
    h0, alpha, I_crit = result.x
    return {
        'h0': h0,
        'alpha': alpha,
        'I_crit': I_crit,
        'r_squared': best_r2,
    }


def analyze_seed(seed_name, df):
    """分析单个seed"""
    result = {'seed': seed_name}
    
    t = df['generation'].values
    I = df['avg_cdi'].values
    
    # 1. CDI峰值
    peak_idx = np.argmax(I)
    result['cdi_peak'] = {
        'gen': int(t[peak_idx]),
        'value': float(I[peak_idx])
    }
    
    # 2. 危险率分析
    h, t_h, I_h = compute_hazard_rate(df)
    
    if h is not None and len(h) > 0:
        # 只使用有灭绝的时段
        valid_mask = h > 0
        if np.sum(valid_mask) >= 5:
            h_valid = h[valid_mask]
            I_valid = I_h[valid_mask]
            
            # 拟合hazard model
            model = fit_hazard_model(I_valid, h_valid)
            if model:
                result['hazard_model'] = model
                result['I_crit'] = model['I_crit']
            else:
                result['I_crit'] = None
        else:
            result['I_crit'] = None
    else:
        result['I_crit'] = None
    
    # 3. 首次灭绝
    if 'alive_universes' in df.columns:
        U = df['alive_universes'].values
        extinction_mask = U < U[0]
        if np.any(extinction_mask):
            first_idx = np.where(extinction_mask)[0][0]
            result['first_extinction'] = {
                'gen': int(t[first_idx]),
                'cdi': float(I[first_idx]),
                'universes': int(U[first_idx])
            }
        else:
            result['first_extinction'] = None
    else:
        result['first_extinction'] = None
    
    # 4. CDI最终值
    result['cdi_final'] = {
        'gen': int(t[-1]),
        'value': float(I[-1])
    }
    
    return result


def compute_hazard_ratio(df, I_crit):
    """计算危险区vs安全区的危险率比"""
    if 'alive_universes' not in df.columns:
        return None
    
    t = df['generation'].values
    U = df['alive_universes'].values
    I = df['avg_cdi'].values
    
    # 计算每个区间的危险率
    # 安全区: I >= I_crit
    safe_mask = I >= I_crit
    danger_mask = I < I_crit
    
    # 计算各区间的灭绝率和暴露
    results = {}
    
    for name, mask in [('safe', safe_mask), ('danger', danger_mask)]:
        if np.sum(mask) < 2:
            results[name] = None
            continue
        
        # 在该区间的灭绝事件
        U_masked = U[mask]
        I_masked = I[mask]
        t_masked = t[mask]
        
        # 计算灭绝数（如果有连续数据）
        if len(U_masked) > 1:
            extinctions = max(0, U_masked[0] - U_masked[-1])
            exposure_time = len(U_masked) * np.median(np.diff(t))
            avg_universes = np.mean(U_masked)
            
            hazard_rate = extinctions / (exposure_time * avg_universes) if exposure_time * avg_universes > 0 else 0
        else:
            hazard_rate = 0
            extinctions = 0
            exposure_time = 0
        
        results[name] = {
            'hazard_rate': hazard_rate,
            'extinctions': int(extinctions),
            'exposure_time': float(exposure_time),
            'avg_universes': float(avg_universes),
            'n_points': int(np.sum(mask))
        }
    
    # 计算hazard ratio
    if results['safe'] and results['danger']:
        h_safe = results['safe']['hazard_rate']
        h_danger = results['danger']['hazard_rate']
        
        if h_safe > 0:
            hr = h_danger / h_safe
        else:
            hr = np.inf if h_danger > 0 else 1.0
        
        results['hazard_ratio'] = hr
    else:
        results['hazard_ratio'] = None
    
    return results


def survival_analysis_by_cdi_zone(df, zones=None):
    """按CDI区间做生存分析"""
    if zones is None:
        zones = [
            (0.60, 0.70, "High [0.60, 0.70]"),
            (0.52, 0.60, "Med-High [0.52, 0.60)"),
            (0.40, 0.52, "Med-Low [0.40, 0.52)"),
            (0.00, 0.40, "Low [0.00, 0.40)")
        ]
    
    if 'alive_universes' not in df.columns:
        return None
    
    t = df['generation'].values
    U = df['alive_universes'].values
    I = df['avg_cdi'].values
    
    results = []
    
    for lower, upper, name in zones:
        mask = (I >= lower) & (I < upper)
        if np.sum(mask) < 2:
            continue
        
        U_zone = U[mask]
        t_zone = t[mask]
        
        # 计算该区间内的灭绝
        extinctions = max(0, U_zone[0] - U_zone[-1])
        
        # 生存率
        survival_rate = U_zone[-1] / U_zone[0] if U_zone[0] > 0 else 0
        
        # 如果在该区间发生了灭绝，计算时间
        if extinctions > 0:
            # 找到灭绝开始点
            extinct_idx = np.where(U_zone < U_zone[0])[0]
            if len(extinct_idx) > 0:
                time_to_extinction = t_zone[extinct_idx[0]] - t_zone[0]
            else:
                time_to_extinction = None
        else:
            time_to_extinction = None
        
        results.append({
            'zone': name,
            'cdi_range': f"[{lower}, {upper})",
            'n_points': int(np.sum(mask)),
            'start_universes': int(U_zone[0]),
            'end_universes': int(U_zone[-1]),
            'extinctions': int(extinctions),
            'survival_rate': float(survival_rate),
            'time_to_extinction': int(time_to_extinction) if time_to_extinction else None
        })
    
    return results


def analyze_false_positives(results_list):
    """分析误报率：CDI<0.52但长时间不灭绝"""
    false_positives = 0
    true_positives = 0
    
    for r in results_list:
        if 'first_extinction' in r and r['first_extinction']:
            I_at_extinction = r['first_extinction']['cdi']
            if I_at_extinction < 0.52:
                true_positives += 1
            else:
                # 灭绝时CDI >= 0.52 (漏报或不同机制)
                pass
    
    return {
        'true_positives': true_positives,
        'total_with_extinction': len([r for r in results_list if r.get('first_extinction')])
    }


def generate_report(csv_files, output_file=None):
    """生成完整分析报告"""
    print("="*70)
    print("5-Seed Bio-World Hazard Rate Analysis")
    print("="*70)
    print()
    
    # 加载数据
    data = load_all_seeds(csv_files)
    print(f"Loaded {len(data)} seed(s)")
    print()
    
    # 分析每个seed
    seed_results = []
    for seed_name, df in data.items():
        print(f"Analyzing {seed_name}...")
        result = analyze_seed(seed_name, df)
        seed_results.append(result)
        
        print(f"  Peak CDI: {result['cdi_peak']['value']:.4f} at Gen {result['cdi_peak']['gen']}")
        if result.get('I_crit'):
            print(f"  I_crit:   {result['I_crit']:.4f}")
        if result.get('first_extinction'):
            print(f"  Extinct:  Gen {result['first_extinction']['gen']}, CDI={result['first_extinction']['cdi']:.4f}")
        print()
    
    # 汇总统计
    print("="*70)
    print("SUMMARY STATISTICS")
    print("="*70)
    
    # I_crit稳定性
    I_crits = [r['I_crit'] for r in seed_results if r.get('I_crit')]
    if len(I_crits) >= 2:
        print(f"\nI_crit Stability:")
        print(f"  Mean:   {np.mean(I_crits):.4f}")
        print(f"  Std:    {np.std(I_crits):.4f}")
        print(f"  Min:    {np.min(I_crits):.4f}")
        print(f"  Max:    {np.max(I_crits):.4f}")
        print(f"  CV:     {np.std(I_crits)/np.mean(I_crits)*100:.2f}%")
        
        # 评级
        cv = np.std(I_crits)/np.mean(I_crits)
        range_val = np.max(I_crits) - np.min(I_crits)
        if cv < 0.05 and range_val < 0.02:
            rating = "STRONG PASS"
        elif cv < 0.10 and range_val < 0.05:
            rating = "MEDIUM PASS"
        else:
            rating = "WEAK PASS / FAIL"
        print(f"  Rating: {rating}")
    
    # R²统计
    r2s = [r['hazard_model']['r_squared'] for r in seed_results if r.get('hazard_model')]
    if r2s:
        print(f"\nModel Fit Quality:")
        print(f"  Mean R²: {np.mean(r2s):.4f}")
        print(f"  Min R²:  {np.min(r2s):.4f}")
    
    # 保存详细结果
    full_results = {
        'protocol': 'P0_5Seed_Hazard_Analysis',
        'timestamp': pd.Timestamp.now().isoformat(),
        'n_seeds': len(seed_results),
        'seed_results': seed_results,
        'summary': {
            'I_crit_mean': float(np.mean(I_crits)) if I_crits else None,
            'I_crit_std': float(np.std(I_crits)) if I_crits else None,
            'I_crit_cv': float(np.std(I_crits)/np.mean(I_crits)) if I_crits else None,
            'r2_mean': float(np.mean(r2s)) if r2s else None,
        }
    }
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(full_results, f, indent=2, default=str)
        print(f"\nDetailed results saved to: {output_file}")
    
    return full_results


def main():
    parser = argparse.ArgumentParser(description='Analyze 5-seed Bio-World results')
    parser.add_argument('--csv-files', nargs='+', required=True, help='CSV files from each seed')
    parser.add_argument('--output', default='model_fit_results/P0_5seed_analysis.json', help='Output JSON file')
    args = parser.parse_args()
    
    if len(args.csv_files) < 3:
        print(f"Warning: Only {len(args.csv_files)} file(s) provided. Need >= 3 for reliable analysis.")
    
    generate_report(args.csv_files, args.output)
    return 0


if __name__ == '__main__':
    exit(main())
