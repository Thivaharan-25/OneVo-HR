# Services Monitor Userflow

## Actor

Operations user.

## Journey

1. Operator opens System Operations -> Services Monitor.
2. Console lists services and component status.
3. Operator opens service detail.
4. If allowed, operator triggers a safe service action.
5. Backend audits any action.

## APIs Used

- `GET /admin/v1/operations/services`
- `GET /admin/v1/operations/services/{serviceKey}`
- `POST /admin/v1/operations/services/{serviceKey}/actions/{action}`
