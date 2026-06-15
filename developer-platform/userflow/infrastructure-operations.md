# Infrastructure Operations Userflow

> Phase 2 only as a standalone userflow. Phase 1 exposes only basic read-only dependency status through Platform Health.

## Actor

Operations user.

## Journey

1. Operator opens Phase 2 Operations -> Infrastructure.
2. Console loads capacity and dependency summaries.
3. Operator reviews degraded provider or infrastructure area.
4. Operator follows links to Platform Health service/dependency detail or Background Jobs.

## APIs Used

- `GET /admin/v1/operations/infrastructure`
- `GET /admin/v1/operations/infrastructure/dependencies`
