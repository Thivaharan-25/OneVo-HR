# Data Retention Userflow

## Actor

Compliance or retention policy manager.

## Journey

1. Operator opens Security & Compliance -> Data Retention.
2. Console loads retention policies.
3. Operator creates or updates a policy.
4. Operator previews impact for destructive changes.
5. Backend saves policy and audits change.
6. Retention sweep job enforces policy while respecting legal holds.

## APIs Used

- `GET /admin/v1/retention-policies`
- `POST /admin/v1/retention-policies`
- `PATCH /admin/v1/retention-policies/{id}`
- `GET /admin/v1/retention-policies/{id}/impact`
