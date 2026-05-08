# Contract: Developer Platform Admin API

**Backend owner:** DEV1 Tasks 7-9, DEV4 Task 8  
**Consumers:** DEV5 Tasks 5-7  
**Canonical source:** `ONEVO.Api` admin surface (`/admin/v1/*`). Phase 1 has one backend deployment; `ONEVO.Admin.Api` must not be deployed.

**Provisioning API count:** Phase 1 tenant provisioning requires 22 admin endpoints: plan catalog, module catalog, tenant validation, tenant list/create/detail/edit/status, subscription, modules, permission catalog, role template list/create/edit/apply, tenant role list/create/permission update, settings, invite admin, provisioning summary, and activation confirm. Tenant-facing role management after activation is separate under `/api/v1/roles`.

---

## POST `/admin/v1/auth/google-callback`

```ts
interface AdminLoginRequestDto {
  google_id_token: string
}

interface AdminAuthResponseDto {
  access_token: string        // 30-minute platform-admin JWT
  token_type: "Bearer"
  expires_in: number
  platform_role: "super_admin" | "admin" | "viewer"
}
```

## GET `/admin/v1/tenants`

```ts
interface TenantListItemDto {
  id: string
  company_name: string
  slug: string
  plan_tier: string
  status: "provisioning" | "active" | "suspended"
  employee_count: number
  agent_count: number
  created_at: string
  last_login_at: string | null
}
```

## GET `/admin/v1/subscription-plans`

Plans are reusable catalog records. Operators select one plan for a tenant; tenant-specific pricing, discounts, contract value, maintenance terms, and manual billing state are stored on the tenant subscription/commercial record.

```ts
interface SubscriptionPlanDto {
  id: string
  code: "starter" | "professional" | "enterprise" | string
  name: string
  tier: string
  included_modules: string[]
  pricing_unit: "per_employee" | "per_device" | "flat" | "custom"
  monthly_price: number | null
  annual_price: number | null
  currency: string
  is_active: boolean
}
```

## GET `/admin/v1/modules/catalog`

```ts
interface ModuleCatalogItemDto {
  module_key: string
  name: string
  pillar: "hr" | "workforce_intelligence" | "worksync" | "shared" | string
  phase: "phase_1" | "phase_2" | "future" | string
  pricing_unit: "per_employee" | "per_device" | "flat" | "custom"
  default_price_monthly: number | null
  default_price_annual: number | null
  full_license_price: number | null
  default_maintenance_rate: number | null
  is_active: boolean
}
```

## GET `/admin/v1/tenants/validate`

Used by the wizard before or during draft creation. Country-specific registration validation may return warnings until product defines strict per-country rules.

```ts
interface TenantValidationQuery {
  slug?: string
  company_name?: string
  email_domain?: string
  registration_number?: string
  country?: string
}

interface TenantValidationResponseDto {
  valid: boolean
  conflicts: Array<{
    field: "slug" | "company_name" | "email_domain" | "registration_number"
    message: string
  }>
  warnings: Array<{
    field: string
    message: string
  }>
}
```

## POST `/admin/v1/tenants`

```ts
interface CreateTenantDraftDto {
  company_name: string
  slug: string
  legal_entity_name: string
  registration_number?: string | null
  country: string
  timezone: string
  currency: string
  industry_profile: string
  company_size_range?: string | null
}

interface CreateTenantDraftResponseDto {
  tenant_id: string
  status: "provisioning"
  next_step: "subscription"
}
```

## GET `/admin/v1/tenants/{id}`

```ts
interface TenantDetailDto {
  id: string
  company_name: string
  slug: string
  legal_entity_name: string
  registration_number: string | null
  country: string
  timezone: string
  currency: string
  industry_profile: string
  plan_tier: string
  status: "provisioning" | "active" | "suspended"
  billing_start_date: string | null
  subscription_override: boolean
  users_summary: { total: number; admins: number }
  agents_summary: { total: number; online: number }
  flags_summary: { overrides: number }
  settings_summary: { timezone: string; privacy_mode: boolean }
}
```

## PATCH `/admin/v1/tenants/{id}`

Draft tenant details can be edited before activation. Post-activation edits should use narrower lifecycle/settings APIs.

```ts
interface UpdateTenantDraftDto {
  company_name?: string
  legal_entity_name?: string
  registration_number?: string | null
  country?: string
  timezone?: string
  currency?: string
  industry_profile?: string
  company_size_range?: string | null
}
// response: 204 No Content
```

## PATCH `/admin/v1/tenants/{id}/status`

```ts
// body
{ action: "suspend" | "unsuspend" | "activate"; reason?: string }
// response: 204 No Content
```

## PATCH `/admin/v1/tenants/{id}/subscription`

```ts
interface SubscriptionOverrideDto {
  plan_code: string
  commercial_model: "subscription" | "full_license_maintenance"
  billing_cycle: "monthly" | "annual" | "manual"
  billing_currency: string
  billing_start_date: string  // ISO date
  contract_start_date?: string
  contract_end_date?: string | null
  stripe_managed?: boolean
  maintenance_status?: "active" | "due" | "expired" | "waived"
  maintenance_renewal_date?: string | null
  maintenance_rate?: number | null
  custom_contract_value?: number | null
  discount_percent?: number | null
  reason: string              // required; written to audit log
}
```

## PUT `/admin/v1/tenants/{id}/modules`

```ts
interface TenantModuleSelectionDto {
  modules: Array<{
    module_key: string
    enabled: boolean
    sales_state: "available" | "trial" | "quoted" | "purchased" | "maintenance_included" | "subscription_included" | "disabled"
    pricing_model?: "subscription" | "full_license" | "maintenance" | "trial" | "custom"
    price?: number | null
    currency?: string | null
    starts_at?: string | null
    ends_at?: string | null
  }>
}
// response: 204 No Content
```

`available` and `quoted` are commercial pipeline states and do not grant tenant-facing access. Active module access is granted by `purchased`, `trial`, `subscription_included`, or `maintenance_included`, unless the entitlement has expired.

## GET `/admin/v1/tenants/{id}/permissions/catalog`

```ts
interface TenantPermissionCatalogDto {
  tenant_id: string
  enabled_modules: string[]
  modules: Array<{
    module_key: string
    display_name: string
    permissions: Array<{
      id: string
      code: string
      description: string
      is_universal: boolean
    }>
  }>
}
```

Only permissions from enabled tenant modules plus universal permissions are returned.

## Role Template APIs

```ts
interface RoleTemplateDto {
  id: string
  name: string
  description: string | null
  module_keys: string[]
  permission_codes: string[]
  is_system: boolean
  version: number
  is_active: boolean
}

interface CreateRoleTemplateDto {
  name: string
  description?: string
  module_keys: string[]
  permission_codes: string[]
}
```

Routes:

```http
GET /admin/v1/role-templates
POST /admin/v1/role-templates
PATCH /admin/v1/role-templates/{id}
POST /admin/v1/tenants/{id}/role-templates/{templateId}/apply
GET /admin/v1/tenants/{id}/roles
POST /admin/v1/tenants/{id}/roles
PUT /admin/v1/tenants/{id}/roles/{roleId}/permissions
```

Applying or editing a role template must validate the permission list against `GET /admin/v1/tenants/{id}/permissions/catalog`.

Operators use global templates for reusable patterns and tenant-specific roles for one-customer needs. Role creation does not require job levels. Job levels only affect scoped permissions, hierarchy, and workflow routing later.

```ts
interface TenantRoleDto {
  id: string
  tenant_id: string
  name: string
  description: string | null
  is_system: boolean
  source_template_id: string | null
  permission_codes: string[]
  created_at: string
  updated_at: string
}

interface CreateTenantRoleDto {
  name: string
  description?: string
  permission_codes: string[]
}

interface UpdateTenantRolePermissionsDto {
  permission_codes: string[]
  reason?: string
}

interface ApplyRoleTemplateDto {
  role_name_override?: string
  duplicate_name_strategy?: "idempotent" | "fail" | "create_copy"
}
```

## PATCH `/admin/v1/tenants/{id}/settings`

```ts
interface TenantInitialSettingsDto {
  timezone: string
  currency: string
  date_format: string
  fiscal_year_start_month?: number
  work_week: Array<"monday" | "tuesday" | "wednesday" | "thursday" | "friday" | "saturday" | "sunday">
  workday_start: string       // HH:mm local time
  workday_end: string         // HH:mm local time
  privacy_mode: boolean
  monitoring_transparency_mode?: "transparent" | "private" | "disclosed"
  desktop_agent_transparency_mode?: "visible" | "silent" | "policy_controlled"
  leave_policy_defaults?: {
    annual_leave_accrual_method?: "monthly" | "annual" | "manual"
    carry_over_cap_days?: number | null
  }
  module_settings?: Record<string, unknown>
}
// response: 204 No Content
```

## POST `/admin/v1/tenants/{id}/invite-admin`

```ts
interface TenantOwnerInviteDto {
  email: string
  first_name: string
  last_name: string
  role_id: string
}
// response
{ user_id: string; invite_expires_at: string }
```

This sends a set-password link. It must not require the operator to choose the tenant owner's final password.

The selected `role_id` must refer to a materialized tenant role that satisfies the minimum owner/admin permission requirement.

## GET `/admin/v1/tenants/{id}/provisioning-summary`

```ts
interface ProvisioningSummaryDto {
  tenant_id: string
  status: "provisioning" | "active" | "suspended"
  sections: {
    tenant_details: ProvisioningSectionStatus
    subscription: ProvisioningSectionStatus
    modules: ProvisioningSectionStatus
    roles: ProvisioningSectionStatus
    settings: ProvisioningSectionStatus
    owner_invite: ProvisioningSectionStatus
  }
  can_activate: boolean
  blocking_errors: Array<{ code: string; message: string; section: string }>
  warnings: Array<{ code: string; message: string; section: string }>
}

interface ProvisioningSectionStatus {
  complete: boolean
  summary: Record<string, unknown>
  missing_fields: string[]
}
```

## PATCH `/admin/v1/tenants/{id}/provision/confirm`

Activation is allowed only after tenant details, subscription/commercial terms, module selection, role templates, required settings, and owner invite are complete.

```ts
// success response: 204 No Content
// incomplete response: 422 with ProvisioningSummaryDto
```

## POST `/admin/v1/tenants/{id}/impersonate`

```ts
// response
{ impersonation_token: string; expires_at: string }
```

## GET `/admin/v1/feature-flags`

```ts
interface FeatureFlagListItemDto {
  key: string
  description: string
  global_default: boolean
  rollout_percentage: number
  tenant_override_count: number
}
```

## GET `/admin/v1/agent-versions`

```ts
interface AgentVersionDto {
  id: string
  version: string             // semver
  channel: "internal" | "beta" | "ga"
  status: "published" | "recalled"
  release_notes: string
  minimum_os: string
  publisher: string
  published_at: string
  recalled_at: string | null
  download_url: string
}
```

## GET `/admin/v1/agent-rings`

```ts
interface AgentRingDto {
  ring_id: string
  name: "Ring 0 Internal" | "Ring 1 Beta" | "Ring 2 GA"
  tenant_count: number
  agent_count: number
}
```

## Notes

- All `/admin/v1/*` endpoints reject tenant JWTs (`iss` mismatch -> 401)
- `platform_role` claim is required on every admin endpoint; `viewer` role cannot mutate
- Impersonation token is non-renewable (15 min) and writes an audit log regardless of outcome
- Provisioning tenants (`status: "provisioning"`) are visible here but excluded from `/api/v1/*`
