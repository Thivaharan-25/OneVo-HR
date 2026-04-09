# Authorization (Hybrid Permission Control in Frontend)

## Permission Model

Permissions flow from the backend JWT as **effective permissions** — already resolved from the user's roles + individual overrides + feature grants. The frontend uses them for **UI gating only** — the API enforces authorization and hierarchy scoping server-side. Frontend authorization is a UX concern: don't show things the user can't access.

### How Effective Permissions Work

The JWT contains the **final resolved permission set** for the user. The frontend does NOT need to know about roles, overrides, or feature grants — it just checks the permission codes in the token.

```
JWT claims:
{
  "permissions": ["employees:read", "leave:approve", "leave:read"],
  "granted_modules": ["core-hr", "leave"],
  "hierarchy_scope": "subordinates",  // "all" for Super Admin
  "sub": "user-uuid",
  "tenant_id": "tenant-uuid"
}
```

### Permission Format

```
{resource}:{action}
{resource}:{action}:{scope}
```

Examples:
```
employees:read            — Can view employee list (scoped to subordinates)
employees:create          — Can create employees
employees:update          — Can edit employee details
employees:delete          — Can delete employees
employees:update:salary   — Can edit salary specifically (field-level)
leave:approve             — Can approve leave requests (scoped to subordinates)
payroll:read              — Can view payroll data
payroll:run               — Can execute payroll runs
workforce:view            — Can view workforce intelligence
exceptions:view           — Can view exception alerts
exceptions:manage         — Can acknowledge/dismiss alerts
monitoring:view-settings  — Can view monitoring configuration
monitoring:update-settings — Can change monitoring settings
settings:read             — Can view tenant settings
billing:read              — Can view billing
```

## Gating Levels

### Level 1: Module-Level (Feature Grants)

Entire module routes gated based on `granted_modules` from JWT. If a module isn't granted, the entire section is hidden:

```tsx
// middleware.ts
function isModuleGranted(module: string): boolean {
  const { grantedModules } = useAuthStore.getState();
  return grantedModules.includes(module);
}

// Route groups only accessible if module is granted
const MODULE_ROUTES: Record<string, string> = {
  '/hr': 'core-hr',
  '/leave': 'leave',
  '/payroll': 'payroll',
  '/workforce': 'workforce',
  '/performance': 'performance',
  '/settings': 'settings',
};
```

### Level 2: Route-Level (Permission Check)

Within a granted module, specific routes require specific permissions:

```tsx
const ROUTE_PERMISSIONS: Record<string, string> = {
  '/people/employees': 'employees:read',
  '/leave/requests': 'leave:read',
  '/payroll/runs': 'payroll:read',
  '/settings/admin': 'settings:admin',
};
```

### Level 3: Sidebar Navigation

Sections and items hidden if user lacks permission or module access:

```tsx
{sidebarConfig.map(section => {
  // Module-level gate
  if (section.module && !isModuleGranted(section.module)) return null;
  // Permission-level gate
  if (section.permission && !hasPermission(section.permission)) return null;

  const visibleItems = section.items.filter(item =>
    (!item.module || isModuleGranted(item.module)) &&
    (!item.permission || hasPermission(item.permission))
  );

  if (visibleItems.length === 0) return null;

  return <SidebarSection key={section.label} {...section} items={visibleItems} />;
})}
```

### Level 4: Page Content

Within a page, gate specific sections:

```tsx
<Tabs>
  <TabsTrigger value="overview">Overview</TabsTrigger>
  <TabsTrigger value="employment">Employment</TabsTrigger>
  <PermissionGate permission="payroll:read">
    <TabsTrigger value="compensation">Compensation</TabsTrigger>
  </PermissionGate>
</Tabs>
```

### Level 5: Component Actions

Individual buttons, links, and actions:

```tsx
<PermissionGate permission="leave:approve">
  <Button onClick={handleApprove}>Approve</Button>
</PermissionGate>
```

### Level 6: Field-Level

Sensitive fields masked or hidden:

```tsx
<PermissionGate
  permission="payroll:read"
  fallback={<span className="text-muted-foreground">Restricted</span>}
>
  <span className="font-mono tabular-nums">{formatCurrency(salary)}</span>
</PermissionGate>
```

## PermissionGate Component

```tsx
interface PermissionGateProps {
  permission?: string | string[];  // Single or any-of
  module?: string;                 // Module-level gate
  requireAll?: boolean;            // All permissions required (default: any)
  fallback?: React.ReactNode;      // Shown when denied (default: null)
  children: React.ReactNode;
}

export function PermissionGate({ permission, module, requireAll = false, fallback = null, children }: PermissionGateProps) {
  const { hasPermission, hasAnyPermission, hasAllPermissions, isModuleGranted } = useAuthStore();

  // Module gate
  if (module && !isModuleGranted(module)) return <>{fallback}</>;

  // Permission gate
  if (permission) {
    const permissions = Array.isArray(permission) ? permission : [permission];
    const hasAccess = requireAll
      ? hasAllPermissions(...permissions)
      : hasAnyPermission(...permissions);
    if (!hasAccess) return <>{fallback}</>;
  }

  return <>{children}</>;
}
```

## useHasPermission Hook

For programmatic permission checks:

```tsx
export function useHasPermission(permission: string): boolean {
  return useAuthStore((state) => state.hasPermission(permission));
}

export function useIsModuleGranted(module: string): boolean {
  return useAuthStore((state) => state.isModuleGranted(module));
}
```

## Data Scoping (Hierarchy)

The **API handles all hierarchy scoping server-side**. The frontend does NOT filter data by hierarchy. However, the frontend should be aware of the user's scope to adjust the UI:

```tsx
// The API already returns only employees the user can see (subordinates)
const { data: employees } = useEmployees(filters);

// Hide "All Departments" filter if user is hierarchy-scoped
const { hierarchyScope } = useAuthStore();
{hierarchyScope === 'all' && <DepartmentFilter showAll />}
{hierarchyScope === 'subordinates' && <DepartmentFilter showOwnOnly />}
```

## Auth Store Shape

```tsx
interface AuthState {
  // From JWT
  permissions: string[];        // Effective permissions (already resolved)
  grantedModules: string[];     // Modules this user has access to
  hierarchyScope: 'all' | 'subordinates';  // Super Admin = 'all'

  // Derived helpers
  hasPermission: (code: string) => boolean;
  hasAnyPermission: (...codes: string[]) => boolean;
  hasAllPermissions: (...codes: string[]) => boolean;
  isModuleGranted: (module: string) => boolean;
  isSuperAdmin: () => boolean;
}
```

## Important: No Hardcoded Roles

The frontend must NEVER hardcode role names (e.g., "HR Manager", "Team Lead"). Roles are custom — the Super Admin creates them. Always check **permissions** and **module grants**, never role names.

```tsx
// WRONG - never do this
if (user.role === 'HR Manager') { ... }

// RIGHT - check the permission
if (hasPermission('employees:update')) { ... }

// RIGHT - check module access
if (isModuleGranted('leave')) { ... }
```

## Related

- [[frontend/cross-cutting/authentication|Authentication]] — auth flow, token management
- [[frontend/architecture/routing|Routing]] — route guards
- [[frontend/design-system/patterns/navigation-patterns|Navigation Patterns]] — sidebar gating
- [[frontend/design-system/patterns/table-patterns|Table Patterns]] — column-level gating
