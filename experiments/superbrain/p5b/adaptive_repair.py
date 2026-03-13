"""
P5b Adaptive Repair
===================
Week 2: 2-class repair (reset, rollback)
Hard constraint: NO CORE WRITE in any repair path
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum
import copy


class RepairStrategy(Enum):
    RESET = "reset"       # 重置到默认状态
    ROLLBACK = "rollback" # 回滚到之前快照


@dataclass
class RepairPlan:
    """
    修复计划 - 结构化输出用于审计
    
    Hard constraint: requires_core_lock 用于验证无core写入
    """
    strategy: RepairStrategy
    target_scope: str  # "adaptive_only" | "state_partial"
    expected_risk_reduction: float
    expected_capability_loss: float
    requires_core_lock: bool  # 必须为False，否则违反约束
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy": self.strategy.value,
            "target_scope": self.target_scope,
            "expected_risk_reduction": self.expected_risk_reduction,
            "expected_capability_loss": self.expected_capability_loss,
            "requires_core_lock": self.requires_core_lock
        }


@dataclass
class RepairResult:
    """修复执行结果"""
    success: bool
    strategy_used: RepairStrategy
    actual_capability_loss: float
    core_modified: bool  # 必须为False
    post_repair_state: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "strategy_used": self.strategy_used.value,
            "actual_capability_loss": self.actual_capability_loss,
            "core_modified": self.core_modified,
            "post_repair_state_hash": hash(str(self.post_repair_state)) % 10000
        }


class AdaptiveRepair:
    """
    P5b 自适应层修复系统 - Week 2 版本
    
    支持2类修复策略：
    - reset: 重置adaptive层到默认状态
    - rollback: 回滚到之前保存的快照
    
    Hard constraint: 任何修复路径都不得修改core identity
    """
    
    def __init__(self):
        self.repair_history: List[RepairResult] = []
        self.state_snapshots: List[Dict[str, Any]] = []
        self._default_adaptive = {
            "capabilities": {},
            "skill_weights": {},
            "strategy": "balanced"
        }
    
    def create_plan(
        self,
        anomaly_type: str,
        severity: float,
        current_state: Dict[str, Any]
    ) -> RepairPlan:
        """
        为异常创建修复计划
        
        Hard constraint: requires_core_lock 必须为 False
        """
        if anomaly_type == "memory_noise":
            # 噪声适合reset
            return RepairPlan(
                strategy=RepairStrategy.RESET,
                target_scope="adaptive_only",
                expected_risk_reduction=0.8,
                expected_capability_loss=0.3,  # 会丢失一些学习
                requires_core_lock=False  # 硬约束
            )
        
        elif anomaly_type == "goal_conflict":
            # 冲突适合rollback
            return RepairPlan(
                strategy=RepairStrategy.ROLLBACK,
                target_scope="state_partial",
                expected_risk_reduction=0.9,
                expected_capability_loss=0.1,  # 只丢失最近变化
                requires_core_lock=False  # 硬约束
            )
        
        else:
            # 默认reset
            return RepairPlan(
                strategy=RepairStrategy.RESET,
                target_scope="adaptive_only",
                expected_risk_reduction=0.5,
                expected_capability_loss=0.5,
                requires_core_lock=False
            )
    
    def execute_repair(
        self,
        plan: RepairPlan,
        current_state: Dict[str, Any],
        core_identity: Any  # 用于验证不修改
    ) -> RepairResult:
        """
        执行修复计划
        
        Args:
            plan: 修复计划
            current_state: 当前状态
            core_identity: 核心身份（用于验证不修改）
        
        Returns:
            RepairResult
        
        Hard constraint: 如果检测到core修改，返回失败
        """
        # 验证计划不违反约束
        if plan.requires_core_lock:
            return RepairResult(
                success=False,
                strategy_used=plan.strategy,
                actual_capability_loss=0.0,
                core_modified=False,  # 拒绝执行，所以未修改
                post_repair_state=current_state
            )
        
        # 执行修复
        if plan.strategy == RepairStrategy.RESET:
            new_state = self._execute_reset(current_state)
        elif plan.strategy == RepairStrategy.ROLLBACK:
            new_state = self._execute_rollback(current_state)
        else:
            new_state = current_state
        
        # 验证core未被修改
        core_modified = self._check_core_modification(
            current_state, new_state, core_identity
        )
        
        if core_modified:
            # 严重违规 - 拒绝此次修复
            return RepairResult(
                success=False,
                strategy_used=plan.strategy,
                actual_capability_loss=0.0,
                core_modified=True,  # 标记违规
                post_repair_state=current_state  # 保持原状态
            )
        
        # 计算能力损失
        capability_loss = self._compute_capability_loss(
            current_state, new_state
        )
        
        result = RepairResult(
            success=True,
            strategy_used=plan.strategy,
            actual_capability_loss=capability_loss,
            core_modified=False,
            post_repair_state=new_state
        )
        
        self.repair_history.append(result)
        return result
    
    def _execute_reset(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """执行reset策略"""
        new_state = copy.deepcopy(state)
        # 只修改adaptive_memory，保留capabilities但降低权重
        new_state["adaptive_memory"] = copy.deepcopy(self._default_adaptive)
        # 保留原始capabilities，但标记为已重置
        if "capabilities" in new_state:
            # 保留capabilites但降低值表示需要重新学习
            new_state["capabilities"] = {
                k: max(0.1, v * 0.5) for k, v in new_state["capabilities"].items()
            }
        # 保留core_identity和其他非adaptive字段
        return new_state
    
    def _execute_rollback(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """执行rollback策略"""
        if not self.state_snapshots:
            # 无快照，fallback到reset
            return self._execute_reset(state)
        
        # 使用最近的快照
        snapshot = self.state_snapshots[-1]
        new_state = copy.deepcopy(snapshot)
        
        # 确保不覆盖当前的core_identity
        if "core_identity" in state:
            new_state["core_identity"] = state["core_identity"]
        
        return new_state
    
    def _check_core_modification(
        self,
        before: Dict[str, Any],
        after: Dict[str, Any],
        core_identity: Any
    ) -> bool:
        """
        检查core是否被修改
        
        Returns:
            True if core modified (VIOLATION), False otherwise
        """
        # 检查core_identity字段
        before_core = before.get("core_identity")
        after_core = after.get("core_identity")
        
        if before_core != after_core:
            return True
        
        # 检查其他core相关字段
        core_fields = ["value_rankings", "mission_statement", "identity_boundary"]
        for field in core_fields:
            if field in before and field in after:
                if before[field] != after[field]:
                    return True
        
        return False
    
    def _compute_capability_loss(
        self,
        before: Dict[str, Any],
        after: Dict[str, Any]
    ) -> float:
        """计算能力损失比例"""
        before_caps = set(before.get("capabilities", {}).keys())
        after_caps = set(after.get("capabilities", {}).keys())
        
        if not before_caps:
            return 0.0
        
        lost = before_caps - after_caps
        return len(lost) / len(before_caps)
    
    def save_snapshot(self, state: Dict[str, Any]):
        """保存状态快照用于rollback"""
        self.state_snapshots.append(copy.deepcopy(state))
        # 只保留最近10个快照
        if len(self.state_snapshots) > 10:
            self.state_snapshots.pop(0)
    
    def get_repair_history(self) -> List[RepairResult]:
        """获取修复历史"""
        return self.repair_history.copy()
    
    def verify_no_core_writes(self) -> bool:
        """
        验证所有历史修复都没有修改core
        
        Week 2 hard constraint verification
        """
        for result in self.repair_history:
            if result.core_modified:
                return False
        return True
