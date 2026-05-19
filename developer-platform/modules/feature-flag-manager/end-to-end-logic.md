# Feature Flag Manager — End-to-End Logic

## Purpose

Feature Flag Manager controls two things:
1. **Feature flags** — boolean switches that gate features globally with optional per-tenant overrides and rollout percentages
2. **Module enable/disable** — toggle individual ONEVO modules on or off for a specific tenant after activation, without going through the subscription wizard

**Route:** `/platform/feature-management`
**Permission:** `platform.feature_flags.read`

---

## Screen Layout

Left tab navigation:
- Global Flags (default)
- Per-Tenant Overrides
- Module Enable/Disable

---

## Global Flags Screen

### Page Header

| Element | Value |
|---|---|
| Title | "Feature Flag Manager" |
| Subtitle | "Control global feature availability and per-tenant overrides." |
| Add Flag button | `+ Create Flag` — requires `platform.feature_flags.manage` |

### Filter Bar

| Filter | Type | Options |
|---|---|---|
| Search | Text | Flag key or description |
| Module | Dropdown | All + each module key |
| Status | Dropdown | All / Enabled / Disabled |
| Has Tenant Overrides | Toggle | Filter to flags with at least one tenant override |

### Global Flags Table

**API:** `GET /admin/v1/feature-flags?search={q}&module={key}&enabled={true|false}&has_overrides={true|false}`

| Column | Description | Sortable |
|---|---|---|
| Flag Key | Machine-readable key, e.g. `chat_ai.streaming_responses` | Yes |
| Description | Human-readable explanation | No |
| Module | Badge showing owning module key | Yes |
| Default Value | ON (green) / OFF (gray) | Yes |
| Rollout % | Percentage of tenants getting this flag as ON (when default = ON) | Yes |
| Tenant Overrides | Count of tenants with non-default override | No |
| Phase | 1 / 2 badge | Yes |
| Actions | Edit, View Overrides, Toggle |

---

## Create Feature Flag — Full Field Specification

**Trigger:** `+ Create Flag` button

| Field | Label | Type | Required | Validation | Notes |
|---|---|---|---|---|---|
| Flag Key | "Flag Key (slug)" | Text input | Yes | Lowercase, dots/underscores allowed, unique, max 120 chars. Format: `{module_key}.{feature_name}` | Permanent — cannot change after any tenant has a value set. e.g. `chat_ai.streaming_responses`, `work_management.ai_task_suggestions` |
| Description | "Description" | Textarea | Yes | 10–300 chars | Explains what enabling this flag does. Shown to operators. |
| Module | "Owning Module" | Dropdown from module catalog | Yes | | Which ONEVO module this flag belongs to. Determines which tenants can have overrides (must be entitled to this module) |
| Default Value | "Default State" | Radio: ON / OFF | Yes | | What all tenants get unless overridden. Changing this after creation immediately affects all tenants without an override. |
| Rollout Percentage | "Rollout Percentage" | Number input 0–100 | Yes | | Only meaningful when Default Value = ON. Sets what percentage of tenants actually receive the flag as ON. 100 = all tenants. 0 = no tenants (effectively OFF). Used for gradual rollouts. |
| Phase | "Phase" | Radio: 1 / 2 | Yes | | Phase 2 flags are visible in the manager but cannot be enabled for Phase 1 tenants |
| Is Active | "Active" | Toggle | Yes | Default: On | Inactive flags are evaluated as their default value everywhere; overrides are preserved but ignored |

### How Rollout Percentage Works

When `default_value = true` and `rollout_percentage = 30`:
- For each tenant without an explicit override, the backend calculates: `hash(tenant_id + flag_key) % 100 < 30`
- The hash is deterministic — the same tenant always gets the same result for the same flag
- Result: exactly ~30% of tenants (those whose hash falls in range) get ON; ~70% get OFF
- Tenants with an explicit override always use their override value, regardless of rollout %

When `default_value = false`: rollout_percentage has no effect — the flag is OFF for everyone without an override.

### Save Flag

**API:** `POST /admin/v1/feature-flags`

```json
{
  "flag_key": "chat_ai.streaming_responses",
  "description": "Enable streaming token-by-token responses in the Agentic Chat UI instead of waiting for full response.",
  "module_key": "chat_ai",
  "default_value": false,
  "rollout_percentage": 0,
  "phase": 1,
  "is_active": true
}
```

**State written:** `feature_flags` row created. Audit log: `action = 'feature_flag.created'`, actor, flag_key, default_value.

---

## Global Flag Toggle — Full Flow

**Trigger:** Click the toggle on a flag row OR open flag detail and click the toggle.

### Toggle Without Confirmation (default_value already set, changing rollout %)

No confirmation dialog. `PATCH /admin/v1/feature-flags/{flagKey}` with updated `rollout_percentage`.

### Toggle With Confirmation (changing default_value)

Changing `default_value` is a high-impact action — it immediately affects all tenants without an override.

**Confirmation dialog:**

```
Changing "chat_ai.streaming_responses" default from OFF → ON

This will enable this feature for all tenants that do not have an explicit override set.
Currently: 0 tenants have overrides. ~847 active tenants will be affected.

Are you sure?
```

**Fields in dialog:**

| Field | Type | Required | Notes |
|---|---|---|---|
| Reason | Textarea | Yes — min 10 chars | "Why are you changing this default? This is audit-logged." |

**API:** `PATCH /admin/v1/feature-flags/{flagKey}`

```json
{
  "default_value": true,
  "rollout_percentage": 10,
  "reason": "Starting gradual rollout of streaming chat. Beginning with 10% of tenants."
}
```

**State written:**
- `feature_flags.default_value` updated
- `feature_flags.rollout_percentage` updated
- Audit log: `action = 'feature_flag.default_changed'`, previous value, new value, reason, actor, affected tenant estimate

**Side effects:**
- Flag evaluation cache invalidated for all tenants without an override — takes effect on next cache miss (within 60 seconds)
- No tenant restart required

---

## Flag Detail Screen

**Route:** `/platform/feature-management/{flagKey}`

**API:** `GET /admin/v1/feature-flags/{flagKey}`

### Sections

**1. Flag Info**
Shows: flag key, description, module badge, default value, rollout %, phase, is_active, created by, created at, last modified by, last modified at.

**Edit** button opens the full create form pre-populated. All fields editable except `flag_key`.

**2. Tenant Overrides Table**

All tenants that have a non-default override for this flag.

| Column | Description |
|---|---|
| Tenant Name | Company name — linked to tenant detail |
| Override Value | ON (green) / OFF (red) — shows the tenant's explicit value |
| Set By | Platform admin who set the override |
| Set At | Timestamp |
| Reason | Reason entered when override was created |
| Actions | Remove Override |

"Add Override" button → opens the per-tenant override flow.

**3. Audit History**

Last 20 audit events for this flag: default changes, override additions/removals. Each row: timestamp, actor, action, previous value, new value, reason.

---

## Per-Tenant Override — Full Flow

An override sets an explicit value for a specific tenant, bypassing both the default value and rollout % entirely.

### Add Override

**Trigger:** "Add Override" on the flag detail screen OR from the Per-Tenant Overrides tab.

**Dialog fields:**

| Field | Label | Type | Required | Validation | Notes |
|---|---|---|---|---|---|
| Tenant | "Tenant" | Autocomplete search | Yes | Must be active | Type to search by name or domain |
| Override Value | "Override Value" | Radio: Force ON / Force OFF | Yes | | The explicit value for this tenant regardless of global default or rollout % |
| Reason | "Reason" | Textarea | Yes | Min 10 chars | Why this tenant gets a different value |

**API:** `PATCH /admin/v1/tenants/{tenantId}/feature-flags/{flagKey}`

```json
{
  "value": true,
  "reason": "Beta testing partner — TechNova requested early access to streaming chat."
}
```

**State written:** `feature_access_grants` row created/updated: `(flag_key, tenant_id, value, granted_by_id, granted_at, reason)`.

**Effect:** Takes effect immediately on next request from this tenant (cache invalidated). No tenant restart required.

### Remove Override

**Trigger:** "Remove Override" on flag detail → tenant overrides table.

**No confirmation dialog** for removing overrides — lower risk than adding.

**API:** `DELETE /admin/v1/tenants/{tenantId}/feature-flags/{flagKey}`

**Effect:** Tenant falls back to global default + rollout % evaluation. Audit logged.

### Per-Tenant Overrides Tab (global view)

**Route:** `/platform/feature-management/tenant-overrides`

Shows ALL overrides across ALL flags and ALL tenants.

| Filter | Options |
|---|---|
| Tenant | Autocomplete search |
| Flag | Autocomplete search by flag key |
| Override Value | All / Force ON / Force OFF |
| Set By | Platform admin name |
| Date Range | Set at date from/to |

| Column | Description |
|---|---|
| Tenant | Company name — linked |
| Flag Key | `module_key.feature_name` format |
| Module | Module badge |
| Override Value | ON / OFF badge |
| Set By | Who set it |
| Set At | Timestamp |
| Reason | Why it was set |
| Actions | Remove Override |

---

## Module Enable/Disable Tab

This tab allows operators to enable or disable a specific ONEVO module for a tenant **after activation** without going through the subscription override flow. This is a post-activation runtime toggle, not a commercial action.

**When to use this vs Subscription Override:**
- **Feature Flag Manager → Module Enable/Disable:** Immediate runtime toggle; does not change billing, subscription snapshot, or module sales state. Use for debugging, temporary access grants, beta access.
- **Tenant Console → Subscriptions → Override Subscription:** Changes the commercial record, module sales state, and billing. Use when the tenant has actually bought or cancelled a module.

**Route:** `/platform/feature-management/modules`

### Module Toggle Screen

| Filter | Options |
|---|---|
| Tenant | Autocomplete search (required — must select a tenant first) |
| Module | Dropdown from module catalog |
| Status | All / Enabled / Disabled |

After selecting a tenant, shows all modules in the catalog with their current status for that tenant.

| Column | Description |
|---|---|
| Module Name | Full name |
| Module Key | slug |
| Pillar | HR / Intelligence / WorkSync badge |
| Sales State | From `tenant_module_entitlements` — subscription_included, purchased, trial, etc. |
| Runtime Status | Enabled (green) / Disabled (red) — the current toggle state |
| Enabled By | Commercial (from entitlement) / Override (explicitly toggled here) |
| Actions | Enable / Disable toggle |

### Disable Module — Full Flow

**Trigger:** Toggle switch on a module row.

**Pre-check:** System checks for connected integrations that would be affected (same as Module Catalog Manager's unlink warning).

**Confirmation dialog:**

```
⚠ Disable "Agentic Chat" for TechNova Solutions?

Runtime effect: tenants users will immediately lose access to Agentic Chat.
Billing: not changed — this is a runtime toggle only. Their subscription still includes chat_ai.

Integrations that will be disconnected:
  • Microsoft Teams (connected by james@technova.com, May 12 2024)

Reason for disable (required):
[textarea]
```

**API:** `PATCH /admin/v1/tenants/{tenantId}/modules/{moduleKey}/runtime-status`

```json
{
  "enabled": false,
  "reason": "Tenant reported AI responses as inappropriate. Temporarily disabling while we investigate."
}
```

**State written:**
- `tenant_module_entitlements.runtime_override = false`
- All linked integrations with `tenant_integration_credentials.status = 'connected'` updated to `status = 'disabled'` (not disconnected — re-enabling the module restores them without re-OAuth)
- Audit log: `action = 'module.runtime_disabled'`, actor, module, tenant, reason
- Warning alert created: `module.operator_disabled` — visible in tenant's alert list

**Re-enable:** Same flow without the integration disconnect warning. Integrations with `status = 'disabled'` are restored to `status = 'connected'` automatically.

---

## APIs — Full Catalog

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/feature-flags` | List all global flags | `platform.feature_flags.read` |
| POST | `/admin/v1/feature-flags` | Create new flag | `platform.feature_flags.manage` |
| GET | `/admin/v1/feature-flags/{flagKey}` | Flag detail with tenant overrides | `platform.feature_flags.read` |
| PATCH | `/admin/v1/feature-flags/{flagKey}` | Update flag default/rollout/description | `platform.feature_flags.manage` |
| DELETE | `/admin/v1/feature-flags/{flagKey}` | Deactivate flag | `platform.feature_flags.manage` |
| GET | `/admin/v1/feature-flags/tenant-overrides` | All overrides across all flags and tenants | `platform.feature_flags.read` |
| PATCH | `/admin/v1/tenants/{id}/feature-flags/{flagKey}` | Set per-tenant override | `platform.feature_flags.manage` |
| DELETE | `/admin/v1/tenants/{id}/feature-flags/{flagKey}` | Remove per-tenant override | `platform.feature_flags.manage` |
| GET | `/admin/v1/tenants/{id}/feature-flags` | All flag values (effective) for a tenant | `platform.feature_flags.read` |
| PATCH | `/admin/v1/tenants/{id}/modules/{moduleKey}/runtime-status` | Enable/disable module runtime | `platform.feature_flags.manage` |
| GET | `/admin/v1/tenants/{id}/modules/runtime-status` | All module runtime statuses for tenant | `platform.feature_flags.read` |

---

## Error Taxonomy

| HTTP | Code | Condition |
|---|---|---|
| 404 | `flag_not_found` | Flag key does not exist |
| 409 | `flag_key_taken` | Flag key already exists |
| 422 | `invalid_rollout_percentage` | Value outside 0–100 |
| 422 | `phase_2_flag_on_phase_1_tenant` | Attempt to enable a Phase 2 flag for a Phase 1-only tenant |
| 422 | `module_not_entitled` | Override attempt for a module the tenant is not entitled to |
| 403 | `permission_denied` | Missing `platform.feature_flags.manage` |
