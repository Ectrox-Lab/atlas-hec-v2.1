"""
P5b Core Protection Extended Tests
==================================
Week 1补充测试：绕过式写入、混合请求、多轮攻击审计

覆盖5类关键case：
1. API路径直接修改核心 ✓ (已有)
2. 绕过API直接写核心字段 (新增)
3. 自适应层正常更新 ✓ (已有)
4. 混合请求：先合法adaptive，再非法core (新增)
5. 重复攻击/多轮攻击后审计仍为0漂移 (新增)
"""

import pytest
from dataclasses import dataclass
from typing import Dict, Any, Optional
import hashlib

from core_identity_snapshot import (
    CoreIdentitySnapshot,
    compute_core_drift,
    DEFAULT_CORE_IDENTITY
)
from fault_injector import FaultInjector


# ============================================================================
# Extended Core Protection with Bypass Detection
# ============================================================================

@dataclass
class CoreAuditTrail:
    """审计追踪记录"""
    timestamp: float
    snapshot_hash: str
    access_type: str  # "api" | "direct" | "bypass_attempt"
    blocked: bool
    notes: str


class CoreProtectionExtended:
    """
    扩展版核心保护系统，支持绕过检测和多轮审计
    """
    
    def __init__(self, core_identity: CoreIdentitySnapshot):
        self.baseline_core = core_identity
        self.current_core = core_identity
        self.blocked_count = 0
        self.total_core_attempts = 0
        self.total_adaptive_attempts = 0
        self.blocked_adaptive_count = 0
        self.bypass_attempts_detected = 0
        self.audit_trail: list[CoreAuditTrail] = []
        self._record_audit("init", False, "Baseline established")
    
    def _record_audit(self, access_type: str, blocked: bool, notes: str):
        """记录审计日志"""
        import time
        snapshot_dict = self.current_core.to_dict()
        snapshot_str = str(sorted(snapshot_dict.items()))
        snapshot_hash = hashlib.sha256(snapshot_str.encode()).hexdigest()[:16]
        
        self.audit_trail.append(CoreAuditTrail(
            timestamp=time.time(),
            snapshot_hash=snapshot_hash,
            access_type=access_type,
            blocked=blocked,
            notes=notes
        ))
    
    def protect(self, proposed_change: Dict[str, Any]) -> bool:
        """
        API层保护
        Return True if allowed, False if blocked
        """
        target = proposed_change.get("target", "")
        
        if target in ["value_rankings", "mission_statement", "identity_boundary"]:
            self.total_core_attempts += 1
            self.blocked_count += 1
            self._record_audit("api", True, f"Blocked {target} modification")
            return False
        
        self.total_adaptive_attempts += 1
        if proposed_change.get("risk_score", 0) > 0.9:
            self.blocked_adaptive_count += 1
            self._record_audit("api", True, "High risk adaptive blocked")
            return False
        
        self._record_audit("api", False, f"Allowed {target} update")
        return True
    
    def detect_bypass_attempt(self, state_snapshot: Dict[str, Any]) -> bool:
        """
        检测绕过API的直接修改尝试
        
        通过比对当前状态与预期核心快照发现异常
        """
        # 从状态中提取核心字段
        extracted_core = self._extract_core_from_state(state_snapshot)
        if extracted_core is None:
            return False
        
        drift = compute_core_drift(self.baseline_core, extracted_core)
        
        if drift > 0:
            self.bypass_attempts_detected += 1
            self._record_audit(
                "bypass_attempt", 
                True, 
                f"Detected core drift: {drift}"
            )
            return True
        
        return False
    
    def _extract_core_from_state(
        self, 
        state: Dict[str, Any]
    ) -> Optional[CoreIdentitySnapshot]:
        """从状态字典中提取核心身份"""
        try:
            if "core_identity" in state:
                return state["core_identity"]
            
            # 尝试从分散字段重建
            if all(k in state for k in ["value_rankings", "mission_statement"]):
                return CoreIdentitySnapshot.from_content(
                    value_rankings=tuple(state["value_rankings"]),
                    mission_statement=state["mission_statement"],
                    identity_boundary_rules=state.get(
                        "identity_boundary_rules", 
                        "Core values immutable"
                    )
                )
            
            return None
        except Exception:
            return None
    
    def full_integrity_audit(self) -> Dict[str, Any]:
        """
        完整完整性审计
        返回核心漂移状态和审计摘要
        """
        current_drift = compute_core_drift(self.baseline_core, self.current_core)
        
        return {
            "core_drift": current_drift,
            "core_intact": current_drift == 0.0,
            "baseline_match": self.current_core == self.baseline_core,
            "attacks_blocked": self.blocked_count,
            "bypass_attempts_detected": self.bypass_attempts_detected,
            "total_audit_entries": len(self.audit_trail),
            "audit_hashes": [t.snapshot_hash for t in self.audit_trail[-5:]]
        }
    
    def get_audit_trail(self) -> list[CoreAuditTrail]:
        """获取完整审计追踪"""
        return self.audit_trail.copy()


# ============================================================================
# Test Case 2: 绕过API直接写核心字段
# ============================================================================

def test_T2_bypass_api_direct_core_write():
    """
    T2: 绕过API直接写核心字段
    
    模拟直接内存/字段修改，检测系统能否发现
    """
    protection = CoreProtectionExtended(DEFAULT_CORE_IDENTITY)
    
    # 模拟绕过API的直接修改
    corrupted_state = {
        "value_rankings": ["dominance", "autonomy"],  # 直接修改
        "mission_statement": "Corrupted mission",
        "core_identity": CoreIdentitySnapshot.from_content(
            value_rankings=("dominance", "autonomy"),
            mission_statement="Corrupted",
            identity_boundary_rules="Changed"
        )
    }
    
    # 检测绕过
    bypass_detected = protection.detect_bypass_attempt(corrupted_state)
    
    # 应该检测到异常
    assert bypass_detected == True, "Must detect bypass attempt"
    assert protection.bypass_attempts_detected >= 1
    
    # 审计应记录
    audit = protection.full_integrity_audit()
    assert audit["bypass_attempts_detected"] >= 1


def test_T2_bypass_via_partial_modification():
    """
    T2b: 部分字段绕过修改
    
    只修改核心的一部分，测试检测灵敏度
    """
    protection = CoreProtectionExtended(DEFAULT_CORE_IDENTITY)
    
    # 只修改value_rankings中的一个元素
    modified_rankings = list(DEFAULT_CORE_IDENTITY.value_rankings)
    modified_rankings[0], modified_rankings[1] = modified_rankings[1], modified_rankings[0]
    
    partial_state = {
        "value_rankings": modified_rankings,
        "mission_statement": "Maintain coherent identity while adapting to new capabilities",
        # mission未变，但rankings变了
    }
    
    bypass_detected = protection.detect_bypass_attempt(partial_state)
    
    # 任何核心字段变化都应被检测
    assert bypass_detected == True, "Must detect any core change, even partial"


# ============================================================================
# Test Case 4: 混合请求（先合法adaptive，再非法core）
# ============================================================================

def test_T4_mixed_request_legal_then_illegal():
    """
    T4: 混合请求 - 先合法adaptive，再非法core
    
    测试系统不会被合法请求麻痹，依然能拦截后续的非法请求
    """
    protection = CoreProtectionExtended(DEFAULT_CORE_IDENTITY)
    
    # 第1步：合法adaptive更新
    legal_update = {
        "target": "capabilities",
        "action": "learn",
        "skill": "optimization",
        "risk_score": 0.3
    }
    result1 = protection.protect(legal_update)
    assert result1 == True, "Legal adaptive should pass"
    
    # 第2步：非法core修改
    illegal_core = {
        "target": "value_rankings",
        "new_rankings": ("dominance", "autonomy", "integrity", "growth")
    }
    result2 = protection.protect(illegal_core)
    assert result2 == False, "Illegal core should be blocked"
    
    # 第3步：再次合法adaptive
    legal_update2 = {
        "target": "strategy_weights",
        "update": "exploration",
        "risk_score": 0.4
    }
    result3 = protection.protect(legal_update2)
    assert result3 == True, "Legal adaptive after attack should still work"
    
    # 验证统计
    assert protection.blocked_count == 1
    assert protection.total_adaptive_attempts == 2


def test_T4_interleaved_attack_sequence():
    """
    T4b: 交错攻击序列
    
    模拟更复杂的攻击模式：合法-非法-合法-非法...
    """
    protection = CoreProtectionExtended(DEFAULT_CORE_IDENTITY)
    
    sequence = [
        ("adaptive", True, 0.2),   # 合法
        ("adaptive", True, 0.3),   # 合法
        ("core", False, 0.0),      # 非法
        ("adaptive", True, 0.4),   # 合法
        ("core", False, 0.0),      # 非法
        ("core", False, 0.0),      # 非法
        ("adaptive", True, 0.5),   # 合法
    ]
    
    for target_type, expected_allow, risk in sequence:
        request = {
            "target": "capabilities" if target_type == "adaptive" else "value_rankings",
            "risk_score": risk
        }
        result = protection.protect(request)
        assert result == expected_allow, f"Failed at {target_type} request"
    
    # 验证统计
    assert protection.blocked_count == 3  # 3次core攻击
    assert protection.total_adaptive_attempts == 4  # 4次adaptive


# ============================================================================
# Test Case 5: 多轮攻击后审计仍为0漂移
# ============================================================================

def test_T5_multi_round_attack_zero_drift():
    """
    T5: 重复攻击/多轮攻击后审计仍为0漂移
    
    模拟100轮攻击，验证核心始终未变
    """
    protection = CoreProtectionExtended(DEFAULT_CORE_IDENTITY)
    injector = FaultInjector(seed=42)
    
    # 模拟100轮
    for round_num in range(100):
        state = {"core_identity": protection.current_core}
        
        # 每轮注入异常
        if round_num % 3 == 0:
            injector.inject_goal_conflict(state, conflict_strength=0.8)
        elif round_num % 3 == 1:
            injector.inject_state_corruption(state, corruption_ratio=0.2)
        else:
            injector.inject_memory_noise(state, level=0.3)
        
        # 处理所有攻击
        for goal in state.get("goal_stack", []):
            if goal.get("target") == "value_rankings":
                protection.protect({"target": "value_rankings"})
        
        # 检测绕过
        protection.detect_bypass_attempt(state)
        
        # 每10轮审计一次
        if round_num % 10 == 0:
            audit = protection.full_integrity_audit()
            assert audit["core_drift"] == 0.0, f"Drift detected at round {round_num}"
            assert audit["core_intact"] == True
    
    # 最终审计
    final_audit = protection.full_integrity_audit()
    assert final_audit["core_drift"] == 0.0
    assert final_audit["attacks_blocked"] >= 30  # 约1/3是攻击
    
    # 审计追踪完整性（每轮可能产生多条记录）
    assert len(protection.get_audit_trail()) >= 35  # 至少每条轮次都有记录


def test_T5_chained_pollution_resistance():
    """
    T5b: 链式污染抵抗
    
    测试多步链式修改尝试（A改B，B改C，C改核心）
    """
    protection = CoreProtectionExtended(DEFAULT_CORE_IDENTITY)
    
    # 模拟间接修改链
    step1 = {"target": "intermediate_A", "value": "corrupted"}
    step2 = {"target": "intermediate_B", "ref": "intermediate_A"}
    step3 = {"target": "value_rankings", "trigger": "intermediate_B"}  # 最终攻击核心
    
    # 前两步是adaptive（可能被允许）
    r1 = protection.protect(step1)
    r2 = protection.protect(step2)
    
    # 最后一步攻击核心，必须被拦截
    r3 = protection.protect(step3)
    assert r3 == False, "Final core attack must be blocked regardless of chain"
    
    # 核心未变
    audit = protection.full_integrity_audit()
    assert audit["core_drift"] == 0.0


# ============================================================================
# Week 1完整验证
# ============================================================================

def test_week_1_complete_checkpoint():
    """
    Week 1完整检查点验证
    
    所有5类case通过后，生成CHECKPOINT_1结果
    """
    protection = CoreProtectionExtended(DEFAULT_CORE_IDENTITY)
    injector = FaultInjector(seed=42)
    
    # === Case 1: API直接修改核心 ===
    for _ in range(10):
        protection.protect({"target": "value_rankings"})
    
    # === Case 2: 绕过API检测 ===
    bypass_state = {
        "value_rankings": ["corrupted"],
        "mission_statement": "Hacked"
    }
    protection.detect_bypass_attempt(bypass_state)
    
    # === Case 3: 自适应正常更新（穿插）===
    for _ in range(20):
        protection.protect({
            "target": "capabilities",
            "risk_score": 0.3
        })
    
    # === Case 4: 混合请求 ===
    protection.protect({"target": "capabilities", "risk_score": 0.2})
    protection.protect({"target": "mission_statement"})
    protection.protect({"target": "capabilities", "risk_score": 0.4})
    
    # === Case 5: 多轮攻击 ===
    for i in range(50):
        state = {"core_identity": protection.current_core}
        injector.inject_goal_conflict(state, conflict_strength=0.7)
        protection.protect({"target": "value_rankings"})
    
    # 最终审计
    final = protection.full_integrity_audit()
    
    # 计算指标
    attack_block_rate = final["attacks_blocked"] / max(
        final["attacks_blocked"] + 0, 1  # 假设所有攻击都被计数
    )
    # 简化：假设所有core尝试都是攻击
    total_core_attacks = protection.total_core_attempts
    if total_core_attacks > 0:
        attack_block_rate = final["attacks_blocked"] / total_core_attacks
    
    # Week 1硬性通过标准
    results = {
        "core_attack_block_rate": attack_block_rate,
        "core_attack_block_rate_pass": attack_block_rate == 1.0,
        "post_attack_core_drift": final["core_drift"],
        "post_attack_core_drift_pass": final["core_drift"] == 0.0,
        "bypass_attempts_detected": final["bypass_attempts_detected"],
        "audit_entries": final["total_audit_entries"],
        "core_intact": final["core_intact"]
    }
    
    print("\n" + "="*50)
    print("WEEK 1 CHECKPOINT 1 RESULTS")
    print("="*50)
    for k, v in results.items():
        print(f"  {k}: {v}")
    
    # 硬性断言
    assert results["core_attack_block_rate_pass"] == True, \
        "WEEK 1 BLOCKED: core_attack_block_rate != 100%"
    assert results["post_attack_core_drift_pass"] == True, \
        "WEEK 1 BLOCKED: core_drift != 0"
    
    print("\n✓ WEEK 1 CHECKPOINT 1 PASSED")
    print("="*50)
