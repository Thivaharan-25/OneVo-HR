# Platform Health Userflow

## Actor

Operations user with `platform.health.read`.

## Journey

1. Operator opens Operations and selects the Platform Health view.
2. Console loads overall status, service health, dependency health, job summary, configuration checks, security checks, and recent events on one screen.
3. Operator expands a degraded service row to view redacted evidence, dependency links, and recent events.
4. If allowed, operator triggers a registered safe service action directly from the service row.
5. Background job, infrastructure, device, and agent-version issues remain read-only summaries in Phase 1; standalone detail screens are Phase 2.

## APIs Used

- `GET /admin/v1/operations/platform-health`
- `GET /admin/v1/operations/platform-health/dependencies`
- `POST /admin/v1/operations/platform-health/services/{serviceKey}/actions/{action}`
