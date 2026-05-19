# Platform Analytics

## Purpose

Platform Analytics provides cross-tenant operational and commercial analytics for ONEVO operators. It surfaces aggregate trends on tenant growth, subscription distribution, product module adoption, and device rollout — enabling data-driven decisions about the platform's commercial and operational health.

## Data / Systems Read

| Source | Role |
|---|---|
| Tenant registry | Tenant count, lifecycle, churn trends |
| `tenant_module_entitlements` | Module adoption by status (active, trial, etc.) |
| `tenant_subscriptions` | Plan distribution and commercial analytics |
| Agent Gateway | Device and agent adoption counts |
| `audit_log` | Operational event volume trends |

## Capabilities

- **Platform overview:** Total active tenants, DAU, device counts, module adoption summary
- **Tenant analytics:** Tenant growth over time, churn rate, status distribution, activation funnel
- **Subscription analytics:** Plan tier distribution, commercial model breakdown, revenue trends (aggregate)
- **Module analytics:** Module adoption count per module (active/trial/disabled), adoption trends over time
- **Device analytics:** Registered device count by ring, agent version distribution, update adoption rate
- Export aggregate analytics as CSV/PDF

## Navigation

| Route | Permission |
|---|---|
| `/analytics/platform` | `platform.reports.read` |
| Commercial detail | `platform.subscriptions.read` (additional) |

## Key Rules

- All analytics are aggregate by default — no individual employee names, individual user activity, or per-user breakdowns
- Commercial analytics (subscription revenue, plan pricing) require `platform.subscriptions.read` in addition to `platform.reports.read`
- Module adoption counts are sourced from `tenant_module_entitlements` — the authoritative entitlement state — not from subscription plan data alone
- Tenant JWT is rejected

## Related

- [[developer-platform/modules/platform-analytics/end-to-end-logic|Platform Analytics End-to-End Logic]]
- [[developer-platform/modules/report-manager/overview|Report Manager]] — export specific reports
- [[developer-platform/modules/subscription-manager/overview|Subscription Manager]] — commercial detail
