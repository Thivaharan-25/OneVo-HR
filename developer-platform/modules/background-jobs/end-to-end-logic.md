# Background Jobs End-to-End Logic

## View Jobs

1. Operator opens System Operations -> Background Jobs.
2. Frontend calls `GET /admin/v1/operations/background-jobs`.
3. Backend verifies `platform.jobs.read`.
4. Backend returns job status, schedule, last run, duration, and failure summary.

## Retry Job

1. Operator opens failed job detail.
2. Operator clicks retry and provides reason if required.
3. Frontend calls `POST /admin/v1/operations/background-jobs/{jobId}/retry`.
4. Backend verifies `platform.jobs.manage`.
5. Backend validates the job is retryable.
6. Backend queues retry and audits the action.

## APIs

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/operations/background-jobs` | Job list | `platform.jobs.read` |
| GET | `/admin/v1/operations/background-jobs/{jobId}` | Job detail | `platform.jobs.read` |
| POST | `/admin/v1/operations/background-jobs/{jobId}/retry` | Retry failed job | `platform.jobs.manage` |
| PATCH | `/admin/v1/operations/background-jobs/{jobId}` | Enable/disable/update schedule | `platform.jobs.manage` |

## Rules

- Non-idempotent jobs must not expose retry controls.
- Schedule changes require audit reason.
