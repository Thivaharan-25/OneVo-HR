# Feature Flags

**Module:** Shared Platform
**Feature:** Feature Flags

---

## Purpose

Feature flags are runtime controls for features that are already commercially included for a tenant. They support gradual rollout, per-tenant overrides, beta access, and emergency disable.

They are not the source of truth for what the tenant bought. Commercial feature inclusion comes from Module Catalog and the current tenant subscription/custom contract.

## Database Tables

### `feature_flags`

Global flag definitions. Key fields:

- `key`
- `module_key`
- `feature_key`
- `default_value`
- `rollout_percentage`
- `is_active`

### `feature_flag_overrides`

Per-tenant runtime overrides for a flag. An override is evaluated only after module entitlement and commercial feature inclusion pass.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/feature-flags` | Authenticated | Active runtime flags for the current tenant/session |

## Related

- [[developer-platform/modules/feature-flag-manager/overview|Developer Platform Tenant Runtime Overrides]]
- [[developer-platform/modules/module-catalog-manager/end-to-end-logic|Module Catalog Feature Registry]]
- [[frontend/cross-cutting/feature-flags|Frontend Feature Flags]]
- [[modules/shared-platform/overview|Shared Platform Module]]
