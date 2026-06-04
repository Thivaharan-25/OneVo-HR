# Tenant Management Flows

## Purpose

All day-to-day company/tenant operations: finding companies, inspecting their tenant state, suspending them, impersonating their admin for support, managing connected-company relationships, and overriding their subscription/commercial terms when the normal payment gateway path cannot be used.

---

## 1. Tenant List View

**Path:** `/tenants`

The list renders all tenants across all statuses. Each row shows:
- Company name and slug
- Plan tier
- Status badge (`provisioning` -> yellow, `pending_confirmation` -> blue, `pending_payment` -> blue, `active` -> green, `suspended` -> red, `cancelled` -> gray)
- Employee count
- Created date

**Filter bar:** filter by status, plan tier, or free-text search on name/slug.

Provisioning-status tenants appear in this list with a yellow **"In Progress"** badge. Clicking them resumes tenant creation if Step 2 is incomplete, or opens the tenant card Manage/Configure flow when the two-step creation is complete but activation is still pending - see `provisioning-flow.md`.

**API:** `GET /admin/v1/tenants`

---

## 2. Tenant Detail View

**Path:** `/tenants/{id}`

Click any tenant row to open the full tenant detail page. This is the primary management surface after initial provisioning. The detail page has tabbed sections:

| Tab | Contents |
|---|---|
| **Overview** | Company profile header, KPI summary cards (total users, active users today, registered devices, active devices, storage used, platform health), user activity chart, work mode distribution, subscription & limits progress bars, recent alerts, top departments by activity, integrations status |
| **Usage & Analytics** | DAU trend, session duration distribution, feature usage breakdown, module engagement heatmap, device activity, exception events |
| **Users** | Tenant user list with role, status, work mode, department, last login - read-only |
| **Devices** | Deferred to Phase 2; Phase 1 may show aggregate agent/device health only in Platform Health |
| **Subscriptions** | Current plan detail, module entitlements table with status per module, invoices table |
| **Policies** | Feature flag overrides for this tenant, global policy overrides |
| **Integrations** | All integration statuses (Microsoft 365, Azure AD SSO, Biometric, Slack, etc.) with connection health and last sync |
| **Activity Log** | Audit log filtered to this tenant only - all actor types (tenant user, platform admin, system) |
| **Settings** | Editable tenant settings: org profile, operational settings, monitoring configuration (if applicable) |

**API:** `GET /admin/v1/tenants/{id}`

**Tenant creation path:** Tenant creation uses a 4-step wizard accessed via `+ Create Tenant` on the Tenants list. After the wizard completes and the tenant is activated, all ongoing management happens from this Tenant Detail page - see [[developer-platform/userflow/provisioning-flow|Provisioning Flow]] for the full wizard specification.

---

## 3. Connected Companies

**Minimum role:** admin to view, super_admin to approve or revoke

Connected Companies links this company tenant to another company tenant for approved cross-company transfers, workflow routing, reporting, data views, or collaboration. A connection never merges users, employees, subscriptions, payroll, settings, branding, or audit logs.

**Eligibility rule:** matching verified owner email can mark another company as eligible, but it does not grant access by itself.

**Steps:**

1. Open tenant detail page (`/tenants/{id}`) -> **Connected Companies**
2. Search by company name, slug, or owner email
3. Review eligibility, owner email match state, tenant status, and existing connection state
4. Click **Request Connection** or **Approve Connection**
5. Backend creates or activates the company connection and audit-logs the action
6. Configure scoped access grants only for the cross-company flows that should be allowed

**APIs:**

- `GET /admin/v1/company-connections/eligible?ownerEmail=...`
- `GET /admin/v1/tenants/{tenantId}/company-connections`
- `POST /admin/v1/tenants/{tenantId}/company-connections`
- `PATCH /admin/v1/company-connections/{connectionId}/approve`
- `PATCH /admin/v1/company-connections/{connectionId}/reject`
- `PATCH /admin/v1/company-connections/{connectionId}/revoke`
- `GET /admin/v1/company-connections/{connectionId}/audit`

---

## 4. Suspend a Tenant

**Minimum role:** super_admin

Suspended tenants cannot log in to the main OneVo app. All tenant data is preserved.

**Steps:**

1. Open the tenant detail page (`/tenants/{id}`)
2. Click **Suspend** in the action bar (top-right)
3. `ConfirmActionDialog` appears - type the tenant slug to confirm
4. Click **Confirm Suspend**
5. API call: `PATCH /admin/v1/tenants/{id}/status` with body `{ "status": "suspended" }`
6. Toast: "Tenant suspended"
7. Status badge on the detail page and list row updates to red **"Suspended"**

**To unsuspend:**

1. Open the suspended tenant's detail page
2. Click **Unsuspend**
3. `ConfirmActionDialog` - no slug confirmation required for unsuspend
4. API call: `PATCH /admin/v1/tenants/{id}/status` with body `{ "status": "active" }`
5. Toast: "Tenant reactivated"
6. Status badge returns to green **"Active"**

Both actions are audit-logged with the developer account, timestamp, and previous status.

---

## 5. Impersonate Tenant Admin

**Minimum role:** super_admin

Impersonation lets a developer log in to the main OneVo app as the tenant's super-admin role - for support debugging, reproducing issues, or validating configuration - without requiring the customer's credentials.

**Steps:**

1. Open the tenant detail page (`/tenants/{id}`)
2. Click **Impersonate as Super Admin**
3. `ConfirmActionDialog` appears with a warning: "This action is audit-logged. The session cannot be extended."
4. Click **Confirm**
5. API call: `POST /admin/v1/tenants/{id}/impersonate`
6. Backend issues a short-lived tenant-scoped JWT
7. The main OneVo app opens in a **new browser tab** with that JWT pre-loaded

**Security constraints - all four apply:**

- Token expiry: **15 minutes**, hard limit
- Token is **not renewable** - there is no refresh token issued
- JWT carries `"impersonation": true` claim - the main app surfaces a persistent banner so the session is visually distinguishable
- Every impersonation event is **audit-logged** with: developer account, target tenant, timestamp, and source IP

When the 15-minute token expires the new tab is logged out automatically. The developer returns to the console tab; the original platform-admin session is unaffected.

---

## 6. Subscription Override

**Minimum role:** super_admin

> **Warning - exception tool only.** The normal, primary path for standard subscription collection is through the configured payment gateway (`stripe`, `paddle`, or `payhere`). Use this tool only when that path cannot be used or when the tenant has negotiated commercial terms:
> - Enterprise deals closed by sales
> - Full-license tenants with manually recorded one-time license payment
> - Internal test accounts
> - Fixing a confirmed gateway sync error
>
> Do not use subscription override as a routine billing management tool. Direct standard subscription changes through the configured Stripe/Paddle/PayHere flow.

**Steps:**

1. Open the tenant detail page (`/tenants/{id}`) -> **Overview** tab
2. Click **Override Subscription**
3. A form appears: select new plan from dropdown, choose commercial model, set billing dates, select collection mode and gateway provider when applicable, enter reason (required free-text field)
4. Click **Apply Override**
5. API call: `PATCH /admin/v1/tenants/{id}/subscription` with body including `plan_code`, `commercial_model`, collection modes, optional `gateway_provider` (`stripe`, `paddle`, or `payhere`), and `reason`
6. Toast: "Subscription updated"
7. Overview tab reflects the new plan; gateway-managed, manually managed, or full-license maintenance labels appear next to billing dates

All overrides are audit-logged with the developer account, the previous plan, the new plan, and the reason provided.


