# Authorization - End-to-End Logic

**Module:** Auth
**Feature:** Authorization

---

## Permission Check

Every tenant-facing protected endpoint must evaluate access in this order:

```text
Any protected API endpoint
  -> [RequirePermission("module:action")]
    -> Authorization pipeline
      -> 1. Resolve current user and tenant from backend-held session/JWT
      -> 2. Resolve required permission metadata:
            - permission code
            - owning module_key
            - optional feature_key
      -> 3. Check module entitlement:
            - tenant_module_entitlements must grant active/trial/purchased/subscription_included/maintenance_included access
            - disabled, available, quoted, expired modules do not grant access
      -> 4. If permission has feature_key:
            - current tenant_subscriptions.selected_feature_keys must include it
            - if a runtime feature flag exists for the feature_key, it must evaluate enabled for this tenant
      -> 5. Check effective permission code for the user
      -> 6. Apply hierarchy/access-policy scope for employee-data reads/writes
      -> 7. Continue to controller/action
```

Platform Super Admin is separate from Tenant Super Admin. Platform Super Admin can operate on Developer Platform `/admin/v1/*` routes only. Platform bypass must never leak into tenant-facing `/api/v1/*` routes.

Tenant Super Admin may receive every permission inside enabled tenant modules, but never bypasses disabled, unpurchased, or commercially excluded features.

## Resolve Effective Permissions

```text
User logs in or refreshes session
  -> AuthSessionService.RefreshPermissionSnapshotAsync(userId, tenantId, ct)
    -> PermissionResolver.ResolveAsync(userId, tenantId, ct)
      -> 1. Resolve tenant active modules from tenant_module_entitlements
      -> 2. Resolve current selected_feature_keys from tenant_subscriptions
      -> 3. Resolve runtime feature flag values for selected feature keys
      -> 4. Start with universal auto-grants
      -> 5. If user is tenant owner / Tenant Super Admin:
            add all permissions whose module is active and whose feature_key, if any, is included + runtime-enabled
      -> 6. Add permission codes from active roles
      -> 7. Apply valid user_permission_overrides:
            grant adds permission
            revoke removes permission
      -> 8. Filter final set:
            keep universal permissions
            keep module permissions only when module is active
            keep feature-bound permissions only when feature is commercially included and runtime-enabled
      -> 9. Apply feature_access_grants only as role/employee visibility filtering inside the already-valid boundary
      -> 10. Return final List<string>
```

Do not use raw `*` as an unrestricted tenant-user shortcut. If a wildcard is retained for implementation convenience, it must mean "all permissions from active tenant modules and included/runtime-enabled feature keys." Only platform-admin routes may use platform-wide bypass behavior.

## Grant Role/Employee Feature Visibility

`feature_access_grants` is optional role/employee visibility inside the commercial boundary. It cannot create commercial access.

```text
POST /api/v1/feature-access
  -> Requires roles:manage
  -> FeatureAccessService.GrantAsync(command, ct)
    -> 1. Validate grantee exists
    -> 2. Validate module_key exists
    -> 3. Validate tenant has active module entitlement
    -> 4. If feature_key is provided:
          validate feature_key belongs to the module
          validate current tenant subscription/custom contract includes feature_key
          validate runtime flag is not hard-disabled for the tenant
    -> 5. Validate caller may manage permissions for that module/feature
    -> 6. Upsert feature_access_grants
    -> 7. Invalidate affected permission snapshots
    -> 8. Audit log: feature_access.granted or feature_access.revoked
```

## Permission Override

```text
POST /api/v1/users/{id}/permission-overrides
  -> Requires roles:manage
  -> PermissionOverrideService.SetAsync(userId, command, ct)
    -> 1. Validate employee belongs to tenant
    -> 2. Validate permission exists
    -> 3. Validate permission's module is active for the tenant
    -> 4. If permission has feature_key:
          validate feature is commercially included and runtime-enabled
    -> 5. Validate optional valid_from/expires_at
    -> 6. Upsert user_permission_overrides
    -> 7. Invalidate user's permission snapshot
    -> 8. Audit log: permission_override.set
```

## Hierarchy Scoping

Employee-data endpoints must apply assignment scope after permission checks. The frontend never sends employee ID lists.

```text
IHierarchyScope.Resolve(userId, permissionCode, tenantId)
  -> returns scope predicate based on user_roles.scope_type/scope_id:
     Own | DirectReports | Department | Team | Organization
```

## Cache Invalidation

Any change to these records invalidates affected permission/session snapshots:

| Change | Cache Invalidated |
|:-------|:------------------|
| Role permissions updated | All users with that role |
| User role assigned/removed | That user |
| User permission override set/expired | That user |
| Feature access grant changed | Affected role users or employee |
| Tenant module entitlement changed | All tenant users |
| Tenant selected feature keys changed | All tenant users |
| Feature flag affecting a tenant changed | Users in affected tenant or feature-flag cache |
| Employee reporting line changed | Affected hierarchy scopes |

## Error Scenarios

| Error | Handling |
|:------|:---------|
| Missing permission | 403 Forbidden |
| Module not active for tenant | 403 Forbidden |
| Feature not commercially included | 403 Forbidden |
| Runtime feature flag disabled | 403 Forbidden |
| Tenant Super Admin tries disabled/unpurchased feature | 403 Forbidden |
| Platform Super Admin token used on tenant-facing route | 403 Forbidden |
| Temporary permission grant expired | Treat as absent |
| Role not found | 404 |
| Duplicate role name | 409 |
| Invalid grantee_type | 422 |

## Related

- [[modules/auth/authorization/overview|Authorization Overview]]
- [[frontend/cross-cutting/authorization|Frontend Authorization]]
- [[frontend/cross-cutting/feature-flags|Feature Flags]]
- [[developer-platform/modules/module-catalog-manager/end-to-end-logic|Module Catalog Feature Registry]]
- [[developer-platform/modules/feature-flag-manager/end-to-end-logic|Feature Flag Seed List]]
