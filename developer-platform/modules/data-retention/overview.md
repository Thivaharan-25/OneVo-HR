# Data Retention

## Purpose

Data Retention manages the policies that determine how long different categories of ONEVO data are kept before deletion. It works in conjunction with Compliance Center's legal holds, which override retention deletion. Phase 1 exposes retention sweep status only as a read-only Platform Health summary; the standalone Background Jobs screen is Phase 2.

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `retention_policies` | Read + write — policy definitions per data category |
| `legal_holds` | Read — hold protection state (written by Compliance Center) |
| Retention sweep job | Read-only sweep health surfaced through Platform Health in Phase 1; standalone monitoring/triggering is Phase 2 |
| Audit log | Write every policy change with old/new values and reason |

## Retention Periods (defaults)

| Data Category | Default Retention | Notes |
|---|---|---|
| Standard audit events | 2 years | |
| Security-category events | 5 years | Regulatory requirement |
| Billing events | 7 years | Legal/financial requirement |
| Platform admin session logs | 1 year | |
| Compliance export download links | 24 hours | |

## Capabilities

- View retention policies by data category with current retention period
- Update a retention policy — requires impact preview acknowledgement and an audit reason
- Preview records and categories that would be affected by a policy change before committing
- Monitor retention sweep job runs and outcomes
- All policies respect active legal holds — data under a legal hold is never deleted regardless of retention policy

## Navigation

| Route | Permission |
|---|---|
| `/security/data-retention` | `platform.compliance.read` |
| Policy updates | `platform.compliance.manage` |

## Key Rules

- Legal holds from Compliance Center always take precedence — a hold blocks deletion for the held tenant unconditionally
- Shortening a retention period requires impact preview before save — cannot be skipped
- Retention sweep is idempotent — re-running does not double-delete
- All policy changes are audit-logged with previous period, new period, actor, and reason
- Audit records are subject to their own retention policy and cannot be deleted before it expires

## Related

- [[developer-platform/modules/data-retention/end-to-end-logic|Data Retention End-to-End Logic]]
- [[developer-platform/modules/compliance-center/overview|Compliance Center]] — legal holds
- [[developer-platform/modules/background-jobs/overview|Background Jobs]] — Phase 2 standalone retention sweep execution/operations
- [[developer-platform/modules/audit-console/overview|Audit Console]] — retention rules for audit log data
