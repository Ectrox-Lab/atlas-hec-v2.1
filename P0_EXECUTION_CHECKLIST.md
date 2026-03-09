# P0 执行检查清单

## 阶段1：运行5-Seed实验

```bash
# 启动实验（预计15小时）
nohup ./run_cross_seed_experiments.sh 5 7000 > cross_seed_run.log 2>&1 &

# 监控进度
tail -f cross_seed_run.log
```

检查点：
- [ ] 5个CSV文件生成完成
- [ ] 每个CSV包含~70行（Gen 100-7000）
- [ ] 所有seed都有extinction事件（extinct_count > 0）

## 阶段2：数据分析

```bash
# 运行5-seed分析
python3 analyze_5seed_results.py \
    --csv-files /home/admin/zeroclaw-labs/v18_1_experiments/cross_seed_*/evolution.csv \
    --output model_fit_results/P0_5seed_analysis.json
```

检查点：
- [ ] 所有5个seed都被成功加载
- [ ] 每个seed都有I_crit估计
- [ ] I_crit CV < 10%

## 阶段3：生成最终报告

填写 `P0_FINAL_REPORT_TEMPLATE.md`：

必须完成的部分：
- [ ] 第一部分：I_crit per seed表格
- [ ] 第一部分：统计摘要（Mean, Std, CV）
- [ ] 第二部分：Hazard ratio计算
- [ ] 第三部分：生存曲线分组数据
- [ ] 第四部分：三维度评分
- [ ] 第四部分：最终评级（A/B/C/D）

## 阶段4：结果判定

### 评级标准

**A级 (80-100)**:
- I_crit CV < 5%
- Hazard ratio > 5x
- 生存曲线明显分离

**B级 (60-79)**:
- I_crit CV < 10%
- Hazard ratio > 2x
- 生存曲线有分离趋势

**C级 (40-59)**:
- I_crit在合理范围[0.45, 0.60]
- Hazard ratio > 1.5x
- 部分支持危险区假说

**D级 (<40)**:
- 不满足上述任何条件

### 下一步行动

| 评级 | 行动 | 时间 |
|-----|------|-----|
| A | 进入P1 (Hazard Model精细化) | 2周 |
| B | 补充3个seed或调整模型 | 1周 |
| C | 重新审视CDI定义或考虑多临界区 | 待定 |
| D | 返回问题定义阶段 | 待定 |

## 当前状态

- [x] P0 Hazard Rate Protocol v2.0 框架完成
- [x] 2-seed初步验证（I_crit = 0.519 ± 0.0002）
- [ ] 5-seed实验运行中
- [ ] 完整分析报告待生成

## 关键时间节点

| 日期 | 事件 |
|-----|------|
| 2026-03-09 | P0 v2.0框架完成，2-seed验证 |
| T+15小时 | 5-seed实验完成（预计） |
| T+16小时 | 完整分析报告 |
| T+1周 | P1启动（如果评级A或B） |

