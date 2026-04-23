# System Config

## Purpose

System Config manages platform-wide default settings and provides direct configuration override capability for individual tenants. It is the escalation tool for support engineers who need to adjust a tenant's settings without involving the tenant's own admin users.

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `tenant_settings` | Read + write — global defaults and per-tenant overrides |
| `monitoring_feature_toggles` | Read + write — global defaults for monitoring toggles |
| `integration_connections` | Read — global connection health view |

## Capabilities

### Global Default Management
- View and edit the default values that are applied to every new tenant created on the platform
- Defaults cover:
  - `tenant_settings` (e.g., monitoring mode, leave policy defaults, transparency mode)
  - `monitoring_feature_toggles` (e.g., screenshot capture enabled, activity scoring enabled)
- Changes to global defaults only affect new tenants provisioned after the change; existing tenants retain their current values

### Per-Tenant Settings Override
- Select any existing tenant and override individual settings without the tenant admin's involvement
- Intended for support escalations where the tenant cannot or should not make the change themselves
- Examples: disabling a feature causing a support incident, correcting a misconfigured policy

### Integration Connection Health
- Read-only view of `integration_connections` across all tenants
- Identify tenants with broken or degraded integration connections (e.g., HRIS sync, calendar integrations)

## Notes

- Per-tenant overrides made through this module are visible to the tenant's own admin in their settings UI — changes are not hidden from tenants.
- All setting writes are audit-logged with the developer account, tenant, field changed, and old/new values.
- Global default changes should be coordinated with the product team, as they affect all future tenant onboarding.
