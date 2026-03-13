#!/usr/bin/env python3
"""
Hypothesis OQS - Gate 1 验证脚本
目标：验证 'spawn → work → summarize → respawn' 结构闭环有效性
"""

import math
import random
from typing import Dict, List, Tuple
from dataclasses import dataclass, field

@dataclass
class QueenState:
    """母体核心状态"""
    identity_hash: int
    global_goal: float
    resource_budget: float
    spawn_count: int = 0
    cull_count: int = 0
    overload_events: int = 0
    lineage_bank: List[Dict] = field(default_factory=list)
    
@dataclass
class WorkerState:
    """子体（章鱼式局部自治单元）"""
    worker_id: int
    role: str
    local_energy: float
    local_memory: List[float] = field(default_factory=list)
    prediction_error: float = 0.5
    task_progress: float = 0.0
    alive: bool = True
    experience_summary: Dict = field(default_factory=dict)
    role_changed: bool = False
    
@dataclass
class SimulationResult:
    architecture: str
    seed: int
    stress_profile: str
    stress_factor: float
    cwci: float
    division_of_labour: float
    role_stability: float
    task_reallocation_latency: float
    worker_utilization: float
    population_persistence: float
    worker_loss_recovery_time: float
    queen_overload_rate: float
    hazard_after_loss: float
    experience_return_quality: float
    spawn_utility_gain: float
    lineage_improvement: float


def simulate_octopus_like(stress_factor: float, seed: int, ticks: int = 3000) -> Dict:
    """纯章鱼型：强局部自治，无分工"""
    random.seed(seed)
    
    n_units = 100
    local_autonomy = 0.9
    
    workers = []
    for i in range(n_units):
        workers.append({
            'id': i,
            'energy': 1.0,
            'autonomy': local_autonomy,
            'task': 'explore',
            'alive': True,
        })
    
    total_tasks = 0
    completed_tasks = 0
    
    for tick in range(ticks):
        for w in workers:
            if not w['alive']:
                continue
            
            success_prob = w['autonomy'] * stress_factor
            if random.random() < success_prob:
                w['energy'] = min(1.0, w['energy'] + 0.01)
                completed_tasks += 1
            else:
                w['energy'] -= 0.02 * (2 - stress_factor)
            
            if w['energy'] <= 0:
                w['alive'] = False
            
            total_tasks += 1
    
    alive_count = sum(1 for w in workers if w['alive'])
    persistence = alive_count / n_units
    
    return {
        'persistence': persistence,
        'task_efficiency': completed_tasks / max(1, total_tasks),
        'specialization': 0.0,
        'recovery_capacity': persistence * 0.8,
    }


def simulate_ant_colony(stress_factor: float, seed: int, ticks: int = 3000) -> Dict:
    """纯蚁群型：强分工，弱局部自治"""
    random.seed(seed + 1)
    
    n_workers = 100
    roles = ['scout', 'builder', 'defender', 'maintainer']
    role_dist = [0.25, 0.35, 0.20, 0.20]
    
    workers = []
    role_counts = {r: 0 for r in roles}
    
    for i in range(n_workers):
        role = random.choices(roles, weights=role_dist)[0]
        role_counts[role] += 1
        workers.append({
            'id': i,
            'role': role,
            'energy': 1.0,
            'autonomy': 0.3,
            'task_efficiency': {'scout': 0.7, 'builder': 0.8, 'defender': 0.6, 'maintainer': 0.75}[role],
            'alive': True,
        })
    
    completed_tasks = 0
    role_stability_count = 0
    target_role_dist = {r: role_counts[r] for r in roles}
    
    for tick in range(ticks):
        current_roles = {r: 0 for r in roles}
        alive_count = sum(1 for w in workers if w['alive'])
        persistence = alive_count / n_workers if n_workers > 0 else 0
        
        for w in workers:
            if not w['alive']:
                continue
            
            task_success = w['task_efficiency'] * stress_factor * (0.5 + 0.5 * role_counts[w['role']] / n_workers)
            
            if random.random() < task_success:
                w['energy'] = min(1.0, w['energy'] + 0.015)
                completed_tasks += 1
                current_roles[w['role']] += 1
            else:
                w['energy'] -= 0.015 * (2 - stress_factor)
            
            if w['energy'] <= 0:
                w['alive'] = False
                if random.random() < 0.3 * stress_factor:
                    w['alive'] = True
                    w['energy'] = 0.5
    
    alive_count = sum(1 for w in workers if w['alive'])
    persistence = alive_count / n_workers
    
    role_variance = sum((role_counts[r] / n_workers - 0.25) ** 2 for r in roles)
    specialization = 1.0 - role_variance * 4
    
    return {
        'persistence': persistence,
        'task_efficiency': completed_tasks / max(1, ticks * n_workers),
        'specialization': specialization,
        'recovery_capacity': 0.9,
        'role_stability': 0.8,
    }


def simulate_octo_queen_swarm(stress_factor: float, seed: int, ticks: int = 3000) -> Dict:
    """OctoQueenSwarm: 章鱼型局部自治 + 蚁群型分工 + 母体整合"""
    random.seed(seed + 2)
    
    queen = QueenState(
        identity_hash=seed,
        global_goal=1.0,
        resource_budget=100.0,
    )
    
    roles = ['scout', 'builder', 'defender', 'maintainer']
    role_lineage = {r: {'utility': 0.5, 'count': 0} for r in roles}
    
    n_workers = 100
    workers = []
    
    for i in range(n_workers):
        utilities = [role_lineage[r]['utility'] for r in roles]
        role = random.choices(roles, weights=utilities)[0]
        
        worker = WorkerState(
            worker_id=i,
            role=role,
            local_energy=1.0,
        )
        workers.append(worker)
        queen.spawn_count += 1
        role_lineage[role]['count'] += 1
    
    completed_tasks = 0
    experience_returns = []
    worker_loss_events = []
    queen_load = []
    
    for tick in range(ticks):
        queen_decisions = 0
        
        for w in workers:
            if not w.alive:
                continue
            
            base_autonomy = 0.7
            role_bonus = {'scout': 0.1, 'builder': 0.15, 'defender': 0.05, 'maintainer': 0.1}[w.role]
            
            task_success = (base_autonomy + role_bonus) * stress_factor
            
            if random.random() < task_success:
                w.local_energy = min(1.0, w.local_energy + 0.02)
                completed_tasks += 1
                w.task_progress += 1
                w.experience_summary = {
                    'role': w.role,
                    'success': True,
                    'energy_efficiency': w.local_energy,
                    'local_learned': True,
                }
            else:
                w.local_energy -= 0.02 * (2 - stress_factor)
                w.prediction_error += 0.01
                w.experience_summary = {
                    'role': w.role,
                    'success': False,
                    'hazard': True,
                }
            
            if w.local_energy <= 0:
                w.alive = False
                worker_loss_events.append(tick)
                experience_returns.append(w.experience_summary)
                
                queen_decisions += 1
                if queen.resource_budget > 0:
                    new_role = random.choices(
                        roles,
                        weights=[role_lineage[r]['utility'] for r in roles]
                    )[0]
                    
                    w.alive = True
                    w.local_energy = 0.5
                    w.role = new_role
                    w.task_progress = 0
                    w.role_changed = True
                    queen.resource_budget -= 1
                    queen.spawn_count += 1
                    
                    if w.experience_summary.get('success'):
                        role_lineage[new_role]['utility'] = min(1.0, role_lineage[new_role]['utility'] + 0.05)
                    else:
                        role_lineage[new_role]['utility'] = max(0.1, role_lineage[new_role]['utility'] - 0.03)
        
        if tick % 500 == 0 and tick > 0:
            worst_role = min(role_lineage.keys(), key=lambda r: role_lineage[r]['utility'])
            if role_lineage[worst_role]['utility'] < 0.3:
                queen.cull_count += 1
                role_lineage[worst_role]['utility'] += 0.1
        
        queen_load.append(queen_decisions)
    
    alive_count = sum(1 for w in workers if w.alive)
    persistence = alive_count / n_workers
    
    role_dist = {r: sum(1 for w in workers if w.role == r and w.alive) for r in roles}
    total_alive = sum(role_dist.values())
    if total_alive > 0:
        role_probs = [role_dist[r] / total_alive for r in roles]
        entropy = -sum(p * math.log(p + 1e-10) for p in role_probs)
        division_of_labour = entropy / math.log(len(roles))
    else:
        division_of_labour = 0.0
    
    role_changes = sum(1 for w in workers if w.role_changed)
    role_stability = 1.0 - (role_changes / max(1, n_workers))
    
    avg_queen_load = sum(queen_load) / len(queen_load)
    overload_threshold = n_workers * 0.1
    overload_rate = sum(1 for load in queen_load if load > overload_threshold) / len(queen_load)
    
    if experience_returns:
        successful_returns = sum(1 for e in experience_returns if e.get('success'))
        return_quality = successful_returns / len(experience_returns)
    else:
        return_quality = 0.0
    
    lineage_gains = [role_lineage[r]['utility'] - 0.5 for r in roles]
    lineage_improvement = sum(lineage_gains) / len(lineage_gains)
    
    if len(worker_loss_events) >= 2:
        recovery_times = [worker_loss_events[i+1] - worker_loss_events[i] 
                         for i in range(len(worker_loss_events)-1)]
        avg_recovery_time = sum(recovery_times) / len(recovery_times)
    else:
        avg_recovery_time = 0.0
    
    return {
        'persistence': persistence,
        'task_efficiency': completed_tasks / max(1, ticks * n_workers),
        'specialization': division_of_labour,
        'recovery_capacity': persistence * 0.95,
        'role_stability': role_stability,
        'division_of_labour': division_of_labour,
        'queen_overload_rate': overload_rate,
        'experience_return_quality': return_quality,
        'lineage_improvement': lineage_improvement,
        'worker_recovery_time': avg_recovery_time,
        'queen_spawn_count': queen.spawn_count,
        'queen_cull_count': queen.cull_count,
    }


def calculate_cwci(metrics: Dict) -> float:
    persistence = metrics['persistence']
    efficiency = metrics['task_efficiency']
    spec = metrics.get('specialization', 0.5)
    recovery = metrics.get('recovery_capacity', 0.5)
    
    scores = [
        persistence,
        efficiency,
        spec,
        recovery,
        efficiency * 0.8,
        persistence * 0.9,
    ]
    
    return sum(scores) / len(scores)


def run_gate1():
    print("=" * 90)
    print("Hypothesis OQS - Gate 1 验证")
    print("目标：验证 'spawn → work → summarize → respawn' 结构闭环有效性")
    print("=" * 90)
    
    ARCHITECTURES = {
        'OctopusLike': simulate_octopus_like,
        'AntColonyLike': simulate_ant_colony,
        'OctoQueenSwarm': simulate_octo_queen_swarm,
    }
    
    STRESS_PROFILES = {
        'ResourceScarcity': 0.65,
        'HighCoordinationDemand': 0.75,
        'FailureBurst': 0.6,
    }
    
    SEEDS = [1000, 2000, 3000, 4000, 5000]
    
    results = []
    
    print("\nRunning simulations...")
    total_runs = len(ARCHITECTURES) * len(STRESS_PROFILES) * len(SEEDS)
    completed = 0
    
    for arch_name, sim_func in ARCHITECTURES.items():
        for stress_name, stress_factor in STRESS_PROFILES.items():
            for seed in SEEDS:
                metrics = sim_func(stress_factor, seed)
                cwci = calculate_cwci(metrics)
                
                results.append({
                    'architecture': arch_name,
                    'stress': stress_name,
                    'seed': seed,
                    'cwci': cwci,
                    **metrics,
                })
                
                completed += 1
                if completed % 10 == 0:
                    print(f"  Progress: {completed}/{total_runs}")
    
    print(f"\n✅ Completed: {completed} simulations")
    
    print("\n" + "=" * 90)
    print("Gate 1 结果汇总")
    print("=" * 90)
    
    print("\n【A. 核心指标对比】（跨所有场景的均值）")
    print("-" * 90)
    print(f"{'Architecture':>15} | {'CWCI':>6} | {'Persist':>8} | {'TaskEff':>8} | {'Spec':>5} | {'Recovery':>8}")
    print("-" * 90)
    
    arch_metrics = {}
    for arch in ARCHITECTURES.keys():
        arch_results = [r for r in results if r['architecture'] == arch]
        
        cwci_mean = sum(r['cwci'] for r in arch_results) / len(arch_results)
        persist_mean = sum(r['persistence'] for r in arch_results) / len(arch_results)
        eff_mean = sum(r['task_efficiency'] for r in arch_results) / len(arch_results)
        spec_mean = sum(r.get('specialization', 0) for r in arch_results) / len(arch_results)
        rec_mean = sum(r.get('recovery_capacity', 0) for r in arch_results) / len(arch_results)
        
        arch_metrics[arch] = {
            'cwci': cwci_mean,
            'persistence': persist_mean,
            'efficiency': eff_mean,
            'specialization': spec_mean,
            'recovery': rec_mean,
        }
        
        print(f"{arch:>15} | {cwci_mean:>6.3f} | {persist_mean:>8.3f} | {eff_mean:>8.3f} | {spec_mean:>5.3f} | {rec_mean:>8.3f}")
    
    print("\n【B. OctoQueenSwarm 特有指标】")
    print("-" * 90)
    print(f"{'Metric':>25} | {'Value':>10}")
    print("-" * 90)
    
    oqs_results = [r for r in results if r['architecture'] == 'OctoQueenSwarm']
    
    div_labour = sum(r.get('division_of_labour', 0) for r in oqs_results) / len(oqs_results)
    role_stab = sum(r.get('role_stability', 0) for r in oqs_results) / len(oqs_results)
    overload = sum(r.get('queen_overload_rate', 0) for r in oqs_results) / len(oqs_results)
    exp_quality = sum(r.get('experience_return_quality', 0) for r in oqs_results) / len(oqs_results)
    lineage_imp = sum(r.get('lineage_improvement', 0) for r in oqs_results) / len(oqs_results)
    
    print(f"{'division_of_labour':>25} | {div_labour:>10.3f}")
    print(f"{'role_stability':>25} | {role_stab:>10.3f}")
    print(f"{'queen_overload_rate':>25} | {overload:>10.3f}")
    print(f"{'experience_return_quality':>25} | {exp_quality:>10.3f}")
    print(f"{'lineage_improvement':>25} | {lineage_imp:>10.3f}")
    
    print("\n【C. 场景表现对比】")
    print("-" * 90)
    print(f"{'Scene':>20} | {'Octopus':>8} | {'AntColony':>10} | {'OctoQueen':>10} | {'OQS Win?':>8}")
    print("-" * 90)
    
    scene_wins = 0
    for stress_name in STRESS_PROFILES.keys():
        oct_cwci = sum(r['cwci'] for r in results if r['architecture'] == 'OctopusLike' and r['stress'] == stress_name) / len([r for r in results if r['architecture'] == 'OctopusLike' and r['stress'] == stress_name])
        ant_cwci = sum(r['cwci'] for r in results if r['architecture'] == 'AntColonyLike' and r['stress'] == stress_name) / len([r for r in results if r['architecture'] == 'AntColonyLike' and r['stress'] == stress_name])
        oqs_cwci = sum(r['cwci'] for r in results if r['architecture'] == 'OctoQueenSwarm' and r['stress'] == stress_name) / len([r for r in results if r['architecture'] == 'OctoQueenSwarm' and r['stress'] == stress_name])
        
        win = oqs_cwci > max(oct_cwci, ant_cwci)
        if win:
            scene_wins += 1
        
        print(f"{stress_name:>20} | {oct_cwci:>8.3f} | {ant_cwci:>10.3f} | {oqs_cwci:>10.3f} | {'✅' if win else '❌':>8}")
    
    print("\n" + "=" * 90)
    print("Gate 1 判定")
    print("=" * 90)
    
    print("\n检查项:")
    
    check1 = scene_wins >= 2
    print(f"1. 场景优势: {scene_wins}/3 场景优于对照组")
    print(f"   {'✅ PASS' if check1 else '❌ FAIL'}")
    
    oqs_recovery = arch_metrics['OctoQueenSwarm']['recovery']
    oct_recovery = arch_metrics['OctopusLike']['recovery']
    ant_recovery = arch_metrics['AntColonyLike']['recovery']
    check2 = oqs_recovery >= min(oct_recovery, ant_recovery)
    print(f"\n2. 恢复能力: OQS={oqs_recovery:.3f} vs Oct={oct_recovery:.3f}, Ant={ant_recovery:.3f}")
    print(f"   {'✅ PASS' if check2 else '❌ FAIL'}")
    
    check3 = div_labour > 0.5
    print(f"\n3. 分工程度: {div_labour:.3f} (threshold 0.5)")
    print(f"   {'✅ PASS' if check3 else '❌ FAIL'}")
    
    check4 = overload < 0.3
    print(f"\n4. Queen 瓶颈: overload={overload:.3f} (threshold 0.3)")
    print(f"   {'✅ PASS' if check4 else '⚠️  WARNING'}")
    
    print("\n" + "-" * 90)
    passes = sum([check1, check2, check3, check4])
    total = 4
    print(f"综合: {passes}/{total} 检查通过")
    
    if passes >= 3:
        verdict = "PASS"
        emoji = "🎉"
    elif passes >= 2:
        verdict = "PARTIAL"
        emoji = "⚠️"
    else:
        verdict = "FAIL"
        emoji = "❌"
    
    print(f"\n{emoji} Gate 1 = {verdict}")
    
    print("\n" + "=" * 90)
    print("一句话结论")
    print("=" * 90)
    
    if verdict == "PASS":
        conclusion = (
            "Gate 1 PASSED: OctoQueenSwarm demonstrates superior performance in "
            f"{scene_wins}/3 scenarios with effective division of labour ({div_labour:.2f}) "
            "and no central bottleneck; spawn-work-summarize-respawn loop validated."
        )
    elif verdict == "PARTIAL":
        conclusion = (
            "Gate 1 PARTIAL: OctoQueenSwarm shows directional advantages but "
            f"with {4-passes} check(s) failing; requires refinement before Gate 2."
        )
    else:
        conclusion = (
            "Gate 1 FAILED: OctoQueenSwarm architecture has fundamental issues; "
            "requires redesign of Queen-Worker relationship or information flow."
        )
    
    print(f"\n{conclusion}")
    
    return verdict, results


if __name__ == '__main__':
    verdict, results = run_gate1()
    exit(0 if verdict in ["PASS", "PARTIAL"] else 1)
