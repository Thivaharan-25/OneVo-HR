# Authorization — End-to-End Logic

**Module:** Auth
**Feature:** Authorization (Hybrid Permission Control)

---

## Permission Check (Every Protected Endpoint)

### Flow

```
Any protected API endpoint
  -> [RequirePermission("module:action")] attribute
    -> HybridPermissionFilter.OnActionExecutionAsync(context, next)
      -> 1. Extract user claims from JWT
      -> 2. Get effective_permissions[] from JWT (resolved at login time)
      -> 3. Check if user is Super Admin (has `*` permission)
         -> If yes -> skip permission check, continue
      -> 4. Check if the required permission's module is in user's granted features
         -> If module not granted -> Return 403 Forbidden
      -> 5. Check if required permission exists in effective_permissions[]
         -> If yes -> continue to controller action
         -> If no -> Return 403 Forbidden
      -> 6. Apply hierarchy scoping via IHierarchyScope
         -> Inject hierarchy filter into the request context
         -> Controller queries automatically scoped to subordinates
```

## Resolve Effective Permissions (At Login / Token Refresh)

### Flow

```
User logs in or refreshes token
  -> TokenService.GenerateAccessTokenAsync(userId, tenantId, ct)
    -> PermissionResolver.ResolveAsync(userId, tenantId, ct)
      -> 1. Get user's assigned roles from user_roles
      -> 2. Collect all permission codes from role_permissions for those roles
      -> 3. Query user_permission_overrides for this user
         -> Add permissions where grant_type = 'grant'
         -> Remove permissions where grant_type = 'revoke'
      -> 4. Query feature_access_grants for this user (both employee-level and role-level)
         -> Build set of granted modules
      -> 5. Filter permissions: only keep permissions whose module is in granted modules
      -> 6. Return final List<string> of permission codes
    -> Embed permissions in JWT claims
    -> Return access token
```

## Hierarchy Scoping (Data Filtering)

### Flow

```
Any endpoint returning employee-related data
  -> Controller calls service with IHierarchyScope and optional featureContext
    -> HierarchyScopeService.GetSubordinateIdsAsync(currentUserId, featureContext?, ct)
      -> Returns HierarchyScopeResult { subordinateIds: Set<Guid>, bypassIds: Set<Guid> }

      SUBORDINATE RESOLUTION (unchanged):
      -> 1. If current user is Super Admin -> subordinateIds = ALL employee IDs
      -> 2. Otherwise: recursive CTE on reports_to_id
           WITH RECURSIVE subordinates AS (
             SELECT id FROM employees WHERE reports_to_id = @currentEmployeeId
             UNION ALL
             SELECT e.id FROM employees e
             INNER JOIN subordinates s ON e.reports_to_id = s.id
           )
           SELECT id FROM subordinates
      -> 3. Cache in Redis (key: `hierarchy:{tenantId}:{userId}`, TTL: 5 min)

      BYPASS RESOLUTION (new):
      -> 4. If featureContext IS PROVIDED:
           SELECT * FROM hierarchy_scope_exceptions
           WHERE tenant_id = @tenantId
             AND granted_to_employee_id = @currentUserId
             AND (applies_to IS NULL OR applies_to = @featureContext)
             AND (expires_at IS NULL OR expires_at > NOW())
         If featureContext IS NULL:
           SELECT * FROM hierarchy_scope_exceptions
           WHERE tenant_id = @tenantId
             AND granted_to_employee_id = @currentUserId
             AND applies_to IS NULL
             AND (expires_at IS NULL OR expires_at > NOW())
         NOTE: applies_to = NULL comparison is always false in SQL —
               the two branches MUST remain separate.
      -> 5. For each exception record, expand scope_id into employee IDs:
           - scope_type = 'department': SELECT id FROM employees WHERE department_id = scope_id
           - scope_type = 'people':     { scope_id }
           - scope_type = 'role':       SELECT employee_id FROM user_roles WHERE role_id = scope_id

      CALLER CONTRACT:
      -> Services apply WHERE employee_id IN (@subordinateIds) to base queries
      -> bypassIds are ALWAYS appended after any additional filters
         (e.g. team creation dept filter applies to subordinateIds only, not bypassIds)
      -> Flows NOT passing featureContext only receive applies_to IS NULL bypasses (safe default)
```

## Bypass Grant Management

### Create Bypass Grant

```
POST /api/v1/employees/{employeeId}/bypass-grants
  -> Requires roles:manage
  -> BypassGrantService.CreateAsync(grantorId, targetEmployeeId, dto)
    -> 1. Resolve granter's accessible scope via IHierarchyScope
    -> 2. Verify dto.scopeId is within granter's accessible scope (ceiling rule)
    -> 3. If granter has permission_delegation_scopes record:
           - Verify dto.appliesTo is within module_scope
           - Block dto.appliesTo = null (All Features) for delegated granters
    -> 4. Insert hierarchy_scope_exceptions record
    -> 5. Invalidate bypass cache for targetEmployeeId
    -> 6. Audit log entry
```

### Permission Delegation Scope

```
Created atomically when roles:manage is granted (Path A or Path B in permission assignment)
  -> PermissionDelegationService.CreateAsync(grantorId, recipientId, moduleScope[])
    -> 1. Resolve granter's own module_scope (from permission_delegation_scopes)
           If no record: granter is root admin, any modules allowed
    -> 2. Verify moduleScope is strict subset of granter's own module_scope
    -> 3. Insert permission_delegation_scopes record
    -> 4. Audit log entry
```

## Grant Feature Access to Role or Employee

### Flow

```
POST /api/v1/feature-access
  -> FeatureAccessController.Grant(GrantFeatureAccessCommand)
    -> [RequirePermission("roles:manage")]
    -> Caller must be Super Admin (enforced in service layer)
    -> FeatureAccessService.GrantAsync(command, ct)
      -> 1. Validate grantee exists (role or employee depending on grantee_type)
      -> 2. Validate module code is valid
      -> 3. UPSERT into feature_access_grants
         -> ON CONFLICT (tenant_id, grantee_type, grantee_id, module) DO UPDATE is_enabled
      -> 4. If grantee_type = 'employee':
         -> Invalidate that user's permission cache
         -> Force token refresh on next request
      -> 5. If grantee_type = 'role':
         -> Invalidate permission cache for ALL users with this role
      -> 6. Log to audit_logs: action = "feature_access.granted"
      -> Return Result.Success()
```

## Grant/Revoke Individual Permission Override for Employee

### Flow

```
POST /api/v1/users/{id}/permission-overrides
  -> PermissionOverrideController.Set(SetPermissionOverrideCommand)
    -> [RequirePermission("roles:manage")]
    -> Caller must be Super Admin (enforced in service layer)
    -> PermissionOverrideService.SetAsync(userId, command, ct)
      -> 1. Validate employee exists and belongs to same tenant
      -> 2. Validate permission_id exists
      -> 3. UPSERT into user_permission_overrides
         -> ON CONFLICT (tenant_id, user_id, permission_id) DO UPDATE grant_type, reason
      -> 4. Invalidate user's permission cache
      -> 5. Force token refresh on next request
      -> 6. Log to audit_logs: action = "permission_override.set"
      -> Return Result.Success()
```

## Assign Role to Employee

### Flow

```
POST /api/v1/users/{userId}/roles
  -> RoleController.AssignRole(AssignRoleCommand)
    -> [RequirePermission("roles:manage")]
    -> RoleService.AssignRoleAsync(userId, roleId, ct)
      -> 1. Validate role exists and belongs to same tenant
      -> 2. Check if user already has this role
         -> If yes -> Return failure("Role already assigned")
      -> 3. INSERT into user_roles (user_id, role_id, assigned_at, assigned_by)
      -> 4. Invalidate user's permission cache
      -> 5. Force token refresh on next request
      -> 6. Log to audit_logs: action = "role.assigned"
      -> Return Result.Success()
```

## Create Custom Role

### Flow

```
POST /api/v1/roles
  -> RoleController.Create(CreateRoleCommand)
    -> [RequirePermission("roles:manage")]
    -> RoleService.CreateRoleAsync(command, ct)
      -> 1. Validate name is unique within tenant
      -> 2. Validate all permission IDs exist in permissions table
      -> 3. INSERT into roles (is_system = false)
      -> 4. INSERT into role_permissions for each permission
      -> 5. Log to audit_logs
      -> Return Result.Success(roleDto)
```

## Cache Invalidation Rules

Any change to roles, overrides, or feature grants must invalidate affected caches:

| Change | Cache Keys Invalidated |
|:-------|:----------------------|
| Role permissions updated | All users with that role |
| User role assigned/removed | That user |
| User permission override set | That user |
| Feature access granted/revoked for role | All users with that role |
| Feature access granted/revoked for employee | That employee |
| Employee `reports_to_id` changed | All employees in affected subtree |

### Error Scenarios

| Error | Handling |
|:------|:---------|
| Permission not in effective permissions | Return 403 Forbidden |
| Module not in granted features | Return 403 Forbidden |
| Role not found | Return 404 |
| Duplicate role name | Return 409 Conflict |
| Cannot delete system role | Return 400 |
| Invalid grantee_type | Return 422 |
| Permission override for nonexistent permission | Return 422 |

## Related

- [[frontend/cross-cutting/authorization|Overview]]
- [[frontend/cross-cutting/authentication|Authentication]]
- [[modules/auth/session-management/overview|Session Management]]
- [[modules/auth/audit-logging/overview|Audit Logging]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
- [[backend/shared-kernel|Shared Kernel]]
- [[frontend/architecture/overview|Teams]] — team membership for scoping
- [[frontend/architecture/overview|Departments]] — department hierarchy for scoping
