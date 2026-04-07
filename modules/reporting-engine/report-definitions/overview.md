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

- [[reporting-engine|Reporting Engine Module]]
- [[reporting-engine/report-execution/overview|Report Execution]]
- [[reporting-engine/report-templates/overview|Report Templates]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[shared-kernel]]
- [[WEEK4-productivity-analytics]]
