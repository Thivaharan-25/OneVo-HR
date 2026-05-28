# Tenant Provisioning â€” Complete 4-Step Wizard

## Purpose

The tenant creation wizard is the **only entry point** for creating a company in ONEVO. There is no public self-signup, no customer-facing registration endpoint, and no checkout flow. Every company is provisioned by an ONEVO operator after a sales agreement is closed.

The wizard collects four categories of information in sequence. After the wizard completes and the tenant is activated, all ongoing management happens from the **Tenant Detail page** â€” accessible by clicking any tenant row in the Tenants list.

---

## Wizard Entry

**Location:** Platform Management â†’ Tenants â†’ `+ Create Tenant` button (top-right)

**Guard:** Button is visible only to accounts with `platform.tenants.create`. If the account lacks this permission the button does not render; it is not shown as disabled.

**Wizard state persistence:**
- Step 1 writes a provisioning draft to the database before Step 2 begins. If the operator closes the wizard after Step 1, the tenant appears in the Tenants list with status `provisioning` and an **In Progress** yellow badge. Clicking that row reopens the wizard at the last incomplete step.
- Steps 2, 3, and 4 save incrementally. Losing browser state after any step does not lose the data already saved.
- Step 1 data is not saved until the operator clicks **Next** at the end of Step 1 â€” closing the browser before that point leaves no record.

**Wizard route:** `/platform/tenants/new` with sub-routes `/platform/tenants/new/step-1`, `/platform/tenants/new/step-2`, `/platform/tenants/new/step-3`, `/platform/tenants/new/step-4`, `/platform/tenants/new/review`.

---

## Step 1 â€” Organization Info

### Screen Header

| Element | Value |
|---|---|
| Page title | "Create Tenant" |
| Subtitle | "Set up a new tenant organization on the OneVo platform." |
| Progress indicator | Step 1 of 4 highlighted â€” "Organization Info" |
| Sidebar summary | Tenant Setup Summary panel on right: lists all 4 steps with current step highlighted in blue, others in gray |

### Fields

#### Company Name
| Property | Value |
|---|---|
| Label | "Company Name" |
| Type | Text input |
| Required | Yes â€” red asterisk shown |
| Placeholder | "e.g., TechNova Solutions" |
| Min length | 2 characters |
| Max length | 100 characters |
| Validation â€” on blur | Minimum length check |
| Validation â€” on submit | Non-empty, within length range |
| Error â€” too short | "Company name must be at least 2 characters." |
| Error â€” too long | "Company name cannot exceed 100 characters." |
| Error â€” empty | "Company name is required." |

#### Legal Company Name
| Property | Value |
|---|---|
| Label | "Legal Company Name" |
| Type | Text input |
| Required | Yes |
| Placeholder | "e.g., TechNova Solutions Inc." |
| Min length | 2 characters |
| Max length | 150 characters |
| Note | This is the registered legal name used in invoices and compliance documents. May differ from display name. |
| Validation â€” on blur | Minimum length check |
| Error â€” too short | "Legal company name must be at least 2 characters." |
| Error â€” too long | "Legal company name cannot exceed 150 characters." |
| Error â€” empty | "Legal company name is required." |

#### Domain
| Property | Value |
|---|---|
| Label | "Domain" |
| Type | Text input with globe icon |
| Required | Yes |
| Placeholder | "e.g., technova.com" |
| Help text | "This will be used for tenant login and email routing." |
| Validation â€” format | Must match `^[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,}$` â€” lowercase only, no `https://`, no trailing slash |
| Validation â€” uniqueness | `GET /admin/v1/tenants/validate?domain={value}` called on blur. If domain already exists returns `409` with `"code": "domain_taken"` |
| Validation â€” reserved | Domains matching ONEVO internal domains (`onevo.io`, `console.onevo.io`, `app.onevo.io`) are rejected |
| Error â€” format | "Enter a valid domain, e.g. company.com â€” no https:// prefix." |
| Error â€” taken | "This domain is already registered to another tenant." |
| Error â€” reserved | "This domain is reserved and cannot be used." |
| Error â€” empty | "Domain is required." |

#### Tenant ID
| Property | Value |
|---|---|
| Label | "Tenant ID (Auto-generated)" |
| Type | Read-only text display |
| Value | Auto-generated on page load â€” format: `TEN-YYYYMMDD-XXXX` where `YYYYMMDD` is today's date and `XXXX` is a zero-padded sequential number, e.g. `TEN-20250520-0009` |
| Help text | "A unique identifier will be used across the platform." |
| Editable | No â€” operator cannot change this |
| Note | Final tenant ID is assigned on `POST /admin/v1/tenants`; the preview shown is a suggested value only. Backend generates the authoritative ID. |

#### Industry
| Property | Value |
|---|---|
| Label | "Industry" |
| Type | Read-only label |
| Required | N/A |
| Value | "Technology / IT" (pre-set for Phase 1) |
| Note | Phase 1 serves IT companies only. Shown as a static label â€” not a dropdown. Multi-industry support is deferred to a future phase. Value stored as `'Technology'` in `tenants.industry`. |
| Editable | No |

#### Estimated Employee Count
#### Estimated Employee Count
| Property | Value |
|---|---|
| Label | "Estimated Employee Count" |
| Type | Number input |
| Required | Yes |
| Placeholder | "Enter estimated employee count" |
| Note | Used for sales context and draft estimates only. It does not define the subscription plan or final invoice quantity. Tenant owner confirms the real total employee count before first invoice generation. |
| Error - empty | "Estimated employee count is required." |
#### Company Description
| Property | Value |
|---|---|
| Label | "Company Description (Optional)" |
| Type | Textarea |
| Required | No |
| Placeholder | "Briefly describe the company and its primary business." |
| Max length | 500 characters |
| Character counter | Shown below â€” "0 / 500" updating live |
| Error â€” too long | "Description cannot exceed 500 characters." |

#### Phone Number
| Property | Value |
|---|---|
| Label | "Phone Number (Optional)" |
| Type | Text input with phone icon |
| Required | No |
| Placeholder | "e.g., +1 (555) 123-4567" |
| Format | E.164 international format â€” must start with `+` and country code |
| Validation â€” on blur | If non-empty: must match E.164 pattern `^\+[1-9]\d{6,14}$` |
| Error â€” format | "Enter a valid international phone number starting with +." |

#### Website
| Property | Value |
|---|---|
| Label | "Website (Optional)" |
| Type | Text input with link icon |
| Required | No |
| Placeholder | "e.g., https://www.technova.com" |
| Validation â€” on blur | If non-empty: must be a valid URL starting with `https://` |
| Error â€” format | "Enter a valid URL starting with https://." |

### Step 1 Actions

| Button | Position | Behavior |
|---|---|---|
| Cancel | Bottom-left | Opens confirmation dialog: "Cancel tenant creation? Any unsaved data will be lost." -> OK navigates to `/platform/tenants`. |
| Previous | Bottom-right, secondary | Disabled on Step 1 â€” grayed out, non-clickable |
| Next | Bottom-right, primary blue | Validates all fields â†’ if valid, calls `POST /admin/v1/tenants` â†’ on success navigates to Step 2 |

### Step 1 API Call

**Endpoint:** `POST /admin/v1/tenants`

**Request body:**
```json
{
  "company_name": "TechNova Solutions",
  "legal_company_name": "TechNova Solutions Inc.",
  "domain": "technova.com",
  "industry": "Technology",
  "estimated_employee_count": 120,
  "description": "Cloud-based HR and workforce management tools for growing tech companies.",
  "phone_number": "+15551234567",
  "website": "https://www.technova.com"
}
```

**Response (201 Created):**
```json
{
  "tenant_id": "a3f1c2d4-...",
  "tenant_code": "TEN-20250520-0009",
  "status": "provisioning",
  "created_at": "2025-05-20T10:24:00Z"
}
```

**Error responses:**

| HTTP | Code | Condition | Display |
|---|---|---|---|
| 409 | `domain_taken` | Domain already registered | Inline error on Domain field |
| 409 | `company_name_taken` | Exact company name already exists | Inline error on Company Name field |
| 422 | `validation_failed` | Field-level validation failures | Inline errors per field |
| 403 | `permission_denied` | Account lacks `platform.tenants.create` | Toast: "You do not have permission to create tenants." |

**State written:**
- New row in `tenants`: `id`, `tenant_code`, `company_name`, `legal_company_name`, `domain`, `industry`, `estimated_employee_count`, `description`, `phone_number`, `website`, `status = 'provisioning'`, `created_at`, `created_by` (platform account ID)
- New row in `tenant_provisioning_states`: `tenant_id`, `step_1_complete = true`, `step_2_complete = false`, `step_3_complete = false`, `step_4_complete = false`, `activated = false`

---

## Step 2 â€” Admin Account

### Screen Header

| Element | Value |
|---|---|
| Step label | "Admin Account" |
| Description | "Create the primary admin account for this tenant organization." |
| Progress indicator | Step 2 of 4 highlighted |

### Fields

#### First Name
| Property | Value |
|---|---|
| Label | "First Name" |
| Type | Text input |
| Required | Yes |
| Placeholder | "e.g., James" |
| Min length | 1 character |
| Max length | 50 characters |
| Validation | Non-empty, within length |
| Error â€” empty | "First name is required." |
| Error â€” too long | "First name cannot exceed 50 characters." |

#### Last Name
| Property | Value |
|---|---|
| Label | "Last Name" |
| Type | Text input |
| Required | Yes |
| Placeholder | "e.g., Anderson" |
| Min length | 1 character |
| Max length | 50 characters |
| Error â€” empty | "Last name is required." |
| Error â€” too long | "Last name cannot exceed 50 characters." |

#### Email Address
| Property | Value |
|---|---|
| Label | "Email Address" |
| Type | Email input |
| Required | Yes |
| Placeholder | "e.g., james.anderson@technova.com" |
| Validation â€” format | Standard email format `^[^@\s]+@[^@\s]+\.[^@\s]+$` |
| Validation â€” domain | Email domain does NOT have to match the tenant domain â€” some owners use personal domains. No blocking validation on domain match. |
| Validation â€” uniqueness within tenant | `GET /admin/v1/tenants/validate?adminEmail={value}&tenantId={id}` â€” same email can exist in other tenants but cannot be a duplicate pending invite for this exact tenant |
| Error â€” format | "Enter a valid email address." |
| Error â€” duplicate invite | "An invite has already been sent to this address for this tenant." |
| Error â€” empty | "Email address is required." |
| Note | The operator does not create a password. The admin sets their password via the invite link emailed after Step 4/activation. |

#### Role Assignment
| Property | Value |
|---|---|
| Label | "Role" |
| Type | Single-select dropdown |
| Required | Yes |
| Default | "Tenant Owner" (pre-selected) |
| Options | Tenant Owner, HR Admin, System Administrator |
| Note | Specific permission set applied to this role is resolved from the module catalog after Step 3 completes. The label selected here is stored; the permission codes are materialized during activation. |
| Error â€” empty | "Role assignment is required." |

#### Send Invite Email
| Property | Value |
|---|---|
| Label | "Send invitation email after activation" |
| Type | Checkbox |
| Default | Checked |
| Note | When checked, an invitation email is sent to the admin email address when the tenant is activated (after Step 4 and Review & Confirm). When unchecked, the invite must be sent manually from the Tenant Detail page. |

### Step 2 API Call

**Endpoint:** `PATCH /admin/v1/tenants/{id}/admin-account`

**Request body:**
```json
{
  "first_name": "James",
  "last_name": "Anderson",
  "email": "james.anderson@technova.com",
  "role_label": "Tenant Owner",
  "send_invite_on_activation": true
}
```

**Response (200 OK):**
```json
{
  "admin_account_id": "b2e4d6f8-...",
  "invite_status": "pending_activation",
  "step_2_complete": true
}
```

**State written:**
- New row in `users` for this tenant: `id`, `tenant_id`, `email`, `first_name`, `last_name`, `status = 'invited'`, `role_label`, `send_invite_on_activation`
- `tenant_provisioning_states.step_2_complete = true`

**Error responses:**

| HTTP | Code | Condition |
|---|---|---|
| 409 | `invite_already_sent` | Duplicate pending invite for same email + tenant |
| 422 | `validation_failed` | Field-level failures |
| 404 | `tenant_not_found` | Tenant ID from Step 1 not found |

---

## Step 3 â€” Subscription Plan

### Screen Header

| Element | Value |
|---|---|
| Step label | "Subscription Plan" |
| Description | "Choose a subscription plan and configure commercial terms for this tenant." |
| Progress indicator | Step 3 of 4 highlighted |

### Fields

#### Subscription Plan
| Property | Value |
|---|---|
| Label | "Subscription Plan" |
| Type | Single-select dropdown (rich options â€” each option shows plan name, included module count, base price range) |
| Required | Yes |
| Placeholder | "Select a plan" |
| API source | `GET /admin/v1/subscription-plans` â€” loads all active plans |
| On change | Triggers module list refresh below and price recalculation |
| Error â€” empty | "Subscription plan is required." |

#### Commercial Model
| Property | Value |
|---|---|
| Label | "Commercial Model" |
| Type | Radio button group |
| Required | Yes |
| Options | Subscription (recurring billing), Full License + Maintenance (one-time license fee with recurring maintenance) |
| Default | "Subscription" |
| On change | Toggles visibility of Billing Cycle (only for Subscription) and Full License Payment fields (only for Full License) |

#### Billing Cycle
| Property | Value |
|---|---|
| Label | "Billing Cycle" |
| Type | Not shown in operator tenant creation |
| Required | No |
| Visible | Tenant owner selects monthly or annual during subscription confirmation |
| Options | Monthly, Annual |
| Note | Developer Platform may define supported cycles per plan, but the tenant owner chooses the billing cycle before the first invoice is generated. |
#### Billing Start Date
| Property | Value |
|---|---|
| Label | "Billing Start Date" |
| Type | Date picker |
| Required | Yes |
| Min value | Today's date |
| Max value | 90 days from today |
| Format | DD/MM/YYYY displayed; stored as ISO 8601 `YYYY-MM-DD` |
| Error â€” empty | "Billing start date is required." |
| Error â€” past date | "Billing start date cannot be in the past." |

#### Included Modules
| Property | Value |
|---|---|
| Label | "Included Modules" |
| Type | Multi-select checkbox list â€” grouped by ONEVO product pillar |
| Required | At least one module must be selected |
| Source | Determined by selected plan's `included_module_keys` array â€” pre-checked modules from plan cannot be unchecked |
| Additional modules | Operator can add purchasable add-on modules on top of plan-included modules |
| Price effect | Selecting/deselecting add-on modules updates an estimate from `module_catalog.price_brackets`. Final first invoice pricing uses the tenant-owner-confirmed total employee count. |
| Display | Each module shows: module name, pillar badge (HR / WI / WorkSync), pricing unit (per employee/per device/flat), base price |
| Error | "At least one module must be selected." |

**Module groups displayed (Phase 1 sellable modules only):**

| Group | Modules shown | Notes |
|:---|:---|:---|
| **HR Management (Package 1)** | Core HR, Leave Management, Calendar | Performance, Payroll, Skills, Learning, Recruitment, Grievance, Expense are Phase 2 â€” not shown |
| **Workforce Intelligence (Package 1)** | Activity Monitoring, Workforce Presence, Identity Verification, Exception Engine, Productivity Analytics | App Usage Tracking is part of Activity Monitoring. Agent Gateway is infrastructure â€” not a sellable module. |
| **WorkSync (Package 2)** | Work Management, Chat, Chat AI, Documents, Reports, GitHub Integration | Projects & Sprints, OKR, and Roadmaps are features within Work Management, not separate sellable modules. Chat and Chat AI are separately sellable. |
| **Foundation (always included, not selectable)** | Authentication, Tenant Configuration, Roles & Permissions, Notifications, Org Structure, Workflow / Automation Engine | Pre-checked and locked. Cannot be unchecked. Provisioned automatically for every tenant. |

**Workflow / Automation Engine:** Foundation module â€” always included, not shown as a selectable item. Automatically provisioned on activation. Powers leave approval, expense approval, attendance correction, exception escalation, and performance review routing. Tenant admins configure workflow definitions post-activation.

#### Calculated Price Display
| Property | Value |
|---|---|
| Label | "Calculated Monthly Price" / "Calculated Annual Price" |
| Type | Read-only computed field |
| Value | Estimated recurring amount from selected plan/add-ons and estimated employee count |
| Updates | Live recalculation on module selection change or estimated employee count change |
| Display | "Calculated: Â£4,200 / month" with breakdown link |

#### Price Override
| Property | Value |
|---|---|
| Label | "Override Price (Optional)" |
| Type | Currency input |
| Required | No |
| Placeholder | "Leave blank to use calculated price" |
| Note | When filled, the effective price is this override value. Calculated price is preserved in DB for audit. Override requires an audit reason. |
| Linked field | "Override Reason" (required when override is entered) |

#### Override Reason
| Property | Value |
|---|---|
| Label | "Reason for Price Override" |
| Type | Textarea |
| Required | Yes â€” only when Override Price is filled |
| Min length | 10 characters |
| Max length | 500 characters |
| Error â€” empty when override set | "Reason is required when overriding the calculated price." |

#### Payment Collection Mode
| Property | Value |
|---|---|
| Label | "Payment Collection Mode" |
| Type | Radio button group |
| Required | Yes |
| Options | Gateway (Paddle or PayHere), Manual (bank transfer, invoice) |
| Note | Gateway is the standard path. Manual is for enterprise/negotiated deals only. |

#### Payment Gateway
| Property | Value |
|---|---|
| Label | "Payment Gateway" |
| Type | Single-select dropdown |
| Required | Yes â€” only when Collection Mode = Gateway |
| Visible | Only when Collection Mode = Gateway |
| Options | Loaded from `GET /admin/v1/payment-gateways` â€” shows provider name (Stripe / Paddle / PayHere) + environment (sandbox / production) |
| Error â€” empty | "Payment gateway is required for gateway collection." |

#### Manual Billing Evidence
| Property | Value |
|---|---|
| Label | "Billing Evidence / Reference" |
| Type | File upload + text reference |
| Required | Yes â€” only when Collection Mode = Manual |
| Visible | Only when Collection Mode = Manual |
| Accepted file types | PDF, JPG, PNG â€” max 10MB |
| Alternative | External reference number instead of file upload |
| Error â€” empty when manual | "Billing evidence or reference is required for manual collection." |

#### AI Monthly Token Limit
| Property | Value |
|---|---|
| Label | "AI Monthly Token Limit" |
| Type | Number input |
| Required | Yes â€” only when selected plan/modules include AI capability (`chat_ai`) |
| Visible | Only when AI-capable modules are selected |
| Min value | 1,000 |
| Max value | 100,000,000 |
| Unit | Tokens per month |
| Placeholder | "e.g., 500000" |
| Error â€” empty when AI selected | "AI token limit is required when AI-capable modules are included." |
| Error â€” below min | "AI token limit must be at least 1,000 tokens per month." |

#### Tenant Storage Limit
| Property | Value |
|---|---|
| Label | "Tenant Storage Limit" |
| Type | Number input + unit selector (GB / TB) |
| Required | Yes â€” for all tenants |
| Visible | Always shown |
| Min value | 1 GB |
| Max value | 1,000 TB |
| Note | Storage is a **single shared pool for the entire tenant** â€” not split per module. All modules draw from it: uploaded files, HR documents, screenshots, payslips, verification photos, attachments. Stored as `tenant_storage_limit_gb` on `tenant_subscriptions`. |
| Error â€” empty | "Tenant storage limit is required." |

#### Payment Exception / Grace Period
| Property | Value |
|---|---|
| Label | "Payment Exception / Grace Period (Optional)" |
| Type | Toggle + date range picker |
| Required | No |
| Description | "Approved period during which the tenant may use the system without an active payment." |
| Fields when enabled | Grace period start date, Grace period end date, Approved reason (required, min 10 chars) |
| Error â€” end before start | "Grace period end date must be after start date." |
| Error â€” no reason | "Reason is required for a payment exception." |

#### Maintenance Fields (Full License model only)
Shown only when Commercial Model = Full License + Maintenance:

| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| License Payment | "Full License Payment Amount" | Currency input | Yes | One-time license fee paid |
| Maintenance Rate | "Annual Maintenance Rate (%)" | Number input (0â€“100) | Yes | Percentage of license fee |
| Maintenance Renewal Date | "Maintenance Renewal Date" | Date picker | Yes | Annual renewal date |
| Maintenance Collection | "Maintenance Collection Mode" | Radio: Gateway / Manual / Waived | Yes | How recurring maintenance is collected |

### Step 3 Price Calculation Logic

1. Backend reads `module_catalog.price_brackets` for each selected module
2. Uses the tenant-owner-confirmed employee count during subscription confirmation to select the plan employee-count pricing tier. The Step 1 estimate is profile/sales context only and is not the final invoice quantity.
3. Sums bracket unit prices across all selected modules
4. If Commercial Model = Annual, multiplies by 12 with optional annual discount from plan
5. If Override Price is entered, stored as `override_price`; calculated price stored as `calculated_price` â€” both preserved in DB

### Step 3 API Call

**Endpoint:** `PATCH /admin/v1/tenants/{id}/subscription`

**Request body:**
```json
{
  "plan_id": "plan-enterprise-v1",
  "commercial_model": "subscription",
  "billing_cycle": "monthly",
  "billing_start_date": "2025-06-01",
  "selected_module_keys": ["core_hr", "leave", "workforce_presence", "activity_monitoring", "worksync_projects"],
  "collection_mode": "gateway",
  "payment_gateway_id": "gw-paddle-global-prod",
  "calculated_price": 4200.00,
  "override_price": null,
  "override_reason": null,
  "currency": "GBP",
  "ai_monthly_token_limit": 500000,
  "tenant_storage_limit_gb": 500,
  "payment_exception_start": null,
  "payment_exception_end": null,
  "payment_exception_reason": null
}
```

**Response (200 OK):**
```json
{
  "subscription_snapshot_id": "snap-...",
  "entitlements_synced": true,
  "step_3_complete": true
}
```

**Side effects:**
- `tenant_module_entitlements` rows created for each selected module with `status = 'provisioning'` â€” not yet `active`; they become `active` when tenant is activated
- `tenant_subscriptions` snapshot written with all commercial terms
- Price calculation preserved: both `calculated_price` and `override_price` stored separately

---

## Step 4 â€” Configuration

### Screen Header

| Element | Value |
|---|---|
| Step label | "Configuration" |
| Description | "Configure default policies, setup services, and operational settings for this tenant." |
| Progress indicator | Step 4 of 4 highlighted |
| Note | Only configuration relevant to the modules selected in Step 3 is shown. If Workforce Intelligence is not selected, monitoring settings are hidden. |

### Section: Work Mode

| Field | Label | Type | Required | Options | Notes |
|---|---|---|---|---|---|
| Work Mode | "Primary Work Mode" | Radio | Yes | Hybrid, Remote, On-site | Drives default policy suggestions for monitoring, leave, and device management |

### Section: Monitoring & Privacy (shown only if Activity Monitoring or Workforce Presence selected)

| Field | Label | Type | Required | Options | Notes |
|---|---|---|---|---|---|
| Monitoring Transparency Mode | "Employee Transparency Mode" | Radio | Yes | Full Transparency (employees see all monitoring data), Summary Only (employees see summaries), Hidden (employees see no monitoring data) | Compliance-critical â€” operators must choose consciously |
| Desktop Agent Transparency | "Desktop Agent Visibility" | Radio | Yes | Visible to employees (tray icon always shown), Silent (no tray icon) | Local law may require visible agent â€” operator is responsible |
| Data Collection Scope | "Collect Application Usage" | Toggle | Yes | On / Off | Default On when monitoring modules selected |
| Screenshot Capture | "Enable Screenshot Capture" | Toggle | Yes | On / Off | Default Off â€” requires explicit opt-in |
| Camera Photo Capture | "Enable Camera Photo Verification" | Toggle | Yes | On / Off | Default Off â€” requires explicit opt-in. WorkPulse tray captures a photo for identity verification events (clock-in, absence spot-check). Subject to biometric consent and retention policy. |
| Input Counting | "Enable Keyboard/Mouse Activity Counting" | Toggle | Yes | On / Off | Counts only â€” never captures content |

### Section: Configuration Template (always shown)

Applies a preset bundle of operational settings (timezone, currency, work week, privacy mode, data retention defaults). The tenant country defaults from Step 1 pre-select the best match.

| Field | Label | Type | Required | Options | Notes |
|---|---|---|---|---|---|
| Configuration Template | "Configuration Template" | Dropdown | No | Loaded from `GET /admin/v1/configuration-templates?type=configuration` | Pre-fills the Org Defaults fields below; operator can override individual fields after selection |

### Section: Org Defaults (always shown)

Pre-filled when a Configuration Template is selected above. All fields are individually editable regardless.

| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| Default Timezone | "Primary Timezone" | Dropdown (IANA timezone list) | Yes | Pre-filled from Step 1 country default |
| Date Format | "Date Display Format" | Radio | Yes | DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD |
| Default Currency | "Reporting Currency" | Dropdown (currency codes) | Yes | Pre-filled from Step 1 country default |
| Work Week Days | "Work Week" | Multi-select (Monâ€“Sun) | Yes | Default Monâ€“Fri |
| Work Start Time | "Default Work Start" | Time picker | Yes | Default 09:00 |
| Work End Time | "Default Work End" | Time picker | Yes | Default 17:30 |
| Privacy Mode | "Employee Privacy Mode" | Radio | Yes | Full Transparency / Summary Only / Covert |

### Section: Monitoring Policy (shown only if Activity Monitoring or Workforce Presence selected)

| Field | Label | Type | Required | Options | Notes |
|---|---|---|---|---|---|
| Monitoring Policy Template | "Monitoring Policy Template" | Dropdown | No | Loaded from `GET /admin/v1/configuration-templates?type=monitoring_policy` â€” auto-selects template matching tenant `industry_profile_tag` if one exists | Seeds `monitoring_feature_toggles` for this tenant; individual toggles can be adjusted after apply |
| Monitoring Transparency Mode | "Employee Transparency Mode" | Radio | Yes | Full Transparency, Summary Only, Hidden | Compliance-critical â€” operators must choose consciously |
| Desktop Agent Transparency | "Desktop Agent Visibility" | Radio | Yes | Visible (tray icon shown), Silent (no tray icon) | Local law may require visible agent |
| Data Collection Scope | "Collect Application Usage" | Toggle | Yes | On / Off | Default On when monitoring modules selected |
| Screenshot Capture | "Enable Screenshot Capture" | Toggle | Yes | On / Off | Default Off â€” requires explicit opt-in |
| Camera Photo Capture | "Enable Camera Photo Verification" | Toggle | Yes | On / Off | Default Off â€” requires explicit opt-in. WorkPulse tray captures a photo for identity verification events (clock-in, absence spot-check). Subject to biometric consent and retention policy. |
| Input Counting | "Enable Keyboard/Mouse Activity Counting" | Toggle | Yes | On / Off | Counts only â€” never captures content |

### Section: Job Family (shown only if Core HR selected)

| Field | Label | Type | Required | Options | Notes |
|---|---|---|---|---|---|
| Job Family Template | "Job Family Template" | Multi-select dropdown | No | Loaded from `GET /admin/v1/configuration-templates?type=job_family` | Each selected template seeds one `job_families` + its `job_levels`. Role links are resolved immediately if the matching role template was already applied in this provisioning session; otherwise `pending_role_template_id` is set and resolved when roles are applied |

### Section: Leave Policy (shown only if Leave Management selected)

| Field | Label | Type | Required | Options | Notes |
|---|---|---|---|---|---|
| Leave Policy Template | "Leave Policy Template" | Dropdown | No | Loaded from `GET /admin/v1/configuration-templates?type=leave_policy` | Seeds `leave_types` and `leave_policies`. If a rule references a job level rank that doesn't exist yet, a warning is returned but apply succeeds |
| Leave Year Start | "Leave Year Start Month" | Dropdown | Yes | Januaryâ€“December | Defines when annual leave entitlement resets |
| Leave Approval | "Leave Approval Flow" | Radio | Yes | Manager Approval Required, Auto-Approved | Default for new employees |
| Carry-Forward Policy | "Leave Carry-Forward" | Radio | Yes | No carry-forward, Limited (max days input), Unlimited | |
| Carry-Forward Max Days | "Maximum Carry-Forward Days" | Number input | Required if limited | 1â€“365 | |

### Section: App Allowlist (shown only if App Usage Tracking or Activity Monitoring selected)

| Field | Label | Type | Required | Options | Notes |
|---|---|---|---|---|---|
| App Allowlist Template | "App Allowlist Template" | Dropdown | No | Loaded from `GET /admin/v1/configuration-templates?type=app_allowlist` | Seeds `app_allowlists` at tenant scope; entries can be edited after apply |

### Section: Data Import (shown only if Data Import module selected)

| Field | Label | Type | Required | Options | Notes |
|---|---|---|---|---|---|
| Data Import Source | "Primary Migration Source" | Dropdown | No | PeopleHR, CSV/Excel, None | Narrows the template list |
| Import Mapping Template | "Import Mapping Template" | Dropdown | No | Loaded from `GET /admin/v1/configuration-templates?type=data_import_mapping` | Seeds field mapping definition; editable after apply |

### Section: Onboarding (shown only if Core HR selected)

| Field | Label | Type | Required | Options | Notes |
|---|---|---|---|---|---|
| Onboarding Template | "Onboarding Checklist Template" | Dropdown | No | Loaded from `GET /admin/v1/configuration-templates?type=onboarding` | Seeds onboarding task template; tasks are instantiated per new hire at onboarding time, not immediately |
| Target Role Template | "Target Role" | Dropdown | No | Global role templates | Optional scope. Null = all roles |
| Target Job Family Template | "Target Job Family" | Dropdown | No | Loaded from selected/applied `job_family` templates | Optional scope. Null = all job families |
| Target Job Level | "Target Job Level" | Dropdown / rank selector | No | Levels from selected Target Job Family Template | Optional scope. Requires Target Job Family Template when selected |
| Target Department | "Target Department" | Text / dropdown when departments already exist | No | Existing or future department name | Optional scope. Null = all departments |

**Onboarding targeting rule:** The onboarding template applies to a new hire only when all non-empty targeting fields match. Target Job Level cannot be selected without Target Job Family Template, because level rank/name is only meaningful inside a job family.

### Section: Setup Services

Setup services are module-connected tasks. Free/global services are auto-listed based on selected modules. Paid services require explicit selection.

**Display:** Checklist table with columns: Service Name, Module, Type (Free / Paid), Status (Not Started / In Progress / Complete).

| Column | Description |
|---|---|
| Service Name | Human-readable name, e.g. "Initial Org Structure Setup", "Leave Policy Configuration" |
| Module | Which ONEVO module this service relates to |
| Type | Free (included with module) or Paid (billed separately) |
| Status | Not Started, In Progress, Complete |
| Configure button | Opens a side panel with service-specific settings |

**Rule:** Free setup services connected to selected modules are auto-added to the checklist. Operator cannot remove free services â€” they can only mark them complete. Paid services are opt-in additions.

**Rule:** Setup service completion status does not block activation, but incomplete free services show a warning in the Review step.

### Step 4 API Call

**Endpoint:** `PATCH /admin/v1/tenants/{id}/settings`

**Request body:**
```json
{
  "work_mode": "hybrid",
  "monitoring": {
    "transparency_mode": "full_transparency",
    "agent_visibility": "visible",
    "collect_app_usage": true,
    "screenshot_capture": false,
    "input_counting": true
  },
  "leave": {
    "leave_year_start_month": 1,
    "default_annual_leave_days": 25,
    "leave_approval": "manager_required",
    "carry_forward": "limited",
    "carry_forward_max_days": 5
  },
  "org": {
    "reporting_currency": "GBP",
    "primary_timezone": "Europe/London",
    "date_format": "DD/MM/YYYY"
  },
  "setup_services": [
    { "service_key": "initial_org_setup", "status": "not_started" },
    { "service_key": "leave_policy_config", "status": "not_started" }
  ],
  "configuration_template_id": "uuid-or-null",
  "monitoring_policy_template_id": "uuid-or-null",
  "job_family_template_ids": [],
  "leave_policy_template_id": "uuid-or-null",
  "app_allowlist_template_id": "uuid-or-null",
  "data_import_mapping_template_id": "uuid-or-null",
  "onboarding_template_id": "uuid-or-null"
}
```

**Template application order (server-enforced):**
1. Configuration template â†’ writes `tenant_settings`
2. Monitoring policy template â†’ writes `monitoring_feature_toggles`
3. Job family templates â†’ writes `job_families` + `job_levels`; resolves role links where possible
4. Leave policy template â†’ writes `leave_types` + `leave_policies`; matches job levels by rank
5. App allowlist template â†’ writes `app_allowlists`
6. Data import mapping template â†’ writes `data_import_mapping_templates`
7. Onboarding template â†’ writes `onboarding_templates` + `onboarding_template_tasks`

Each template generates a row in `tenant_configuration_template_applications`. Warnings from any step are collected and returned in the response.

**Response (200 OK):**
```json
{
  "settings_saved": true,
  "step_4_complete": true,
  "setup_services_added": 2,
  "template_applications": [
    { "template_id": "uuid", "type": "configuration", "status": "applied", "warnings": [] },
    { "template_id": "uuid", "type": "job_family", "status": "applied", "warnings": ["Level 'Senior' role link is pending â€” apply role template 'team-lead' to resolve."] }
  ]
}
```

**State written:**
- `tenant_settings` rows for work_mode, monitoring config, org defaults
- `monitoring_feature_toggles` row (if monitoring policy template applied)
- `job_families` + `job_levels` rows (if job family templates applied)
- `leave_types` + `leave_policies` rows (if leave policy template applied)
- `app_allowlists` rows (if app allowlist template applied)
- `data_import_mapping_templates` rows (if data import template applied)
- `onboarding_templates` + `onboarding_template_tasks` rows (if onboarding template applied)
- `tenant_setup_service_states` rows for each listed service
- `tenant_configuration_template_applications` rows for each applied template
- `tenant_provisioning_states.step_4_complete = true`

---

## Review & Confirm

This is not a data-entry step. It is a read-only summary of all choices from Steps 1â€“4.

### Screen Layout

| Section | What Is Shown | Edit Link |
|---|---|---|
| Organization Info | Company name, legal name, domain, tenant ID, industry, estimated employee count | "Edit" â†’ navigates back to Step 1 in edit mode |
| Admin Account | Admin name, email, role, invite-on-activation setting | "Edit" â†’ Step 2 |
| Subscription Plan | Plan name, commercial model, billing cycle, billing start date, selected modules list, calculated price, override price if any, payment mode, gateway if applicable | "Edit" â†’ Step 3 |
| Configuration | Work mode, monitoring settings, leave defaults, setup services list | "Edit" â†’ Step 4 |
| Warnings | Any incomplete optional items (e.g. "2 setup services marked Not Started") shown as yellow callout â€” not blocking |

### Activation Button

| Element | Value |
|---|---|
| Button label | "Activate Tenant" |
| Position | Bottom-right, primary blue |
| Guard | All 4 step completion flags must be `true` in `tenant_provisioning_states`. If any is false, button shows "Complete required steps" in orange and cannot be clicked. |

### Activation API Call

**Endpoint:** `PATCH /admin/v1/tenants/{id}/provision/confirm`

**Request body:** `{}` â€” no body required; all data already saved in previous steps

**Activation guard â€” backend checks before flipping status:**

| Check | Failure code | Message shown |
|---|---|---|
| `company_name` not null | `missing_company_name` | "Company name is required." |
| `domain` not null and unique | `missing_domain` | "Domain is required." |
| `subscription.commercial_model` set | `missing_commercial_terms` | "Subscription commercial terms must be completed." |
| At least one module entitled | `no_modules_entitled` | "At least one module must be entitled." |
| Admin account set | `no_admin_account` | "An admin account must be created." |
| `step_1_complete = true` through `step_4_complete = true` | `provisioning_incomplete` | "All wizard steps must be completed before activation." |
| AI token limit when AI modules present | `missing_ai_token_limit` | "AI token limit is required." |
| Tenant storage limit not set | `missing_storage_limit` | "Tenant storage limit is required." |
| Manual billing evidence when manual collection | `missing_billing_evidence` | "Billing evidence is required for manual collection." |

**On all checks passed:**

**Response (200 OK):**
```json
{
  "tenant_id": "a3f1c2d4-...",
  "status": "active",
  "activated_at": "2025-05-20T11:15:00Z",
  "invite_email_sent": true
}
```

**State written on activation:**
- `tenants.status` â†’ `'active'`
- `tenant_module_entitlements` rows updated: `status` â†’ `'active'` for all provisioning entitlements
- Tenant role materialized from role template â€” `roles` and `role_permissions` rows created
- If `send_invite_on_activation = true` â†’ invite email sent to admin email via Resend; `users.invite_sent_at` recorded
- Audit log entry: `action = 'tenant.activated'`, actor = platform account ID, target = tenant ID, timestamp

**Error response (422 Unprocessable Entity) when checks fail:**
```json
{
  "error": "activation_blocked",
  "blockers": [
    { "code": "missing_ai_token_limit", "message": "AI token limit is required when AI-capable modules are included." },
    { "code": "missing_billing_evidence", "message": "Billing evidence is required for manual collection." }
  ]
}
```

Frontend renders the blockers as a red callout list above the Activate button.

### Post-Activation State

After activation:
- Tenant appears in Tenants list with green **Active** badge
- Yellow "In Progress" badge is removed
- Tenant is now visible to `/api/v1/*` tenant-facing endpoints
- Admin can log in once they complete set-password via the invite link
- Platform account can click the tenant row to open the full **Tenant Detail page** for ongoing management

---

## Resuming an In-Progress Wizard

When an operator closes the wizard after Step 1 but before activation:

1. Tenant appears in Tenants list with yellow **"In Progress"** badge
2. Clicking the row calls `GET /admin/v1/tenants/{id}` â€” response includes `provisioning_state`
3. Frontend reads `step_1_complete`, `step_2_complete`, `step_3_complete`, `step_4_complete` and navigates to the first incomplete step
4. All previously saved values are pre-populated from the GET response
5. Operator can edit any completed step before activating

---

## Related Documents

- [[developer-platform/modules/tenant-console/end-to-end-logic|Tenant Console End-to-End Logic]] â€” ongoing management after activation
- [[developer-platform/modules/subscription-manager/end-to-end-logic|Subscription Manager]] â€” plan catalog and gateway configuration
- [[developer-platform/modules/module-catalog-manager/end-to-end-logic|Module Catalog Manager]] â€” ONEVO product module pricing and permission ownership
- [[developer-platform/modules/role-template-manager/end-to-end-logic|Role Template Manager]] â€” role templates applied during Manage/Configure
- [[developer-platform/auth|Authentication & Authorization]] â€” platform-admin JWT and impersonation model


