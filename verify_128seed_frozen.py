#!/usr/bin/env python3
"""
128-Seed Frozen Manifest Verification Script
验证所有seeds是否符合冻结规范
"""

import json
import sys
from pathlib import Path
from collections import Counter

REQUIRED_FIELDS = [
    'seed_id', 'pool', 'source_pool', 'family_id',
    'parent_candidates', 'variation_ops', 'generation_mode',
    'inheritance_mode', 'is_control', 'is_leakage_monitor',
    'is_gray_zone', 'expected_role', 'manifest_version', 'frozen_at'
]

ZONE_FAMILIES = {
    'core': {"F_P3T4M4", "F_P2T4M3", "F_P3T4M3", "F_P3T3M2", "F_P3T3M4", "F_P2T4M4", "F_P2T3M4"},
    'leakage': {"F_P1T3M3", "F_P1T3M4", "F_P4T4M3", "F_P4T4M4", "F_P3T5M5", "F_P2T5M4"}
}

POOL_CONFIG = {
    'A': {'size': 32, 'is_control': False, 'is_leakage': False},
    'B': {'size': 32, 'is_control': False, 'is_leakage': False},
    'C': {'size': 24, 'is_control': False, 'is_leakage': False},
    'D': {'size': 16, 'is_control': False, 'is_leakage': False},
    'E': {'size': 16, 'is_control': True, 'is_leakage': False},
    'F': {'size': 8, 'is_control': False, 'is_leakage': True},
}

def load_all_seeds():
    """加载所有128 seeds"""
    seeds = []
    for pool in ['a', 'b', 'c', 'd', 'e', 'f']:
        pool_dir = Path(f"next_128_seed/pool_{pool}")
        for f in pool_dir.glob("S*.json"):
            with open(f) as fp:
                seed = json.load(fp)
                seed['_file'] = f.name
                seeds.append(seed)
    return seeds

def verify_fields(seeds):
    """验证必需字段"""
    errors = []
    for s in seeds:
        missing = [f for f in REQUIRED_FIELDS if f not in s]
        if missing:
            errors.append(f"{s.get('seed_id', 'UNKNOWN')}: missing fields {missing}")
    return errors

def verify_zone_consistency(seeds):
    """验证zone标记与family一致性"""
    errors = []
    for s in seeds:
        fam = s.get('family_id', '')
        zone = s.get('zone', '')
        
        if fam in ZONE_FAMILIES['core'] and zone != 'core':
            errors.append(f"{s['seed_id']}: family {fam} is core but marked as {zone}")
        elif fam in ZONE_FAMILIES['leakage'] and zone != 'leakage':
            errors.append(f"{s['seed_id']}: family {fam} is leakage but marked as {zone}")
    return errors

def verify_pool_consistency(seeds):
    """验证pool标记与is_control/is_leakage一致性"""
    errors = []
    for s in seeds:
        pool = s.get('pool', '')
        is_control = s.get('is_control', False)
        is_leakage = s.get('is_leakage_monitor', False)
        
        expected = POOL_CONFIG.get(pool, {})
        if is_control != expected.get('is_control', False):
            errors.append(f"{s['seed_id']}: pool {pool} is_control mismatch (expected {expected.get('is_control')}, got {is_control})")
        if is_leakage != expected.get('is_leakage', False):
            errors.append(f"{s['seed_id']}: pool {pool} is_leakage mismatch (expected {expected.get('is_leakage')}, got {is_leakage})")
    return errors

def verify_pool_sizes(seeds):
    """验证各pool数量"""
    errors = []
    pool_counts = Counter(s.get('pool') for s in seeds)
    
    for pool, config in POOL_CONFIG.items():
        actual = pool_counts.get(pool, 0)
        expected = config['size']
        if actual != expected:
            errors.append(f"Pool-{pool}: expected {expected}, got {actual}")
    
    return errors, pool_counts

def verify_gray_zone(seeds):
    """验证灰区seeds"""
    gray_seeds = [s for s in seeds if s.get('is_gray_zone')]
    
    expected_gray = {'S2088', 'S2096', 'S2092', 'S2100', 'S2126', 'S2127'}
    actual_gray = {s['seed_id'] for s in gray_seeds}
    
    missing = expected_gray - actual_gray
    extra = actual_gray - expected_gray
    
    errors = []
    if missing:
        errors.append(f"Gray zone seeds missing: {missing}")
    if extra:
        errors.append(f"Unexpected gray zone seeds: {extra}")
    if len(gray_seeds) != 6:
        errors.append(f"Gray zone count mismatch: expected 6, got {len(gray_seeds)}")
    
    return errors, gray_seeds

def verify_control_group(seeds):
    """验证控制组"""
    control_seeds = [s for s in seeds if s.get('is_control')]
    
    errors = []
    if len(control_seeds) != 16:
        errors.append(f"Control group size mismatch: expected 16, got {len(control_seeds)}")
    
    no_inheritance = [s for s in control_seeds if s.get('inheritance_mode') == 'disabled']
    bias_zero = [s for s in control_seeds if s.get('inheritance_mode') == 'package_loaded_bias_zero']
    
    if len(no_inheritance) != 8:
        errors.append(f"Control split mismatch: expected 8 no_inheritance, got {len(no_inheritance)}")
    if len(bias_zero) != 8:
        errors.append(f"Control split mismatch: expected 8 bias_zero, got {len(bias_zero)}")
    
    return errors, control_seeds

def verify_leakage_monitors(seeds):
    """验证泄漏监测组"""
    leakage_seeds = [s for s in seeds if s.get('is_leakage_monitor')]
    
    errors = []
    if len(leakage_seeds) != 8:
        errors.append(f"Leakage monitor count mismatch: expected 8, got {len(leakage_seeds)}")
    
    # 验证是否都来自Pool-F
    non_f_leakage = [s for s in leakage_seeds if s.get('pool') != 'F']
    if non_f_leakage:
        errors.append(f"Leakage monitors not in Pool-F: {[s['seed_id'] for s in non_f_leakage]}")
    
    return errors, leakage_seeds

def verify_manifest_frozen(seeds):
    """验证manifest已冻结"""
    errors = []
    versions = set(s.get('manifest_version') for s in seeds)
    frozen_times = set(s.get('frozen_at') for s in seeds)
    
    if versions != {'1.0-frozen'}:
        errors.append(f"Manifest version not uniform: {versions}")
    if len(frozen_times) != 1:
        errors.append(f"Frozen timestamps not uniform: {frozen_times}")
    
    return errors

def print_summary(seeds, pool_counts, gray_seeds, control_seeds, leakage_seeds):
    """打印摘要"""
    print("\n" + "="*60)
    print("128-Seed Frozen Manifest Verification Summary")
    print("="*60)
    
    print(f"\n总Seeds数: {len(seeds)}")
    print(f"版本: 1.0-frozen")
    print(f"冻结时间: {seeds[0].get('frozen_at', 'N/A')}")
    
    print("\nPool分布:")
    for pool in ['A', 'B', 'C', 'D', 'E', 'F']:
        count = pool_counts.get(pool, 0)
        expected = POOL_CONFIG[pool]['size']
        status = "✅" if count == expected else "❌"
        print(f"  Pool-{pool}: {count}/{expected} {status}")
    
    print("\n区域分布:")
    zones = Counter(s.get('zone') for s in seeds)
    for zone, count in zones.items():
        print(f"  {zone}: {count}")
    
    print("\n关键组:")
    print(f"  控制组 (Pool-E): {len(control_seeds)} seeds")
    print(f"  泄漏监测 (Pool-F): {len(leakage_seeds)} seeds")
    print(f"  灰区: {len(gray_seeds)} seeds")
    
    print("\nFamily Top 5:")
    families = Counter(s.get('family_id') for s in seeds)
    for fam, count in families.most_common(5):
        pct = count / len(seeds) * 100
        print(f"  {fam}: {count} ({pct:.1f}%)")
    
    f_p3t4m4_pct = families.get('F_P3T4M4', 0) / len(seeds) * 100
    print(f"\nF_P3T4M4占比: {f_p3t4m4_pct:.1f}%")
    if f_p3t4m4_pct > 50:
        print("  ⚠️  WARNING: 超过50%，存在contraction风险")
    elif f_p3t4m4_pct > 60:
        print("  ❌  CRITICAL: 超过60%，contraction_warning触发")
    else:
        print("  ✅  健康范围 (25-50%)")

def main():
    print("Loading 128 seeds...")
    seeds = load_all_seeds()
    
    if len(seeds) != 128:
        print(f"❌ CRITICAL: Expected 128 seeds, found {len(seeds)}")
        sys.exit(1)
    
    print(f"Loaded {len(seeds)} seeds")
    
    # 运行所有验证
    all_errors = []
    
    print("\nVerifying required fields...")
    errors = verify_fields(seeds)
    all_errors.extend(errors)
    print(f"  {'✅ Pass' if not errors else f'❌ {len(errors)} errors'}")
    
    print("Verifying zone consistency...")
    errors = verify_zone_consistency(seeds)
    all_errors.extend(errors)
    print(f"  {'✅ Pass' if not errors else f'❌ {len(errors)} errors'}")
    
    print("Verifying pool consistency...")
    errors = verify_pool_consistency(seeds)
    all_errors.extend(errors)
    print(f"  {'✅ Pass' if not errors else f'❌ {len(errors)} errors'}")
    
    print("Verifying pool sizes...")
    errors, pool_counts = verify_pool_sizes(seeds)
    all_errors.extend(errors)
    print(f"  {'✅ Pass' if not errors else f'❌ {len(errors)} errors'}")
    
    print("Verifying gray zone (6 seeds)...")
    errors, gray_seeds = verify_gray_zone(seeds)
    all_errors.extend(errors)
    print(f"  {'✅ Pass' if not errors else f'❌ {len(errors)} errors'}")
    
    print("Verifying control group (16 seeds)...")
    errors, control_seeds = verify_control_group(seeds)
    all_errors.extend(errors)
    print(f"  {'✅ Pass' if not errors else f'❌ {len(errors)} errors'}")
    
    print("Verifying leakage monitors (8 seeds)...")
    errors, leakage_seeds = verify_leakage_monitors(seeds)
    all_errors.extend(errors)
    print(f"  {'✅ Pass' if not errors else f'❌ {len(errors)} errors'}")
    
    print("Verifying manifest frozen...")
    errors = verify_manifest_frozen(seeds)
    all_errors.extend(errors)
    print(f"  {'✅ Pass' if not errors else f'❌ {len(errors)} errors'}")
    
    # 打印摘要
    print_summary(seeds, pool_counts, gray_seeds, control_seeds, leakage_seeds)
    
    # 最终判定
    print("\n" + "="*60)
    if all_errors:
        print(f"❌ VERIFICATION FAILED: {len(all_errors)} errors")
        print("\nErrors:")
        for e in all_errors[:10]:  # 只显示前10个
            print(f"  - {e}")
        if len(all_errors) > 10:
            print(f"  ... and {len(all_errors) - 10} more")
        sys.exit(1)
    else:
        print("✅ ALL VERIFICATIONS PASSED")
        print("\n128-Seed池已冻结，符合L4-v2 Bridge/Mainline验证要求")
        print("\n下一步: 执行Bridge Phase 1 (全量128)")
        sys.exit(0)

if __name__ == "__main__":
    main()
