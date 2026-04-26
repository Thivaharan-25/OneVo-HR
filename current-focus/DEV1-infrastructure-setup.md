# Task: Infrastructure & Foundation Setup

**Assignee:** Dev 1
**Module:** Infrastructure + SharedKernel
**Priority:** Critical
**Dependencies:** None (first task)

---

## Step 1: Backend

### Acceptance Criteria

- [ ] Solution structure created with all **22 module projects** per [[backend/module-catalog|Module Catalog]]
- [ ] SharedKernel implemented: BaseEntity, BaseRepository, ITenantContext, Result<T>, IEncryptionService
- [ ] PostgreSQL with EF Core configured (snake_case convention, RLS policies)
- [ ] Redis connection configured
- [ ] Tenant CRUD + provisioning flow (signup -> seed -> activate) **with `industry_profile` selection**
- [ ] Industry profile sets default monitoring toggles in `monitoring_feature_toggles` — see [[modules/configuration/monitoring-toggles/overview|configuration]]
- [ ] User CRUD with password hashing (Argon2id)
- [ ] File upload service (local disk for dev, configurable for production)
- [ ] Country reference data seeded (LK, GB, etc.)
- [ ] Docker Compose for local development (PostgreSQL + Redis)
- [ ] Swagger/OpenAPI documentation working
- [ ] Health check endpoints

### Backend References

- [[AI_CONTEXT/tech-stack|Tech Stack]] — full tech stack
- [[backend/shared-kernel|Shared Kernel]] — SharedKernel structure
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant isolation
- [[database/migration-patterns|Migration Patterns]] — EF Core migrations
- [[infrastructure/environment-parity|Environment Parity]] — Docker Compose setup
- [[code-standards/backend-standards|Backend Standards]] — naming conventions
- [[backend/module-catalog|Module Catalog]] — 22-module solution structure

### AI Instructions

When generating code for this task:
1. Create the solution structure per [[backend/module-catalog|Module Catalog]]
2. Follow naming conventions in [[code-standards/backend-standards|Backend Standards]]
3. Ensure all entities inherit from BaseEntity
4. Include tenant_id on all tenant-scoped entities
5. Use UUID v7 for primary keys

---

## Step 2: Frontend

### Pages to Build

```
app/
├── layout.tsx                        # Root layout: providers, fonts, ThemeProvider, AuthProvider
├── not-found.tsx                     # Global 404
├── error.tsx                         # Global error boundary
│
├── (auth)/
│   └── layout.tsx                    # Centered card layout, brand logo
│
├── (dashboard)/
│   ├── layout.tsx                    # DashboardLayout: Sidebar, Topbar, CommandPalette, Breadcrumbs
│   └── page.tsx                      # Permission-aware landing dashboard (placeholder KPI widgets)

# Note: This task creates the shell layouts only. Feature pages are built by their respective tasks.
# Shared components (PermissionGate, ManagerHierarchyTree, DataTable wrapper, NotificationBell)
# go in a top-level components/ or lib/components/ directory — NOT inside any feature folder.
```

### What to Build

- [ ] Root layout with provider stack: QueryClientProvider, AuthProvider, PermissionProvider, SignalRProvider, ThemeProvider, ToastProvider
- [ ] Dashboard layout shell: **icon rail** (52px dark floating card) + **expansion panel** (210px animated) + **topbar** (40px) — floating-cards layout, NOT a traditional sidebar. See [[frontend/design-system/components/shell-layout|Shell Layout]] for exact spec before writing a single line of code
- [ ] Permission-gated sidebar navigation (sections visible based on permission keys, not role names)
- [ ] Breadcrumb component (auto-generated from route hierarchy with label overrides)
- [ ] Overview dashboard page with placeholder KPI cards
- [ ] Global error.tsx and not-found.tsx
- [ ] Shared components directory with: PermissionGate, DataTable (generic wrapper), StatusBadge

### Userflows

- [[Userflow/Platform-Setup/tenant-provisioning|Tenant Provisioning]] — tenant signup + industry profile selection

### API Endpoints (Frontend Consumes)

| Method | Endpoint | Purpose |
|:-------|:---------|:--------|
| GET | `/api/v1/tenants/resolve?domain={hostname}` | Resolve tenant from subdomain |
| POST | `/api/v1/tenants` | Create tenant (provisioning) |
| GET | `/api/v1/dashboard` | Dashboard widgets |
| GET | `/api/v1/health` | Health check |

### Frontend References

**Shell layout — read these first before building the dashboard layout:**

- [[frontend/design-system/components/shell-layout|Shell Layout]] — floating-cards structure, body padding/gap, full Next.js layout implementation
- [[frontend/design-system/components/nav-rail|Nav Rail]] — icon rail exact spec (52px, `#17181F`, all 9 pillars, icon names, states, Tailwind code)
- [[frontend/design-system/components/expansion-panel|Expansion Panel]] — panel exact spec (210px, animation, all items per pillar with icon names, routes, permissions)
- [[frontend/architecture/topbar|Topbar]] — topbar exact spec (40px, all sub-components with pixel values)
- [[Userflow/Dashboard/shell-navigation|Shell Navigation]] — how rail/panel/topbar interact (active states, panel open/close flow)

**General:**

- [[frontend/architecture/app-structure|Frontend Structure]] — app directory layout
- [[frontend/design-system/README|Design System]] — design principles
- [[frontend/design-system/components/component-catalog|Component Catalog]] — shadcn/ui components
- [[frontend/design-system/foundations/color-tokens|Color Tokens]] — brand + shell color values
- [[frontend/architecture/sidebar-nav|Sidebar Nav Map]] — all pillar routes and permission keys
- [[frontend/design-system/foundations/typography|Typography]] — font scale including shell navigation sizes
- [[frontend/design-system/patterns/layout-patterns|Layout Patterns]] — sidebar, topbar, content areas
- [[frontend/data-layer/api-integration|API Integration]] — API client pattern
- [[frontend/data-layer/state-management|State Management]] — TanStack Query + Zustand

---

## Related Tasks

- [[current-focus/DEV2-auth-security|DEV2 Auth Security]] — builds auth on top of shared kernel
- [[current-focus/DEV3-org-structure|DEV3 Org Structure]] — depends on shared kernel
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4 Shared Platform Agent Gateway]] — depends on shared kernel
