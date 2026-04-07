# Report Execution

**Module:** Reporting Engine  
**Feature:** Report Execution

---

## Purpose

Tracks report execution status and generated files.

## Database Tables

### `report_executions`
Fields: `definition_id`, `status` (`queued`, `running`, `completed`, `failed`), `file_record_id`, `row_count`, `started_at`, `completed_at`, `error_message`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/reports/execute/{definitionId}` | `reports:create` | Run on-demand |
| GET | `/api/v1/reports/executions` | `reports:read` | List past executions |
| GET | `/api/v1/reports/executions/{id}/download` | `reports:read` | Download report |

## Related

- [[reporting-engine|Reporting Engine Module]]
- [[reporting-engine/report-definitions/overview|Report Definitions]]
- [[reporting-engine/report-templates/overview|Report Templates]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[data-classification]]
- [[WEEK4-productivity-analytics]]
