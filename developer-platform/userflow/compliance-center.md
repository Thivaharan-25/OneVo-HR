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

## Legal Document Version Journey

1. Operator opens Compliance Center -> Legal Documents.
2. Operator creates a new version for Terms & Conditions, Privacy Notice, Activity Monitoring Notice, Screenshot Notice, Biometric / Photo Consent, or Marketing Consent.
3. Operator marks whether the version is required and enters a publish reason.
4. Backend publishes the version, notifies affected users, and writes audit history.
5. Required Terms or Privacy changes block dashboard access until accepted or acknowledged.
6. Monitoring, screenshot, and biometric/photo notices block only the affected WorkPulse collection or verification path until completed.
7. Operator reviews acceptance tracking by tenant, user, document type, and version.

## APIs Used

- `GET /admin/v1/compliance/overview`
- `GET /admin/v1/compliance/exports`
- `POST /admin/v1/compliance/exports`
- `GET /admin/v1/legal-holds`
- `POST /admin/v1/legal-holds`
- `PATCH /admin/v1/legal-holds/{id}`
- `GET /admin/v1/legal-documents`
- `POST /admin/v1/legal-documents/{documentType}/versions`
- `GET /admin/v1/legal-documents/{documentType}/acceptance`
