# Background Jobs Userflow

## Actor

Operations user.

## Journey

1. Operator opens System Operations -> Background Jobs.
2. Console lists recurring, running, failed, and completed jobs.
3. Operator opens failed job detail.
4. If job is retryable and operator has manage permission, operator retries with reason.
5. Backend audits retry or schedule change.

## APIs Used

- `GET /admin/v1/operations/background-jobs`
- `GET /admin/v1/operations/background-jobs/{jobId}`
- `POST /admin/v1/operations/background-jobs/{jobId}/retry`
- `PATCH /admin/v1/operations/background-jobs/{jobId}`
