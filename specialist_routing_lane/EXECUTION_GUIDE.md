# P2.6 执行指南
## 给执行器的直接指令

---

## 一键启动命令

```bash
cd /home/admin/atlas-hec-v2.1-repo/specialist_routing_lane

# ========== Phase 1: 提取指纹 (Day 1-2) ==========
python scripts/extract_structure_fingerprint.py \
  --input ../experiments/outputs/ \
  --output data/candidate_fingerprints/fingerprint_v1.jsonl

# 预期输出: fingerprint_v1.jsonl (每个候选一行JSON)

# ========== Phase 2: 聚类 (Day 3-4) ==========
python scripts/build_structure_index.py \
  --input data/candidate_fingerprints/fingerprint_v1.jsonl \
  --config configs/clustering_config.yaml \
  --output data/clustered_regions/

# 预期输出: regions_v1.json, embedding_v1.npy, clusters_v1.npy

# ========== Phase 3: 验证 (Day 5-6) ==========
python scripts/validate_clusters.py \
  --clusters data/clustered_regions/ \
  --output outputs/gate_sr1_validation_report.md

# 预期输出: gate_sr1_validation_report.md (Pass/Fail 判定)

# ========== Phase 4: 阿卡西集成 (Day 7) ==========
python scripts/write_akashic_region_summary.py \
  --regions data/clustered_regions/ \
  --output data/akashic_region_map/

# 预期输出: region_summary_v1.md, region_mapping_v1.json
```

---

## 验收标准速查

| Gate | 指标 | 阈值 | 命令检查 |
|------|------|------|----------|
| SR1 | Silhouette Score | > 0.5 | 见 validation_report |
| SR1 | Seed-spike Precision | > 80% | 见 validation_report |
| SR1 | Mainline in stable | 是 | 见 region_summary |
| SR1 | Davies-Bouldin | < 1.0 | 见 validation_report |

---

## 文件产出清单

### Gate SR1 必须产出

```
specialist_routing_lane/
├── data/candidate_fingerprints/fingerprint_v1.jsonl
├── data/clustered_regions/regions_v1.json
├── data/clustered_regions/embedding_v1.npy
├── data/akashic_region_map/region_summary_v1.md
└── outputs/gate_sr1_validation_report.md
```

### 成功产出

```
specialist_routing_lane/
├── outputs/region_report.md
├── outputs/specialist_map.json
└── proposals/promotion_candidates.md (自动更新)
```

---

## 常见问题处理

### 指纹提取失败

```bash
# 检查输入数据格式
head -1 ../experiments/outputs/*.json | python -m json.tool

# 使用特定模式
python scripts/extract_structure_fingerprint.py \
  --input ../experiments/outputs/ \
  --pattern "*gate*.json" \
  --output data/candidate_fingerprints/fingerprint_v1.jsonl
```

### 聚类数过少

```bash
# 调整聚类参数
# 编辑 configs/clustering_config.yaml:
#   hdbscan.min_cluster_size: 3  (原来是 5)
#   hdbscan.min_samples: 2       (原来是 3)

# 或使用 KMeans 强制指定簇数
#   clustering.primary_algorithm: "kmeans"
```

### 验证失败

```bash
# 查看详细指标
python scripts/validate_clusters.py \
  --clusters data/clustered_regions/ \
  --json

# 重新聚类后再次验证
```

---

## 给执行器的检查清单

### 开始之前

- [ ] 确认主线 OctopusLike R3 数据已生成
- [ ] 确认 OQS Gate 2 数据已生成
- [ ] 确认 `../experiments/outputs/` 目录存在且有数据

### Phase 1 完成后

- [ ] `fingerprint_v1.jsonl` 文件存在
- [ ] 文件大小 > 1KB (至少包含几个候选)
- [ ] 每行 JSON 格式正确

### Phase 2 完成后

- [ ] `regions_v1.json` 存在且非空
- [ ] `embedding_v1.npy` 存在
- [ ] 报告中发现 3+ 个簇

### Phase 3 完成后

- [ ] `gate_sr1_validation_report.md` 存在
- [ ] 报告中有明确的 Pass/Fail 结论
- [ ] 所有 4 个指标都有数值

### Phase 4 完成后

- [ ] `region_summary_v1.md` 存在
- [ ] 包含 OctopusLike 位置说明
- [ ] 包含 OQS 位置说明
- [ ] `promotion_candidates_v1.json` 存在

---

## 上报格式

完成后向上汇报请使用以下格式:

```markdown
## P2.6 Gate SR1 完成报告

**完成日期**: YYYY-MM-DD
**验收结果**: ✅ PASS / ❌ FAIL / 🟡 CONDITIONAL

### 关键指标
| 指标 | 值 | 阈值 | 状态 |
|------|-----|------|------|
| Silhouette Score | X.XX | > 0.5 | ✅/❌ |
| Seed-spike Precision | XX% | > 80% | ✅/❌ |
| Mainline Stability | 是/否 | 是 | ✅/❌ |
| Davies-Bouldin | X.XX | < 1.0 | ✅/❌ |

### 主要发现
1. OctopusLike 位于 [region_name]
2. OQS 位于 [region_name]
3. 发现 [N] 个 seed-spike 候选
4. 建议升级的候选: [list]

### 下一步
- [ ] 进入 Gate SR2 / [ ] 修复后重试 / [ ] 调整假设

### 文件位置
- 验证报告: `specialist_routing_lane/outputs/gate_sr1_validation_report.md`
- 区域摘要: `specialist_routing_lane/data/akashic_region_map/region_summary_v1.md`
```

---

## 联系信息

- **P2.6 Owner**: Atlas-HEC Research Team
- **主线同步**: 每周与 OctopusLike Mainline 对齐
- **紧急联系**: 见项目根目录 STATUS.md

---

**记住**: P2.6 的产出是帮助主线做决策，不是替代主线。所有结果都要反馈给主线团队。
