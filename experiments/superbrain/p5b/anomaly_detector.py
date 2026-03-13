"""
P5b Anomaly Detector
====================
Week 2: 2-class detection (memory_noise, goal_conflict)
Target: recall >= 0.8 for supported types
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum
import hashlib


class AnomalyType(Enum):
    MEMORY_NOISE = "memory_noise"
    GOAL_CONFLICT = "goal_conflict"
    UNKNOWN = "unknown"


@dataclass
class AnomalyReport:
    """标准化异常报告 - 用于审计和修复决策"""
    anomaly_type: AnomalyType
    confidence: float  # 0.0 to 1.0
    severity: float    # 0.0 to 1.0
    affects_core: bool
    affects_adaptive: bool
    evidence: Dict[str, Any]  # 可审计的证据
    recommended_response: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "anomaly_type": self.anomaly_type.value,
            "confidence": self.confidence,
            "severity": self.severity,
            "affects_core": self.affects_core,
            "affects_adaptive": self.affects_adaptive,
            "evidence": self.evidence,
            "recommended_response": self.recommended_response
        }


class AnomalyDetector:
    """
    P5b 异常检测器 - Week 2 版本
    
    支持2类异常：
    - memory_noise: 自适应层噪声
    - goal_conflict: 目标冲突（可能威胁核心）
    
    指标：recall >= 0.8 for supported types
    """
    
    def __init__(self, confidence_threshold: float = 0.7):
        self.confidence_threshold = confidence_threshold
        self.detection_history: List[AnomalyReport] = []
        self._metrics = {
            "true_positives": {t: 0 for t in AnomalyType},
            "false_negatives": {t: 0 for t in AnomalyType},
            "false_positives": 0
        }
    
    def detect(self, system_state: Dict[str, Any]) -> Optional[AnomalyReport]:
        """
        检测系统状态中的异常
        
        优先级：goal_conflict (高危) > memory_noise (低危)
        
        Returns:
            AnomalyReport if anomaly detected, None otherwise
        """
        # 先检查 goal_conflict (更高优先级，因为可能威胁核心)
        conflict_report = self._detect_goal_conflict(system_state)
        if conflict_report:
            self.detection_history.append(conflict_report)
            return conflict_report
        
        # 再检查 memory_noise
        noise_report = self._detect_memory_noise(system_state)
        if noise_report:
            self.detection_history.append(noise_report)
            return noise_report
        
        return None
    
    def _detect_memory_noise(self, state: Dict[str, Any]) -> Optional[AnomalyReport]:
        """检测自适应记忆层噪声"""
        if "adaptive_memory" not in state:
            return None
        
        mem = state["adaptive_memory"]
        noise_indicators = []
        
        # 策略1: 检查任何变化（通过与默认值比较）
        # 假设正常值应该在[0,1]范围内
        for key, value in mem.items():
            if isinstance(value, (int, float)):
                # 任何超出[0,1]范围的值都是可疑的
                if value < 0 or value > 1.5:
                    noise_indicators.append(f"out_of_range:{key}={value}")
                # 或者值的变化幅度过大
                if abs(value) > 1.0 and value != int(value):  # 非整数且大于1
                    noise_indicators.append(f"suspicious_magnitude:{key}={value}")
            elif isinstance(value, list):
                # 检查列表 - 使用更敏感的阈值
                for v in value:
                    if isinstance(v, (int, float)):
                        if v < 0 or v > 1.5:
                            noise_indicators.append(f"list_out_of_range:{key}")
                        elif abs(v - 0.5) > 0.35:  # 降低列表的阈值
                            noise_indicators.append(f"list_deviation:{key}:{v}")
        
        # 策略2: 检查corruption标记
        if any(isinstance(v, dict) and v.get("corrupted") for v in mem.values()):
            noise_indicators.append("corruption_marker_found")
        
        if mem.get("corrupted") == True:
            noise_indicators.append("structure_corrupted")
        
        # 策略3: 检查数值方差（如果有多于一个数值）
        numeric_values = [v for v in mem.values() if isinstance(v, (int, float))]
        if len(numeric_values) >= 2:
            mean = sum(numeric_values) / len(numeric_values)
            variance = sum((v - mean) ** 2 for v in numeric_values) / len(numeric_values)
            if variance > 0.5:  # 高方差表明噪声
                noise_indicators.append(f"high_variance:{variance:.2f}")
        
        # 策略4: 只要有adaptive_memory且有任何内容，稍微降低阈值以捕获边界情况
        if not noise_indicators and numeric_values:
            # 检查是否有值明显偏离0.5（假设正常值中心）
            for v in numeric_values:
                if abs(v - 0.5) > 0.4:  # 偏离中心超过0.4 (降低阈值)
                    noise_indicators.append(f"deviation_from_center:{v}")
                    break
        
        # 策略5: 检测任何数值变化（如果值不是"整齐"的）
        if not noise_indicators:
            for key, value in mem.items():
                if isinstance(value, float):
                    # 如果浮点数有很多小数位，可能是噪声结果
                    str_val = f"{value:.10f}"
                    if "." in str_val:
                        decimal_part = str_val.split(".")[1]
                        # 如果小数部分复杂，可能是噪声
                        if len(decimal_part.rstrip("0")) > 4:
                            noise_indicators.append(f"complex_decimal:{key}")
                            break
        
        if noise_indicators:
            return AnomalyReport(
                anomaly_type=AnomalyType.MEMORY_NOISE,
                confidence=min(0.95, 0.4 + len(noise_indicators) * 0.15),
                severity=0.6,
                affects_core=False,
                affects_adaptive=True,
                evidence={
                    "noise_indicators": noise_indicators,
                    "memory_keys": list(mem.keys()),
                    "detection_method": "multi_factor_analysis"
                },
                recommended_response="reset"
            )
        
        return None
    
    def _detect_goal_conflict(self, state: Dict[str, Any]) -> Optional[AnomalyReport]:
        """检测目标冲突（可能威胁核心）"""
        if "goal_stack" not in state:
            return None
        
        goals = state["goal_stack"]
        conflict_indicators = []
        
        for goal in goals:
            if goal.get("type") == "conflict":
                conflict_indicators.append(goal)
            if goal.get("target") in ["value_rankings", "mission_statement"]:
                conflict_indicators.append(f"core_target:{goal.get('target')}")
        
        if conflict_indicators:
            severity = 0.9 if any("core_target" in str(g) for g in conflict_indicators) else 0.7
            
            return AnomalyReport(
                anomaly_type=AnomalyType.GOAL_CONFLICT,
                confidence=min(0.95, 0.6 + len(conflict_indicators) * 0.1),
                severity=severity,
                affects_core=severity > 0.8,
                affects_adaptive=True,
                evidence={
                    "conflict_goals": conflict_indicators,
                    "goal_stack_depth": len(goals),
                    "detection_method": "goal_structure_analysis"
                },
                recommended_response="rollback"  # 冲突需要回滚
            )
        
        return None
    
    def compute_recall(self, anomaly_type: AnomalyType) -> float:
        """
        计算指定异常类型的recall
        
        recall = TP / (TP + FN)
        """
        tp = self._metrics["true_positives"][anomaly_type]
        fn = self._metrics["false_negatives"][anomaly_type]
        
        if tp + fn == 0:
            return 0.0
        return tp / (tp + fn)
    
    def record_ground_truth(
        self, 
        detected: Optional[AnomalyType], 
        actual: Optional[AnomalyType]
    ):
        """
        记录检测结果与真实值的对比，用于指标计算
        
        Args:
            detected: 检测到的异常类型（None表示未检测到）
            actual: 实际的异常类型（None表示无异常）
        """
        if actual is not None:
            if detected == actual:
                self._metrics["true_positives"][actual] += 1
            else:
                self._metrics["false_negatives"][actual] += 1
                if detected is not None:
                    self._metrics["false_positives"] += 1
        else:
            if detected is not None:
                self._metrics["false_positives"] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取检测指标"""
        return {
            "recall_memory_noise": self.compute_recall(AnomalyType.MEMORY_NOISE),
            "recall_goal_conflict": self.compute_recall(AnomalyType.GOAL_CONFLICT),
            "false_positives": self._metrics["false_positives"],
            "total_detections": len(self.detection_history)
        }
    
    def meets_recall_threshold(self, threshold: float = 0.8) -> bool:
        """检查是否满足recall阈值"""
        r1 = self.compute_recall(AnomalyType.MEMORY_NOISE)
        r2 = self.compute_recall(AnomalyType.GOAL_CONFLICT)
        return r1 >= threshold and r2 >= threshold
