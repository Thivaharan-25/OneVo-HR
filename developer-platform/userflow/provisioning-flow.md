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
- Timezone

**Action:** Click **Create Tenant**

**API call:** `POST /admin/v1/tenants`

**State written:** New row in `tenants` with `status = 'provisioning'`. The tenant ID is returned and stored for all subsequent wizard steps.

**Note:** If you close the browser before completing this step, nothing is saved — the tenant does not exist yet.

---

## Step 2 — Plan Assignment

**What you fill in:**
- Subscription plan (dropdown of all plans from `subscription_plans`)
- Commercial model: `subscription` or `full_license_maintenance`
- Billing start date
- Whether Stripe billing is active for this tenant or manually managed
- Maintenance renewal date and status when the commercial model is `full_license_maintenance`
- Custom contract value, maintenance rate, and pricing overrides when the sales agreement is manually negotiated

**Action:** Click **Save & Continue**

**API call:** `PATCH /admin/v1/tenants/{id}/subscription`

**State written:** `subscription_plans` association updated; commercial model, billing cycle/currency, contract dates, maintenance status/renewal date, custom contract value, and `stripe_managed` flag set for the tenant.

---

## Step 3 — Module Selection

**What you fill in:**
- Checklist of all available OneVo modules, each labelled with its phase (Phase 1, Phase 2, etc.)
- Toggle which modules are active for this tenant
- For each module, mark the sales state as `available`, `trial`, `quoted`, `purchased`, `maintenance_included`, `subscription_included`, or `disabled`
- Optional module-specific pricing override, currency, start date, and end/trial expiry date

**Action:** Click **Save & Continue**

**API call:** `PUT /admin/v1/tenants/{id}/modules`

**Sales rule:** Future modules must start disabled or available; they are enabled only after sales, trial approval, purchase, or maintenance entitlement is recorded.

**Commercial entitlement rule:** Pricing and module entitlement decide what the tenant has access to. RBAC decides which users inside the tenant can use it. The permission catalog in Step 4 is filtered only after the active module entitlement set is resolved.

**State written:** tenant module entitlement records through the module entitlement registry. This module set becomes the permission boundary for role templates and tenant role management.

---

## Step 4 - Role Template Setup

**What you fill in:**
- Pick ONEVO starter templates, such as Tenant Owner, HR Admin, Leave Manager, and Employee.
- Create or edit tenant-specific role templates from the filtered permission catalog.
- Confirm which templates should be materialized into tenant roles at activation.

**API calls:**
- `GET /admin/v1/tenants/{id}/permissions/catalog`
- `GET /admin/v1/role-templates`
- `POST /admin/v1/role-templates`
- `POST /admin/v1/tenants/{id}/role-templates/{templateId}/apply`

**Permission boundary:** the catalog only includes universal permissions and permissions from modules enabled in Step 3. If the tenant bought only Employee Management and Leave, Payroll, Workforce Intelligence, WorkSync, Agent Gateway, and Identity Verification permissions are not shown and cannot be assigned.

**State written:** tenant-scoped `roles` and `role_permissions` through Auth interfaces, plus audit records for every template applied or changed.

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

**State written:** A new row in `users` for this tenant with `role = 'super_admin'` and `status = 'invited'`. A set-password email is sent to the provided address.

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

**After confirmation:**
- The tenant is now live and visible to the main OneVo app
- The invited admin can log in once they complete set-password
- The yellow "In Progress" badge is replaced with a green "Active" badge in the Tenants list
- The provisioning event is audit-logged with the developer account and timestamp

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
