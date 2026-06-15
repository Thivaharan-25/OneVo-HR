# Feature Flags - End-to-End Logic

**Module:** Shared Platform
**Feature:** Feature Flags

---

## Check Feature Flag

Feature flag checks never bypass commercial entitlement.

Tenant-facing product feature flags must be linked to a real module feature: `module_key` and `feature_key` are required, and `feature_key` must belong to `module_key`. Platform operational flags that are not sold as tenant features may omit both fields.

```text
Internal call from any module:
  -> IFeatureFlagService.IsEnabledAsync(flagKey, tenantId, ct)
    -> 1. Load flag definition by key
    -> 2. If feature_flags.is_active = false, return false
    -> 3. If flag has module_key, validate tenant has active module entitlement and runtime_override is not false
    -> 4. If flag has feature_key, validate tenant subscription/custom contract includes that feature key
    -> 5. Check per-tenant override
    -> 6. If no override, evaluate default_value + rollout_percentage
    -> 7. Cache result briefly by tenant + flag key
    -> Return true/false
```

## Toggle Feature Flag

Tenant-facing APIs do not toggle flags. Developer Platform admin APIs manage global defaults and tenant overrides.

```text
PATCH /admin/v1/feature-flags/{flagKey}
  -> requires platform.runtime_flags.manage
  -> update default_value / rollout_percentage / description
  -> invalidate tenant flag cache

PATCH /admin/v1/tenants/{id}/feature-flags/{flagKey}
  -> requires platform.tenants.feature_overrides.manage
  -> validate tenant has module entitlement and commercial feature inclusion before allowing value = true
  -> set per-tenant override
  -> invalidate tenant flag cache

DELETE /admin/v1/tenants/{id}/feature-flags/{flagKey}
  -> requires platform.tenants.feature_overrides.manage
  -> remove per-tenant override
  -> invalidate tenant flag cache
```

## Related

- [[developer-platform/modules/feature-flag-manager/end-to-end-logic|Developer Platform Feature Flag Logic]]
- [[frontend/cross-cutting/feature-flags|Frontend Feature Flags]]
