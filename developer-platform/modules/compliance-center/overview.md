# Compliance Center

## Purpose

Compliance Center manages cross-tenant compliance exports and legal holds for ONEVO operators responding to legal requests, regulatory audits, or internal compliance reviews.

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `compliance_exports` | Read + write — export requests, status, and download metadata |
| `legal_holds` | Read + write — legal hold definitions and release records |
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

## Navigation

| Route | Permission |
|---|---|
| `/security/compliance` | `platform.compliance.read` |
| Export requests | `platform.compliance.manage` |
| Legal hold management | `platform.compliance.manage` |

## Key Rules

- Legal holds take precedence over all retention policies — held tenant data is never deleted while any hold is active
- Export download links expire and are not re-issuable without a new export request
- All compliance actions (create hold, release hold, request export, download export) are audit-logged with actor and reason
- Compliance exports must include scope and reason fields — both are required for every request

## Related

- [[developer-platform/modules/compliance-center/end-to-end-logic|Compliance Center End-to-End Logic]]
- [[developer-platform/modules/data-retention/overview|Data Retention]] — retention policies that legal holds override
- [[developer-platform/modules/audit-console/overview|Audit Console]] — audit trail for compliance investigation
