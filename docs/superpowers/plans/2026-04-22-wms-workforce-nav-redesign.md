# WMS Integration + Navigation Architecture — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Populate the ONEVO knowledge base with 12 new documentation files and 6 updated files covering the WMS integration, redesigned Workforce pillar, Chat pillar, and cleaned-up navigation architecture — no demo or product code changes.

**Architecture:** Start with the canonical sidebar nav reference (Task 1), which all later files cite for routes and permission keys. Cascade to frontend architecture docs (Tasks 2–4), then WMS userflows (Tasks 5–11), then presence and chat userflows (Tasks 12–14), then module doc updates (Tasks 15–17), then the userflow index (Task 18).

**Tech Stack:** Markdown (Obsidian-compatible). Internal cross-references use `[[path|Label]]` link syntax. No code changes in this plan.

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `frontend/architecture/sidebar-nav.md` | **Create** | Canonical nav reference — every pillar, item, route, permission key, label |
| `frontend/architecture/topbar.md` | **Create** | Legal entity switcher design, hierarchy scope, switching behavior |
| `frontend/architecture/app-structure.md` | **Update** | Add WMS + org routes, remove workforce/live tab model, update module map |
| `frontend/architecture/routing.md` | **Update** | Entity context in middleware, WMS route guards |
| `Userflow/Work-Management/wm-overview.md` | **Create** | WMS entry point — module map, frontend/backend ownership, HR integration points |
| `Userflow/Work-Management/project-flow.md` | **Create** | Project CRUD, membership, milestones, change control |
| `Userflow/Work-Management/task-flow.md` | **Create** | Task lifecycle, issues, bugs, submission, approval |
| `Userflow/Work-Management/planning-flow.md` | **Create** | Sprints, boards, roadmap, releases |
| `Userflow/Work-Management/goals-okr-flow.md` | **Create** | Objectives, key results, check-ins, alignment |
| `Userflow/Work-Management/time-tracking-flow.md` | **Create** | Time logs, timesheets, overtime connection to HR Calendar |
| `Userflow/Work-Management/resource-flow.md` | **Create** | Capacity snapshots, skill matching, allocation planning |
| `Userflow/Workforce-Presence/presence-overview.md` | **Create** | Card grid, agent escalation sort, card anatomy |
| `Userflow/Workforce-Presence/employee-activity-detail.md` | **Create** | Activity screen filters (date/task/project), productivity breakdown |
| `Userflow/Chat/chat-overview.md` | **Create** | Channels, DMs, messages, read receipts |
| `modules/workforce-presence/overview.md` | **Update** | Replace 3-tab model with card view + agent escalation |
| `modules/calendar/overview.md` | **Update** | Add Schedules/Attendance/Overtime, link to WMS time module |
| `Userflow/Workforce-Presence/shift-schedule-setup.md` | **Update** | Add WMS capacity/resource connection note |
| `Userflow/README.md` | **Update** | Add Work Management + Chat sections, update Workforce section |

---

## Task 1: Canonical Sidebar Nav Reference

**Files:**
- Create: `frontend/architecture/sidebar-nav.md`

- [ ] **Step 1: Create the file with this exact content**

```markdown
# Sidebar Navigation Map

Canonical reference for the ONEVO shell navigation. Navigation components, permission gates, and cross-module links must reference this document for route paths, label names, and permission keys. Never hardcode a label or route — always verify against this file.

## Design Principles

- **Business language labels** — "Activity Trail" not "Audit Logs". "People Access" not "Users".
- **No role name checks** — all visibility is permission-key driven, never role-name driven.
- **Panels only where needed** — Home, Chat, and Inbox have no expansion panels.
- **WMS lives in Workforce** — all Work Management System screens route under `/workforce/`.
- **Scheduling lives in Calendar** — Schedules, Attendance, and Overtime belong in Calendar, not Workforce.

## Topbar

```
[■ Acme Malaysia Sdn Bhd  ▾]  |  [  Search...  ⌘K  ]  |  🔔  ☀  [Avatar ▾]
```

Left: Legal entity name + hierarchy switcher dropdown  
Center: Search — command palette (⌘K / Ctrl+K)  
Right: Notification bell · Theme toggle · User avatar menu

See `topbar.md` for full legal entity switcher design.

## Icon Rail — 9 Pillars

| Position | Pillar | Has Panel | Default Route | Visible When |
|---|---|---|---|---|
| 1 | Home | No | `/` | Any authenticated user |
| 2 | People | Yes | `/people/employees` | `employees:read` OR `leave:read` |
| 3 | Workforce | Yes | `/workforce` | `workforce:read` |
| 4 | Org | Yes | `/org` | `org:read` |
| 5 | Calendar | Yes | `/calendar` | `calendar:read` |
| 6 | Chat | No | `/chat` | `chat:read` |
| 7 | Inbox | No | `/inbox` | Any authenticated user |
| 8 | Admin | Yes | `/admin/users` | `admin:read` |
| 9 | Settings | Yes | `/settings/general` | `settings:read` |

## Expansion Panel Items

### People

| Label | Route | Permission Key | Notes |
|---|---|---|---|
| Employees | `/people/employees` | `employees:read` | Directory, profiles, lifecycle |
| Leave | `/people/leave` | `leave:read` | Requests, calendar, balances, policies |

### Workforce

| Label | Route | Permission Key | WMS Module(s) | Notes |
|---|---|---|---|---|
| Presence | `/workforce` | `workforce:read` | workforce-presence, productivity-analytics, exception-engine | Default — live employee card grid |
| Projects | `/workforce/projects` | `projects:read` | project | All projects in entity scope |
| My Work | `/workforce/my-work` | `tasks:read` | task | My assigned tasks across all projects |
| Planner | `/workforce/planner` | `planning:read` | planning | Sprints, Boards, Roadmap, Releases |
| Goals | `/workforce/goals` | `goals:read` | okr | Objectives, key results, check-ins |
| Docs | `/workforce/docs` | `docs:read` | collab | Documents and Wiki |
| Timesheets | `/workforce/time` | `time:read` | time | Time logs, timesheets, reports |
| Analytics | `/workforce/analytics` | `analytics:read` | productivity-analytics, resource | Productivity scores + capacity |

### Org

| Label | Route | Permission Key | Notes |
|---|---|---|---|
| Org Chart | `/org` | `org:read` | Visual hierarchy |
| Departments | `/org/departments` | `org:read` | Department CRUD |
| Teams | `/org/teams` | `org:read` | Team CRUD |
| Job Families | `/org/job-families` | `org:manage` | Role groupings for compensation bands and career paths |
| Legal Entities | `/org/legal-entities` | `org:manage` | Create + manage entities shown in the topbar switcher |

### Calendar

| Label | Route | Permission Key | Notes |
|---|---|---|---|
| Calendar | `/calendar` | `calendar:read` | Unified: leave, holidays, review cycles |
| Schedules | `/calendar/schedule` | `schedule:read` | Shift schedules (was "Shifts & Schedules") |
| Attendance | `/calendar/attendance` | `attendance:read` | Attendance corrections (was "Attendance Correction") |
| Overtime | `/calendar/overtime` | `overtime:read` | Overtime requests and approvals |

### Chat (no panel)

Direct navigation to `/chat`. Full chat UI renders in the content area.  
Permission key: `chat:read`

### Inbox (no panel)

Direct navigation to `/inbox`. Unified approvals, tasks, mentions, exception alerts.  
Permission key: any authenticated user (content filtered by their permissions).

### Admin

| Label | Route | Permission Key | Was Named |
|---|---|---|---|
| People Access | `/admin/users` | `admin:users` | Users |
| Permissions | `/admin/roles` | `admin:roles` | Roles |
| Activity Trail | `/admin/audit` | `admin:audit` | Audit Logs |
| Agents | `/admin/agents` | `admin:agents` | — |
| Devices | `/admin/devices` | `admin:devices` | — |
| Data & Privacy | `/admin/compliance` | `admin:compliance` | Compliance |

### Settings

| Label | Route | Permission Key | Notes |
|---|---|---|---|
| General | `/settings/general` | `settings:read` | Tenant configuration |
| Alerts | `/settings/alert-rules` | `settings:alerts` | Alert rule configuration (was "Alert Rules") |
| Notifications | `/settings/notifications` | `settings:notifications` | Channel config (org-level) |
| Integrations | `/settings/integrations` | `settings:integrations` | SSO, LMS, payroll providers |
| Branding | `/settings/branding` | `settings:branding` | Logo, colors, domain |
| Billing | `/settings/billing` | `settings:billing` | Subscription and plan |
| System | `/settings/system` | `settings:system` | Merges Monitoring (system health, feature toggles) + Feature Flags into one page with two sections |

## Label Change Reference

| Old Label | New Label | Pillar | Reason |
|---|---|---|---|
| Users | People Access | Admin | Describes purpose — who can access the system |
| Roles | Permissions | Admin | Describes outcome — what permissions are configured |
| Audit Logs | Activity Trail | Admin | Business language — "trail" is more intuitive |
| Compliance | Data & Privacy | Admin | Describes user concern — data protection |
| Shifts & Schedules | Schedules | Calendar | Shorter, unambiguous |
| Attendance Correction | Attendance | Calendar | Shorter — correction is implied by the action |
| Alert Rules | Alerts | Settings | Shorter — rules implied by the config screen |
| Monitoring | → System (merged) | Settings | Combined with Feature Flags — both are technical admin controls |
| Feature Flags | → System (merged) | Settings | Combined with Monitoring |
```

- [ ] **Step 2: Verify**

Confirm: 9 pillars listed in the rail table. Workforce panel has 8 items. Org panel has 5 items (including Job Families + Legal Entities). Calendar has 4 items. Admin has 6 items. Settings has 7 items. Label Change Reference has 9 rows.

- [ ] **Step 3: Commit**

```bash
git add frontend/architecture/sidebar-nav.md
git commit -m "docs(frontend): canonical sidebar nav map — all pillars, routes, permission keys"
```

---

## Task 2: Topbar Architecture Doc

**Files:**
- Create: `frontend/architecture/topbar.md`

- [ ] **Step 1: Create the file with this exact content**

```markdown
# Topbar Architecture

## Layout

```
[■ Acme Malaysia Sdn Bhd  ▾]  |  [  Search...  ⌘K  ]  |  🔔  ☀  [Avatar ▾]
Left (fixed width ~200px)        Center (flex-grow)       Right (fixed width)
```

Height: 48px (`h-12`). Spans full width above both the icon rail and expansion panel.

## Left — Legal Entity Switcher

### What it shows
The legal entity the user currently operates within — the registered company or business unit their data access is scoped to. Not a generic "workspace" or "tenant" name.

### Why legal entity, not workspace name
ONEVO's permission model is hierarchy-scoped. A Super Admin may govern multiple entities (e.g., "Acme Malaysia Sdn Bhd", "Acme Singapore Pte Ltd", "Acme Group"). Their data access changes depending on which entity they are operating in. The topbar makes this context explicit and switchable.

### Switcher dropdown anatomy

```
[■ Acme Malaysia Sdn Bhd  ▾]
─────────────────────────────────
✓  Acme Malaysia Sdn Bhd         ← current (checkmark)
   Acme Group                    ← parent entity (if user has access)
   Acme Singapore Pte Ltd        ← sibling entity (if user has access)
─────────────────────────────────
   + Add Entity                  ← only visible with org:manage permission
```

Only entities within the user's hierarchy-scoped access appear. A regular employee sees only their own entity — the label is static, no dropdown triggered.

### Entity switching behavior
When user selects a different entity:
1. Auth session updates the active entity context
2. All scoped data re-fetches (employees, projects, reports visible in this entity)
3. App redirects to `/` (Home) — prevents showing stale data on the current page
4. Active entity persists in session across page refreshes

### Permission gating
| Permission | Behavior |
|---|---|
| `org:read` | User sees their own entity name as a static label — no dropdown |
| Any user with access to 2+ entities | Switcher dropdown is active |
| `org:manage` | Dropdown includes "+ Add Entity" option |

### Component
`EntitySwitcher` — lives in the topbar layout component.

### Data source
Entities are created and managed at Org → Legal Entities (`/org/legal-entities`). The switcher reads from this list filtered to the user's hierarchy access scope.

## Center — Search

Command palette trigger. Opens on click or keyboard shortcut (⌘K on Mac, Ctrl+K on Windows).

Shows: quick nav to any page, recent pages, global people search, global actions (create task, request leave, etc.).

## Right — Actions

**Notification Bell (`🔔`):** Badge count of unread inbox items. Click navigates to `/inbox`.

**Theme Toggle (`☀`):** Cycles system → light → dark.

**User Avatar Menu:** Dropdown showing user name, job title, link to their employee profile, and Sign Out.

## Related

- [[frontend/architecture/sidebar-nav|Sidebar Nav Map]] — full pillar and permission reference
- [[Userflow/Org/legal-entities|Legal Entity Management]] — where entities are created
```

- [ ] **Step 2: Verify**

Confirm: Entity switching behavior has 4 steps. Permission gating table has 3 rows. Component name `EntitySwitcher` is used consistently.

- [ ] **Step 3: Commit**

```bash
git add frontend/architecture/topbar.md
git commit -m "docs(frontend): topbar architecture — legal entity switcher and hierarchy scope"
```

---

## Task 3: Update App Structure — WMS Routes + Org Routes

**Files:**
- Modify: `frontend/architecture/app-structure.md`

- [ ] **Step 1: Replace the PILLAR 2: WORKFORCE section**

Find this block (approximately lines 78–83):
```
│   │── ─── PILLAR 2: WORKFORCE ────
│   │
│   ├── workforce/
│   │   │
│   │   └── live/page.tsx                     # Real-time workforce overview (tabs: Activity, Work Insights, Online Status)
```

Replace with:
```
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
```

- [ ] **Step 2: Replace the PILLAR 3: ORGANIZATION section**

Find:
```
│   ├── org/                                  # [OrgStructure]
│   │   ├── page.tsx                          # Org chart
│   │   ├── departments/page.tsx              # Department management
│   │   ├── teams/page.tsx                    # Team management
│   │   ├── components/                       # Colocated feature components
│   │   │   ├── DepartmentTree.tsx             # Interactive department hierarchy
│   │   │   ├── TeamMemberList.tsx             # Team member add/remove
│   │   │   └── OrgChart.tsx                   # Visual org chart component
│   │   └── _types.ts                         # Local TypeScript definitions
```

Replace with:
```
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
│   │   └── _types.ts                         # Local TypeScript definitions
```

- [ ] **Step 3: Add Chat route after the Inbox route**

Find:
```
│   ├── inbox/page.tsx                        # Unified approvals, tasks, mentions
│   ├── calendar/page.tsx                     # Unified calendar
```

Replace with:
```
│   ├── inbox/page.tsx                        # Unified approvals, tasks, mentions, exception alerts
│   ├── chat/
│   │   └── page.tsx                          # Channels, DMs, message threads (WMS chat module)
│   ├── calendar/
│   │   ├── page.tsx                          # Unified calendar (leave, holidays, review cycles)
│   │   ├── schedule/page.tsx                 # Shift schedules
│   │   ├── attendance/page.tsx               # Attendance corrections
│   │   └── overtime/page.tsx                 # Overtime requests and approvals
```

- [ ] **Step 4: Update the Module → Route Mapping table**

Find the rows for activity-monitoring, identity-verification, productivity-analytics, workforce-presence and update them. Also add WMS module rows. Replace the entire table with:

```markdown
## Module → Route Mapping

| # | Backend Module | Route(s) | Notes |
|---|---|---|-------|
| 1 | activity-monitoring | `/workforce` (card productivity data), `/workforce/[id]` (activity detail) | Replaces Activity tab |
| 2 | agent-gateway | `/admin/agents/` | Fleet overview, agent detail |
| 3 | auth | `(auth)/`, `/admin/users/`, `/admin/roles/` | Login/MFA + user/role management |
| 4 | calendar | `/calendar` | Unified (leave, holidays, reviews) |
| 5 | configuration | `/settings/general`, `/settings/system` | Tenant config + system health/feature controls |
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
| WMS | planning | `/workforce/planner`, `/workforce/projects/[id]/sprints` | Sprints, boards, roadmap |
| WMS | okr | `/workforce/goals/` | Goals and OKRs |
| WMS | collab (docs/wiki) | `/workforce/docs/` | Documents and Wiki |
| WMS | collab (comments) | Embedded within tasks, projects, docs | Contextual, not a nav item |
| WMS | time | `/workforce/time/` | Timesheets and time logs |
| WMS | resource | `/workforce/analytics` (capacity section) | Capacity and allocation |
| WMS | chat | `/chat` | Channels, DMs, messages |
```

- [ ] **Step 5: Update the Layout System section**

Find:
```
- **Icon Rail:** 64px glass sidebar with 8 pillar icons, permission-gated via `hasPermission()`
```

Replace with:
```
- **Icon Rail:** 56px sidebar with 9 pillar icons, permission-gated via `hasPermission()`. Starts below the topbar (`top-12`).
- **Topbar:** Full-width (`left-0 right-0`), 48px height. Shows legal entity switcher (left), command palette search (center), notification bell + theme toggle + avatar (right). See `topbar.md`.
```

- [ ] **Step 6: Update the Page Count table**

Find the Page Count section and replace with:

```markdown
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
```

- [ ] **Step 7: Commit**

```bash
git add frontend/architecture/app-structure.md
git commit -m "docs(frontend): update app structure — WMS routes, org extensions, chat, 3-tab removal"
```

---

## Task 4: Update Routing — Entity Context + WMS Guards

**Files:**
- Modify: `frontend/architecture/routing.md`

- [ ] **Step 1: Add entity context to middleware**

Find the middleware code block. After the line:
```
  response.headers.set('x-user-role', decoded.role);
```

Add:
```
  // Entity context — drives data scope for WMS and HR data
  response.headers.set('x-entity-id', decoded.activeEntityId ?? decoded.tenantId);
```

- [ ] **Step 2: Add WMS route guards**

Find:
```
  if (pathname.startsWith('/workforce') && !decoded.features?.includes('workforce')) {
    return NextResponse.redirect(new URL('/', request.url));
  }
```

Replace with:
```
  if (pathname.startsWith('/workforce') && !decoded.features?.includes('workforce')) {
    return NextResponse.redirect(new URL('/', request.url));
  }

  // WMS sub-routes require specific feature flags in addition to workforce access
  if (pathname.startsWith('/workforce/projects') && !decoded.features?.includes('wms:projects')) {
    return NextResponse.redirect(new URL('/workforce', request.url));
  }
  if (pathname.startsWith('/workforce/goals') && !decoded.features?.includes('wms:okr')) {
    return NextResponse.redirect(new URL('/workforce', request.url));
  }
  if (pathname.startsWith('/chat') && !decoded.features?.includes('wms:chat')) {
    return NextResponse.redirect(new URL('/', request.url));
  }
```

- [ ] **Step 3: Add entity context note to the Route Groups table**

In the Route Groups table, add a note to the `(dashboard)` row:

Find:
```
| `(dashboard)` | All authenticated views | Rail + Panel + Topbar + Breadcrumbs | Yes (permission-driven) |
```

Replace with:
```
| `(dashboard)` | All authenticated views | Rail + Panel + Topbar + Breadcrumbs | Yes (permission + entity-context driven) |
```

- [ ] **Step 4: Commit**

```bash
git add frontend/architecture/routing.md
git commit -m "docs(frontend): add entity context header and WMS route guards to routing spec"
```

---

## Task 5: WMS Overview Userflow

**Files:**
- Create: `Userflow/Work-Management/wm-overview.md`

- [ ] **Step 1: Create the file**

```markdown
# Work Management (WMS) — Overview

**Area:** Workforce Pillar  
**Trigger:** User navigates to any Workforce panel item (Projects, My Work, Planner, Goals, Docs, Timesheets, Analytics)  
**Required Permission:** `workforce:read` minimum; specific features gated by additional permission keys (see sidebar-nav.md)

## Purpose

ONEVO's Work Management System (WMS) is the project and task management layer built on top of workforce data. It answers two questions together: who is working (Presence), and what are they working on (Projects, Tasks, Goals, Time). All WMS screens live under the Workforce pillar.

## Ownership

| Layer | Owner |
|---|---|
| WMS Frontend (UI, routing, state) | ONEVO team |
| WMS Backend (API, business logic, data) | WMS backend team |
| HR ↔ WMS Integration | ONEVO team |

## Module Map

| WMS Module | ONEVO Route | Backend Key |
|---|---|---|
| Project | `/workforce/projects` | project |
| Task (issues, bugs) | `/workforce/my-work`, `/workforce/projects/[id]/board` | task |
| Planning (sprints, boards, roadmap) | `/workforce/planner` | planning |
| Goals / OKR | `/workforce/goals` | okr |
| Collaboration — Docs + Wiki | `/workforce/docs` | collab |
| Collaboration — Comments, reactions | Embedded inside tasks + docs | collab |
| Time (logs, timesheets) | `/workforce/time` | time |
| Resource (capacity, skills) | `/workforce/analytics` | resource |
| Chat | `/chat` | chat |

## Integration Points with ONEVO HR

| WMS Concept | ONEVO HR Connection |
|---|---|
| WMS User | Maps to ONEVO Employee — profile at `/people/employees/[id]` |
| Task assignee | Must be an employee within the current legal entity scope |
| Timesheet entry | Connects to Calendar → Attendance correction records |
| Overtime entry | Connects to Calendar → Overtime approval records |
| Resource capacity | Uses shift schedule data from Calendar → Schedules |
| Project team member | Must be an employee within the same entity scope |
| Productivity score | Surfaces on Workforce Presence card for each employee |

## Data Scope

All WMS data is scoped to the legal entity selected in the topbar. Switching legal entity changes which projects, tasks, goals, and docs are visible.

## Related Flows

- [[Userflow/Work-Management/project-flow|Project Management]]
- [[Userflow/Work-Management/task-flow|Task Management]]
- [[Userflow/Work-Management/planning-flow|Planning — Sprints and Boards]]
- [[Userflow/Work-Management/goals-okr-flow|Goals and OKRs]]
- [[Userflow/Work-Management/time-tracking-flow|Time Tracking]]
- [[Userflow/Work-Management/resource-flow|Resource Management]]
- [[Userflow/Workforce-Presence/presence-overview|Workforce Presence]]
- [[Userflow/Chat/chat-overview|Chat]]
```

- [ ] **Step 2: Commit**

```bash
git add Userflow/Work-Management/wm-overview.md
git commit -m "docs(userflow): WMS overview — module map, ownership, HR integration points"
```

---

## Task 6: Project Management Userflow

**Files:**
- Create: `Userflow/Work-Management/project-flow.md`

- [ ] **Step 1: Create the file**

```markdown
# Project Management

**Area:** Workforce → Projects (`/workforce/projects`)  
**Trigger:** User clicks "Projects" in the Workforce panel  
**Required Permission:** `projects:read` (view); `projects:write` (create/edit)

## Purpose

Projects are the top-level containers for all work in the WMS. Each project holds tasks, epics, milestones, sprints, and members. Projects are scoped to the current legal entity.

## Key Entities

| Entity | Role |
|---|---|
| `PROJECT` | Top-level container — name, status, dates |
| `PROJECT_MEMBER` | User-to-project link with role (owner / member / viewer) |
| `EPIC` | Groups of related tasks within a project |
| `MILESTONE` | Target deliverable with a due date |
| `PROJECT_SETTING` | Timezone, working days, default priority |
| `CHANGE_REQUEST` | Formal request to change project scope or timeline |

## Flow Steps

### View All Projects
1. User opens Workforce → Projects
2. System loads all projects in the current legal entity scope, filtered by user membership
3. Projects display as a list or grid: name, status badge, member count, open task count, due date
4. User can filter by status (Active / On Hold / Completed) or search by name

### Create Project
1. User clicks "+ Create" in the Workforce panel header
2. System opens a create form: name, description, start date, end date, default priority, working days
3. User submits — system creates `PROJECT` + `PROJECT_SETTING` records
4. Creator is automatically added as `PROJECT_MEMBER` with role "owner"
5. System redirects to the new project detail page

### Project Detail (`/workforce/projects/[id]`)
1. User clicks a project card
2. System loads: project overview, epics, milestones, recent activity, member list
3. Sub-routes available from within project detail:
   - `/workforce/projects/[id]/board` — Kanban or list view of all tasks
   - `/workforce/projects/[id]/sprints` — sprint planning and management
   - `/workforce/projects/[id]/roadmap` — timeline view of epics and milestones

### Add Project Member
1. From project detail, user clicks "Add Member" (requires `projects:write`)
2. User searches for an employee — scoped to the same legal entity
3. User selects a role: owner, member, or viewer
4. System creates a `PROJECT_MEMBER` record

### Submit Change Request
1. User clicks "Request Change" on project detail (scope, timeline, or resource change)
2. User fills the change form: type, description, impact
3. System creates a `CHANGE_REQUEST` with status "pending"
4. Project owners receive an Inbox notification to approve or reject
5. Outcome is logged in the change request history

## Connection Points

| Connects to | How |
|---|---|
| Workforce → Presence | The employee's current task (from this project) shows on their presence card |
| Workforce → My Work | My Work shows tasks from all projects where I am a member |
| Workforce → Planner | Project sprints and roadmap are accessible from the Planner item |
| Workforce → Timesheets | Time is logged against tasks within this project |
| People → Employees | Project members are ONEVO employees — profile link on the member list |
| Inbox | Change request approvals and project notifications land in Inbox |

## Related Flows

- [[Userflow/Work-Management/wm-overview|WMS Overview]]
- [[Userflow/Work-Management/task-flow|Task Management]]
- [[Userflow/Work-Management/planning-flow|Planning — Sprints and Boards]]
- [[Userflow/Work-Management/time-tracking-flow|Time Tracking]]
```

- [ ] **Step 2: Commit**

```bash
git add Userflow/Work-Management/project-flow.md
git commit -m "docs(userflow): project management flow — CRUD, membership, milestones, change control"
```

---

## Task 7: Task Management Userflow

**Files:**
- Create: `Userflow/Work-Management/task-flow.md`

- [ ] **Step 1: Create the file**

```markdown
# Task Management

**Area:** Workforce → My Work / Workforce → Projects → Board  
**Trigger:** User clicks "My Work" in Workforce panel, or opens a project board  
**Required Permission:** `tasks:read` (view); `tasks:write` (create/edit/assign)

## Purpose

Tasks are the atomic unit of work in the WMS. A task can be a feature, bug, issue, or any actionable item. Tasks live inside projects and support a full lifecycle: creation → assignment → work → submission → approval → close. Bugs are a specialised task type with additional reproduction steps and resolution tracking.

## Key Entities

| Entity | Role |
|---|---|
| `TASK` | Core work item — title, status, priority |
| `TASK_ASSIGNEE` | User-to-task assignment link |
| `CHECKLIST_ITEM` | Sub-steps within a task |
| `TASK_DEPENDENCY` | Blocks / blocked-by relationships |
| `LABEL` + `TASK_LABEL` | Tag system for filtering |
| `TASK_SUBMISSION` + `TASK_SUBMISSION_FILE` | Work submitted for review |
| `TASK_APPROVAL` | Approval request linked to a submission |
| `TASK_REOPEN_LOG` | Audit trail when a closed task is reopened |
| `BUG_REPORT` | Bug-specific task with severity and reproduction steps |
| `BUG_REPRODUCTION_STEP` | Numbered steps to reproduce the bug |
| `BUG_RESOLUTION` | Resolution type and who resolved it |

## Flow Steps

### View My Work (`/workforce/my-work`)
1. User opens Workforce → My Work
2. System loads all tasks assigned to the current user across all projects in the entity scope
3. Tasks are grouped by project and filterable by status, priority, due date
4. User clicks a task to open its detail panel

### Create Task (from project board)
1. User opens a project board (`/workforce/projects/[id]/board`)
2. User clicks "+ Add Task" in a status column
3. User enters title, description, priority, due date, labels
4. System creates `TASK` record linked to the project
5. User optionally assigns the task to a project member — creates `TASK_ASSIGNEE` record

### Task Lifecycle
```
Open → In Progress → In Review → Approved → Closed
                              ↓
                           Rejected → In Progress (reopened)
```

1. **Open** — task created, not yet started
2. **In Progress** — assignee begins work, logs time against the task
3. **In Review** — assignee submits work: creates `TASK_SUBMISSION` + uploads `TASK_SUBMISSION_FILE`
4. **Approved** — reviewer creates `TASK_APPROVAL` with status "approved"; task moves to Closed
5. **Rejected** — reviewer rejects with comment; system creates `TASK_REOPEN_LOG`; task returns to In Progress

### Bug Tracking
1. User creates a task and marks it as type "Bug"
2. System creates `BUG_REPORT` linked to the task
3. User adds reproduction steps: `BUG_REPRODUCTION_STEP` records (numbered, action + expected result)
4. When fixed, user adds a `BUG_RESOLUTION` record: resolution type, resolver, timestamp
5. Bug severity (critical / high / medium / low) determines priority in the Inbox exception alerts

### Dependencies
1. From task detail, user clicks "Add Dependency"
2. User searches for another task and sets type: blocks / blocked-by / relates-to
3. System creates `TASK_DEPENDENCY` record
4. Blocked tasks are visually marked on the board with a dependency badge

## Connection Points

| Connects to | How |
|---|---|
| Workforce → Presence | Assignee's current task shows on their presence card |
| Workforce → Timesheets | Time logs are attached to tasks — flow into timesheets |
| Inbox | Task approvals, assignment notifications, and mentions land in Inbox |
| Workforce → Planner | Tasks are organised into sprints on the Planner board |

## Related Flows

- [[Userflow/Work-Management/wm-overview|WMS Overview]]
- [[Userflow/Work-Management/project-flow|Project Management]]
- [[Userflow/Work-Management/planning-flow|Planning — Sprints and Boards]]
- [[Userflow/Work-Management/time-tracking-flow|Time Tracking]]
```

- [ ] **Step 2: Commit**

```bash
git add Userflow/Work-Management/task-flow.md
git commit -m "docs(userflow): task management flow — lifecycle, bugs, submission, approval"
```

---

## Task 8: Planning Userflow

**Files:**
- Create: `Userflow/Work-Management/planning-flow.md`

- [ ] **Step 1: Create the file**

```markdown
# Planning — Sprints, Boards, Roadmap

**Area:** Workforce → Planner (`/workforce/planner`) and Workforce → Projects → Sprints / Roadmap  
**Trigger:** User clicks "Planner" in the Workforce panel, or navigates to a project's sprint or roadmap sub-route  
**Required Permission:** `planning:read` (view); `planning:write` (create/edit sprints and boards)

## Purpose

Planning organises tasks into time-boxed sprints, visual boards, and a timeline roadmap. The Planner item in the Workforce panel shows a workspace-level view across all projects. Individual project sprints and roadmaps are accessible from within project detail.

## Key Entities

| Entity | Role |
|---|---|
| `SPRINT` | Time-boxed work period — start date, end date, tasks |
| `SPRINT_REPORT` | Velocity and completed points for a finished sprint |
| `BOARD` | Visual task grouping — kanban or list type |
| `BOARD_VIEW` | User-specific saved view (column config, filters) |
| `ROADMAP` | Workspace-level timeline of epics and milestones |
| `ROADMAP_ITEM` | An epic or milestone placed on the roadmap |
| `VERSION` | A planned release with a target date |
| `RELEASE_CALENDAR` | Scheduled release events |
| `BASELINE` | Snapshot of the project plan at a point in time |

## Flow Steps

### Workspace Planner (`/workforce/planner`)
1. User opens Workforce → Planner
2. System loads all active sprints and boards across all projects the user is a member of
3. User can switch between Board view (kanban) and List view
4. Filters: project, assignee, priority, label, sprint

### Create Sprint (within a project)
1. User opens `/workforce/projects/[id]/sprints`
2. User clicks "New Sprint" — enters name, start date, end date
3. System creates `SPRINT` record linked to the project
4. User drags tasks from the backlog into the sprint

### Sprint Lifecycle
```
Planning → Active → Completed
```
1. **Planning** — sprint created, tasks being assigned
2. **Active** — sprint started, tasks in progress, daily updates visible
3. **Completed** — sprint ends, system generates `SPRINT_REPORT` (velocity, completed vs planned points)
4. Incomplete tasks are moved back to the backlog or carried into the next sprint

### Board View
1. User opens a project board at `/workforce/projects/[id]/board`
2. Board renders tasks as cards in status columns (Open / In Progress / In Review / Closed)
3. User drags cards between columns to update task status
4. User saves a custom column config — stored as `BOARD_VIEW`

### Roadmap
1. User opens `/workforce/projects/[id]/roadmap`
2. System renders epics and milestones as a horizontal timeline (Gantt-style)
3. User places `ROADMAP_ITEM` records by dragging epics/milestones onto the timeline
4. Baseline snapshot can be taken to compare planned vs actual progress

### Release Planning
1. User creates a `VERSION` (e.g., "v1.2") with a target release date
2. User schedules the release via `RELEASE_CALENDAR`
3. Tasks can be tagged to a version — they appear grouped in the version detail

## Connection Points

| Connects to | How |
|---|---|
| Workforce → Projects | Sprints and roadmaps are sub-views of a project |
| Workforce → My Work | Tasks planned in sprints appear in My Work for assignees |
| Calendar | Release dates from `RELEASE_CALENDAR` can appear in the Calendar unified view |
| Inbox | Sprint completion reports and release notifications land in Inbox |

## Related Flows

- [[Userflow/Work-Management/wm-overview|WMS Overview]]
- [[Userflow/Work-Management/project-flow|Project Management]]
- [[Userflow/Work-Management/task-flow|Task Management]]
```

- [ ] **Step 2: Commit**

```bash
git add Userflow/Work-Management/planning-flow.md
git commit -m "docs(userflow): planning flow — sprints, boards, roadmap, releases"
```

---

## Task 9: Goals and OKR Userflow

**Files:**
- Create: `Userflow/Work-Management/goals-okr-flow.md`

- [ ] **Step 1: Create the file**

```markdown
# Goals and OKRs

**Area:** Workforce → Goals (`/workforce/goals`)  
**Trigger:** User clicks "Goals" in the Workforce panel  
**Required Permission:** `goals:read` (view); `goals:write` (create/edit)

## Purpose

Goals are the strategic layer above projects and tasks. An Objective defines a qualitative target. Key Results are measurable outcomes that determine if the Objective was achieved. Goals are scoped to the legal entity and can be aligned across teams.

## Key Entities

| Entity | Role |
|---|---|
| `OBJECTIVE` | Strategic goal — title, owner, progress percentage |
| `KEY_RESULT` | Measurable outcome linked to an objective |
| `OKR_UPDATE` | A progress update on an objective or key result |
| `OKR_ALIGNMENT` | Parent-child alignment between objectives |
| `INITIATIVE` | A specific action or project contributing to a key result |
| `GOAL_CHECKIN` | Periodic progress check-in with commentary |

## Flow Steps

### View Goals (`/workforce/goals`)
1. User opens Workforce → Goals
2. System loads all objectives in the entity scope, grouped by owner or team
3. Each objective shows: title, owner, progress bar, count of key results, status
4. User clicks an objective to open its detail

### Create Objective
1. User clicks "+ Create" → "New Objective"
2. User enters: title, description, owner (employee), time period (quarterly / annual)
3. System creates `OBJECTIVE` record with progress at 0%

### Add Key Results to Objective
1. From objective detail (`/workforce/goals/[id]`), user clicks "Add Key Result"
2. User enters: title, target value (numeric), unit, start value
3. System creates `KEY_RESULT` linked to the objective

### Track Progress (Check-in)
1. User opens objective detail and clicks "Check In"
2. User updates the current value for one or more key results
3. System creates `OKR_UPDATE` records and recalculates objective progress
4. User optionally adds a `GOAL_CHECKIN` note with commentary and `progress_delta`

### OKR Alignment
1. User opens an objective and clicks "Align to Parent"
2. User selects a parent objective (team or company level)
3. System creates `OKR_ALIGNMENT` record with `contribution_weight`
4. Parent objective progress is partially influenced by child objective progress

### Link Initiative
1. From a key result, user clicks "Add Initiative"
2. User links an existing project or creates a new initiative title
3. System creates `INITIATIVE` record linked to the key result

## Connection Points

| Connects to | How |
|---|---|
| Workforce → Projects | An initiative under a key result can link to a WMS project |
| Workforce → Analytics | Objective progress contributes to workforce productivity analytics |
| Inbox | Check-in reminders and alignment requests land in Inbox |
| People → Employees | Objectives are owned by employees — profile link on objective detail |

## Related Flows

- [[Userflow/Work-Management/wm-overview|WMS Overview]]
- [[Userflow/Work-Management/project-flow|Project Management]]
- [[Userflow/Work-Management/resource-flow|Resource Management]]
```

- [ ] **Step 2: Commit**

```bash
git add Userflow/Work-Management/goals-okr-flow.md
git commit -m "docs(userflow): goals and OKR flow — objectives, key results, check-ins, alignment"
```

---

## Task 10: Time Tracking Userflow

**Files:**
- Create: `Userflow/Work-Management/time-tracking-flow.md`

- [ ] **Step 1: Create the file**

```markdown
# Time Tracking

**Area:** Workforce → Timesheets (`/workforce/time`)  
**Trigger:** User clicks "Timesheets" in the Workforce panel, or logs time from within a task  
**Required Permission:** `time:read` (view own); `time:read:team` (view team); `time:write` (log time)

## Purpose

Time tracking captures how long employees spend on tasks. Time logs roll up into weekly timesheets for approval and connect directly to the HR modules: Attendance (corrections feed from timesheets) and Overtime (excess hours logged here become Overtime entries in Calendar → Overtime).

## Key Entities

| Entity | Role |
|---|---|
| `TIME_LOG` | A single time entry — task, user, duration, date |
| `TIMER_SESSION` | An active running timer (start → stop → creates TIME_LOG) |
| `TIMESHEET` | Weekly summary of all time logs for a user |
| `TIMESHEET_ENTRY` | A time log grouped under a timesheet period |
| `OVERTIME_ENTRY` | Hours exceeding the scheduled shift — requires approval |
| `BILLABLE_RATE` | User/project rate for billable time |
| `TIME_REPORT` | Aggregated time report by project, user, or period |

## Flow Steps

### Log Time Against a Task
1. From a task detail, user clicks "Log Time" or starts the timer (creates `TIMER_SESSION`)
2. User stops the timer — system calculates duration and creates `TIME_LOG`
3. Alternatively, user manually enters duration and date without a timer
4. Time log appears in the task's time history and rolls into the current week's `TIMESHEET`

### View Timesheet (`/workforce/time`)
1. User opens Workforce → Timesheets
2. System loads the current week's `TIMESHEET` for the user
3. Timesheet shows: date, task name, project, duration — grouped by day
4. Total hours per day compared against scheduled shift hours from Calendar → Schedules
5. Hours exceeding the daily schedule are flagged as potential overtime

### Submit Timesheet for Approval
1. User reviews the week's entries and clicks "Submit"
2. Timesheet status changes from "draft" to "submitted"
3. Manager receives an Inbox notification to approve or return for correction
4. On approval, timesheet status changes to "approved"

### Overtime Creation (automatic)
1. When a timesheet is approved and total daily hours exceed the scheduled shift, system automatically creates an `OVERTIME_ENTRY`
2. The `OVERTIME_ENTRY` appears in Calendar → Overtime for the manager to formally approve
3. Approved overtime entries feed into payroll (Phase 2)

### Attendance Correction Connection
1. If an employee's attendance record in Calendar → Attendance shows a discrepancy with their `TIME_LOG` entries, an attendance correction request is created
2. The correction adjusts the attendance record to match actual logged time

### Time Reports (`/workforce/time/reports`)
1. User with `time:read:team` permission opens time reports
2. Filters: date range, employee, project, task, billable / non-billable
3. System generates `TIME_REPORT` — exportable as CSV or PDF

## Connection Points

| Connects to | How |
|---|---|
| Workforce → Tasks | Time is logged directly from task detail |
| Calendar → Attendance | Timesheet entries reconcile with attendance records |
| Calendar → Overtime | Excess hours from approved timesheets create overtime entries |
| Calendar → Schedules | Scheduled shift hours are the baseline for overtime calculation |
| Workforce → Analytics | Time data feeds productivity and capacity analytics |
| Inbox | Timesheet approval requests land in Inbox |

## Related Flows

- [[Userflow/Work-Management/wm-overview|WMS Overview]]
- [[Userflow/Work-Management/task-flow|Task Management]]
- [[Userflow/Work-Management/resource-flow|Resource Management]]
- [[Userflow/Workforce-Presence/shift-schedule-setup|Shift Schedule Setup]]
```

- [ ] **Step 2: Commit**

```bash
git add Userflow/Work-Management/time-tracking-flow.md
git commit -m "docs(userflow): time tracking flow — logs, timesheets, overtime and attendance connections"
```

---

## Task 11: Resource Management Userflow

**Files:**
- Create: `Userflow/Work-Management/resource-flow.md`

- [ ] **Step 1: Create the file**

```markdown
# Resource Management

**Area:** Workforce → Analytics (`/workforce/analytics`)  
**Trigger:** User clicks "Analytics" in the Workforce panel; resource data also surfaces within project detail  
**Required Permission:** `analytics:read` (view); `analytics:write` (manage allocations)

## Purpose

Resource management answers: who is available, at what capacity, and with which skills — so that project work can be planned and allocated without overloading employees. It connects workforce scheduling (Calendar → Schedules) with WMS project planning (Projects, Sprints).

## Key Entities

| Entity | Role |
|---|---|
| `SKILL` | A named capability defined at the workspace level |
| `USER_SKILL` | An employee's skill record with proficiency level |
| `RESOURCE_PLAN` | An employee's allocation to a project (percentage) |
| `CAPACITY_SNAPSHOT` | Weekly utilisation percentage per employee |
| `SKILL_REQUIREMENT` | Skills needed for a project (headcount + level) |
| `RESOURCE_ALLOCATION_LOG` | History of allocation changes |

## Flow Steps

### View Capacity (`/workforce/analytics`)
1. User opens Workforce → Analytics
2. System loads capacity snapshots for all employees in the entity scope
3. Capacity view shows: employee name, current allocation %, available hours, scheduled hours
4. Employees above 100% utilisation are highlighted as overallocated
5. Data is sourced from `CAPACITY_SNAPSHOT` records (weekly snapshots)

### Allocate Employee to Project
1. From a project detail or the Analytics page, user clicks "Allocate Resource"
2. User selects an employee and sets allocation percentage (e.g., 50%)
3. System creates `RESOURCE_PLAN` record
4. Employee's capacity snapshot is updated on the next weekly calculation
5. Allocation history logged in `RESOURCE_ALLOCATION_LOG`

### Skill Matching
1. Project lead defines `SKILL_REQUIREMENT` records: skill, required proficiency, headcount needed
2. User opens the "Find Resources" view — system matches employees with `USER_SKILL` records meeting the requirement
3. User reviews the matched list and allocates selected employees to the project

### Employee Skills
1. Employee skills are managed in their People profile (Employee detail → Skills section)
2. HR admin or manager adds `USER_SKILL` records: skill name, proficiency level, verification date
3. Skills defined at the workspace level via Admin or the Org → Job Families structure

## Connection Points

| Connects to | How |
|---|---|
| Workforce → Projects | Resource allocations are linked to projects — visible in project member list |
| Workforce → Planner | Sprint planning references capacity to avoid overallocation |
| Calendar → Schedules | Scheduled shift hours determine available capacity |
| People → Employees | Employee skills and profile link from the resource view |
| Workforce → Timesheets | Actual time logged feeds into real utilisation vs planned |
| Org → Job Families | Job family defines expected skills for role groups |

## Related Flows

- [[Userflow/Work-Management/wm-overview|WMS Overview]]
- [[Userflow/Work-Management/project-flow|Project Management]]
- [[Userflow/Work-Management/time-tracking-flow|Time Tracking]]
- [[Userflow/Workforce-Presence/presence-overview|Workforce Presence]]
```

- [ ] **Step 2: Commit**

```bash
git add Userflow/Work-Management/resource-flow.md
git commit -m "docs(userflow): resource management flow — capacity, skills, allocation"
```

---

## Task 12: Workforce Presence Overview Userflow

**Files:**
- Create: `Userflow/Workforce-Presence/presence-overview.md`

- [ ] **Step 1: Create the file**

```markdown
# Workforce Presence — Overview

**Area:** Workforce → Presence (`/workforce`)  
**Trigger:** User clicks the Workforce pillar icon, or navigates to `/workforce`  
**Required Permission:** `workforce:read`

## Purpose

The Presence screen is the default landing for the Workforce pillar. It shows a live card grid of all employees the user has access to see. Each card combines three data points — online status, productivity score, and current task — so managers can understand who is working and how effectively without switching between tabs or views.

If the exception engine or desktop agent detects a problem with an employee (missed punch, anomaly, biometric mismatch), that employee's card is escalated: a red alert banner appears on the card and it is sorted to the top of the grid.

## Card Anatomy

```
┌──────────────────────────────────────────┐
│ 🔴 AGENT ALERT: Missed clock-in 09:00   │  ← alert banner (only when flagged)
├──────────────────────────────────────────┤
│  [Avatar]  Sarah Johnson                 │
│            Senior Engineer   ● Online    │  ← name, job title, online status dot
│  Productivity  ████████░░  82%          │  ← weekly productivity score
│  Now: "Fix login redirect bug"           │  ← current assigned task (from WMS)
└──────────────────────────────────────────┘
```

**Card data sources:**
| Card Element | Source Module |
|---|---|
| Online status dot (●) | workforce-presence |
| Productivity % | productivity-analytics |
| Current task text | WMS task module (active `TASK` assigned to this user) |
| Alert banner | exception-engine + agent-gateway |

**Online status dot colours:**
- Green ● — Clocked in and active
- Amber ● — On break
- Grey ● — Offline / not clocked in
- Red ● — Exception flagged

## Card Sort Order

1. Agent-flagged cards — sorted to top, ordered by exception severity (critical → high → medium)
2. Online employees — sorted alphabetically
3. On-break employees
4. Offline employees

## Flow Steps

1. User opens Workforce pillar — default route is `/workforce`
2. System loads all employees in the entity scope that the user has `workforce:read` access to
3. Cards render in sort order (flagged first, then online, then break, then offline)
4. Live updates stream via SignalR — presence status and productivity scores update without page refresh
5. User clicks any card → navigates to `/workforce/[employeeId]` (Employee Activity Detail)

## Filtering and Search

- Search bar filters cards by employee name or job title
- Department filter (dropdown) — narrows to employees within a department
- Status filter — show only: Online / On Break / Offline / Flagged

## Related Flows

- [[Userflow/Workforce-Presence/employee-activity-detail|Employee Activity Detail]]
- [[Userflow/Work-Management/wm-overview|WMS Overview]]
- [[Userflow/Work-Management/resource-flow|Resource Management]]
```

- [ ] **Step 2: Commit**

```bash
git add Userflow/Workforce-Presence/presence-overview.md
git commit -m "docs(userflow): workforce presence card view — anatomy, sort order, agent escalation"
```

---

## Task 13: Employee Activity Detail Userflow

**Files:**
- Create: `Userflow/Workforce-Presence/employee-activity-detail.md`

- [ ] **Step 1: Create the file**

```markdown
# Employee Activity Detail

**Area:** Workforce → Presence → Employee (`/workforce/[employeeId]`)  
**Trigger:** User clicks an employee card on the Presence screen  
**Required Permission:** `workforce:read` (view); `activity:read:team` (view another employee's activity)

## Purpose

The activity detail screen shows what a specific employee has been working on. It is the drill-down from their presence card. The screen combines time logs, task activity, and productivity analytics into a single filterable timeline — replacing the old Activity tab.

## Layout

```
← Back to Presence                                  [Link: View People Profile]

[Avatar] Sarah Johnson — Senior Engineer   ● Online
Productivity this week: ████████░░ 82%    Exception: None

──────────────────────────────────────────
Filters: [Date Range ▾]  [Task ▾]  [Project ▾]
──────────────────────────────────────────

Activity Timeline
─────────────────
09:15  Logged 45min on "Fix login redirect bug"        [Project: Auth Revamp]
10:02  Status changed: In Progress → In Review         [Task: Fix login redirect bug]
11:30  Added comment on "API timeout investigation"    [Project: Backend Stability]
13:00  Clock-in resumed after lunch break
14:15  Logged 1h 10min on "Write unit tests for auth"  [Project: Auth Revamp]
```

## Data Sources

| Section | Source |
|---|---|
| Online status, break/clock events | workforce-presence module |
| Productivity score | productivity-analytics module |
| Time logs | WMS time module (`TIME_LOG`) |
| Task status changes | WMS activity log (`ACTIVITY_LOG`) |
| Comments | WMS collab module (`COMMENT`) |
| Exception history | exception-engine |

## Flow Steps

1. User clicks an employee card on the Presence screen
2. System navigates to `/workforce/[employeeId]`
3. System loads: employee summary (name, title, status, productivity score), activity timeline for the current day
4. Timeline shows events in reverse-chronological order: time logs, task status changes, comments, clock events
5. User applies filters:
   - **Date Range** — select a custom range or preset (today / this week / last 7 days / this month)
   - **Task** — filter timeline to events for a specific task
   - **Project** — filter timeline to events for a specific project
6. Filtered timeline re-renders immediately
7. User clicks "View People Profile" → navigates to `/people/employees/[employeeId]`

## Exception History

If the employee has active or recent exceptions (from the exception-engine), an "Exceptions" section appears below the summary:
- Lists each exception: type, timestamp, severity, resolution status
- Exceptions sourced from the exception-engine module

## Related Flows

- [[Userflow/Workforce-Presence/presence-overview|Workforce Presence]]
- [[Userflow/Work-Management/task-flow|Task Management]]
- [[Userflow/Work-Management/time-tracking-flow|Time Tracking]]
```

- [ ] **Step 2: Commit**

```bash
git add Userflow/Workforce-Presence/employee-activity-detail.md
git commit -m "docs(userflow): employee activity detail — filterable timeline, data sources"
```

---

## Task 14: Chat Userflow

**Files:**
- Create: `Userflow/Chat/chat-overview.md`

- [ ] **Step 1: Create the file**

```markdown
# Chat

**Area:** Chat pillar (`/chat`)  
**Trigger:** User clicks the Chat icon on the icon rail  
**Required Permission:** `chat:read` (view channels); `chat:write` (send messages)

## Purpose

Chat is real-time team communication within ONEVO. It is a first-class pillar — not nested inside Workforce — because communication happens across HR, project, and org contexts. Channels can be tied to projects, teams, or be open workspace-wide.

## Key Entities

| Entity | Role |
|---|---|
| `CHANNEL` | A named conversation space — public, private, or project-linked |
| `CHANNEL_MEMBER` | User-to-channel membership with role |
| `MESSAGE` | A single chat message with optional attachments and reactions |
| `MESSAGE_REACTION` | Emoji reaction on a message |
| `MESSAGE_ATTACHMENT` | File attached to a message (linked to `FILE_ASSET`) |
| `DIRECT_MESSAGE_CHANNEL` | A private 1:1 or group DM conversation |
| `DM_PARTICIPANT` | Members of a DM conversation |
| `MESSAGE_READ_RECEIPT` | Tracks who has read which messages |

## Flow Steps

### View Channels (`/chat`)
1. User opens the Chat pillar
2. System loads the sidebar of channels the user is a member of, grouped:
   - **Direct Messages** — 1:1 and group DMs
   - **Channels** — workspace public channels and private channels user belongs to
3. Unread channels are bolded with an unread count badge
4. User clicks a channel to open its message thread

### Send a Message
1. User opens a channel or DM
2. User types in the message input and presses Enter (or clicks Send)
3. System creates a `MESSAGE` record and delivers it to all channel members via SignalR
4. `MESSAGE_READ_RECEIPT` is created for the sender; others receive receipts as they view

### Create a Channel
1. User clicks "+ New Channel" (requires `chat:write`)
2. User enters: channel name, description, type (public / private)
3. User optionally links the channel to a WMS project
4. System creates `CHANNEL` and adds the creator as a member with role "admin"
5. User invites other members

### Start a Direct Message
1. User clicks "+ New DM"
2. User searches for one or more employees within the entity scope
3. System creates `DIRECT_MESSAGE_CHANNEL` and `DM_PARTICIPANT` records
4. Conversation opens immediately

### React to a Message
1. User hovers over a message and clicks the emoji picker
2. User selects an emoji — system creates `MESSAGE_REACTION`
3. Reaction appears on the message with a count; clicking again removes it

### Attach a File
1. User clicks the attachment icon in the message input
2. User uploads a file — system creates `FILE_ASSET` and `MESSAGE_ATTACHMENT` records
3. Attachment is displayed inline in the message thread

## Connection Points

| Connects to | How |
|---|---|
| Workforce → Projects | A channel can be linked to a WMS project for project-specific communication |
| People → Employees | DM participants are ONEVO employees — name and avatar from their profile |
| Inbox | @mentions in a channel message create an Inbox notification for the mentioned user |

## Related Flows

- [[Userflow/Work-Management/wm-overview|WMS Overview]]
- [[Userflow/Work-Management/task-flow|Task Management]]
```

- [ ] **Step 2: Commit**

```bash
git add Userflow/Chat/chat-overview.md
git commit -m "docs(userflow): chat flow — channels, DMs, messages, reactions, file attachments"
```

---

## Task 15: Update Workforce Presence Module Overview

**Files:**
- Modify: `modules/workforce-presence/overview.md`

- [ ] **Step 1: Find the section describing the current UI and replace it**

Open `modules/workforce-presence/overview.md`. Find any section that describes the three-tab layout (Activity tab, Work Insights tab, Online Status tab). Replace it with:

```markdown
## Frontend — Presence Card View

The workforce-presence module surfaces on the Workforce pillar default screen (`/workforce`) as a live card grid.

**Card per employee shows:**
- Online status dot — sourced from this module (clocked-in, break, offline)
- Productivity score — sourced from productivity-analytics module
- Current task — sourced from WMS task module
- Agent alert banner — sourced from exception-engine (when flagged)

**Replaced:** The previous 3-tab design (Activity tab, Work Insights tab, Online Status tab) is replaced by this single card grid. Online status is embedded in each card. Productivity is embedded in each card. Activity is the drill-down at `/workforce/[employeeId]`.

**Agent escalation:** When the exception-engine or agent-gateway detects an issue (missed punch, biometric anomaly, late clock-in), the employee's card receives a red alert banner and is sorted to the top of the grid.

See [[Userflow/Workforce-Presence/presence-overview|Presence Overview]] for the full flow.
```

- [ ] **Step 2: Commit**

```bash
git add modules/workforce-presence/overview.md
git commit -m "docs(modules): update workforce-presence overview — card view replaces 3-tab model"
```

---

## Task 16: Update Calendar Module Overview

**Files:**
- Modify: `modules/calendar/overview.md`

- [ ] **Step 1: Add the scheduling items section**

Open `modules/calendar/overview.md`. At the end of the file (or after the main features section), add:

```markdown
## Calendar Panel Navigation Items

The Calendar pillar expansion panel contains four items:

| Label | Route | Purpose |
|---|---|---|
| Calendar | `/calendar` | Unified view — leave dates, public holidays, review cycles, and shift schedule overlays |
| Schedules | `/calendar/schedule` | Shift schedule management — view and edit employee shift patterns |
| Attendance | `/calendar/attendance` | Attendance correction requests — adjust clock-in/out records |
| Overtime | `/calendar/overtime` | Overtime request submission and approval |

**Why scheduling lives in Calendar (not Workforce):**
Schedules, Attendance, and Overtime are time-visual concepts — they are understood in the context of a calendar timeline. The Workforce pillar is for doing work (projects, tasks). The Calendar pillar is for scheduling when work happens.

**Connection to WMS:**
- Shift schedule hours from this module feed into WMS Resource Management as the available capacity baseline for each employee.
- Approved timesheets from WMS Time Tracking create Attendance correction records here when discrepancies exist.
- Excess hours from approved timesheets create Overtime entries here for manager approval.

See [[Userflow/Work-Management/time-tracking-flow|Time Tracking Flow]] for the full overtime and attendance connection.
```

- [ ] **Step 2: Commit**

```bash
git add modules/calendar/overview.md
git commit -m "docs(modules): update calendar overview — add scheduling items and WMS connection"
```

---

## Task 17: Update Shift Schedule Setup Userflow

**Files:**
- Modify: `Userflow/Workforce-Presence/shift-schedule-setup.md`

- [ ] **Step 1: Add the WMS connection note**

Open `Userflow/Workforce-Presence/shift-schedule-setup.md`. At the end of the file (after the last section), add:

```markdown
## Connection to Work Management

Shift schedule data from this flow feeds directly into WMS Resource Management:

- **Capacity baseline:** Each employee's scheduled hours per day/week (from their shift pattern) become the capacity baseline in WMS Resource Planning (`CAPACITY_SNAPSHOT`).
- **Overtime threshold:** When an employee's WMS time logs exceed their scheduled shift hours, the excess is flagged as potential overtime. The overtime entry (`OVERTIME_ENTRY`) is created automatically when the timesheet is approved.
- **Availability for sprint planning:** Resource management uses scheduled hours to determine how many hours an employee can realistically be allocated to a project sprint.

See [[Userflow/Work-Management/time-tracking-flow|Time Tracking Flow]] and [[Userflow/Work-Management/resource-flow|Resource Management Flow]].
```

- [ ] **Step 2: Commit**

```bash
git add Userflow/Workforce-Presence/shift-schedule-setup.md
git commit -m "docs(userflow): add WMS capacity and overtime connection to shift schedule setup"
```

---

## Task 18: Update Userflow README Index

**Files:**
- Modify: `Userflow/README.md`

- [ ] **Step 1: Add the Work Management section**

Open `Userflow/README.md`. After the last existing section in the flow index, add:

```markdown
## Work Management — (`workforce:read` + feature-specific permissions)

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Work-Management/wm-overview\|WMS Overview]] | Module map, ownership, HR integration points | Documented | MUST |
| [[Userflow/Work-Management/project-flow\|Project Management]] | Project CRUD, membership, milestones, change control | Documented | MUST |
| [[Userflow/Work-Management/task-flow\|Task Management]] | Task lifecycle, bugs, submission, approval | Documented | MUST |
| [[Userflow/Work-Management/planning-flow\|Planning — Sprints and Boards]] | Sprints, boards, roadmap, releases | Documented | MUST |
| [[Userflow/Work-Management/goals-okr-flow\|Goals and OKRs]] | Objectives, key results, check-ins, alignment | Documented | MUST |
| [[Userflow/Work-Management/time-tracking-flow\|Time Tracking]] | Time logs, timesheets, overtime and attendance connections | Documented | MUST |
| [[Userflow/Work-Management/resource-flow\|Resource Management]] | Capacity, skills, allocation planning | Documented | MUST |
```

- [ ] **Step 2: Add the Chat section**

After the Work Management section, add:

```markdown
## Chat — (`chat:read`)

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Chat/chat-overview\|Chat Overview]] | Channels, DMs, messages, reactions, file attachments | Documented | MUST |
```

- [ ] **Step 3: Update the Workforce Presence section**

Find the existing Workforce Presence section in `Userflow/README.md`. Add the two new flows to its table:

```markdown
| [[Userflow/Workforce-Presence/presence-overview\|Presence Overview]] | Live card grid, agent escalation, card anatomy | Documented | MUST |
| [[Userflow/Workforce-Presence/employee-activity-detail\|Employee Activity Detail]] | Activity timeline, filters (date/task/project), productivity breakdown | Documented | MUST |
```

- [ ] **Step 4: Commit**

```bash
git add Userflow/README.md
git commit -m "docs(userflow): add Work Management, Chat sections and new Workforce Presence flows to index"
```

---

## Self-Review

**Spec coverage check:**
- ✅ Sidebar nav — canonical reference with all pillars, items, routes, permission keys (Task 1)
- ✅ Topbar legal entity switcher (Task 2)
- ✅ App structure updated — WMS routes, org extensions, chat, 3-tab removal (Task 3)
- ✅ Routing updated — entity context, WMS guards (Task 4)
- ✅ WMS overview userflow (Task 5)
- ✅ Project management flow (Task 6)
- ✅ Task management flow — lifecycle, bugs, submission (Task 7)
- ✅ Planning flow — sprints, boards, roadmap, releases (Task 8)
- ✅ Goals/OKR flow (Task 9)
- ✅ Time tracking flow — overtime + attendance HR connections (Task 10)
- ✅ Resource management flow — capacity, skills, allocation (Task 11)
- ✅ Presence card view — agent escalation, card anatomy, sort order (Task 12)
- ✅ Employee activity detail — filters, data sources (Task 13)
- ✅ Chat flow — channels, DMs, messages (Task 14)
- ✅ Workforce presence module updated — 3-tab → card view (Task 15)
- ✅ Calendar module updated — scheduling items + WMS connection (Task 16)
- ✅ Shift schedule setup updated — WMS capacity connection (Task 17)
- ✅ Userflow README updated — WMS, Chat, Workforce sections (Task 18)

**Placeholder scan:** None found. All steps contain complete content.

**Type consistency check:**
- Permission keys used in sidebar-nav.md match usage in all userflow files ✅
- Routes in sidebar-nav.md match routes in app-structure.md update ✅
- WMS entity names (e.g., `TASK`, `SPRINT`, `OBJECTIVE`) match wms-work-management-flow.md source ✅
- `EntitySwitcher` component name used consistently in topbar.md and app-structure.md ✅
- All cross-reference links use `[[path|Label]]` format consistently ✅
