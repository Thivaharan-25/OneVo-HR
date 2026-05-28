# Feature Flag Manager

## Purpose

Feature Flag Manager controls two things that affect tenant feature availability at runtime:

1. **Feature flags** — boolean switches with global defaults, rollout percentages, and per-tenant overrides that gate specific ONEVO features without requiring a deployment
2. **Module runtime toggles** — enable or disable a specific ONEVO module for a specific tenant post-activation, without touching billing or the subscription record

It is the tool for gradual rollouts, beta access grants, emergency disables, and support-driven temporary access changes.

Feature Flag Manager is not the commercial packaging source of truth. If a module has ten features and a paid plan includes only five, that inclusion is defined in Module Catalog / Subscription Manager as plan feature inclusion. Feature flags can only turn an already-included feature on or off at runtime. They must not be used to silently change what the tenant bought or how much the tenant pays.

The authoritative Phase 1 runtime flag seed list is in [[developer-platform/modules/feature-flag-manager/end-to-end-logic|Feature Flag Manager End-to-End Logic]] under "Phase 1 Runtime Flag Seed List". Do not create runtime flags for every normal CRUD feature.

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `feature_flags` | Read + write — global flag definitions, default values, rollout percentages |
| `feature_flag_overrides` | Read + write - per-tenant flag overrides |
| `tenant_module_entitlements` | Write `runtime_override` — module enable/disable without changing commercial state |
| Commercial plan feature inclusion | Read-only validation — confirms the tenant bought the module feature before a flag can grant runtime access |
| `tenant_integration_credentials` | Write `status = 'disabled'` when connected integration's required module is disabled |
| Audit log | Write every flag change, override, and module toggle |

## Capabilities

### Global Feature Flags
- Create feature flags with machine-readable key (format: `{module_key}.{feature_name}`), default value (ON/OFF), rollout percentage, owning module, and phase
- Toggle global default — affects all tenants without an explicit override
- Set rollout percentage: when default = ON, percentage controls what fraction of tenants actually get ON via a deterministic hash. 0% = effectively off for all. 100% = on for all.
- Rollout is deterministic: `hash(tenant_id + flag_key) % 100 < rollout_pct` — same tenant always gets the same result

### Per-Tenant Flag Overrides
- Force a specific tenant ON or OFF regardless of global default and rollout percentage
- Remove override to let the tenant fall back to global evaluation
- All overrides require a reason and are audit-logged
- Overrides cannot grant access to a feature that is not included in the tenant's commercial plan or custom contract

### Module Runtime Enable/Disable
- Toggle a module ON or OFF for a specific tenant after activation
- Does NOT change the tenant's subscription, billing, or `sales_state` — runtime only
- When a module is disabled, connected integrations linked to that module are set to `disabled` status (not disconnected — re-enabling the module restores them automatically)
- Confirmation dialog shows which integrations will be affected before confirming
- Separate from commercial module enable/disable (which goes through Tenant Console → Subscriptions)

## Navigation

| Route | Permission |
|---|---|
| `/platform/feature-flags` | `platform.feature_flags.read` |
| Write operations | `platform.feature_flags.manage` |

## Key Rules

- Flag keys are permanent — cannot change after any tenant has a value set
- Per-tenant override wins unconditionally over global default and rollout %
- Commercial feature inclusion is checked before runtime flags. A feature is available only when the tenant has the module entitlement, the plan/custom contract includes the feature, and the runtime flag evaluates to enabled.
- Disabling features by flag does not reduce price. Pricing changes require Subscription Manager or Tenant Console subscription override.
- Phase 2 flags cannot be enabled for Phase 1-only tenants
- Module runtime disable does not affect billing; commercial module changes require Subscription Manager
- Integration disconnect on module disable is reversible — re-enabling restores `connected` status automatically
- Every change (flag create, default toggle, override set/remove, module toggle) is audit-logged with reason

## Related

- [[developer-platform/modules/feature-flag-manager/end-to-end-logic|Feature Flag Manager End-to-End Logic]]
- [[developer-platform/modules/module-catalog-manager/overview|Module Catalog Manager]] — integration linking
- [[developer-platform/modules/tenant-console/overview|Tenant Console]] — commercial module changes
