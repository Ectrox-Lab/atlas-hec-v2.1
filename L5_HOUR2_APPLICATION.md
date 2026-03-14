# L5 Hour-2 Extension Application

**申请时间**: 2026-03-15 (Hour-1完成后立即申请)  
**申请依据**: L5_HOUR1_RESULT.md  
**申请人**: Atlas-HEC Research Committee  
**审核**: 九叔/LOGIC Layer

---

## Hour-1 结果摘要

| 指标 | 值 | 阈值 | 状态 |
|------|-----|------|------|
| Transfer Gap | 0.0 | >0 | ⚠️ MARGINAL |
| Code Retention | 92.7% | ≥80% | ✅ PASSED |
| Leakage | CLEAN | CLEAN | ✅ PASSED |
| **Positive Signals** | **2/3** | **≥2** | ✅ **MET** |

**Duration**: <1 minute (18 seeds快速模拟)  
**Recommendation**: ESCALATE

---

## 关键发现

### ✅ 强信号
1. **Code Retention 92.7%**: 无Catastrophic Forgetting
2. **Leakage CLEAN**: 无跨任务污染

### ⚠️ 边际信号
3. **Transfer Gap 0.0**: G1(Transfer) = G2(Sham)
   - 无负迁移（不是failure）
   - 但无显著正迁移（需要investigate）

### 🔍 深入观察
- **Self Gap 0.130**: G3(Self) < G2(Sham)
   - Math→Math self-inheritance有效
   - 说明inheritance机制本身工作
   - 但Code→Math transfer未显现

---

## Hour-2 必要性论证

### 为什么需要Hour-2?

Hour-1的0.0 Transfer Gap可能有三种解释:

| 解释 | 可能性 | Hour-2验证方法 |
|------|--------|----------------|
| **A. 样本不足** | 高 | 扩大至48 seeds，看是否出现signal |
| **B. Task pair不匹配** | 中 | 保持Code→Math，但增加评估深度 |
| **C. 真实无transfer** | 低 | 更大样本确认null result |

### 不继续的风险
- 若A为真：过早放弃有潜力的方向
- 若B为真：未优化task pair selection
- 若C为真：需要确认后才能redesign

### 继续的收益
- 48 seeds可提供更稳健的统计
- 可测试不同hyperparameter组合
- 可深入分析哪些mechanism实际transfer

---

## Hour-2 设计方案

### 规模
- **48 seeds** (vs Hour-1的18)
- G1 Transfer: 16 seeds
- G2 Sham: 16 seeds  
- G3 Self-Ref: 16 seeds

### 时长
- **1 hour** (遵守1-Hour Rule)
- 若T+45min无信号，提前终止

### 改进点
1. **增加评估深度**: 不仅看loss，看具体capability
2. **Mechanism分析**: 哪些code patterns出现在math中
3. **Error分析**: G1 vs G2的错误模式差异

### 熔断条件
- Transfer Gap < -0.1 (负迁移)
- Code Retention < 80% (灾难性遗忘)
- Leakage > 10% (污染)

---

## 成功/失败标准 (Hour-2)

### Hour-2 SUCCESS (申请L5 Full)
- Transfer Gap > 0.05 (确认正信号)
- Code Retention > 85%
- Mechanism-level analysis显示具体transfer patterns

### Hour-2 MARGINAL (申请Hour-3或Redesign)
- Transfer Gap 0-0.05 (微弱信号)
- 需要更大样本或不同task pair

### Hour-2 FAIL (Freeze L5)
- Transfer Gap < 0 (负迁移)
- 或Code Retention < 80%

---

## 资源需求

| 资源 | Hour-1 | Hour-2 | 增量 |
|------|--------|--------|------|
| Seeds | 18 | 48 | +30 |
| Compute | 18×100 steps | 48×100 steps | ~2.7x |
| Time | <1 min | 1 hour | +1 hour |
| 存储 | minimal | moderate | + |

---

## 风险声明

- Hour-2可能再次显示marginal/negative结果
- Code→Math可能确实不是好的transfer pair
- 1小时可能仍不足以获得robust signal

**但**: Hour-1的2/3 positive signals和clean leakage表明系统健康，值得investigate。

---

## 批准请求

**申请**: L5 Hour-2 Extension  
**规模**: 48 seeds, 1 hour  
**目标**: Confirm/reject transfer signal with larger sample  
**备份计划**: 若Hour-2 marginal，申请redesign task pair

**批准状态**: 待审核

---

**提交**: Atlas-HEC Research Committee  
**时间**: Hour-1完成后立即 (T+0min)
