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

- [[modules/reporting-engine/overview|Reporting Engine Module]]
- [[frontend/architecture/overview|Report Definitions]]
- [[frontend/architecture/overview|Report Templates]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[security/data-classification|Data Classification]]
- [[current-focus/DEV1-productivity-analytics|DEV1: Productivity Analytics]]
