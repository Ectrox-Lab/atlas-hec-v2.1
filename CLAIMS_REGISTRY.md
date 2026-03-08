# CLAIMS_REGISTRY.md - 声明注册表

> 所有重要声明的证据状态追踪

---

## ✅ CONFIRMED (已验证)

| Claim | 证据 | 状态 | 备注 |
|-------|------|------|------|
| 6小时零崩溃燃烧测试 | `logs/HETERO_BURN_6HOUR.log` | ✅ CONFIRMED | 2,100,850步，97.3Hz |
| C组奖励增长13.8倍 | `logs/HETERO_BURN_6HOUR.log` | ✅ CONFIRMED | 1,800→24,867 |
| 异构CPU+GPU架构有效 | 源代码+日志 | ✅ CONFIRMED | Rust+CUDA FFI工作 |
| STDP学习机制实现 | `source/hetero_bridge/kernels.cu` | ✅ CONFIRMED | CUDA内核实现 |
| DigitalMetabolism模块存在 | `source/src/biomimetic/metabolism.rs` | ✅ CONFIRMED | 但为硬编码规则 |
| 内存无泄漏 | 日志+监控 | ✅ CONFIRMED | 386MiB恒定 |
| Izhikevich神经元实现 | 多处源代码 | ✅ CONFIRMED | 基础计算单元 |

---

## ⚠️ PARTIAL (部分验证/有条件)

| Claim | 证据 | 状态 | 备注 |
|-------|------|------|------|
| 神经发生(neurogenesis) | 代码存在，未完整验证 | ⚠️ PARTIAL | 需要更多epoch验证 |
| 自适应增长优势 | Fashion-MNIST实验 | ⚠️ PARTIAL | 需要与pre-allocation对照 |
| GridWorld学习 | 奖励增长确认 | ⚠️ PARTIAL | 但非泛化到MNIST |
| 多核CPU优化 | 代码存在 | ⚠️ PARTIAL | B组显示单核运行 |

---

## ❌ UNVERIFIED (未验证/无法验证)

| Claim | 原因 | 需要的证据 |
|-------|------|------------|
| Self-Model形成 | 无struct SelfState | 需要代码实现+运行日志 |
| 真正自我维持 | 硬编码规则非学习 | 需要学习曲线证明 |
| 时间连续身份 | 无autobiographical memory | 需要跨时间引用证据 |
| Persistent Identity | 无identity字段 | 需要SelfState实现 |
| Self-Report能力 | 无法回答"你是谁" | 需要自然语言接口 |
| 元认知 | 无"我在学习"表示 | 需要元认知模块 |

---

## ❌ FALSE/FAILED (已证伪/失败)

| Claim | 结果 | 失败原因 | 教训 |
|-------|------|----------|------|
| MNIST认证>95% | 10%准确率 | 单层感知机无法提取空间特征 | 需要卷积SNN架构 |
| 单核B组满载CPU | 0.2%占用 | Izhikevich计算太轻量 | 需要增加负载或并行化 |
| Self-Preservation学习 | 不存在 | 睡眠机制是硬编码(if>0.6) | 规则vs学习的区别 |

---

## 🔄 NEEDS REPRO (需要重新验证)

| Claim | 上次验证 | 需要重跑 | 原因 |
|-------|----------|----------|------|
| Growth Trigger阈值 | 未完整记录 | 需要系统化实验 | 参数敏感性未知 |
| Fashion-MNIST 85% | 声称存在 | 需要完整日志 | 证据片段化 |
| Adaptive vs Preallocation | 未对照实验 | 需要A/B测试 | 缺乏对照组 |
| 72小时长期运行 | 未进行 | 需要资源 | 只跑到6小时 |

---

## 📝 验证标准定义

- **CONFIRMED**: 有可复现的日志+代码实现+可运行
- **PARTIAL**: 有代码实现，但缺乏完整验证或条件受限
- **UNVERIFIED**: 无代码实现或无法验证
- **FALSE**: 已测试并失败
- **NEEDS REPRO**: 需要重新运行以确认

---

## 🔍 关键区分

### 已实现 vs 声称的区别

| 声称 | 实际情况 | 差距 |
|------|----------|------|
| "半只脚跨过AGI门槛" | 复杂动态基质，无self-model | 缺internal reference |
| "自我维持" | DigitalMetabolism硬编码规则 | 规则vs学习的区别 |
| "涌现学习" | STDP有效(13.8x增长) | 但无元认知"我在学习" |
| "异构智能" | CPU+GPU协同有效 | 但未达到Agent门槛 |

---

*最后更新: 2026-03-09 - 遵循BRUTAL HONESTY原则*
