# Subscriptions & Billing

**Module:** Shared Platform  
**Feature:** Subscriptions & Billing (Stripe + PayHere)

---

## Purpose

Plan definitions, module pricing, tenant subscriptions, invoices, AI token limits, and payment methods. Integrated with Stripe and PayHere.

Stripe and PayHere are the primary Phase 1 payment gateways. The selected provider is stored as `gateway_provider` (`stripe` or `payhere`) on the tenant subscription/commercial setup. Gateway API keys, merchant secrets, and webhook secrets are stored through encrypted payment gateway configuration and must never be returned by API responses.

## Database Tables

### `subscription_plans`
NOT tenant-scoped. Fields: `name`, `code` (`starter`, `professional`, `enterprise`), `feature_limits` (jsonb), `included_modules` (jsonb), `company_size_range`, `calculated_monthly_price`, `calculated_annual_price`, optional `override_monthly_price`, optional `override_annual_price`, `ai_token_limit_per_month`, and `currency`.

Reusable plan prices are calculated from selected module price brackets and the selected company-size range. Overrides are stored separately from calculated prices.

### `module_catalog`
NOT tenant-scoped. Fields include `module_key`, `name`, `pillar`, `phase`, `pricing_unit`, `price_brackets` (jsonb), `full_license_price`, `maintenance_rate`, and `is_active`.

Example calculation: Core HR at `$3.50` for `51-200` employees plus Work Management at `$4.00` for `51-200` employees produces `$7.50 per employee`.

### `plan_features`
Per-plan feature inclusions: `feature_key`, `limit_value`, `is_included`.

### `tenant_subscriptions`
Active subscription: `plan_id`, `billing_cycle`, `status`, `gateway_provider`, `gateway_customer_ref`, `gateway_subscription_ref`, selected company-size range, selected module keys, calculated price snapshots, override prices, and AI monthly token limit.

### `subscription_invoices`
Synced from Stripe or PayHere: `invoice_number`, `amount`, `status` (`draft`, `open`, `paid`, `void`), gateway invoice/payment reference.

### `payment_methods`
Stored methods: `type` (`card`, `bank_transfer`), `last_four`, `brand`, `is_default`, gateway payment method reference.

### `payment_gateway_configs`
Gateway configuration for Stripe and PayHere. Stores provider, mode (`test`, `live`), public identifiers, merchant ID where applicable, encrypted secret/API key, encrypted webhook secret, webhook URL, default flag, and active flag.

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
