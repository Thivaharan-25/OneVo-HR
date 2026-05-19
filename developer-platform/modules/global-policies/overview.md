# Global Policies

## Purpose

Global Policies manages platform-wide policy defaults. These are operator-controlled baselines that determine the starting configuration for new tenants and can be selectively pushed to existing tenants through a reviewed propagation workflow.

It is not a replacement for per-tenant settings — those are managed in Tenant Console → Settings and System Config → Per-Tenant Overrides. Global Policies defines the platform baseline that tenant-specific overrides are measured against.

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `global_policies` / `system_settings` | Read + write — policy definitions and default values |
| `tenant_settings` | Read for impact preview; write only through explicit propagation (does not overwrite tenant overrides) |
| Audit log | Write every policy change with old/new values and reason |

## Capabilities

- Create and edit platform policy defaults (session limits, security baselines, retention defaults, monitoring defaults, provisioning defaults)
- Preview how many tenants would be affected by publishing a policy change
- Publish policy — applies new default to all future tenants; existing tenants unaffected unless explicitly propagated
- Propagate a published policy to existing tenants — with impact confirmation, preview count, and mandatory audit reason
- View policy change history

## Navigation

| Route | Permission |
|---|---|
| `/platform/global-policies` | `platform.policies.read` |
| Create / update / publish | `platform.policies.manage` |

## Key Rules

- Publishing a policy does NOT overwrite existing tenant-specific overrides — only tenants with no override for that setting are affected
- Propagating to existing tenants requires: impact preview acknowledgement, explicit confirmation, and an audit reason
- Background propagation is idempotent — re-running does not double-apply the change
- Every publish writes an audit log entry with previous default, new default, reason, and affected tenant count

## Related

- [[developer-platform/modules/global-policies/end-to-end-logic|Global Policies End-to-End Logic]]
- [[developer-platform/modules/system-config/overview|System Config]] — per-tenant setting overrides
- [[developer-platform/modules/data-retention/overview|Data Retention]] — retention-specific policies
