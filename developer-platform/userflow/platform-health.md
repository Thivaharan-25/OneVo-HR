# Platform Health Userflow

## Actor

Operations user with `platform.health.read`.

## Journey

1. Operator opens System Operations -> Platform Health.
2. Console loads service and dependency health.
3. Operator drills into degraded service or background job.
4. Console routes to Services Monitor or Background Jobs for detail.

## APIs Used

- `GET /admin/v1/operations/platform-health`
- `GET /admin/v1/operations/platform-health/dependencies`
