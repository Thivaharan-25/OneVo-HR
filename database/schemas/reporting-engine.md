# Reporting Engine — Schema

**Module:** [[modules/reporting-engine/overview|Reporting Engine]]
**Phase:** Phase 2
**Tables:** 3

---

## `report_definitions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `name` | `varchar(100)` |  |
| `report_type` | `varchar(30)` | `headcount`, `turnover`, `leave_utilization`, `productivity_daily`, `productivity_weekly`, `workforce_summary`, `exception_summary` |
| `parameters_json` | `jsonb` | Filters, date ranges |
| `schedule_cron` | `varchar(50)` | Cron expression (nullable — on-demand) |
| `output_format` | `varchar(10)` | `csv`, `xlsx` |
| `recipients_json` | `jsonb` | Email recipients |
| `is_active` | `boolean` |  |
| `created_by_id` | `uuid` |  |
| `created_at` | `timestamptz` |  |

---

## `report_executions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `definition_id` | `uuid` | FK → report_definitions |
| `status` | `varchar(20)` | `queued`, `running`, `completed`, `failed` |
| `file_record_id` | `uuid` | FK → file_records (generated report) |
| `row_count` | `int` |  |
| `started_at` | `timestamptz` |  |
| `completed_at` | `timestamptz` |  |
| `error_message` | `text` |  |

**Foreign Keys:** `definition_id` → [[#`report_definitions`|report_definitions]], `file_record_id` → [[database/schemas/infrastructure#`file_records`|file_records]]

---

## `report_templates`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `name` | `varchar(100)` |  |
| `report_type` | `varchar(30)` |  |
| `columns_json` | `jsonb` | Column definitions |
| `filters_json` | `jsonb` | Default filters |
| `is_system` | `boolean` | System templates can't be deleted |

---

## Related

- [[modules/reporting-engine/overview|Reporting Engine Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]