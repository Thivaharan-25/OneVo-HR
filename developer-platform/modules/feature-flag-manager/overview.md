# Feature Flag Manager

## Purpose

The Feature Flag Manager controls which features and modules are enabled globally and per tenant. It is the primary tool for rolling out new functionality in a controlled way — from internal testing through GA — and for module-level access configuration.

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `feature_flags` | Read + write — global flag definitions and default values |
| `feature_access_grants` | Read + write — per-tenant flag overrides |
| `module_registry` | Read + write — which modules are active per tenant |

All of these tables live in the **SharedPlatform** layer and affect all OneVo tenants.

## Capabilities

### Global Flag List
- View all feature flags with their current default value and rollout percentage
- Toggle any flag globally (affects all tenants that have no per-tenant override)
- Set rollout percentage for gradual global rollouts

### Per-Flag Detail
- Override the flag's value for a specific tenant, independent of the global default
- View all tenants that have a non-default override for this flag

### Per-Tenant Override View
- Select a tenant and see every flag override active for that tenant in one place
- Add, modify, or remove individual flag overrides

### Module Enable / Disable
- Turn specific OneVo modules on or off for individual tenants
- Writes directly to `module_registry`
- Reflects in what the tenant's users see in their OneVo navigation

### Audit Trail
- Every flag change — global toggle, per-tenant override, or module toggle — is logged with:
  - Developer account that made the change
  - Timestamp
  - Previous and new value

## Notes

- Flag changes take effect without a tenant restart.
- Module disabling via this tool is additive to the provisioning wizard's module selection — modules can be toggled post-provisioning without going through the wizard again.
