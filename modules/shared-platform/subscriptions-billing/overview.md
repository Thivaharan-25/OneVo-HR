# Subscriptions & Billing

**Module:** Shared Platform  
**Feature:** Subscriptions & Billing (Stripe + PayHere)

---

## Purpose

Plan definitions, module pricing, tenant subscriptions, invoices, AI token limits, Work Management storage limits, manual billing evidence, approved payment exception/grace periods, and payment methods. Integrated with Stripe and PayHere.

Stripe and PayHere are the primary Phase 1 payment gateways. The selected provider is stored as `gateway_provider` (`stripe` or `payhere`) on the tenant subscription/commercial setup. Gateway API keys, merchant secrets, and webhook secrets are stored through encrypted payment gateway configuration and must never be returned by API responses.

## Database Tables

### `subscription_plans`
NOT tenant-scoped. Fields: `name`, `code` (`starter`, `professional`, `enterprise`), `feature_limits` (jsonb), `included_modules` (jsonb), `company_size_range`, `calculated_monthly_price`, `calculated_annual_price`, optional `override_monthly_price`, optional `override_annual_price`, `ai_token_limit_per_month`, and `currency`.

Reusable plan prices are calculated from selected package/module price brackets and the selected company-size range. Overrides are stored separately from calculated prices.

### `module_catalog`
NOT tenant-scoped. Fields include `module_key`, `name`, `pillar`, `phase`, `pricing_unit`, `price_brackets` (jsonb), `full_license_price`, `maintenance_rate`, module-owned `permission_codes_json`, module limit flags such as `requires_ai_token_limit` and `requires_storage_limit`, and `is_active`.

Each permission belongs to exactly one module. The Developer Platform must show which module owns each permission and reject assigning one permission to multiple modules.

Example calculation: Core HR at `$3.50` for `51-200` employees plus Work Management at `$4.00` for `51-200` employees produces `$7.50 per employee`.

### `plan_features`
Per-plan feature inclusions: `feature_key`, `limit_value`, `is_included`.

### `tenant_subscriptions`
Active subscription/commercial record: `plan_id`, `billing_cycle`, `status`, `gateway_provider`, `gateway_customer_ref`, `gateway_subscription_ref`, selected company-size range, selected module keys, calculated price snapshots, monthly/annual/full-license/maintenance override prices, AI monthly token limit, Work Management storage limit, manual billing evidence/reference, and approved payment exception/grace dates.

Also stores trial and grace period fields snapshotted at tenant creation time:

| Field | Description |
|:------|:------------|
| `TrialStartDate` | Date the trial begins (set at tenant creation) |
| `TrialEndDate` | `TrialStartDate + trial_period_days`; the date payment first becomes required |
| `UnpaidGracePeriodDays` | How many days after going unpaid before suspension begins (plan default: 7) |
| `AccessEndsAt` | Computed date after which the tenant's access is suspended if unpaid |

#### Trial and grace period rules

- `trial_period_days` (plan default: 30): the free-access window for a new tenant before payment is required. If set to `0`, no trial is applied and the subscription status begins as `active` immediately.
- `unpaid_grace_period_days` (plan default: 7): once a tenant goes unpaid (past `TrialEndDate` or a missed recurring payment), this is how many days access continues before suspension or termination.
- **Both values are snapshotted onto `TenantSubscription` at tenant creation time.** Changes to the plan catalog — including changes to plan-level trial or grace period defaults — do NOT retroactively alter existing tenant contracts.
- The ONEVO operator may override either value per tenant during commercial selection.
- Approved payment exception/grace periods may also be set on the tenant commercial record for subscription or full-license/maintenance tenants. They are tenant-specific exceptions and are not retroactively changed by plan catalog updates.
- Manual subscription, license, or maintenance payments require billing evidence or an external reference plus an audit reason.
- AI-capable modules require a positive monthly token limit. Work Management storage-backed modules require a storage limit or selected plan default.

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
