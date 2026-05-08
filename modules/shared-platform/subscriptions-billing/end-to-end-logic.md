# Subscriptions & Billing — End-to-End Logic

**Module:** Shared Platform
**Feature:** Subscriptions & Billing (Stripe + PayHere)

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

## Related

- [[modules/shared-platform/subscriptions-billing/overview|Overview]]
- [[modules/infrastructure/tenant-management/overview|Tenant Management]]
- [[frontend/cross-cutting/feature-flags|Feature Flags]]
- [[modules/shared-platform/notification-infrastructure/overview|Notification Infrastructure]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
