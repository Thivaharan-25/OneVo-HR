# Shared Platform — Schema

**Module:** [[modules/shared-platform/overview|Shared Platform]]
**Phase:** Phase 1 + Phase 2 integration additions
**Tables:** 36

---

## `api_keys`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | Friendly name |
| `key_hash` | `varchar(255)` | SHA-256 hash (never store raw) |
| `key_prefix` | `varchar(10)` | First 8 chars for identification |
| `scopes` | `jsonb` | Permitted API scopes |
| `expires_at` | `timestamptz` | Nullable |
| `is_active` | `boolean` |  |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` |  |
| `last_used_at` | `timestamptz` | Nullable |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `created_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `approval_actions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `workflow_instance_id` | `uuid` | FK → workflow_instances |
| `workflow_step_id` | `uuid` | FK → workflow_steps |
| `actor_id` | `uuid` | FK → employees |
| `action` | `varchar(20)` | `approve`, `reject`, `delegate`, `request_info` |
| `comment` | `text` | Nullable |
| `acted_at` | `timestamptz` |  |
| `delegated_to_id` | `uuid` | FK → employees (nullable — only for delegate action) |

**Foreign Keys:** `workflow_instance_id` → [[#`workflow_instances`|workflow_instances]], `workflow_step_id` → [[#`workflow_steps`|workflow_steps]], `actor_id` → [[database/schemas/core-hr#`employees`|employees]], `delegated_to_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## `compliance_exports`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `requested_by_id` | `uuid` | FK → users |
| `export_type` | `varchar(30)` | `subject_access`, `data_portability`, `erasure` |
| `scope` | `varchar(30)` | `full`, `partial` |
| `target_user_id` | `uuid` | FK → users (whose data) |
| `status` | `varchar(20)` | `pending`, `processing`, `completed`, `failed` |
| `file_url` | `varchar(500)` | Download URL when completed |
| `requested_at` | `timestamptz` |  |
| `completed_at` | `timestamptz` | Nullable |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `requested_by_id` → [[database/schemas/infrastructure#`users`|users]], `target_user_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `escalation_rules`

> **Scope:** Workflow SLA timeouts — fires when a workflow item (leave request, expense claim, etc.) sits in a pending state longer than `sla_hours`. See [[database/schemas/exception-engine#`escalation_chains`|escalation_chains]] for alert routing on system-detected anomalies — that is a separate system.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `resource_type` | `varchar(50)` | e.g., `leave_request`, `expense_claim` |
| `trigger_condition` | `varchar(100)` | e.g., `status = 'pending'` |
| `sla_hours` | `integer` | Hours before escalation fires |
| `action_type` | `varchar(30)` | `remind`, `escalate`, `auto_approve` |
| `escalate_to_role_id` | `uuid` | FK → roles (nullable) |
| `notification_template_id` | `uuid` | FK → notification_templates |
| `is_active` | `boolean` |  |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `escalate_to_role_id` → [[database/schemas/auth#`roles`|roles]], `notification_template_id` → [[#`notification_templates`|notification_templates]], `created_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `global_app_catalog`

Global catalog of known applications managed by the OneVo dev team via the developer platform. No `tenant_id` — shared across all tenants. HR admins browse this when configuring app allowlists.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `app_name` | `varchar(200)` | e.g., "Google Chrome" |
| `process_name` | `varchar(100)` | e.g., "chrome.exe" — authoritative matching key used by ingest processor |
| `category` | `varchar(50)` | `browser`, `communication`, `development`, `office`, `design`, `productivity`, `other` |
| `publisher` | `varchar(200)` | e.g., "Google LLC" |
| `icon_url` | `varchar(500)` | App icon for HR admin UI display |
| `is_public` | `boolean` | True = visible to all HR admins in catalog browser |
| `is_productive_default` | `boolean` | Default productivity classification applied when no tenant override exists |
| `created_by_id` | `uuid` | FK → dev_platform_accounts |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Foreign Keys:** `created_by_id` → `dev_platform_accounts`

**Index:** `process_name` UNIQUE — no duplicate process names in catalog.

> Managed via `/admin/v1/app-catalog/*` endpoints in the developer platform. See [[docs/superpowers/plans/2026-04-26-app-catalog-observed-applications|App Catalog Plan]] and [[database/schemas/configuration#`observed_applications`|observed_applications]] for the per-tenant discovery table.

---

## `feature_flags`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `flag_key` | `varchar(100)` | Unique per tenant |
| `is_enabled` | `boolean` |  |
| `conditions` | `jsonb` | Targeting rules (e.g., percentage rollout, user segment) |
| `toggled_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `toggled_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `hardware_terminals`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `office_location_id` | `uuid` | FK → office_locations |
| `terminal_code` | `varchar(50)` | Unique device code |
| `terminal_type` | `varchar(30)` | `biometric`, `rfid`, `kiosk` |
| `webhook_url` | `varchar(500)` | Callback URL for events |
| `api_key_encrypted` | `bytea` | Encrypted terminal API key |
| `status` | `varchar(20)` | `active`, `offline`, `maintenance` |
| `last_heartbeat_at` | `timestamptz` |  |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `office_location_id` → [[database/schemas/org-structure#`office_locations`|office_locations]]

---

## `legal_holds`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `resource_type` | `varchar(50)` | Polymorphic |
| `resource_id` | `uuid` | Polymorphic |
| `reason` | `text` |  |
| `placed_by_id` | `uuid` | FK → users |
| `placed_at` | `timestamptz` |  |
| `released_by_id` | `uuid` | FK → users (nullable) |
| `released_at` | `timestamptz` | Nullable |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `placed_by_id` → [[database/schemas/infrastructure#`users`|users]], `released_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `notification_channels`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `channel_type` | `varchar(30)` | `email`, `push`, `slack` |
| `provider` | `varchar(50)` | `resend`, `fcm`, `slack_webhook` |
| `credentials_encrypted` | `jsonb` | Encrypted API keys/tokens |
| `is_active` | `boolean` |  |
| `configured_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `configured_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `notification_templates`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `template_code` | `varchar(50)` | e.g., `leave_requested`, `payroll_completed` |
| `channel` | `varchar(20)` | `email`, `push`, `in_app` |
| `subject_template` | `text` | For email subject line |
| `body_template` | `text` | Handlebars/Liquid template |
| `locale` | `varchar(10)` | e.g., `en`, `si`, `ta` |
| `version` | `integer` |  |
| `is_active` | `boolean` |  |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `created_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `payment_methods`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `type` | `varchar(20)` | `card`, `bank_transfer` |
| `last_four` | `varchar(4)` | Last 4 digits |
| `brand` | `varchar(20)` | `visa`, `mastercard`, etc. |
| `expiry_month` | `integer` |  |
| `expiry_year` | `integer` |  |
| `is_default` | `boolean` |  |
| `payment_provider_ref` | `varchar(100)` | Stripe payment method ID |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `plan_features`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `plan_id` | `uuid` | FK → subscription_plans |
| `feature_key` | `varchar(100)` | e.g., `payroll`, `activity_monitoring` |
| `limit_value` | `integer` | Nullable — null means unlimited |
| `is_included` | `boolean` |  |

**Foreign Keys:** `plan_id` → [[#`subscription_plans`|subscription_plans]]

---

## `module_catalog`

Global commercial catalog for modules and add-ons. This supports both subscription sales and full-license plus maintenance sales. No tenant access should be inferred from this table alone; it provides default pricing and catalog metadata.

| Column | Type | Notes |
|:-------|:-----|:------|
| `module_key` | `varchar(100)` | PK; e.g., `core_hr`, `leave`, `payroll`, `workforce_intelligence` |
| `name` | `varchar(150)` | Display name |
| `pillar` | `varchar(50)` | `hr`, `workforce_intelligence`, `worksync`, `shared` |
| `phase` | `varchar(30)` | `phase_1`, `phase_2`, `future`, or product-defined release phase |
| `default_price_monthly` | `decimal(10,2)` | Nullable default subscription add-on price |
| `default_price_annual` | `decimal(10,2)` | Nullable default annual subscription add-on price |
| `full_license_price` | `decimal(12,2)` | Nullable one-time purchase price |
| `default_maintenance_rate` | `decimal(5,2)` | Nullable yearly percentage for maintenance, e.g., 18.00 |
| `pricing_unit` | `varchar(30)` | `per_employee`, `per_device`, `flat`, `custom` |
| `is_active` | `boolean` | Whether the module can be sold/provisioned |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

---

## `tenant_module_entitlements`

Tenant-level module/commercial entitlement records. Use this table for module-wise sales, trials, quoted modules, maintenance-included modules, and manual add-ons. It complements `tenant_subscriptions` and `subscription_plans`; it does not replace RBAC.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `module_key` | `varchar(100)` | FK -> module_catalog.module_key |
| `sales_state` | `varchar(30)` | `available`, `purchased`, `trial`, `quoted`, `maintenance_included`, `subscription_included`, `disabled` |
| `pricing_model` | `varchar(30)` | `subscription`, `full_license`, `maintenance`, `trial`, `custom` |
| `price` | `decimal(12,2)` | Nullable override price |
| `currency` | `varchar(3)` | ISO 4217 |
| `starts_at` | `date` | Nullable entitlement start |
| `ends_at` | `date` | Nullable entitlement end/trial expiry |
| `created_by_id` | `uuid` | FK -> users or dev platform account boundary, depending on implementation |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Entitlement rule:** For subscription tenants, enabled modules = plan included modules + paid add-ons + trial modules - disabled modules. For full-license tenants, enabled modules = owned license modules + maintenance-included modules + purchased add-ons + trial modules - disabled modules. `available` and `quoted` are commercial pipeline states and do not grant tenant-facing access. Permission catalogs are filtered after module entitlement resolution.

---

## `subscription_plan_price_history`

Audit/history for reusable subscription plan catalog price changes. This preserves historical pricing decisions without silently rewriting tenant contracts.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `plan_id` | `uuid` | FK -> subscription_plans |
| `old_monthly_price` | `decimal(10,2)` | Nullable |
| `new_monthly_price` | `decimal(10,2)` | Nullable |
| `old_annual_price` | `decimal(10,2)` | Nullable |
| `new_annual_price` | `decimal(10,2)` | Nullable |
| `old_currency` | `varchar(3)` | Nullable |
| `new_currency` | `varchar(3)` | ISO 4217 |
| `old_pricing_unit` | `varchar(30)` | Nullable |
| `new_pricing_unit` | `varchar(30)` | `per_employee`, `per_device`, `flat`, `custom` |
| `changed_by_id` | `uuid` | FK -> users or dev platform account boundary |
| `reason` | `text` | Required business reason |
| `changed_at` | `timestamptz` | |

**Foreign Keys:** `plan_id` -> [[#`subscription_plans`|subscription_plans]]

---

## `module_catalog_price_history`

Audit/history for reusable module catalog price changes.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `module_key` | `varchar(100)` | FK -> module_catalog.module_key |
| `old_default_price_monthly` | `decimal(10,2)` | Nullable |
| `new_default_price_monthly` | `decimal(10,2)` | Nullable |
| `old_default_price_annual` | `decimal(10,2)` | Nullable |
| `new_default_price_annual` | `decimal(10,2)` | Nullable |
| `old_full_license_price` | `decimal(12,2)` | Nullable |
| `new_full_license_price` | `decimal(12,2)` | Nullable |
| `old_default_maintenance_rate` | `decimal(5,2)` | Nullable |
| `new_default_maintenance_rate` | `decimal(5,2)` | Nullable |
| `old_pricing_unit` | `varchar(30)` | Nullable |
| `new_pricing_unit` | `varchar(30)` | `per_employee`, `per_device`, `flat`, `custom` |
| `changed_by_id` | `uuid` | FK -> users or dev platform account boundary |
| `reason` | `text` | Required business reason |
| `changed_at` | `timestamptz` | |

**Foreign Keys:** `module_key` -> [[#`module_catalog`|module_catalog]]

---

## `tenant_provisioning_states`

Draft-safe provisioning wizard state. This is the source for resume behavior and activation checklist state.

| Column | Type | Notes |
|:-------|:-----|:------|
| `tenant_id` | `uuid` | PK, FK -> tenants |
| `current_step` | `varchar(50)` | `tenant_details`, `subscription`, `modules`, `roles`, `settings`, `owner_invite`, `review` |
| `tenant_details_completed_at` | `timestamptz` | Nullable |
| `subscription_completed_at` | `timestamptz` | Nullable |
| `modules_completed_at` | `timestamptz` | Nullable |
| `roles_completed_at` | `timestamptz` | Nullable |
| `settings_completed_at` | `timestamptz` | Nullable |
| `owner_invite_completed_at` | `timestamptz` | Nullable |
| `activation_ready` | `boolean` | Cached readiness after latest validation |
| `activated_at` | `timestamptz` | Nullable |
| `last_updated_by_id` | `uuid` | FK -> users or dev platform account boundary |
| `updated_at` | `timestamptz` | |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `tenant_provisioning_validation_results`

Latest activation blockers and warnings returned by `/admin/v1/tenants/{id}/provisioning-summary`.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `section` | `varchar(50)` | Provisioning section |
| `code` | `varchar(100)` | Machine-readable validation code |
| `message` | `text` | Human-readable message |
| `severity` | `varchar(20)` | `blocker` or `warning` |
| `resolved_at` | `timestamptz` | Nullable |
| `created_at` | `timestamptz` | |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]]

---

## Commercial Entitlement Notes

The schema supports the commercial model requested by product:

- `tenant_subscriptions.commercial_model` records `subscription` vs `full_license_maintenance`.
- Subscription tenants normally use `tenant_subscriptions.subscription_collection_mode = gateway` with `gateway_provider` and gateway refs so recurring SaaS fees are collected through the payment gateway.
- Full-license tenants can use `tenant_subscriptions.license_payment_mode = manual` for the one-time license sale; `full_license_amount`, `license_paid_at`, and `license_reference` record the manual/offline purchase.
- `tenant_subscriptions.maintenance_collection_mode = gateway` means full-license maintenance/support is collected through the system payment gateway even when the one-time license was manually paid.
- `tenant_subscriptions.maintenance_status`, `maintenance_start_date`, `maintenance_renewal_date`, `maintenance_rate`, and `maintenance_amount` track maintenance state and recurring fee calculation for full-license tenants.
- `tenant_module_entitlements.sales_state` records manual sales state per module: `available`, `purchased`, `trial`, `quoted`, `maintenance_included`, `subscription_included`, or `disabled`.
- Pricing defaults live on `subscription_plans` and `module_catalog`; tenant-specific negotiated pricing lives on `tenant_subscriptions` and `tenant_module_entitlements`.

Pricing and module entitlement decide what the tenant has access to. RBAC permissions decide which users inside that tenant can use the entitled capabilities.

Catalog price changes do not silently update existing tenant commercial records. Existing tenant subscriptions and module entitlements keep their stored negotiated prices unless ONEVO runs an explicit reviewed reprice/migration process.

---

## `rate_limit_rules`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants (nullable — null for global rules) |
| `endpoint_pattern` | `varchar(200)` | e.g., `/api/v1/leave/*` |
| `max_requests` | `integer` | Per window |
| `window_seconds` | `integer` | Sliding window size |
| `is_active` | `boolean` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `refresh_tokens`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `user_id` | `uuid` | FK → users |
| `tenant_id` | `uuid` | FK → tenants |
| `token_hash` | `varchar(255)` | SHA-256 hash (never store raw token) |
| `device_fingerprint` | `varchar(255)` | Browser/device identifier |
| `issued_at` | `timestamptz` |  |
| `expires_at` | `timestamptz` |  |
| `is_revoked` | `boolean` |  |
| `replaced_by_id` | `uuid` | FK → refresh_tokens (rotation chain) |

**Foreign Keys:** `user_id` → [[database/schemas/infrastructure#`users`|users]], `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `replaced_by_id` → [[#`refresh_tokens`|refresh_tokens]]

---

## `retention_policies`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `resource_type` | `varchar(50)` |  |
| `retention_days` | `integer` |  |
| `action_on_expiry` | `varchar(30)` | `delete`, `anonymize`, `archive` |
| `compliance_framework` | `varchar(50)` | e.g., `GDPR`, `local_labor_law` |
| `is_active` | `boolean` |  |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `created_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `scheduled_tasks`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants (nullable — null for system tasks) |
| `task_type` | `varchar(100)` | Job class name |
| `cron_expression` | `varchar(50)` |  |
| `description` | `text` |  |
| `is_active` | `boolean` |  |
| `last_run_at` | `timestamptz` | Nullable |
| `next_run_at` | `timestamptz` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `signalr_connections`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `user_id` | `uuid` | FK → users |
| `tenant_id` | `uuid` | FK → tenants |
| `connection_id` | `varchar(100)` | SignalR connection ID |
| `channel` | `varchar(30)` | `web`, `mobile`, `desktop_agent` |
| `device_type` | `varchar(30)` | `browser`, `ios`, `android`, `windows` |
| `connected_at` | `timestamptz` |  |
| `last_ping_at` | `timestamptz` |  |
| `is_active` | `boolean` |  |

**Foreign Keys:** `user_id` → [[database/schemas/infrastructure#`users`|users]], `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `sso_providers`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `provider_type` | `varchar(30)` | Phase 1: `google` only. Future: `saml`, `oidc` if needed. Microsoft Teams is not an SSO provider in Phase 1. |
| `name` | `varchar(100)` | Display name |
| `client_id_encrypted` | `bytea` | Encrypted via IEncryptionService |
| `client_secret_encrypted` | `bytea` | Encrypted via IEncryptionService |
| `metadata_url` | `varchar(500)` | SAML metadata / OIDC discovery URL |
| `domain_hint` | `varchar(100)` | Auto-select provider by email domain |
| `auto_provision_users` | `boolean` | Create user on first SSO login |
| `is_active` | `boolean` |  |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `external_account_connections`

User-level links to external product accounts such as Microsoft Teams. Used to verify whether a ONEVO user can send/sync Teams messages. This is integration account linking, not ONEVO login SSO.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `user_id` | `uuid` | FK -> users |
| `provider` | `varchar(30)` | `microsoft_teams`, future providers |
| `external_user_id` | `varchar(255)` | Azure AD user id for Teams |
| `external_email` | `varchar(255)` | Email/mail returned by Graph |
| `display_name` | `varchar(200)` | External display name |
| `status` | `varchar(20)` | `active`, `reauth_required`, `revoked`, `disabled` |
| `linked_at` | `timestamptz` | |
| `last_verified_at` | `timestamptz` | Nullable |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Unique:** `(tenant_id, provider, user_id)`, `(tenant_id, provider, external_user_id)`

---

## `microsoft_graph_tokens`

Encrypted Microsoft Graph token material for Teams sync. Raw tokens are never logged or returned by API.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `external_account_connection_id` | `uuid` | FK -> external_account_connections |
| `access_token_encrypted` | `bytea` | Nullable; short lived |
| `refresh_token_encrypted` | `bytea` | Encrypted refresh token |
| `scopes` | `jsonb` | Granted Graph scopes |
| `expires_at` | `timestamptz` | Access token expiry |
| `last_refresh_at` | `timestamptz` | Nullable |
| `revoked_at` | `timestamptz` | Nullable |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

---

## `teams_webhook_subscriptions`

Microsoft Graph change notification subscriptions for linked Teams channels/chats.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `resource_type` | `varchar(30)` | `channel_messages`, `chat_messages` |
| `resource_id` | `varchar(500)` | Graph resource path or Teams channel/chat id |
| `subscription_id` | `varchar(255)` | Graph subscription id |
| `client_state_hash` | `varchar(255)` | Hash of webhook client state |
| `expires_at` | `timestamptz` | Graph subscription expiry |
| `status` | `varchar(20)` | `active`, `renewal_due`, `expired`, `failed` |
| `last_notification_at` | `timestamptz` | Nullable |
| `last_error` | `text` | Nullable |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

---

## `teams_delta_sync_state`

Stores Microsoft Graph delta tokens and cursor state for reliable Teams message import.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `resource_type` | `varchar(30)` | `team_channel`, `chat` |
| `resource_id` | `varchar(500)` | Teams channel/chat id |
| `delta_token_encrypted` | `bytea` | Encrypted delta token |
| `last_delta_at` | `timestamptz` | Nullable |
| `status` | `varchar(20)` | `active`, `reset_required`, `failed` |
| `last_error` | `text` | Nullable |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Unique:** `(tenant_id, resource_type, resource_id)`

---

## `subscription_invoices`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `subscription_id` | `uuid` | FK → tenant_subscriptions |
| `invoice_number` | `varchar(50)` |  |
| `amount` | `decimal(10,2)` |  |
| `currency` | `varchar(3)` |  |
| `status` | `varchar(20)` | `draft`, `open`, `paid`, `void` |
| `payment_provider_ref` | `varchar(100)` | Stripe invoice ID |
| `issued_at` | `timestamptz` |  |
| `paid_at` | `timestamptz` | Nullable |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `subscription_id` → [[#`tenant_subscriptions`|tenant_subscriptions]]

---

## `billing_snapshots`

End-of-month snapshot of billable units per tenant. Used to generate `subscription_invoices` and as a cached fallback when live active-user/device counts are unavailable.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `snapshot_date` | `date` | Last day of the billing month |
| `active_employee_count` | `integer` | Active employees at snapshot time |
| `enrolled_device_count` | `integer` | Enrolled devices at snapshot time |
| `employee_breakdown` | `jsonb` | Count by department |
| `device_breakdown` | `jsonb` | Count by department |
| `created_at` | `timestamptz` | |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

**Unique:** `(tenant_id, snapshot_date)` — one snapshot per tenant per month.

---

## `subscription_plans`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `name` | `varchar(100)` |  |
| `code` | `varchar(20)` | `starter`, `professional`, `enterprise` |
| `tier` | `varchar(20)` | Ordering tier |
| `feature_limits` | `jsonb` | e.g., `{"max_employees": 50, "modules": ["core_hr","leave"]}` |
| `included_modules` | `jsonb` | Plan-allowed/included module keys used by entitlement resolution |
| `pricing_unit` | `varchar(30)` | `per_employee`, `per_device`, `flat`, `custom` |
| `monthly_price` | `decimal(10,2)` |  |
| `annual_price` | `decimal(10,2)` |  |
| `currency` | `varchar(3)` | ISO 4217 |
| `is_active` | `boolean` |  |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

---

## `system_settings`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `setting_key` | `varchar(100)` | Unique |
| `setting_value` | `jsonb` |  |
| `description` | `text` |  |
| `updated_by_id` | `uuid` | FK → users |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `updated_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `tenant_branding`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `custom_domain` | `varchar(255)` | Nullable |
| `logo_file_id` | `uuid` | FK → file_records (nullable) |
| `primary_color` | `varchar(7)` | Hex color |
| `accent_color` | `varchar(7)` | Hex color |
| `metadata` | `jsonb` | Additional branding config |
| `updated_by_id` | `uuid` | FK → users |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `logo_file_id` → [[database/schemas/infrastructure#`file_records`|file_records]], `updated_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `tenant_feature_flags`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `flag_key` | `varchar(100)` |  |
| `is_enabled` | `boolean` | Override value |
| `overridden_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `overridden_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `tenant_subscriptions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `plan_id` | `uuid` | FK → subscription_plans |
| `billing_cycle` | `varchar(20)` | `monthly`, `annual` |
| `status` | `varchar(20)` | `active`, `past_due`, `cancelled`, `trialing` |
| `current_period_start` | `date` |  |
| `current_period_end` | `date` |  |
| `payment_provider_ref` | `varchar(100)` | Legacy provider ref; prefer explicit gateway refs below |
| `commercial_model` | `varchar(30)` | `subscription` or `full_license_maintenance` |
| `billing_currency` | `varchar(3)` | ISO 4217; overrides plan currency for custom contracts |
| `subscription_collection_mode` | `varchar(20)` | `gateway` or `manual`; subscriptions normally use `gateway` |
| `gateway_provider` | `varchar(50)` | `stripe`, `payhere`, or configured payment provider |
| `gateway_customer_ref` | `varchar(100)` | Nullable payment gateway customer ID |
| `gateway_subscription_ref` | `varchar(100)` | Nullable payment gateway recurring subscription ID |
| `license_payment_mode` | `varchar(20)` | `manual` or `gateway`; full-license one-time sale can be manual |
| `full_license_amount` | `decimal(12,2)` | Nullable one-time full-license amount |
| `license_paid_at` | `date` | Nullable date the full license was paid/recorded |
| `license_reference` | `varchar(100)` | Nullable invoice/reference number for manual full-license sale |
| `maintenance_collection_mode` | `varchar(20)` | `gateway`, `manual`, or `waived`; maintenance normally uses gateway |
| `maintenance_billing_cycle` | `varchar(20)` | `monthly` or `annual`, nullable when waived |
| `contract_start_date` | `date` | Commercial agreement start date |
| `contract_end_date` | `date` | Nullable; required if agreement is fixed-term |
| `maintenance_status` | `varchar(20)` | `active`, `due`, `expired`, `waived`; used for full-license tenants |
| `maintenance_start_date` | `date` | Nullable; first maintenance billing period start |
| `maintenance_renewal_date` | `date` | Nullable; next maintenance renewal date |
| `maintenance_rate` | `decimal(5,2)` | Nullable percentage of license value, e.g., 18.00 |
| `maintenance_amount` | `decimal(12,2)` | Nullable explicit recurring maintenance amount when not rate-derived |
| `custom_contract_value` | `decimal(12,2)` | Nullable manually-entered enterprise contract amount |
| `discount_percent` | `decimal(5,2)` | Nullable negotiated discount applied to the tenant commercial record |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `plan_id` → [[#`subscription_plans`|subscription_plans]], `created_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `user_preferences`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `user_id` | `uuid` | FK → users |
| `tenant_id` | `uuid` | FK → tenants |
| `preference_key` | `varchar(100)` | e.g., `theme`, `locale`, `timezone` |
| `preference_value` | `jsonb` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `user_id` → [[database/schemas/infrastructure#`users`|users]], `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `webhook_deliveries`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `webhook_endpoint_id` | `uuid` | FK → webhook_endpoints |
| `event_type` | `varchar(50)` |  |
| `payload` | `jsonb` | Sent payload |
| `response_status` | `integer` | HTTP status code |
| `response_body` | `text` | Truncated response |
| `attempt_number` | `integer` | Retry count |
| `delivered_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `webhook_endpoint_id` → [[#`webhook_endpoints`|webhook_endpoints]]

---

## `webhook_endpoints`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `url` | `varchar(500)` | Target URL |
| `secret_hash` | `varchar(255)` | HMAC signing secret hash |
| `events` | `jsonb` | Subscribed event types |
| `is_active` | `boolean` |  |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `created_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `workflow_definitions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` |  |
| `code` | `varchar(50)` | Unique identifier |
| `resource_type` | `varchar(50)` | e.g., `LeaveRequest`, `ExpenseClaim` |
| `description` | `text` |  |
| `is_active` | `boolean` |  |
| `version` | `integer` | Versioning for definition changes |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `created_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `workflow_instances`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `workflow_definition_id` | `uuid` | FK → workflow_definitions |
| `resource_type` | `varchar(50)` | Polymorphic — e.g., `LeaveRequest` |
| `resource_id` | `uuid` | Polymorphic — FK to resource |
| `initiated_by_id` | `uuid` | FK → employees |
| `current_step_order` | `integer` | Which step is active |
| `status` | `varchar(20)` | `in_progress`, `completed`, `cancelled` |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `workflow_definition_id` → [[#`workflow_definitions`|workflow_definitions]], `initiated_by_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## `workflow_step_instances`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `workflow_instance_id` | `uuid` | FK → workflow_instances |
| `workflow_step_id` | `uuid` | FK → workflow_steps |
| `assigned_to_id` | `uuid` | FK → employees (resolved approver) |
| `status` | `varchar(20)` | `pending`, `approved`, `rejected`, `skipped` |
| `started_at` | `timestamptz` |  |
| `completed_at` | `timestamptz` | Nullable |
| `sla_deadline_at` | `timestamptz` | When timeout fires |

**Foreign Keys:** `workflow_instance_id` → [[#`workflow_instances`|workflow_instances]], `workflow_step_id` → [[#`workflow_steps`|workflow_steps]], `assigned_to_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## `workflow_steps`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `workflow_definition_id` | `uuid` | FK → workflow_definitions |
| `step_order` | `integer` | Execution order |
| `step_type` | `varchar(30)` | `approval`, `notification`, `condition` |
| `approver_type` | `varchar(30)` | `reporting_manager`, `department_head`, `role`, `specific_user` |
| `approver_role_id` | `uuid` | FK → roles (nullable — only for role-based steps) |
| `conditions` | `jsonb` | Step conditions (e.g., skip if amount < threshold) |
| `sla_hours` | `integer` | Hours before timeout action |
| `on_timeout_action` | `varchar(30)` | `escalate`, `auto_approve`, `auto_reject` |

**Foreign Keys:** `workflow_definition_id` → [[#`workflow_definitions`|workflow_definitions]], `approver_role_id` → [[database/schemas/auth#`roles`|roles]]

---

## Related

- [[modules/shared-platform/overview|Shared Platform Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]
