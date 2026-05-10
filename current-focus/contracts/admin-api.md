# Contract: Developer Platform Admin API

**Backend owner:** DEV1 Tasks 7-9, DEV4 Task 8  
**Consumers:** DEV5 Tasks 5-7  
**Canonical source:** `ONEVO.Api` admin surface (`/admin/v1/*`). Phase 1 has one backend deployment; `ONEVO.Admin.Api` must not be deployed.

**Provisioning API count:** Phase 1 tenant provisioning requires 23 admin endpoints: plan catalog, module catalog, country defaults, tenant validation, tenant list/create/detail/edit/status, subscription, modules, permission catalog, role template list/create/edit/apply, tenant role list/create/permission update, settings, invite admin, provisioning summary, and activation confirm. Tenant-facing role management after activation is separate under `/api/v1/roles`.

**Catalog cost-management APIs:** reusable plan prices are calculated from selected module price brackets and company-size ranges. Reusable module price brackets are managed through catalog admin endpoints. Tenant provisioning can override calculated prices per tenant, but base catalog prices need their own APIs.

**Backend API data rule:** every DTO below is the backend JSON contract between `ONEVO.Api` and the Developer Console. Field names are API response/request fields, not just UI labels. Frontend state may add view-only fields, but it must not rename or invent backend contract fields without updating this file.

```ts
type TenantLifecycleStatus = "provisioning" | "trial" | "active" | "suspended" | "cancelled"
```

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
interface TenantListQueryDto {
  search?: string
  status?: TenantLifecycleStatus
  plan_code?: string
  page?: number
  page_size?: number
}

interface TenantListItemDto {
  id: string
  company_name: string
  slug: string
  plan_tier: string
  status: TenantLifecycleStatus
  employee_count: number
  agent_count: number
  created_at: string
  last_login_at: string | null
}

interface TenantListResponseDto {
  items: TenantListItemDto[]
  total: number
  page: number
  page_size: number
}
```

## GET `/admin/v1/subscription-plans`

Plans are reusable catalog records. Operators select one plan for a tenant; tenant-specific pricing, discounts, contract value, payment collection mode, full-license payment evidence, and maintenance terms are stored on the tenant subscription/commercial record.

```ts
interface SubscriptionPlanDto {
  id: string
  code: "starter" | "professional" | "enterprise" | string
  name: string
  tier: string
  included_modules: string[]
  company_size_range: string
  pricing_unit: "per_employee" | "per_device" | "flat" | "custom"
  calculated_monthly_price: number
  calculated_annual_price: number
  override_monthly_price: number | null
  override_annual_price: number | null
  effective_monthly_price: number
  effective_annual_price: number
  ai_token_limit_per_month: number | null
  currency: string
  is_active: boolean
}

interface SubscriptionPlanListResponseDto {
  items: SubscriptionPlanDto[]
}
```

`effective_*_price` is derived as `override_*_price ?? calculated_*_price`. The backend calculates `calculated_*_price` from `module_catalog.price_brackets` for `included_modules` and `company_size_range`.

## POST `/admin/v1/subscription-plans`

Creates a reusable plan catalog record. Operators should use this only when ONEVO wants a plan reusable across tenants, not for one customer deal. The backend calculates plan prices from selected modules and company-size range; request override fields are optional negotiated catalog-level overrides.

```ts
interface CreateSubscriptionPlanDto {
  code: string
  name: string
  tier: string
  included_modules: string[]
  company_size_range: string
  pricing_unit: "per_employee" | "per_device" | "flat" | "custom"
  override_monthly_price?: number | null
  override_annual_price?: number | null
  ai_token_limit_per_month?: number | null
  currency: string
  is_active?: boolean
}

// response: SubscriptionPlanDto
```

## PATCH `/admin/v1/subscription-plans/{id}`

Updates reusable plan metadata, included modules, and base prices. Existing tenant subscriptions keep their stored commercial terms unless product explicitly runs a migration/reprice operation.

```ts
interface UpdateSubscriptionPlanDto {
  name?: string
  tier?: string
  included_modules?: string[]
  company_size_range?: string
  pricing_unit?: "per_employee" | "per_device" | "flat" | "custom"
  override_monthly_price?: number | null
  override_annual_price?: number | null
  ai_token_limit_per_month?: number | null
  currency?: string
  is_active?: boolean
  reason: string
}

// response: SubscriptionPlanDto
```

## GET `/admin/v1/modules/catalog`

```ts
interface ModuleCatalogItemDto {
  module_key: string
  name: string
  pillar: "hr" | "workforce_intelligence" | "worksync" | "shared" | string
  phase: "phase_1" | "phase_2" | "future" | string
  pricing_unit: "per_employee" | "per_device" | "flat" | "custom"
  price_brackets: ModulePriceBracketDto[]
  full_license_price: number | null
  maintenance_rate: number | null
  is_active: boolean
}

interface ModulePriceBracketDto {
  min_employees: number
  max_employees: number       // -1 means unlimited
  monthly_price: number
  annual_price: number
}

interface ModuleCatalogResponseDto {
  items: ModuleCatalogItemDto[]
}
```

## POST `/admin/v1/modules/catalog`

Creates a reusable module catalog record. This is for ONEVO product/catalog management, not tenant-specific enablement.

```ts
interface CreateModuleCatalogItemDto {
  module_key: string
  name: string
  pillar: "hr" | "workforce_intelligence" | "worksync" | "shared" | string
  phase: "phase_1" | "phase_2" | "future" | string
  pricing_unit: "per_employee" | "per_device" | "flat" | "custom"
  price_brackets: ModulePriceBracketDto[]
  full_license_price?: number | null
  maintenance_rate?: number | null
  is_active?: boolean
}

// response: ModuleCatalogItemDto
```

## PATCH `/admin/v1/modules/catalog/{moduleKey}`

Updates reusable module metadata and bracketed catalog prices. Existing tenant entitlements and tenant subscriptions keep their stored pricing snapshots unless product explicitly runs a migration/reprice operation.

```ts
interface UpdateModuleCatalogItemDto {
  name?: string
  pillar?: "hr" | "workforce_intelligence" | "worksync" | "shared" | string
  phase?: "phase_1" | "phase_2" | "future" | string
  pricing_unit?: "per_employee" | "per_device" | "flat" | "custom"
  price_brackets?: ModulePriceBracketDto[]
  full_license_price?: number | null
  maintenance_rate?: number | null
  is_active?: boolean
  reason: string
}

// response: ModuleCatalogItemDto
```

## GET `/admin/v1/payment-gateways`

Lists safe gateway metadata for Stripe and PayHere. Secrets are never returned.

```ts
interface PaymentGatewayConfigDto {
  id: string
  tenant_id: string | null
  provider: "stripe" | "payhere"
  mode: "test" | "live"
  display_name: string
  public_key?: string | null
  merchant_id?: string | null
  webhook_url: string
  is_default: boolean
  is_active: boolean
  created_at: string
  updated_at: string | null
}

interface PaymentGatewayConfigListResponseDto {
  items: PaymentGatewayConfigDto[]
}
```

## POST `/admin/v1/payment-gateways`

Creates a Stripe or PayHere gateway config. Secret fields are encrypted and are never returned.

```ts
interface CreatePaymentGatewayConfigDto {
  tenant_id?: string | null
  provider: "stripe" | "payhere"
  mode: "test" | "live"
  display_name: string
  public_key?: string | null          // Stripe publishable key when applicable
  merchant_id?: string | null         // PayHere merchant ID when applicable
  secret: string                      // Stripe secret key or PayHere merchant secret
  webhook_secret?: string | null      // Stripe webhook secret or PayHere notify/hash secret when separate
  webhook_url: string
  is_default?: boolean
  is_active?: boolean
}

// response: PaymentGatewayConfigDto
```

## PATCH `/admin/v1/payment-gateways/{id}`

Updates safe metadata and optionally rotates gateway secrets.

```ts
interface UpdatePaymentGatewayConfigDto {
  display_name?: string
  public_key?: string | null
  merchant_id?: string | null
  secret?: string
  webhook_secret?: string | null
  webhook_url?: string
  is_default?: boolean
  is_active?: boolean
  reason: string
}

// response: PaymentGatewayConfigDto
```

## GET `/admin/v1/reference/countries/{countryCode}/defaults`

Used by the tenant provisioning wizard after country selection to prefill timezone and legal entity currency.

```ts
interface CountryDefaultsDto {
  country_code: string
  country_name: string
  default_timezone: string
  timezones: string[]
  default_currency: string
  currencies: Array<{
    code: string
    name: string
    symbol: string
  }>
}
```

Rule: single-timezone countries may auto-fill timezone. Multi-timezone countries must return all supported choices so the frontend can require operator selection. Currency defaults from country but is saved on `legal_entities.currency_code`.

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
interface TenantOwnerInviteDto {
  email: string
  first_name: string
  last_name: string
  role_id?: string | null
  completion_methods?: string[] | null
  allow_google_email_mismatch?: boolean | null
  allowed_email_domains?: string[] | null
}

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
  tenant_configuration_options?: string[] | null
  owner_invite?: TenantOwnerInviteDto | null  // One-call shortcut — see design note below
}

interface CreateTenantDraftResponseDto {
  tenant_id: string
  status: "provisioning"
  next_step: "subscription"
  owner_invite?: {
    user_id: string
    invite_expires_at: string
    delivery_status: "sent" | "failed"
  } | null
}
```

Persistence rule: `company_size_range` is stored on `tenants`; `legal_entity_name`, `registration_number`, `country`, and `currency` are stored on the primary `legal_entities` row (`currency_code`); `timezone` is stored in tenant settings/default timezone.

**Design decision — one-call owner invite shortcut:** The KB provisioning wizard defines owner invite as Step 6 (`POST /admin/v1/tenants/{id}/invite-admin`). As an intentional product shortcut, `POST /admin/v1/tenants` optionally accepts `owner_invite` and orchestrates the invite in the same call. When `owner_invite` is supplied the backend runs the full invite flow (baseline owner role materialised, inactive user created, invite token issued, email sent) within the same database transaction. Email send failure after commit does NOT roll back the tenant draft — the operator can resend via the dedicated invite endpoint. When `owner_invite` is omitted, behaviour is identical to the sequential wizard step. The dedicated `POST /admin/v1/tenants/{id}/invite-admin` endpoint remains available for subsequent or re-sent invites.

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
  company_size_range: string | null
  plan_tier: string
  status: TenantLifecycleStatus
  billing_start_date: string | null
  subscription_override: boolean
  commercial_model: "subscription" | "full_license_maintenance" | null
  subscription_collection_mode: "gateway" | "manual" | null
  license_payment_mode: "manual" | "gateway" | null
  maintenance_collection_mode: "gateway" | "manual" | "waived" | null
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
interface TenantStatusUpdateDto {
  action: "suspend" | "unsuspend" | "activate"
  reason?: string
}

// response: 204 No Content
```

## PATCH `/admin/v1/tenants/{id}/subscription`

```ts
interface SubscriptionOverrideDto {
  plan_code: string
  commercial_model: "subscription" | "full_license_maintenance"
  billing_currency: string
  contract_start_date?: string
  contract_end_date?: string | null
  company_size_range: string
  selected_modules: string[]
  calculated_monthly_price: number
  calculated_annual_price: number
  override_monthly_price?: number | null
  override_annual_price?: number | null
  ai_token_limit_per_month?: number | null

  // Required for commercial_model = "subscription".
  billing_cycle?: "monthly" | "annual"
  billing_start_date?: string  // ISO date
  subscription_collection_mode?: "gateway" | "manual"
  gateway_provider?: "stripe" | "payhere" | "manual_gateway" | string
  gateway_customer_ref?: string | null
  gateway_subscription_ref?: string | null

  // Required for commercial_model = "full_license_maintenance".
  license_payment_mode?: "manual" | "gateway"
  full_license_amount?: number | null
  license_paid_at?: string | null
  license_reference?: string | null

  // Maintenance may still be collected through the payment gateway even when the full license was paid manually.
  maintenance_collection_mode?: "gateway" | "manual" | "waived"
  maintenance_billing_cycle?: "monthly" | "annual" | null
  maintenance_status?: "active" | "due" | "expired" | "waived"
  maintenance_start_date?: string | null
  maintenance_renewal_date?: string | null
  maintenance_rate?: number | null
  maintenance_amount?: number | null

  custom_contract_value?: number | null  // total negotiated contract value when different from plan/module defaults
  discount_percent?: number | null
  reason: string              // required; written to audit log
}
// response: 204 No Content
```

Rules:

- Subscription tenants normally use `subscription_collection_mode = "gateway"` and `gateway_provider` so recurring plan/module fees are charged by the payment gateway.
- `company_size_range` uses the same option set as tenant creation. `selected_modules` plus `company_size_range` must be recalculated from `module_catalog.price_brackets`; the calculated values supplied by the UI are display echoes and the backend remains authoritative.
- `override_monthly_price` and `override_annual_price` are negotiated/effective prices when present. They must not replace `calculated_monthly_price` and `calculated_annual_price` in storage.
- `ai_token_limit_per_month` is required and positive when the selected module set includes an AI capability such as `chat_ai`; it is omitted/null for non-AI plans.
- Full-license tenants can use `license_payment_mode = "manual"` for the one-time license sale. The operator records `full_license_amount`, `license_paid_at`, and `license_reference`.
- Full-license maintenance is separate from the one-time license. It normally uses `maintenance_collection_mode = "gateway"` so recurring maintenance/support fees are collected by the system payment gateway.
- `manual` collection modes are exception paths and require `reason`.

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

## GET `/admin/v1/role-templates`

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
  created_at: string
  updated_at: string | null
}

interface RoleTemplateListQueryDto {
  search?: string
  module_key?: string
  include_inactive?: boolean
}

interface RoleTemplateListResponseDto {
  items: RoleTemplateDto[]
}
```

## POST `/admin/v1/role-templates`

```ts
interface CreateRoleTemplateDto {
  name: string
  description?: string
  module_keys: string[]
  permission_codes: string[]
}

// response: RoleTemplateDto
```

## PATCH `/admin/v1/role-templates/{id}`

```ts
interface UpdateRoleTemplateDto {
  name?: string
  description?: string | null
  module_keys?: string[]
  permission_codes?: string[]
  is_active?: boolean
  reason?: string
}

// response: RoleTemplateDto
```

Applying or editing a role template must validate the permission list against `GET /admin/v1/tenants/{id}/permissions/catalog`.

Operators use global templates for reusable patterns and tenant-specific roles for one-customer needs. Role creation does not require job levels. Job levels only affect scoped permissions, hierarchy, and workflow routing later.

## POST `/admin/v1/tenants/{id}/role-templates/{templateId}/apply`

```ts
interface ApplyRoleTemplateDto {
  role_name_override?: string
  duplicate_name_strategy?: "idempotent" | "fail" | "create_copy"
}

interface ApplyRoleTemplateResponseDto {
  role: TenantRoleDto
  applied_permission_codes: string[]
  skipped_permission_codes: string[]
  validation_errors: Array<{ permission_code: string; message: string }>
}
```

Applying a template creates or updates a normal tenant-scoped role. Permissions outside the tenant's module entitlement boundary must be rejected or returned as explicit validation errors.

## GET `/admin/v1/tenants/{id}/roles`

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

interface TenantRoleListResponseDto {
  items: TenantRoleDto[]
}
```

## POST `/admin/v1/tenants/{id}/roles`

```ts
interface CreateTenantRoleDto {
  name: string
  description?: string
  permission_codes: string[]
}

// response: TenantRoleDto
```

Description is optional. The backend must accept a role with `name` and `permission_codes` only.

## PUT `/admin/v1/tenants/{id}/roles/{roleId}/permissions`

```ts
interface UpdateTenantRolePermissionsDto {
  permission_codes: string[]
  reason?: string
}

interface UpdateTenantRolePermissionsResponseDto {
  role: TenantRoleDto
  added_permission_codes: string[]
  removed_permission_codes: string[]
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
  completion_methods?: Array<"password" | "google">
  allow_google_email_mismatch?: boolean
  allowed_email_domains?: string[]
}
// response
{ user_id: string; invite_expires_at: string }
```

This sends a set-password link. It must not require the operator to choose the tenant owner's final password.

The selected `role_id` must refer to a materialized tenant role that satisfies the minimum owner/admin permission requirement.

The invite email starts the acceptance flow, but account activation happens through tenant-facing Auth APIs:

- `GET /api/v1/auth/invitations/{token}`
- `POST /api/v1/auth/invitations/{token}/accept-password`
- `POST /api/v1/auth/invitations/{token}/accept-google`

Completing the invite with password uses the invited email. Completing the invite with Google can use a different verified Google email only when `allow_google_email_mismatch` and `allowed_email_domains` permit it; otherwise it is rejected and audit-logged.

## GET `/admin/v1/tenants/{id}/provisioning-summary`

```ts
interface ProvisioningSummaryDto {
  tenant_id: string
  status: TenantLifecycleStatus
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
interface ProvisionConfirmRequestDto {
  confirm: true
}

// success response: 204 No Content
// incomplete response: 422 with ProvisioningSummaryDto
```

## Tenant-Facing Role APIs After Activation

These are not Developer Platform provisioning endpoints, but they use the same module-filtered permission boundary. Tenant owners can create and edit only roles inside their own active tenant.

## GET `/api/v1/roles`

```ts
interface TenantAppRoleDto {
  id: string
  name: string
  description: string | null
  is_system: boolean
  permission_codes: string[]
  created_at: string
  updated_at: string
}

interface TenantAppRoleListResponseDto {
  items: TenantAppRoleDto[]
}
```

## POST `/api/v1/roles`

```ts
interface CreateTenantAppRoleDto {
  name: string
  description?: string
  permission_codes: string[]
}

// response: TenantAppRoleDto
```

Description is optional here too. Role creation does not require job levels.

## PUT `/api/v1/roles/{id}`

```ts
interface UpdateTenantAppRoleDto {
  name?: string
  description?: string | null
}

// response: TenantAppRoleDto
```

## PUT `/api/v1/roles/{id}/permissions`

```ts
interface UpdateTenantAppRolePermissionsDto {
  permission_codes: string[]
}

interface UpdateTenantAppRolePermissionsResponseDto {
  role: TenantAppRoleDto
  added_permission_codes: string[]
  removed_permission_codes: string[]
}
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
