# Shared Platform - Schema

**Module:** [[modules/shared-platform/overview|Shared Platform]]
**Phase:** Phase 1, including optional Microsoft Teams integration additions
**Tables:** 36

---

## `api_keys`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `name` | `varchar(100)` | Friendly name |
| `key_hash` | `varchar(255)` | SHA-256 hash (never store raw) |
| `key_prefix` | `varchar(10)` | First 8 chars for identification |
| `scopes` | `jsonb` | Permitted API scopes |
| `expires_at` | `timestamptz` | Nullable |
| `is_active` | `boolean` |  |
| `created_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` |  |
| `last_used_at` | `timestamptz` | Nullable |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `created_by_id` -> [[database/schemas/infrastructure#`users`|users]]

---

## `approval_actions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `workflow_instance_id` | `uuid` | FK -> workflow_instances |
| `workflow_step_id` | `uuid` | FK -> workflow_steps |
| `actor_id` | `uuid` | FK -> employees |
| `action` | `varchar(20)` | `approve`, `reject`, `delegate`, `request_info` |
| `comment` | `text` | Nullable |
| `acted_at` | `timestamptz` |  |
| `workflow_step_assignment_id` | `uuid` | FK -> workflow_step_assignments; nullable for legacy actions |
| `action_metadata` | `jsonb` | Optional action-card or resolver metadata |
| `delegated_to_id` | `uuid` | FK -> employees (nullable - only for delegate action) |

**Foreign Keys:** `workflow_instance_id` -> [[#`workflow_instances`|workflow_instances]], `workflow_step_id` -> [[#`workflow_steps`|workflow_steps]], `actor_id` -> [[database/schemas/core-hr#`employees`|employees]], `delegated_to_id` -> [[database/schemas/core-hr#`employees`|employees]], `workflow_step_assignment_id` -> [[#`workflow_step_assignments`|workflow_step_assignments]]

---

## `compliance_exports`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `requested_by_id` | `uuid` | FK -> users |
| `export_type` | `varchar(30)` | `subject_access`, `data_portability`, `erasure` |
| `scope` | `varchar(30)` | `full`, `partial` |
| `target_user_id` | `uuid` | FK -> users (whose data) |
| `status` | `varchar(20)` | `pending`, `processing`, `completed`, `failed` |
| `file_url` | `varchar(500)` | Download URL when completed |
| `requested_at` | `timestamptz` |  |
| `completed_at` | `timestamptz` | Nullable |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `requested_by_id` -> [[database/schemas/infrastructure#`users`|users]], `target_user_id` -> [[database/schemas/infrastructure#`users`|users]]

---

## `escalation_rules`

> **Scope:** Workflow SLA timeouts - fires when a workflow item (leave request, expense claim, etc.) sits in a pending state longer than `sla_hours`. See [[database/schemas/exception-engine#`escalation_chains`|escalation_chains]] for alert routing on system-detected anomalies - that is a separate system.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `resource_type` | `varchar(50)` | e.g., `leave_request`, `expense_claim` |
| `trigger_condition` | `varchar(100)` | e.g., `status = 'pending'` |
| `sla_hours` | `integer` | Hours before escalation fires |
| `action_type` | `varchar(30)` | `remind`, `escalate`, `auto_approve` |
| `escalate_to_role_id` | `uuid` | FK -> roles (nullable) |
| `notification_template_id` | `uuid` | FK -> notification_templates |
| `is_active` | `boolean` |  |
| `created_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `escalate_to_role_id` -> [[database/schemas/auth#`roles`|roles]], `notification_template_id` -> [[#`notification_templates`|notification_templates]], `created_by_id` -> [[database/schemas/infrastructure#`users`|users]]

---

## `global_app_catalog`

Global catalog of known applications managed by the OneVo dev team via the developer platform. No `tenant_id` - shared across all tenants. HR admins browse this when configuring app allowlists.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `app_name` | `varchar(200)` | e.g., "Google Chrome" |
| `process_name` | `varchar(100)` | e.g., "chrome.exe" - authoritative matching key used by ingest processor |
| `category` | `varchar(50)` | `browser`, `communication`, `development`, `office`, `design`, `productivity`, `other` |
| `publisher` | `varchar(200)` | e.g., "Google LLC" |
| `icon_url` | `varchar(500)` | App icon for HR admin UI display |
| `is_public` | `boolean` | True = visible to all HR admins in catalog browser |
| `is_productive_default` | `boolean` | Default productivity classification applied when no tenant override exists |
| `created_by_id` | `uuid` | FK -> platform_users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Foreign Keys:** `created_by_id` -> `platform_users`

**Index:** `process_name` UNIQUE - no duplicate process names in catalog.

> Managed via `/admin/v1/app-catalog/*` endpoints in the developer platform. See [[docs/superpowers/plans/2026-04-26-app-catalog-observed-applications|App Catalog Plan]] and [[database/schemas/configuration#`observed_applications`|observed_applications]] for the per-tenant discovery table.

---

## `feature_flags`

| Column | Type | Notes |
|:-------|:-----|:------|
| `key` | `varchar(120)` | PK; machine-readable flag key |
| `description` | `text` | Nullable |
| `default_value` | `boolean` | Global default value |
| `rollout_percentage` | `int` | 0-100 deterministic tenant rollout percentage |
| `module_key` | `varchar(80)` | Nullable FK -> module_catalog(module_key) |
| `feature_key` | `varchar(120)` | Nullable FK -> module_features(feature_key); commercial feature controlled at runtime |
| `is_active` | `boolean` | Soft-deactivate flag without deleting history |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

Global feature flag definitions. Tenant-specific exceptions are stored in `feature_flag_overrides`.

**Linkage rule:** Tenant-facing product feature flags must set both `module_key` and `feature_key`, and `feature_key` must reference a feature owned by that module in `module_features`. Only platform operational flags that are not sold as tenant features may leave `module_key` and `feature_key` null.

---

## `hardware_terminals`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `office_location_id` | `uuid` | FK -> office_locations |
| `terminal_code` | `varchar(50)` | Unique device code |
| `terminal_type` | `varchar(30)` | `biometric`, `rfid`, `kiosk` |
| `webhook_url` | `varchar(500)` | Callback URL for events |
| `api_key_encrypted` | `bytea` | Encrypted terminal API key |
| `status` | `varchar(20)` | `active`, `offline`, `maintenance` |
| `last_heartbeat_at` | `timestamptz` |  |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `office_location_id` -> [[database/schemas/org-structure#`office_locations`|office_locations]]

---

## `legal_holds`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `resource_type` | `varchar(50)` | Polymorphic |
| `resource_id` | `uuid` | Polymorphic |
| `reason` | `text` |  |
| `placed_by_id` | `uuid` | FK -> users |
| `placed_at` | `timestamptz` |  |
| `released_by_id` | `uuid` | FK -> users (nullable) |
| `released_at` | `timestamptz` | Nullable |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `placed_by_id` -> [[database/schemas/infrastructure#`users`|users]], `released_by_id` -> [[database/schemas/infrastructure#`users`|users]]

---

## `notification_channels`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `channel_type` | `varchar(30)` | `email`, `push`, `slack` |
| `provider` | `varchar(50)` | `resend`, `fcm`, `slack_webhook` |
| `credentials_encrypted` | `jsonb` | Encrypted API keys/tokens |
| `is_active` | `boolean` |  |
| `configured_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `configured_by_id` -> [[database/schemas/infrastructure#`users`|users]]

---

## `notification_templates`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `template_code` | `varchar(50)` | e.g., `leave_requested`, `payroll_completed` |
| `channel` | `varchar(20)` | `email`, `push`, `in_app` |
| `subject_template` | `text` | For email subject line |
| `body_template` | `text` | Handlebars/Liquid template |
| `locale` | `varchar(10)` | e.g., `en`, `si`, `ta` |
| `version` | `integer` |  |
| `is_active` | `boolean` |  |
| `created_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `created_by_id` -> [[database/schemas/infrastructure#`users`|users]]

---

## `payment_methods`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `type` | `varchar(20)` | `card`, `bank_transfer` |
| `last_four` | `varchar(4)` | Last 4 digits |
| `brand` | `varchar(20)` | `visa`, `mastercard`, etc. |
| `expiry_month` | `integer` |  |
| `expiry_year` | `integer` |  |
| `is_default` | `boolean` |  |
| `payment_provider_ref` | `varchar(100)` | Gateway payment method ID from Stripe, Paddle, or PayHere |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `payment_gateway_configs`

Gateway configuration for Stripe, Paddle, and PayHere. Supports platform-managed gateway configs only. Secrets are encrypted through `IEncryptionService`; admin APIs return safe metadata only. Country assignment is stored in `payment_gateway_country_routes`, not as free-form gateway selection by tenants.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `provider` | `varchar(30)` | `stripe`, `paddle`, `payhere` |
| `environment` | `varchar(20)` | `sandbox`, `production` |
| `display_name` | `varchar(100)` | Friendly operator label |
| `public_key` | `varchar(255)` | Nullable; Stripe/Paddle public identifier or equivalent public key where applicable |
| `merchant_id` | `varchar(100)` | Nullable; Paddle seller ID or PayHere merchant ID |
| `secret_encrypted` | `bytea` | Encrypted Stripe secret key, Paddle API key, or PayHere merchant secret |
| `webhook_secret_encrypted` | `bytea` | Encrypted Stripe/Paddle webhook secret or PayHere notify/hash secret when separate |
| `webhook_url` | `varchar(500)` | Gateway callback/notify URL |
| `is_default` | `boolean` | Default gateway for tenant/platform |
| `is_active` | `boolean` | Whether this config can be used for payment collection |
| `created_by_id` | `uuid` | FK -> users or dev platform account boundary |
| `created_at` | `timestamptz` | |

---

## `payment_gateway_country_routes`

Country-to-gateway routing for subscription and invoice collection. Operators select country names in System Config; backend stores ISO country codes.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `country_code` | `varchar(2)` | ISO 3166-1 alpha-2 |
| `country_name_snapshot` | `varchar(120)` | Display snapshot for audit/readability |
| `gateway_config_id` | `uuid` | FK -> payment_gateway_configs |
| `environment` | `varchar(20)` | `sandbox`, `production` |
| `is_active` | `boolean` | Whether this route can be used |
| `created_by_id` | `uuid` | FK -> users or dev platform account boundary |
| `created_at` | `timestamptz` | |

**Rule:** one active route per `country_code + environment`. A single gateway config may have many country route rows.
| `updated_at` | `timestamptz` | |

**Rule:** Subscription and invoice collection must reference a configured payment provider when payment-provider collection is enabled.

---

## `plan_features`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `plan_id` | `uuid` | FK -> subscription_plans |
| `feature_key` | `varchar(100)` | e.g., `payroll`, `activity_monitoring` |
| `limit_value` | `integer` | Nullable - null means unlimited |
| `is_included` | `boolean` |  |

**Foreign Keys:** `plan_id` -> [[#`subscription_plans`|subscription_plans]]

---

## `module_catalog`

Global catalog for actual ONEVO modules. No tenant access should be inferred from this table alone; it provides module metadata and reference values for Subscription Plans.

| Column | Type | Notes |
|:-------|:-----|:------|
| `module_key` | `varchar(100)` | PK; e.g., `core_hr`, `leave`, `work_management` |
| `name` | `varchar(150)` | Display name |
| `pillar` | `varchar(50)` | Product grouping only |
| `phase` | `varchar(30)` | `phase_1`, `phase_2`, `future`, or product-defined release phase |
| `pricing_reference` | `jsonb` | Company-size pricing reference only |
| `storage_reference` | `jsonb` | Company-size storage reference only |
| `ai_token_reference` | `jsonb` | Company-size AI token reference only |
| `pricing_unit` | `varchar(30)` | `per_employee`, `per_user`, `flat`, `custom` |
| `is_ai_enabled` | `boolean` | True when AI token references are relevant |
| `is_storage_consuming` | `boolean` | True when storage references are relevant |
| `is_active` | `boolean` | Whether the module can be selected for new plans |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Reference rule:** Module Catalog references help operators build plans. Subscription Plans owns base/add-on/resource composition and live billing. Existing tenant subscriptions do not automatically change when catalog references change.

**Permission ownership rule:** permission ownership is stored in `module_permission_ownership`, not directly on `module_catalog`. A permission code can be owned by only one module catalog item. The Developer Platform must show the owning module beside each permission and reject attempts to assign a permission to a second module unless it is first removed from the original module through an explicit catalog update.

---
## `module_features`

Commercial feature registry inside a module. These are plan/custom-contract packaging units, not runtime rollout flags.

| Column | Type | Notes |
|:-------|:-----|:------|
| `feature_key` | `varchar(120)` | PK; format `{module_key}.{feature_name}` |
| `module_key` | `varchar(100)` | FK -> module_catalog.module_key |
| `name` | `varchar(150)` | Display name |
| `description` | `text` | Nullable |
| `is_default_included` | `boolean` | Selected by default when the module is added to a plan |
| `is_active` | `boolean` | Whether this feature can be selected for new plans/contracts |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

---

## `module_permission_ownership`

Exclusive ownership map between product modules and seeded tenant-facing permission codes. Permission namespaces do not need to match module keys; for example, `core_hr` may own `employees:read`.

| Column | Type | Notes |
|:-------|:-----|:------|
| `module_key` | `varchar(100)` | FK -> module_catalog.module_key |
| `permission_code` | `varchar(120)` | FK -> permissions/code catalog |
| `is_default_permission` | `boolean` | Included in future tenant Owner role materialization |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Primary key:** `(module_key, permission_code)`

**Unique constraint:** `(permission_code)` - one permission can be owned by only one module.

**Rule:** Permission codes are seeded/version-controlled by the backend permission catalog. Module Catalog assigns ownership of existing permission codes; it does not create or rename permission codes.

---

## `tenant_module_entitlements`

Tenant-level module entitlement records derived from the active subscription plan and selected optional module add-ons. Resource-only add-ons do not create rows here.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `module_key` | `varchar(100)` | FK -> module_catalog.module_key |
| `sales_state` | `varchar(30)` | `subscription_included`, `purchased`, `quoted`, `available`, or `disabled` |
| `runtime_override` | `boolean` | Nullable runtime-only override; `NULL` inherits commercial entitlement, `false` force-disables runtime access, `true` explicitly restores runtime access without bypassing commercial entitlement |
| `pricing_model` | `varchar(30)` | `subscription`, `addon`, or `custom` |
| `price` | `decimal(12,2)` | Nullable override price |
| `currency` | `varchar(3)` | ISO 4217 |
| `starts_at` | `date` | Nullable entitlement start |
| `ends_at` | `date` | Nullable entitlement/subscription end |
| `created_by_id` | `uuid` | FK -> users or platform_users, depending on implementation boundary |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Entitlement rule:** Commercially entitled modules = selected plan base modules + selected optional module add-ons - disabled modules. `available` and `quoted` are commercial pipeline states and do not grant tenant-facing access. Runtime module access requires commercial entitlement and `runtime_override IS DISTINCT FROM false`.

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
| `old_pricing_reference` | `jsonb` | Nullable previous company-size pricing references |
| `new_pricing_reference` | `jsonb` | Nullable new company-size pricing references |
| `old_storage_reference` | `jsonb` | Nullable previous storage references |
| `new_storage_reference` | `jsonb` | Nullable new storage references |
| `old_ai_token_reference` | `jsonb` | Nullable previous AI token references |
| `new_ai_token_reference` | `jsonb` | Nullable new AI token references |
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
| `current_step` | `varchar(50)` | `tenant_profile`, `subscription`, `modules`, `roles`, `setup_services`, `settings`, `owner_invite`, `review` |
| `tenant_details_completed_at` | `timestamptz` | Nullable |
| `subscription_completed_at` | `timestamptz` | Nullable |
| `modules_completed_at` | `timestamptz` | Nullable |
| `roles_completed_at` | `timestamptz` | Nullable |
| `setup_services_completed_at` | `timestamptz` | Nullable |
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

The schema supports the corrected subscription model requested by product:

- `tenant_subscriptions` records one selected plan, billing cycle, selected optional module add-ons, selected resource-only add-ons, confirmed employee count, and invoice/payment state.
- `tenant_module_entitlements.sales_state` records module state: `available`, `purchased`, `quoted`, `subscription_included`, or `disabled`.
- Module Catalog reference values do not automatically change existing tenant subscriptions.
- Subscription plan pricing is calculated from the selected base plan, selected optional module add-ons, selected resource-only add-ons, and company-size pricing tiers.
- Tenant owner confirmed total employee count selects the first invoice pricing tier.
- Store operator overrides separately from calculated prices.
- Shared storage and shared AI allowances are resolved into tenant resource limits.
- Unpaid seat dues block cancellation and renewal changes.

Pricing and module entitlement decide what the tenant has access to. RBAC permissions decide which users inside that tenant can use the entitled capabilities.

---

## `setup_services`

Reusable Developer Platform setup services. Every setup service is connected to one or more module keys so the tenant's selected subscription/modules determine which services can be applied. A service can be free/global or paid, but it is still resolved through module entitlement.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `service_key` | `varchar(100)` | Unique service key |
| `name` | `varchar(150)` | Display name |
| `description` | `text` | Nullable |
| `module_keys_json` | `jsonb` | One or more `module_catalog.module_key` values this setup service applies to |
| `applies_to_all_entitled_modules` | `boolean` | True for free/global services that should be auto-added for every matching entitled module |
| `is_free` | `boolean` | True when ONEVO provides this service without setup billing |
| `price` | `decimal(12,2)` | Nullable service price when paid |
| `currency` | `varchar(3)` | Nullable ISO 4217 |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Rules:**

- A setup service can be selected or auto-added for a tenant only when at least one linked module key is in the tenant's entitled module set.
- Free/global setup services are auto-added for matching entitled modules with `is_billable = false`; operators can still configure them during tenant setup.
- Paid setup services are explicitly selected by the operator and tracked against the linked entitled module.

---

## `tenant_setup_services`

Tenant-specific service setup checklist and charge state.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `setup_service_id` | `uuid` | FK -> setup_services |
| `module_key` | `varchar(100)` | Entitled module that caused or allowed this setup service |
| `status` | `varchar(30)` | `needed`, `in_progress`, `configured`, `waived`, `cancelled` |
| `is_billable` | `boolean` | Snapshot from service and tenant agreement |
| `price` | `decimal(12,2)` | Nullable tenant-specific setup price |
| `selected_by_id` | `uuid` | FK -> users or dev platform account boundary |
| `configured_by_id` | `uuid` | Nullable FK -> users or dev platform account boundary |
| `configured_at` | `timestamptz` | Nullable |
| `notes` | `text` | Nullable |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

---

## `configuration_templates`

Reusable setup templates managed in the Developer Platform -> Configuration Template Manager. Platform operators create and version these globally; applying a template to a tenant seeds the corresponding module tables without mutating the global template.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `template_key` | `varchar(100)` | Unique machine-readable key, e.g. `uk-standard-leave`, `engineering-positions` |
| `template_type` | `varchar(50)` | `configuration`, `org_structure`, `leave_policy`, `onboarding`, `app_allowlist`, `monitoring_policy`, `data_import_mapping` |
| `name` | `varchar(150)` | Display name |
| `description` | `varchar(500)` | Nullable - human-readable summary shown in the template picker |
| `version` | `integer` | Incremented on every edit; applied version is snapshotted in `tenant_configuration_template_applications` |
| `module_keys_json` | `jsonb` | Module keys that must be entitled on the tenant before apply is allowed |
| `industry_profile_tag` | `varchar(50)` | Nullable - links monitoring policy templates to an industry for auto-selection during provisioning |
| `payload_json` | `jsonb` | Type-specific template content - schema defined per `template_type` in the Configuration Template Manager end-to-end-logic doc |
| `is_system` | `boolean` | `true` = ONEVO-managed default; system templates cannot be edited, only cloned |
| `is_active` | `boolean` | Inactive templates cannot be applied |
| `created_by_id` | `uuid` | FK -> platform_users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Note on role templates:** Role templates are managed separately via the Role Template Manager module and stored in `role_templates`, not here. Org structure templates may create departments and positions, but they must not auto-assign security roles.

**Foreign Keys:** `created_by_id` -> [[developer-platform/database/schema#platform_users|platform_users]]

---

## `tenant_configuration_template_applications`

Audit record of every template application to a tenant. One row per apply action - reapplying creates a new row, not an update.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `configuration_template_id` | `uuid` | FK -> configuration_templates |
| `template_type` | `varchar(50)` | Snapshot of the template type at apply time |
| `applied_version` | `integer` | Template version that was applied |
| `applied_payload_json` | `jsonb` | Snapshot of the payload that was applied - immutable after creation |
| `custom_payload_json` | `jsonb` | Nullable - tenant-specific overrides made after application; does not mutate the global template |
| `warnings_json` | `jsonb` | Array of warning strings returned at apply time, e.g. unresolved job level rank references |
| `status` | `varchar(20)` | `applied` -> `customized` (if tenant edited) -> `superseded` (if reapplied) -> `removed` |
| `applied_by_id` | `uuid` | FK -> platform_users |
| `applied_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | Nullable - set when status changes or custom payload is edited |

**Rule:** Applying a template creates tenant-specific configuration; the global template record is never mutated. Editing the tenant copy sets `status = customized`. Reapplying the same template sets the previous application row to `superseded` and creates a new `applied` row.

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#tenants|tenants]], `configuration_template_id` -> [[#configuration_templates|configuration_templates]], `applied_by_id` -> [[developer-platform/database/schema#platform_users|platform_users]]

Catalog price changes do not silently update existing tenant commercial records. Existing tenant subscriptions and module entitlements keep their stored negotiated prices unless ONEVO runs an explicit reviewed reprice/migration process.

---

## `rate_limit_rules`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants (nullable - null for global rules) |
| `endpoint_pattern` | `varchar(200)` | e.g., `/api/v1/leave/*` |
| `max_requests` | `integer` | Per window |
| `window_seconds` | `integer` | Sliding window size |
| `is_active` | `boolean` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `refresh_tokens`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `user_id` | `uuid` | FK -> users |
| `tenant_id` | `uuid` | FK -> tenants |
| `token_hash` | `varchar(255)` | SHA-256 hash (never store raw token) |
| `device_fingerprint` | `varchar(255)` | Browser/device identifier |
| `issued_at` | `timestamptz` |  |
| `expires_at` | `timestamptz` |  |
| `is_revoked` | `boolean` |  |
| `replaced_by_id` | `uuid` | FK -> refresh_tokens (rotation chain) |

**Foreign Keys:** `user_id` -> [[database/schemas/infrastructure#`users`|users]], `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `replaced_by_id` -> [[#`refresh_tokens`|refresh_tokens]]

---

## `retention_policies`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `resource_type` | `varchar(50)` |  |
| `retention_days` | `integer` |  |
| `action_on_expiry` | `varchar(30)` | `delete`, `anonymize`, `archive` |
| `compliance_framework` | `varchar(50)` | e.g., `GDPR`, `local_labor_law` |
| `is_active` | `boolean` |  |
| `created_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `created_by_id` -> [[database/schemas/infrastructure#`users`|users]]

---

## `scheduled_tasks`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants (nullable - null for system tasks) |
| `task_type` | `varchar(100)` | Job class name |
| `cron_expression` | `varchar(50)` |  |
| `description` | `text` |  |
| `is_active` | `boolean` |  |
| `last_run_at` | `timestamptz` | Nullable |
| `next_run_at` | `timestamptz` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `signalr_connections`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `user_id` | `uuid` | FK -> users |
| `tenant_id` | `uuid` | FK -> tenants |
| `connection_id` | `varchar(100)` | SignalR connection ID |
| `channel` | `varchar(30)` | `web`, `mobile`, `desktop_agent` |
| `device_type` | `varchar(30)` | `browser`, `ios`, `android`, `windows` |
| `connected_at` | `timestamptz` |  |
| `last_ping_at` | `timestamptz` |  |
| `is_active` | `boolean` |  |

**Foreign Keys:** `user_id` -> [[database/schemas/infrastructure#`users`|users]], `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `sso_providers`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
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

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]]

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
| `tenant_id` | `uuid` | FK -> tenants |
| `subscription_id` | `uuid` | FK -> tenant_subscriptions |
| `invoice_number` | `varchar(50)` |  |
| `amount` | `decimal(10,2)` |  |
| `currency` | `varchar(3)` |  |
| `status` | `varchar(20)` | `draft`, `open`, `paid`, `void` |
| `payment_provider_ref` | `varchar(100)` | Stripe invoice ID |
| `issued_at` | `timestamptz` |  |
| `paid_at` | `timestamptz` | Nullable |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `subscription_id` -> [[#`tenant_subscriptions`|tenant_subscriptions]]

---

## `billing_snapshots`

End-of-month snapshot of billable units per tenant. Used to generate `subscription_invoices` and as a cached fallback when live active-user/device counts are unavailable.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `snapshot_date` | `date` | Last day of the billing month |
| `active_employee_count` | `integer` | Active employees at snapshot time |
| `enrolled_device_count` | `integer` | Enrolled devices at snapshot time |
| `employee_breakdown` | `jsonb` | Count by department |
| `device_breakdown` | `jsonb` | Count by department |
| `created_at` | `timestamptz` | |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]]

**Unique:** `(tenant_id, snapshot_date)` - one snapshot per tenant per month.

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
| `price_tiers` | `jsonb` | Employee-count pricing tiers/rate table; not a plan identity and not module configuration |
| `pricing_unit` | `varchar(30)` | `per_employee`, `per_device`, `flat`, `custom` |
| `calculated_monthly_price` | `decimal(10,2)` | Sum of selected module bracket monthly prices |
| `calculated_annual_price` | `decimal(10,2)` | Sum of selected module bracket annual prices |
| `override_monthly_price` | `decimal(10,2)` | Nullable operator-adjusted monthly price |
| `override_annual_price` | `decimal(10,2)` | Nullable operator-adjusted annual price |
| `ai_token_limit_per_month` | `integer` | Nullable; required positive cap when the plan includes AI entitlement |
| `currency` | `varchar(3)` | ISO 4217 |
| `is_active` | `boolean` |  |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Pricing source rule:** `subscription_plans.price_tiers` defines employee-count pricing tiers. Tenant owner confirmed total employee count selects the tier for the first invoice. `subscription_plans.calculated_*` values are calculated from the selected plan/module bundle and selected employee-count tier. `override_*` values are the effective price only when present; they never erase the calculated values.

---

## `system_settings`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `setting_key` | `varchar(100)` | Unique |
| `setting_value` | `jsonb` |  |
| `description` | `text` |  |
| `updated_by_id` | `uuid` | FK -> users |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `updated_by_id` -> [[database/schemas/infrastructure#`users`|users]]

---

## `tenant_branding`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `logo_file_id` | `uuid` | FK -> file_records (nullable) |
| `primary_color` | `varchar(7)` | Hex color |
| `accent_color` | `varchar(7)` | Hex color |
| `metadata` | `jsonb` | Additional branding config |
| `updated_by_id` | `uuid` | FK -> users |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `logo_file_id` -> [[database/schemas/infrastructure#`file_records`|file_records]], `updated_by_id` -> [[database/schemas/infrastructure#`users`|users]]

---

## `feature_flag_overrides`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `flag_key` | `varchar(120)` | FK -> feature_flags(key) |
| `tenant_id` | `uuid` | FK -> tenants |
| `value` | `boolean` | Override value for this tenant |
| `granted_by_id` | `uuid` | FK -> platform_users(id) |
| `granted_at` | `timestamptz` | |
| `reason` | `text` | Nullable audit reason |
| UNIQUE: `(flag_key, tenant_id)` | | |

Per-tenant runtime overrides. Overrides are evaluated only after module entitlement and commercial feature inclusion pass.

---

## `tenant_subscriptions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `allowed_plan_ids` | `jsonb` | Plan IDs the tenant may choose from during demo upgrade or onboarding |
| `recommended_plan_id` | `uuid` | Nullable FK -> subscription_plans |
| `plan_id` | `uuid` | Nullable FK -> subscription_plans; final selected plan |
| `billing_cycle` | `varchar(20)` | `monthly` or `annual` |
| `status` | `varchar(30)` | `pending_payment`, `active`, `past_due`, `cancelled` |
| `current_period_start` | `date` | |
| `current_period_end` | `date` | |
| `billing_currency` | `varchar(3)` | ISO 4217 |
| `confirmed_employee_count` | `integer` | Used for first invoice quantity and company-size bracket |
| `selected_base_modules` | `jsonb` | Snapshot from selected plan |
| `selected_addon_modules` | `jsonb` | Selected optional module add-ons |
| `selected_resource_addons` | `jsonb` | Selected storage/AI resource packs |
| `calculated_monthly_price` | `decimal(10,2)` | Snapshot of calculated monthly amount |
| `calculated_annual_price` | `decimal(10,2)` | Snapshot of calculated annual amount |
| `annual_price_override` | `decimal(10,2)` | Nullable explicit annual override |
| `annual_discount_percent` | `decimal(5,2)` | Nullable annual discount |
| `ai_token_limit_per_month` | `integer` | Resolved shared AI token allowance |
| `tenant_storage_limit_gb` | `integer` | Resolved shared storage pool |
| `payment_gateway_config_id` | `uuid` | FK -> payment_gateway_configs; resolved from tenant country route |
| `unpaid_seat_dues_amount` | `decimal(12,2)` | Blocks cancellation/renewal changes when greater than zero |
| `created_by_id` | `uuid` | FK -> users or platform_users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

---
## `user_preferences`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `user_id` | `uuid` | FK -> users |
| `tenant_id` | `uuid` | FK -> tenants |
| `preference_key` | `varchar(100)` | e.g., `theme`, `locale`, `timezone` |
| `preference_value` | `jsonb` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `user_id` -> [[database/schemas/infrastructure#`users`|users]], `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `webhook_deliveries`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `webhook_endpoint_id` | `uuid` | FK -> webhook_endpoints |
| `event_type` | `varchar(50)` |  |
| `payload` | `jsonb` | Sent payload |
| `response_status` | `integer` | HTTP status code |
| `response_body` | `text` | Truncated response |
| `attempt_number` | `integer` | Retry count |
| `delivered_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `webhook_endpoint_id` -> [[#`webhook_endpoints`|webhook_endpoints]]

---

## `webhook_endpoints`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `url` | `varchar(500)` | Target URL |
| `secret_hash` | `varchar(255)` | HMAC signing secret hash |
| `events` | `jsonb` | Subscribed event types |
| `is_active` | `boolean` |  |
| `created_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `created_by_id` -> [[database/schemas/infrastructure#`users`|users]]

---

## `automation_definitions`

Customer-created Automation Center definitions.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `name` | `varchar(100)` | |
| `description` | `text` | Nullable |
| `trigger_type` | `varchar(50)` | Domain event or scheduled/manual trigger |
| `resource_type` | `varchar(50)` | Resource type this automation handles |
| `is_active` | `boolean` | |
| `current_version` | `integer` | Active definition version |
| `created_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `created_by_id` -> [[database/schemas/infrastructure#`users`|users]]

---

## `automation_definition_versions`

Immutable version snapshots for Automation Center definitions.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `automation_definition_id` | `uuid` | FK -> automation_definitions |
| `version` | `integer` | |
| `definition_json` | `jsonb` | Trigger, condition, resolver, action, wait, escalation config |
| `created_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` | |

**Foreign Keys:** `automation_definition_id` -> [[#`automation_definitions`|automation_definitions]], `created_by_id` -> [[database/schemas/infrastructure#`users`|users]]

---

## `automation_templates`

Operator-managed starter templates that customers can apply and edit.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `name` | `varchar(100)` | |
| `description` | `text` | Nullable |
| `resource_type` | `varchar(50)` | |
| `template_json` | `jsonb` | Builder configuration copied into an automation definition |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

---

## `automation_runs`

Execution record for an automation definition version.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `automation_definition_id` | `uuid` | FK -> automation_definitions |
| `automation_definition_version_id` | `uuid` | FK -> automation_definition_versions |
| `workflow_instance_id` | `uuid` | FK -> workflow_instances; nullable until workflow starts |
| `trigger_event_type` | `varchar(100)` | |
| `resource_type` | `varchar(50)` | |
| `resource_id` | `uuid` | |
| `status` | `varchar(20)` | `matched`, `started`, `completed`, `failed`, `skipped` |
| `started_at` | `timestamptz` | |
| `completed_at` | `timestamptz` | Nullable |
| `metadata_json` | `jsonb` | Nullable execution metadata |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `automation_definition_id` -> [[#`automation_definitions`|automation_definitions]], `automation_definition_version_id` -> [[#`automation_definition_versions`|automation_definition_versions]], `workflow_instance_id` -> [[#`workflow_instances`|workflow_instances]]

---

## `workflow_definitions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `name` | `varchar(100)` |  |
| `code` | `varchar(50)` | Unique identifier |
| `resource_type` | `varchar(50)` | e.g., `LeaveRequest`, `ExpenseClaim` |
| `description` | `text` |  |
| `is_active` | `boolean` |  |
| `version` | `integer` | Versioning for definition changes |
| `created_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `created_by_id` -> [[database/schemas/infrastructure#`users`|users]]

---

## `workflow_instances`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `workflow_definition_id` | `uuid` | FK -> workflow_definitions |
| `resource_type` | `varchar(50)` | Polymorphic - e.g., `LeaveRequest` |
| `resource_id` | `uuid` | Polymorphic - FK to resource |
| `initiated_by_id` | `uuid` | FK -> employees |
| `current_step_order` | `integer` | Which step is active |
| `status` | `varchar(20)` | `in_progress`, `waiting_for_info`, `blocked`, `approved`, `rejected`, `cancelled`, `expired` |
| `requester_tenant_id` | `uuid` | Nullable; cross-company workflow provenance |
| `source_tenant_id` | `uuid` | Nullable; cross-company source tenant |
| `target_tenant_id` | `uuid` | Nullable; cross-company target tenant |
| `subject_tenant_id` | `uuid` | Nullable; tenant that owns the workflow subject/resource |
| `actor_tenant_id` | `uuid` | Nullable; tenant of the initiating actor |
| `company_connection_id` | `uuid` | Nullable; Shared Platform company connection used for routing |
| `data_sharing_scope` | `jsonb` | Nullable; approved fields/evidence scope for cross-company case |
| `completion_policy` | `varchar(30)` | Nullable; behavior if company connection is revoked mid-case |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `workflow_definition_id` -> [[#`workflow_definitions`|workflow_definitions]], `initiated_by_id` -> [[database/schemas/core-hr#`employees`|employees]]

---

## `workflow_step_instances`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `workflow_instance_id` | `uuid` | FK -> workflow_instances |
| `workflow_step_id` | `uuid` | FK -> workflow_steps |
| `assigned_to_id` | `uuid` | Legacy single-assignee compatibility field; new implementation uses `workflow_step_assignments` |
| `status` | `varchar(20)` | `pending`, `approved`, `rejected`, `skipped` |
| `started_at` | `timestamptz` |  |
| `completed_at` | `timestamptz` | Nullable |
| `sla_deadline_at` | `timestamptz` | When timeout fires |

**Foreign Keys:** `workflow_instance_id` -> [[#`workflow_instances`|workflow_instances]], `workflow_step_id` -> [[#`workflow_steps`|workflow_steps]], `assigned_to_id` -> [[database/schemas/core-hr#`employees`|employees]] (legacy only)

---

## `workflow_step_assignments`

Resolved assignees/approvers for one active workflow step.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `workflow_step_instance_id` | `uuid` | FK -> workflow_step_instances |
| `assigned_employee_id` | `uuid` | FK -> employees |
| `assigned_user_id` | `uuid` | FK -> users; nullable if employee has no user account |
| `sequence_order` | `integer` | Used for sequential approval |
| `status` | `varchar(20)` | `pending`, `approved`, `rejected`, `skipped`, `expired` |
| `resolved_from` | `varchar(50)` | Resolver that produced this assignment |
| `assigned_at` | `timestamptz` | |
| `acted_at` | `timestamptz` | Nullable |
| `expires_at` | `timestamptz` | Nullable |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `workflow_step_instance_id` -> [[#`workflow_step_instances`|workflow_step_instances]], `assigned_employee_id` -> [[database/schemas/core-hr#`employees`|employees]], `assigned_user_id` -> [[database/schemas/infrastructure#`users`|users]]

---

## `case_conversations`

Shared Platform metadata linking workflow/case state to WorkSync Chat private channels.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `channel_id` | `uuid` | FK -> WorkSync Chat `channels` |
| `case_type` | `varchar(50)` | `approval`, `alert`, `request`, `escalation`, `workflow` |
| `resource_type` | `varchar(50)` | Polymorphic resource type |
| `resource_id` | `uuid` | Polymorphic resource id |
| `workflow_instance_id` | `uuid` | FK -> workflow_instances |
| `workflow_step_instance_id` | `uuid` | FK -> workflow_step_instances; nullable |
| `status` | `varchar(20)` | `open`, `resolved`, `cancelled` |
| `created_by_automation_id` | `uuid` | FK -> automation_definitions; nullable |
| `created_at` | `timestamptz` | |
| `resolved_at` | `timestamptz` | Nullable |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `channel_id` -> [[database/schemas/wms-chat#`channels`|channels]], `workflow_instance_id` -> [[#`workflow_instances`|workflow_instances]], `workflow_step_instance_id` -> [[#`workflow_step_instances`|workflow_step_instances]], `created_by_automation_id` -> [[#`automation_definitions`|automation_definitions]]

---

## `workflow_delivery_routes`

Delivery routing state for workflow action cards.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `workflow_instance_id` | `uuid` | FK -> workflow_instances |
| `workflow_step_instance_id` | `uuid` | FK -> workflow_step_instances |
| `target_type` | `varchar(30)` | `employee`, `user`, `channel`, `inbox`, `teams` |
| `target_id` | `uuid` | Target id where available |
| `delivery_surface` | `varchar(30)` | `chat`, `inbox`, `teams_mirror`, `email`, `push`, `signalr` |
| `status` | `varchar(20)` | `pending`, `sent`, `failed`, `cancelled` |
| `last_sent_at` | `timestamptz` | Nullable |
| `metadata_json` | `jsonb` | Provider/action-card metadata |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `workflow_instance_id` -> [[#`workflow_instances`|workflow_instances]], `workflow_step_instance_id` -> [[#`workflow_step_instances`|workflow_step_instances]]

---

## `workflow_steps`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `workflow_definition_id` | `uuid` | FK -> workflow_definitions |
| `step_order` | `integer` | Execution order |
| `step_type` | `varchar(30)` | `approval`, `notification`, `condition` |
| `approver_type` | `varchar(30)` | Legacy compatibility field; do not use for new definitions |
| `approver_role_id` | `uuid` | Legacy compatibility field; do not use for new definitions |
| `resolver_type` | `varchar(50)` | Dynamic resolver type, e.g. `reporting_manager`, `selected_permission`, `case_participants` |
| `resolver_config` | `jsonb` | Resolver parameters such as permission code, legal entity/department/team/position/position branch, optional job level when configured, employee id, connected tenant scope |
| `approval_mode` | `varchar(30)` | `only_one_required`, `all_required`, `sequential` |
| `action_config` | `jsonb` | Action-card, request-info, escalation, or task creation settings |
| `delivery_config` | `jsonb` | Chat, Inbox, Teams mirror, notification routing preferences |
| `conditions` | `jsonb` | Step conditions (e.g., skip if amount < threshold) |
| `sla_hours` | `integer` | Hours before timeout action |
| `on_timeout_action` | `varchar(30)` | `escalate`, `auto_approve`, `auto_reject` |

**Foreign Keys:** `workflow_definition_id` -> [[#`workflow_definitions`|workflow_definitions]], `approver_role_id` -> [[database/schemas/auth#`roles`|roles]] (legacy only)

---

## Related

- [[modules/shared-platform/overview|Shared Platform Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]

