# Platform Health Userflow

## Actor

Operations user with `platform.health.read`.

## Journey

1. Operator opens System Operations -> Platform Health.
2. Console loads service and dependency health.
3. Operator drills into a degraded service when Services Monitor is available.
4. Background job and infrastructure issues remain read-only summaries in Phase 1; standalone detail screens are Phase 2.

## APIs Used

- `GET /admin/v1/operations/platform-health`
- `GET /admin/v1/operations/platform-health/dependencies`
