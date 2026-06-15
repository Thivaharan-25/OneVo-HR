# Report Manager

## Purpose

Report Manager provides a catalog of pre-defined platform reports that operators can generate and export. Unlike Reports / Analytics (which is a live dashboard), Report Manager is for generating point-in-time, structured exports of specific operational or commercial data sets — for sharing with leadership, handing off to legal/compliance teams, or archiving.

## Data / Systems Read and Written

| Source | Role |
|---|---|
| Reporting Engine | Report definitions, export job queue, export status |
| Analytics readers | Data inputs for each report type |
| File storage | Store generated export packages |
| Audit log | Write every export request with actor, report type, filters, and row count |

## Capabilities

- Browse the platform report catalog (report name, description, available filters, supported export formats)
- Generate a report for a selected date range, tenant filter, and other report-specific parameters
- Export as CSV — standard for all reports
- Track export job status (synchronous for small exports; async with email notification for large)
- Download generated reports via access-controlled, time-limited download links
- View export history with requester, filters, row count, and download expiry

## Navigation

| Route | Permission |
|---|---|
| `/analytics/reports` | `platform.reports.read` |
| Generate and export | `platform.reports.read` (export may require separate export permission) |

## Key Rules

- Generated report files expire per platform retention policy (typically 24 hours after generation)
- Failed report generation returns a human-readable error message — no raw stack traces or SQL errors
- Every export request is audit-logged with actor, report type, filters applied, and row count
- Report access is permission-filtered by data domain — billing reports require subscription read permission

## Related

- [[developer-platform/modules/report-manager/end-to-end-logic|Report Manager End-to-End Logic]]
- [[developer-platform/modules/platform-analytics/overview|Reports / Analytics]] — live aggregate dashboards
- [[developer-platform/modules/audit-console/overview|Audit Console]] — audit-specific export
- [[developer-platform/modules/compliance-center/overview|Compliance Center]] — compliance-specific data exports
