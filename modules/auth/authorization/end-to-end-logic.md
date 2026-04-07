# Authorization — End-to-End Logic

**Module:** Auth
**Feature:** Authorization (RBAC)

---

## Permission Check

### Flow

```
Any protected API endpoint
  -> [RequirePermission("module:action")] attribute
    -> RequirePermissionFilter.OnActionExecutionAsync(context, next)
      -> 1. Extract user claims from JWT
      -> 2. Get permissions[] claim from token
      -> 3. Check if required permission exists in permissions array
         -> If yes -> continue to controller action
         -> If no -> Return 403 Forbidden
```

## Assign Role to User

### Flow

```
POST /api/v1/roles/{roleId}/assign
  -> RoleController.AssignRole(roleId, AssignRoleCommand)
    -> [RequirePermission("roles:manage")]
    -> RoleService.AssignRoleAsync(userId, roleId, ct)
      -> 1. Validate role exists and belongs to same tenant
      -> 2. Check if user already has this role
         -> If yes -> Return failure("Role already assigned")
      -> 3. INSERT into user_roles (user_id, role_id, assigned_at)
      -> 4. Log to audit_logs: action = "role.assigned"
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

### Error Scenarios

| Error | Handling |
|:------|:---------|
| Permission not in JWT | Return 403 Forbidden |
| Role not found | Return 404 |
| Duplicate role name | Return 409 Conflict |
| Cannot delete system role | Return 400 |

## Related

- [[authorization|Overview]]
- [[authentication]]
- [[session-management]]
- [[audit-logging]]
- [[event-catalog]]
- [[error-handling]]
- [[shared-kernel]]
