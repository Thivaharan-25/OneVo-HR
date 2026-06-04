# Billing & Subscription Management

**Area:** Platform Setup
**Trigger:** Admin navigates to billing settings (user action)
**Required Permission(s):** `billing:manage`
**Related Permissions:** `settings:billing` (for viewing invoice history and tax settings)

---

## Billing Model

ONEVO uses **employee-count-based first billing** followed by snapshot-based recurring billing. There is no self-service signup or public checkout on the ONEVO website. Tenants are acquired through a sales conversation and provisioned by an ONEVO operator. The operator decides the allowed plans, payment gateway or manual collection method, setup charges, and negotiated commercial terms. The tenant owner later chooses a subscription plan from the allowed list, chooses the billing cycle, confirms total employee count, and pays the generated invoice.


### Commercial Models

ONEVO supports both commercial models:

| Model | Meaning | Access Rule |
|------|---------|-------------|
| `subscription` | Tenant pays recurring SaaS fees for the selected plan. Billing cycle is selected by the tenant owner during onboarding. | Enabled modules come from the selected plan plus paid add-ons, minus disabled modules. |
| `full_license_maintenance` | Tenant buys an agreed license up front, then pays recurring maintenance/support when applicable. | Enabled modules come from owned license modules plus maintenance-included modules and purchased add-ons, minus disabled modules. |

For full-license tenants, expired maintenance may block support, updates, or new module access according to the contract. It should not automatically disable already-owned core access unless the signed agreement explicitly says so.

### Pricing Configuration

Pricing is configurable in Developer Platform and must not be hardcoded. Operators can maintain:

| Pricing Area | Example |
|--------------|---------|
| Plan calculated price | Plan rate table selected by confirmed employee count = calculated recurring total before override |
| Plan override price | Sales-approved override = 7.00/employee/month |
| Package price bracket | Package 1 = 3.50/employee/month for `51-200` employees |
| Per employee/device price | Package-specific employee/device pricing configured by operator |
| Full license purchase price | Agreed ONEVO package license = 10,000 one-time |
| Maintenance price | 18% of license value yearly |
| AI token limit | Package 2 agentic chat includes 500,000 tokens/month |
| Custom enterprise price | Manually entered contract amount |

Module entitlement and pricing decide what the tenant has access to. RBAC decides which users inside the tenant can use those capabilities. These concerns must remain separate.

Reusable subscription plans define feature/module bundles and pricing rules. Company-size/employee-count tiers live inside the subscription plan pricing table; they are not module configuration and not separate plan identities. The tenant owner's confirmed total employee count determines the first invoice quantity and selects the applicable pricing tier. Tenant subscriptions store the selected plan, billing cycle, employee-count snapshot, calculated price, and any override so future catalog price changes do not rewrite old contracts.

AI-capable plans must carry a positive monthly token cap. Non-AI plans leave the token cap empty.
### Pricing Packs

| Pack | Modules Included | Pricing Unit |
|------|-----------------|--------------|
| **Foundation** | Authentication and Authorization, Tenant Configuration and Onboarding, Roles and Permissions | Always included |
| **Package 1** | Profile Management, Attendance and Leave Management, E2E Monitoring, Productivity and Performance Analytics, Exception Detection, Overtime Management | Commercial pricing by active employee and/or monitored employee/device, finalized in billing configuration |
| **Package 2** | Project Management, Agentic Chat, Third Party Integrations, IDE Extension | Commercial pricing by active Work Management user, finalized in billing configuration |

Future modules (Governance, Skill & Talent Development, Payroll, Performance, etc.) are released as standalone add-ons. When ONEVO introduces a new module, the operator adds it to the catalog in the Developer Console and it appears as a purchasable add-on for all tenants that don't have it.

### Billing Calculation

| Item | Rule |
|------|------|
| First invoice billing unit | Tenant-owner-confirmed total employee count |
| Recurring Package 1 billing unit | Active employees in ONEVO at the billing snapshot. No device-based billing. |
| Recurring Package 2 billing unit | Active WorkSync workspace members at end-of-month snapshot, if Package 2 uses separate usage-based pricing |
| AI token billing | Consumed tokens tracked against the agreed monthly limit. Overages are a Phase 2 concern. |
| Billing cycle | Tenant owner selects monthly or annual during subscription confirmation |
| First invoice generation | After tenant owner confirms selected plan, billing cycle, total employee count, and billing contact |
| Recurring invoice generation | ONEVO generates and sends invoices from billing snapshots by the 3rd of the following month, unless annual prepaid terms apply |
| Proration | Packages added mid-cycle are prorated for remaining days. Removals take effect from the next billing cycle. |

**First invoice rule:** Do not ask the tenant owner to classify users by monitoring, WorkSync, or internal package usage in the invoice email. The first payable invoice uses the tenant-owner-confirmed total employee count. More detailed recurring billing quantities can be calculated later from system data after onboarding/import.

---

## One-Time Setup Charges

One-time setup charges are fees billed once per tenant for initial ONEVO operator configuration services (see `setup_options` in [[Userflow/Platform-Setup/tenant-provisioning|Tenant Provisioning]]). They are **separate** from recurring monthly or annual subscription charges.

### Key rules

- Setup charges are priced and managed by the ONEVO operator via `/admin/v1/tenants/{tenantId}/billing/one-time-charges`.
- They are billed **once** - not monthly or annually. They cover one-off operator labour such as job family creation, employee invites, or role and permission configuration.
- The first invoice a tenant receives **should include both** the first subscription charge and one-time setup line items together unless the signed contract explicitly requires setup-only prepayment. The customer is not required to make two separate payments by default.
- Setup charges can be tied to the specific `setup_options` selected during tenant creation.

### Setup charge lifecycle

| Status | Meaning |
|:-------|:--------|
| `draft` | Created by operator, not yet approved for invoicing |
| `approved` | Approved; will be included on the next invoice run |
| `invoiced` | Included on a generated invoice |
| `paid` | Payment confirmed |
| `void` | Cancelled before payment |

### API (operator only)

| Method | Route | Description |
|:-------|:------|:------------|
| GET | `/admin/v1/tenants/{tenantId}/billing/one-time-charges` | List setup charges for a tenant |
| POST | `/admin/v1/tenants/{tenantId}/billing/one-time-charges` | Create a new setup charge |
| PATCH | `/admin/v1/tenants/{tenantId}/billing/one-time-charges/{chargeId}` | Update status or amount |

---

## Preconditions

- Tenant provisioned via [[developer-platform/userflow/provisioning-flow|Provisioning Flow]]
- User has `billing:manage` permission
- ONEVO operator selected payment gateway/collection method in Developer Platform. Tenant owner cannot choose Stripe, Paddle, PayHere, or Manual.

---

## Flow Steps
### Step 1: Navigate to Billing

- **UI:** Settings sidebar > Billing & Subscription. Before first invoice, dashboard shows:
  - Allowed subscription plans
  - Recommended plan, if set by ONEVO
  - Total employee count confirmation
  - Monthly/annual billing cycle choice
  - Billing contact details
  - Estimated first invoice amount

After activation/payment, dashboard shows:
  - Active packs and add-ons with their current rates
  - Active employee count used by the latest billing snapshot
  - Current billing cycle dates
  - Next invoice date and estimated amount
  - Invoice history (view / download)
  - Billing contact email
- **API:** `GET /api/v1/billing/subscription`
- **Backend:** `BillingService.GetCurrentSubscriptionAsync()`
- **DB:** `tenant_subscriptions`, `subscription_plans`

### Step 2: Confirm Plan, Billing Cycle, And Employee Count

- **UI:** Tenant owner selects one plan from the operator-allowed list, chooses monthly or annual billing, confirms total employee count, and confirms billing contact details.
- **Copy rule:** Do not ask for "monitoring employees", "WorkSync employees", or similar internal billing classifications in the invoice email or first-billing confirmation screen.
- **API:** `POST /api/v1/billing/subscription/confirm`
- **Backend:** Validates the selected plan is allowed for the tenant, validates the billing cycle is supported, snapshots confirmed employee count, calculates first invoice, and initiates the operator-selected payment flow.
- **DB:** `tenant_subscriptions`, `subscription_invoices`, `tenant_one_time_charges`

### Step 3: First Invoice And Payment

- **UI:** Tenant owner receives one first invoice/payment request showing selected plan, billing cycle, confirmed employee count, subscription amount, one-time setup charges, discounts/overrides, taxes, total, due date, and payment action.
- **Calculation:** `first_invoice_total = selected_plan_rate_for_confirmed_employee_count * confirmed_employee_count * billing_cycle_multiplier + one_time_setup_charges - discounts_or_overrides + tax`.
- **Payment:** Uses the gateway or manual collection method selected by the ONEVO operator during tenant creation.
- **DB:** `subscription_invoices`, `tenant_subscriptions`, `tenant_one_time_charges`

### Step 4: View Invoice History and Download PDFs

- **UI:** Table of past invoices - date, billing basis, rate, total, status (paid/pending). Each row has a **Download PDF** button.
- **API:** `GET /api/v1/billing/invoices` - list; `GET /api/v1/billing/invoices/{id}/pdf` - download
- **Backend:** Stripe/PayHere tenants: ONEVO can generate or stream the invoice PDF server-side. Paddle tenants: redirect `302` to the Paddle-hosted invoice URL when Paddle is the merchant of record.
- **DB:** `subscription_invoices`

### Step 5: Add a New Pack or Add-on (Self-Service Upgrade)

Tenant admins can add packs and the Chat AI add-on directly when their commercial model and payment policy allow self-service upgrades. Subscription tenants use the operator-configured payment gateway (`stripe`, `paddle`, or `payhere`). Full-license tenants route new purchases through ONEVO sales/operator approval unless the contract explicitly allows gateway-collected add-ons.

- **UI:** "Available Add-ons" section shows all packs and add-ons the tenant has not purchased.
- **API:** `POST /api/v1/billing/modules/{moduleId}/add`
- **Backend:** Validates the configured gateway/payment method, charges any required proration, updates module entitlements, publishes `SubscriptionChangedEvent`, and writes an audit log entry.
- **DB:** `tenant_module_entitlements`, `tenant_subscriptions`, `feature_flag_overrides`

**Note:** Pack removal (downgrade) is not self-service - tenant contacts ONEVO. This prevents accidental data access loss.

### Step 6: Cancel Subscription

Tenant admins with `billing:manage` permission can request cancellation of their subscription.

- **UI:** Settings sidebar > Billing & Subscription > Danger Zone section > **Cancel Subscription** button. Shows confirmation modal with:
  - Current plan name
  - Access end date (last day of current billing period)
  - Warning: "All tenant data is retained for 90 days after cancellation. After that, data is permanently deleted."
  - Required free-text reason field
  - **Confirm Cancellation** button
- **API:** `POST /api/v1/billing/subscription/cancel` with `{ "reason": "..." }`
- **Backend:**
  1. Sets `tenant_subscriptions.cancellation_requested_at = now()`, `cancel_at_period_end = true`
  2. For Paddle tenants: calls Paddle API to cancel subscription at period end
  3. For PayHere tenants: no gateway call needed - `DunningJob` will not generate next invoice
  4. Creates `billing_audit_logs` entry: `action = 'subscription.cancel_requested'`
  5. Platform admin notified via Info alert: `billing.cancellation_requested`
  6. Tenant retains full access until `billing_period_end`
- **DB:** `tenant_subscriptions`, `billing_audit_logs`, `platform_alerts`

**Rules:**
- Cancellation takes effect at end of current billing period - never immediate
- Once requested, cancellation can only be reversed by a platform admin (not tenant self-service)
- Tenant status transitions to `cancelled` after `billing_period_end` passes (handled by background job)

### Step 7: Upgrade Nudge (In-App)

Locked features across the app surface an upgrade prompt to guide tenant admins to the billing section.

- **UI:** Lock icon on any feature from an unpurchased pack. Tooltip: "Available in [Pack Name] - from $X/user/month. **Add it in Billing.**" Clicking the lock navigates to the billing section with that pack pre-highlighted in the Available Add-ons section.
- No API call from the lock icon itself - it is a frontend navigation cue only.

---

## Active User Definition

### Package 1 Billable Seat

An employee counts as a **billable Package 1 seat** at the monthly snapshot when ALL of the following are true:

1. `employees.status = 'active'`
2. `users.status != 'deactivated'` (associated user account exists and is not deactivated)
3. Monitoring is **not** fully disabled for this employee - at least one monitoring feature toggle is enabled (from tenant default or employee-specific override)

**Excluded from billing:**
- Employees with monitoring fully disabled
- Offboarded / deactivated employees
- Invited users who have not yet accepted (`status = 'invited'`)

### Package 2 Billable Seat

An employee/user counts as a **billable WorkSync seat** when they are an active member of at least one WorkSync workspace at snapshot time.

> **Open decision:** Whether Package 2 requires at least one login action in the billing period (vs. just workspace membership) is not yet finalised. Confirm with product and finance before Phase 1 billing goes live.

---

## Plan Change Rules

### Upgrade / Adding Modules

| Scenario | Rule |
|:---|:---|
| Operator adds a module | Effective immediately; module entitlement activated |
| Proration | Prorated charge for remaining days in current cycle included on next invoice |
| Gateway subscription update | Stripe/Paddle/PayHere subscription updated via gateway API |
| Manual collection | Operator records new commercial terms; next manual invoice reflects updated amount |

### Downgrade / Removing Modules

| Scenario | Rule |
|:---|:---|
| Operator removes a module | Effective at end of current billing period - never immediate |
| Data preservation | Configuration and data preserved until period end |
| No proration credit | No credit issued for removed modules mid-cycle |
| Downgrade restrictions | Cannot remove modules that other active modules depend on (e.g. cannot remove Core HR while Leave is active) |
| Self-service | Pack removal is NOT self-service - tenant contacts ONEVO |

### Cancellation

| Scenario | Rule |
|:---|:---|
| Tenant requests cancellation | `cancel_at_period_end = true`; full access until `billing_period_end` |
| Timing | Always at end of current billing period |
| Reversal | Platform admin only - not tenant self-service |
| Data retention | All tenant data retained for **90 days** after `billing_period_end` |
| After 90 days | Permanent deletion job runs; data cannot be recovered |
| Status | `tenants.status = 'cancelled'`; all module entitlements set to `disabled` |

### Restarting a Cancelled Subscription

| Scenario | Rule |
|:---|:---|
| Within 90-day retention window | Operator re-activates via Developer Console; existing data intact; new billing start date set |
| After 90-day window | Data deleted; must re-provision as a new account |

### Payment Failure

| Scenario | Rule |
|:---|:---|
| First failure | Retry attempted automatically; tenant continues operating |
| After 3 retries (~17 days) | Critical alert; 7-day grace period before auto-suspension |
| Payment exception window | Operator can grant approved exception to halt dunning |
| Auto-suspension | `tenants.status = 'suspended'`; users cannot log in |
| Recovery | Operator unsuspends via Developer Console after payment confirmed |

### Usage Limit Breach

| Scenario | Rule |
|:---|:---|
| AI tokens at 80% | Warning alert raised |
| AI tokens at 100% | AI features soft-limited or blocked; platform admin alerted |
| Storage at 80% | Warning alert raised |
| Storage at 100% | File uploads return `413 storage_limit_exceeded`; existing data preserved |

---

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Gateway payment method missing | Add pack blocked | "Please add a payment method before adding new modules." |
| Gateway charge fails | Module not activated | "Payment failed. Please check your payment method and try again." |
| Active user count API unavailable | Cached snapshot used | Count shown with "(estimate)" label |
| Invoice PDF unavailable | Retry link shown | "Invoice PDF is being generated. Try again shortly." |
| Cancellation attempted with no active subscription | Request blocked | "No active subscription to cancel." |
| Cancellation already requested | Request blocked | "A cancellation is already pending for this subscription." |

---

## Events Triggered

- `BillingSnapshotTakenEvent` - end-of-month background job, triggers invoice generation
- `SubscriptionChangedEvent` -> feature flag service updates active modules for the tenant
- `AuditLogEntry` (action: `billing.module_added`) -> [[modules/auth/audit-logging/overview|Audit Logging]]

---

## Related Flows

- [[developer-platform/userflow/provisioning-flow|Provisioning Flow]] - initial pack assignment by ONEVO operator
- [[developer-platform/userflow/tenant-management|Tenant Management]] - operator changes plan or removes packs via Developer Console
- [[Userflow/Configuration/tenant-settings|Tenant Settings]] - billing contact email

## Module References

- [[modules/shared-platform/subscriptions-billing/overview|Subscriptions Billing]]
- [[backend/module-catalog|Module Catalog]] - full pack and add-on definitions
- [[modules/notifications/overview|Notifications]] - invoice and billing event emails

