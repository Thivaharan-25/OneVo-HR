# Reports Userflow

## Actor

Platform analyst or operator.

## Journey

1. Operator opens Reports / Analytics -> Reports.
2. Console lists available platform reports.
3. Operator selects report, filters, date range, and export format.
4. Backend queues export.
5. Operator downloads export when complete.

## APIs Used

- `GET /admin/v1/reports`
- `POST /admin/v1/reports/export`
- `GET /admin/v1/reports/exports/{id}`
