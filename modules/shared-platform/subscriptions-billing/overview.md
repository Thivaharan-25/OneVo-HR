# Subscriptions & Billing

**Module:** Shared Platform  
**Feature:** Subscriptions & Billing (Stripe + Paddle + PayHere)

---

## Purpose

Plan definitions, module pricing, tenant subscription confirmation, invoices, AI token limits, Work Management storage limits, manual billing evidence, payment exception/grace periods, and payment methods. Integrated with Stripe, Paddle, and PayHere.

Stripe, Paddle, and PayHere are supported payment gateways. The selected provider is chosen by the ONEVO operator in Developer Platform and stored as `gateway_provider` (`stripe`, `paddle`, or `payhere`) on the tenant commercial setup. Tenant owners do not choose the gateway or manual collection mode. Gateway API keys, merchant secrets, and webhook secrets are stored through encrypted payment gateway configuration and must never be returned by API responses.

## Database Tables

### `subscription_plans`
NOT tenant-scoped. Fields: `name`, `code` (`starter`, `professional`, `enterprise`), `feature_limits` (jsonb), `included_modules` (jsonb), price tiers/rate table, optional `override_monthly_price`, optional `override_annual_price`, `ai_token_limit_per_month`, and `currency`.

Reusable subscription plans define feature/module bundles and pricing rules. Company-size/employee-count tiers live inside the subscription plan pricing table; they are not module configuration and not separate plan identities. Confirmed employee count selects the applicable pricing tier and first invoice quantity. Overrides are stored separately from calculated prices.

### `module_catalog`
NOT tenant-scoped. Fields include `module_key`, `name`, `pillar`, `phase`, `pricing_unit`, `price_brackets` (jsonb), `full_license_price`, `maintenance_rate`, module limit flags such as `requires_ai_token_limit` and `requires_storage_limit`, and `is_active`.

Permission ownership is stored in `module_permission_ownership`. Each seeded permission belongs to exactly one module. The Developer Platform must show which module owns each permission and reject assigning one permission to multiple modules.

Example first-invoice calculation: Professional plan rate for the `51-200` employee tier is `$7.50 per employee`; tenant owner confirms `120` employees; monthly subscription line is `120 * $7.50`.

### `plan_features`
Per-plan feature inclusions: `feature_key`, `limit_value`, `is_included`.

### `tenant_subscriptions`
Active subscription/commercial record: operator-allowed plan ids, tenant-selected `plan_id`, tenant-selected `billing_cycle`, `status`, `gateway_provider`, `gateway_customer_ref`, `gateway_subscription_ref`, confirmed employee-count snapshot, selected module keys, calculated price snapshots, monthly/annual/full-license/maintenance override prices, AI monthly token limit, Work Management storage limit, manual billing evidence/reference, and approved payment exception/grace dates.

#### Tenant creation and first-billing rules

- Tenant creation does not create a trial.
- Developer Platform operator selects allowed plans, optional recommended plan, gateway/manual collection method, setup charges, and negotiated overrides.
- Tenant owner selects the final plan from the allowed list, chooses monthly or annual billing, confirms total employee count, and confirms billing contact details.
- First invoice quantity is the tenant-owner-confirmed total employee count, not monitoring employees or WorkSync employees.
- Future recurring invoices may use system snapshots after onboarding/import.
- Manual subscription, license, or maintenance payments require billing evidence or an external reference plus an audit reason.
- AI-capable modules require a positive monthly token limit. Work Management storage-backed modules require a storage limit or selected plan default.

### `subscription_invoices`
Synced/generated from Stripe, Paddle, PayHere, or manual collection: `invoice_number`, `amount`, `status` (`draft`, `open`, `paid`, `void`), gateway invoice/payment reference.

### `payment_methods`
Stored methods: `type` (`card`, `bank_transfer`), `last_four`, `brand`, `is_default`, gateway payment method reference.

### `payment_gateway_configs`
Gateway configuration for Stripe, Paddle, and PayHere. Stores provider, mode (`test`, `live`), public identifiers, merchant ID/seller ID where applicable, encrypted secret/API key, encrypted webhook secret, webhook URL, default flag, and active flag.
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

