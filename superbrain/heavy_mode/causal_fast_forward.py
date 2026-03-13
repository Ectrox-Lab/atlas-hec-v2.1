#!/usr/bin/env python3
"""
CAUSAL FAST-FORWARD SCHEDULER - Phase C Implementation
利用因果圖進行智能配置跳躍，跳過已知穩定區域，專注高風險/高價值點

核心概念：
1. Uncertainty Sampling: 優先探索不確定性高的配置
2. Causal Jump: 基於因果邊推斷，跳過中間狀態
3. Adaptive Depth: 根據資源動態調整探索深度
"""

import numpy as np
import json
import time
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict
import heapq


@dataclass
class ConfigPoint:
    """配置空間中的一個點"""
    p: int
    t: int
    m: int
    d: int
    
    @property
    def signature(self) -> str:
        return f"P{self.p}T{self.t}M{self.m}D{self.d}"
    
    @property
    def vector(self) -> np.ndarray:
        return np.array([self.p, self.t, self.m, self.d])
    
    def distance_to(self, other: 'ConfigPoint') -> float:
        return np.linalg.norm(self.vector - other.vector)
    
    def to_dict(self) -> Dict:
        return {"p": self.p, "t": self.t, "m": self.m, "d": self.d}


@dataclass
class ConfigEvaluation:
    """配置評估結果"""
    config: ConfigPoint
    drift_score: float
    confidence: float  # 0-1，基於歷史數據量
    n_samples: int
    last_evaluated: float
    
    @property
    def uncertainty(self) -> float:
        """不確定性 = 1 - confidence，但對極端drift給予更高權重"""
        base_uncertainty = 1.0 - self.confidence
        # 如果drift異常高/低，視為高不確定性（需要更多驗證）
        if self.drift_score > 0.8 or self.drift_score < 0.1:
            return min(base_uncertainty * 1.5, 1.0)
        return base_uncertainty


class CausalFastForwardScheduler:
    """
    Phase C: Causal Fast-Forward Scheduler
    
    目標：讓 Heavy Mode 從 O(N) 線性探索 → O(log N) 跳躍探索
    
    策略：
    1. 維護配置空間的不確定性地圖
    2. 優先選擇信息增益最大的配置點
    3. 利用因果邊進行跨區域推斷
    4. 動態調整探索粒度（資源緊張時跳過更多）
    """
    
    def __init__(self, 
                 config_ranges: Dict[str, Tuple[int, int]] = None,
                 exploration_budget: int = 100,
                 min_confidence_threshold: float = 0.7):
        
        # 配置空間範圍 (p, t, m, d)
        self.config_ranges = config_ranges or {
            "p": (1, 8),   # persona depth
            "t": (1, 8),   # transformation capacity
            "m": (1, 8),   # memory layers
            "d": (1, 5)    # diversity threshold
        }
        
        # 探索預算
        self.exploration_budget = exploration_budget
        self.min_confidence_threshold = min_confidence_threshold
        
        # 已評估的配置點
        self.evaluated_configs: Dict[str, ConfigEvaluation] = {}
        
        # 待探索隊列（優先級 = 不確定性 × 預期價值）
        self.exploration_queue: List[Tuple[float, str, ConfigPoint]] = []
        
        # 因果推斷的跳躍歷史
        self.jump_history: List[Dict] = []
        
        # 統計
        self.stats = {
            "total_evaluations": 0,
            "jumps_taken": 0,
            "linear_steps_avoided": 0,
            "time_saved_estimate_ms": 0
        }
        
        # 初始化：填充探索隊列
        self._initialize_exploration_space()
    
    def _initialize_exploration_space(self):
        """初始化配置空間，按不確定性排序"""
        p_range = range(self.config_ranges["p"][0], self.config_ranges["p"][1] + 1)
        t_range = range(self.config_ranges["t"][0], self.config_ranges["t"][1] + 1)
        m_range = range(self.config_ranges["m"][0], self.config_ranges["m"][1] + 1)
        d_range = range(self.config_ranges["d"][0], self.config_ranges["d"][1] + 1)
        
        # 生成所有配置點（粗粒度採樣）
        configs = []
        for p in p_range:
            for t in t_range:
                for m in m_range:
                    for d in d_range:
                        # 跳過明顯不合理的組合（啟發式剪枝）
                        if self._is_reasonable_config(p, t, m, d):
                            configs.append(ConfigPoint(p, t, m, d))
        
        # 按「與已知危險區的距離」排序，優先探索邊界
        for config in configs:
            priority = self._compute_initial_priority(config)
            heapq.heappush(self.exploration_queue, (-priority, config.signature, config))
        
        print(f"[FAST-FORWARD] Initialized {len(configs)} config points in exploration space")
    
    def _is_reasonable_config(self, p: int, t: int, m: int, d: int) -> bool:
        """啟發式：過濾明顯不合理的配置"""
        # 記憶層數不應小於轉換能力
        if m < t // 2:
            return False
        # persona depth 與 transformation 應該協調
        if abs(p - t) > 4:
            return False
        return True
    
    def _compute_initial_priority(self, config: ConfigPoint) -> float:
        """計算初始優先級（基於與默認配置的距離）"""
        default = ConfigPoint(2, 3, 3, 1)
        distance = config.distance_to(default)
        # 中等距離的點優先（探索邊界而非極端）
        return 1.0 / (1.0 + abs(distance - 3.0))
    
    def next_configuration(self, 
                          resource_pressure: float = 0.0,
                          target_drift_threshold: float = 0.5) -> Optional[ConfigPoint]:
        """
        選擇下一個要測試的配置
        
        Args:
            resource_pressure: 0-1，資源壓力（高壓力時跳躍更激進）
            target_drift_threshold: 目標drift閾值（優先探索接近閾值的區域）
        
        Returns:
            ConfigPoint or None (探索完成)
        """
        if not self.exploration_queue:
            return None
        
        # 資源壓力高時，激進跳躍（skip更多點）
        skip_factor = int(resource_pressure * 5)  # 0-5
        
        # 找到下一個值得測試的配置
        attempts = 0
        while self.exploration_queue and attempts < 50:
            neg_priority, sig, config = heapq.heappop(self.exploration_queue)
            
            # 已評估過的跳過
            if sig in self.evaluated_configs:
                attempts += 1
                continue
            
            # 檢查1：鄰居推斷
            inference = self._infer_from_neighbors(config)
            if inference and inference['confidence'] > self.min_confidence_threshold:
                self._record_jump(config, inference, "inference_skip")
                self.stats["linear_steps_avoided"] += 1
                attempts += 1
                continue
            
            # 檢查2：梯度跳躍（資源壓力高時）
            gradient_jump = self._try_gradient_jump(config, resource_pressure)
            if gradient_jump and gradient_jump['confidence'] > self.min_confidence_threshold:
                self._record_jump(config, gradient_jump, "gradient_jump")
                self.stats["linear_steps_avoided"] += 2  # 梯度跳躍節省更多步驟
                attempts += 1
                continue
            
            # 選中此配置
            return config
        
        return None
    
    def _try_gradient_jump(self, config: ConfigPoint, resource_pressure: float) -> Optional[Dict]:
        """
        梯度跳躍：如果沿某方向的配置趨勢明確，跳過中間點
        """
        if resource_pressure < 0.3 or len(self.evaluated_configs) < 5:
            return None
        
        # 找到最近的已評估點
        nearest = None
        min_dist = float('inf')
        for ev in self.evaluated_configs.values():
            dist = config.distance_to(ev.config)
            if dist < min_dist and dist > 0:
                min_dist = dist
                nearest = ev
        
        if not nearest or min_dist > 2.5:
            return None
        
        # 計算梯度方向
        direction = config.vector - nearest.config.vector
        direction_norm = np.linalg.norm(direction)
        if direction_norm == 0:
            return None
        
        direction = direction / direction_norm
        
        # 檢查同方向的點是否有明確趨勢
        aligned_configs = []
        for ev in self.evaluated_configs.values():
            if ev.config.signature == config.signature:
                continue
            vec_to_ev = ev.config.vector - nearest.config.vector
            dist_to_ev = np.linalg.norm(vec_to_ev)
            if dist_to_ev == 0:
                continue
            vec_to_ev = vec_to_ev / dist_to_ev
            # 檢查是否大致同方向
            alignment = np.dot(direction, vec_to_ev)
            if alignment > 0.7:  # 夾角小於45度
                aligned_configs.append((dist_to_ev, ev))
        
        if len(aligned_configs) < 2:
            return None
        
        # 檢查趨勢一致性
        aligned_configs.sort(key=lambda x: x[0])
        drifts = [ev.drift_score for _, ev in aligned_configs]
        
        # 如果趨勢單調，可以跳躍
        drift_variance = np.var(drifts)
        trend_consistency = 1.0 / (1.0 + drift_variance)
        
        # 外推預測
        if len(drifts) >= 2:
            # 簡單線性外推
            trend = drifts[-1] - drifts[0]
            extrapolated = drifts[-1] + trend * (min_dist / aligned_configs[-1][0])
            inferred_drift = np.clip(extrapolated, 0.0, 1.0)
        else:
            inferred_drift = np.mean(drifts)
        
        confidence = min(len(aligned_configs) / 3, 1.0) * trend_consistency * 0.8
        
        return {
            "inferred_drift": inferred_drift,
            "confidence": confidence,
            "jump_type": "gradient_extrapolation",
            "aligned_points": len(aligned_configs)
        }
    
    def _infer_from_neighbors(self, config: ConfigPoint) -> Optional[Dict]:
        """
        從鄰居配置推斷當前配置的性能
        使用更激進的推斷策略以啟用更多跳躍
        """
        # 擴大搜索半徑以找到更多鄰居
        neighbors = self._get_neighbor_evaluations(config, radius=3.0)
        
        if len(neighbors) < 1:  # 只需要1個鄰居即可推斷
            return None
        
        # 基於距離加權的插值
        weights = []
        drift_scores = []
        
        for neighbor in neighbors:
            dist = config.distance_to(neighbor.config)
            if dist == 0:
                continue
            # 使用高斯權重而非倒數平方，對遠處點更友好
            weight = np.exp(-dist ** 2 / 4.0)
            weights.append(weight)
            drift_scores.append(neighbor.drift_score)
        
        if not weights:
            return None
        
        # 加權平均
        total_weight = sum(weights)
        inferred_drift = sum(w * d for w, d in zip(weights, drift_scores)) / total_weight
        
        # 計算方差（高方差 = 低置信度）
        weighted_var = sum(w * (d - inferred_drift) ** 2 for w, d in zip(weights, drift_scores)) / total_weight
        variance_penalty = 1.0 / (1.0 + weighted_var * 10)
        
        # 置信度：基於鄰居數量、鄰居置信度、方差
        avg_neighbor_confidence = np.mean([n.confidence for n in neighbors])
        # 只需要2個高置信度鄰居即可達到max confidence
        neighbor_factor = min(len(neighbors) / 2, 1.0)
        confidence = neighbor_factor * avg_neighbor_confidence * variance_penalty
        
        return {
            "inferred_drift": inferred_drift,
            "confidence": confidence,
            "neighbors_used": len(neighbors),
            "variance": float(weighted_var)
        }
    
    def _get_neighbor_evaluations(self, config: ConfigPoint, radius: float = 2.0) -> List[ConfigEvaluation]:
        """獲取指定半徑內的鄰居評估"""
        neighbors = []
        for ev in self.evaluated_configs.values():
            if config.distance_to(ev.config) <= radius:
                neighbors.append(ev)
        return neighbors
    
    def _record_jump(self, target: ConfigPoint, inference: Dict, jump_type: str):
        """記錄一次跳躍"""
        self.jump_history.append({
            "timestamp": time.time(),
            "target_config": target.to_dict(),
            "inferred_drift": inference['inferred_drift'],
            "inference_confidence": inference['confidence'],
            "jump_type": jump_type
        })
        self.stats["jumps_taken"] += 1
    
    def report_evaluation(self, config: ConfigPoint, drift_score: float):
        """
        報告配置評估結果，更新不確定性地圖
        
        Args:
            config: 被評估的配置
            drift_score: 測得的drift score
        """
        sig = config.signature
        
        if sig in self.evaluated_configs:
            # 更新現有評估
            existing = self.evaluated_configs[sig]
            # 指數移動平均
            alpha = 0.3
            existing.drift_score = alpha * drift_score + (1 - alpha) * existing.drift_score
            existing.n_samples += 1
            existing.confidence = min(existing.n_samples / 5, 1.0)
            existing.last_evaluated = time.time()
        else:
            # 新評估
            self.evaluated_configs[sig] = ConfigEvaluation(
                config=config,
                drift_score=drift_score,
                confidence=0.2,  # 初始置信度低
                n_samples=1,
                last_evaluated=time.time()
            )
        
        self.stats["total_evaluations"] += 1
        
        # 觸發相關配置的不確定性更新
        self._propagate_uncertainty_update(config)
    
    def _propagate_uncertainty_update(self, evaluated_config: ConfigPoint):
        """將評估結果傳播到鄰居，更新其優先級"""
        # 找到隊列中受影響的配置
        new_queue = []
        
        while self.exploration_queue:
            neg_priority, sig, config = heapq.heappop(self.exploration_queue)
            
            # 重新計算優先級（基於與新評估點的距離）
            new_priority = self._compute_dynamic_priority(config)
            
            heapq.heappush(new_queue, (-new_priority, sig, config))
        
        self.exploration_queue = new_queue
    
    def _compute_dynamic_priority(self, config: ConfigPoint) -> float:
        """動態計算配置探索優先級"""
        # 基礎：與已評估點的平均距離（越遠越優先）
        if not self.evaluated_configs:
            return self._compute_initial_priority(config)
        
        distances = []
        for ev in self.evaluated_configs.values():
            dist = config.distance_to(ev.config)
            distances.append(dist)
        
        avg_distance = np.mean(distances) if distances else 5.0
        min_distance = min(distances) if distances else 5.0
        
        # 優先級組成：
        # 1. 距離已知區域的遠近（探索 vs 利用）
        # 2. 不確定性（需要更多樣本）
        
        exploration_bonus = avg_distance / 10.0  # 0-1
        
        # 如果很近，利用已知情報
        if min_distance < 1.5 and self.evaluated_configs:
            nearest = min(self.evaluated_configs.values(), 
                         key=lambda e: config.distance_to(e.config))
            uncertainty_bonus = 1.0 - nearest.confidence
        else:
            uncertainty_bonus = 0.8  # 未知區域高不確定性
        
        return exploration_bonus * 0.3 + uncertainty_bonus * 0.7
    
    def get_fast_forward_plan(self, n_steps: int = 10) -> List[Dict]:
        """
        生成 Fast-Forward 探索計劃
        
        Returns:
            List of {config, priority, estimated_drift, confidence}
        """
        plan = []
        
        # 保存當前隊列狀態
        saved_queue = self.exploration_queue.copy()
        
        for _ in range(n_steps):
            if not self.exploration_queue:
                break
            
            neg_priority, sig, config = heapq.heappop(self.exploration_queue)
            
            inference = self._infer_from_neighbors(config)
            
            plan.append({
                "config": config.to_dict(),
                "priority": -neg_priority,
                "estimated_drift": inference['inferred_drift'] if inference else None,
                "inference_confidence": inference['confidence'] if inference else 0.0
            })
        
        # 恢復隊列
        self.exploration_queue = saved_queue
        
        return plan
    
    def get_exploration_summary(self) -> Dict:
        """獲取探索摘要"""
        if not self.evaluated_configs:
            return {"status": "not_started"}
        
        drift_scores = [ev.drift_score for ev in self.evaluated_configs.values()]
        confidences = [ev.confidence for ev in self.evaluated_configs.values()]
        
        # 識別危險區域（drift > 0.7）
        danger_zone = [ev for ev in self.evaluated_configs.values() if ev.drift_score > 0.7]
        
        # 識別安全區域（drift < 0.3）
        safe_zone = [ev for ev in self.evaluated_configs.values() if ev.drift_score < 0.3]
        
        return {
            "status": "active",
            "evaluated_configs": len(self.evaluated_configs),
            "remaining_queue": len(self.exploration_queue),
            "avg_drift": float(np.mean(drift_scores)),
            "max_drift": float(np.max(drift_scores)),
            "min_drift": float(np.min(drift_scores)),
            "avg_confidence": float(np.mean(confidences)),
            "danger_zone_configs": len(danger_zone),
            "safe_zone_configs": len(safe_zone),
            "jumps_taken": self.stats["jumps_taken"],
            "linear_steps_avoided": self.stats["linear_steps_avoided"],
            "efficiency_gain": self.stats["linear_steps_avoided"] / max(self.stats["total_evaluations"], 1)
        }


# ============================================================================
# INTEGRATION: Heavy Mode + Fast Forward
# ============================================================================

class HeavyModeFastForwardIntegration:
    """
    Heavy Mode 與 Fast-Forward Scheduler 的集成
    """
    
    def __init__(self, heavy_engine, scheduler: CausalFastForwardScheduler = None):
        self.heavy_engine = heavy_engine
        self.scheduler = scheduler or CausalFastForwardScheduler()
        
        # 執行統計
        self.execution_log = []
    
    def run_fast_forward_cycle(self, resource_pressure: float = 0.0) -> Dict:
        """
        執行一次 Fast-Forward 週期
        
        Returns:
            execution report
        """
        cycle_start = time.time()
        
        # 1. 獲取下一個配置（Fast-Forward 選擇）
        config = self.scheduler.next_configuration(resource_pressure=resource_pressure)
        
        if config is None:
            return {"status": "exploration_complete"}
        
        print(f"[FAST-FORWARD] Testing config: {config.signature}")
        
        # 2. 在 Heavy Mode 中測試此配置
        # 這裡我們調整 heavy_engine 的配置並運行簡化測試
        drift_score = self._test_configuration_in_heavy_mode(config)
        
        # 3. 報告結果
        self.scheduler.report_evaluation(config, drift_score)
        
        cycle_time = time.time() - cycle_start
        
        result = {
            "config": config.to_dict(),
            "drift_score": drift_score,
            "cycle_time": cycle_time,
            "resource_pressure": resource_pressure
        }
        
        self.execution_log.append(result)
        
        return result
    
    def _test_configuration_in_heavy_mode(self, config: ConfigPoint) -> float:
        """
        在 Heavy Mode 中測試配置，返回 drift score
        
        注意：這裡使用簡化測試，真實場景需要調整 heavy_engine 參數
        """
        # 模擬：根據配置計算理論 drift
        # 實際實現需要調用 heavy_engine 的真實計算
        
        # 啟發式：某些配置組合更容易產生 drift
        base_drift = 0.25
        
        # persona depth 過高增加 drift
        if config.p > 5:
            base_drift += 0.15
        
        # transformation 與 memory 不匹配增加 drift
        if config.t > config.m:
            base_drift += 0.1 * (config.t - config.m)
        
        # diversity 閾值影響
        if config.d > 3:
            base_drift += 0.05 * (config.d - 3)
        
        # 添加噪聲
        noise = np.random.normal(0, 0.05)
        drift = np.clip(base_drift + noise, 0.0, 1.0)
        
        return drift
    
    def run_fast_forward_benchmark(self, n_cycles: int = 20) -> Dict:
        """
        運行 Fast-Forward Benchmark
        """
        print("\n" + "="*70)
        print("CAUSAL FAST-FORWARD BENCHMARK")
        print("="*70)
        
        for i in range(n_cycles):
            # 動態調整資源壓力
            resource_pressure = i / n_cycles  # 逐漸增加壓力
            
            result = self.run_fast_forward_cycle(resource_pressure=resource_pressure)
            
            if result.get("status") == "exploration_complete":
                print(f"[FAST-FORWARD] Exploration complete at cycle {i}")
                break
            
            if i % 5 == 0:
                summary = self.scheduler.get_exploration_summary()
                print(f"  Cycle {i}: {summary['evaluated_configs']} configs evaluated, "
                      f"efficiency gain: {summary.get('efficiency_gain', 0):.2f}x")
        
        # 最終報告
        final_summary = self.scheduler.get_exploration_summary()
        plan = self.scheduler.get_fast_forward_plan(n_steps=5)
        
        print("\n" + "="*70)
        print("FAST-FORWARD RESULTS")
        print("="*70)
        print(f"Configs evaluated: {final_summary['evaluated_configs']}")
        print(f"Jumps taken: {final_summary['jumps_taken']}")
        print(f"Steps avoided: {final_summary['linear_steps_avoided']}")
        print(f"Efficiency gain: {final_summary['efficiency_gain']:.2f}x")
        print(f"Avg drift: {final_summary['avg_drift']:.3f}")
        print(f"Danger zone configs: {final_summary['danger_zone_configs']}")
        print(f"Safe zone configs: {final_summary['safe_zone_configs']}")
        
        print("\nTop 5 next explorations:")
        for i, item in enumerate(plan, 1):
            drift_str = f"{item['estimated_drift']:.2f}" if item['estimated_drift'] else "N/A"
            print(f"  {i}. P{item['config']['p']}T{item['config']['t']}M{item['config']['m']}D{item['config']['d']} "
                  f"(priority={item['priority']:.2f}, est_drift={drift_str})")
        
        return {
            "summary": final_summary,
            "execution_log": self.execution_log,
            "next_explorations": plan
        }


# ============================================================================
# 測試入口
# ============================================================================

if __name__ == "__main__":
    print("CAUSAL FAST-FORWARD SCHEDULER - Phase C Test")
    print()
    
    # 創建調度器
    scheduler = CausalFastForwardScheduler(
        exploration_budget=50,
        min_confidence_threshold=0.6
    )
    
    # 運行 benchmark
    integration = HeavyModeFastForwardIntegration(heavy_engine=None, scheduler=scheduler)
    results = integration.run_fast_forward_benchmark(n_cycles=30)
    
    print("\n✓ Phase C Fast-Forward Test Complete")
