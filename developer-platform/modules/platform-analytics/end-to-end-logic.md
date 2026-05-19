# Platform Analytics End-to-End Logic

## Load Analytics

1. Operator opens Analytics & Reports -> Platform Analytics.
2. Frontend calls analytics endpoints for tenant, subscription, module, and operations summaries.
3. Backend verifies `platform.analytics.read`.
4. Backend returns aggregate metrics with date ranges and filters.

## APIs

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/analytics/platform` | Platform overview analytics | `platform.analytics.read` |
| GET | `/admin/v1/analytics/tenants` | Tenant lifecycle analytics | `platform.analytics.read` |
| GET | `/admin/v1/analytics/subscriptions` | Commercial analytics | `platform.analytics.read` |
| GET | `/admin/v1/analytics/modules` | Product module adoption | `platform.analytics.read` |

## Rules

- Responses must be aggregate unless a specific drill-down endpoint is documented.
- Subscription-sensitive drilldowns require both analytics and subscription read permission.
