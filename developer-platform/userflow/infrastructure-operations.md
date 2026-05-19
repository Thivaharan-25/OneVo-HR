# Infrastructure Operations Userflow

## Actor

Operations user.

## Journey

1. Operator opens System Operations -> Infrastructure.
2. Console loads capacity and dependency summaries.
3. Operator reviews degraded provider or infrastructure area.
4. Operator follows links to Services Monitor or Background Jobs.

## APIs Used

- `GET /admin/v1/operations/infrastructure`
- `GET /admin/v1/operations/infrastructure/dependencies`
