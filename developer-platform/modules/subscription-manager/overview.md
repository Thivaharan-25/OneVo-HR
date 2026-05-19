# Subscription Manager

## Purpose

Subscription Manager maintains the global commercial catalog: reusable subscription plans, payment gateway configurations, invoice records, and billing lifecycle management. It provides the catalog data that Tenant Console reads during tenant provisioning and subscription override.

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `subscription_plans` | Read + write — reusable global plan definitions |
| `subscription_plan_price_brackets` | Read + write — per-plan, per-size-range pricing |
| `subscription_plan_price_history` | Write — immutable price change audit trail |
| `payment_gateways` | Read + write — Paddle/PayHere gateway configs with encrypted secrets |
| `tenant_subscriptions` | Read — current tenant commercial state; write through tenant subscription APIs only |
| `subscription_invoices` | Read + write — invoice lifecycle management |
| `webhook_event_queue` | Read — webhook processing status |
| `module_catalog` | Read — module pricing for plan price calculation |
| Audit log | Write every billing action |

## Phase 1 Sellable Modules (for plan creation)

Plans are built from Phase 1 modules only. Phase 2 modules (`payroll`, `performance`, `skills`, `learning`, `recruitment`, `hr_docs`, `grievance`, `expense`) are rejected by plan creation validators.

| Group | Module Keys | Notes |
|:---|:---|:---|
| HR Core (Package 1) | `core_hr`, `leave`, `calendar` | |
| Intelligence (Package 1) | `monitoring`, `workforce`, `verification`, `exceptions`, `analytics` | |
| WorkSync (Package 2) | `work_management`, `chat`, `chat_ai`, `documents`, `reports`, `integrations` | `chat` and `chat_ai` are separately sellable |
| Foundation (always included) | `auth`, `configuration`, `roles`, `notifications`, `org`, `workflow_engine` | Not selectable in plans — auto-included |

`chat` and `chat_ai` are **separately sellable** — a plan can include one, both, or neither. `chat_ai` requires a positive `ai_token_limit_per_month`.

## Capabilities

### Subscription Plans
- Create reusable plans from Phase 1 modules with company-size bracket pricing
- Select modules → set unit price per module per size range → calculated monthly total shown live
- Store calculated price and operator override separately for audit
- Set commercial model support (Subscription, Full License + Maintenance), billing cycles, collection modes, trial terms
- Clone plans; deactivate plans without affecting existing tenant assignments

### Payment Gateway Configuration
- Configure Paddle or PayHere gateway credentials with encrypted secrets (AES-256)
- Verify account credentials against provider before saving
- Upload gateway logo for display in provisioning Step 3 dropdown
- Rotate secrets atomically
- Country-code filtering: gateway dropdown in tenant provisioning shows only gateways matching the tenant's country

### Invoice Management
- View all invoices across all tenants with status, amount, and payment method
- Mark manual invoices as paid with evidence reference
- Void open invoices
- Download invoice PDFs

### Dunning
- Paddle/PayHere payment failures trigger automatic retry schedule (3 retries over ~17 days)
- After final retry fails: Critical alert raised; 7-day grace period before auto-suspension
- Payment exceptions halt dunning for tenants in approved grace periods

### Webhook Processing
- Paddle: `transaction.completed`, `transaction.payment_failed`, `subscription.past_due`, `subscription.canceled`, `transaction.refunded`, `dispute.created` — HMAC-SHA256 signature verification
- PayHere: notify callback with MD5 signature verification
- All events processed asynchronously via `webhook_event_queue` with at-least-once delivery and dead-letter handling

## Navigation

| Route | Permission |
|---|---|
| `/platform/subscriptions` | `platform.subscriptions.read` |
| Write operations | `platform.subscriptions.manage` |
| Gateway read | `platform.payment_gateways.read` |
| Gateway write | `platform.payment_gateways.manage` |

## Key Rules

- Updating a plan's pricing does NOT rewrite existing tenant subscription snapshots
- Gateway secrets are AES-256 encrypted — never returned by any API response
- Manual collection requires billing evidence/reference and an audit reason
- `chat_ai` module in a plan requires the operator to set an AI token limit during tenant provisioning
- Dunning auto-suspension is logged as a system action; platform admins can halt it via payment exception

## Related

- [[developer-platform/modules/subscription-manager/end-to-end-logic|Subscription Manager End-to-End Logic]]
- [[developer-platform/modules/tenant-console/overview|Tenant Console]] — applies plans to tenants
- [[developer-platform/modules/module-catalog-manager/overview|Module Catalog Manager]] — module pricing used in plan calculation
- [[developer-platform/modules/system-config/overview|System Config]] — payment gateway credential management
