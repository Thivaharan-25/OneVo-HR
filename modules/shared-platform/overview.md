# Module: Shared Platform

**Namespace:** `ONEVO.Modules.SharedPlatform`
**Phase:** 1 — Build
**Pillar:** Shared Foundation
**Owner:** Dev 4 (Week 1 + Week 4)
**Tables:** 30

---

## Purpose

Cross-cutting platform services: SSO provider management, subscription/billing (Stripe), feature flags, and the generic workflow/approval engine used by leave, overtime, expense, document approvals, etc.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/infrastructure/overview\|Infrastructure]] | `ITenantContext` | Multi-tenancy |
| **Consumed by** | [[modules/leave/overview\|Leave]], [[modules/core-hr/overview\|Core Hr]], [[modules/expense/overview\|Expense]] | Workflow engine | Approval routing |
| **Consumed by** | All modules | Feature flags | Feature toggle checks |

---

## Database Tables (30)

### Sub-System 1: SSO & Authentication

#### `sso_providers`

SSO configuration (Google, Microsoft, SAML). Encrypted fields via `IEncryptionService`.

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
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

#### `refresh_tokens`

JWT refresh token tracking with rotation.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `user_id` | `uuid` | FK → users |
| `tenant_id` | `uuid` | FK → tenants |
| `token_hash` | `varchar(255)` | SHA-256 hash (never store raw token) |
| `device_fingerprint` | `varchar(255)` | Browser/device identifier |
| `issued_at` | `timestamptz` | |
| `expires_at` | `timestamptz` | |
| `is_revoked` | `boolean` | |
| `replaced_by_id` | `uuid` | FK → refresh_tokens (rotation chain) |

### Sub-System 2: Subscriptions & Billing (Stripe)

#### `subscription_plans`

Plan definitions. **NOT tenant-scoped** — global catalog.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `name` | `varchar(100)` | |
| `code` | `varchar(20)` | `starter`, `professional`, `enterprise` |
| `tier` | `varchar(20)` | Ordering tier |
| `feature_limits` | `jsonb` | e.g., `{"max_employees": 50, "modules": ["core_hr","leave"]}` |
| `monthly_price` | `decimal(10,2)` | |
| `annual_price` | `decimal(10,2)` | |
| `currency` | `varchar(3)` | ISO 4217 |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

#### `plan_features`

Features included per subscription plan. Not in HTML ERD — to be added.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `plan_id` | `uuid` | FK → subscription_plans |
| `feature_key` | `varchar(100)` | e.g., `payroll`, `activity_monitoring` |
| `limit_value` | `integer` | Nullable — null means unlimited |
| `is_included` | `boolean` | |

#### `tenant_subscriptions`

Active subscription per tenant.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `plan_id` | `uuid` | FK → subscription_plans |
| `billing_cycle` | `varchar(20)` | `monthly`, `annual` |
| `status` | `varchar(20)` | `active`, `past_due`, `cancelled`, `trialing` |
| `current_period_start` | `date` | |
| `current_period_end` | `date` | |
| `payment_provider_ref` | `varchar(100)` | Stripe subscription ID |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

#### `subscription_invoices`

Invoice records synced from Stripe. Not in HTML ERD — to be added.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `subscription_id` | `uuid` | FK → tenant_subscriptions |
| `invoice_number` | `varchar(50)` | |
| `amount` | `decimal(10,2)` | |
| `currency` | `varchar(3)` | |
| `status` | `varchar(20)` | `draft`, `open`, `paid`, `void` |
| `payment_provider_ref` | `varchar(100)` | Stripe invoice ID |
| `issued_at` | `timestamptz` | |
| `paid_at` | `timestamptz` | Nullable |

#### `payment_methods`

Stored payment methods for a tenant. Not in HTML ERD — to be added.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `type` | `varchar(20)` | `card`, `bank_transfer` |
| `last_four` | `varchar(4)` | Last 4 digits |
| `brand` | `varchar(20)` | `visa`, `mastercard`, etc. |
| `expiry_month` | `integer` | |
| `expiry_year` | `integer` | |
| `is_default` | `boolean` | |
| `payment_provider_ref` | `varchar(100)` | Stripe payment method ID |
| `created_at` | `timestamptz` | |

### Sub-System 3: Feature Flags

#### `feature_flags`

Feature flag definitions per tenant.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `flag_key` | `varchar(100)` | Unique per tenant |
| `is_enabled` | `boolean` | |
| `conditions` | `jsonb` | Targeting rules (e.g., percentage rollout, user segment) |
| `toggled_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

#### `tenant_feature_flags`

Per-tenant overrides for global feature flags. Not in HTML ERD — to be added.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `flag_key` | `varchar(100)` | |
| `is_enabled` | `boolean` | Override value |
| `overridden_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |

> **Note:** `feature_flags` in HTML ERD is tenant-scoped (has `tenant_id`). `tenant_feature_flags` allows a separate override layer if global flags are added later.

### Sub-System 4: Tenant Branding & Configuration

#### `tenant_branding`

Custom branding per tenant (logo, colors, domain).

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
| `updated_at` | `timestamptz` | |

#### `user_preferences`

Per-user UI/notification preferences.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `user_id` | `uuid` | FK → users |
| `tenant_id` | `uuid` | FK → tenants |
| `preference_key` | `varchar(100)` | e.g., `theme`, `locale`, `timezone` |
| `preference_value` | `jsonb` | |
| `updated_at` | `timestamptz` | |

### Sub-System 5: Notification Infrastructure

#### `notification_templates`

Templates per channel + locale for rendering notifications.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `template_code` | `varchar(50)` | e.g., `leave_requested`, `payroll_completed` |
| `channel` | `varchar(20)` | `email`, `push`, `in_app` |
| `subject_template` | `text` | For email subject line |
| `body_template` | `text` | Handlebars/Liquid template |
| `locale` | `varchar(10)` | e.g., `en`, `si`, `ta` |
| `version` | `integer` | |
| `is_active` | `boolean` | |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

#### `notification_channels`

Channel provider configuration per tenant.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `channel_type` | `varchar(30)` | `email`, `push`, `slack` |
| `provider` | `varchar(50)` | `resend`, `fcm`, `slack_webhook` |
| `credentials_encrypted` | `jsonb` | Encrypted API keys/tokens |
| `is_active` | `boolean` | |
| `configured_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

#### `escalation_rules`

SLA-based escalation triggers. Checked by Hangfire recurring job (hourly).

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
| `is_active` | `boolean` | |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |

### Sub-System 6: Workflow Engine (Generic)

The workflow engine is **resource-type agnostic** — it works via `resource_type` + `resource_id` polymorphic references. Same engine handles leave, overtime, document, expense approvals.

**How it works:**
1. Module creates a workflow instance: `resource_type = "LeaveRequest"`, `resource_id = {leaveRequestId}`
2. Engine resolves approvers based on step definition (reporting manager, department head, etc.)
3. Approver takes action → engine advances to next step or completes
4. Module receives `WorkflowCompleted` event with outcome

#### `workflow_definitions`

Workflow templates (e.g., "Leave Approval", "Expense Approval").

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | |
| `code` | `varchar(50)` | Unique identifier |
| `resource_type` | `varchar(50)` | e.g., `LeaveRequest`, `ExpenseClaim` |
| `description` | `text` | |
| `is_active` | `boolean` | |
| `version` | `integer` | Versioning for definition changes |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

#### `workflow_steps`

Steps within a workflow definition.

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

#### `workflow_instances`

Active workflow instance for a specific resource.

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
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

#### `workflow_step_instances`

Current step state for an active workflow instance. Not in HTML ERD — to be added.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `workflow_instance_id` | `uuid` | FK → workflow_instances |
| `workflow_step_id` | `uuid` | FK → workflow_steps |
| `assigned_to_id` | `uuid` | FK → employees (resolved approver) |
| `status` | `varchar(20)` | `pending`, `approved`, `rejected`, `skipped` |
| `started_at` | `timestamptz` | |
| `completed_at` | `timestamptz` | Nullable |
| `sla_deadline_at` | `timestamptz` | When timeout fires |

#### `approval_actions`

Individual approval/rejection action records.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `workflow_instance_id` | `uuid` | FK → workflow_instances |
| `workflow_step_id` | `uuid` | FK → workflow_steps |
| `actor_id` | `uuid` | FK → employees |
| `action` | `varchar(20)` | `approve`, `reject`, `delegate`, `request_info` |
| `comment` | `text` | Nullable |
| `acted_at` | `timestamptz` | |
| `delegated_to_id` | `uuid` | FK → employees (nullable — only for delegate action) |

### Sub-System 7: Compliance & Data Governance

#### `legal_holds`

Prevents data deletion for legal/compliance reasons.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `resource_type` | `varchar(50)` | Polymorphic |
| `resource_id` | `uuid` | Polymorphic |
| `reason` | `text` | |
| `placed_by_id` | `uuid` | FK → users |
| `placed_at` | `timestamptz` | |
| `released_by_id` | `uuid` | FK → users (nullable) |
| `released_at` | `timestamptz` | Nullable |

#### `retention_policies`

Data retention rules per resource type.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `resource_type` | `varchar(50)` | |
| `retention_days` | `integer` | |
| `action_on_expiry` | `varchar(30)` | `delete`, `anonymize`, `archive` |
| `compliance_framework` | `varchar(50)` | e.g., `GDPR`, `local_labor_law` |
| `is_active` | `boolean` | |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |

#### `compliance_exports`

GDPR subject access requests and data exports.

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
| `requested_at` | `timestamptz` | |
| `completed_at` | `timestamptz` | Nullable |

### Sub-System 8: Hardware & Devices

#### `hardware_terminals`

Physical terminals (biometric scanners, kiosks) connected via webhooks.

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
| `last_heartbeat_at` | `timestamptz` | |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

### Sub-System 9: Real-Time & Integrations

#### `signalr_connections`

Active SignalR connections for real-time push (in-app notifications, live updates).

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `user_id` | `uuid` | FK → users |
| `tenant_id` | `uuid` | FK → tenants |
| `connection_id` | `varchar(100)` | SignalR connection ID |
| `channel` | `varchar(30)` | `web`, `mobile`, `desktop_agent` |
| `device_type` | `varchar(30)` | `browser`, `ios`, `android`, `windows` |
| `connected_at` | `timestamptz` | |
| `last_ping_at` | `timestamptz` | |
| `is_active` | `boolean` | |

> **Note:** Renamed from `presence_sessions` to avoid collision with workforce_presence `presence_sessions` (table 127).

#### `system_settings`

Global system configuration. Not in HTML ERD — to be added.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `setting_key` | `varchar(100)` | Unique |
| `setting_value` | `jsonb` | |
| `description` | `text` | |
| `updated_by_id` | `uuid` | FK → users |
| `updated_at` | `timestamptz` | |

> **Note:** NOT tenant-scoped — global system settings. Tenant-specific settings use `tenant_settings` in the Configuration module.

#### `api_keys`

Tenant API keys for external integrations. Not in HTML ERD — to be added.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | Friendly name |
| `key_hash` | `varchar(255)` | SHA-256 hash (never store raw) |
| `key_prefix` | `varchar(10)` | First 8 chars for identification |
| `scopes` | `jsonb` | Permitted API scopes |
| `expires_at` | `timestamptz` | Nullable |
| `is_active` | `boolean` | |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |
| `last_used_at` | `timestamptz` | Nullable |

#### `webhook_endpoints`

Registered webhook URLs for outbound events. Not in HTML ERD — to be added.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `url` | `varchar(500)` | Target URL |
| `secret_hash` | `varchar(255)` | HMAC signing secret hash |
| `events` | `jsonb` | Subscribed event types |
| `is_active` | `boolean` | |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |

#### `webhook_deliveries`

Delivery log for webhook attempts. Not in HTML ERD — to be added.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `webhook_endpoint_id` | `uuid` | FK → webhook_endpoints |
| `event_type` | `varchar(50)` | |
| `payload` | `jsonb` | Sent payload |
| `response_status` | `integer` | HTTP status code |
| `response_body` | `text` | Truncated response |
| `attempt_number` | `integer` | Retry count |
| `delivered_at` | `timestamptz` | |

#### `rate_limit_rules`

Per-endpoint rate limit configuration. Not in HTML ERD — to be added.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants (nullable — null for global rules) |
| `endpoint_pattern` | `varchar(200)` | e.g., `/api/v1/leave/*` |
| `max_requests` | `integer` | Per window |
| `window_seconds` | `integer` | Sliding window size |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |

#### `scheduled_tasks`

Hangfire job metadata for visibility/management. Not in HTML ERD — to be added.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants (nullable — null for system tasks) |
| `task_type` | `varchar(100)` | Job class name |
| `cron_expression` | `varchar(50)` | |
| `description` | `text` | |
| `is_active` | `boolean` | |
| `last_run_at` | `timestamptz` | Nullable |
| `next_run_at` | `timestamptz` | |
| `created_at` | `timestamptz` | |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/sso/providers` | `settings:admin` | List SSO providers |
| POST | `/api/v1/sso/providers` | `settings:admin` | Configure SSO |
| GET | `/api/v1/subscriptions/current` | `billing:read` | Current subscription |
| POST | `/api/v1/subscriptions/upgrade` | `billing:manage` | Upgrade plan |
| GET | `/api/v1/feature-flags` | Authenticated | Active feature flags |
| GET | `/api/v1/workflows/{resourceType}/{resourceId}` | Authenticated | Workflow status |
| POST | `/api/v1/workflows/{instanceId}/approve` | Authenticated | Approve step |
| POST | `/api/v1/workflows/{instanceId}/reject` | Authenticated | Reject step |

## Features

- [[modules/shared-platform/sso-authentication/overview|Sso Authentication]] — SSO provider configuration (Google, Microsoft, SAML, OIDC) with auto-provisioning
- [[modules/shared-platform/subscriptions-billing/overview|Subscriptions Billing]] — Stripe-backed subscription plans, invoices, and payment methods
- [[frontend/cross-cutting/feature-flags|Feature Flags]] — Per-tenant feature flag definitions with targeting conditions
- [[frontend/design-system/theming/tenant-branding|Tenant Branding]] — Custom domain, logo, and brand colors per tenant
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]] — Generic approval engine for leave, expense, overtime, document workflows
- [[modules/shared-platform/compliance-governance/overview|Compliance Governance]] — Legal holds, retention policies, GDPR subject access exports
- [[modules/shared-platform/hardware-terminals/overview|Hardware Terminals]] — Physical biometric/RFID/kiosk terminal management
- [[modules/shared-platform/real-time-integrations/overview|Real Time Integrations]] — SignalR connections, API keys, webhooks, rate limits
- [[modules/shared-platform/notification-infrastructure/overview|Notification Infrastructure]] — Notification templates and channel provider configuration
- Overview Dashboard — Frontend: [[modules/shared-platform/overview-dashboard/frontend|Frontend]]
- Self Service — Frontend: [[modules/shared-platform/self-service/frontend|Frontend]]

---

## Related

- [[security/auth-architecture|Auth Architecture]] — SSO provider tokens and refresh token rotation
- [[infrastructure/multi-tenancy|Multi Tenancy]] — Subscription plans are global; all other data is tenant-scoped
- [[security/compliance|Compliance]] — Legal holds prevent data deletion; compliance exports for GDPR
- [[security/data-classification|Data Classification]] — SSO client secrets and API keys encrypted via `IEncryptionService`
- [[backend/messaging/event-catalog|Event Catalog]] — Workflow events: approval/rejection drive module state transitions
- [[backend/messaging/error-handling|Error Handling]] — SLA-based escalation rules with auto-approve/reject timeouts
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]] — Implementation task file

See also: [[backend/module-catalog|Module Catalog]], [[modules/infrastructure/overview|Infrastructure]], [[modules/auth/overview|Auth]], [[backend/external-integrations|External Integrations]]
