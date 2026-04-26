# Shared Platform — Schema

**Module:** [[modules/shared-platform/overview|Shared Platform]]
**Phase:** Phase 1
**Tables:** 33

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
| `provider_type` | `varchar(30)` | `google`, `microsoft`, `saml`, `oidc` |
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

## `subscription_plans`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `name` | `varchar(100)` |  |
| `code` | `varchar(20)` | `starter`, `professional`, `enterprise` |
| `tier` | `varchar(20)` | Ordering tier |
| `feature_limits` | `jsonb` | e.g., `{"max_employees": 50, "modules": ["core_hr","leave"]}` |
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
| `payment_provider_ref` | `varchar(100)` | Stripe subscription ID |
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

## `bridge_api_keys`

API keys issued to external systems (WMS and other integrations) for bridge endpoint authentication. Stored hashed — the raw key is shown once at creation. Scoped to bridge permissions only, cannot access HR data.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | Human label, e.g. "WorkManage Pro" |
| `key_hash` | `varchar(255)` | bcrypt hash of the key |
| `key_prefix` | `varchar(8)` | First 8 chars for display (e.g., `onv_brdg`) |
| `scopes` | `varchar[]` | e.g., `["bridges:read", "bridges:write"]` |
| `last_used_at` | `timestamptz` | Nullable |
| `expires_at` | `timestamptz` | Nullable — null = no expiry |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |
| `revoked_at` | `timestamptz` | Nullable — soft revocation |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `created_by_id` → [[database/schemas/infrastructure#`users`|users]]

**Index:** `(tenant_id, key_prefix)`, `(key_hash)` UNIQUE (for lookup during auth)

---

## `wms_role_mappings`

Maps ONEVO roles to WMS permission sets. Used by the People Sync bridge to push the correct WMS permissions when an employee's role changes. Populated by the tenant admin in Settings → Integrations.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `onevo_role_id` | `uuid` | FK → roles |
| `wms_role_identifier` | `varchar(100)` | The WMS-side role name/ID (defined by WMS team) |
| `wms_permissions_json` | `jsonb` | Which WMS features are enabled for this ONEVO role |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `onevo_role_id` → [[database/schemas/auth#`roles`|roles]]

**Index:** `(tenant_id, onevo_role_id)` UNIQUE

---

## `wms_tenant_links`

Links an ONEVO tenant to a WMS tenant. Created when a customer purchases both products (auto-provisioned) or manually links existing accounts via Settings → Integrations.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants (ONEVO side) |
| `wms_tenant_id` | `varchar(255)` | WMS-assigned tenant identifier |
| `wms_base_url` | `varchar(500)` | WMS API base URL for this tenant |
| `bridge_api_key_id` | `uuid` | FK → bridge_api_keys (the key ONEVO uses to call WMS) |
| `sync_enabled` | `boolean` | Master toggle for all bridge sync |
| `people_sync_enabled` | `boolean` | |
| `availability_sync_enabled` | `boolean` | |
| `work_activity_sync_enabled` | `boolean` | |
| `linked_at` | `timestamptz` | |
| `linked_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `bridge_api_key_id` → [[#`bridge_api_keys`|bridge_api_keys]], `linked_by_id` → [[database/schemas/infrastructure#`users`|users]]

**Index:** `(tenant_id)` UNIQUE — one WMS link per ONEVO tenant

---

## Messaging Tables (MassTransit Outbox + Idempotency)

> These tables are managed by MassTransit and must not be written to directly. They are part of each module's DbContext.

### `shared_platform_outbox_events`

Transactional outbox — written in the same DB transaction as the business write. A background processor reads and forwards to RabbitMQ.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `event_type` | `varchar(200)` | Fully-qualified event class name |
| `payload` | `jsonb` | Serialized IntegrationEvent |
| `created_at` | `timestamptz` | |
| `processed_at` | `timestamptz` | NULL = not yet delivered to RabbitMQ |
| `retry_count` | `integer` | Default 0; max 5 |
| `last_error` | `text` | Last failure message if any |

Index: `WHERE processed_at IS NULL` on `created_at` — the outbox processor queries this.

### `processed_integration_events`

Idempotency table — prevents double-processing if RabbitMQ redelivers a message.

| Column | Type | Notes |
|:-------|:-----|:------|
| `event_id` | `uuid` | PK — same as `IntegrationEvent.EventId` |
| `event_type` | `varchar(200)` | |
| `processed_at` | `timestamptz` | |

---

## Related

- [[modules/shared-platform/overview|Shared Platform Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]