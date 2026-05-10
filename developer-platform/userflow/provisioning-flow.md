# Manual Customer Provisioning Flow

## Purpose

The provisioning wizard is the **only way** a tenant is created in ONEVO. There is no public self-signup, no public tenant registration endpoint, and no customer-facing checkout flow. Every tenant — regardless of size or plan — is created by an ONEVO operator through this wizard after a sales agreement is reached.

**Use this flow for all tenant creation:**
- Enterprise deal closed by sales
- White-glove onboarding — ONEVO team sets up the environment on behalf of the customer
- Internal test tenants — creating isolated test accounts

**ADE rule:** Do not build or expose a public tenant creation path. `POST /api/v1/tenants` must not exist on the customer-facing API. Tenant creation is always through `POST /admin/v1/tenants` via this console.

---

## Starting the Wizard

1. Navigate to `/tenants`
2. Click **Provision New Customer** (top-right button)
3. The 7-step wizard opens

---

## Draft Behaviour

After Step 1 completes, the tenant exists in `tenants.status = 'provisioning'`. This tenant is **invisible to the main OneVo app** — no customer-facing endpoint returns provisioning-status tenants.

The wizard can be **closed at any point after Step 1** and resumed later:
- The tenant appears in the Tenants list with a yellow **"In Progress"** badge
- Click the row to reopen the wizard at the last completed step
- Any step can be edited before the final confirm in Step 7

---

## Step 1 — Account Setup

**What you fill in:**
- Company name
- Slug (URL-safe identifier, must be unique — validated on blur)
- Country
- Industry
- Legal entity name
- Registration number
- Company size
- Timezone
- Currency

**Action:** Click **Create Tenant**

**API call:** `POST /admin/v1/tenants`

**State written:** New row in `tenants` with `status = 'provisioning'` and `company_size_range`; primary row in `legal_entities` with legal entity name, registration number, `country_id`, `currency_code`, and address; default timezone in `tenant_settings`. The tenant ID is returned and stored for all subsequent wizard steps.

**Country defaults rule:** The UI calls `GET /admin/v1/reference/countries/{countryCode}/defaults` after country selection. Single-timezone countries can auto-fill timezone; multi-timezone countries must show a timezone dropdown. Currency defaults from country but remains editable.

**Note:** If you close the browser before completing this step, nothing is saved — the tenant does not exist yet.

---

## Step 2 — Plan Assignment

**What you fill in:**
- Subscription plan (dropdown of reusable plans from `subscription_plans`; operators do not create a new plan for every tenant)
- Company size price band (same values as the Step 1 company-size dropdown; defaults from the tenant's saved `company_size_range`)
- Modules included in the plan; selecting modules recalculates the per-unit price from `module_catalog.price_brackets`
- Calculated monthly/annual price and optional operator override price
- Monthly AI token limit when the selected modules/plan include AI capability
- Commercial model: `subscription` or `full_license_maintenance`
- Billing start date
- Payment collection mode and gateway provider (`stripe` or `payhere`) for subscription billing
- Full-license payment mode (`manual` or `gateway`) when the commercial model is `full_license_maintenance`
- Maintenance collection mode (`gateway`, `manual`, or `waived`) and gateway provider when maintenance is collected through the system
- Maintenance renewal date and status when the commercial model is `full_license_maintenance`
- Custom contract value, maintenance rate, and pricing overrides when the sales agreement is manually negotiated

**Action:** Click **Save & Continue**

**API call:** `PATCH /admin/v1/tenants/{id}/subscription`

**State written:** `subscription_plans` association updated; commercial model, billing cycle/currency, contract dates, subscription collection mode, gateway provider, gateway references, license payment fields, maintenance collection mode/status/renewal date, selected company-size range, selected module keys, calculated plan price snapshot, optional override price, AI monthly token limit, custom contract value, and pricing overrides set for the tenant.

**Plan rule:** plans are global commercial catalog records. A tenant receives one selected plan plus tenant-specific commercial terms. Custom pricing, discounts, contract value, maintenance rate, billing dates, and manual billing state belong on the tenant subscription/commercial record, not on a new one-off plan unless product intentionally adds a reusable custom plan.

**Dynamic pricing rule:** plan price is the sum of selected module bracket prices for the selected company-size range. Example: `core_hr` at `$3.50` for `51-200` employees plus `work_management` at `$4.00` for `51-200` employees shows `$7.50 per employee`. Changing company size or selected modules recalculates immediately. Operator overrides change the effective price but must preserve the calculated price for audit.

**AI token rule:** when AI capability is included, the operator must set a positive monthly token limit. Non-AI plans store no AI token limit.

**Gateway rule:** Stripe and PayHere are the primary Phase 1 payment gateways. Subscription tenants normally use gateway collection. Full-license tenants may record the one-time license payment manually, but recurring maintenance fees should use Stripe or PayHere when gateway collection is enabled. Gateway API keys, merchant secrets, and webhook secrets are managed through encrypted payment gateway configuration, not returned from APIs.

**Cost rule:** plan pricing and module pricing are commercial inputs. They decide what the tenant has bought, trialed, or been granted. They do not grant user permissions directly. RBAC is applied only after the tenant's entitled modules are resolved.

---

## Step 3 — Module Selection

**What you fill in:**
- Checklist loaded from the reusable `module_catalog`, each module labelled with pillar, phase, default pricing unit, and sellable status
- Toggle which modules are active for this tenant
- For each module, mark the sales state as `available`, `trial`, `quoted`, `purchased`, `maintenance_included`, `subscription_included`, or `disabled`
- Optional module-specific pricing override, currency, start date, and end/trial expiry date

**Action:** Click **Save & Continue**

**API call:** `PUT /admin/v1/tenants/{id}/modules`

**Sales rule:** Future modules must start disabled or available; they are enabled only after sales, trial approval, purchase, or maintenance entitlement is recorded.

**Commercial entitlement rule:** Pricing and module entitlement decide what the tenant has access to. RBAC decides which users inside the tenant can use it. The permission catalog in Step 4 is filtered only after the active module entitlement set is resolved.

**State written:** tenant module entitlement records through the module entitlement registry. This module set becomes the permission boundary for role templates and tenant role management.

**Module cost rule:** module prices may default from `module_catalog`, be included by the selected plan, or be overridden per tenant. The backend must preserve the operator-entered pricing model, price, currency, start date, end/trial expiry date, and sales state for audit and billing. A module in `quoted` or `available` state is visible in the console but is not active for tenant-facing access until it becomes `purchased`, `trial`, `subscription_included`, or `maintenance_included`.

---

## Step 4 - Role Template Setup

**What you fill in:**
- Pick reusable ONEVO starter templates, such as Tenant Owner, HR Admin, Leave Manager, Employee, Workforce Supervisor, or WorkSync Project Manager.
- Create a new reusable operator-managed role template and save it to the global template library when the pattern should be reused for other tenants.
- Create tenant-specific roles directly during provisioning when the role is unique to this customer and should not become a global template.
- Edit permissions on materialized tenant roles before activation, still constrained by the tenant's filtered permission catalog.
- Confirm which templates and tenant-specific roles should exist before owner invite and activation.

**API calls:**
- `GET /admin/v1/tenants/{id}/permissions/catalog`
- `GET /admin/v1/role-templates`
- `POST /admin/v1/role-templates`
- `POST /admin/v1/tenants/{id}/role-templates/{templateId}/apply`
- `GET /admin/v1/tenants/{id}/roles`
- `POST /admin/v1/tenants/{id}/roles`
- `PUT /admin/v1/tenants/{id}/roles/{roleId}/permissions`

**Permission boundary:** the catalog only includes universal permissions and permissions from modules enabled in Step 3. If the tenant bought only Employee Management and Leave, Payroll, Workforce Intelligence, WorkSync, Agent Gateway, and Identity Verification permissions are not shown and cannot be assigned.

**State written:** tenant-scoped `roles` and `role_permissions` through Auth interfaces, plus audit records for every template applied or changed.

**Role independence rule:** role creation does not require job levels. Basic roles are independent permission containers. Job levels, departments, reporting lines, and hierarchy are only needed later for scoped permissions, approval workflows, escalation rules, and organisation-aware access.

**Template rule:** role templates are blueprints, not runtime authorization records. Applying a template materializes normal tenant-scoped roles. Applying the same template twice must be idempotent or require an explicit duplicate-name override; it must never silently create confusing duplicate roles.

---

## Step 5 — Initial Configuration

**What you fill in:**
- Monitoring transparency mode (select: `transparent` | `private` | `disclosed`)
- Leave policy defaults (annual leave accrual method, carry-over cap)
- Desktop agent transparency mode (whether employees see the agent is running)
- Working hours defaults (start time, end time, timezone confirmation)

**Action:** Click **Save & Continue**

**API call:** `PATCH /admin/v1/tenants/{id}/settings`

**State written:** `tenant_settings` rows for the configuration keys above.

---

## Step 6 — Invite Admin

**What you fill in:**
- Customer's super-admin email address
- Customer's super-admin full name

**Action:** Click **Send Invite**

**API call:** `POST /admin/v1/tenants/{id}/invite-admin`

**State written:** A new row in `users` for this tenant with invited status, assignment to the selected tenant owner/admin role, and a set-password email record/token. A set-password email is sent to the provided address.

**Password rule:** the operator never chooses or handles the tenant owner's final password. The tenant owner sets it through the invite link.

**Note:** The invited user cannot log in yet — the tenant is still in `provisioning` status. The set-password link is valid for 72 hours. If the tenant is not activated within that window, a new invite can be sent.

---

## Step 7 — Review & Confirm

**What you see:** A summary screen showing all choices from Steps 1–6:
- Company details and slug
- Plan and billing configuration
- Active modules list
- Role templates and materialized starter roles
- Key settings values
- Invited admin email

**Review each section.** Any step can be edited by clicking **Edit** next to that section — this navigates back to that step without losing progress on others.

When satisfied, click **Activate Tenant**.

**API call:** `PATCH /admin/v1/tenants/{id}/provision/confirm`

**State written:** `tenants.status` flips from `provisioning` to `active`.

**Activation guard:** activation must fail with a checklist response until all required provisioning sections are complete: tenant details, subscription/commercial terms, module entitlements, at least one valid tenant owner/admin role, required settings, and first owner invite. Invalid role permissions, missing billing/commercial fields, expired required trial dates, or missing module-required settings must block activation.

**After confirmation:**
- The tenant is now live and visible to the main OneVo app
- The invited admin can log in once they complete set-password
- The yellow "In Progress" badge is replaced with a green "Active" badge in the Tenants list
- The provisioning event is audit-logged with the developer account and timestamp

## Required Admin API Surface

The complete Phase 1 provisioning surface requires these admin endpoints:

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/admin/v1/subscription-plans` | Load reusable plans with calculated/override pricing, included modules, company-size range, and AI token limits for Step 2 |
| `POST` | `/admin/v1/subscription-plans` | Create reusable plans from selected modules and company-size bracket pricing |
| `PATCH` | `/admin/v1/subscription-plans/{id}` | Update reusable plan modules, company-size price band, overrides, active state, and AI token limits |
| `GET` | `/admin/v1/payment-gateways` | Load configured Stripe/PayHere gateway options for Step 2 |
| `GET` | `/admin/v1/modules/catalog` | Load reusable module catalog and default pricing for Step 3 |
| `GET` | `/admin/v1/tenants/validate` | Validate slug/company/domain before or during draft creation |
| `GET` | `/admin/v1/reference/countries/{countryCode}/defaults` | Return default timezone/currency and supported timezone choices for account setup |
| `POST` | `/admin/v1/tenants` | Create provisioning draft |
| `GET` | `/admin/v1/tenants/{id}` | Load tenant detail and resume state |
| `PATCH` | `/admin/v1/tenants/{id}` | Edit draft tenant details before activation |
| `PATCH` | `/admin/v1/tenants/{id}/subscription` | Save plan and commercial terms |
| `PUT` | `/admin/v1/tenants/{id}/modules` | Save module entitlements and module pricing |
| `GET` | `/admin/v1/tenants/{id}/permissions/catalog` | Load module-filtered permission catalog |
| `GET` | `/admin/v1/role-templates` | Load reusable role templates |
| `POST` | `/admin/v1/role-templates` | Create reusable role template |
| `PATCH` | `/admin/v1/role-templates/{id}` | Edit reusable non-system role template |
| `GET` | `/admin/v1/tenants/{id}/roles` | List materialized tenant roles during provisioning |
| `POST` | `/admin/v1/tenants/{id}/roles` | Create tenant-specific role during provisioning |
| `POST` | `/admin/v1/tenants/{id}/role-templates/{templateId}/apply` | Materialize template into tenant roles |
| `PUT` | `/admin/v1/tenants/{id}/roles/{roleId}/permissions` | Adjust tenant role permissions |
| `PATCH` | `/admin/v1/tenants/{id}/settings` | Save required settings |
| `POST` | `/admin/v1/tenants/{id}/invite-admin` | Invite first tenant owner/admin |
| `GET` | `/admin/v1/tenants/{id}/provisioning-summary` | Review activation checklist and chosen data |
| `PATCH` | `/admin/v1/tenants/{id}/provision/confirm` | Activate provisioning tenant |

Tenant-facing role APIs are separate and become available after activation:

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/roles` | List tenant roles |
| `POST` | `/api/v1/roles` | Tenant owner creates a role |
| `PUT` | `/api/v1/roles/{id}` | Tenant owner edits role metadata |
| `PUT` | `/api/v1/roles/{id}/permissions` | Tenant owner edits permissions within enabled module boundary |

## Product Decisions Required Before Implementation

- Exact default plan catalog, pricing units, seeded module price brackets, and whether plan prices are per employee, per device, flat, or custom.
- Whether plan-included modules are automatically enabled or only proposed in the wizard for operator confirmation.
- How total contract value is calculated when both calculated plan price, module override prices, and tenant subscription override prices exist.
- Exact AI token-limit defaults for AI-enabled plans.
- Whether trial modules require billing dates before activation.
- Whether role templates can be tenant-private reusable templates or only global operator-managed templates plus tenant-specific roles.
- Whether template re-apply updates an existing role, creates a duplicate with explicit override, or is blocked.
- Which exact permission codes are required for the first tenant owner/admin role.
- Exact required settings by module before activation.
- Whether company registration number and email domain validation are strict blockers or warnings by country.
- Whether the tenant owner may complete set-password before activation. Recommended rule: password can be set, but login remains blocked until tenant activation.

## Related

- [[developer-platform/modules/tenant-console/overview|Tenant Console]]
- [[developer-platform/modules/role-template-manager|Role Template Manager]]
- [[modules/auth/overview|Auth & Security]]
- [[Userflow/Auth-Access/role-creation|Role Creation]]
- [[Userflow/Auth-Access/permission-assignment|Permission Assignment]]
- [[modules/data-import/overview|Data Import]]
- [[modules/data-import/peoplehr-full-migration|PeopleHR Full Migration]]
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
- [[modules/configuration/app-allowlist/overview|App Allowlist]]
- [[modules/configuration/integrations/overview|Integrations]]
- [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]]
