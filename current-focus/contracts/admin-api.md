# Contract: Developer Platform Admin API

**Backend owner:** DEV1 Tasks 7-9, DEV4 Task 8  
**Consumers:** DEV5 Tasks 5-7  
**Canonical source:** `ONEVO.Admin.Api` (authoritative once built)

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
  billing_start_date: string  // ISO date
  reason: string              // required; written to audit log
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

