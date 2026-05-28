# Subscriptions & Billing - End-to-End Logic

**Module:** Shared Platform
**Feature:** Subscriptions & Billing (Stripe + Paddle + PayHere)

---

## Tenant Commercial Boundary

Tenant profile creation, operator commercial boundary, and tenant owner subscription confirmation are separate steps. `POST /admin/v1/tenants` creates only the provisioning tenant profile. The ONEVO operator then saves allowed plans, gateway/manual collection method, setup charges, and negotiated terms. The tenant owner later chooses the final plan and billing cycle from the allowed boundary.

### Operator commercial boundary flow

```
PATCH /admin/v1/tenants/{id}/subscription
  -> TenantProvisioningService.SaveCommercialBoundaryAsync()
    -> 1. Resolve provisioning tenant profile
    -> 2. Store allowed plan ids and optional recommended plan id
    -> 3. Store operator-selected gateway_provider (`stripe`, `paddle`, `payhere`) or manual collection mode
    -> 4. Store one-time setup charges and negotiated overrides/discounts
    -> 5. Store AI token limit and Work Management storage limit when allowed plans require them
    -> 6. Do not finalize billing cycle or first invoice quantity, and do not create a trial
    -> Return tenantId + commercial boundary summary
```

Tenant owner invitation is not sent by this flow. Tenant creation does not create a trial.

### Tenant owner subscription confirmation flow

```
POST /api/v1/billing/subscription/confirm
  -> BillingController.ConfirmSubscription(ConfirmSubscriptionCommand)
    -> [RequirePermission("billing:manage")]
    -> 1. Validate selected plan is in operator-allowed plan ids
    -> 2. Validate selected billing_cycle is monthly or annual and supported by the plan
    -> 3. Validate confirmed_employee_count > 0
    -> 4. Snapshot selected plan, billing cycle, confirmed employee count, and billing contact
    -> 5. Calculate first invoice using confirmed employee count and selected billing cycle
    -> 6. Include approved one-time setup charges as separate line items
    -> 7. Initiate payment through the operator-selected gateway/manual collection path
    -> Return invoice/payment summary
```

First invoice calculation:

```
first_invoice_total =
  plan_rate_for_confirmed_employee_count
  * confirmed_employee_count
  * billing_cycle_multiplier
  + one_time_setup_charges
  - discounts_or_overrides
  + tax
```

The tenant owner is not asked to classify employees by monitoring, WorkSync, or package usage during first billing.
### One-time setup charges

One-time setup charges are managed separately from the subscription via the billing API. They represent charges for ONEVO operator configuration services and are **not** recurring fees.

```
POST /admin/v1/tenants/{tenantId}/billing/one-time-charges
  -> BillingService.CreateOneTimeChargeAsync()
    -> Validate tenantId and charge details
    -> INSERT one-time charge record with status "draft"
    -> Link to setup_option key if applicable
    -> Return charge record

PATCH /admin/v1/tenants/{tenantId}/billing/one-time-charges/{chargeId}
  -> Transition status: draft -> approved -> invoiced -> paid | void
```

Setup charges and the first subscription charge appear as **separate line items** on the same first invoice by default. The customer makes a single payment unless the signed contract explicitly requires setup-only prepayment.

---

## Get Current Subscription

### Flow

```
GET /api/v1/subscriptions/current
  -> SubscriptionController.GetCurrent()
    -> [RequirePermission("billing:read")]
    -> SubscriptionService.GetCurrentAsync(tenantId, ct)
      -> Query tenant_subscriptions WHERE tenant_id
      -> Include: plan details, billing cycle, status
      -> Return Result.Success(subscriptionDto)
```

## Upgrade Plan

### Flow

```
POST /api/v1/subscriptions/upgrade
  -> SubscriptionController.Upgrade(UpgradeCommand)
    -> [RequirePermission("billing:manage")]
    -> SubscriptionService.UpgradeAsync(command, ct)
      -> 1. Load current subscription
      -> 2. Validate new plan exists and is higher tier
      -> 3. Resolve operator-selected gateway_provider (stripe, paddle, or payhere) and gateway config
      -> 4. Call selected gateway API to update subscription
      -> 5. UPDATE tenant_subscriptions with new plan and gateway refs
      -> 6. Update feature_limits based on new plan
      -> Return Result.Success(updatedDto)

```

## Payment Gateway Configuration

```
GET /admin/v1/payment-gateways
POST /admin/v1/payment-gateways
PATCH /admin/v1/payment-gateways/{id}
  -> Supports provider = "stripe", "paddle", or "payhere"
  -> Stores API keys, merchant secrets, and webhook secrets encrypted
  -> Returns masked/public configuration only
```

## Commercial Rules

- Subscription tenants normally collect recurring payments through the operator-selected Stripe, Paddle, or PayHere gateway.
- Full-license tenants may record the one-time license payment manually.
- Full-license maintenance fees are separate from the license sale and should be collected through Stripe, Paddle, or PayHere when gateway collection is enabled.
- Manual subscription, full-license, or maintenance collection requires billing evidence/reference and an audit reason.
- Payment exception/grace periods can apply to subscription and full-license/maintenance tenants.
- AI-capable modules require a token limit; Work Management storage-backed modules require a storage limit.

## Related

- [[modules/shared-platform/subscriptions-billing/overview|Overview]]
- [[modules/infrastructure/tenant-management/overview|Tenant Management]]
- [[frontend/cross-cutting/feature-flags|Feature Flags]]
- [[modules/shared-platform/notification-infrastructure/overview|Notification Infrastructure]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]

