# Feature Flag Flows

## Purpose

Feature flags control runtime availability for capabilities that are already commercially included. The Feature Flag Manager has two scopes: global defaults that apply to all tenants, and per-tenant overrides that deviate from those defaults.

It does not define what a tenant bought or what price they pay. Module Catalog / Subscription Manager define module features and plan inclusion. A feature flag can only activate an included feature; it must not grant a feature outside the tenant's plan or custom contract.

All flag changes are audit-logged with the developer account and timestamp.

---

## 1. Global Flag List View

**Path:** `/feature-flags`

The list shows all flags defined in `feature_flags`. Each row shows:
- Flag key (e.g. `activity_monitoring_v2`)
- Human-readable description
- Global default value (`enabled` | `disabled`)
- Rollout percentage (if the flag supports gradual rollout)
- Number of tenants with an active override

**Filter bar:** search by flag key or description. Filter by default value.

**API:** `GET /admin/v1/feature-flags`

---

## 2. Toggle a Global Default

**Minimum role:** admin

Changing the global default affects all tenants that do **not** have a per-tenant override. Tenants with an override are unaffected.

**Steps:**

1. Navigate to `/feature-flags`
2. Find the flag in the list (use the search bar for large lists)
3. Click the toggle in the **Default** column, or click the flag row to open the detail view and toggle from there
4. `ConfirmActionDialog` appears: "Change global default for `<flag_key>` from `<current>` to `<new>`?"
5. Click **Confirm**
6. **API call:** `PATCH /admin/v1/feature-flags/{flag}` with body `{ "default_value": true | false, "reason": "..." }`
7. Toast: "Global default updated"
8. The toggle reflects the new state immediately (optimistic update, reverted on API error)

**Flag detail view** (`/feature-flags/{flag}`): shows the full list of tenants that have a per-tenant override for this flag, with each override value. Useful for assessing blast radius before changing the global default.

**API for detail:** `GET /admin/v1/feature-flags/{flag}`

---

## 3. Per-Tenant Flag Override

**Minimum role:** admin

A per-tenant override lets a specific tenant have a flag value that differs from the global default. Overrides are stored in `feature_flag_overrides`.

Override ON is allowed only when the tenant has the parent module entitlement and the current subscription/custom contract includes the feature key. Override OFF has no billing effect; the tenant keeps paying the same commercial price until the subscription record changes.

### Accessing the Flags Tab

1. Navigate to `/platform/tenants`
2. Click the target tenant row
3. Select the **Flags** tab on the tenant detail page

The Flags tab shows every flag defined on the platform, with columns:
- Flag key
- Global default value
- This tenant's override (or "— (inherits default)" if no override is set)
- Override toggle

### Toggling a Single Override

1. Find the flag in the Flags tab table
2. Click the toggle in the **Override** column
3. Optimistic update: the toggle switches immediately
4. **API call:** `PATCH /admin/v1/tenants/{id}/feature-flags/{flag}` with body `{ "value": true | false, "reason": "..." }`
5. On success: the override value persists to `feature_flag_overrides`
6. On error: optimistic update is reverted, error toast shown

### Clearing an Override (Revert to Global Default)

1. On the flag row with an active override, click **Clear Override** (appears as a small x next to the toggle)
2. The row reverts to showing "— (inherits default)"
3. **API call:** `DELETE /admin/v1/tenants/{id}/feature-flags/{flag}`. Deleting the override removes the `feature_flag_overrides` row.

### Bulk Override (All Flags for a Tenant)

For initial tenant setup or a wholesale flag reset:

**API call:** `PUT /admin/v1/tenants/{id}/feature-flags` with body `{ "overrides": { "<flag_key>": true | false, ... }, "reason": "..." }`

This replaces all existing overrides for the tenant with the provided set. Flags omitted from the payload revert to global default. This API is not exposed in the UI as a single action — it is called by the tenant card Manage/Configure module setup flow when bulk flag alignment is required.
