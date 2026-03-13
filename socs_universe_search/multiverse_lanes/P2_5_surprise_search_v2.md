# P2.5 - Surprise Search Lane v2.0 (强化版)

## 状态
**当前**: 运行中，已优化  
**上一轮结果**: 发现3个候选，全部SEED_SPIKE，已被Intake Pipeline正确过滤  
**当前策略**: 强化稳健性门槛，积累负面知识

---

## 核心更新

### 1. SEED_SPIKE 正式定义

```python
SEED_SPIKE = {
    "definition": "单次或少量seeds下出现异常高分，但跨seeds无法稳定复现的候选",
    "detection": "原始CWCI - 复现min CWCI > 0.10",
    "severity": {
        "critical": "drop > 0.15",
        "high": "drop > 0.10",
        "medium": "drop > 0.05",
        "low": "drop <= 0.05"
    },
    "action": "立即标记，拒绝进入EMERGENT tier，但保留在阿卡西中作为负面知识"
}
```

### 2. 更新后的 Surprise Triggers (v2.0)

旧标准 (导致假阳性):
- CWCI > 0.65
- 单次扫描出现

**新标准 (稳健性优先)**:
```python
SURPRISE_TRIGGERS_V2 = {
    "robustness": {
        "description": "跨seeds稳定性",
        "criteria": "min CWCI > 0.75, CV < 10%, 3+ seeds测试"
    },
    "stress_coverage": {
        "description": "多场景覆盖",
        "criteria": "至少在3种stress场景下CWCI > 0.70"
    },
    "novelty": {
        "description": "参数空间新颖性", 
        "criteria": "不在已知SEED_SPIKE高风险区域"
    },
    "resilience": {
        "description": "规模稳健性",
        "criteria": "5x规模下CWCI保留>80% (Intake Step 3预筛)"
    }
}
```

### 3. 负面知识驱动扫描

利用阿卡西v2的SEED_SPIKE注册表主动规避风险：

```python
def calculate_seed_spike_risk(dna: Dict) -> float:
    """
    基于历史SEED_SPIKE查询新DNA的风险
    """
    risk = 0.0
    
    # 已知脆弱组合
    if dna["local_autonomy"] > 0.8 and dna["hierarchy_depth"] < 2:
        risk += 0.4  # high_autonomy_low_hierarchy
    if dna["broadcast_sparsity"] < 0.06:
        risk += 0.3  # ultra_sparse_broadcast
        
    # 与已记录SEED_SPIKE的DNA相似度
    for entry in AKASHIC.seed_spike_registry:
        similarity = dna_similarity(dna, entry["dna_features"])
        if similarity > 0.8:
            risk += 0.3
            
    return min(1.0, risk)

# 扫描时优先探索低风险区域
def generate_next_batch(n: int) -> List[StructureDNA]:
    candidates = []
    while len(candidates) < n:
        dna = generate_random_dna()
        risk = calculate_seed_spike_risk(dna)
        if random.random() > risk:  # 风险越高，被接受概率越低
            candidates.append(dna)
    return candidates
```

---

## 资源分配 (维持)

| 组件 | 资源 | 说明 |
|------|------|------|
| 多元宇宙扫描 | 10% | 128 universes |
| Intake验证 | 3% | 4步Pipeline |
| 阿卡西更新 | 2% | 正负知识记录 |
| **总计** | **15%** | 不超过上限 |

---

## 产出物更新

### 新增
- `seed_spike_registry.jsonl` - SEED_SPIKE正式记录
- `fragile_combinations.json` - 需规避的DNA组合
- `robustness_digest.json` - 稳健性知识摘要

### 原有 (继续)
- `surprise_candidates.jsonl` - 通过Intake的候选
- `structure_signatures.json` - 结构签名
- `akashic_digest.json` - 跨宇宙摘要

---

## 关键指标

| 指标 | 目标 | 上一轮 | 状态 |
|------|------|--------|------|
| 扫描宇宙数/轮 | 128 | 128 | ✅ |
| SEED_SPIKE识别率 | >90% | 100% (3/3) | ✅ |
| 误报进入EMERGENT | 0 | 0 | ✅ |
| 负面知识条目 | 增长 | +3 | ✅ |

---

## 与主线关系 (不变)

```
P2.5 (Surprise Search) 
    ↓ 产出: 通过4步Intake的稳健候选
    ↓ 进入: P1 CHALLENGER验证
    ↓ 可能晋升: PRIMARY (如果超越OctopusLike)
    
P2.5 (负面知识)
    ↓ 产出: SEED_SPIKE注册表
    ↓ 用途: 优化扫描策略，降低未来假阳性
    ↓ 不干扰: 主线判断标准
```

---

## 一句话总结

> P2.5 surprise search is operational, but the first three emergent candidates were non-robust seed spikes and were correctly rejected by intake.

**惊喜搜索继续运行，但已从"追求高分"转向"追求稳健性"，并利用负面知识优化扫描效率。**
