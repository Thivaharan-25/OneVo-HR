# Subscriptions & Billing

**Module:** Shared Platform  
**Feature:** Subscriptions & Billing (Stripe)

---

## Purpose

Plan definitions, tenant subscriptions, invoices, and payment methods. Integrated with Stripe.

## Database Tables

### `subscription_plans`
NOT tenant-scoped. Fields: `name`, `code` (`starter`, `professional`, `enterprise`), `feature_limits` (jsonb), `monthly_price`, `annual_price`.

### `plan_features`
Per-plan feature inclusions: `feature_key`, `limit_value`, `is_included`.

### `tenant_subscriptions`
Active subscription: `plan_id`, `billing_cycle`, `status`, `payment_provider_ref` (Stripe ID).

### `subscription_invoices`
Synced from Stripe: `invoice_number`, `amount`, `status` (`draft`, `open`, `paid`, `void`).

### `payment_methods`
Stored methods: `type` (`card`, `bank_transfer`), `last_four`, `brand`, `is_default`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/subscriptions/current` | `billing:read` | Current subscription |
| POST | `/api/v1/subscriptions/upgrade` | `billing:manage` | Upgrade plan |

## Related

- [[modules/shared-platform/overview|Shared Platform Module]]
- [[modules/infrastructure/tenant-management/overview|Tenant Management]]
- [[frontend/cross-cutting/feature-flags|Feature Flags]]
- [[modules/shared-platform/compliance-governance/overview|Compliance Governance]]
- [[modules/shared-platform/notification-infrastructure/overview|Notification Infrastructure]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[database/migration-patterns|Migration Patterns]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]]
