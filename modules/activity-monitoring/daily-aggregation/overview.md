# Daily Aggregation

**Module:** Activity Monitoring
**Feature:** Daily Aggregation

---

## Purpose

Pre-aggregates activity snapshots into daily rollups. **This is the primary table for reporting.** The only activity table that allows UPDATE (upsert on conflict).

## Database Tables

### `activity_daily_summary`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `date` | `date` | |
| `total_active_minutes` | `int` | |
| `total_idle_minutes` | `int` | |
| `total_meeting_minutes` | `int` | |
| `active_percentage` | `decimal(5,2)` | |
| `top_apps_json` | `jsonb` | Top 5 apps with time |
| `intensity_avg` | `decimal(5,2)` | Average intensity score |
| `keyboard_total` | `int` | Total keyboard events |
| `mouse_total` | `int` | Total mouse events |

**Retention:** 2 years (small, pre-aggregated)
**Upsert:** INSERT or UPDATE on conflict for `(tenant_id, employee_id, date)`

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `DailySummaryAggregated` | Daily summary job completes | [[productivity-analytics]] (build reports) |

## Hangfire Jobs

| Job | Schedule | Queue | Purpose |
|:----|:---------|:------|:--------|
| `AggregateDailySummaryJob` | Every 30 min + EOD | Default | Roll up snapshots → daily summary |
