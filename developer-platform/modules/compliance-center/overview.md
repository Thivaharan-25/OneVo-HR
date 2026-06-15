# Compliance Center

## Purpose

Compliance Center manages cross-tenant compliance exports, legal holds, legal document versions, and legal/privacy acceptance evidence for ONEVO operators responding to legal requests, regulatory audits, policy changes, or internal compliance reviews.

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `compliance_exports` | Read + write — export requests, status, and download metadata |
| `legal_holds` | Read + write — legal hold definitions and release records |
| `legal_document_versions` | Read + write - versioned Terms, Privacy Notice, monitoring notice, screenshot notice, biometric/photo consent, and marketing consent documents |
| `legal_acceptance_records` | Read - user acceptance/acknowledgement evidence by document type and version |
| Audit log | Write every compliance action |
| File storage | Store generated compliance export packages |

## Capabilities

### Legal Holds
- Create legal holds on a specific tenant's data — prevents any retention sweep job from deleting data for that tenant while the hold is active
- Release legal holds when the legal matter is resolved (requires a release reason)
- View all active and released legal holds with full history

### Compliance Exports
- Request a scoped data export for a tenant or date range (for legal discovery, regulatory audit, DSAR)
- Track export job status — async for large datasets
- Download export packages via access-controlled, time-limited download links
- Download links expire per retention policy (typically 24–72 hours)

### Legal Document Versions
- Create and publish new versions of Terms & Conditions, Privacy Notice, Activity Monitoring Notice, Screenshot Notice, Biometric / Photo Consent, and Marketing Consent text
- Mark each version as required or optional and define whether it blocks dashboard access or only the affected WorkPulse collection category
- Notify affected users when a required document version changes
- View acceptance status by tenant, user, document type, and version

## Navigation

| Route | Permission |
|---|---|
| `/security/compliance` | `platform.compliance.read` |
| Export requests | `platform.compliance.manage` |
| Legal hold management | `platform.compliance.manage` |
| Legal document version management | `platform.compliance.manage` |

## Key Rules

- Legal holds take precedence over all retention policies — held tenant data is never deleted while any hold is active
- Export download links expire and are not re-issuable without a new export request
- All compliance actions (create hold, release hold, request export, download export) are audit-logged with actor and reason
- Compliance exports must include scope and reason fields — both are required for every request

- Publishing a required Terms & Conditions or Privacy Notice version marks affected users pending and blocks dashboard access until accepted or acknowledged
- Publishing a required Activity Monitoring Notice, Screenshot Notice, or Biometric / Photo Consent version blocks only the affected WorkPulse collection or verification path until completed
- Marketing consent is optional and must not block product access

## Related

- [[developer-platform/modules/compliance-center/end-to-end-logic|Compliance Center End-to-End Logic]]
- [[developer-platform/modules/data-retention/overview|Data Retention]] — retention policies that legal holds override
- [[developer-platform/modules/audit-console/overview|Audit Console]] — audit trail for compliance investigation
