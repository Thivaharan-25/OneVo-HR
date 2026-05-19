# Report Manager End-to-End Logic

## Generate Report

1. Operator opens Analytics & Reports -> Reports.
2. Frontend calls `GET /admin/v1/reports`.
3. Operator selects report, filters, and export format.
4. Frontend calls `POST /admin/v1/reports/export`.
5. Backend verifies `platform.reports.export`.
6. Backend queues report job and stores status.
7. Operator downloads when job completes.

## APIs

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/reports` | Report catalog | `platform.reports.read` |
| POST | `/admin/v1/reports/export` | Start export | `platform.reports.export` |
| GET | `/admin/v1/reports/exports/{id}` | Export status/download metadata | `platform.reports.read` |

## Rules

- Export payload must record filters and requester.
- Export access expires.
- Report generation failures appear in Background Jobs or report export status.
