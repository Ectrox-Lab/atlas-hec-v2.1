# G1: Immediate Action — Drift Pattern Check

**Time**: 2026-03-12 20:15 UTC  
**Owner**: Alex Chen  
**ETA**: 20 minutes

---

## Action (Do Now)

### Step 1: Pull Drift Data (5 min)
```python
# Get drift metrics from last 6h
drift_series = g1.get_metric("goal_deviation", window="6h", granularity="1h")
# [2.1%, 2.3%, 2.0%, 2.4%, 2.5%, 2.8%]
```

### Step 2: Calculate Trend (5 min)
```python
slope = calculate_trend(drift_series)
# slope > 0 → Accumulating
# slope ≈ 0 → Fluctuating
# slope < 0 → Decreasing
```

### Step 3: Check Correlations (5 min)
```python
# Drift vs specialist interactions
corr_specialist = correlation(drift_series, specialist_interaction_events)

# Drift vs memory growth
corr_memory = correlation(drift_series, memory_growth_series)

# Flag if strong correlation found
```

### Step 4: Classify (5 min)
```
If slope > 0.2%/hour → Accumulating (potential problem)
If -0.2% < slope < 0.2%/hour → Fluctuating (acceptable)
If slope < -0.2%/hour → Stable/Improving

If drift > 4% → Flag for escalation watch
If drift > 5% → Recommend halt for diagnosis
```

---

## Target Output (in 20 min)

```
G1 drift pattern: Accumulating/Fluctuating/Stable
Current drift: 2.8%
Trend: +0.1%/hour (example)
Correlation specialist: weak/moderate/strong
Correlation memory: weak/moderate/strong
Escalation triggered: No/Yes (if >4% or strong correlation)
```

---

**Start now. Finish in 20 min. Report immediately.**
