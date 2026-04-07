# Subscriptions & Billing — End-to-End Logic

**Module:** Shared Platform
**Feature:** Subscriptions & Billing (Stripe)

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
      -> 3. Call Stripe API to update subscription
      -> 4. UPDATE tenant_subscriptions with new plan
      -> 5. Update feature_limits based on new plan
      -> Return Result.Success(updatedDto)

```

## Related

- [[subscriptions-billing|Overview]]
- [[tenant-management]]
- [[feature-flags]]
- [[notification-infrastructure]]
- [[event-catalog]]
- [[error-handling]]
