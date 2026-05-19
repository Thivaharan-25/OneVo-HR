# Compliance Center End-to-End Logic

## Request Export

1. Operator opens Security & Compliance -> Compliance Center.
2. Operator selects tenant, subject/scope, data categories, and reason.
3. Frontend calls `POST /admin/v1/compliance/exports`.
4. Backend verifies `platform.compliance.export`.
5. Backend queues export job and writes audit event.
6. Operator tracks status through export list.

## Create Legal Hold

1. Operator opens Legal Holds.
2. Operator enters tenant, scope, data categories, dates, and reason.
3. Frontend calls `POST /admin/v1/legal-holds`.
4. Backend verifies `platform.compliance.manage`.
5. Backend stores hold and ensures retention sweep skips held data.

## APIs

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/compliance/overview` | Compliance summary | `platform.compliance.read` |
| GET | `/admin/v1/compliance/exports` | Export list/status | `platform.compliance.read` |
| POST | `/admin/v1/compliance/exports` | Request export | `platform.compliance.export` |
| GET | `/admin/v1/legal-holds` | Legal hold list | `platform.compliance.read` |
| POST | `/admin/v1/legal-holds` | Create legal hold | `platform.compliance.manage` |
| PATCH | `/admin/v1/legal-holds/{id}` | Release/update hold | `platform.compliance.manage` |

## Rules

- Export scope must be explicit.
- Legal holds override retention deletion.
- Compliance export access is audit-logged.
