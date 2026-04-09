# Report Definitions

**Module:** Reporting Engine  
**Feature:** Report Definitions

---

## Purpose

Scheduled and on-demand report definitions with cron scheduling and output format configuration.

## Database Tables

### `report_definitions`
Key columns: `name`, `report_type` (`headcount`, `turnover`, `leave_utilization`, `productivity_daily`, `productivity_weekly`, `workforce_summary`, `exception_summary`), `parameters_json`, `schedule_cron` (nullable for on-demand), `output_format` (`csv`, `xlsx`), `recipients_json`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/reports/definitions` | `reports:read` | List definitions |
| POST | `/api/v1/reports/definitions` | `reports:create` | Create scheduled report |

## Related

- [[modules/reporting-engine/overview|Reporting Engine Module]]
- [[frontend/architecture/overview|Report Execution]]
- [[frontend/architecture/overview|Report Templates]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV1-productivity-analytics|DEV1: Productivity Analytics]]
