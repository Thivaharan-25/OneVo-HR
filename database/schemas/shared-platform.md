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
| `workflow_step_assignment_id` | `uuid` | FK -> workflow_step_assignments; nullable for legacy actions |
| `action_metadata` | `jsonb` | Optional action-card or resolver metadata |
| `delegated_to_id` | `uuid` | FK → employees (nullable — only for delegate action) |

**Foreign Keys:** `workflow_instance_id` → [[#`workflow_instances`|workflow_instances]], `workflow_step_id` → [[#`workflow_steps`|workflow_steps]], `actor_id` → [[database/schemas/core-hr#`employees`|employees]], `delegated_to_id` → [[database/schemas/core-hr#`employees`|employees]], `workflow_step_assignment_id` -> [[#`workflow_step_assignments`|workflow_step_assignments]]

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
| `payment_provider_ref` | `varchar(100)` | Gateway payment method ID from Stripe or PayHere |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `payment_gateway_configs`

Gateway configuration for Stripe and PayHere. Supports global platform defaults and optional tenant-specific gateway configuration. Secrets are encrypted through `IEncryptionService`; admin APIs return safe metadata only.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | Nullable; null means platform/global default gateway config |
| `provider` | `varchar(30)` | `stripe`, `payhere` |
| `mode` | `varchar(20)` | `test`, `live` |
| `display_name` | `varchar(100)` | Friendly operator label |
| `public_key` | `varchar(255)` | Nullable; Stripe publishable key or equivalent public identifier |
| `merchant_id` | `varchar(100)` | Nullable; PayHere merchant ID |
| `secret_encrypted` | `bytea` | Encrypted Stripe secret key or PayHere merchant secret |
| `webhook_secret_encrypted` | `bytea` | Encrypted Stripe webhook secret or PayHere notify/hash secret when separate |
| `webhook_url` | `varchar(500)` | Gateway callback/notify URL |
| `is_default` | `boolean` | Default gateway for tenant/platform |
| `is_active` | `boolean` | Whether this config can be used for payment collection |
| `created_by_id` | `uuid` | FK -> users or dev platform account boundary |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Rule:** Subscription collection and full-license maintenance collection must reference a configured gateway provider (`stripe` or `payhere`) when `*_collection_mode = gateway`.

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
| `price_brackets` | `jsonb` | Company-size price ranges; see module pricing JSON below |
| `full_license_price` | `decimal(12,2)` | Nullable one-time purchase price |
| `maintenance_rate` | `decimal(5,2)` | Nullable yearly percentage for maintenance, e.g., 18.00 |
| `pricing_unit` | `varchar(30)` | `per_employee`, `per_device`, `flat`, `custom` |
| `permission_codes_json` | `jsonb` | Permission codes owned by this module; each permission may belong to only one module |
| `requires_ai_token_limit` | `boolean` | True when tenant subscription must set an AI token limit for this module |
| `requires_storage_limit` | `boolean` | True when tenant subscription must set a storage limit for this module |
| `default_storage_limit_gb` | `integer` | Nullable default storage entitlement for storage-backed modules |
| `is_active` | `boolean` | Whether the module can be sold/provisioned |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Module pricing JSON contract:** `price_brackets` is the reusable catalog source for dynamic subscription-plan pricing. It uses the same employee ranges exposed by the tenant creation company-size dropdown. `max_employees = -1` means unlimited.

```json
{
  "module_key": "core_hr",
  "name": "Core HR",
  "pricing_unit": "per_employee",
  "is_active": true,
  "price_brackets": [
    { "min_employees": 0, "max_employees": 50, "monthly_price": 4, "annual_price": 40 },
    { "min_employees": 51, "max_employees": 200, "monthly_price": 3.5, "annual_price": 35 },
    { "min_employees": 201, "max_employees": -1, "monthly_price": 3, "annual_price": 30 }
  ],
  "full_license_price": 500000,
  "maintenance_rate": 18
}
```

**Dynamic plan pricing rule:** when an operator creates a reusable subscription plan, the plan editor selects a company-size range and modules. The backend sums the matching bracket price for each selected module. Example: Core HR at `$3.50` for `51-200` employees plus Work Management at `$4.00` for `51-200` employees produces `$7.50` per employee. Operator-entered overrides are stored separately from calculated prices.

**Permission ownership rule:** a permission code can be owned by only one module catalog item. The Developer Platform must show the owning module beside each permission and must reject attempts to assign a permission to a second module unless it is first removed from the original module through an explicit catalog update.

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
| `old_price_brackets` | `jsonb` | Nullable previous company-size bracket pricing |
| `new_price_brackets` | `jsonb` | Nullable new company-size bracket pricing |
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

The schema supports the commercial model requested by product:

- `tenant_subscriptions.commercial_model` records `subscription` vs `full_license_maintenance`.
- Subscription tenants normally use `tenant_subscriptions.subscription_collection_mode = gateway` with `gateway_provider` and gateway refs so recurring SaaS fees are collected through the payment gateway.
- Full-license tenants can use `tenant_subscriptions.license_payment_mode = manual` for the one-time license sale; `full_license_amount`, `license_paid_at`, and `license_reference` record the manual/offline purchase.
- `tenant_subscriptions.maintenance_collection_mode = gateway` means full-license maintenance/support is collected through the system payment gateway even when the one-time license was manually paid.
- `tenant_subscriptions.maintenance_status`, `maintenance_start_date`, `maintenance_renewal_date`, `maintenance_rate`, and `maintenance_amount` track maintenance state and recurring fee calculation for full-license tenants.
- Manual subscription, full-license, and maintenance payments require `manual_billing_evidence_file_id` or `manual_billing_reference` plus an audit reason. Evidence files are stored through Infrastructure file records.
- Payment exception/grace windows can apply to subscription tenants and full-license/maintenance tenants. They are tenant-specific commercial exceptions and are not inferred from reusable plan defaults after assignment.
- Work Management storage-backed modules require `work_management_storage_limit_gb`; AI-capable modules require `ai_token_limit_per_month`.
- `tenant_module_entitlements.sales_state` records manual sales state per module: `available`, `purchased`, `trial`, `quoted`, `maintenance_included`, `subscription_included`, or `disabled`.
- Module pricing defaults live on `module_catalog.price_brackets`; reusable plan calculated/override prices live on `subscription_plans`; tenant-specific negotiated snapshots live on `tenant_subscriptions` and `tenant_module_entitlements`.
- Subscription plan pricing is calculated from selected packages/modules plus company-size range. Use the same company-size range values as tenant creation, and store operator overrides separately from calculated prices.
- AI-capable plans and tenant subscriptions must store a positive `ai_token_limit_per_month`; non-AI plans leave it null.

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

Reusable setup templates visible in the Developer Platform Templates area.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `template_key` | `varchar(100)` | Unique template key |
| `template_type` | `varchar(50)` | `configuration`, `role`, `org_structure`, `job_family`, `leave_policy`, `onboarding`, `app_allowlist`, `monitoring_policy`, `data_import_mapping` |
| `name` | `varchar(150)` | Display name |
| `version` | `integer` | Template version |
| `module_keys_json` | `jsonb` | Modules/services this template applies to |
| `payload_json` | `jsonb` | Template content owned by the target module contract |
| `is_system` | `boolean` | ONEVO default template |
| `is_active` | `boolean` | |
| `created_by_id` | `uuid` | FK -> users or dev platform account boundary |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

---

## `tenant_configuration_template_applications`

Tracks when a reusable template is applied and then customized for a tenant.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `configuration_template_id` | `uuid` | FK -> configuration_templates |
| `template_type` | `varchar(50)` | Snapshot of the template type |
| `applied_version` | `integer` | Version applied |
| `custom_payload_json` | `jsonb` | Tenant-specific override payload after application |
| `status` | `varchar(20)` | `applied`, `customized`, `superseded`, `removed` |
| `applied_by_id` | `uuid` | FK -> users or dev platform account boundary |
| `applied_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | Nullable |

**Rule:** applying a reusable template creates tenant-specific configuration. Editing the tenant copy must not mutate the global template.

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
| `company_size_range` | `varchar(30)` | Same value set as tenant creation company-size dropdown |
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

**Pricing source rule:** `subscription_plans.calculated_*` values are calculated from `module_catalog.price_brackets` for the selected `company_size_range` and `included_modules`. `override_*` values are the effective price only when present; they never erase the calculated values.

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
| `company_size_range` | `varchar(30)` | Snapshot copied from the selected plan/tenant company-size range |
| `selected_modules` | `jsonb` | Snapshot of module keys included in this tenant's commercial record |
| `calculated_monthly_price` | `decimal(10,2)` | Snapshot of calculated monthly per-unit price at assignment time |
| `calculated_annual_price` | `decimal(10,2)` | Snapshot of calculated annual per-unit price at assignment time |
| `override_monthly_price` | `decimal(10,2)` | Nullable negotiated monthly per-unit price |
| `override_annual_price` | `decimal(10,2)` | Nullable negotiated annual per-unit price |
| `override_full_license_amount` | `decimal(12,2)` | Nullable negotiated one-time full-license amount |
| `override_maintenance_rate` | `decimal(5,2)` | Nullable negotiated maintenance percentage |
| `override_maintenance_amount` | `decimal(12,2)` | Nullable negotiated recurring maintenance amount |
| `ai_token_limit_per_month` | `integer` | Nullable monthly AI token cap for this tenant subscription |
| `work_management_storage_limit_gb` | `integer` | Nullable storage entitlement for Work Management storage-backed features |
| `manual_billing_evidence_file_id` | `uuid` | Nullable FK -> file_records for manual subscription/license/maintenance evidence |
| `manual_billing_reference` | `varchar(100)` | Nullable external invoice/reference for manual payment evidence |
| `payment_exception_starts_at` | `date` | Nullable approved commercial exception start |
| `payment_exception_ends_at` | `date` | Nullable approved commercial exception end |
| `payment_exception_reason` | `text` | Nullable reason for approved payment grace/exception |
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

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `workflow_definition_id` → [[#`workflow_definitions`|workflow_definitions]], `initiated_by_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## `workflow_step_instances`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `workflow_instance_id` | `uuid` | FK → workflow_instances |
| `workflow_step_id` | `uuid` | FK → workflow_steps |
| `assigned_to_id` | `uuid` | Legacy single-assignee compatibility field; new implementation uses `workflow_step_assignments` |
| `status` | `varchar(20)` | `pending`, `approved`, `rejected`, `skipped` |
| `started_at` | `timestamptz` |  |
| `completed_at` | `timestamptz` | Nullable |
| `sla_deadline_at` | `timestamptz` | When timeout fires |

**Foreign Keys:** `workflow_instance_id` → [[#`workflow_instances`|workflow_instances]], `workflow_step_id` → [[#`workflow_steps`|workflow_steps]], `assigned_to_id` → [[database/schemas/core-hr#`employees`|employees]] (legacy only)

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
| `workflow_definition_id` | `uuid` | FK → workflow_definitions |
| `step_order` | `integer` | Execution order |
| `step_type` | `varchar(30)` | `approval`, `notification`, `condition` |
| `approver_type` | `varchar(30)` | Legacy compatibility field; do not use for new definitions |
| `approver_role_id` | `uuid` | Legacy compatibility field; do not use for new definitions |
| `resolver_type` | `varchar(50)` | Dynamic resolver type, e.g. `reporting_manager`, `selected_permission`, `case_participants` |
| `resolver_config` | `jsonb` | Resolver parameters such as permission code, department/team/job level, employee id, connected tenant scope |
| `approval_mode` | `varchar(30)` | `only_one_required`, `all_required`, `sequential` |
| `action_config` | `jsonb` | Action-card, request-info, escalation, or task creation settings |
| `delivery_config` | `jsonb` | Chat, Inbox, Teams mirror, notification routing preferences |
| `conditions` | `jsonb` | Step conditions (e.g., skip if amount < threshold) |
| `sla_hours` | `integer` | Hours before timeout action |
| `on_timeout_action` | `varchar(30)` | `escalate`, `auto_approve`, `auto_reject` |

**Foreign Keys:** `workflow_definition_id` → [[#`workflow_definitions`|workflow_definitions]], `approver_role_id` → [[database/schemas/auth#`roles`|roles]] (legacy only)

---

## Related

- [[modules/shared-platform/overview|Shared Platform Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]
