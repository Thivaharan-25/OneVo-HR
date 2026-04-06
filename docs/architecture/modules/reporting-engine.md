# Module: Reporting Engine

**Namespace:** `ONEVO.Modules.ReportingEngine`
**Pillar:** Shared Foundation
**Owner:** Dev 1 (Week 4)
**Tables:** 3

---

## Purpose

Scheduled and on-demand report generation serving **both pillars** — HR reports (headcount, turnover, leave utilization) and workforce intelligence reports (productivity, exceptions, presence). Supports CSV/Excel export.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[productivity-analytics]] | `IProductivityAnalyticsService` | Workforce reports |
| **Depends on** | [[core-hr]] | `IEmployeeService` | HR reports |
| **Depends on** | [[leave]] | `ILeaveService` | Leave utilization reports |
| **Depends on** | [[workforce-presence]] | `IWorkforcePresenceService` | Attendance reports |

---

## Database Tables (3)

### `report_definitions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `name` | `varchar(100)` | |
| `report_type` | `varchar(30)` | `headcount`, `turnover`, `leave_utilization`, `productivity_daily`, `productivity_weekly`, `workforce_summary`, `exception_summary` |
| `parameters_json` | `jsonb` | Filters, date ranges |
| `schedule_cron` | `varchar(50)` | Cron expression (nullable — on-demand) |
| `output_format` | `varchar(10)` | `csv`, `xlsx` |
| `recipients_json` | `jsonb` | Email recipients |
| `is_active` | `boolean` | |
| `created_by_id` | `uuid` | |
| `created_at` | `timestamptz` | |

### `report_executions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `definition_id` | `uuid` | FK → report_definitions |
| `status` | `varchar(20)` | `queued`, `running`, `completed`, `failed` |
| `file_record_id` | `uuid` | FK → file_records (generated report) |
| `row_count` | `int` | |
| `started_at` | `timestamptz` | |
| `completed_at` | `timestamptz` | |
| `error_message` | `text` | |

### `report_templates`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `name` | `varchar(100)` | |
| `report_type` | `varchar(30)` | |
| `columns_json` | `jsonb` | Column definitions |
| `filters_json` | `jsonb` | Default filters |
| `is_system` | `boolean` | System templates can't be deleted |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/reports/definitions` | `reports:read` | List report definitions |
| POST | `/api/v1/reports/definitions` | `reports:create` | Create scheduled report |
| POST | `/api/v1/reports/execute/{definitionId}` | `reports:create` | Run report on-demand |
| GET | `/api/v1/reports/executions` | `reports:read` | List past executions |
| GET | `/api/v1/reports/executions/{id}/download` | `reports:read` | Download report file |

See also: [[module-catalog]], [[productivity-analytics]], [[core-hr]]
