# Tenant Management Flows

## Purpose

All day-to-day tenant operations: finding tenants, inspecting their state, suspending them, impersonating their admin for support, and overriding their subscription when the normal Stripe path cannot be used.

---

## 1. Tenant List View

**Path:** `/tenants`

The list renders all tenants across all statuses. Each row shows:
- Company name and slug
- Plan tier
- Status badge (`active` → green, `suspended` → red, `provisioning` → yellow, `trial` → blue)
- Employee count
- Created date

**Filter bar:** filter by status, plan tier, or free-text search on name/slug.

Provisioning-status tenants (in-progress wizard) appear in this list with a yellow **"In Progress"** badge. Clicking them resumes the provisioning wizard at the last completed step — see `provisioning-flow.md`.

**API:** `GET /admin/v1/tenants`

---

## 2. Tenant Detail View

**Path:** `/tenants/{id}`

Click any active or suspended tenant row to open its detail page. The detail page has tabbed sections:

| Tab | Contents |
|---|---|
| **Overview** | Plan name, billing dates, `status`, employee count, agent count, last login (any user) |
| **Flags** | All per-tenant feature flag overrides — see `feature-flags.md` |
| **Settings** | Current `tenant_settings` values; editable by admin+ |
| **Users** | User list with roles and last-login timestamps (read-only) |
| **Audit** | Audit log filtered to this tenant only |

**API:** `GET /admin/v1/tenants/{id}`

---

## 3. Suspend a Tenant

**Minimum role:** super_admin

Suspended tenants cannot log in to the main OneVo app. All tenant data is preserved.

**Steps:**

1. Open the tenant detail page (`/tenants/{id}`)
2. Click **Suspend** in the action bar (top-right)
3. `ConfirmActionDialog` appears — type the tenant slug to confirm
4. Click **Confirm Suspend**
5. API call: `PATCH /admin/v1/tenants/{id}/status` with body `{ "status": "suspended" }`
6. Toast: "Tenant suspended"
7. Status badge on the detail page and list row updates to red **"Suspended"**

**To unsuspend:**

1. Open the suspended tenant's detail page
2. Click **Unsuspend**
3. `ConfirmActionDialog` — no slug confirmation required for unsuspend
4. API call: `PATCH /admin/v1/tenants/{id}/status` with body `{ "status": "active" }`
5. Toast: "Tenant reactivated"
6. Status badge returns to green **"Active"**

Both actions are audit-logged with the developer account, timestamp, and previous status.

---

## 4. Impersonate Tenant Admin

**Minimum role:** super_admin

Impersonation lets a developer log in to the main OneVo app as the tenant's super-admin role — for support debugging, reproducing issues, or validating configuration — without requiring the customer's credentials.

**Steps:**

1. Open the tenant detail page (`/tenants/{id}`)
2. Click **Impersonate as Super Admin**
3. `ConfirmActionDialog` appears with a warning: "This action is audit-logged. The session cannot be extended."
4. Click **Confirm**
5. API call: `POST /admin/v1/tenants/{id}/impersonate`
6. Backend issues a short-lived tenant-scoped JWT
7. The main OneVo app opens in a **new browser tab** with that JWT pre-loaded

**Security constraints — all four apply:**

- Token expiry: **15 minutes**, hard limit
- Token is **not renewable** — there is no refresh token issued
- JWT carries `"impersonation": true` claim — the main app surfaces a persistent banner so the session is visually distinguishable
- Every impersonation event is **audit-logged** with: developer account, target tenant, timestamp, and source IP

When the 15-minute token expires the new tab is logged out automatically. The developer returns to the console tab; the original platform-admin session is unaffected.

---

## 5. Subscription Override

**Minimum role:** super_admin

> **Warning — exception tool only.** The normal, primary path for plan changes is: customer → Stripe checkout → plan auto-assigned. Use this tool only when that path cannot be used:
> - Enterprise deals closed by sales (no Stripe checkout involved)
> - Trial extensions approved outside Stripe
> - Internal test accounts
> - Fixing a confirmed Stripe sync error
>
> Do not use subscription override as a routine billing management tool. Direct tenants to Stripe for standard plan changes.

**Steps:**

1. Open the tenant detail page (`/tenants/{id}`) → **Overview** tab
2. Click **Override Subscription**
3. A form appears: select new plan from dropdown, set billing start date, enter reason (required free-text field)
4. Click **Apply Override**
5. API call: `PATCH /admin/v1/tenants/{id}/subscription` with body `{ "plan_id": "<id>", "billing_start": "<date>", "reason": "<text>", "stripe_managed": false }`
6. Toast: "Subscription updated"
7. Overview tab reflects the new plan; a "Manually managed" label appears next to billing dates

All overrides are audit-logged with the developer account, the previous plan, the new plan, and the reason provided.
