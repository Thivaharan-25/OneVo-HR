# Frontend App Structure

> **Note:** A second frontend app (`dev-console`) exists for platform administration — see `developer-platform/frontend/app-structure.md` for details. This document covers the primary ONEVO tenant-facing app only.

## Route Tree

All 22 backend modules + 9 WMS modules mapped to ~63 frontend pages. Single route tree with permission-driven views (no separate employee self-service group).

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
│   │   │   └── _types.ts                     # Route-local: form schemas, column defs — NOT API shapes
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
│   │       └── _types.ts                     # Route-local: form schemas, column defs — NOT API shapes
│   │
│   │── ─── PILLAR 2: WORKFORCE + WMS ────
│   │
│   ├── workforce/
│   │   │
│   │   ├── page.tsx                              # Presence — live employee card grid (replaces 3-tab live view)
│   │   ├── [employeeId]/
│   │   │   └── page.tsx                          # Employee activity detail (filterable by date, task, project)
│   │   ├── projects/
│   │   │   ├── page.tsx                          # All projects in entity scope
│   │   │   ├── new/page.tsx                      # Create project
│   │   │   └── [id]/
│   │   │       ├── page.tsx                      # Project overview (epics, milestones, members)
│   │   │       ├── board/page.tsx                # Kanban / list view of tasks
│   │   │       ├── sprints/page.tsx              # Sprint management
│   │   │       └── roadmap/page.tsx              # Timeline view of epics and milestones
│   │   ├── my-work/
│   │   │   └── page.tsx                          # My assigned tasks across all projects
│   │   ├── planner/
│   │   │   └── page.tsx                          # Sprints, boards, roadmap (workspace-level view)
│   │   ├── goals/
│   │   │   ├── page.tsx                          # OKR overview — objectives and key results
│   │   │   └── [id]/page.tsx                     # Objective detail + key results + check-ins
│   │   ├── docs/
│   │   │   ├── page.tsx                          # Documents + Wiki list
│   │   │   └── [id]/page.tsx                     # Document or Wiki page
│   │   ├── time/
│   │   │   ├── page.tsx                          # My timesheet
│   │   │   └── reports/page.tsx                  # Time reports (personal and team)
│   │   └── analytics/
│   │       └── page.tsx                          # Productivity scores + capacity analytics
│   │
│   │── ─── CROSS-CUTTING ────
│   │
│   ├── inbox/page.tsx                        # Unified approvals, tasks, mentions, exception alerts
│   ├── chat/
│   │   └── page.tsx                          # Channels, DMs, message threads (WMS chat module)
│   ├── calendar/
│   │   ├── page.tsx                          # Unified calendar (leave, holidays, review cycles)
│   │   ├── schedule/page.tsx                 # Shift schedules
│   │   ├── attendance/page.tsx               # Attendance corrections
│   │   └── overtime/page.tsx                 # Overtime requests and approvals
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
│   │   ├── job-families/                     # [OrgStructure - Job Taxonomy]
│   │   │   ├── page.tsx                      # Job family list
│   │   │   └── [id]/page.tsx                 # Job family detail + associated roles
│   │   ├── legal-entities/                   # [OrgStructure - Entity Hierarchy]
│   │   │   ├── page.tsx                      # Legal entity list + hierarchy view
│   │   │   └── [id]/page.tsx                 # Entity detail + settings
│   │   ├── components/                       # Colocated feature components
│   │   │   ├── DepartmentTree.tsx             # Interactive department hierarchy
│   │   │   ├── TeamMemberList.tsx             # Team member add/remove
│   │   │   ├── OrgChart.tsx                   # Visual org chart component
│   │   │   ├── JobFamilyEditor.tsx            # Job family CRUD form
│   │   │   └── LegalEntityTree.tsx            # Entity hierarchy visualisation
│   │   └── _types.ts                         # Route-local: form schemas, column defs — NOT API shapes
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
│   │   └── _types.ts                         # Route-local: form schemas, column defs — NOT API shapes
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
|---|---|---|-------|
| 1 | activity-monitoring | `/workforce` (card productivity data), `/workforce/[employeeId]` (activity detail) | Replaces Activity tab |
| 2 | agent-gateway | `/admin/agents/` | Fleet overview, agent detail |
| 3 | auth | `(auth)/`, `/admin/users/`, `/admin/roles/` | Login/MFA + user/role management |
| 4 | calendar | `/calendar` | Unified (leave, holidays, reviews) |
| 5 | configuration | `/settings/general`, `/settings/monitoring` | Tenant config + overrides |
| 6 | core-hr | `/people/employees/` | Profile + lifecycle |
| 7 | documents | Employee detail `#documents` section | Permission-gated section in employee profile |
| 8 | exception-engine | `/settings/alert-rules`, escalated cards on `/workforce` | Rule config in settings; alerts surface as card escalation |
| 9 | expense | Employee detail section | Phase 2 |
| 10 | grievance | Employee detail section | Phase 2 |
| 11 | identity-verification | `/workforce` (online status dot on cards) | Replaces Online Status tab |
| 12 | infrastructure | No pages | Backend-only |
| 13 | leave | `/people/leave/` | Requests, calendar, balances, policies |
| 14 | notifications | `/notifications/`, `/settings/notifications` | Inbox + preferences + org config |
| 15 | org-structure | `/org/` | Departments, teams, org chart, job families, legal entities |
| 16 | payroll | Employee detail `#pay-benefits` section | Phase 2 |
| 17 | performance | Employee detail section | Phase 2 |
| 18 | productivity-analytics | `/workforce` (card score), `/workforce/analytics` | Card score + dedicated analytics page |
| 19 | reporting-engine | Accessible via Quick Search (⌘K) | No dedicated route |
| 20 | shared-platform | `/admin/`, `/settings/` | Spread across admin + settings |
| 21 | skills | `/org/job-families/`, Employee detail section | Job family taxonomy + employee skill records |
| 22 | workforce-presence | `/workforce` (presence cards) | Replaces Online Status tab |
| WMS | project | `/workforce/projects/` | Project management |
| WMS | task | `/workforce/projects/[id]/board`, `/workforce/my-work` | Task management |
| WMS | planning | `/workforce/planner`, `/workforce/projects/[id]/sprints`, `/workforce/projects/[id]/roadmap` | Sprints, boards, roadmap |
| WMS | okr | `/workforce/goals/` | Goals and OKRs |
| WMS | collab (docs/wiki) | `/workforce/docs/` | Documents and Wiki |
| WMS | collab (comments) | Embedded within tasks, projects, docs | Contextual, not a nav item |
| WMS | time | `/workforce/time/` | Timesheets and time logs |
| WMS | resource | `/workforce/analytics` (capacity section) | Capacity and allocation |
| WMS | chat | `/chat` | Channels, DMs, messages |

## Layout System

### Dashboard Layout (`(dashboard)/layout.tsx`)

The shell uses a **floating-cards** layout — every element is a separate rounded card with `8px` body padding and `6px` gaps between cards. See [[frontend/design-system/components/shell-layout|Shell Layout]] for the full implementation pattern.

- **Icon Rail:** **52px** floating dark card (`#17181F`, radius 12px). Permission-gated, always visible. See [[frontend/design-system/components/nav-rail|Nav Rail]].
- **Topbar:** **40px** height, floating white/dark card (radius 10px). See [[frontend/architecture/topbar|Topbar Architecture]] for pixel-precise spec.
- **Expansion Panel:** **210px** floating card, width+opacity animation (220ms ease-out). See [[frontend/design-system/components/expansion-panel|Expansion Panel]].
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

Feature components start colocated in the route's `components/` folder, then get promoted when reused.

**Three-tier hierarchy — one location at a time:**

| Scope | Location |
|---|---|
| Used by only one route | `app/(dashboard)/.../components/` (colocated) |
| Used by 2+ pages within the same module | `components/{module}/` — e.g. `components/hr/`, `components/org/` |
| Used across different modules | `components/shared/` |

**Promotion rule:** when a component moves to a higher tier, **delete the colocated copy**. Never keep both. Duplicating causes them to diverge silently.

**`_types.ts` scope:**
- ✅ Form schemas, column definitions, local UI state shapes
- ❌ API response shapes — those belong in `types/{module}.ts`, not here

**File placement:**
- `loading.tsx` goes inside `[id]/` folders for detail page skeletons
- `layout.tsx` goes inside `[id]/` when detail views share chrome (breadcrumbs, back nav)

**Heavy components require `next/dynamic()`:**

```tsx
const OrgChart = dynamic(() => import('@/components/org/org-chart'), {
  ssr: false,
  loading: () => <ChartSkeleton height={600} />,
});
const KanbanBoard = dynamic(() => import('@/components/projects/kanban-board'), {
  loading: () => <TableSkeleton rows={10} />,
});
```

Apply to: org charts, kanban boards, roadmap timelines, activity heatmaps, rich text editors, drag-and-drop widgets.

## Page Count

| Section | Pages |
|---------|-------|
| Auth | 4 |
| People (Employees + Leave) | ~12 |
| Workforce Presence | ~2 |
| Workforce WMS (Projects, My Work, Planner, Goals, Docs, Time, Analytics) | ~18 |
| Org (Chart, Departments, Teams, Job Families, Legal Entities) | ~8 |
| Calendar (Calendar, Schedules, Attendance, Overtime) | ~4 |
| Chat | ~1 |
| Inbox | 1 |
| Admin | ~6 |
| Settings | ~7 |
| **Total** | **~63** |

## Related

- [[frontend/architecture/routing|Routing]] — Route guards, middleware, breadcrumbs
- [[frontend/architecture/module-boundaries|Module Boundaries]] — Code splitting, import rules, component promotion path
- [[frontend/architecture/rendering-strategy|Rendering Strategy]] — SSR vs CSR per route
- [[frontend/cross-cutting/authorization|Authorization]] — Permission system details
- [[frontend/data-layer/state-management|State Management]] — TanStack Query + Zustand
