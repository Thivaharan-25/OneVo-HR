# Raw Data Processing

**Module:** Activity Monitoring
**Feature:** Raw Data Processing

---

## Purpose

Receives raw activity data from the desktop agent via [[modules/agent-gateway/overview|Agent Gateway]] and processes it into structured activity snapshots. Uses a temporary high-volume buffer (`activity_raw_buffer`) partitioned daily, purged after 48 hours.

## Database Tables

### `activity_raw_buffer`

Temporary high-volume buffer. Data arrives from [[modules/agent-gateway/overview|Agent Gateway]], sits here until processed.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `agent_device_id` | `uuid` | FK → registered_agents |
| `received_at` | `timestamptz` | Server receive time |
| `payload_json` | `jsonb` | Raw agent payload |

**Partitioning:** Daily via `pg_partman` on `received_at`
**Retention:** Purged after 48 hours by `PurgeRawBufferJob`
**Insert method:** `COPY` or `unnest()` for batch performance
**NEVER query this table for reporting** — use `activity_daily_summary` instead.

### `activity_snapshots`

Periodic activity data from agent (every 2-3 minutes).

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `captured_at` | `timestamptz` | When agent captured this snapshot |
| `keyboard_events_count` | `int` | Key press count (NOT keystrokes content) |
| `mouse_events_count` | `int` | Mouse event count |
| `active_seconds` | `int` | Seconds with input activity |
| `idle_seconds` | `int` | Seconds without input |
| `intensity_score` | `decimal(5,2)` | 0–100 computed score |
| `foreground_app` | `varchar(255)` | Application name |
| `created_at` | `timestamptz` | |

**Partitioning:** Monthly via `pg_partman` on `captured_at`
**Retention:** 90 days
**Volume estimate:** ~240 rows/employee/day (one every 2-3 min for 8 hours). 500 employees = 120,000 rows/day.

## Key Business Rules

1. Activity data is **append-only** — never UPDATE rows in `activity_snapshots` or `activity_raw_buffer`.
2. **Intensity score formula:** `(keyboard_events_count + mouse_events_count) / max_expected_events * 100`, capped at 100.
3. Feature toggle check required before processing any data via `IConfigurationService`.

## Data Pipeline

```
Agent → Agent Gateway (202 Accepted)
  → activity_raw_buffer (COPY/unnest, partitioned daily)
  → ProcessRawBufferJob (Hangfire, every 2 min)
    → activity_snapshots (parsed, validated)
```

## Hangfire Jobs

| Job | Schedule | Queue | Purpose |
|:----|:---------|:------|:--------|
| `ProcessRawBufferJob` | Every 2 min | High | Parse raw buffer → snapshots |
| `PurgeRawBufferJob` | Daily 3:00 AM | Low | Drop partitions older than 48 hours |
| `PurgeExpiredSnapshotsJob` | Monthly | Batch | Drop snapshot partitions older than 90 days |

See also: [[frontend/architecture/overview|Overview]], [[frontend/architecture/overview|Overview]]
