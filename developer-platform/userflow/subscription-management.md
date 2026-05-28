# Subscription Management Userflow

## Actor

Billing or platform operator with subscription permissions.

## Reusable Plan Journey

1. Operator opens Platform Management -> Subscriptions.
2. Console loads subscription plans and product modules.
3. Operator creates or edits a reusable plan.
4. Operator selects included modules and the commercial features included inside each selected module.
5. Backend calculates prices from Module Catalog price brackets.
6. Operator saves plan; overrides require audit reason.

Commercial feature inclusion is part of the plan/custom contract. Feature flags can only control runtime rollout for features already included here; disabling features with Feature Flag Manager does not reduce the tenant's price.

## Payment Gateway Journey

1. Operator opens payment gateway settings.
2. Operator adds Paddle or PayHere credentials.
3. Backend encrypts secrets and returns safe metadata only.

## Tenant Commercial Assignment

Tenant-specific commercial terms are applied from Tenant Console through:

- `PATCH /admin/v1/tenants/{id}/subscription`

## APIs Used

- `GET /admin/v1/subscription-plans`
- `POST /admin/v1/subscription-plans`
- `PATCH /admin/v1/subscription-plans/{id}`
- `GET /admin/v1/payment-gateways`
- `POST /admin/v1/payment-gateways`
- `PATCH /admin/v1/payment-gateways/{id}`
- `GET /admin/v1/subscription-invoices`
- `GET /admin/v1/tenants/{id}/subscription`
- `PATCH /admin/v1/tenants/{id}/subscription`
