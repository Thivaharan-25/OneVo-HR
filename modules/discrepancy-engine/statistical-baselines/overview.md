# Statistical Baselines

**Module:** Discrepancy Engine
**Feature:** Statistical Baselines

---

## Purpose

Pre-computes per-employee rolling 30-day statistics on `unaccounted_minutes` so the main `DiscrepancyEngineJob` can classify severity relative to that employee's personal norm rather than absolute thresholds. Reduces false positives for employees who systematically under-log (e.g., researchers, field roles) while catching genuine anomalies.

## How It Works

`ComputeDiscrepancyBaselinesJob` runs daily at 10:00 PM (30 minutes before `DiscrepancyEngineJob`). For each employee, it runs a rolling SQL aggregate over the past 30 days of `discrepancy_events`:

```sql
SELECT employee_id,
       AVG(unaccounted_minutes)::DECIMAL(8,2),
       STDDEV(unaccounted_minutes)::DECIMAL(8,2),
       COUNT(*)
FROM discrepancy_events
WHERE tenant_id = @tenantId AND date >= @windowStart AND date < @today
GROUP BY employee_id
```

Results are upserted into `employee_discrepancy_baselines`.

## Severity Calculation

`DiscrepancySeverityCalculator.Calculate()` applies:

| Condition | Method | Severity Brackets |
|:----------|:-------|:------------------|
| Baseline has ≥ 5 samples + stddev > 0 | `baseline_relative` (z-score) | z < 1.0 → none, 1.0–1.5 → low, 1.5–2.5 → high, ≥ 2.5 → critical |
| Baseline unavailable or < 5 samples | `absolute` (fallback) | < 30 min → none, 30–60 → low, 60–180 → high, ≥ 180 → critical |

## Hangfire Job

| Job | Schedule | Queue |
|:----|:---------|:------|
| `ComputeDiscrepancyBaselinesJob` | Daily 10:00 PM | Default |

## Key Rules

1. **Minimum 5 samples required** before baseline is used. New employees always use absolute thresholds.
2. **Zero stddev is treated as unusable** — prevents division-by-zero and handles employees with perfectly consistent patterns.
3. **Results are per-tenant, per-employee** — one baseline row per employee per day.
4. **Baseline data is stored on `discrepancy_events`** as `z_score`, `baseline_avg_minutes`, `baseline_stddev_minutes`, and `severity_method` for auditability.

## Related

- [[database/schemas/discrepancy-engine|Discrepancy Engine Schema]] — `employee_discrepancy_baselines` table
- [[modules/discrepancy-engine/overview|Discrepancy Engine Overview]]
