# CLAIMS_REGISTRY.md - 声明注册表

> 所有重要声明的证据状态追踪  
> **Repo Root**: `/home/admin/atlas-hec-v2.1-repo`  
> **验证命令**: 使用`grep -rn`搜索代码，使用`ls -la`检查日志

---

## ✅ CONFIRMED (已验证)

| Claim | 代码证据 | 运行时证据 | 复现命令 | Git Commit | 最后验证 |
|-------|----------|------------|----------|------------|----------|
| 6小时零崩溃燃烧测试 | N/A | `logs/HETERO_BURN_6HOUR.log` L1-L600 | `timeout 7h ./target/release/atlas_hec_burn --mode hetero` | `0786074` | 2026-03-09 |
| C组奖励增长13.8倍 | N/A | `logs/HETERO_BURN_6HOUR.log` L580-L600 (Reward: 24798.88) | 同上 | `0786074` | 2026-03-09 |
| 异构CPU+GPU架构有效 | `source/src/main_5k.rs` L20-L50 | 日志中CPU+GPU同时使用 | 同上 | `0786074` | 2026-03-09 |
| STDP学习机制实现 | `source/hetero_bridge/kernels.cu` L1-L150 | N/A (编译产物) | `make -C source/hetero_bridge` | `0786074` | 2026-03-09 |
| DigitalMetabolism模块存在 | `source/src/biomimetic/metabolism.rs` L15-L30 | 日志中Energy字段 | 运行任何burn test | `0786074` | 2026-03-09 |
| 内存无泄漏 | N/A | 日志中GPU内存386MiB恒定 | `nvidia-smi`监控 | `0786074` | 2026-03-09 |
| Izhikevich神经元实现 | `source/src/lib.rs` L1-L50 (重导出) | N/A | `cargo build` | `0786074` | 2026-03-09 |

### 详细证据链

**6小时燃烧测试确认:**
```bash
# 验证命令
grep "Steps:" logs/HETERO_BURN_6HOUR.log | tail -1
# 输出: [5h59m] Steps: 2094969, Energy: 0.41, Reward: 24798.88

# 验证零崩溃
grep -i "crash\|error\|panic" logs/HETERO_BURN_6HOUR.log
# 输出: (无)

# 验证完成标记
grep "HETERO COMPLETE" logs/HETERO_BURN_6HOUR.log
# 输出: ✅ HETERO COMPLETE: 2100850 steps
```

---

## ⚠️ PARTIAL (部分验证/有条件)

| Claim | 代码证据 | 限制条件 | 需要补充 |
|-------|----------|----------|----------|
| 神经发生(neurogenesis) | `source/src/superbrain/mod.rs` (如存在) | 未完整运行足够epoch | 需要10+ epoch日志 |
| 自适应增长优势 | 代码存在但未对照 | 缺乏pre-allocation对照组 | 需要A/B测试 |
| GridWorld学习 | `source/src/gridworld/mod.rs` L1-L200 | 奖励增长确认但非泛化 | 需要移植到MNIST验证 |
| 多核CPU优化 | `source/src/bin/control_burn_multicore.rs` | B组显示单核运行(0.2%) | 需要重跑D组验证 |

---

## ❌ UNVERIFIED (未验证/无法验证)

| Claim | 搜索命令 | 结果 | 需要实现 |
|-------|----------|------|----------|
| Self-Model形成 | `grep -rn "struct SelfState\|self_model" source/src/` | 未找到 | `struct SelfState { ... }` |
| 真正自我维持 | `grep -rn "learned.*preservation\|adaptive.*survival" source/src/` | 未找到 | 学习算法替代硬编码规则 |
| 时间连续身份 | `grep -rn "yesterday\|persistent.*identity\|autobiographical" source/src/` | 未找到 | `AutobiographicalMemory`模块 |
| Persistent Identity | `grep -rn "identity_token\|this_is_me" source/src/` | 未找到 | identity字段 |
| Self-Report能力 | `grep -rn "who_am_i\|self_report\|answer.*who" source/src/` | 未找到 | `SelfReportInterface` trait |
| 元认知 | `grep -rn "meta_cognitive\|i_am_learning\|self_aware" source/src/` | 未找到 | 元认知监控模块 |

---

## ❌ FALSE/FAILED (已证伪/失败)

| Claim | 结果 | 失败原因 | 证据位置 | 教训 |
|-------|------|----------|----------|------|
| MNIST认证>95% | 10%准确率 | 单层感知机无法提取空间特征 | `logs/mnist_certification_20260309_010727.log` | 需要卷积SNN架构 |
| 单核B组满载CPU | 0.2%占用 | Izhikevich计算太轻量 | `logs/CONTROL_BURN_6HOUR.log` | 需要增加负载或并行化 |
| Self-Preservation学习 | 不存在 | 睡眠机制是硬编码 | `source/src/biomimetic/metabolism.rs` L88: `if self.adenosine_level > 0.6` | 规则vs学习的区别 |

---

## 🔄 NEEDS REPRO (需要重新验证)

| Claim | 上次验证 | 需要重跑 | 重跑命令 | 预期输出 |
|-------|----------|----------|----------|----------|
| Growth Trigger阈值 | 未完整记录 | 系统化实验 | `cargo run --bin atlas_superbrain -- --growth-enabled 2>&1 | tee logs/growth-test-$(date +%s).log` | neuron count随epoch增加 |
| Fashion-MNIST 85% | 声称存在 | 完整日志 | 需要确认数据集路径和运行命令 | 准确率>85% |
| Adaptive vs Preallocation | 未对照实验 | A/B测试 | 需要设计对照实验 | 对比报告 |
| 72小时长期运行 | 未进行(只到6h) | 资源允许时 | `timeout 73h ./target/release/atlas_hec_burn --duration 259200` | 零崩溃日志 |

---

## 📝 证据粒度标准

### Code Evidence 格式
```
file: source/src/path/to/file.rs
line: L15-L30
struct/function: StructName::method_name
grep: grep -n "pattern" source/src/file.rs
```

### Runtime Evidence 格式
```
file: logs/EXPERIMENT_NAME_YYYYMMDD.log
line: L120-L150
key metric: "Steps: X, Reward: Y"
command: grep "pattern" logs/file.log
```

### Repro Command 格式
```
环境: REPO_ROOT=/home/admin/atlas-hec-v2.1-repo
cd: $REPO_ROOT/source
build: cargo build --release --bin BIN_NAME
run: ./target/release/BIN_NAME --args
verify: grep "expected_output" logs/output.log
```

---

## 🔍 关键区分

### 已实现 vs 声称的区别

| 声称 | 实际情况 | 差距 | 验证命令 |
|------|----------|------|----------|
| "半只脚跨过AGI门槛" | 复杂动态基质，无self-model | 缺internal reference | `grep -r "this_is_me" source/src/` |
| "自我维持" | DigitalMetabolism硬编码规则 | 规则vs学习的区别 | `cat source/src/biomimetic/metabolism.rs | grep -A3 "needs_rem"` |
| "涌现学习" | STDP有效(13.8x增长) | 但无元认知"我在学习" | `grep -r "meta\|aware" source/src/` |
| "异构智能" | CPU+GPU协同有效 | 但未达到Agent门槛 | `grep -r "SelfState\|Agent" source/src/` |

---

*最后更新: 2026-03-09 - 遵循BRUTAL HONESTY原则*  
*所有路径相对于repo根目录，所有grep命令可立即执行验证*
