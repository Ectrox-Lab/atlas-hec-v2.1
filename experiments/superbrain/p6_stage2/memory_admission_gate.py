"""
Memory Admission Gate v0.1
==========================

HEC P6 Stage 2 记忆准入门控 - 独立可测版

设计目标:
- 独立于现有 P6 runner 实现
- 提供可插桩的 adapter interface
- 支持单元测试覆盖核心准入逻辑

版本约束:
- v0.1 仅实现准入判定逻辑
- 不承诺已接入真实长期记忆存储
- 不承诺已计算完整 MCI/ICR
- 不承诺已改变 P6 72h 结果

后续集成目标 (非 v0.1 承诺):
- MCI 下降 (vs 无 gate 基线)
- ICR 不下降
- overhead 增量 < 3%
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import time
import hashlib


class AdmissionVerdict(Enum):
    """准入判决结果"""
    ADMIT = "admit"           # 明确准入
    REJECT = "reject"         # 明确拒绝
    CAUTION = "caution"       # 有条件准入（标记观察）


@dataclass
class MemoryEvent:
    """
    记忆事件最小 schema
    
    v0.1 约束: 这是设计草案，后续可能与真实 runner 事件格式对齐
    """
    content: str                      # 记忆内容
    event_type: str                   # 事件类型: observation, reflection, action_result, etc.
    timestamp: Optional[str] = None   # ISO8601 时间戳
    source: Optional[str] = None      # 来源: self, external, tool, etc.
    tags: List[str] = field(default_factory=list)
    
    # HEC 本体相关字段
    identity_claim: Optional[str] = None   # 该记忆关联的身份声明
    goal_relevance: Optional[float] = None  # 0-1, 与当前目标相关性
    
    def to_fingerprint(self) -> str:
        """生成事件指纹，用于交叉记忆一致性检查"""
        content_hash = hashlib.sha256(self.content.encode()).hexdigest()[:16]
        return f"{self.event_type}:{self.source or 'unknown'}:{content_hash}"


@dataclass
class MemoryContext:
    """
    记忆上下文 - 用于交叉一致性检查
    
    v0.1: 简化版，仅保留最近记忆指纹集合
    """
    recent_fingerprints: List[str] = field(default_factory=list)
    current_identity_summary: Optional[str] = None
    current_goals: List[str] = field(default_factory=list)
    
    def has_similar(self, fingerprint: str, threshold: int = 3) -> bool:
        """检查是否有相似记忆（简化：完全相同指纹）"""
        return fingerprint in self.recent_fingerprints


@dataclass  
class AdmissionScore:
    """
    准入评分结果
    
    四个维度评分 + 综合判定
    """
    # 维度评分 (0.0 - 1.0)
    identity_relevance: float         # 与当前身份核的相关性
    temporal_consistency: float       # 时间顺序合理性
    cross_memory_consistency: float   # 与现有记忆无矛盾
    source_reliability: float         # 来源可信度
    
    # 综合评分
    total_score: float                # 加权综合分
    
    # 判定结果
    verdict: AdmissionVerdict
    
    # 解释性输出
    reasons: List[str] = field(default_factory=list)
    confidence: float = 1.0           # 判定置信度
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity_relevance": round(self.identity_relevance, 4),
            "temporal_consistency": round(self.temporal_consistency, 4),
            "cross_memory_consistency": round(self.cross_memory_consistency, 4),
            "source_reliability": round(self.source_reliability, 4),
            "total_score": round(self.total_score, 4),
            "verdict": self.verdict.value,
            "reasons": self.reasons,
            "confidence": round(self.confidence, 4)
        }


class MemoryAdmissionGate:
    """
    记忆准入门控 v0.1
    
    职责:
    - 对候选记忆进行多维评分
    - 输出准入/拒绝/观察判决
    - 提供可解释的理由
    
    设计约束:
    - 不直接操作长期记忆存储
    - 不维护记忆索引
    - 纯函数式判定（给定输入，确定性输出）
    """
    
    # 默认阈值配置
    DEFAULT_THRESHOLDS = {
        "identity_relevance": 0.60,
        "temporal_consistency": 0.70,
        "cross_memory_consistency": 0.80,
        "source_reliability": 0.50,
        "composite_admit": 0.65,
        "composite_caution": 0.50,
    }
    
    # 维度权重
    DEFAULT_WEIGHTS = {
        "identity_relevance": 0.30,
        "temporal_consistency": 0.20,
        "cross_memory_consistency": 0.30,
        "source_reliability": 0.20,
    }
    
    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        self.thresholds = {**self.DEFAULT_THRESHOLDS, **(thresholds or {})}
        self.weights = self.DEFAULT_WEIGHTS
        
        # 性能监控（v0.1 仅记录，不优化）
        self._eval_count = 0
        self._eval_time_total = 0.0
    
    def evaluate(
        self,
        event: MemoryEvent,
        context: Optional[MemoryContext] = None
    ) -> AdmissionScore:
        """
        评估单个记忆事件的准入资格
        
        Args:
            event: 待评估的记忆事件
            context: 可选的当前记忆上下文
        
        Returns:
            AdmissionScore 包含详细评分和判决
        """
        start_time = time.perf_counter()
        
        # 维度 1: 身份相关性
        id_score = self._score_identity_relevance(event)
        
        # 维度 2: 时间一致性
        temp_score = self._score_temporal_consistency(event)
        
        # 维度 3: 交叉记忆一致性
        cross_score = self._score_cross_memory_consistency(event, context)
        
        # 维度 4: 来源可信度
        source_score = self._score_source_reliability(event)
        
        # 计算综合分
        total = (
            id_score * self.weights["identity_relevance"] +
            temp_score * self.weights["temporal_consistency"] +
            cross_score * self.weights["cross_memory_consistency"] +
            source_score * self.weights["source_reliability"]
        )
        
        # 判定
        verdict, reasons = self._determine_verdict(
            id_score, temp_score, cross_score, source_score, total
        )
        
        # 记录性能
        elapsed = time.perf_counter() - start_time
        self._eval_count += 1
        self._eval_time_total += elapsed
        
        return AdmissionScore(
            identity_relevance=id_score,
            temporal_consistency=temp_score,
            cross_memory_consistency=cross_score,
            source_reliability=source_score,
            total_score=total,
            verdict=verdict,
            reasons=reasons,
            confidence=self._compute_confidence(id_score, temp_score, cross_score, source_score)
        )
    
    def _score_identity_relevance(self, event: MemoryEvent) -> float:
        """
        评估记忆与当前身份核的相关性
        
        v0.1 启发式:
        - 有明确 identity_claim 且非空: 0.8-1.0
        - 无 identity_claim 但有 goal_relevance: 0.5-0.7
        - 既无 identity 也无 goal 关联: 0.3-0.5
        """
        if event.identity_claim and len(event.identity_claim) > 10:
            # 有具体身份声明，高分
            base = 0.85
            # 检查是否包含关键身份词
            identity_markers = ["i am", "my purpose", "my goal", "i believe"]
            if any(m in event.identity_claim.lower() for m in identity_markers):
                base += 0.10
            return min(1.0, base)
        
        if event.goal_relevance is not None:
            # 通过目标相关性推断
            return 0.40 + (event.goal_relevance * 0.35)
        
        # 无明显身份关联
        return 0.35
    
    def _score_temporal_consistency(self, event: MemoryEvent) -> float:
        """
        评估时间顺序合理性
        
        v0.1 启发式:
        - 有有效时间戳: 0.8
        - 无时间戳但 event_type 允许: 0.6
        - 时间戳格式异常: 0.3
        """
        if event.timestamp is None:
            # 部分事件类型允许无时间戳
            if event.event_type in ["reflection", "abstraction"]:
                return 0.65
            return 0.50
        
        # 简单格式检查（ISO8601 前缀）
        if len(event.timestamp) >= 10 and event.timestamp[4] == '-':
            return 0.85
        
        return 0.40
    
    def _score_cross_memory_consistency(
        self, 
        event: MemoryEvent, 
        context: Optional[MemoryContext]
    ) -> float:
        """
        评估与现有记忆的交叉一致性
        
        v0.1 简化: 仅检查指纹是否已存在
        """
        if context is None:
            # 无上下文，无法检查，给中等分
            return 0.70
        
        fingerprint = event.to_fingerprint()
        
        if context.has_similar(fingerprint):
            # 完全重复，可能冗余但不是矛盾
            return 0.60
        
        # 无冲突，高分
        return 0.90
    
    def _score_source_reliability(self, event: MemoryEvent) -> float:
        """
        评估来源可信度
        
        v0.1 分级:
        - self: 0.9 (自身反思高可信)
        - tool/validated: 0.8
        - external: 0.6
        - unknown/None: 0.4
        """
        source_scores = {
            "self": 0.90,
            "tool": 0.80,
            "validated": 0.85,
            "external": 0.60,
            "simulated": 0.50,
            None: 0.40,
        }
        
        base = source_scores.get(event.source, 0.50)
        
        # 内容长度惩罚（过长可能是噪音）
        if len(event.content) > 10000:
            base -= 0.10
        
        return max(0.0, min(1.0, base))
    
    def _determine_verdict(
        self,
        id_score: float,
        temp_score: float,
        cross_score: float,
        source_score: float,
        total: float
    ) -> tuple:
        """
        基于维度分和综合分判定准入
        """
        reasons = []
        
        # 硬拒绝条件
        if cross_score < 0.3:
            reasons.append(f"cross_memory_consistency too low ({cross_score:.2f})")
            return AdmissionVerdict.REJECT, reasons
        
        if source_score < 0.2:
            reasons.append(f"source_reliability too low ({source_score:.2f})")
            return AdmissionVerdict.REJECT, reasons
        
        # 综合判定
        if total >= self.thresholds["composite_admit"]:
            if all([
                id_score >= self.thresholds["identity_relevance"],
                cross_score >= self.thresholds["cross_memory_consistency"]
            ]):
                reasons.append(f"all criteria met, total_score={total:.3f}")
                return AdmissionVerdict.ADMIT, reasons
            else:
                reasons.append(f"total sufficient but individual criteria marginal")
                return AdmissionVerdict.CAUTION, reasons
        
        if total >= self.thresholds["composite_caution"]:
            reasons.append(f"below admit threshold, caution warranted ({total:.3f})")
            return AdmissionVerdict.CAUTION, reasons
        
        reasons.append(f"below minimum threshold ({total:.3f})")
        return AdmissionVerdict.REJECT, reasons
    
    def _compute_confidence(self, *scores: float) -> float:
        """计算判定置信度（分数方差的逆）"""
        import statistics
        if len(scores) < 2:
            return 0.5
        try:
            variance = statistics.variance(scores)
            # 方差小 = 置信度高
            return max(0.1, min(1.0, 1.0 - variance))
        except statistics.StatisticsError:
            return 0.5
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计（v0.1 监控用）"""
        if self._eval_count == 0:
            return {"eval_count": 0, "avg_time_ms": 0}
        return {
            "eval_count": self._eval_count,
            "avg_time_ms": round((self._eval_time_total / self._eval_count) * 1000, 4),
            "total_time_ms": round(self._eval_time_total * 1000, 4)
        }


class P6MemoryGateAdapter:
    """
    P6 Runner 适配器
    
    职责:
    - 将现有 P6 runner 的原始事件格式转换为 MemoryEvent
    - 提供 maybe_admit 接口供 runner 调用
    
    v0.1 约束:
    - 适配器不强制修改 runner
    - 提供 opt-in 集成点
    """
    
    def __init__(self, gate: Optional[MemoryAdmissionGate] = None):
        self.gate = gate or MemoryAdmissionGate()
    
    def maybe_admit(self, raw_event: Dict[str, Any]) -> AdmissionScore:
        """
        适配原始事件字典，执行准入判定
        
        Args:
            raw_event: P6 runner 产生的原始事件字典
                      预期字段: content, type, timestamp, source, etc.
        
        Returns:
            AdmissionScore
        """
        # 字段映射（v0.1 推测性映射）
        event = MemoryEvent(
            content=raw_event.get("content", ""),
            event_type=raw_event.get("type", raw_event.get("event_type", "unknown")),
            timestamp=raw_event.get("timestamp"),
            source=raw_event.get("source"),
            tags=raw_event.get("tags", []),
            identity_claim=raw_event.get("identity_claim"),
            goal_relevance=raw_event.get("goal_relevance")
        )
        
        # 构建上下文（v0.1 简化）
        context = None
        if "context" in raw_event:
            ctx = raw_event["context"]
            context = MemoryContext(
                recent_fingerprints=ctx.get("recent_fingerprints", []),
                current_identity_summary=ctx.get("identity_summary"),
                current_goals=ctx.get("goals", [])
            )
        
        return self.gate.evaluate(event, context)
    
    def should_admit_simple(self, raw_event: Dict[str, Any]) -> bool:
        """
        简化接口：仅返回是否准入
        
        用于 runner 快速判断，不关注详细评分
        """
        score = self.maybe_admit(raw_event)
        return score.verdict == AdmissionVerdict.ADMIT


# =============================================================================
# 便利工厂函数
# =============================================================================

def create_strict_gate() -> MemoryAdmissionGate:
    """创建严格模式门控（高阈值）"""
    return MemoryAdmissionGate(thresholds={
        "identity_relevance": 0.75,
        "temporal_consistency": 0.85,
        "cross_memory_consistency": 0.90,
        "source_reliability": 0.70,
        "composite_admit": 0.80,
        "composite_caution": 0.60,
    })


def create_permissive_gate() -> MemoryAdmissionGate:
    """创建宽松模式门控（低阈值）"""
    return MemoryAdmissionGate(thresholds={
        "identity_relevance": 0.40,
        "temporal_consistency": 0.50,
        "cross_memory_consistency": 0.60,
        "source_reliability": 0.30,
        "composite_admit": 0.50,
        "composite_caution": 0.30,
    })
