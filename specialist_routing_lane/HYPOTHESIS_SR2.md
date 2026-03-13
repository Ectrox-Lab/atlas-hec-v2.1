# HYPOTHESIS SR2: Routing Usefulness

## Metadata

| Field | Value |
|-------|-------|
| **Hypothesis ID** | SR2 |
| **Line** | P2.6 Specialist Routing Lane |
| **Phase** | Gate 2 - Routing Validation |
| **Status** | ⏸️ **PENDING** (Blocked on Gate SR1) |
| **Created** | 2026-03-12 |

---

## ⚠️ 重要说明

**本文件为占位符，尚未开始验证。**

Gate SR2 将在 **Gate SR1 通过之后** 正式启动。

---

## 目标预览

验证路由层是否真能给主线提供有效建议：

1. 能根据 stress 给出不同结构推荐
2. 推荐结果与真实 smoke/validation 方向一致
3. 能提前拦截一部分假阳性 candidate

## 通过标准预览

| Metric | Threshold |
|--------|-----------|
| Routing accuracy | > 75% |
| False positive reduction | > 30% |
| Stress-specific recall | > 70% |

---

## 启动条件

- [ ] Gate SR1 明确 PASS
- [ ] Akashic region map 已生成
- [ ] 主线需要 stress-specific 推荐

---

**请勿提前启动 SR2 验证。**
