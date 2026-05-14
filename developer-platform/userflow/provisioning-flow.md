# Manual Customer Provisioning Flow

## Purpose

The tenant creation wizard is the **only way** a company tenant is created in ONEVO. There is no public self-signup, no public tenant registration endpoint, and no customer-facing checkout flow. Every company is created as its own tenant by an ONEVO operator after a sales agreement is reached.

Tenant creation has two steps only: customer profile and commercial/subscription selection. Module entitlement confirmation, setup services, role/template application, tenant-specific configuration, owner invite, and activation happen after creation through the tenant card **Manage/Configure** action.

**Use this flow for all tenant creation:**
- Enterprise deal closed by sales
- White-glove onboarding â€” ONEVO team sets up the environment on behalf of the customer
- Internal test tenants â€” creating isolated test accounts

Separate operating companies must be provisioned as separate tenants. Do not create another company as a legal entity inside an existing tenant. If companies need to share workflows, data views, employee transfers, or reporting, create a [[modules/shared-platform/company-connections/overview|Company Connection]] after both tenants exist.

**ADE rule:** Do not build or expose a public tenant creation path. `POST /api/v1/tenants` must not exist on the customer-facing API. Tenant creation is always through `POST /admin/v1/tenants` via this console.

---

## Starting the Wizard

1. Navigate to `/tenants`
2. Click **Provision New Customer** (top-right button)
3. The two-step tenant creation wizard opens

---

## Draft Behaviour

After Step 1 completes, the tenant exists in `tenants.status = 'provisioning'`. This tenant is **invisible to the main OneVo app** â€” no customer-facing endpoint returns provisioning-status tenants.

The wizard can be **closed at any point after Step 1** and resumed later:
- The tenant appears in the Tenants list with a yellow **"In Progress"** badge
- Click the row to reopen the wizard at the last completed step
- The profile and commercial selection can be edited before post-creation activation

---

## Step 1 â€” Customer Profile

**What you fill in:**
- Company name
- Slug (URL-safe identifier, must be unique â€” validated on blur)
- Primary contact email
- Country
- Industry
- Registration/profile name
- Registration number
- Company size
- Timezone
- Currency

**Action:** Click **Create Tenant**

**API call:** `POST /admin/v1/tenants`

**State written:** New row in `tenants` with `status = 'provisioning'`, `slug`, `primary_contact_email`, `country`, `timezone`, `currency`, `industry_profile`, `registration_profile_name`, `registration_number`, `company_size_range`, and profile/contact metadata. The tenant ID is returned and stored for Step 2 and the later Manage/Configure flow.

**Country defaults rule:** The UI calls `GET /admin/v1/reference/countries/{countryCode}/defaults` after country selection. Single-timezone countries can auto-fill timezone; multi-timezone countries must show a timezone dropdown. Currency defaults from country but remains editable.

**No legal-entity rule:** Registration/profile fields, country, timezone, and currency are tenant profile data in this wizard. This step must not create `legal_entities` rows or model multiple companies as legal entities under one tenant. Separate operating companies are separate tenants. The same owner email can be invited to, and accept invitations for, multiple isolated tenants.

**Note:** If you close the browser before completing this step, nothing is saved â€” the tenant does not exist yet.

---

## Step 2 â€” Commercial Selection

**What you fill in:**
- Subscription plan (dropdown of reusable plans from `subscription_plans`; operators do not create a new plan for every tenant)
- Company size price band (same values as the Step 1 company-size dropdown; defaults from the tenant's saved `company_size_range`)
- Modules included in the plan; selecting modules recalculates the per-unit price from `module_catalog.price_brackets`
- Calculated monthly/annual price and optional operator override price
- Calculated full-license price and optional operator override full-license amount
- Calculated maintenance rate/amount and optional operator override maintenance rate/amount
- Monthly AI token limit when the selected modules/plan include AI capability
- Storage limit when selected Work Management modules require storage entitlement
- Commercial model: `subscription` or `full_license_maintenance`
- Billing cycle for subscriptions: `monthly` or `annual`
- Billing start date
- Payment collection mode and gateway provider (`stripe` or `payhere`) for subscription billing
- Full-license payment mode (`manual` or `gateway`) when the commercial model is `full_license_maintenance`
- Billing evidence attachment/reference when subscription, full-license, or maintenance is paid manually
- Payment exception/grace period when ONEVO allows the tenant to use the system without payment for an approved period
- Maintenance collection mode (`gateway`, `manual`, or `waived`) and gateway provider when maintenance is collected through the system
- Maintenance renewal date and status when the commercial model is `full_license_maintenance`
- Custom contract value, maintenance rate, and pricing overrides when the sales agreement is manually negotiated

**Action:** Click **Save & Continue**

**API call:** `PATCH /admin/v1/tenants/{id}/subscription`

**State written:** `subscription_plans` association updated; commercial model, billing cycle/currency, contract dates, subscription collection mode, gateway provider, gateway references, license payment fields, maintenance collection mode/status/renewal date, selected company-size range, selected module keys, calculated plan price snapshot, optional monthly/annual/full-license/maintenance overrides, AI monthly token limit, Work Management storage limit, manual billing evidence references, payment exception/grace dates, custom contract value, and pricing overrides set for the tenant.

After this step succeeds, the tenant card can show **Manage/Configure**. The tenant remains in `provisioning` until module entitlement confirmation, role/template setup, required tenant configuration, setup services, and activation checks are complete.

**Plan rule:** plans are global commercial catalog records. A tenant receives one selected plan plus tenant-specific commercial terms. Custom pricing, discounts, contract value, maintenance rate, billing dates, and manual billing state belong on the tenant subscription/commercial record, not on a new one-off plan unless product intentionally adds a reusable custom plan.

**Dynamic pricing rule:** plan price is the sum of selected package/module bracket prices for the selected company-size range. Example: Package 1 plus Package 2 for `51-200` employees shows the calculated package total before any override. Changing company size or selected packages/modules recalculates immediately. Operator overrides change the effective price but must preserve the calculated price for audit.

**AI token rule:** when AI capability is included, the operator must set a positive monthly token limit. Non-AI plans store no AI token limit.

**Work Management storage rule:** when Work Management modules include storage-backed features, the operator must set a positive storage limit or select a plan default. Non-Work Management plans store no Work Management storage entitlement.

**Manual billing evidence rule:** manual subscription, manual full-license payment, and manual maintenance payment require billing evidence or a reference plus an audit reason. Evidence must be stored as an Infrastructure file record or approved external reference; raw files are not stored on the subscription row.

**Payment exception rule:** payment exceptions/grace periods are approved commercial exceptions. They may apply to subscription tenants and full-license/maintenance tenants. They are snapshotted to the tenant commercial record and must not silently change when reusable plan defaults change.

**Gateway rule:** Stripe and PayHere are the primary Phase 1 payment gateways. Subscription tenants normally use gateway collection. Full-license tenants may record the one-time license payment manually, but recurring maintenance fees should use Stripe or PayHere when gateway collection is enabled. Gateway API keys, merchant secrets, and webhook secrets are managed through encrypted payment gateway configuration, not returned from APIs.

**Cost rule:** plan pricing and module pricing are commercial inputs. They decide what the tenant has bought, trialed, or been granted. They do not grant user permissions directly. RBAC is applied only after the tenant's entitled modules are resolved.

---

## Post-Creation Manage / Configure - Module Entitlements

**What you fill in:**
- Checklist loaded from the reusable `module_catalog`, each module labelled with pillar, phase, default pricing unit, and sellable status
- Toggle which modules are active for this tenant
- For each module, mark the sales state as `available`, `trial`, `quoted`, `purchased`, `maintenance_included`, `subscription_included`, or `disabled`
- Optional module-specific pricing override, currency, start date, and end/trial expiry date

**Action:** Click **Save & Continue**

**API call:** `PUT /admin/v1/tenants/{id}/modules`

**Sales rule:** Future modules must start disabled or available; they are enabled only after sales, trial approval, purchase, or maintenance entitlement is recorded.

**Commercial entitlement rule:** Pricing and module entitlement decide what the tenant has access to. RBAC decides which users inside the tenant can use it. The permission catalog in the role/template setup area is filtered only after the active module entitlement set is resolved.

**State written:** tenant module entitlement records through the module entitlement registry. This module set becomes the permission boundary for role templates and tenant role management.

**Module cost rule:** module prices may default from `module_catalog`, be included by the selected plan, or be overridden per tenant. The backend must preserve the operator-entered pricing model, price, currency, start date, end/trial expiry date, and sales state for audit and billing. A module in `quoted` or `available` state is visible in the console but is not active for tenant-facing access until it becomes `purchased`, `trial`, `subscription_included`, or `maintenance_included`.

**Setup-service rule:** every setup service is connected to one or more module keys. The selected subscription/modules determine which setup services can be applied. Free/global setup services are auto-added for the tenant when their module is entitled, can still be configured by the operator, and must not create billing. Paid setup services must be explicitly selected and tracked. When the operator clicks apply/configure for a paid setup service, the system knows the valid service list from the tenant's entitled modules.

---

## Post-Creation Manage / Configure - Role And Permission Templates

**What you fill in:**
- Pick reusable ONEVO starter templates, such as Tenant Owner, HR Admin, Leave Manager, Employee, Workforce Supervisor, or WorkSync Project Manager.
- Create a new reusable operator-managed role template and save it to the global template library when the pattern should be reused for other tenants.
- Create tenant-specific roles directly during Manage/Configure when the role is unique to this customer and should not become a global template.
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

**Permission boundary:** the catalog only includes universal permissions and permissions from modules enabled in the tenant's commercial/module entitlement set. If the tenant bought only Employee Management and Leave, Payroll, Workforce Intelligence, WorkSync, Agent Gateway, and Identity Verification permissions are not shown and cannot be assigned.

**Permission ownership rule:** each permission belongs to exactly one module. The Developer Platform module catalog must show the owning module for each permission. Once a permission is assigned to a module, it cannot be assigned to another module unless it is first removed from the original module through an explicit catalog change.

**State written:** tenant-scoped `roles` and `role_permissions` through Auth interfaces, plus audit records for every template applied or changed.

**Role independence rule:** role creation does not require job levels. Basic roles are independent permission containers. Job levels, departments, reporting lines, and hierarchy are only needed later for scoped permissions, approval workflows, escalation rules, and organisation-aware access.

**Template rule:** role templates are blueprints, not runtime authorization records. Applying a template materializes normal tenant-scoped roles. Applying the same template twice must be idempotent or require an explicit duplicate-name override; it must never silently create confusing duplicate roles.

---

## Post-Creation Manage / Configure - Tenant Configuration And Setup Services

**What you fill in:**
- Apply or customize Configuration Templates
- Apply or customize Role Templates already materialized in the role/template setup area
- Apply or customize Org Structure Templates, Job Family Templates, Leave Policy Templates, Onboarding Templates, App Allowlist Templates, Monitoring Policy Templates, and Data Import Mapping Templates when those modules/services are included
- Mark module-connected free/global setup services complete
- Select and configure paid setup services requested by the customer
- Configure only services/modules included in the tenant's selected commercial plan/module entitlements
- Monitoring transparency mode and desktop agent transparency mode where monitoring modules are selected
- Leave policy defaults where leave is selected
- Data import mapping where migration/import service is selected
- App allowlist templates based on the App Catalog where monitoring/app tracking is selected

**Action:** Click **Save & Continue**

**API call:** `PATCH /admin/v1/tenants/{id}/settings`

**State written:** `tenant_settings`, module-owned configuration rows, setup-service state, selected template applications, and tenant-specific template overrides as required by selected modules/services.

**Template rule:** global templates are reusable starting points. Applying a template to a tenant creates tenant-specific configuration that can be customized without changing the global template.

**App allowlist template rule:** app allowlist templates are created from App Catalog identities. App Catalog identities can come from curated entries or from applications observed by the Tray App running on a Super Admin/operator device and then categorized/saved into the catalog.

---

## Post-Creation Manage / Configure - Invite Tenant Owner

**What you fill in:**
- Customer's super-admin email address
- Customer's super-admin full name

**Action:** Click **Send Invite**

**API call:** `POST /admin/v1/tenants/{id}/invite-admin`

**State written:** A new row in `users` for this tenant with invited status, assignment to the selected tenant owner/admin role, and a set-password email record/token. A set-password email is sent to the provided address.

**Password rule:** the operator never chooses or handles the tenant owner's final password. The tenant owner sets it through the invite link.

**Explicit-send rule:** no tenant owner invitation email is sent by Step 1 profile creation, Step 2 commercial selection, module entitlement save, template application, setup completion, or activation. Email is sent only when the operator clicks **Send Invite** on this step or the equivalent tenant-card invite action.

**Multi-tenant email rule:** the same email address can be invited as owner/admin for multiple tenants. Accepting one tenant invitation creates/activates access only for that tenant and does not merge tenant data or grant cross-company access.

**Note:** The invited user cannot log in yet â€” the tenant is still in `provisioning` status. The set-password link is valid for 72 hours. If the tenant is not activated within that window, a new invite can be sent.

---

## Post-Creation Manage / Configure - Review & Confirm

**What you see:** A summary screen showing all choices from tenant creation and Manage/Configure:
- Company details and slug
- Plan and billing configuration
- Active modules list
- Role templates and materialized starter roles
- Key settings/template/setup-service values
- Invited admin email if an invite was sent, or invite-pending state if activation is allowed before sending owner invite

**Review each section.** Any section can be edited by clicking **Edit** next to that section without losing progress on others.

When satisfied, click **Activate Tenant**.

**API call:** `PATCH /admin/v1/tenants/{id}/provision/confirm`

**State written:** `tenants.status` flips from `provisioning` to `active`.

**Activation guard:** activation must fail with a checklist response until all required provisioning sections are complete: tenant profile, subscription/commercial terms, module entitlements, at least one valid tenant owner/admin role, required settings/templates, and required module/setup-service configuration. Invalid role permissions, missing billing/commercial fields, expired required trial/payment-exception dates, or missing module-required settings must block activation. Tenant owner invite status is tracked separately and must not be sent implicitly.

**After confirmation:**
- The tenant is now live and visible to the main OneVo app
- The invited admin can log in once they receive/complete the invite and the tenant is active
- The yellow "In Progress" badge is replaced with a green "Active" badge in the Tenants list
- The provisioning event is audit-logged with the developer account and timestamp

## Required Admin API Surface

The complete Phase 1 creation plus Manage/Configure surface requires these admin endpoints:

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/admin/v1/subscription-plans` | Load reusable plans with calculated/override pricing, included modules, company-size range, and AI token limits for Step 2 |
| `POST` | `/admin/v1/subscription-plans` | Create reusable plans from selected packages/modules and company-size bracket pricing |
| `PATCH` | `/admin/v1/subscription-plans/{id}` | Update reusable plan modules, company-size price band, overrides, active state, and AI token limits |
| `GET` | `/admin/v1/payment-gateways` | Load configured Stripe/PayHere gateway options for Step 2 |
| `GET` | `/admin/v1/modules/catalog` | Load reusable module catalog and default pricing for Manage/Configure |
| `GET` | `/admin/v1/tenants/validate` | Validate slug/company/domain before or during draft creation |
| `POST` | `/admin/v1/tenants` | Create provisioning draft |
| `GET` | `/admin/v1/tenants/{id}` | Load tenant detail and resume state |
| `PATCH` | `/admin/v1/tenants/{id}` | Edit draft tenant details before activation |
| `PATCH` | `/admin/v1/tenants/{id}/subscription` | Save plan and commercial terms |
| `PUT` | `/admin/v1/tenants/{id}/modules` | Save module entitlements and module pricing |
| `GET` | `/admin/v1/tenants/{id}/permissions/catalog` | Load module-filtered permission catalog |
| `GET` | `/admin/v1/role-templates` | Load reusable role templates |
| `POST` | `/admin/v1/role-templates` | Create reusable role template |
| `PATCH` | `/admin/v1/role-templates/{id}` | Edit reusable non-system role template |
| `GET` | `/admin/v1/tenants/{id}/roles` | List materialized tenant roles during Manage/Configure |
| `POST` | `/admin/v1/tenants/{id}/roles` | Create tenant-specific role during Manage/Configure |
| `POST` | `/admin/v1/tenants/{id}/role-templates/{templateId}/apply` | Materialize template into tenant roles |
| `PUT` | `/admin/v1/tenants/{id}/roles/{roleId}/permissions` | Adjust tenant role permissions |
| `GET` | `/admin/v1/reference/countries/{countryCode}/defaults` | Return default timezone/currency and supported timezone choices for profile setup |
| `GET` | `/admin/v1/setup-services` | Load module-connected free/global and paid setup services |
| `PUT` | `/admin/v1/tenants/{id}/setup-services` | Select and track required setup services |
| `GET` | `/admin/v1/configuration-templates` | Load reusable configuration and module templates |
| `POST` | `/admin/v1/configuration-templates` | Create reusable configuration template |
| `POST` | `/admin/v1/tenants/{id}/configuration-templates/{templateId}/apply` | Apply template to tenant-specific configuration |
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
- Whether plan-included modules are automatically enabled or only proposed in Manage/Configure for operator confirmation.
- How total contract value is calculated when both calculated plan price, module override prices, and tenant subscription override prices exist.
- Exact AI token-limit defaults for AI-enabled plans.
- Whether trial modules require billing dates before activation.
- Whether role templates can be tenant-private reusable templates or only global operator-managed templates plus tenant-specific roles.
- Whether template re-apply updates an existing role, creates a duplicate with explicit override, or is blocked.
- Which exact permission codes are required for the first tenant owner/admin role.
- Exact required settings by module before activation.
- Whether primary contact email domain validation is a strict blocker or warning.
- Whether the tenant owner may complete set-password before activation. Recommended rule: password can be set, but login remains blocked until tenant activation.
- Whether company connections are Developer Platform-only in Phase 1 or whether tenant owners can request connections from the tenant-facing app.
- Exact data model for template application history and tenant-specific template overrides.

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
