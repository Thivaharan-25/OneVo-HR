# Tenant Runtime Overrides - End-to-End Logic

## Purpose

Tenant Runtime Overrides are managed from Tenant Management -> Tenant Detail, not from a top-level Feature Flags sidebar item. They control two things:
1. **Feature flags** - boolean switches that gate features globally with optional per-tenant overrides and rollout percentages
2. **Module enable/disable** - toggle individual ONEVO modules on or off for a specific tenant after activation, without going through the subscription wizard

It does not define paid package contents or prices. Module Catalog defines which module features exist. Commercial inclusion is owned by Subscription Plans, selected optional module add-ons, and tenant subscription/custom commercial snapshots. Runtime flag evaluation must sit after commercial entitlement checks:

```text
feature_key exists in Module Catalog for the module
AND tenant has active module entitlement
AND module runtime override is not false
AND tenant_subscriptions.selected_feature_keys includes the feature_key
AND feature flag evaluates enabled
= feature available
```

Tenant-facing product feature flags must be linked to Module Catalog by setting both `module_key` and `feature_key`. The `feature_key` must exist in `module_features` and belong to the selected `module_key`. Only platform operational flags that are not sold as tenant features may omit both fields.

**Route:** `/platform/tenants/{id}` -> Runtime Overrides tab
**Permission:** `platform.tenants.feature_overrides.read`

---

## Screen Layout

Tenant Detail tab navigation:
- Runtime Overrides
- Feature Flag Overrides
- Module Runtime Status

---

## Runtime Overrides Screen

### Page Header

| Element | Value |
|---|---|
| Title | "Runtime Overrides" |
| Subtitle | "Control this tenant's feature flag overrides and module runtime status." |
| Add Override button | `+ Add Override` - requires `platform.tenants.feature_overrides.manage` |

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

## Create Feature Flag - Full Field Specification

**Trigger:** `+ Create Flag` button

| Field | Label | Type | Required | Validation | Notes |
|---|---|---|---|---|---|
| Flag Key | "Flag Key (slug)" | Text input | Yes | Lowercase, dots/underscores allowed, unique, max 120 chars. Format: `{module_key}.{feature_name}` | Permanent - cannot change after any tenant has a value set. e.g. `chat_ai.streaming_responses`, `work_management.ai_task_suggestions` |
| Description | "Description" | Textarea | Yes | 10-300 chars | Explains what enabling this flag does. Shown to operators. |
| Module | "Owning Module" | Dropdown from module catalog | Required for tenant-facing product flags; empty only for platform operational flags | | Which ONEVO module this flag belongs to. Determines which tenants can have overrides (must be entitled to this module and commercially include this feature) |
| Commercial Feature | "Commercial Feature" | Dropdown from selected module's feature list | Required for tenant-facing product flags; empty only for platform operational flags | Must belong to selected module | Which Module Catalog feature this flag controls at runtime. This is what the tenant subscription/custom contract is checked against. |
| Default Value | "Default State" | Radio: ON / OFF | Yes | | What all tenants get unless overridden. Changing this after creation immediately affects all tenants without an override. |
| Rollout Percentage | "Rollout Percentage" | Number input 0-100 | Yes | | Only meaningful when Default Value = ON. Sets what percentage of tenants actually receive the flag as ON. 100 = all tenants. 0 = no tenants (effectively OFF). Used for gradual rollouts. |
| Phase | "Phase" | Radio: 1 / 2 | Yes | | Phase 2 flags are visible in the manager but cannot be enabled for Phase 1 tenants |
| Is Active | "Active" | Toggle | Yes | Default: On | Inactive flags always evaluate to false. Overrides are preserved but ignored until the flag is reactivated. |

### How Rollout Percentage Works

When `default_value = true` and `rollout_percentage = 30`:
- For each tenant without an explicit override, the backend calculates: `hash(tenant_id + flag_key) % 100 < 30`
- The hash is deterministic - the same tenant always gets the same result for the same flag
- Result: exactly ~30% of tenants (those whose hash falls in range) get ON; ~70% get OFF
- Tenants with an explicit override always use their override value, regardless of rollout %

When `default_value = false`: rollout_percentage has no effect - the flag is OFF for everyone without an override.

### Phase 1 Runtime Flag Seed List

Seed only these Phase 1 runtime flags by default. Do not create runtime flags for every normal CRUD feature; use module entitlement, plan feature inclusion, permissions, or tenant configuration for stable capabilities.

| Flag Key | Module | Feature Key | Default Value | Rollout % | Purpose |
|---|---|---|---|---|---|
| `leave.accrual_rules` | `leave` | `leave.accrual_rules` | true | 100 | Allows staged rollout of advanced leave accrual logic |
| `monitoring.website_usage` | `monitoring` | `monitoring.website_usage` | false | 0 | Privacy-sensitive tracking control |
| `monitoring.screenshot_on_demand` | `monitoring` | `monitoring.screenshot_on_demand` | false | 0 | Privacy-sensitive screenshot command control |
| `monitoring.app_allowlist` | `monitoring` | `monitoring.app_allowlist` | true | 100 | Allows emergency disable of allowlist enforcement |
| `monitoring.productivity_classification` | `monitoring` | `monitoring.productivity_classification` | true | 100 | Allows rollback of productivity classification rules |
| `workforce.overtime` | `workforce` | `workforce.overtime` | true | 100 | Controls overtime workflows where tenant rollout varies |
| `workforce.attendance_corrections` | `workforce` | `workforce.attendance_corrections` | true | 100 | Controls attendance correction workflow rollout |
| `workforce.biometric_devices` | `workforce` | `workforce.biometric_devices` | false | 0 | Hardware-dependent rollout |
| `verification.face_match` | `verification` | `verification.face_match` | false | 0 | AI/biometric rollout control |
| `verification.manual_review` | `verification` | `verification.manual_review` | true | 100 | Allows operational disable of manual review queue |
| `verification.photo_challenge` | `verification` | `verification.photo_challenge` | false | 0 | Camera/biometric challenge rollout |
| `exceptions.baseline_relative_rules` | `exceptions` | `exceptions.baseline_relative_rules` | true | 100 | Allows rollback of baseline-relative alert conditions |
| `exceptions.remote_screenshot_request` | `exceptions` | `exceptions.remote_screenshot_request` | false | 0 | Privacy-sensitive remote command |
| `exceptions.remote_photo_request` | `exceptions` | `exceptions.remote_photo_request` | false | 0 | Privacy-sensitive remote command |
| `analytics.productivity_dashboard` | `analytics` | `analytics.productivity_dashboard` | true | 100 | Allows tenant-level dashboard rollout control |
| `analytics.data_export` | `analytics` | `analytics.data_export` | false | 0 | Controls sensitive data export access |
| `analytics.scheduled_reports` | `analytics` | `analytics.scheduled_reports` | false | 0 | Background report rollout control |
| `work_management.resource_planning` | `work_management` | `work_management.resource_planning` | false | 0 | Advanced WorkSync feature rollout |
| `work_management.work_analytics` | `work_management` | `work_management.work_analytics` | false | 0 | WorkSync analytics rollout |
| `work_management.github_integration` | `work_management` | `work_management.github_integration` | false | 0 | Integration-dependent rollout |
| `work_management.automation_rules` | `work_management` | `work_management.automation_rules` | false | 0 | Automation rollout and emergency disable |
| `chat.message_search` | `chat` | `chat.message_search` | false | 0 | Search/index rollout control |
| `chat.teams_sync` | `chat` | `chat.teams_sync` | false | 0 | Microsoft Teams sync rollout |
| `chat_ai.agentic_chat` | `chat_ai` | `chat_ai.agentic_chat` | false | 0 | AI feature rollout and provider dependency control |
| `chat_ai.streaming_responses` | `chat_ai` | `chat_ai.streaming_responses` | false | 0 | Streaming response rollout |
| `chat_ai.ai_task_suggestions` | `chat_ai` | `chat_ai.ai_task_suggestions` | false | 0 | AI task suggestion rollout |
| `chat_ai.ai_summaries` | `chat_ai` | `chat_ai.ai_summaries` | false | 0 | AI summary rollout |
| `chat_ai.ai_insights` | `chat_ai` | `chat_ai.ai_insights` | false | 0 | AI insight rollout |
| `integrations.microsoft_teams` | `integrations` | `integrations.microsoft_teams` | false | 0 | Tenant integration rollout |
| `integrations.github` | `integrations` | `integrations.github` | false | 0 | Tenant integration rollout |
| `integrations.webhooks` | `integrations` | `integrations.webhooks` | false | 0 | Webhook surface rollout |
| `integrations.api_access` | `integrations` | `integrations.api_access` | false | 0 | Public/API access rollout |

Optional operational foundation flags may be seeded if the backend implements them as global operational safeguards, but they must not be sold as plan features:

| Flag Key | Module | Default Value | Rollout % | Purpose |
|---|---|---|---|---|
| `auth.optional_google_oauth` | `auth` | false | 0 | Enable optional Google OAuth setup/sign-in for invited managers only |
| `auth.mfa_enforcement` | `auth` | true | 100 | Gradual MFA enforcement |
| `notifications.email_delivery` | `notifications` | true | 100 | Emergency disable for outbound email |
| `notifications.in_app_delivery` | `notifications` | true | 100 | Emergency disable for in-app notifications |
| `workflow_engine.automation_execution` | `workflow_engine` | true | 100 | Emergency stop for automation execution |

### Save Flag

**API:** `POST /admin/v1/feature-flags`

```json
{
  "flag_key": "chat_ai.streaming_responses",
  "description": "Enable streaming token-by-token responses in the Agentic Chat UI instead of waiting for full response.",
  "module_key": "chat_ai",
  "feature_key": "chat_ai.streaming_responses",
  "default_value": false,
  "rollout_percentage": 0,
  "phase": 1,
  "is_active": true
}
```

**State written:** `feature_flags` row created. Audit log: `action = 'feature_flag.created'`, actor, flag_key, default_value.

**Commercial boundary:** Creating a feature flag does not add the feature to any paid plan, tenant subscription, or pricing package. Operators must first register the feature key in Module Catalog, then commercially include it through a Subscription Plan, selected optional module add-on, or audited tenant subscription/custom override before any tenant can receive runtime access.

**Production testing one feature for one tenant:**
1. Register the feature key in Module Catalog.
2. Do not add it to normal plan `included_feature_keys`.
3. Add it only to the test tenant's `tenant_subscriptions.selected_feature_keys` through an audited subscription/custom override.
4. Enable the runtime flag only for that tenant.
5. Optionally expose it only to selected roles/users through `feature_access_grants`.

---

## Global Flag Toggle - Full Flow

**Trigger:** Click the toggle on a flag row OR open flag detail and click the toggle.

### Toggle Without Confirmation (default_value already set, changing rollout %)

No confirmation dialog. `PATCH /admin/v1/feature-flags/{flagKey}` with updated `rollout_percentage`.

### Toggle With Confirmation (changing default_value)

Changing `default_value` is a high-impact action - it immediately affects all tenants without an override.

**Confirmation dialog:**

```
Changing "chat_ai.streaming_responses" default from OFF -> ON

This will enable this feature for all tenants that do not have an explicit override set.
Currently: 0 tenants have overrides. ~847 active tenants will be affected.

Are you sure?
```

**Fields in dialog:**

| Field | Type | Required | Notes |
|---|---|---|---|
| Reason | Textarea | Yes - min 10 chars | "Why are you changing this default? This is audit-logged." |

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
- Flag evaluation cache invalidated for all tenants without an override - takes effect on next cache miss (within 60 seconds)
- No tenant restart required

---

## Flag Detail Reference

**Operator route:** Tenant Detail -> Runtime Overrides

**API:** `GET /admin/v1/feature-flags/{flagKey}`

### Sections

**1. Flag Info**
Shows: flag key, description, module badge, default value, rollout %, phase, is_active, created by, created at, last modified by, last modified at.

**Edit** button opens the full create form pre-populated. All fields editable except `flag_key`.

**2. Tenant Overrides Table**

All tenants that have a non-default override for this flag.

| Column | Description |
|---|---|
| Tenant Name | Company name - linked to tenant detail |
| Override Value | ON (green) / OFF (red) - shows the tenant's explicit value |
| Set By | Platform admin who set the override |
| Set At | Timestamp |
| Reason | Reason entered when override was created |
| Actions | Remove Override |

"Add Override" button -> opens the per-tenant override flow.

**3. Audit History**

Last 20 audit events for this flag: default changes, override additions/removals. Each row: timestamp, actor, action, previous value, new value, reason.

---

## Per-Tenant Override - Full Flow

An override sets an explicit value for a specific tenant, bypassing both the default value and rollout % entirely.

It does not bypass commercial eligibility. Before saving `value = true`, the backend validates that:
- the flag belongs to a module in `module_catalog`
- the tenant has an active module entitlement for that module
- the tenant's current subscription snapshot includes the requested feature key in `tenant_subscriptions.selected_feature_keys`

### Add Override

**Trigger:** "Add Override" from Tenant Detail -> Runtime Overrides.

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
  "reason": "Beta testing partner - TechNova requested early access to streaming chat."
}
```

**State written:** `feature_flag_overrides` row created/updated: `(flag_key, tenant_id, value, granted_by_id, granted_at, reason)`.

**Effect:** Takes effect immediately on next request from this tenant (cache invalidated). No tenant restart required.

**Billing effect:** None. If three features are disabled for a tenant, the tenant keeps paying the same subscription price until Subscription Plans or Tenant Management changes the commercial record.

### Remove Override

**Trigger:** "Remove Override" on flag detail -> tenant overrides table.

**No confirmation dialog** for removing overrides - lower risk than adding.

**API:** `DELETE /admin/v1/tenants/{tenantId}/feature-flags/{flagKey}`

**Effect:** Tenant falls back to global default + rollout % evaluation. Audit logged.

### Runtime Overrides Review

**Operator route:** Tenant Management -> Tenant Detail -> Runtime Overrides. Cross-tenant review, if exposed later, belongs under Reports / Analytics or Operations and is not a sidebar item.

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
| Tenant | Company name - linked |
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
- **Tenant Detail -> Runtime Overrides -> Module Runtime Status:** Immediate runtime toggle for a module the tenant is already commercially entitled to; does not change billing, subscription snapshot, or module sales state. Use for debugging, emergency disable, or restoring previously disabled runtime access.
- **Tenant Management -> Subscriptions -> Override Subscription:** Changes the commercial record, module sales state, selected feature keys, and billing. Use when the tenant has actually bought, cancelled, trialed, or been approved to test a module or feature.

Production testing a feature for one tenant must use the subscription override path first to add the feature key to that tenant's commercial snapshot. Runtime overrides may then turn the feature on for that tenant; they must not create commercial feature access by themselves.

**Operator route:** Tenant Detail -> Runtime Overrides -> Module Runtime Status

### Module Toggle Screen

| Filter | Options |
|---|---|
| Tenant | Autocomplete search (required - must select a tenant first) |
| Module | Dropdown from module catalog |
| Status | All / Enabled / Disabled |

After selecting a tenant, shows all modules in the catalog with their current status for that tenant.

| Column | Description |
|---|---|
| Module Name | Full name |
| Module Key | slug |
| Pillar | HR / Intelligence / WorkSync badge |
| Sales State | From `tenant_module_entitlements` - subscription_included, purchased, trial, etc. |
| Runtime Status | Enabled (green) / Disabled (red) - the current toggle state |
| Enabled By | Commercial (from entitlement) / Override (explicitly toggled here) |
| Actions | Enable / Disable toggle |

### Disable Module - Full Flow

**Trigger:** Toggle switch on a module row.

**Pre-check:** System checks for connected integrations that would be affected (same as Module Catalog Manager's unlink warning).

**Confirmation dialog:**

```
WARNING: Disable "Agentic Chat" for TechNova Solutions?

Runtime effect: tenants users will immediately lose access to Agentic Chat.
Billing: not changed - this is a runtime toggle only. Their subscription still includes chat_ai.

Integrations that will be disconnected:
  - Microsoft Teams (connected by james@technova.com, May 12 2024)

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
- All linked integrations with `tenant_integration_credentials.status = 'connected'` updated to `status = 'disabled'` (not disconnected - re-enabling the module restores them without re-OAuth)
- Audit log: `action = 'module.runtime_disabled'`, actor, module, tenant, reason
- Warning alert created: `module.operator_disabled` - visible in tenant's alert list

**Re-enable:** Same flow without the integration disconnect warning. Set `tenant_module_entitlements.runtime_override = true` to explicitly restore runtime access while preserving commercial state. Integrations with `status = 'disabled'` are restored to `status = 'connected'` automatically.

---

## APIs - Full Catalog

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/feature-flags` | List all global flags | `platform.runtime_flags.read` |
| POST | `/admin/v1/feature-flags` | Create new flag | `platform.runtime_flags.manage` |
| GET | `/admin/v1/feature-flags/{flagKey}` | Flag detail with tenant overrides | `platform.runtime_flags.read` |
| PATCH | `/admin/v1/feature-flags/{flagKey}` | Update flag default/rollout/description | `platform.runtime_flags.manage` |
| DELETE | `/admin/v1/feature-flags/{flagKey}` | Deactivate flag | `platform.runtime_flags.manage` |
| GET | `/admin/v1/feature-flags/tenant-overrides` | All overrides across all flags and tenants | `platform.tenants.feature_overrides.read` |
| PUT | `/admin/v1/tenants/{id}/feature-flags` | Replace all tenant overrides with an `overrides` value map | `platform.tenants.feature_overrides.manage` |
| PATCH | `/admin/v1/tenants/{id}/feature-flags/{flagKey}` | Set per-tenant override with `{ "value": true | false, "reason": "..." }` | `platform.tenants.feature_overrides.manage` |
| DELETE | `/admin/v1/tenants/{id}/feature-flags/{flagKey}` | Remove per-tenant override | `platform.tenants.feature_overrides.manage` |
| GET | `/admin/v1/tenants/{id}/feature-flags` | All flag values (effective) for a tenant | `platform.tenants.feature_overrides.read` |
| PATCH | `/admin/v1/tenants/{id}/modules/{moduleKey}/runtime-status` | Enable/disable module runtime | `platform.tenants.feature_overrides.manage` |
| GET | `/admin/v1/tenants/{id}/modules/runtime-status` | All module runtime statuses for tenant | `platform.tenants.feature_overrides.read` |

---

## Error Taxonomy

| HTTP | Code | Condition |
|---|---|---|
| 404 | `flag_not_found` | Flag key does not exist |
| 409 | `flag_key_taken` | Flag key already exists |
| 422 | `invalid_rollout_percentage` | Value outside 0-100 |
| 422 | `phase_2_flag_on_phase_1_tenant` | Attempt to enable a Phase 2 flag for a Phase 1-only tenant |
| 422 | `module_not_entitled` | Override attempt for a module the tenant is not entitled to |
| 403 | `permission_denied` | Missing `platform.tenants.feature_overrides.manage` for tenant overrides, or `platform.runtime_flags.manage` for global flag definitions |
