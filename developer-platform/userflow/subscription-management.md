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

Commercial feature inclusion is part of the plan/custom contract. Feature flags can only control runtime rollout for features already included here; disabling features with Tenant Runtime Overrides does not reduce the tenant's price.

A subscription plan may include a module without including every feature key registered under that module in Module Catalog. `included_feature_keys` is the plan's reusable commercial feature package. Existing tenant subscription snapshots keep their stored commercial terms when Module Catalog or Subscription Plan records change, unless a migration/reprice operation is explicitly run.

Optional module add-ons belong under subscription plans and can create additional module entitlements plus the feature keys packaged with that add-on. Resource-only add-ons also belong under subscription plans, but they only change shared limits such as storage or AI tokens; they must not create module entitlements or write `selected_feature_keys`.

## Payment Gateway Journey

1. Operator opens payment gateway settings.
2. Operator adds Paddle or PayHere credentials.
3. Backend encrypts secrets and returns safe metadata only.

## Tenant Commercial Assignment

Tenant-specific commercial terms are applied from Tenant Management through:

- `PATCH /admin/v1/tenants/{id}/subscription`

This tenant subscription update is the commercial override path. It can change selected plan, selected optional module add-ons, selected resource-only add-ons, selected feature keys, prices, resource limits, and audit reason. Runtime overrides must not be used as a substitute for this commercial update.

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
