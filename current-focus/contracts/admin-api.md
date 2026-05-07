# Contract: Developer Platform Admin API

**Backend owner:** DEV1 Tasks 7-9, DEV4 Task 8  
**Consumers:** DEV5 Tasks 5-7  
**Canonical source:** `ONEVO.Api` admin surface (`/admin/v1/*`). Phase 1 has one backend deployment; `ONEVO.Admin.Api` must not be deployed.

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

## GET `/admin/v1/tenants/{id}`

```ts
interface TenantDetailDto {
  id: string
  company_name: string
  slug: string
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

## PATCH `/admin/v1/tenants/{id}/status`

```ts
// body
{ action: "suspend" | "unsuspend" | "activate"; reason?: string }
// response: 204 No Content
```

## PATCH `/admin/v1/tenants/{id}/subscription`

```ts
interface SubscriptionOverrideDto {
  plan_tier: string
  commercial_model: "subscription" | "full_license_maintenance"
  billing_cycle: "monthly" | "annual" | "manual"
  billing_currency: string
  billing_start_date: string  // ISO date
  contract_start_date?: string
  contract_end_date?: string | null
  maintenance_status?: "active" | "due" | "expired" | "waived"
  maintenance_renewal_date?: string | null
  maintenance_rate?: number | null
  custom_contract_value?: number | null
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
POST /admin/v1/tenants/{id}/role-templates/{templateId}/apply
PUT /admin/v1/tenants/{id}/roles/{roleId}/permissions
```

Applying or editing a role template must validate the permission list against `GET /admin/v1/tenants/{id}/permissions/catalog`.

## POST `/admin/v1/tenants/{id}/invite-admin`

```ts
interface TenantOwnerInviteDto {
  email: string
  first_name: string
  last_name: string
}
// response
{ user_id: string; invite_expires_at: string }
```

This sends a set-password link. It must not require the operator to choose the tenant owner's final password.

## PATCH `/admin/v1/tenants/{id}/provision/confirm`

Activation is allowed only after tenant details, subscription/commercial terms, module selection, role templates, required settings, and owner invite are complete.

```ts
// response: 204 No Content
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

