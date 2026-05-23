# Subscription Manager — End-to-End Logic

## Purpose

Subscription Manager maintains the global commercial catalog: reusable subscription plans, payment gateway configurations, invoice records, and commercial rules. It does not directly assign subscriptions to tenants — that is done through Tenant Console. Subscription Manager provides the catalog data that Tenant Console reads during provisioning and override.

**Route:** `/platform/subscriptions`
**Permission to access:** `platform.subscriptions.read`

---

## Screen Layout

Left sidebar navigation within the module:
- Plans (default view)
- Payment Gateways
- Invoices
- Pricing History

---

## Plans Screen

### Page Header

| Element | Value |
|---|---|
| Title | "Subscription Plans" |
| Subtitle | "Manage reusable subscription plan templates. Plans are assigned to tenants during provisioning." |
| Create Plan button | `+ Create Plan` — visible to accounts with `platform.subscriptions.manage` |

### Plans Table

**API:** `GET /admin/v1/subscription-plans?page={n}&per_page={n}&search={q}&is_active={true|false}`

| Column | Description | Sortable |
|---|---|---|
| Plan Name | Display name, e.g. "Enterprise", "Business", "Professional" | Yes |
| Tier | Badge: Enterprise / Business / Professional / Custom | Yes |
| Included Modules | Count of modules included, e.g. "12 modules" | No |
| Company Size Range | Target company size, e.g. "201-1,000 employees" | Yes |
| Base Monthly Price | Calculated price for the target size range | Yes |
| Active | Toggle — yes/no | Yes |
| Tenants Using | Count of active tenants on this plan | Yes |
| Created | Date | Yes |
| Actions | Edit, Clone, Deactivate | No |

---

## Create Reusable Plan — Full Field Specification

### How to Open

Plans table → `+ Create Plan` button → opens full-page form (not modal — too much content).

### Section 1: Plan Identity

| Field | Label | Type | Required | Validation | Notes |
|---|---|---|---|---|---|
| Plan Name | "Plan Name" | Text input | Yes | 2–80 chars, unique across active plans | e.g., "Enterprise 2025" |
| Plan Tier | "Plan Tier" | Dropdown: Enterprise / Business / Professional / Custom | Yes | | Determines sort order in provisioning wizard plan dropdown |
| Description | "Plan Description" | Textarea | No | Max 500 chars | Shown to operators in plan selection dropdown |
| Is Active | "Active" | Toggle | Yes | | Inactive plans cannot be selected during new provisioning but existing tenant assignments are preserved |

### Section 2: Target Company Size

| Field | Label | Type | Required | Validation | Notes |
|---|---|---|---|---|---|
| Company Size Range | "Target Company Size" | Multi-select checkboxes | Yes | At least one size range required | Determines which price brackets apply — different sizes have different prices |

Company size options: `1-10`, `11-50`, `51-200`, `201-500`, `501-1000`, `1001-5000`, `5000+`

**Rule:** A plan can target multiple company sizes. Each selected size range gets its own price bracket row in Section 4.

### Section 3: Included Modules

Module checklist grouped by ONEVO product pillar. Each module row shows:
- Checkbox (included in plan or not)
- Module name
- Pillar badge
- Pricing unit (per employee / per device / per user / flat rate / per seat)
- Base unit price from `module_catalog`

**Foundation Modules — Always Included (no separate cost, not sellable individually)**
| Module Key | Module Name | Notes |
|---|---|---|
| `auth` | Authentication & Authorization | Always included — no pricing unit |
| `configuration` | Tenant Configuration & Settings | Always included |
| `roles` | Roles & Permissions | Always included |
| `notifications` | Notifications | Always included |
| `org` | Organisation Structure | Always included |

**Package 1 — HR Core (sellable)**
| Module Key | Module Name | Pricing Unit |
|---|---|---|
| `core_hr` | Core HR (Profile Management) | Per employee |
| `leave` | Attendance & Leave Management | Per employee |
| `calendar` | Calendar | Per employee |

**Package 1 — Intelligence (sellable)**
| Module Key | Module Name | Pricing Unit |
|---|---|---|
| `monitoring` | E2E Monitoring (Activity Monitoring) | Per monitored employee (user-based; no device billing) |
| `workforce` | Workforce Presence | Per enrolled employee |
| `verification` | Identity Verification | Per enrolled employee |
| `exceptions` | Exception Detection | Per active rule |
| `analytics` | Productivity & Performance Analytics | Per employee |

> **Billing rule:** Users with monitoring fully disabled are excluded from the Package 1 billable seat count at the monthly snapshot. Billing is user-based only — there is no device count billing.

**Package 2 — Work Management (sellable — all sold independently)**
| Module Key | Module Name | Pricing Unit | AI Required |
|---|---|---|---|
| `work_management` | Project Management (WorkSync — projects, tasks, sprints, OKR, roadmaps, GitHub integration) | Per active user | No |
| `chat` | Chat (no AI — basic messaging, channels, threads) | Per active user | No |
| `chat_ai` | Agentic Chat (AI-powered — requires AI provider config to be set) | Per active user + AI token limit | Yes |
| `integrations` | Third Party Integrations (Microsoft 365, Teams, Slack, Google Workspace) | Flat rate | No |

> **Chat independence rule:** `chat` and `chat_ai` are separate sellable modules. A plan can include one, both, or neither:
> - `chat` only → basic messaging, no AI assistant
> - `chat_ai` only → AI chat only (no basic channels unless `chat` also included)
> - Both → full chat with AI assistant as an optional mode
> - Neither → no chat at all
>
> `chat_ai` cannot function without an active AI provider config for the `agentic_chat` purpose in System Config. If `chat_ai` is entitled for a tenant but no AI config exists, the Agentic Chat feature shows a configuration-required error — it does not fall back to basic chat.
>
> A subscription plan that includes `chat_ai` automatically requires the operator to set an AI token limit during Step 3 of the provisioning wizard.

> **Phase 2 Modules — NOT available in Phase 1:**
> The following modules are out of scope for Phase 1 and must NOT appear in plans, the module catalog sellable list, or tenant provisioning options: `payroll`, `performance` (standalone), `skills`, `learning`, `recruitment`, `hr_docs`, `grievance`, `expense`, `documents`, `reports`.
> They exist in the module catalog with `is_active = false` and `phase = 2`. Do not seed them as sellable options.

**AI Capability toggle:**
| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| AI Capabilities | "Include AI Capabilities" | Toggle | No | When enabled, plan requires AI token limit to be set per tenant; enables AI Insights Engine features |
| Default AI Token Limit | "Default Monthly AI Token Limit" | Number input | Yes (when AI toggled on) | Suggested default when operator assigns this plan; can be overridden per tenant |
| Min AI token limit | Min 1,000 tokens | | | |
| Max AI token limit | Max 100,000,000 tokens | | | |

**Tenant Storage (plan default):**
| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| Default Tenant Storage | "Default Tenant Storage Limit (GB)" | Number input | Yes | Suggested default for tenants on this plan. Storage is a **single shared pool for the entire tenant** — not split per module. Operator can override per tenant during provisioning Step 3. |

> **Storage rule:** `tenant_storage_limit_gb` applies to all modules — uploaded files, HR documents, screenshots, payslips, verification photos, attachments. Never create per-module storage limits.

### Section 4: Pricing Brackets

For each company size range selected in Section 2, a pricing bracket row is generated. Each bracket defines the unit prices for all selected modules at that size range.

**Price bracket row (one per selected company size):**

| Field | Description | Type | Required |
|---|---|---|---|
| Size Range label | Read-only, e.g. "51–200 employees" | Display | N/A |
| Monthly total (calculated) | Sum of all selected module prices × bracket multiplier | Display — auto-calculated | N/A |
| Per-module price cells | One input per selected module — unit price at this size range | Currency input | Yes per module |
| Override monthly total | Operator-entered flat monthly total for this bracket instead of per-module sum | Currency input | No |
| Override reason | Required if override entered | Textarea | Conditional |

**Price bracket calculation rule:**
```
monthly_total = SUM(module_unit_price × applicable_quantity_for_size_range)

For per-employee modules: quantity = midpoint of size range (e.g. for "51-200" = 125)
For flat rate modules:     quantity = 1
For per-active-user modules: quantity = company_size_midpoint × 0.6 (assumed 60% active)
```

> **No per-device pricing.** Billing is user-based only. Do not create per-device price brackets or per-device quantity estimates.

The calculated total is shown in real-time as prices are entered. Operators may override the total with a flat amount per bracket — override and calculated prices are stored separately.

### Section 5: Billing Options

| Field | Label | Type | Required | Options | Notes |
|---|---|---|---|---|---|
| Supported Commercial Models | "Supported Commercial Models" | Multi-select checkboxes | Yes | Subscription, Full License + Maintenance | Determines which commercial models operators can choose when assigning this plan |
| Supported Billing Cycles | "Supported Billing Cycles" | Multi-select checkboxes (shown only if Subscription selected) | Yes when Subscription | Monthly, Annual | Annual may include a configured discount percentage |
| Annual Discount | "Annual Discount (%)" | Number input 0–50 | No | | Discount applied to monthly price × 12 for annual billing |
| Supported Collection Modes | "Supported Collection Modes" | Multi-select | Yes | Gateway, Manual | Whether this plan is sold via gateway or manual billing |
| Trial Allowed | "Allow Trial Period" | Toggle | No | | Enables trial assignment for tenants on this plan |
| Trial Duration | "Default Trial Duration (days)" | Number input | Yes when Trial toggled | 1–365 | |

### Create Plan API Call

**Endpoint:** `POST /admin/v1/subscription-plans`

**Request body:**
```json
{
  "name": "Enterprise 2025",
  "tier": "enterprise",
  "description": "Full-access enterprise plan with all HR, WI, and WorkSync modules.",
  "is_active": true,
  "target_company_size_ranges": ["201-500", "501-1000", "1001-5000"],
  "included_module_keys": ["core_hr", "leave", "calendar", "monitoring", "workforce", "verification", "exceptions", "analytics", "work_management", "chat_ai"],
  "ai_capabilities": true,
  "default_ai_monthly_token_limit": 1000000,
  "default_tenant_storage_limit_gb": 500,
  "price_brackets": [
    {
      "company_size_range": "201-500",
      "module_prices": {
        "core_hr": 8.00,
        "leave": 3.00,
        "calendar": 1.00,
        "monitoring": 6.00,
        "workforce": 4.00,
        "verification": 2.00,
        "exceptions": 2.00,
        "analytics": 3.00,
        "work_management": 5.00,
        "chat_ai": 4.00
      },
      "calculated_monthly_total": 8750.00,
      "override_monthly_total": null,
      "override_reason": null
    }
  ],
  "supported_commercial_models": ["subscription", "full_license_maintenance"],
  "supported_billing_cycles": ["monthly", "annual"],
  "annual_discount_pct": 10,
  "supported_collection_modes": ["gateway", "manual"],
  "trial_allowed": true,
  "default_trial_duration_days": 30
}
```

**Response (201 Created):**
```json
{
  "plan_id": "plan-enterprise-2025-v1",
  "name": "Enterprise 2025",
  "created_at": "2025-05-20T10:00:00Z"
}
```

**Error responses:**

| HTTP | Code | Condition |
|---|---|---|
| 409 | `plan_name_taken` | Active plan with same name already exists |
| 422 | `no_modules_selected` | At least one module must be included |
| 422 | `missing_price_brackets` | Price bracket required for each selected company size range |
| 422 | `ai_limit_required` | AI token limit required when AI capabilities enabled |

---

## Update Existing Plan — Field Behavior

**Endpoint:** `PATCH /admin/v1/subscription-plans/{id}`

**Critical rule:** Updating a plan does NOT retroactively change any tenant's commercial snapshot. Existing tenant subscriptions reference the plan ID but their pricing snapshot (`tenant_subscriptions.snapshot_module_keys`, `snapshot_calculated_price`) was taken at assignment time and is immutable.

**What changes when a plan is updated:**
- New tenants provisioned after the update get the new price brackets
- The Tenant Console "Stale pricing" warning appears on existing tenants whose snapshot price differs from the current plan price — operators can choose to re-price manually
- `subscription_plan_price_history` table records the change with `changed_by_id` and `changed_at`

**Fields that cannot be changed after plan has active tenant assignments:**
- `tier` — would break tier-based filtering logic
- `name` — can be changed but all audit logs retain the name at time of assignment

**Fields that can always be changed:**
- Price brackets (creates price history entry)
- Description
- Included modules (only adding — removing modules from plan does not remove entitlements from existing tenants)
- AI/storage defaults
- Is active (deactivation prevents new assignments; existing assignments unaffected)

---

## Payment Gateway Configuration — Full Field Specification

**Route:** `/platform/subscriptions/gateways`

**Purpose:** Store encrypted payment gateway credentials for Paddle and PayHere. These credentials are used when the system automatically charges tenants or when the operator records gateway references for manually-managed payments.

**Gateway routing rule:** Tenant country = `LKA` (Sri Lanka) → PayHere. All other countries → Paddle. This is enforced at provisioning Step 3 via `country_codes` filtering on each gateway config.

### Gateway List Screen

| Column | Description |
|---|---|
| Provider | "Paddle" or "PayHere" with logo |
| Name | Display name, e.g. "Paddle Global Production" |
| Country Codes | Country flags + codes where gateway is used |
| Environment | Badge: Production (green) / Sandbox (yellow) |
| Is Active | Toggle |
| Created | Date |
| Actions | Edit, Rotate Secrets, Deactivate |

**Rule:** Secrets are never shown in list or detail views — only non-secret metadata is displayed. Rotating secrets requires the full new secret value; partial updates to encrypted fields are not permitted.

### Create Payment Gateway — Fields

| Field | Label | Type | Required | Validation | Notes |
|---|---|---|---|---|---|
| Provider | "Payment Provider" | Radio: Paddle / PayHere | Yes | | Determines which credential fields appear |
| Display Name | "Display Name" | Text input | Yes | 2–80 chars | e.g., "Paddle Global Production" |
| Country Codes | "Applicable Countries" | Multi-select tag input (ISO codes) | Yes | Valid ISO 3166-1 alpha-2 codes | Countries where this gateway is offered to tenants |
| Environment | "Environment" | Radio: Sandbox / Production | Yes | | |
| Is Active | "Active" | Toggle | Yes | Default: On | |

**Paddle-specific fields (shown when Provider = Paddle):**

| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| API Key | "Paddle API Key" | Password input | Yes | Never returned by API after save |
| Seller ID | "Paddle Seller ID" | Text input | Yes | Numeric seller ID from Paddle dashboard |
| Webhook Secret | "Paddle Webhook Secret" | Password input | Yes | Used to verify `Paddle-Signature` header (HMAC-SHA256) |

**PayHere-specific fields (shown when Provider = PayHere):**

| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| Merchant ID | "PayHere Merchant ID" | Text input | Yes | |
| Merchant Secret | "PayHere Merchant Secret" | Password input | Yes | Never returned after save |
| Webhook Secret | "PayHere Webhook Secret" | Password input | Yes | Used to verify incoming webhook notify_url signatures |

### Create Gateway API Call

**Endpoint:** `POST /admin/v1/payment-gateways`

**Request body:**
```json
{
  "provider": "paddle",
  "name": "Paddle Global Production",
  "country_codes": ["GB", "US", "AU", "IN"],
  "environment": "production",
  "is_active": true,
  "credentials": {
    "api_key": "pdl_live_...",
    "seller_id": "12345",
    "webhook_secret": "pdl_ntfset_..."
  }
}
```

**The `credentials` object is AES-256 encrypted before storage.** The API never returns the `credentials` object — only safe metadata fields are returned.

**Response (201 Created):**
```json
{
  "gateway_id": "gw-paddle-global-prod",
  "provider": "paddle",
  "name": "Paddle Global Production",
  "country_codes": ["GB", "US", "AU", "IN"],
  "environment": "production",
  "is_active": true,
  "created_at": "2025-05-20T10:00:00Z"
}
```

### Rotate Gateway Secrets

**Endpoint:** `PATCH /admin/v1/payment-gateways/{id}/rotate-secrets`

Rotation requires the full new credential object — not a partial update. All encrypted fields are replaced atomically.

**Request body:**
```json
{
  "credentials": {
    "api_key": "pdl_live_NEW_...",
    "seller_id": "12345",
    "webhook_secret": "pdl_ntfset_NEW_..."
  },
  "rotation_reason": "Quarterly secret rotation per security policy."
}
```

---

## Invoice Lifecycle — Full Specification

### Invoice States

| Status | Color | Meaning |
|---|---|---|
| Draft | Gray | Invoice generated but not yet finalized — editable |
| Open | Blue | Invoice finalized, sent to tenant or recorded — awaiting payment |
| Paid | Green | Payment received and confirmed |
| Overdue | Red | Payment due date passed without payment |
| Void | Gray | Invoice cancelled — no payment expected |
| Uncollectible | Dark red | Debt written off — tenant commercial issue |
| Partially Refunded | Orange | Paddle issued a partial refund — original amount not fully returned |

### Invoice Generation Trigger

**For Paddle tenants (international):**

Paddle is Merchant of Record — Paddle owns billing cycle and tax. ONEVO creates the Paddle subscription at provisioning; Paddle charges automatically on each renewal date.

1. At provisioning, `InvoiceGenerationJob` creates a Paddle customer + subscription via Paddle Billing API (`POST /customers`, `POST /subscriptions`)
2. Paddle stores `paddle_customer_id` and `paddle_subscription_id` on `tenant_subscriptions`
3. On each billing date, Paddle charges the customer automatically — ONEVO does not initiate the charge
4. Paddle sends `transaction.completed` webhook → ONEVO creates/updates `subscription_invoices` record, status → `paid`
5. Tax: Paddle calculates and remits VAT/GST automatically — `tax_amount` is synced from Paddle transaction data, ONEVO does not calculate it
6. Invoice PDF: hosted by Paddle; ONEVO stores the Paddle invoice URL for display in tenant portal

**For PayHere tenants (Sri Lanka):**

ONEVO owns billing cycle. Invoice generated and charge initiated locally.

1. On `billing_start_date`, `InvoiceGenerationJob` reads `tenant_subscriptions` where `next_billing_date = today` and `gateway = payhere`
2. Generates invoice with:
   - Line items per selected module (module name, unit price, quantity, line total)
   - Subtotal = sum of line items
   - If override price exists: override total replaces calculated total (override noted on invoice)
   - `tax_amount = 0` for Phase 1 (Sri Lanka — no VAT on SaaS subscription services)
   - Grand total
3. Invoice status → `open`
4. PayHere payment initiated via PayHere Recurring API; awaits webhook callback

**For subscription tenants with manual collection:**
1. Invoice generated same way — status → `open`
2. No automatic charge
3. Invoice PDF generated and (optionally) emailed to tenant primary contact
4. Operator must manually mark payment received: `PATCH /admin/v1/invoices/{id}/mark-paid`

**For full-license tenants:**
1. One-time license invoice generated at provisioning
2. Recurring maintenance invoices generated on `maintenance_renewal_date` annually

### Invoice Fields

| Field | Description |
|---|---|
| `invoice_number` | Auto-generated: `INV-{tenant_code}-{YYYYMM}-{seq}` |
| `tenant_id` | Tenant this invoice belongs to |
| `plan_id` | Plan at time of invoice generation |
| `billing_period_start` | Start of the billing cycle |
| `billing_period_end` | End of the billing cycle |
| `line_items` | JSON array of `{module_key, module_name, unit_price, quantity, pricing_unit, line_total}` |
| `subtotal` | Sum of line items |
| `calculated_price` | What the price brackets calculated |
| `override_price` | If operator set an override — shown separately for audit |
| `effective_price` | `override_price ?? calculated_price` |
| `tax_amount` | Tax if applicable |
| `total` | `effective_price + tax_amount` |
| `currency` | ISO currency code |
| `status` | Invoice state from catalog above |
| `due_date` | `invoice_generated_at + 30 days` for manual; immediate for gateway |
| `paid_at` | Timestamp when payment confirmed |
| `payment_method` | `paddle`, `payhere`, `manual`, `waived` |
| `payment_reference` | External reference for manual payments |
| `paddle_transaction_id` | Paddle transaction ID when gateway = paddle — idempotency key |
| `paddle_invoice_url` | Paddle-hosted invoice PDF URL when gateway = paddle |
| `gateway_charge_id` | PayHere charge ref when gateway = payhere |

---

## Paddle Webhook Handling — Full Specification

Paddle sends webhook events to `POST /webhooks/paddle`. The backend must:
1. Parse `Paddle-Signature` header: format is `ts={timestamp};h1={signature}`
2. Verify HMAC-SHA256 signature: `HMAC(webhook_secret, ts + ":" + raw_body)`
3. Reject with `400` if signature invalid or timestamp > 5 seconds old — do not process
4. Respond `200` immediately upon signature validation — process asynchronously
5. Use `paddle_transaction_id` as idempotency key — ignore duplicate events

### Handled Paddle Events

| Paddle Event | ONEVO Action | DB State Change |
|---|---|---|
| `transaction.completed` | Create/sync invoice as Paid | `invoice.status = 'paid'`, `invoice.paid_at = now()`, `invoice.paddle_transaction_id` set, `invoice.paddle_invoice_url` set |
| `transaction.payment_failed` | Record failure, increment retry count | `invoice.payment_attempt_count++`, Warning alert `billing.payment_failed` if attempt_count = 1 |
| `subscription.activated` | Confirm subscription active | `tenant_subscriptions.status = 'active'` |
| `subscription.updated` | Sync subscription state if Paddle-side change detected | Log mismatch, raise Warning alert for operator review |
| `subscription.canceled` | Raise Critical alert | `billing.subscription_expired` Critical alert created |
| `subscription.past_due` | After repeated failures → raise Critical alert | `billing.payment_failed_final` Critical alert; `invoice.status = 'overdue'` |
| `subscription.trialing` | Confirm trial active | `tenant_subscriptions.status = 'trialing'` |
| `transaction.refunded` | Record refund | `invoice.refund_amount`, `invoice.refunded_at` updated |
| `dispute.created` | Raise Warning alert for dispute review | Warning alert: "Payment disputed by customer bank" |

### Paddle Webhook Retry / Idempotency

- ONEVO returns `200` immediately on signature validation — Paddle does not retry if we return `200`
- If processing fails internally, the event is written to `webhook_event_queue` with `status = 'pending_processing'`
- Background job `WebhookRetryJob` retries failed events up to 5 times with exponential backoff: 1min, 5min, 15min, 1h, 4h
- After 5 failures, event is marked `status = 'dead_letter'` and a Critical alert is raised: `billing.webhook_processing_failed`
- Each event has `paddle_event_id` as unique constraint in `webhook_event_queue` — duplicate events are ignored with `200` response

### PayHere Webhook Handling

PayHere sends POST to `POST /webhooks/payhere/notify`.

| Field | Verification Method |
|---|---|
| Signature | MD5 hash of `merchant_id + order_id + amount + currency + status_code + uppercase(MD5(merchant_secret))` |
| Validation | Recalculate hash server-side; reject if mismatch |

| PayHere Status Code | ONEVO Action |
|---|---|
| `2` (Success) | Mark invoice Paid |
| `0` (Pending) | No change — await final status |
| `-1` (Cancelled) | Warning alert |
| `-2` (Failed) | Increment retry; Critical after 3 failures |
| `-3` (Charged Back) | Warning alert for chargeback review |

---

## Dunning Sequence — Full Specification

Dunning is the automated payment recovery flow for tenants with failed gateway payments.

### Dunning Schedule

| Attempt | When | Action | Alert |
|---|---|---|---|
| Attempt 1 | Billing date | Gateway charge initiated (Paddle auto-charges; PayHere initiated by ONEVO) | — (normal) |
| Retry 1 | +3 days after failure | Gateway retry | Warning: `billing.payment_failed` |
| Retry 2 | +7 days after Retry 1 | Gateway retry | Warning: `billing.payment_failed` (existing alert updated) |
| Retry 3 | +7 days after Retry 2 | Gateway retry — final | Critical: `billing.payment_failed_final` if fails |
| Grace window | After Retry 3 | Tenant access continues for 7 days | Critical alert remains open |
| Suspension | +7 days after Retry 3 | `PATCH /admin/v1/tenants/{id}/status {status: suspended}` auto-applied by `DunningJob` | Audit log: `action = 'tenant.auto_suspended_dunning'` |

**Rule:** Auto-suspension is logged as a system action, not a platform admin action. The platform admin who owns the tenant relationship is notified via the Critical alert and can override the suspension before it triggers by:
- Manually marking the invoice paid with evidence
- Entering a payment exception/grace period
- Upgrading to manual collection with billing evidence

**Dunning override:** Platform admin can halt dunning for a tenant at any point by setting a payment exception. `PATCH /admin/v1/tenants/{id}/subscription` with `payment_exception_start` and `payment_exception_end` set stops the dunning job from running for that tenant during the exception window.

---

## Invoice Invoices Screen — Full Specification

**Route:** `/platform/subscriptions/invoices`

**API:** `GET /admin/v1/subscription-invoices?{filters}&page={n}&per_page={n}`

### Filter Bar

| Filter | Type | Options |
|---|---|---|
| Search | Text | Invoice number, tenant name |
| Status | Dropdown | All / Draft / Open / Paid / Overdue / Void / Uncollectible |
| Tenant | Autocomplete search | Tenant name |
| Date range | Date picker | Invoice generation date from/to |
| Amount range | Number inputs | Min / Max |
| Payment method | Dropdown | All / Paddle / PayHere / Manual / Waived |

### Invoices Table

| Column | Description |
|---|---|
| Invoice Number | Linked — opens invoice detail side panel |
| Tenant | Company name, linked to tenant detail |
| Period | "May 2025" |
| Amount | Formatted with currency |
| Status | Colored badge |
| Issued | Date |
| Due | Date — red text if overdue |
| Paid | Date or "—" |
| Method | Paddle / PayHere / Manual |
| Actions | Download PDF, Mark Paid (if manual/open), Void, View Paddle dashboard link |

### Mark Invoice Paid (Manual Collection)

**Endpoint:** `PATCH /admin/v1/invoices/{id}/mark-paid`

**Request body:**
```json
{
  "payment_method": "manual",
  "payment_reference": "BANK-TRF-20250520-0042",
  "payment_date": "2025-05-19",
  "evidence_file_id": "file-uuid-...",
  "notes": "Wire transfer confirmed by finance team."
}
```

**Response (200 OK):**
```json
{
  "invoice_id": "...",
  "status": "paid",
  "paid_at": "2025-05-19T00:00:00Z"
}
```

**State written:**
- `invoice.status = 'paid'`
- `invoice.paid_at` set
- `invoice.payment_reference` set
- If tenant had `billing.payment_failed` or `billing.payment_failed_final` alert: alert auto-resolved with `resolved_reason = 'payment_confirmed_manually'`
- If tenant was in dunning: dunning halted for this invoice cycle
- Audit log: `action = 'invoice.manually_marked_paid'`

---

## Pricing History Screen

**Route:** `/platform/subscriptions/pricing-history`

Shows all historical price bracket changes across all plans, with before/after comparison.

| Column | Description |
|---|---|
| Plan | Plan name |
| Module | Module that had price change |
| Company Size | Which bracket changed |
| Previous Price | Unit price before change |
| New Price | Unit price after change |
| Changed By | Platform admin who made the change |
| Changed At | Timestamp |
| Reason | Audit reason entered at time of change |

---

## APIs — Full Catalog

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/subscription-plans` | List plans | `platform.subscriptions.read` |
| POST | `/admin/v1/subscription-plans` | Create plan | `platform.subscriptions.manage` |
| GET | `/admin/v1/subscription-plans/{id}` | Plan detail with brackets | `platform.subscriptions.read` |
| PATCH | `/admin/v1/subscription-plans/{id}` | Update plan metadata/modules/pricing | `platform.subscriptions.manage` |
| POST | `/admin/v1/subscription-plans/{id}/clone` | Clone plan with new name | `platform.subscriptions.manage` |
| DELETE | `/admin/v1/subscription-plans/{id}` | Deactivate plan (cannot delete if tenants assigned) | `platform.subscriptions.manage` |
| GET | `/admin/v1/payment-gateways` | List gateways (no secrets) | `platform.payment_gateways.read` |
| POST | `/admin/v1/payment-gateways` | Create gateway config | `platform.payment_gateways.manage` |
| GET | `/admin/v1/payment-gateways/{id}` | Gateway detail (no secrets) | `platform.payment_gateways.read` |
| PATCH | `/admin/v1/payment-gateways/{id}` | Update gateway metadata | `platform.payment_gateways.manage` |
| PATCH | `/admin/v1/payment-gateways/{id}/rotate-secrets` | Rotate credentials | `platform.payment_gateways.manage` |
| DELETE | `/admin/v1/payment-gateways/{id}` | Deactivate gateway | `platform.payment_gateways.manage` |
| GET | `/admin/v1/subscription-invoices` | List invoices | `platform.subscriptions.read` |
| GET | `/admin/v1/subscription-invoices/{id}` | Invoice detail | `platform.subscriptions.read` |
| PATCH | `/admin/v1/subscription-invoices/{id}/mark-paid` | Mark manual invoice paid | `platform.subscriptions.manage` |
| PATCH | `/admin/v1/subscription-invoices/{id}/void` | Void invoice | `platform.subscriptions.manage` |
| GET | `/admin/v1/subscription-invoices/{id}/pdf` | Download invoice PDF | `platform.subscriptions.read` |
| GET | `/admin/v1/tenants/{id}/subscription` | Tenant commercial detail | `platform.subscriptions.read` |
| PATCH | `/admin/v1/tenants/{id}/subscription` | Assign/override tenant subscription | `platform.subscriptions.manage` |
| GET | `/admin/v1/subscription-plans/pricing-history` | All plan pricing history | `platform.subscriptions.read` |
| POST | `/webhooks/paddle` | Paddle webhook inbound | None (signature-verified) |
| POST | `/webhooks/payhere/notify` | PayHere webhook inbound | None (signature-verified) |

---

## Invoice PDF Generation — Full Specification

### Scope

PayHere tenants: ONEVO generates the invoice PDF server-side using QuestPDF. Paddle tenants: Paddle hosts the PDF; ONEVO stores `paddle_invoice_url` and redirects to it.

### QuestPDF Generation (PayHere tenants)

**Library:** QuestPDF (open-source, MIT-licensed, .NET 10 compatible)

**Trigger:** On-demand — PDF is generated at request time, not stored. Generated bytes are streamed directly in the response.

**Endpoint:** `GET /admin/v1/subscription-invoices/{id}/pdf`
**Tenant endpoint:** `GET /api/v1/billing/invoices/{id}/pdf`

**PDF content:**

| Section | Content |
|---|---|
| Header | ONEVO logo, "TAX INVOICE" heading, invoice number, issue date, due date |
| Billed To | Tenant legal name, primary contact email, country, company size range |
| Billed By | ONEVO company name, registration number, address, contact email |
| Line Items Table | Module name, pricing unit (per user / flat rate), quantity (billable users with monitoring enabled for Package 1; active WorkSync users for Package 2), unit price, line total |
| Subtotal row | Sum of line totals |
| Tax row | `tax_amount` (0.00 for Sri Lanka Phase 1) |
| Total row | Grand total in tenant's billing currency |
| Payment section | Payment method, payment reference, paid date (if paid) |
| Footer | Invoice number, "Generated by ONEVO Platform", page number |

**Response headers:**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="INV-{invoice_number}.pdf"
```

**Authorization:** Platform admin requires `platform.subscriptions.read`. Tenant user requires authenticated session and ownership of the invoice's tenant.

**Paddle tenant handling:** If `invoice.payment_method = 'paddle'` and `paddle_invoice_url` is set, respond with `302 Redirect` to `paddle_invoice_url`. Do not generate a local PDF.

---

## Chargeback / Dispute Resolution — Full Specification

### Trigger

Paddle sends `dispute.created` webhook → ONEVO creates Warning alert: `billing.dispute_raised`.

### Resolution Flow

| Step | Action |
|---|---|
| 1 | Alert raised: `billing.dispute_raised` — links to invoice, dispute amount, dispute reason from Paddle |
| 2 | Platform admin reviews dispute in Paddle dashboard (linked from alert) |
| 3 | Admin chooses action in ONEVO: Accept Dispute or Contest Dispute |
| 4a — Accept | `PATCH /admin/v1/subscription-invoices/{id}/mark-uncollectible` — invoice status → `uncollectible`; audit logged; alert resolved |
| 4b — Contest | Admin records contest reference; alert status → `acknowledged`; no invoice state change |
| 5 | Paddle sends `dispute.closed` webhook → ONEVO resolves the alert; if lost, invoice → `uncollectible` automatically |

**Rule:** Dispute outcome must be recorded in ONEVO regardless of Paddle dashboard action — invoice state must match the financial reality.

### Handled Paddle Dispute Events

| Paddle Event | ONEVO Action |
|---|---|
| `dispute.created` | Warning alert `billing.dispute_raised`; invoice flagged |
| `dispute.closed` (won) | Alert resolved; no invoice state change |
| `dispute.closed` (lost) | Alert resolved; `invoice.status → 'uncollectible'`; audit log entry |

---

## Billing Audit Log — Full Specification

Every mutation to billing state must be logged. Platform admins must be able to reconstruct the full billing history for any tenant.

### What Is Logged

| Action | Trigger | Fields Logged |
|---|---|---|
| Invoice marked paid | `PATCH /admin/v1/subscription-invoices/{id}/mark-paid` | `actor_id`, `invoice_id`, `old_status`, `new_status = 'paid'`, `payment_reference`, `paid_at`, `reason` |
| Invoice voided | `PATCH /admin/v1/subscription-invoices/{id}/void` | `actor_id`, `invoice_id`, `old_status`, `new_status = 'void'`, `reason` |
| Invoice marked uncollectible | `PATCH /admin/v1/subscription-invoices/{id}/mark-uncollectible` | `actor_id`, `invoice_id`, `old_status`, `new_status = 'uncollectible'`, `reason` |
| Subscription assigned/overridden | `PATCH /admin/v1/tenants/{id}/subscription` | `actor_id`, `tenant_id`, `old_plan_id`, `new_plan_id`, `old_commercial_model`, `new_commercial_model`, `reason` |
| Override price set | Plan override during provisioning or update | `actor_id`, `tenant_id`, `plan_id`, `old_override_price`, `new_override_price`, `reason` |
| Tenant auto-suspended (dunning) | `DunningJob` | `actor_id = 'system'`, `tenant_id`, `invoice_id`, `action = 'tenant.auto_suspended_dunning'` |
| Payment exception set | Admin halts dunning | `actor_id`, `tenant_id`, `exception_type`, `approved_until`, `reason` |
| Gateway secrets rotated | `PATCH /admin/v1/payment-gateways/{id}/rotate-secrets` | `actor_id`, `gateway_id`, `action = 'gateway.secrets_rotated'`, `rotation_reason` |

### Storage

All entries go to `billing_audit_logs` table (see database schema). Entries are **immutable** — no UPDATE or DELETE. Retention: indefinite.

### Rule

`reason` is a required free-text field on every admin-triggered billing mutation. System-triggered entries (dunning, webhook) use `actor_id = 'system'` and a fixed reason string.

---

## MRR / ARR / Churn Reporting — Full Specification

### Report Definitions

| Metric | Formula |
|---|---|
| MRR (Monthly Recurring Revenue) | Sum of `effective_price` for all `tenant_subscriptions` with `status IN ('active', 'trialing')` and `billing_cycle = 'monthly'` + (annual / 12) |
| ARR (Annual Recurring Revenue) | MRR × 12 |
| Churn rate (monthly) | Subscriptions cancelled this month / active subscriptions start of month |
| Net revenue retention | (MRR end of period − MRR start + expansion − contraction − churn) / MRR start |
| Failed payments | Count of `subscription_invoices` with `status = 'overdue'` in period |
| Outstanding invoices | Sum of `total` for invoices with `status IN ('open', 'overdue')` |

### Report Endpoints

| Method | Route | Description | Permission |
|---|---|---|---|
| GET | `/admin/v1/reports/billing/mrr` | MRR for a given month (`?year=2025&month=6`) | `platform.reports.read` |
| GET | `/admin/v1/reports/billing/arr` | ARR at a given date (`?as_of=2025-06-01`) | `platform.reports.read` |
| GET | `/admin/v1/reports/billing/churn` | Churn rate for a period (`?from=2025-01-01&to=2025-06-30`) | `platform.reports.read` |
| GET | `/admin/v1/reports/billing/revenue-by-plan` | Revenue breakdown per plan for a period | `platform.reports.read` |
| GET | `/admin/v1/reports/billing/revenue-by-tenant` | Revenue breakdown per tenant for a period | `platform.reports.read` |
| GET | `/admin/v1/reports/billing/failed-payments` | Failed payment count + amount in period | `platform.reports.read` |
| GET | `/admin/v1/reports/billing/outstanding` | All open + overdue invoices with amounts | `platform.reports.read` |

### Data Source

All reports query `subscription_invoices`, `tenant_subscriptions`, and `subscription_plans` directly. No pre-aggregated reporting table in Phase 1 — queries are run on-demand. Add database-level indexes if query performance degrades with scale.

---

## Billable User Definition and Billing Rules

### Package 1 Billable Seat

An employee is counted as a **billable Package 1 seat** at the monthly snapshot when ALL of the following are true:

1. `employees.status = 'active'`
2. `users.status ≠ 'deactivated'`
3. Monitoring is **not** fully disabled for this employee — at least one monitoring feature toggle is enabled (from tenant default or employee-specific override in `monitoring_feature_toggles`)

**Excluded from billing:**
- Employees with monitoring fully disabled (operator or employee-level override)
- Offboarded / deactivated employees
- Users with `status = 'invited'` who have not yet accepted

### Package 2 Billable Seat

An employee/user counts as a **billable WorkSync seat** when they are an active member of at least one WorkSync workspace at snapshot time.

> **Open decision:** Whether Package 2 requires at least one login action in the billing period (vs. just workspace membership) is not yet finalised. Confirm with product and finance before Phase 1 billing goes live.

### Billing Snapshot Job

- Runs at end of each calendar month
- Reads `employees` filtered by `status = 'active'`
- Joins `monitoring_feature_toggles` to exclude fully-disabled employees
- Stores result in `billing_snapshots` with `tenant_id`, `billing_period_start`, `billing_period_end`, `billable_user_count_p1`, `billable_user_count_p2`
- Idempotent: same `tenant_id + billing_period_start` is an upsert, not an insert

---

## Plan Change Rules

### Upgrade / Adding Modules

| Scenario | Rule |
|:---|:---|
| Operator adds a module via `PUT /admin/v1/tenants/{id}/modules` | Entitlement active immediately; billable from next snapshot |
| Gateway subscription | Paddle/PayHere subscription updated via gateway API; next invoice reflects new rate |
| Manual collection | Operator records new commercial terms; next manual invoice reflects updated amount |
| Proration | Prorated charge for remaining days in cycle; included as a line item on next invoice |

### Downgrade / Removing Modules

| Scenario | Rule |
|:---|:---|
| Operator disables a module | Entitlement set to `disabled` at end of current billing period |
| Data preservation | All module data and configuration preserved until period end |
| No proration credit | No credit for removed modules mid-cycle |
| Downgrade restrictions | Cannot remove modules required by other active modules (e.g. cannot remove `core_hr` while `leave` is active) |
| Self-service | Pack removal is NOT self-service — tenant contacts ONEVO |

### Cancellation

| Scenario | Rule |
|:---|:---|
| Request | `cancel_at_period_end = true`; full access until `billing_period_end` |
| Paddle | Cancels subscription at period end via Paddle API |
| PayHere | DunningJob will not generate next invoice |
| Data retention | All tenant data retained for **90 days** after `billing_period_end` |
| After 90 days | Permanent deletion job; data unrecoverable |
| Status transition | `tenants.status → 'cancelled'`; all entitlements → `disabled` |
| Reversal | Platform admin only — not self-service |

### Restarting a Cancelled Subscription

| Scenario | Rule |
|:---|:---|
| Within 90-day window | Operator re-activates via Tenant Console; existing data intact; new billing start date set |
| After 90-day window | Data deleted; must be re-provisioned as a new account |

### Payment Failure

See [Dunning Sequence](#dunning-sequence--full-specification) for full retry schedule.

| Scenario | Rule |
|:---|:---|
| 3 retries exhausted | 7-day grace period before auto-suspension |
| Payment exception window | Operator can grant approved exception to halt dunning |
| Auto-suspension | `tenants.status = 'suspended'`; users blocked from login |
| Recovery | Operator unsuspends after payment confirmed |

### Usage Limit Breach

| Scenario | Rule |
|:---|:---|
| AI tokens at 80% | Warning alert raised; no service disruption |
| AI tokens at 100% | AI features soft-limited or blocked per plan terms; platform admin alerted |
| Storage at 80% | Warning alert raised; no service disruption |
| Storage at 100% | File uploads return `413 storage_limit_exceeded`; existing data preserved |

---

## Error Taxonomy

| HTTP | Code | Condition |
|---|---|---|
| 400 | `webhook_signature_invalid` | Paddle/PayHere webhook signature mismatch |
| 404 | `plan_not_found` | Plan ID does not exist |
| 404 | `gateway_not_found` | Gateway ID does not exist |
| 404 | `invoice_not_found` | Invoice ID does not exist |
| 409 | `plan_name_taken` | Active plan with same name exists |
| 409 | `gateway_in_use` | Cannot deactivate gateway with active tenant assignments |
| 409 | `plan_in_use` | Cannot delete plan with active tenant assignments |
| 422 | `no_modules_selected` | Plan must include at least one module |
| 422 | `phase2_modules_rejected` | Phase 2 module keys (`payroll`, `performance`, `documents`, `reports`, etc.) not allowed in Phase 1 plans |
| 422 | `missing_price_brackets` | Bracket required per selected size range |
| 422 | `invoice_already_paid` | Cannot void a paid invoice |
| 422 | `invoice_not_open` | Can only mark open/overdue invoices as paid |
| 422 | `missing_payment_evidence` | Manual payment requires reference or file |
| 500 | `paddle_api_error` | Paddle API unreachable or returned error |
| 500 | `payhere_api_error` | PayHere API unreachable or returned error |
