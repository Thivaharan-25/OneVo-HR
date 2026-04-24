# Activity Baselines

**Module:** Exception Engine
**Feature:** Baseline-Relative Thresholds

---

## Purpose

Pre-computes per-employee rolling 30-day statistics for each tracked activity metric so exception rules can evaluate thresholds relative to that employee's personal norm rather than absolute values. Reduces false positives for employees whose baseline activity differs from the global default (e.g., field roles, part-time employees).

## How It Works

`ComputeActivityBaselinesJob` runs daily at 9:45 PM (before the exception engine evaluation cycle). For each tenant and each tracked metric, it runs a rolling SQL aggregate over `activity_daily_summary`:

```sql
SELECT employee_id,
       AVG(<metric>)::DECIMAL(10,2),
       STDDEV(<metric>)::DECIMAL(10,2),
       COUNT(*)
FROM activity_daily_summary
WHERE tenant_id = @tenantId AND date >= @windowStart AND date < @today
GROUP BY employee_id
```

Results are upserted into `employee_activity_baselines` (one row per employee per metric per day).

## Tracked Metrics

| Metric | Column in `activity_daily_summary` |
|:-------|:-----------------------------------|
| `idle_minutes` | `total_idle_minutes` |
| `active_minutes` | `total_active_minutes` |
| `intensity_avg` | `intensity_avg` |
| `keyboard_total` | `keyboard_total` |
| `mouse_total` | `mouse_total` |

## Baseline-Relative Rule Conditions

Exception rules set `Operator = "baseline_relative"` on a `RuleCondition` to opt in to this evaluation path. Two additional fields are required:

| Field | Purpose |
|:------|:--------|
| `SigmaMultiplier` | How many standard deviations above the baseline constitutes a breach (e.g., `2.0`) |
| `FallbackAbsoluteThreshold` | Used when no usable baseline exists (new employee, < 5 samples) |

**Threshold formula:** `avg_value + (sigma_multiplier × stddev_value)`

## Evaluation Path

`BaselineRuleEvaluator.EvaluateAsync()` handles `baseline_relative` conditions:

1. Fetch the latest pre-computed baseline for `(tenantId, employeeId, metric)`
2. If baseline is usable (≥ 5 samples, stddev > 0): compute `avg + sigma × stddev` as the threshold
3. If not usable: fall back to `FallbackAbsoluteThreshold`
4. Evaluate: `metric_value > threshold` → condition breached

## Hangfire Job

| Job | Schedule | Queue |
|:----|:---------|:------|
| `ComputeActivityBaselinesJob` | Daily 9:45 PM | Default |

## Key Rules

1. **Minimum 5 samples required** before baseline thresholds are applied. New employees always use the absolute fallback.
2. **Zero stddev is treated as unusable** — prevents division-by-zero and handles employees with perfectly flat activity patterns.
3. **One row per employee per metric per day** — the unique index on `(tenant_id, employee_id, metric, computed_at)` enforces this.
4. **Existing absolute rules are unaffected** — only conditions with `Operator = "baseline_relative"` use this path. All other operators (`gt`, `lt`, `gte`, `lte`) evaluate against their explicit `Threshold` value as before.

## Related

- [[database/schemas/exception-engine|Exception Engine Schema]] — `employee_activity_baselines` table
- [[modules/exception-engine/evaluation-engine/overview|Evaluation Engine]] — where `BaselineRuleEvaluator` is wired in
- [[modules/exception-engine/exception-rules/overview|Exception Rules]] — `RuleCondition` fields `SigmaMultiplier` and `FallbackAbsoluteThreshold`
- [[modules/exception-engine/overview|Exception Engine Overview]]
