# Billing & Subscription Management

**Area:** Platform Setup
**Trigger:** Admin navigates to billing settings (user action)
**Required Permission(s):** `billing:manage`
**Related Permissions:** `settings:billing` (for viewing invoice history and tax settings)

---

## Billing Model

ONEVO uses **active-user-based billing**. There is no self-service signup or checkout on the ONEVO website. Tenants are acquired via a sales conversation and provisioned by an ONEVO operator. Once active, tenant admins can request or add new packs/add-ons according to their commercial model and contract rules. Subscription tenants can use self-service upgrades only when payment policy allows it; full-license tenants route module purchases or maintenance-included upgrades through ONEVO sales/operator approval.


### Commercial Models

ONEVO supports both commercial models:

| Model | Meaning | Access Rule |
|------|---------|-------------|
| `subscription` | Tenant pays recurring SaaS fees for selected plans/modules. Billing can be monthly or annual. | Enabled modules come from plan-included modules plus paid add-ons and trial modules, minus disabled modules. |
| `full_license_maintenance` | Tenant buys an agreed license up front, then pays recurring maintenance/support. | Enabled modules come from owned license modules plus maintenance-included modules, purchased add-ons, and trial modules, minus disabled modules. |

For full-license tenants, expired maintenance may block support, updates, or new module access according to the contract. It should not automatically disable already-owned core access unless the signed agreement explicitly says so.

### Pricing Configuration

Pricing is configurable in Developer Platform and must not be hardcoded. Operators can maintain:

| Pricing Area | Example |
|--------------|---------|
| Plan calculated price | Package 1 + Package 2 for the selected company-size range = calculated package total before override |
| Plan override price | Sales-approved override = 7.00/employee/month |
| Package price bracket | Package 1 = 3.50/employee/month for `51-200` employees |
| Per employee/device price | Package-specific employee/device pricing configured by operator |
| Full license purchase price | Agreed ONEVO package license = 10,000 one-time |
| Maintenance price | 18% of license value yearly |
| AI token limit | Package 2 agentic chat includes 500,000 tokens/month |
| Trial terms | Free for 30 days |
| Custom enterprise price | Manually entered contract amount |

Module entitlement and pricing decide what the tenant has access to. RBAC decides which users inside the tenant can use those capabilities. These concerns must remain separate.

Reusable plan prices are calculated from selected package/module price brackets and the selected company-size range. The company-size range uses the same values as the operator tenant-creation dropdown. Tenant subscriptions store the calculated price and any override as a snapshot so future catalog price changes do not rewrite old contracts.

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
| Package 1 billing unit | Active employees and/or monitored employees/devices, based on commercial configuration |
| Package 2 billing unit | Active Work Management users at end-of-month snapshot |
| Billing cycle | Calendar month (1st to last day) |
| Invoice generation | ONEVO generates and sends invoice by 3rd of the following month |
| Proration | Packages added mid-cycle are prorated for remaining days. Removals take effect from the next billing cycle. |

---

## One-Time Setup Charges

One-time setup charges are fees billed once per tenant for initial ONEVO operator configuration services (see `setup_options` in [[Userflow/Platform-Setup/tenant-provisioning|Tenant Provisioning]]). They are **separate** from recurring monthly or annual subscription charges.

### Key rules

- Setup charges are priced and managed by the ONEVO operator via `/admin/v1/tenants/{tenantId}/billing/one-time-charges`.
- They are billed **once** — not monthly or annually. They cover one-off operator labour such as job family creation, employee invites, or role and permission configuration.
- The first invoice a tenant receives **may include both** recurring subscription line items and one-time setup line items together. The customer is NOT required to make two separate payments — both charge types appear as distinct line items on the same invoice and are settled in a single payment.
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

---

## Flow Steps

### Step 1: Navigate to Billing

- **UI:** Settings sidebar > Billing & Subscription. Dashboard shows:
  - Active packs and add-ons with their current rates
  - Active employee count and enrolled device count (billing basis)
  - Current billing cycle dates
  - Next invoice date and estimated amount
  - Invoice history (view / download)
  - Billing contact email
- **API:** `GET /api/v1/billing/subscription`
- **Backend:** `BillingService.GetCurrentSubscriptionAsync()`
- **DB:** `tenant_subscriptions`, `subscription_plans`

### Step 2: View Active User / Device Count

- **UI:** Expandable breakdown — active employees by department, enrolled devices by department. Read-only. Helps the tenant understand how their invoice is calculated.
- **API:** `GET /api/v1/billing/active-users`, `GET /api/v1/billing/enrolled-devices`
- **Backend:** `BillingService.GetActiveUserCountAsync()`, `BillingService.GetEnrolledDeviceCountAsync()`
- **DB:** `employees` (status filter), `registered_agents` (status filter), `billing_snapshots`

### Step 3: View Invoice History

- **UI:** Table of past invoices — date, billing basis (user/device count), rate, total, status (paid/pending). Each row has a **Download PDF** link.
- **API:** `GET /api/v1/billing/invoices`
- **Backend:** `BillingService.GetInvoiceHistoryAsync()`
- **DB:** `subscription_invoices`

### Step 4: Add a New Pack or Add-on (Self-Service Upgrade)

Tenant admins can add packs and the Chat AI add-on directly when their commercial model and payment policy allow self-service upgrades. Subscription tenants use the configured payment gateway (`stripe` or `payhere`). Full-license tenants route new purchases through ONEVO sales/operator approval unless the contract explicitly allows gateway-collected add-ons.

- **UI:** "Available Add-ons" section shows all packs and add-ons the tenant has not purchased. Each card shows:
  - Pack / add-on name and modules included
  - Price per user or per device per month
  - Estimated monthly cost based on current active user / device count
  - Proration amount if adding mid-cycle
  - **"Add [Pack Name]"** button
- **API:** `POST /api/v1/billing/modules/{moduleId}/add`
- **Backend:**
  1. Validates a payment method is on file for the configured gateway (`stripe` or `payhere`)
  2. Charges proration through the selected gateway
  3. Updates the tenant module entitlement registry through module interfaces
  4. Publishes `SubscriptionChangedEvent` → feature flag service activates new modules immediately
  5. Writes audit log entry
- **DB:** `tenant_feature_flags`, `tenant_subscriptions`

**Note:** Pack removal (downgrade) is not self-service — tenant contacts ONEVO. This prevents accidental data access loss.

### Step 5: Upgrade Nudge (In-App)

Locked features across the app surface an upgrade prompt to guide tenant admins to the billing section.

- **UI:** Lock icon on any feature from an unpurchased pack. Tooltip: "Available in [Pack Name] — from $X/user/month. **Add it in Billing.**" Clicking the lock navigates to the billing section with that pack pre-highlighted in the Available Add-ons section.
- No API call from the lock icon itself — it is a frontend navigation cue only.

---

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Gateway payment method missing | Add pack blocked | "Please add a payment method before adding new modules." |
| Gateway charge fails | Module not activated | "Payment failed. Please check your payment method and try again." |
| Active user count API unavailable | Cached snapshot used | Count shown with "(estimate)" label |
| Invoice PDF unavailable | Retry link shown | "Invoice PDF is being generated. Try again shortly." |

---

## Events Triggered

- `BillingSnapshotTakenEvent` — end-of-month background job, triggers invoice generation
- `SubscriptionChangedEvent` → feature flag service updates active modules for the tenant
- `AuditLogEntry` (action: `billing.module_added`) → [[modules/auth/audit-logging/overview|Audit Logging]]

---

## Related Flows

- [[developer-platform/userflow/provisioning-flow|Provisioning Flow]] — initial pack assignment by ONEVO operator
- [[developer-platform/userflow/tenant-management|Tenant Management]] — operator changes plan or removes packs via Developer Console
- [[Userflow/Configuration/tenant-settings|Tenant Settings]] — billing contact email

## Module References

- [[modules/shared-platform/subscriptions-billing/overview|Subscriptions Billing]]
- [[backend/module-catalog|Module Catalog]] — full pack and add-on definitions
- [[modules/notifications/overview|Notifications]] — invoice and billing event emails
