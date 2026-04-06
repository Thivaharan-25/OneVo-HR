# Frontend RBAC Patterns

## Permission Source

Permissions come from the JWT access token, decoded in AuthProvider:

```json
{
  "permissions": ["employees:read", "leave:approve", "workforce:view", "exceptions:view"]
}
```

These are cached in AuthProvider state and refreshed every 15 minutes when the access token is refreshed.

## PermissionGate Component

The primary way to gate UI by permission:

```tsx
interface PermissionGateProps {
  permission: string;                    // Single permission check
  permissions?: string[];                // Multiple (all required)
  anyPermission?: string[];              // Multiple (any one sufficient)
  fallback?: React.ReactNode;            // Shown when denied (default: null)
  children: React.ReactNode;
}

// Usage examples:

// Single permission
<PermissionGate permission="workforce:view">
  <WorkforceDashboard />
</PermissionGate>

// Any of multiple permissions
<PermissionGate anyPermission={["monitoring:configure", "monitoring:view-settings"]}>
  <MonitoringSettings />
</PermissionGate>

// With fallback
<PermissionGate permission="payroll:read" fallback={<Forbidden />}>
  <PayrollPage />
</PermissionGate>

// Render nothing if no permission (default)
<PermissionGate permission="exceptions:manage">
  <ConfigureRulesButton />
</PermissionGate>
```

## Hook-Based Checks

For conditional logic within components:

```tsx
const { hasPermission, hasAnyPermission } = useAuth();

// Conditional rendering
{hasPermission('leave:approve') && <ApproveButton />}

// Conditional data fetching
const { data } = useQuery({
  queryKey: ['exceptions'],
  queryFn: () => api.exceptions.list(),
  enabled: hasPermission('exceptions:view'),
});
```

## Sidebar Navigation Gating

Sidebar sections are gated by permission groups:

```typescript
const sidebarSections: SidebarSection[] = [
  {
    title: 'HR Management',
    permission: null, // Always visible if authenticated
    items: [
      { label: 'Employees', href: '/hr/employees', permission: 'employees:read' },
      { label: 'Leave', href: '/hr/leave', permission: 'leave:read' },
      { label: 'Performance', href: '/hr/performance', permission: 'performance:read' },
      { label: 'Payroll', href: '/hr/payroll', permission: 'payroll:read' },
      { label: 'Skills', href: '/hr/skills', permission: 'skills:read' },
      { label: 'Documents', href: '/hr/documents', permission: 'documents:read' },
    ],
  },
  {
    title: 'Workforce Intelligence',
    permission: 'workforce:view', // Entire section gated
    items: [
      { label: 'Live Dashboard', href: '/workforce/live', permission: 'workforce:view' },
      { label: 'Reports', href: '/workforce/reports', permission: 'analytics:view' },
      { label: 'Exceptions', href: '/workforce/exceptions', permission: 'exceptions:view' },
    ],
  },
  {
    title: 'Settings',
    permission: null,
    items: [
      { label: 'Monitoring', href: '/settings/monitoring', permission: 'monitoring:view-settings' },
      { label: 'General', href: '/settings/general', permission: 'settings:read' },
    ],
  },
];
```

Items where the user lacks permission are **hidden entirely** (not grayed out).

## Role-Based Data Scoping

The frontend doesn't enforce data scoping — the backend does. But the frontend should be aware of scope for UX:

| Role | Employee List | Leave Requests | Workforce Data |
|:-----|:-------------|:---------------|:---------------|
| Employee | Own only | Own only | Own only (self-service) |
| Manager | Team members | Team requests | Team data |
| HR Admin | All employees | All requests | All data |
| Org Owner | All + settings | All + policies | All + config |

## Monitoring Config Gating

Beyond RBAC, Workforce Intelligence UI is also gated by monitoring configuration:

```tsx
function WorkforceSection() {
  const { hasPermission } = useAuth();
  const { data: config } = useMonitoringConfig();
  
  // Need BOTH permission AND monitoring enabled
  if (!hasPermission('workforce:view')) return null;
  if (!config?.activityMonitoring) return <MonitoringDisabledBanner />;
  
  return <WorkforceDashboard />;
}
```

## Permission Reference

### HR Management
| Permission | Grants |
|:-----------|:-------|
| `employees:read` | View employee list, profiles |
| `employees:write` | Create, edit employees |
| `employees:read-team` | View team members (Manager scope) |
| `leave:read` | View leave requests |
| `leave:approve` | Approve/reject leave |
| `leave:manage` | Configure leave policies |
| `payroll:read` | View payroll runs |
| `payroll:run` | Execute payroll calculation |
| `payroll:approve` | Approve payroll for payment |
| `performance:read` | View reviews |
| `performance:manage` | Create cycles, manage reviews |

### Workforce Intelligence
| Permission | Grants |
|:-----------|:-------|
| `workforce:view` | Live dashboard, employee activity |
| `workforce:manage` | Modify presence records |
| `exceptions:view` | View exception alerts |
| `exceptions:acknowledge` | Acknowledge/dismiss alerts |
| `exceptions:manage` | Configure rules, escalation chains |
| `monitoring:configure` | Edit monitoring feature toggles |
| `monitoring:view-settings` | View monitoring settings (read-only) |
| `analytics:view` | View reports and analytics |
| `analytics:export` | Export reports (CSV/Excel) |
| `verification:view` | View verification logs |
| `verification:configure` | Configure verification policies |
| `agent:manage` | Manage registered agents |
| `agent:view-health` | View agent health status |

## Related

- Auth flow: `frontend/docs/security/auth-flow.md`
- Backend RBAC: `docs/security/auth-architecture.md`
- Monitoring config: `docs/architecture/modules/configuration.md`
