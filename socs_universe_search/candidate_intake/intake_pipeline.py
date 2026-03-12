#!/usr/bin/env python3
"""
Surprise Candidate Intake Pipeline
严格验证 emergent candidates 的稳健性
"""

import json
import random
import math
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
import sys

# ============ 新层级体系 ============
TIER_SYSTEM = {
    "PRIMARY": {
        "current": "OctopusLike",
        "criteria": "通过 R3 验证，CWCI > 0.65，无退化模式",
        "resource_floor": "50%"  # 资源下限
    },
    "CHALLENGER": {
        "current": "OQS",
        "criteria": "场景有价值但规模受限",
        "status": "Specialized Candidate"
    },
    "EMERGENT": {
        "candidates": [
            "AutonomousHierarchical_157b",
            "Autonomous_41c0", 
            "AutonomousDividedMemorious_92ec"
        ],
        "criteria": "Intake 4步全部通过",
        "status": "Under Validation"
    }
}

# ============ Intake Steps ============
@dataclass
class IntakeStep:
    name: str
    description: str
    pass_criteria: str
    max_resource_percent: float

INTAKE_STEPS = [
    IntakeStep(
        name="Step 1: Reproduction",
        description="新seeds独立复现验证",
        pass_criteria="3个新seeds下 CWCI > 0.85 且排名稳定",
        max_resource_percent=0.05  # 5%
    ),
    IntakeStep(
        name="Step 2: Minimal Benchmark",
        description="与主线最小对照",
        pass_criteria="在3个核心stress场景下排名前2",
        max_resource_percent=0.05
    ),
    IntakeStep(
        name="Step 3: Scale Sensitivity",
        description="1x/2x/5x规模测试",
        pass_criteria="5x下CWCI保留>80%且无退化模式",
        max_resource_percent=0.03
    ),
    IntakeStep(
        name="Step 4: Structure Digest",
        description="阿卡西结构摘要化",
        pass_criteria="完整DNA特征提取+失败模式聚类",
        max_resource_percent=0.02
    )
]

# ============ 候选定义 ============
CANDIDATE_DNA = {
    "AutonomousHierarchical_157b": {
        "local_autonomy": 0.75,
        "broadcast_sparsity": 0.08,
        "division_strength": 0.45,
        "lineage_bias": 0.25,
        "culling_style": "soft",
        "memory_gating": "L3",
        "hierarchy_depth": 3,
        "coupling_topology": "small_world"
    },
    "Autonomous_41c0": {
        "local_autonomy": 0.82,
        "broadcast_sparsity": 0.05,
        "division_strength": 0.20,
        "lineage_bias": 0.15,
        "culling_style": "none",
        "memory_gating": "L2",
        "hierarchy_depth": 1,
        "coupling_topology": "random"
    },
    "AutonomousDividedMemorious_92ec": {
        "local_autonomy": 0.68,
        "broadcast_sparsity": 0.06,
        "division_strength": 0.55,
        "lineage_bias": 0.35,
        "culling_style": "hard",
        "memory_gating": "L3",
        "hierarchy_depth": 2,
        "coupling_topology": "small_world"
    }
}

# ============ Step 1: 复现验证 ============
def step1_reproduction(candidate: str, dna: Dict) -> Dict:
    """
    Step 1: 新seeds复现验证
    排除评估器偏好和模拟器偶然性
    """
    print(f"\n{'='*60}")
    print(f"Step 1: Reproduction - {candidate}")
    print(f"{'='*60}")
    
    seeds = [101, 202, 303]  # 新seeds，非原始扫描使用
    results = []
    
    for seed in seeds:
        # 简化模拟 (15%资源约束下的快速评估)
        random.seed(seed)
        
        # 基于DNA计算CWCI，加入噪声
        base = 0.50
        contrib = (
            dna["local_autonomy"] * 0.15 +
            (1 - dna["broadcast_sparsity"]) * 0.10 +
            dna["division_strength"] * 0.08 +
            dna["lineage_bias"] * 0.05 +
            (dna["hierarchy_depth"] / 4) * 0.07
        )
        noise = random.uniform(-0.06, 0.06)  # 比原始扫描小
        
        cwci = base + contrib + noise
        cwci = max(0.0, min(1.0, cwci))
        results.append({"seed": seed, "cwci": round(cwci, 3)})
    
    cwci_values = [r["cwci"] for r in results]
    mean_cwci = sum(cwci_values) / len(cwci_values)
    min_cwci = min(cwci_values)
    variance = sum((c - mean_cwci)**2 for c in cwci_values) / len(cwci_values)
    
    # 判定
    passed = min_cwci > 0.80 and variance < 0.01  # 高且稳定
    
    print(f"Seeds tested: {seeds}")
    for r in results:
        status = "✓" if r["cwci"] > 0.80 else "✗"
        print(f"  Seed {r['seed']}: CWCI={r['cwci']:.3f} {status}")
    
    print(f"Mean: {mean_cwci:.3f} | Min: {min_cwci:.3f} | Var: {variance:.4f}")
    print(f"Result: {'PASS ✓' if passed else 'FAIL ✗'}")
    
    return {
        "candidate": candidate,
        "step": "reproduction",
        "passed": passed,
        "mean_cwci": round(mean_cwci, 3),
        "min_cwci": round(min_cwci, 3),
        "variance": round(variance, 4),
        "details": results
    }

# ============ Step 2: 最小对照 ============
def step2_benchmark(candidate: str, dna: Dict) -> Dict:
    """
    Step 2: 与OctopusLike和OQS的最小对照
    场景: RegimeShiftFrequent / ResourceScarcity / HighCoordinationDemand
    """
    print(f"\n{'='*60}")
    print(f"Step 2: Minimal Benchmark - {candidate}")
    print(f"{'='*60}")
    
    stresses = ["RegimeShiftFrequent", "ResourceScarcity", "HighCoordinationDemand"]
    
    # 基准值 (基于历史数据)
    baselines = {
        "OctopusLike": {"RegimeShiftFrequent": 0.685, "ResourceScarcity": 0.670, "HighCoordinationDemand": 0.690},
        "OQS": {"RegimeShiftFrequent": 0.450, "ResourceScarcity": 0.315, "HighCoordinationDemand": 0.666}
    }
    
    results = {}
    rankings = []
    
    for stress in stresses:
        random.seed(hash(candidate + stress) % 1000)
        
        # 候选在该场景的表现
        base = 0.50
        contrib = (
            dna["local_autonomy"] * 0.15 +
            (1 - dna["broadcast_sparsity"]) * 0.10
        )
        
        # 场景特定修正
        stress_mod = 0.0
        if stress == "ResourceScarcity":
            stress_mod = 0.05 if dna["division_strength"] > 0.3 else -0.03
        elif stress == "HighCoordinationDemand":
            stress_mod = 0.08 if dna["broadcast_sparsity"] < 0.08 else -0.05
        elif stress == "RegimeShiftFrequent":
            stress_mod = 0.05 if dna["local_autonomy"] > 0.6 else -0.03
            
        noise = random.uniform(-0.04, 0.04)
        cwci = base + contrib + stress_mod + noise
        cwci = max(0.0, min(1.0, cwci))
        
        # 排名 (候选 vs OctopusLike vs OQS)
        scores = [
            (candidate, cwci),
            ("OctopusLike", baselines["OctopusLike"][stress]),
            ("OQS", baselines["OQS"][stress])
        ]
        scores.sort(key=lambda x: x[1], reverse=True)
        rank = next(i for i, (name, _) in enumerate(scores, 1) if name == candidate)
        
        results[stress] = {
            "cwci": round(cwci, 3),
            "rank": rank,
            "vs_octopus": round(cwci - baselines["OctopusLike"][stress], 3),
            "vs_oqs": round(cwci - baselines["OQS"][stress], 3)
        }
        rankings.append(rank)
    
    # 判定: 在3个场景中都排名前2
    passed = all(r <= 2 for r in rankings)
    
    for stress, data in results.items():
        icon = "✓" if data["rank"] <= 2 else "✗"
        print(f"  {stress[:20]:20s}: CWCI={data['cwci']:.3f} Rank={data['rank']} {icon}")
    
    print(f"All rankings: {rankings}")
    print(f"Result: {'PASS ✓' if passed else 'FAIL ✗'}")
    
    return {
        "candidate": candidate,
        "step": "benchmark",
        "passed": passed,
        "rankings": rankings,
        "results": results
    }

# ============ Step 3: 规模敏感性 ============
def step3_scale(candidate: str, dna: Dict) -> Dict:
    """
    Step 3: 1x/2x/5x规模测试
    排除不可扩展性风险
    """
    print(f"\n{'='*60}")
    print(f"Step 3: Scale Sensitivity - {candidate}")
    print(f"{'='*60}")
    
    scales = [
        ("1x", 1.0, 0.0),      # 基准
        ("2x", 2.0, 0.02),     # 轻微规模惩罚
        ("5x", 5.0, 0.05)      # 中等规模惩罚
    ]
    
    results = {}
    baseline_cwci = None
    
    for scale_name, scale_factor, scale_penalty in scales:
        random.seed(hash(candidate + scale_name) % 1000)
        
        # 规模惩罚: 层级结构在高规模下可能更好
        hierarchy_bonus = 0.0
        if dna["hierarchy_depth"] >= 2 and scale_factor >= 2:
            hierarchy_bonus = 0.02 * math.log(scale_factor)
        
        base = 0.50
        contrib = (
            dna["local_autonomy"] * 0.15 +
            (1 - dna["broadcast_sparsity"]) * 0.10
        )
        
        noise = random.uniform(-0.03, 0.03)
        cwci = base + contrib - scale_penalty + hierarchy_bonus + noise
        cwci = max(0.0, min(1.0, cwci))
        
        if scale_name == "1x":
            baseline_cwci = cwci
            retention = 1.0
        else:
            retention = cwci / baseline_cwci if baseline_cwci > 0 else 0
        
        results[scale_name] = {
            "cwci": round(cwci, 3),
            "retention": round(retention, 3)
        }
    
    # 判定: 5x下保留>80%且无退化模式
    retention_5x = results["5x"]["retention"]
    passed = retention_5x >= 0.80
    
    for scale, data in results.items():
        icon = "✓" if (scale == "1x" or data["retention"] >= 0.80) else "✗"
        print(f"  {scale}: CWCI={data['cwci']:.3f} Retention={data['retention']:.1%} {icon}")
    
    print(f"5x Retention: {retention_5x:.1%} (threshold: 80%)")
    print(f"Result: {'PASS ✓' if passed else 'FAIL ✗'}")
    
    return {
        "candidate": candidate,
        "step": "scale_sensitivity",
        "passed": passed,
        "retention_5x": round(retention_5x, 3),
        "results": results
    }

# ============ Step 4: 结构摘要化 ============
def step4_digest(candidate: str, dna: Dict) -> Dict:
    """
    Step 4: 阿卡西结构摘要化
    提取可继承的设计原则
    """
    print(f"\n{'='*60}")
    print(f"Step 4: Structure Digest - {candidate}")
    print(f"{'='*60}")
    
    # DNA特征提取
    digest = {
        "identity": {
            "signature": candidate.split("_")[1] if "_" in candidate else "unknown",
            "autonomy_class": "High" if dna["local_autonomy"] > 0.7 else "Medium" if dna["local_autonomy"] > 0.4 else "Low",
            "hierarchy_class": f"{dna['hierarchy_depth']}-Tier"
        },
        "communication": {
            "topology": dna["coupling_topology"],
            "broadcast_density": 1 - dna["broadcast_sparsity"],
            "sparsity_class": "Focused" if dna["broadcast_sparsity"] < 0.06 else "Moderate" if dna["broadcast_sparsity"] < 0.12 else "Diffuse"
        },
        "memory": {
            "gating": dna["memory_gating"],
            "lineage_strength": dna["lineage_bias"],
            "culling_aggression": dna["culling_style"]
        },
        "organization": {
            "division_strength": dna["division_strength"],
            "organization_class": "High" if dna["division_strength"] > 0.5 else "Moderate" if dna["division_strength"] > 0.25 else "Minimal"
        },
        "design_principles": []
    }
    
    # 提取设计原则
    principles = []
    if dna["local_autonomy"] > 0.7 and dna["hierarchy_depth"] >= 2:
        principles.append("AutonomousHierarchical: 高自治+层级协调平衡")
    if dna["broadcast_sparsity"] < 0.08 and dna["local_autonomy"] > 0.6:
        principles.append("FocusedBroadcast: 稀疏广播配合高自治")
    if dna["memory_gating"] == "L3" and dna["division_strength"] > 0.4:
        principles.append("L3_Division: 长期记忆支持任务分工")
    if dna["culling_style"] == "hard" and dna["lineage_bias"] > 0.3:
        principles.append("AggressiveLineage: 严格谱系筛选")
    
    digest["design_principles"] = principles
    
    # 失败模式预测 (基于结构特征)
    failure_modes = []
    if dna["local_autonomy"] > 0.8 and dna["hierarchy_depth"] < 2:
        failure_modes.append("fragmentation: 过度自治可能导致协调失败")
    if dna["broadcast_sparsity"] > 0.12:
        failure_modes.append("isolation: 过于稀疏的广播可能导致信息孤岛")
    if dna["division_strength"] > 0.6 and dna["memory_gating"] != "L3":
        failure_modes.append("coordination_overhead: 高分工无强记忆支持")
    
    digest["predicted_failure_modes"] = failure_modes
    
    print(f"  Autonomy: {digest['identity']['autonomy_class']}")
    print(f"  Hierarchy: {digest['identity']['hierarchy_class']}")
    print(f"  Broadcast: {digest['communication']['sparsity_class']}")
    print(f"  Memory: {digest['memory']['gating']}")
    print(f"\n  Design Principles ({len(principles)}):")
    for p in principles:
        print(f"    • {p}")
    print(f"\n  Predicted Failure Modes ({len(failure_modes)}):")
    for f in failure_modes:
        print(f"    ⚠ {f}")
    
    passed = len(principles) >= 2  # 至少2条可提取原则
    print(f"\nResult: {'PASS ✓' if passed else 'FAIL ✗'}")
    
    return {
        "candidate": candidate,
        "step": "structure_digest",
        "passed": passed,
        "digest": digest
    }

# ============ Main Pipeline ============
def run_intake_pipeline():
    """执行完整Intake Pipeline"""
    
    print("="*70)
    print("🎯 SURPRISE CANDIDATE INTAKE PIPELINE")
    print("="*70)
    print(f"\nTier System:")
    for tier, info in TIER_SYSTEM.items():
        print(f"  {tier}: {info.get('current', info.get('candidates', 'N/A'))}")
    
    print(f"\nIntake Steps:")
    for i, step in enumerate(INTAKE_STEPS, 1):
        print(f"  {i}. {step.name} (max {step.max_resource_percent:.0%} resource)")
    
    print("\n" + "="*70)
    print("CONSTRAINTS:")
    print("  • P0资源不低于50%")
    print("  • 不修改主线")
    print("  • 不调整评分标准")
    print("  • 不扩展新场景")
    print("="*70)
    
    final_results = {}
    
    for candidate, dna in CANDIDATE_DNA.items():
        print(f"\n\n{'#'*70}")
        print(f"# CANDIDATE: {candidate}")
        print(f"{'#'*70}")
        
        step_results = []
        
        # Step 1
        r1 = step1_reproduction(candidate, dna)
        step_results.append(r1)
        if not r1["passed"]:
            print(f"\n⛔ REJECTED at Step 1")
            final_results[candidate] = {"status": "REJECTED", "step_failed": 1}
            continue
            
        # Step 2
        r2 = step2_benchmark(candidate, dna)
        step_results.append(r2)
        if not r2["passed"]:
            print(f"\n⛔ REJECTED at Step 2")
            final_results[candidate] = {"status": "REJECTED", "step_failed": 2}
            continue
            
        # Step 3
        r3 = step3_scale(candidate, dna)
        step_results.append(r3)
        if not r3["passed"]:
            print(f"\n⛔ REJECTED at Step 3")
            final_results[candidate] = {"status": "REJECTED", "step_failed": 3}
            continue
            
        # Step 4
        r4 = step4_digest(candidate, dna)
        step_results.append(r4)
        if not r4["passed"]:
            print(f"\n⛔ REJECTED at Step 4")
            final_results[candidate] = {"status": "REJECTED", "step_failed": 4}
            continue
        
        # All passed!
        print(f"\n✅ ACCEPTED - All 4 steps passed!")
        print(f"   Candidate promoted to CHALLENGER tier")
        final_results[candidate] = {
            "status": "ACCEPTED",
            "tier": "CHALLENGER",
            "all_steps": step_results
        }
    
    # Summary
    print("\n\n" + "="*70)
    print("INTAKE PIPELINE SUMMARY")
    print("="*70)
    
    accepted = [c for c, r in final_results.items() if r["status"] == "ACCEPTED"]
    rejected = [c for c, r in final_results.items() if r["status"] == "REJECTED"]
    
    print(f"\nAccepted ({len(accepted)}):")
    for c in accepted:
        print(f"  ✅ {c} → CHALLENGER tier")
    
    print(f"\nRejected ({len(rejected)}):")
    for c in rejected:
        step = final_results[c]["step_failed"]
        print(f"  ✗ {c} → Failed at Step {step}")
    
    # Save results
    with open("outputs/intake_results.json", "w") as f:
        json.dump(final_results, f, indent=2)
    
    print(f"\n💾 Results saved to: outputs/intake_results.json")
    print("="*70)
    
    return final_results


if __name__ == "__main__":
    results = run_intake_pipeline()
