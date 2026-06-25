# Tenant Runtime Overrides

## Purpose

Tenant Runtime Overrides are managed from Tenant Management -> Tenant Detail, not from a top-level Feature Flags sidebar item. They control two things that affect one tenant's runtime feature availability:

1. **Feature flags** - boolean switches with global defaults, rollout percentages, and per-tenant overrides that gate specific ONEVO features without requiring a deployment
2. **Module runtime toggles** - enable or disable a specific ONEVO module for a specific tenant post-activation, without touching billing or the subscription record

It is the tenant-context tool for support-driven runtime changes, emergency disables, and controlled rollout for commercially entitled tenants. Global feature flag definition is a technical/admin API concern; Phase 1 does not expose a separate Feature Flags navigation item.

Tenant Runtime Overrides are not the commercial packaging source of truth. If a module has ten features and a paid plan includes only five, that inclusion is defined in Subscription Plans and the tenant subscription snapshot. Module Catalog only defines the possible product surface. Feature flags can only turn an already-included feature on or off at runtime. They must not be used to silently change what the tenant bought or how much the tenant pays.

The authoritative Phase 1 runtime flag seed list is in [[developer-platform/modules/feature-flag-manager/end-to-end-logic|Tenant Runtime Overrides End-to-End Logic]] under "Phase 1 Runtime Flag Seed List". Do not create runtime flags for every normal CRUD feature.

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `feature_flags` | Read-only in Tenant Runtime Overrides; global flag definitions, default values, and rollout percentages are managed from System Config -> Runtime Flags |
| `feature_flag_overrides` | Read + write - per-tenant flag overrides |
| `tenant_module_entitlements` | Write `runtime_override` - module enable/disable without changing commercial state |
| Commercial plan feature inclusion | Read-only validation - confirms the tenant bought the module feature before a flag can grant runtime access |
| `tenant_integration_credentials` | Write `status = 'disabled'` when a connected integration's linked module (via `module_integration_links`) is disabled |
| Audit log | Write every flag change, override, and module toggle |

## Capabilities

### Feature Flag Definitions
These are backend definitions, not a top-level sidebar workflow. Operators normally interact with them from Tenant Detail when setting tenant-specific runtime overrides.
- Tenant Runtime Overrides can read flag definitions to show available overrides for a tenant.
- Tenant Runtime Overrides must not create, edit, deactivate, or change rollout settings for global flag definitions.
- Global runtime flag definition management, if exposed, belongs in System Config -> Runtime Flags and requires `platform.runtime_flags.read` / `platform.runtime_flags.manage`.
- Rollout is deterministic: `hash(tenant_id + flag_key) % 100 < rollout_pct`; the same tenant always gets the same result.

### Per-Tenant Flag Overrides
- Force a specific tenant ON or OFF regardless of global default and rollout percentage
- Remove override to let the tenant fall back to global evaluation
- All overrides require a reason and are audit-logged
- Overrides cannot grant access to a feature that is not included in the tenant's commercial plan or custom contract
- Override ON is rejected when the feature key is absent from `tenant_subscriptions.selected_feature_keys`

### Module Runtime Enable/Disable
- Toggle a module ON or OFF for a specific tenant after activation
- Does NOT change the tenant's subscription, billing, or `sales_state` - runtime only
- When a module is disabled, connected integrations linked to that module are set to `disabled` status (not disconnected - re-enabling the module restores them automatically)
- Confirmation dialog shows which integrations will be affected before confirming
- Separate from commercial module enable/disable (which goes through Tenant Management -> Subscriptions)

## Navigation

| Route | Permission |
|---|---|
| Tenant Detail -> Runtime Overrides | `platform.tenants.feature_overrides.read` |
| Set / clear tenant override | `platform.tenants.feature_overrides.manage` |

## Key Rules

- Flag keys are permanent - cannot change after any tenant has a value set
- Per-tenant override wins unconditionally over global default and rollout %
- Commercial feature inclusion is checked before runtime flags. A feature is available only when the tenant has the module entitlement, the tenant subscription snapshot includes the feature key, and the runtime flag evaluates to enabled.
- Disabling features by flag does not reduce price. Pricing changes require Subscription Plans or Tenant Management subscription override.
- Phase 2 flags cannot be enabled for Phase 1-only tenants
- Module runtime disable does not affect billing; commercial module changes require Subscription Plans
- Integration disconnect on module disable is reversible - re-enabling restores `connected` status automatically
- Every tenant override or module runtime toggle is audit-logged with reason

## Related

- [[developer-platform/modules/feature-flag-manager/end-to-end-logic|Tenant Runtime Overrides End-to-End Logic]]
- [[developer-platform/modules/module-catalog-manager/overview|Module Catalog Manager]] - integration linking
- [[developer-platform/modules/tenant-console/overview|Tenant Management]] - commercial module changes
