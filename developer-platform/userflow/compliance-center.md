# Compliance Center Userflow

## Actor

Compliance operator.

## Export Journey

1. Operator opens Security & Compliance -> Compliance Center.
2. Operator selects tenant, data scope, category, date range, and reason.
3. Console calls `POST /admin/v1/compliance/exports`.
4. Backend queues export and audits request.
5. Operator tracks export status.

## Legal Hold Journey

1. Operator opens legal holds.
2. Operator creates hold with tenant, scope, category, date range, and reason.
3. Retention sweep skips held data.

## APIs Used

- `GET /admin/v1/compliance/overview`
- `GET /admin/v1/compliance/exports`
- `POST /admin/v1/compliance/exports`
- `GET /admin/v1/legal-holds`
- `POST /admin/v1/legal-holds`
- `PATCH /admin/v1/legal-holds/{id}`
