# Feature Flags And Feature Gates

## Purpose

Frontend gating mirrors the backend access order. The frontend is only a UX layer; the API remains the security boundary.

The access order is:

```text
active module entitlement
AND commercial feature inclusion
AND runtime feature flag, when one exists
AND user permission
```

## Three Concepts

| Concept | Source | Purpose | Example |
|:--------|:-------|:--------|:--------|
| Module entitlement | `tenant_module_entitlements` | Tenant has access to a product module | `work_management` |
| Commercial feature inclusion | `tenant_subscriptions.selected_feature_keys` | Tenant bought this feature inside a module/package | `work_management.projects` |
| Runtime feature flag | `feature_flags` + tenant overrides | Beta rollout, emergency disable, privacy/AI controls | `monitoring.website_usage` |

Feature flags are not the commercial source of truth. They cannot grant features outside the tenant's plan/custom contract.

## Session Metadata

The backend session response should expose both module and feature metadata:

```ts
interface SessionAuthorizationDto {
  permissions: string[]
  active_modules: string[]
  active_features: string[]
}
```

`active_features` contains feature keys that are commercially included and runtime-enabled. It should not contain feature keys excluded from the tenant's subscription/custom contract, even if a runtime flag is ON.

## Frontend Helpers

```ts
hasModule(moduleKey: string): Signal<boolean>
hasFeature(featureKey: string): Signal<boolean>
hasPermission(permission: string): Signal<boolean>
```

Use module keys for broad navigation sections and feature keys for screens/actions inside a module.

```html
@if (auth.hasModule('work_management')()) {
  <a routerLink="/work">Work</a>
}

@if (auth.hasFeature('work_management.projects')() && auth.hasPermission('projects:read')()) {
  <a routerLink="/work/projects">Projects</a>
}

@if (auth.hasFeature('monitoring.website_usage')() && auth.hasPermission('monitoring:read')()) {
  <app-streaming-chat />
}
```

## Upgrade And Disabled States

When a tenant lacks a module or commercial feature, show an upgrade prompt only where product wants upsell visibility. Do not show controls that imply the user can self-enable a paid feature.

When a runtime flag disables an included feature, show an unavailable/temporarily disabled state only where the user already has the commercial feature.

## Runtime Flag Lifecycle

Use runtime flags only for:

- beta rollout
- risky backend behavior
- AI/provider-dependent features
- privacy-sensitive monitoring features
- emergency disable
- per-tenant temporary support override

Do not create runtime flags for every normal CRUD feature.

Lifecycle:

```text
1. Create flag with default OFF unless the feature is already stable.
2. Enable for internal or beta tenants.
3. Roll out by tenant percentage or explicit tenant overrides.
4. Move to 100% when stable.
5. Remove flag and dead code when it is no longer operationally useful.
```

## Related

- [[frontend/cross-cutting/authorization|Authorization]]
- [[developer-platform/modules/module-catalog-manager/end-to-end-logic|Module Catalog Feature Registry]]
- [[developer-platform/modules/feature-flag-manager/end-to-end-logic|Feature Flag Seed List]]
