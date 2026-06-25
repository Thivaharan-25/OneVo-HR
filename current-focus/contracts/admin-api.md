# Contract: Developer Platform Admin API

**Backend owner:** DEV1 Tasks 7-9, DEV4 Task 8  
**Consumers:** DEV5 Tasks 5-7  
**Canonical source:** `ONEVO.Api` admin surface (`/admin/v1/*`). Phase 1 has one backend deployment; no separate admin backend service is deployed.

**Provisioning API count:** Phase 1 tenant provisioning requires 23 admin endpoints: plan catalog, module catalog, country defaults, tenant validation, tenant list/create/detail/edit/status, subscription, modules, permission catalog, role template list/create/edit/apply, tenant role list/create/permission update, settings, invite admin, provisioning summary, and first-invoice generation. Tenant-facing role management after activation is separate under `/api/v1/roles`.

**Catalog cost-management APIs:** reusable plan prices are calculated from selected package/module price brackets and company-size ranges. Reusable package/module price brackets are managed through catalog admin endpoints. Tenant provisioning can override calculated prices per tenant, but base catalog prices need their own APIs.

**Backend API data rule:** every DTO below is the backend JSON contract between `ONEVO.Api` and the Developer Console. Field names are API response/request fields, not just UI labels. Frontend state may add view-only fields, but it must not rename or invent backend contract fields without updating this file.

```ts
type TenantLifecycleStatus = "provisioning" | "trial" | "trial_expired" | "pending_payment" | "active" | "suspended" | "cancelled"
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

Plans are reusable catalog records. Operators select or allow one plan for a tenant; tenant-specific pricing, discounts, selected optional add-ons, selected resource-only add-ons, shared resource limits, resolved payment gateway config, and unpaid dues are stored on the tenant subscription/commercial record.

```ts
interface SubscriptionPlanDto {
  id: string
  code: "starter" | "professional" | "enterprise" | string
  name: string
  tier: string
  included_modules: string[]
  included_feature_keys: Record<string, string[]>
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

`effective_*_price` is derived as `override_*_price ?? calculated_*_price`. The backend calculates `calculated_*_price` from `module_catalog.price_brackets` for `included_modules` and `company_size_range`. `included_feature_keys` is the commercial feature package inside those modules. A module can be included in a plan without including every feature key registered under that module in Module Catalog.

## POST `/admin/v1/subscription-plans`

Creates a reusable plan catalog record. Operators should use this only when ONEVO wants a plan reusable across tenants, not for one customer deal. The backend calculates plan prices from selected packages/modules and company-size range; request override fields are optional negotiated catalog-level overrides.

```ts
interface CreateSubscriptionPlanDto {
  code: string
  name: string
  tier: string
  included_modules: string[]
  included_feature_keys: Record<string, string[]>
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

Updates reusable plan metadata, included modules, included feature keys, and base prices. Existing tenant subscriptions keep their stored commercial terms unless product explicitly runs a migration/reprice operation. Adding a feature key to Module Catalog or to a reusable plan must not silently rewrite existing tenant subscription snapshots.

```ts
interface UpdateSubscriptionPlanDto {
  name?: string
  tier?: string
  included_modules?: string[]
  included_feature_keys?: Record<string, string[]>
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
  pillar: "hr" | "monitoring" | "worksync" | "shared" | string
  phase: "phase_1" | "phase_2" | "future" | string
  pricing_unit: "per_employee" | "per_device" | "flat" | "custom"
  pricing_references: ModulePriceReferenceDto[]
  storage_references: ModuleStorageReferenceDto[]
  ai_token_references: ModuleAiTokenReferenceDto[]
  is_active: boolean
}

interface ModulePriceReferenceDto {
  min_employees: number
  max_employees: number       // -1 means unlimited
  monthly_price: number
  annual_price: number
}

interface ModuleStorageReferenceDto {
  min_employees: number
  max_employees: number
  storage_gb: number
}

interface ModuleAiTokenReferenceDto {
  min_employees: number
  max_employees: number
  tokens_per_month: number
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
  pillar: "hr" | "monitoring" | "worksync" | "shared" | string
  phase: "phase_1" | "phase_2" | "future" | string
  pricing_unit: "per_employee" | "per_device" | "flat" | "custom"
  pricing_references?: ModulePriceReferenceDto[]
  storage_references?: ModuleStorageReferenceDto[]
  ai_token_references?: ModuleAiTokenReferenceDto[]
  is_active?: boolean
}

// response: ModuleCatalogItemDto
```

## PATCH `/admin/v1/modules/catalog/{moduleKey}`

Updates reusable module metadata and reference values. Existing tenant entitlements and tenant subscriptions keep their stored pricing snapshots unless product explicitly runs a migration/reprice operation.

```ts
interface UpdateModuleCatalogItemDto {
  name?: string
  pillar?: "hr" | "monitoring" | "worksync" | "shared" | string
  phase?: "phase_1" | "phase_2" | "future" | string
  pricing_unit?: "per_employee" | "per_device" | "flat" | "custom"
  pricing_references?: ModulePriceReferenceDto[]
  storage_references?: ModuleStorageReferenceDto[]
  ai_token_references?: ModuleAiTokenReferenceDto[]
  is_active?: boolean
  reason: string
}

// response: ModuleCatalogItemDto
```

## GET `/admin/v1/payment-gateways`

Lists safe gateway metadata for Stripe, Paddle, and PayHere. Secrets are never returned. Country routing is returned as country codes resolved from `payment_gateway_country_routes`.

```ts
interface PaymentGatewayConfigDto {
  id: string
  provider: "stripe" | "paddle" | "payhere"
  environment: "sandbox" | "production"
  display_name: string
  logo_url?: string | null
  public_key?: string | null
  merchant_id?: string | null
  webhook_url: string
  country_codes: string[]
  has_active_credentials: boolean
  is_active: boolean
  created_at: string
  updated_at: string | null
}

interface PaymentGatewayConfigListResponseDto {
  items: PaymentGatewayConfigDto[]
}
```

## POST `/admin/v1/payment-gateways`

Creates gateway metadata, stores encrypted credentials as a new `payment_gateway_credentials` row, and creates country routes. Secret fields are accepted only in the request body and are never returned.

```ts
interface CreatePaymentGatewayConfigDto {
  provider: "stripe" | "paddle" | "payhere"
  environment: "sandbox" | "production"
  display_name: string
  logo_url?: string | null
  public_key?: string | null
  merchant_id?: string | null
  webhook_url: string
  country_codes: string[]
  credentials: {
    secret: string
    webhook_secret?: string | null
  }
  is_active?: boolean
}

// response: PaymentGatewayConfigDto
```

## PATCH `/admin/v1/payment-gateways/{id}`

Updates safe metadata, country routes, and optionally creates a new active credential version. Existing credential rows are deactivated; they are not overwritten.

```ts
interface UpdatePaymentGatewayConfigDto {
  display_name?: string
  logo_url?: string | null
  public_key?: string | null
  merchant_id?: string | null
  webhook_url?: string
  country_codes?: string[]
  credentials?: {
    secret: string
    webhook_secret?: string | null
  }
  is_active?: boolean
  reason: string
}

// response: PaymentGatewayConfigDto
```

## GET `/admin/v1/payment-gateways/resolve?country={countryCode}`

Resolves the active gateway for a country and environment from `payment_gateway_country_routes`.

```ts
interface PaymentGatewayResolveResponseDto {
  country_code: string
  gateway_config: PaymentGatewayConfigDto | null
}
```

## GET `/admin/v1/reference/countries/{countryCode}/defaults`

Reference endpoint used by tenant profile setup after the operator selects a country. The response supplies default timezone and currency choices for the tenant profile. These values are profile data and must not create or update legal entities.

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

Rule: single-timezone countries may auto-fill timezone. Multi-timezone countries must return all supported choices so the frontend can require operator selection.

## GET `/admin/v1/tenants/validate`

Used by the wizard before or during draft creation.

```ts
interface TenantValidationQuery {
  slug?: string
  company_name?: string
  email_domain?: string
  primary_contact_email?: string
  registration_profile_name?: string
  registration_number?: string
  country_code?: string
  timezone?: string
  currency_code?: string
}

interface TenantValidationResponseDto {
  valid: boolean
  conflicts: Array<{
    field: "slug" | "company_name" | "email_domain" | "primary_contact_email" | "registration_profile_name" | "registration_number" | "country_code" | "timezone" | "currency_code"
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
  primary_contact_email: string
  country_code: string
  industry_profile: string
  registration_profile_name: string
  registration_number?: string | null
  company_size_range?: string | null
  timezone: string
  currency_code: string
}

interface CreateTenantDraftResponseDto {
  tenant_id: string
  status: "provisioning"
  next_step: "subscription"
}
```

Persistence rule: company name, slug, primary contact email, country, industry, registration/profile name, registration number, company size, timezone, and currency are stored as tenant profile/provisioning data. Tenant draft creation does not create deprecated registration-profile records. First-payment activation/setup seeding creates the primary legal entity.

**Invite rule:** `POST /admin/v1/tenants` must not send the tenant owner invitation. The dedicated `POST /admin/v1/tenants/{id}/invite-admin` endpoint is the explicit send action.

## GET `/admin/v1/tenants/{id}`

```ts
interface TenantDetailDto {
  id: string
  company_name: string
  slug: string
  primary_contact_email: string
  country_code: string
  industry_profile: string
  registration_profile_name: string
  registration_number: string | null
  company_size_range: string | null
  timezone: string
  currency_code: string
  plan_tier: string
  status: TenantLifecycleStatus
  billing_start_date: string | null
  subscription_override: boolean
  billing_cycle: "monthly" | "annual" | null
  selected_addon_count: number
  unpaid_seat_dues_amount: number
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
  primary_contact_email?: string
  country_code?: string
  industry_profile?: string
  registration_profile_name?: string
  registration_number?: string | null
  company_size_range?: string | null
  timezone?: string
  currency_code?: string
}
// response: 204 No Content
```

## PATCH `/admin/v1/tenants/{id}/status`

```ts
interface TenantStatusUpdateDto {
  action: "suspend" | "unsuspend" | "cancel"
  reason?: string
}

// response: 204 No Content
```

## PATCH `/admin/v1/tenants/{id}/subscription`

```ts
interface SubscriptionOverrideDto {
  plan_code: string
  billing_currency: string
  contract_start_date?: string
  contract_end_date?: string | null
  company_size_range: string
  selected_base_modules: string[]
  selected_addon_modules: string[]
  selected_resource_addons: Array<{ addon_id: string; quantity: number }>
  selected_feature_keys: Record<string, string[]>
  calculated_monthly_price: number
  calculated_annual_price: number
  override_monthly_price?: number | null
  override_annual_price?: number | null
  annual_price_override?: number | null
  annual_discount_percent?: number | null
  ai_token_limit_per_month?: number | null
  tenant_storage_limit_gb?: number | null
  unpaid_seat_dues_amount?: number

  billing_cycle?: "monthly" | "annual"
  billing_start_date?: string  // ISO date
  discount_percent?: number | null
  reason: string              // required; written to audit log
}
// response: 204 No Content
```

Rules:

- `company_size_range` uses the same option set as tenant creation. `selected_base_modules`, `selected_addon_modules`, `selected_resource_addons`, selected feature keys, and company size must be validated against Subscription Plans and Module Catalog. The backend remains authoritative for price and resource calculation.
- `selected_feature_keys` is the tenant's commercial feature snapshot. Runtime feature flags cannot add keys that are absent from this object.
- Resource-only add-ons affect shared limits such as storage or AI tokens only. They must not create module entitlements or add `selected_feature_keys`.
- `override_monthly_price` and `override_annual_price` are negotiated/effective prices when present. They must not replace `calculated_monthly_price` and `calculated_annual_price` in storage.
- `ai_token_limit_per_month` is the resolved shared tenant AI allowance.
- `tenant_storage_limit_gb` is the resolved shared tenant storage pool.
- Unpaid seat dues block cancellation and renewal changes.
- Gateway payment references are handled by invoice/payment APIs where applicable.

## PUT `/admin/v1/tenants/{id}/modules`

```ts
interface TenantModuleSelectionDto {
  modules: Array<{
    module_key: string
    enabled: boolean
    sales_state: "available" | "trial" | "quoted" | "purchased" | "subscription_included" | "disabled"
    pricing_model?: "subscription" | "addon" | "trial" | "custom"
    price?: number | null
    currency?: string | null
    starts_at?: string | null
    ends_at?: string | null
  }>
}
// response: 204 No Content
```

`available` and `quoted` are commercial pipeline states and do not grant tenant-facing access. Active module access is granted by `purchased`, `trial`, or `subscription_included`, unless the entitlement has expired.

## GET `/admin/v1/tenants/{id}/permissions/catalog`

```ts
interface TenantPermissionCatalogDto {
  tenant_id: string
  enabled_modules: string[]
  enabled_features: string[]
  modules: Array<{
    module_key: string
    display_name: string
    included_feature_keys: string[]
    permissions: Array<{
      id: string
      code: string
      description: string
      is_universal: boolean
    }>
  }>
}
```

Only permissions from enabled tenant modules plus universal permissions are returned. If a permission is bound to a feature key, that feature key must be present in `enabled_features`; otherwise the permission is excluded.

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
  time_off_policy_defaults?: {
    annual_time_off_accrual_method?: "monthly" | "annual" | "manual"
    carry_over_cap_days?: number | null
  }
  module_settings?: Record<string, unknown>
}
// response: 204 No Content
```

## GET `/admin/v1/setup-services`

Loads reusable setup services that ONEVO can configure during tenant provisioning. Every setup service is linked to one or more module keys. Free/global services are still module-connected; they are auto-added for tenants with matching entitled modules and must not create billing.

```ts
interface SetupServiceDto {
  id: string
  service_key: string
  name: string
  description: string | null
  module_keys: string[]
  applies_to_all_entitled_modules: boolean
  is_free: boolean
  price: number | null
  currency: string | null
  is_active: boolean
}

interface SetupServiceListQueryDto {
  module_keys?: string[]
  include_inactive?: boolean
}

interface SetupServiceListResponseDto {
  items: SetupServiceDto[]
}
```

## PUT `/admin/v1/tenants/{id}/setup-services`

Stores the tenant setup-service checklist for module-connected free/global and paid services.

```ts
interface TenantSetupServiceSelectionDto {
  setup_service_id: string
  module_key: string
  status: "needed" | "in_progress" | "configured" | "waived" | "cancelled"
  is_billable: boolean
  price?: number | null
  currency?: string | null
  notes?: string | null
}

interface UpdateTenantSetupServicesDto {
  services: TenantSetupServiceSelectionDto[]
}

// response: 204 No Content
```

Rules:

- `module_key` must be one of the tenant's entitled modules and one of the setup service's linked module keys.
- Free/global services are saved with `is_billable = false`.
- Paid services require explicit operator selection and are tracked for billing/evidence outside RBAC.

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
    setup_services: ProvisioningSectionStatus
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

First-invoice generation is allowed only after tenant profile, subscription/commercial terms, module selection, role templates, required settings/templates, and required setup services are complete. Owner invitation is an explicit action and must not be sent implicitly. This action sets the tenant to `pending_payment` and keeps module entitlements non-active/payment-limited until first payment succeeds.

```ts
interface ProvisionConfirmRequestDto {
  confirm: true
}

// success response: { tenant_id: string; status: "pending_payment"; first_invoice_id: string; invoice_url: string }
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
  module_key: string
  feature_key: string | null
  global_default: boolean
  rollout_percentage: number
  tenant_override_count: number
  is_active: boolean
}
```

## POST `/admin/v1/feature-flags`

```ts
interface CreateFeatureFlagRequest {
  key: string
  description: string
  module_key: string | null   // required for tenant-facing product flags; null only for platform operational flags
  feature_key: string | null  // required for tenant-facing product flags; null only for platform operational flags
  default_value: boolean
  rollout_percentage: number
  is_active: boolean
}
```

## GET `/admin/v1/feature-flags/{flagKey}`

```ts
interface FeatureFlagDetailDto extends FeatureFlagListItemDto {
  tenant_overrides: FeatureFlagTenantOverrideDto[]
}

interface FeatureFlagTenantOverrideDto {
  tenant_id: string
  tenant_name: string
  value: boolean
  granted_by_id: string
  granted_at: string
  reason: string | null
}
```

## PATCH `/admin/v1/feature-flags/{flagKey}`

```ts
interface UpdateFeatureFlagRequest {
  description?: string
  module_key?: string | null
  feature_key?: string | null
  default_value?: boolean
  rollout_percentage?: number
  is_active?: boolean
  reason?: string
}
```

Tenant-facing product flags must provide both `module_key` and `feature_key`. The `feature_key` must exist in `module_features` and belong to the selected `module_key`. Only platform operational flags that are not sold as tenant features may set both fields to null.

## DELETE `/admin/v1/feature-flags/{flagKey}`

Soft-deactivates the flag by setting `is_active = false`. Evaluation returns `false` for inactive flags.

## GET `/admin/v1/feature-flags/tenant-overrides`

Returns `FeatureFlagTenantOverrideDto[]`.

## GET `/admin/v1/tenants/{id}/feature-flags`

```ts
interface TenantFeatureFlagValueDto {
  key: string
  module_key: string
  feature_key: string | null
  effective_value: boolean
  source: "inactive" | "override" | "default" | "rollout" | "commercially_unavailable"
  override_value: boolean | null
}
```

## PUT `/admin/v1/tenants/{id}/feature-flags`

```ts
interface ReplaceTenantFeatureFlagOverridesRequest {
  overrides: Record<string, boolean>
  reason: string
}
```

## PATCH `/admin/v1/tenants/{id}/feature-flags/{flagKey}`

```ts
interface SetTenantFeatureFlagOverrideRequest {
  value: boolean
  reason: string
}
```

## DELETE `/admin/v1/tenants/{id}/feature-flags/{flagKey}`

Removes the tenant override. The tenant returns to global default plus rollout evaluation.

## GET `/admin/v1/tenants/{id}/modules/runtime-status`

```ts
interface TenantModuleRuntimeStatusDto {
  module_key: string
  sales_state: string
  commercially_entitled: boolean
  runtime_override: boolean | null
  runtime_enabled: boolean
}
```

## PATCH `/admin/v1/tenants/{id}/modules/{moduleKey}/runtime-status`

```ts
interface SetTenantModuleRuntimeStatusRequest {
  enabled: boolean
  reason: string
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
- Provisioning and pending-payment tenants (`status: "provisioning"` or `"pending_payment"`) are visible here but excluded from `/api/v1/*`


