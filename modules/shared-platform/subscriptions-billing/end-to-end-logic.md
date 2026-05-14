# Subscriptions & Billing — End-to-End Logic

**Module:** Shared Platform
**Feature:** Subscriptions & Billing (Stripe + PayHere)

---

## Tenant Commercial Selection

Tenant profile creation and commercial selection are separate steps. `POST /admin/v1/tenants` creates only the provisioning tenant profile. The operator then saves commercial terms through `PATCH /admin/v1/tenants/{id}/subscription`.

### Subscription bootstrap flow

```
PATCH /admin/v1/tenants/{id}/subscription
  -> TenantProvisioningService.SaveCommercialTermsAsync()
    -> 1. Resolve provisioning tenant profile
    -> 2. Resolve plan from plan_id; snapshot trial_period_days, unpaid_grace_period_days, payment exception/grace dates, selected modules, and commercial limits
         (operator-supplied values override plan defaults)
    -> 3. INSERT/UPDATE tenant_subscriptions with status:
         - "trialing" if trial_period_days > 0
         - "active"   if trial_period_days = 0
         TrialStartDate = now, TrialEndDate = now + trial_period_days
    -> 4. Store calculated monthly/annual/full-license/maintenance snapshots and any overrides
    -> 5. Store AI token limit and Work Management storage limit when selected modules require them
    -> 6. Store billing evidence file/reference for manual payment modes
    -> Return tenantId + subscription summary
```

Tenant owner invitation is not sent by this flow.

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

Setup charges and recurring subscription charges appear as **separate line items** on the same invoice. The customer makes a single payment for both — there are no two separate payments.

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
      -> 3. Resolve gateway_provider (stripe or payhere) and gateway config
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
  -> Supports provider = "stripe" or "payhere"
  -> Stores API keys, merchant secrets, and webhook secrets encrypted
  -> Returns masked/public configuration only
```

## Commercial Rules

- Subscription tenants normally collect recurring payments through Stripe or PayHere.
- Full-license tenants may record the one-time license payment manually.
- Full-license maintenance fees are separate from the license sale and should be collected through Stripe or PayHere when gateway collection is enabled.
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
