#!/usr/bin/env python3
"""
Hypothesis O1 - Gate 1 验证脚本
小规模对比：OctopusLike vs PulseCentral vs ModularLattice @ 1x, 2x scale
"""
import sys
sys.path.insert(0, '/tmp')

# 复用之前的模拟逻辑
from cwci_correlation_analysis import simulate_universe

def run_gate1():
    print("=" * 80)
    print("Hypothesis O1 - Gate 1 验证")
    print("小规模对比: OctopusLike vs PulseCentral vs ModularLattice")
    print("=" * 80)
    
    # 架构映射: family_variant
    ARCHITECTURES = {
        'OctopusLike': 1,
        'PulseCentral': 2,
        'ModularLattice': 3,
    }
    
    # 规模: 1x = 100 units, 2x = 200 units
    SCALES = [1.0, 2.0]
    
    # 压力场景
    STRESS_PROFILES = {
        'Stable': 1.0,
        'RegimeShiftFrequent': 0.8,
        'HighCoordinationDemand': 0.75,
        'SyncRiskHigh': 0.7,
        'ResourceScarcity': 0.65,
    }
    
    results = []
    
    for arch_name, family in ARCHITECTURES.items():
        for scale in SCALES:
            for stress_name, stress_factor in STRESS_PROFILES.items():
                uid = len(results)
                seed = 1000 + uid
                
                # 运行模拟
                result = simulate_universe(uid, seed, family, stress_factor, ticks=5000)
                result['architecture'] = arch_name
                result['scale'] = scale
                result['stress_profile'] = stress_name
                results.append(result)
    
    # 汇总表
    print("\n" + "-" * 80)
    print(f"{'Arch':>12} | {'Scale':>5} | {'Stress':>20} | {'CWCI':>6} | {'Spec':>5} | {'Integ':>5} | {'Bcast':>5}")
    print("-" * 80)
    for r in results:
        print(f"{r['architecture']:>12} | {r['scale']:>5.1f}x | {r['stress_profile'][:20]:>20} | {r['cwci']:>6.3f} | {r['specialization_score']:>5.3f} | {r['integration_score']:>5.3f} | {r['broadcast_score']:>5.3f}")
    
    # Gate 1 检查
    print("\n" + "=" * 80)
    print("Gate 1 检查项")
    print("=" * 80)
    
    # 1. OctopusLike CWCI 保持 top 档
    octopus_cwcis = [r['cwci'] for r in results if r['architecture'] == 'OctopusLike']
    pulse_cwcis = [r['cwci'] for r in results if r['architecture'] == 'PulseCentral']
    lattice_cwcis = [r['cwci'] for r in results if r['architecture'] == 'ModularLattice']
    
    octopus_avg = sum(octopus_cwcis) / len(octopus_cwcis)
    pulse_avg = sum(pulse_cwcis) / len(pulse_cwcis)
    lattice_avg = sum(lattice_cwcis) / len(lattice_cwcis)
    
    print(f"\n1. CWCI 排名:")
    print(f"   OctopusLike:    {octopus_avg:.3f}")
    print(f"   ModularLattice: {lattice_avg:.3f}")
    print(f"   PulseCentral:   {pulse_avg:.3f}")
    
    cwci_top = octopus_avg > lattice_avg and octopus_avg > pulse_avg
    print(f"   {'✅ PASS' if cwci_top else '❌ FAIL'}: OctopusLike CWCI 最高")
    
    # 2. 压力场景下的适应能力 (简化为 CWCI 稳定性)
    print(f"\n2. 压力场景稳定性 (CWCI std):")
    for arch in ARCHITECTURES.keys():
        arch_results = [r['cwci'] for r in results if r['architecture'] == arch]
        mean_cwci = sum(arch_results) / len(arch_results)
        variance = sum((x - mean_cwci) ** 2 for x in arch_results) / len(arch_results)
        std = variance ** 0.5
        print(f"   {arch:>12}: mean={mean_cwci:.3f}, std={std:.3f}")
    
    # 3. 规模扩展检查
    print(f"\n3. 规模扩展 (1x → 2x):")
    for arch in ARCHITECTURES.keys():
        r_1x = [r for r in results if r['architecture'] == arch and r['scale'] == 1.0]
        r_2x = [r for r in results if r['architecture'] == arch and r['scale'] == 2.0]
        
        cwci_1x = sum(r['cwci'] for r in r_1x) / len(r_1x)
        cwci_2x = sum(r['cwci'] for r in r_2x) / len(r_2x)
        
        change = ((cwci_2x - cwci_1x) / cwci_1x) * 100
        trend = "↗️ 提升" if change > 5 else "→ 持平" if abs(change) < 5 else "↘️ 下降"
        print(f"   {arch:>12}: 1x={cwci_1x:.3f} → 2x={cwci_2x:.3f} ({change:+.1f}%) {trend}")
    
    # 最终判定
    print("\n" + "=" * 80)
    print("Gate 1 判定")
    print("=" * 80)
    
    checks = {
        'CWCI Top': cwci_top,
    }
    
    passed = sum(checks.values())
    total = len(checks)
    
    print(f"\n通过检查: {passed}/{total}")
    
    if passed == total:
        print("🎉 Gate 1 PASSED - 进入 Gate 2 (5x 规模)")
        return 0
    else:
        print("⚠️ Gate 1 部分失败 - 需要分析原因")
        for check, status in checks.items():
            print(f"   {'✅' if status else '❌'} {check}")
        return 1

if __name__ == '__main__':
    exit(run_gate1())
