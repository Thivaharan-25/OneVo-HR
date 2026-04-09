# Frontend App Structure

## Route Tree

All 22 backend modules mapped to ~41 frontend pages. Single route tree with permission-driven views (no separate employee self-service group).

### Authorization Model

**Hybrid permissions — not traditional fixed-role RBAC:**
1. **Custom roles** — tenants create roles with custom names and assign granular permissions
2. **Per-employee overrides** — individual employees can be granted/revoked specific module/feature access independent of their role

**Never hardcode role names.** Always check permission keys (e.g., `leave:read`, `leave:approve`, `payroll:manage`).

```tsx
// Permission check evaluates BOTH role permissions AND employee-level overrides
const { hasPermission } = usePermissions();

const canViewTeam = hasPermission('leave:read:team');
const canApprove = hasPermission('leave:approve');
const canManagePolicies = hasPermission('leave:manage');
```

---

```
app/
├── layout.tsx                        # Root: providers, fonts, ThemeProvider, AuthProvider
├── not-found.tsx                     # Global 404
├── error.tsx                         # Global error boundary
│
├── (auth)/                           # Public — no sidebar/topbar
│   ├── layout.tsx                    # Centered card layout
│   ├── login/page.tsx                # Email + password
│   ├── forgot-password/page.tsx      # Password reset request
│   ├── reset-password/page.tsx       # Token-based reset
│   └── mfa/page.tsx                  # TOTP/SMS verification
│
├── (dashboard)/                      # Authenticated — sidebar + topbar
│   ├── layout.tsx                    # DashboardLayout: Rail, Panel, Topbar, CommandPalette
│   ├── page.tsx                      # Permission-aware landing dashboard
│   │
│   │── ─── PILLAR 1: PEOPLE ────
│   │
│   ├── people/
│   │   │
│   │   ├── employees/                        # [CoreHR - Profile]
│   │   │   ├── page.tsx                      # Employee directory (list + grid)
│   │   │   ├── new/page.tsx                  # Create employee (multi-step wizard)
│   │   │   ├── @modal/                       # Parallel route: intercepted create
│   │   │   │   └── (.)new/page.tsx           # Create modal over list
│   │   │   ├── [id]/
│   │   │   │   ├── layout.tsx                # Shared layout for detail views
│   │   │   │   ├── loading.tsx               # Skeleton while loading
│   │   │   │   ├── not-found.tsx             # Employee not found
│   │   │   │   ├── page.tsx                  # Employee detail (scrollable sections: identity, quick facts, alerts, employment, pay & benefits, documents, timeline)
│   │   │   │   └── @panel/                   # Parallel route: intercepted edit
│   │   │   │       └── (.)edit/page.tsx      # Edit panel over detail
│   │   │   ├── components/                   # Colocated feature components
│   │   │   │   ├── EmployeeDataTable.tsx     # Sortable columns, search, filters
│   │   │   │   ├── EmployeeDetailSections.tsx # Scrollable section blocks (replaces tabs)
│   │   │   │   ├── EmployeeWizardSteps.tsx   # Multi-step create form stepper
│   │   │   │   └── AvatarUpload.tsx          # Profile photo upload
│   │   │   └── _types.ts                     # Local TypeScript definitions
│   │   │
│   │   └── leave/                            # [Leave]
│   │       ├── page.tsx                      # Leave requests (own or team)
│   │       ├── calendar/page.tsx             # Leave calendar view
│   │       ├── balances/page.tsx             # Leave balances
│   │       ├── policies/page.tsx             # Leave policy config
│   │       ├── components/                   # Colocated feature components
│   │       │   ├── LeaveRequestForm.tsx      # Apply / edit leave request
│   │       │   ├── LeaveCalendar.tsx         # Calendar with leave overlays
│   │       │   ├── LeaveBalanceCard.tsx      # Balance summary cards
│   │       │   └── LeavePolicyEditor.tsx     # Policy CRUD form
│   │       └── _types.ts                     # Local TypeScript definitions
│   │
│   │── ─── PILLAR 2: WORKFORCE ────
│   │
│   ├── workforce/
│   │   │
│   │   └── live/page.tsx                     # Real-time workforce overview (tabs: Activity, Work Insights, Online Status)
│   │
│   │── ─── CROSS-CUTTING ────
│   │
│   ├── inbox/page.tsx                        # Unified approvals, tasks, mentions
│   ├── calendar/page.tsx                     # Unified calendar
│   │
│   ├── notifications/                        # [Notifications]
│   │   ├── page.tsx                          # Notification inbox
│   │   └── preferences/page.tsx              # Channel preferences
│   │
│   │── ─── PILLAR 3: ORGANIZATION ────
│   │
│   ├── org/                                  # [OrgStructure]
│   │   ├── page.tsx                          # Org chart
│   │   ├── departments/page.tsx              # Department management
│   │   ├── teams/page.tsx                    # Team management
│   │   ├── components/                       # Colocated feature components
│   │   │   ├── DepartmentTree.tsx             # Interactive department hierarchy
│   │   │   ├── TeamMemberList.tsx             # Team member add/remove
│   │   │   └── OrgChart.tsx                   # Visual org chart component
│   │   └── _types.ts                         # Local TypeScript definitions
│   │
│   │── ─── PILLAR 4: ADMIN ────
│   │
│   ├── admin/                                # Requires admin permissions
│   │   ├── users/page.tsx                    # User management + role assignment
│   │   ├── roles/page.tsx                    # Role & permission management
│   │   ├── audit/page.tsx                    # Audit log viewer
│   │   ├── agents/                           # [AgentGateway]
│   │   │   ├── page.tsx                      # Desktop agent fleet
│   │   │   ├── [id]/
│   │   │   │   ├── loading.tsx               # Skeleton while loading
│   │   │   │   └── page.tsx                  # Agent detail
│   │   │   └── components/                   # Colocated feature components
│   │   │       ├── AgentStatusCard.tsx        # Agent health + status
│   │   │       └── AgentCommandPanel.tsx      # Remote commands
│   │   ├── devices/page.tsx                  # Hardware terminals
│   │   ├── compliance/page.tsx               # GDPR, data governance
│   │   ├── components/                       # Colocated admin components
│   │   │   ├── UserTable.tsx                  # User management DataTable
│   │   │   ├── RolePermissionMatrix.tsx       # Permission grid editor
│   │   │   └── AuditLogViewer.tsx             # Filterable audit log
│   │   └── _types.ts                         # Local TypeScript definitions
│   │
│   │── ─── PILLAR 5: SETTINGS ────
│   │
│   └── settings/                             # [Configuration + SharedPlatform]
│       ├── general/page.tsx                  # Tenant settings
│       ├── monitoring/page.tsx               # Feature toggles + overrides
│       ├── notifications/page.tsx            # Channel config (org-level)
│       ├── integrations/page.tsx             # SSO, LMS, payroll providers
│       ├── branding/page.tsx                 # Logo, colors, domain
│       ├── billing/page.tsx                  # Subscription & plan
│       ├── alert-rules/page.tsx              # Alert rule configuration
│       ├── feature-flags/page.tsx            # Feature flag management
│       └── components/                       # Colocated settings components
│           ├── SettingsForm.tsx               # Reusable settings form layout
│           └── IntegrationCard.tsx            # Integration status card
│
└── api/                                      # Next.js API routes (BFF)
    └── health/route.ts
```

## Module → Route Mapping

| # | Backend Module | Route(s) | Notes |
|---|---------------|----------|-------|
| 1 | activity-monitoring | `/workforce/live` | Activity tab within live dashboard |
| 2 | agent-gateway | `/admin/agents/` | Fleet overview, agent detail |
| 3 | auth | `(auth)/`, `/admin/users/`, `/admin/roles/` | Login/MFA + user/role management |
| 4 | calendar | `/calendar` | Unified (leave, holidays, reviews) |
| 5 | configuration | `/settings/general`, `/settings/monitoring` | Tenant config + overrides |
| 6 | core-hr | `/people/employees/` | Profile + lifecycle (onboarding/offboarding within employee creation flow) |
| 7 | documents | Employee detail `#documents` section | Permission-gated section in employee profile |
| 8 | exception-engine | `/settings/alert-rules`, alerts surfaced in Inbox | Rule config in settings; alerts in `/inbox` |
| 9 | expense | Employee detail section | Within employee profile (Phase 2) |
| 10 | grievance | Employee detail section | Within employee profile (Phase 2) |
| 11 | identity-verification | `/workforce/live` | Online Status tab within live dashboard |
| 12 | infrastructure | No pages | Backend-only |
| 13 | leave | `/people/leave/` | Requests, calendar, balances, policies |
| 14 | notifications | `/notifications/`, `/settings/notifications` | Inbox + preferences + org config |
| 15 | org-structure | `/org/` | Departments, teams, org chart |
| 16 | payroll | Employee detail `#pay-benefits` section | Permission-gated (Phase 2) |
| 17 | performance | Employee detail section | Within employee profile (Phase 2) |
| 18 | productivity-analytics | `/workforce/live` | Work Insights tab within live dashboard |
| 19 | reporting-engine | Accessible via Quick Search (⌘K) | No dedicated route |
| 20 | shared-platform | `/admin/`, `/settings/` | Spread across admin + settings |
| 21 | skills | Employee detail section | Within employee profile (Phase 2) |
| 22 | workforce-presence | `/workforce/live` | Online Status tab within live dashboard |

## Layout System

### Dashboard Layout (`(dashboard)/layout.tsx`)
- **Icon Rail:** 64px glass sidebar with 8 pillar icons, permission-gated via `hasPermission()`
- **Expansion Panel:** 220px glass panel, slides out on pillar hover/click
- **Topbar:** Glass surface, Quick Search (⌘K), notification bell (FYI only — no action badge), user menu
- **Pillar visibility:** Permission-gated via `hasPermission()` — never hardcode role names

### Auth Layout (`(auth)/layout.tsx`)
- Centered card, brand logo, no navigation

## Provider Stack (Root Layout)

```tsx
// app/layout.tsx
<QueryClientProvider>
  <AuthProvider>
    <PermissionProvider>     {/* Loads role + employee-level permissions */}
      <SignalRProvider>
        <ThemeProvider>
          <ToastProvider>
            {children}
          </ToastProvider>
        </ThemeProvider>
      </SignalRProvider>
    </PermissionProvider>
  </AuthProvider>
</QueryClientProvider>
```

## Colocated Component Pattern

Feature-specific components live inside each route's `components/` folder. Only truly shared components (e.g., `PermissionGate`, `ManagerHierarchyTree`, generic `DataTable` wrapper) belong in a top-level `components/` or `lib/` directory outside `app/`.

**Rules:**
- If a component is used by **only one feature** → `app/(dashboard)/people/employees/components/`
- If a component is used by **2+ features** → `components/` at project root or `lib/components/`
- `_types.ts` holds local TypeScript types for the feature (form schemas, table column defs, API response shapes)
- `loading.tsx` goes inside `[id]/` folders for detail page skeletons
- `layout.tsx` goes inside `[id]/` when detail views share chrome (breadcrumbs, back nav)

## Page Count

| Section | Pages |
|---------|-------|
| Auth | 4 |
| People (Employees + Leave) | ~12 |
| Workforce Live | ~4 |
| Org | 4 |
| Calendar | 2 |
| Inbox | 1 |
| Admin | ~6 |
| Settings | 8 |
| **Total** | **~41** |

## Related

- [[frontend/architecture/routing|Routing]] — Route guards, middleware, breadcrumbs
- [[backend/module-boundaries|Module Boundaries]] — Code splitting, import rules
- [[frontend/architecture/rendering-strategy|Rendering Strategy]] — SSR vs CSR per route
- [[frontend/cross-cutting/authorization|Authorization]] — Permission system details
- [[frontend/data-layer/state-management|State Management]] — TanStack Query + Zustand
