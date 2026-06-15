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

## Publish Legal Document Version

1. Operator opens Security & Compliance -> Compliance Center -> Legal Documents.
2. Operator selects document type, enters version label, document content/link, required flag, affected audience, and publish reason.
3. Frontend calls `POST /admin/v1/legal-documents/{documentType}/versions`.
4. Backend verifies `platform.compliance.manage`.
5. Backend creates the new published version, marks affected users pending where required, sends notifications, and writes audit events.
6. Required Terms & Conditions or Privacy Notice versions block dashboard access until accepted or acknowledged.
7. Required Activity Monitoring Notice, Screenshot Notice, or Biometric / Photo Consent versions block only the affected WorkPulse collection or verification path until completed.

## APIs

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/compliance/overview` | Compliance summary | `platform.compliance.read` |
| GET | `/admin/v1/compliance/exports` | Export list/status | `platform.compliance.read` |
| POST | `/admin/v1/compliance/exports` | Request export | `platform.compliance.export` |
| GET | `/admin/v1/legal-holds` | Legal hold list | `platform.compliance.read` |
| POST | `/admin/v1/legal-holds` | Create legal hold | `platform.compliance.manage` |
| PATCH | `/admin/v1/legal-holds/{id}` | Release/update hold | `platform.compliance.manage` |
| GET | `/admin/v1/legal-documents` | List legal document types and published versions | `platform.compliance.read` |
| POST | `/admin/v1/legal-documents/{documentType}/versions` | Publish a legal document version | `platform.compliance.manage` |
| GET | `/admin/v1/legal-documents/{documentType}/acceptance` | Acceptance status by tenant/user/version | `platform.compliance.read` |

## Rules

- Export scope must be explicit.
- Legal holds override retention deletion.
- Compliance export access is audit-logged.
- Legal document publishes are audit-logged and must include a reason.
- Required legal document changes notify affected users and create pending acceptance work.
