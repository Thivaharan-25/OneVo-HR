# Global Policies

## Purpose

Global Policies is a System Config section that manages platform-wide auth and security policy defaults. These are the baseline values that every new tenant's `tenant_auth_policies` row is seeded with on provisioning, and can be propagated to existing tenants through a governed workflow when platform security requirements change.

Global Policies does not manage monitoring defaults, retention defaults, work-hour defaults, or any configuration preset — those are Config Templates applied during provisioning. Global Policies does not manage session TTL, invite expiry, or dunning — those are in System Config.

## What This Module Manages

The six auth/security policy keys are fixed — operators edit their default values, they do not create or delete keys.

| Policy Key | Type | Default | Seeds |
|---|---|---|---|
| `auth.mfa_required_default` | boolean | `false` | `tenant_auth_policies.mfa_required` |
| `auth.google_login_allowed_default` | boolean | `true` | `tenant_auth_policies.google_login_enabled` |
| `auth.password_login_allowed_default` | boolean | `true` | `tenant_auth_policies.password_login_enabled` |
| `auth.google_email_mismatch_allowed_default` | boolean | `false` | `tenant_auth_policies.invite_google_email_mismatch_allowed` |
| `auth.failed_login_lockout_threshold` | integer | `5` | Read by AuthService at login from `system_settings` — not stored per tenant |
| `auth.failed_login_lockout_minutes` | integer | `15` | Read by AuthService at login from `system_settings` — not stored per tenant |

These values seed the `tenant_auth_policies` row created during tenant provisioning. After provisioning, platform operators can view and override per-tenant values from Tenant Management → Policies tab.

**Backend implementation note:** `CreateTenantCommandHandler` currently seeds `TenantAuthPolicy` using C# entity property defaults. It must be updated to read the four `tenant_auth_policies` columns from `system_settings` instead so that changes published here take effect for new tenants. The two lockout keys (`auth.failed_login_lockout_threshold`, `auth.failed_login_lockout_minutes`) require `AuthService` to read from `system_settings` at login time instead of using hardcoded values.

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `system_settings` | Read + write — stores the six policy key definitions and their current published default values |
| `tenant_auth_policies` | Read for impact preview; write on provisioning (new tenants) and on explicit propagation to existing tenants |
| Audit log | Write every publish and propagation event with previous default, new default, reason, and affected tenant count |

## Capabilities

- View all six auth/security policy defaults and their current published values
- Edit a policy's default value (creates a draft — does not take effect until published)
- Preview how many existing tenants would be affected by a publish (tenants whose `tenant_auth_policies` value still matches the current global default and has not been explicitly overridden)
- Publish a policy — updates the platform default; all future tenant provisioning uses the new value immediately; existing tenants are unaffected unless explicitly propagated
- Propagate a published policy to existing tenants — with impact preview acknowledgement, explicit confirmation, and mandatory audit reason
- View policy change history per key

## Navigation

| Route | Permission |
|---|---|
| System Config -> Global Policies | `platform.system_config.read` |
| Edit draft / publish / propagate | `platform.system_config.manage` |

## Key Rules

- The six policy keys are seeded by ONEVO and are always present — operators cannot create or delete keys
- Publishing does NOT auto-propagate to existing tenants — propagation is always a separate explicit action
- Publishing does NOT overwrite existing tenant-specific overrides — only tenants whose value still matches the previous global default are counted as affected
- Propagating to existing tenants requires: impact preview acknowledgement, explicit confirmation, and a mandatory audit reason
- Background propagation is idempotent — re-running does not double-apply
- Every publish and every propagation writes an audit log entry with previous default, new default, reason, and affected tenant count
- Monitoring defaults → Configuration Template Manager (`monitoring_policy` template type)
- Retention defaults, work hours, privacy mode → Configuration Template Manager (`configuration` template type)
- Session TTL, invite expiry, dunning schedule → System Config
- `auth.failed_login_lockout_threshold` and `auth.failed_login_lockout_minutes` take effect immediately on publish across all tenants — no propagation step; AuthService reads these from `system_settings` at login time

## Related

- [[developer-platform/modules/global-policies/end-to-end-logic|Global Policies End-to-End Logic]]
- [[developer-platform/modules/configuration-template-manager/overview|Configuration Template Manager]] — monitoring policy, configuration presets, leave policy, and all other provisioning templates
- [[developer-platform/modules/system-config/overview|System Config]] — session TTL, invite expiry, dunning, and platform infrastructure credentials
- [[developer-platform/modules/tenant-console/overview|Tenant Management]] — Tenant Management → Policies tab shows this tenant's auth policy values that differ from global defaults; platform operators can set per-tenant overrides from there
