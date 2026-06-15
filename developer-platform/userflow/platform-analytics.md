# Reports / Analytics Userflow

## Actor

Platform analyst or operator.

## Journey

1. Operator opens Reports / Analytics -> Reports / Analytics.
2. Console loads tenant, subscription, module, and operational analytics.
3. Operator filters by date, tenant segment, plan, module, or status.
4. Operator follows drilldown links where permitted.

## APIs Used

- `GET /admin/v1/reports/analytics`
- `GET /admin/v1/analytics/tenants`
- `GET /admin/v1/analytics/subscriptions`
- `GET /admin/v1/analytics/modules`
