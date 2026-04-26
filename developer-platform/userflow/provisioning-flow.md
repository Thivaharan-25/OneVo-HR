# Manual Customer Provisioning Flow

## Purpose

The provisioning wizard lets the dev team create a fully configured tenant account without the customer going through self-service signup. It is **not required for every customer** — use it when the situation calls for it.

**Use this flow when:**
- Enterprise deal closed by sales — customer is not going through self-signup
- White-glove onboarding — OneVo team sets up the environment on behalf of the customer
- Internal test tenants — creating isolated test accounts

**Do not use this flow for:** standard signups. Those go through the normal customer self-signup → Stripe → auto-provisioning path.

---

## Starting the Wizard

1. Navigate to `/tenants`
2. Click **Provision New Customer** (top-right button)
3. The 6-step wizard opens

---

## Draft Behaviour

After Step 1 completes, the tenant exists in `tenants.status = 'provisioning'`. This tenant is **invisible to the main OneVo app** — no customer-facing endpoint returns provisioning-status tenants.

The wizard can be **closed at any point after Step 1** and resumed later:
- The tenant appears in the Tenants list with a yellow **"In Progress"** badge
- Click the row to reopen the wizard at the last completed step
- Any step can be edited before the final confirm in Step 6

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
- Billing start date
- Whether Stripe billing is active for this tenant or manually managed

**Action:** Click **Save & Continue**

**API call:** `PATCH /admin/v1/tenants/{id}/subscription`

**State written:** `subscription_plans` association updated; `stripe_managed` flag set on the tenant.

---

## Step 3 — Module Selection

**What you fill in:**
- Checklist of all available OneVo modules, each labelled with its phase (Phase 1, Phase 2, etc.)
- Toggle which modules are active for this tenant

**Action:** Click **Save & Continue**

**API call:** `PUT /admin/v1/tenants/{id}/modules`

**State written:** `module_registry` rows for this tenant — one row per active module.

---

## Step 4 — Initial Configuration

**What you fill in:**
- Monitoring transparency mode (select: `transparent` | `private` | `disclosed`)
- Leave policy defaults (annual leave accrual method, carry-over cap)
- Desktop agent transparency mode (whether employees see the agent is running)
- Working hours defaults (start time, end time, timezone confirmation)

**Action:** Click **Save & Continue**

**API call:** `PATCH /admin/v1/tenants/{id}/settings`

**State written:** `tenant_settings` rows for the configuration keys above.

---

## Step 5 — Invite Admin

**What you fill in:**
- Customer's super-admin email address
- Customer's super-admin full name

**Action:** Click **Send Invite**

**API call:** `POST /admin/v1/tenants/{id}/invite-admin`

**State written:** A new row in `users` for this tenant with `role = 'super_admin'` and `status = 'invited'`. A set-password email is sent to the provided address.

**Note:** The invited user cannot log in yet — the tenant is still in `provisioning` status. The set-password link is valid for 72 hours. If the tenant is not activated within that window, a new invite can be sent.

---

## Step 6 — Review & Confirm

**What you see:** A summary screen showing all choices from Steps 1–5:
- Company details and slug
- Plan and billing configuration
- Active modules list
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
