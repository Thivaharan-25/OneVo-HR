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
| Plan base price | Professional = 300/month |
| Module add-on price | Payroll = 80/month |
| Per employee/device price | 3/employee/month or 2/device/month |
| Full license purchase price | Full HR Suite = 10,000 one-time |
| Maintenance price | 18% of license value yearly |
| Trial terms | Free for 30 days |
| Custom enterprise price | Manually entered contract amount |

Module entitlement and pricing decide what the tenant has access to. RBAC decides which users inside the tenant can use those capabilities. These concerns must remain separate.
### Pricing Packs

| Pack | Modules Included | Pricing Unit |
|------|-----------------|--------------|
| **HR Pack** | Org Structure, Core HR, Leave, Calendar, Skills Core | Per active employee / month |
| **Workforce Intelligence Pack** | Workforce Presence, Activity Monitoring, Discrepancy Engine, Identity Verification, Exception Engine, Productivity Analytics + Desktop Agent | Per monitored device / month |
| **WorkSync Pack** | Projects, Tasks, Planning, OKR, Time, Resources, Chat, Collaboration, Analytics, Integrations + IDE Extension | Per active employee / month |
| **Chat AI Add-on** | AI-assisted chat actions, premium AI detections | Per active employee / month |

Future modules (Governance, Skill & Talent Development, Payroll, Performance, etc.) are released as standalone add-ons. When ONEVO introduces a new module, the operator adds it to the catalog in the Developer Console and it appears as a purchasable add-on for all tenants that don't have it.

### Billing Calculation

| Item | Rule |
|------|------|
| HR Pack / WorkSync Pack billing unit | Active employees (`employees.status = 'active'`) at end-of-month snapshot |
| Workforce Intelligence Pack billing unit | Enrolled devices (`registered_agents` with `status = 'active'`) at end-of-month snapshot |
| Chat AI add-on billing unit | Active employees at end-of-month snapshot |
| Billing cycle | Calendar month (1st to last day) |
| Invoice generation | ONEVO generates and sends invoice by 3rd of the following month |
| Proration | New packs/add-ons added mid-cycle are prorated for remaining days. Removals take effect from the next billing cycle. |

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

Tenant admins can add packs and the Chat AI add-on directly — no sales call needed for upgrades.

- **UI:** "Available Add-ons" section shows all packs and add-ons the tenant has not purchased. Each card shows:
  - Pack / add-on name and modules included
  - Price per user or per device per month
  - Estimated monthly cost based on current active user / device count
  - Proration amount if adding mid-cycle
  - **"Add [Pack Name]"** button
- **API:** `POST /api/v1/billing/modules/{moduleId}/add`
- **Backend:**
  1. Validates Stripe payment method is on file
  2. Charges proration via Stripe
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
| Stripe payment method missing | Add pack blocked | "Please add a payment method before adding new modules." |
| Stripe charge fails | Module not activated | "Payment failed. Please check your payment method and try again." |
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
