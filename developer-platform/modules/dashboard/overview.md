# Dashboard

## Purpose

Dashboard is the default Developer Platform landing screen. It gives ONEVO operators a cross-tenant operational summary without opening any tenant-specific workflow.

Dashboard is a read-only aggregation surface. It does not own product data and it must not mutate tenant, subscription, module, security, or system records.

## Data / Systems Read

| Source | Role |
|---|---|
| `tenants` | Counts by status, trial/demo follow-up, recent provisioning activity |
| `users` | Active user counts across active tenants |
| Agent Gateway | Registered device and agent health counts |
| Shared Platform health readers | Service health, alert totals, background job status |
| Audit log reader | Recent platform events |
| Subscription readers | Tenant distribution by plan/commercial model, payment pending, revenue overview, expiring subscriptions |
| Demo Profile readers | Trial tenants, expiring/expired demos, converted demos, pending payment |
| Requests Center readers | Demo access requests and trial extension queues |

## Capabilities

- Show top KPI cards: Total Tenants, Active Tenants, Trial Tenants, Payment Pending, Platform Health, Monthly Revenue.
- Show Trial Follow-up: Expiring Soon, Expired, Converted, Pending Payment.
- Show Revenue Overview: revenue this month, month-over-month growth, paid tenants, new tenants, average revenue per tenant, and revenue trend chart.
- Show Platform Health Overview: per-service health status (API Gateway, Auth, Data, Sync, Reporting, AI Insights Engine) with uptime %.
- Show Platform Operations: active users, active devices, alerts overview, and resource utilization.
- Show Tenant Distribution donut: breakdown by plan tier and lifecycle status (Enterprise, Business, Professional, Pending Payment, Active, Suspended).
- Show Active Users Over Time line chart - adapts resolution to selected time window.
- Show Device Status donut: Online / Idle / Offline breakdown with Sync Success Rate.
- Show Alerts Overview donut: Critical (red) / Warning (orange) / Info (blue) / Resolved (green) with MTTR.
- Show System Resource Utilization gauges: CPU / Memory / Storage with threshold color bands.
- Show Recent System Events table: last 10 platform-significant events across all tenants.
- Show Expiring / Attention queues: trials ending soon, subscriptions ending soon, tenants with unpaid invoices, and demo/trial requests awaiting review.
- Quick Actions panel: Create Tenant, Create Demo Profile, Review Requests, Add Platform Admin, View System Health, Manage Policies, Export Report.
- Link every summary card and widget to the owning Developer Platform module.

## Alert Detection (summary)

Alerts are generated automatically by three backend pathways - not by operators:
1. **MediatR domain event handlers** - module events (login failures, payment failures, identity verification spikes, agent disconnects) publish events that `AlertCreationHandler` converts to `platform_alerts` rows when thresholds are crossed.
2. **Background health check jobs** - `PlatformHealthCheckJob` polls service endpoints every 2 minutes; `ResourceUtilizationCheckJob` checks CPU/memory/storage every 5 minutes.
3. **Webhook handlers** - Paddle and PayHere event processing creates billing alerts when payments fail or disputes occur.

Every alert has a severity (`critical`, `warning`, `info`) set by the detection pathway based on the condition. See [[developer-platform/modules/dashboard/end-to-end-logic|Dashboard End-to-End Logic]] for the full alert condition catalog, severity classification rules, deduplication logic, and auto-resolution behavior.

## Navigation

Dashboard is a top-level sidebar icon with no expansion panel.

| Route | Permission |
|---|---|
| `/` | `platform.dashboard.view` |

## Rules

- Dashboard data must be aggregated and permission-filtered by platform permission.
- Dashboard must not expose employee-level data.
- Dashboard links must route to the owning Developer Platform module, not duplicate module behavior.

## Related

- [[developer-platform/modules/platform-health/overview|Platform Health]]
- [[developer-platform/modules/tenant-console/overview|Tenant Management]]
- [[developer-platform/modules/audit-console/overview|Audit Console]]

