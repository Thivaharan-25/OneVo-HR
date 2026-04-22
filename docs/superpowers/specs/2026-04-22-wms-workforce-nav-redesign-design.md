# WMS Integration + Navigation Architecture Redesign — Design Spec

**Date:** 2026-04-22
**Branch:** feature/luminous-depth
**Scope:** Knowledge base only — no demo or product code changes in this phase.

---

## Problem Statement

The current navigation architecture has four compounding issues:

1. **Workforce pillar is a stub.** `/workforce/live` is a single page with 3 tabs (Activity, Work Insights, Online Status) that do not scale as WMS features are added. The WMS frontend has no home in the nav yet.
2. **Scheduling items are duplicated.** Shifts, Attendance Correction, and Overtime appear in both Workforce and Calendar panels — confusing and redundant.
3. **Labels are developer-facing.** "Audit Logs", "Feature Flags", "Monitoring", "Compliance" are not language a business user understands.
4. **Key WMS modules are unplaced.** Chat, Collaboration (Docs/Wiki), Planner (Sprints/Boards/Roadmap), Goals (OKRs), Timesheets, and Resource Analytics have no assigned home in the navigation.

---

## Design Decisions

### Decision 1 — WMS lives inside the Workforce pillar

All WMS frontend screens (Projects, My Work, Planner, Goals, Docs, Timesheets, Analytics) live under `/workforce/...`. The Workforce pillar is the single entry point for work management.

**Rationale:** Workforce is where work happens. Separating WMS into its own pillar would create an artificial split between presence data (who is working) and work data (what they are working on).

### Decision 2 — Chat gets its own icon rail pillar (no expansion panel)

Chat is cross-cutting — users discuss HR decisions, project issues, and org topics. Burying it inside the Workforce panel would make it feel like a WMS-only tool.

**Rationale:** Mirrors how ClickUp, Slack, and Notion treat messaging — first-class persistent access, not nested under a feature module.

### Decision 3 — Collaboration is embedded, not a nav item

Comments, reactions, mentions, and file attachments happen inside tasks, projects, and docs. Documents and Wiki are surfaced as "Docs" inside the Workforce panel. There is no standalone "Collaboration" nav item.

### Decision 4 — Scheduling items (Schedules, Attendance, Overtime) belong only in Calendar

These are time-visual concepts — they are best understood in a calendar context. They connect to the WMS time module via data (timesheets, overtime entries) but their UI home is Calendar.

### Decision 5 — Topbar shows Legal Entity, not workspace name

ONEVO's access model is hierarchy-scoped. The topbar entity switcher makes that hierarchy visible and operable. Users with access to multiple entities (e.g., Super Admin over a group) can switch context, changing what data is visible across the entire app.

### Decision 6 — Job Families and Legal Entities belong in the Org pillar

Both are organizational structure concepts, not system administration or configuration. Job Families define role taxonomy (used for compensation bands and career paths). Legal Entities define the corporate hierarchy. Both sit alongside Departments and Teams in Org.

### Decision 7 — Admin and Settings labels use business language

Technical labels (Audit Logs → Activity Trail, Compliance → Data & Privacy, Monitoring + Feature Flags → System) are replaced with language a business admin understands.

---

## Complete Navigation Architecture

### Topbar

```
[■ Acme Malaysia Sdn Bhd ▾]  |  [  Search...  ⌘K  ]  |  🔔  ☀  [Avatar ▾]
```

**Left — Legal Entity Switcher:**
- Shows the legal entity the user currently operates within
- Dropdown lists all entities the user has hierarchy-scoped access to
- Switching entity changes the data context across the entire app (employees, projects, reports visible)
- Only entities in the user's permission scope appear

**Center — Search (⌘K):** Command palette

**Right — Actions:** Notifications bell · Theme toggle · User avatar + menu

---

### Icon Rail (9 Pillars)

| # | Pillar | Has Panel | Notes |
|---|---|---|---|
| 1 | Home | No | Direct `/` |
| 2 | People | Yes | |
| 3 | Workforce | Yes | WMS hub |
| 4 | Org | Yes | |
| 5 | Calendar | Yes | |
| 6 | Chat | No | Direct `/chat` |
| 7 | Inbox | No | Direct `/inbox` |
| 8 | Admin | Yes | |
| 9 | Settings | Yes | |

---

### Expansion Panel Items Per Pillar

#### People
| Label | Route | Notes |
|---|---|---|
| Employees | `/people/employees` | Directory, profiles, lifecycle |
| Leave | `/people/leave` | Requests, calendar, balances, policies |

#### Workforce
| Label | Route | WMS Module | Notes |
|---|---|---|---|
| Presence | `/workforce` | workforce-presence + productivity-analytics + exception-engine | Default — card-based live view |
| Projects | `/workforce/projects` | project | All projects in workspace |
| My Work | `/workforce/my-work` | task | My assigned tasks across projects |
| Planner | `/workforce/planner` | planning | Sprints, Boards (kanban/list), Roadmap, Releases |
| Goals | `/workforce/goals` | okr | Objectives, key results, check-ins |
| Docs | `/workforce/docs` | collab | Documents + Wiki |
| Timesheets | `/workforce/time` | time | Time logs, timesheets, reports |
| Analytics | `/workforce/analytics` | productivity-analytics + resource | Productivity scores, capacity, allocation |

#### Org
| Label | Route | Notes |
|---|---|---|
| Org Chart | `/org` | Visual hierarchy |
| Departments | `/org/departments` | Department CRUD |
| Teams | `/org/teams` | Team CRUD |
| Job Families | `/org/job-families` | Role groupings for compensation bands and career paths |
| Legal Entities | `/org/legal-entities` | Create + manage entities shown in topbar switcher |

#### Calendar
| Label | Route | Notes |
|---|---|---|
| Calendar | `/calendar` | Unified: leave, holidays, review cycles |
| Schedules | `/calendar/schedule` | Shift schedules (was "Shifts & Schedules") |
| Attendance | `/calendar/attendance` | Corrections (was "Attendance Correction") |
| Overtime | `/calendar/overtime` | Overtime requests and approvals |

#### Chat (no panel)
Direct nav to `/chat` — channel list, DMs, message threads.

#### Inbox (no panel)
Direct nav to `/inbox` — unified approvals, tasks, mentions, exception alerts.

#### Admin
| Label | Route | Notes |
|---|---|---|
| People Access | `/admin/users` | User management + role assignment (was "Users") |
| Permissions | `/admin/roles` | Role + permission management (was "Roles") |
| Activity Trail | `/admin/audit` | Audit log viewer (was "Audit Logs") |
| Agents | `/admin/agents` | Desktop agent fleet |
| Devices | `/admin/devices` | Hardware terminals |
| Data & Privacy | `/admin/compliance` | GDPR, data governance (was "Compliance") |

#### Settings
| Label | Route | Notes |
|---|---|---|
| General | `/settings/general` | Tenant configuration |
| Alerts | `/settings/alert-rules` | Alert rule configuration (was "Alert Rules") |
| Notifications | `/settings/notifications` | Channel config (org-level) |
| Integrations | `/settings/integrations` | SSO, LMS, payroll providers |
| Branding | `/settings/branding` | Logo, colors, domain |
| Billing | `/settings/billing` | Subscription and plan |
| System | `/settings/system` | Merges "Monitoring" (system health, feature toggles) + "Feature Flags" (feature controls) into one page with two sections |

---

## Workforce Presence Screen Redesign

### Default: `/workforce` — Live Presence Cards

Replaces the 3-tab page (`/workforce/live`) entirely.

**Layout:** Card grid of all employees the user has access to see.

**Each card shows:**
```
┌──────────────────────────────────────────┐
│ 🔴 AGENT ALERT: Missed clock-in 09:00   │  ← only if agent flagged
├──────────────────────────────────────────┤
│  [Avatar]  Sarah Johnson                 │
│            Senior Engineer   ● Online    │
│  Productivity  ████████░░  82%          │
│  Now: "Fix login redirect bug"           │
└──────────────────────────────────────────┘
```

**Card data sources:**
- Online status dot → workforce-presence module
- Productivity % → productivity-analytics module
- Current task → WMS `TASK` assigned to this user
- Agent alert banner → exception-engine + agent-gateway detection

**Sort order:** Agent-flagged cards float to top of grid, sorted by severity. Normal cards sorted by online status (online → break → offline).

**Clicking a card** → navigates to `/workforce/[employeeId]`

### Employee Activity Detail: `/workforce/[employeeId]`

**Content:**
- Activity feed (time logs + activity log entries in chronological order)
- **Filters:** Date range · Task · Project
- Productivity breakdown (score trend, logged vs scheduled hours)
- Exception history for this employee
- Quick link → their People profile at `/people/employees/[id]`

### How the 3 tabs map to the new design:

| Old Tab | New Location |
|---|---|
| Online Status | Embedded in each card (presence dot) |
| Work Insights | Embedded in each card (productivity %) + full Analytics page |
| Activity | Click any card → `/workforce/[employeeId]` |

---

## Updated Route Tree (Workforce + Org additions)

```
workforce/
├── page.tsx                      # Presence card grid
├── [employeeId]/
│   └── page.tsx                  # Employee activity detail (filterable)
├── projects/
│   ├── page.tsx                  # All projects
│   ├── new/page.tsx
│   └── [id]/
│       ├── page.tsx              # Project overview
│       ├── board/page.tsx        # Kanban / list view
│       ├── sprints/page.tsx
│       └── roadmap/page.tsx
├── my-work/page.tsx              # My assigned tasks across projects
├── planner/page.tsx              # Sprints, boards, roadmap (workspace-level)
├── goals/
│   ├── page.tsx                  # OKR overview
│   └── [id]/page.tsx             # Objective detail
├── docs/
│   ├── page.tsx                  # Documents + Wiki list
│   └── [id]/page.tsx             # Document/Wiki page
├── time/
│   ├── page.tsx                  # My timesheet
│   └── reports/page.tsx          # Time reports
└── analytics/page.tsx            # Productivity + capacity analytics

org/
├── page.tsx                      # Org chart (existing)
├── departments/page.tsx          # (existing)
├── teams/page.tsx                # (existing)
├── job-families/                 # NEW
│   ├── page.tsx                  # Job family list
│   └── [id]/page.tsx             # Job family detail + roles
└── legal-entities/               # NEW
    ├── page.tsx                  # Legal entity list + hierarchy view
    └── [id]/page.tsx             # Entity detail + settings

chat/
└── page.tsx                      # Channel list + DM + message area
```

---

## Knowledge Base File Plan

### Files to CREATE (12 new)

| File | Purpose |
|---|---|
| `frontend/architecture/sidebar-nav.md` | Canonical sidebar map — every pillar, item, route, permission key, label |
| `frontend/architecture/topbar.md` | Legal entity switcher design, hierarchy scope, permission gating per entity |
| `Userflow/Work-Management/wm-overview.md` | What WMS is, module map, frontend vs backend ownership split |
| `Userflow/Work-Management/project-flow.md` | Project → epics → milestones → change control |
| `Userflow/Work-Management/task-flow.md` | Task lifecycle: create → assign → submit → approve → reopen; issues vs bugs |
| `Userflow/Work-Management/planning-flow.md` | Sprints, Boards, Roadmap, Releases |
| `Userflow/Work-Management/goals-okr-flow.md` | Objectives → key results → initiatives → check-ins |
| `Userflow/Work-Management/time-tracking-flow.md` | Time logs, timesheets, connection to HR overtime/attendance |
| `Userflow/Work-Management/resource-flow.md` | Capacity snapshots, skill matching, allocation planning |
| `Userflow/Workforce-Presence/presence-overview.md` | Card grid view, agent escalation, sort order, card anatomy |
| `Userflow/Workforce-Presence/employee-activity-detail.md` | Activity screen, filters (date/task/project), productivity breakdown |
| `Userflow/Chat/chat-overview.md` | Channels, DMs, messages, read receipts |

### Files to UPDATE (6 existing)

| File | What changes |
|---|---|
| `frontend/architecture/app-structure.md` | Add full WMS route tree, new org routes, Chat route, remove workforce/live tab structure, update module-to-route mapping, update page count |
| `frontend/architecture/routing.md` | Add WMS routes, entity-context switching in middleware, activity detail dynamic route |
| `modules/workforce-presence/overview.md` | Replace 3-tab description with card view + agent escalation model |
| `modules/calendar/overview.md` | Clarify Schedules/Attendance/Overtime as calendar-adjacent HR ops, note connection to WMS time module |
| `Userflow/README.md` | Add Work Management section (7 flows), Chat section (1 flow), update Workforce Presence section |
| `Userflow/Workforce-Presence/shift-schedule-setup.md` | Add connection note: schedule data feeds WMS capacity/resource planning |

---

## Execution Sequence

Write in dependency order — canonical refs first, then everything that cites them:

```
1. frontend/architecture/sidebar-nav.md         ← canonical nav reference
2. frontend/architecture/topbar.md              ← canonical topbar reference
3. frontend/architecture/app-structure.md       ← route tree update (cites sidebar-nav)
4. frontend/architecture/routing.md             ← route guards update
5. Userflow/Work-Management/wm-overview.md      ← WMS entry point (all WMS flows cite this)
6. Userflow/Work-Management/project-flow.md
7. Userflow/Work-Management/task-flow.md
8. Userflow/Work-Management/planning-flow.md
9. Userflow/Work-Management/goals-okr-flow.md
10. Userflow/Work-Management/time-tracking-flow.md
11. Userflow/Work-Management/resource-flow.md
12. Userflow/Workforce-Presence/presence-overview.md
13. Userflow/Workforce-Presence/employee-activity-detail.md
14. Userflow/Chat/chat-overview.md
15. modules/workforce-presence/overview.md      ← update
16. modules/calendar/overview.md                ← update
17. Userflow/Workforce-Presence/shift-schedule-setup.md  ← update
18. Userflow/README.md                          ← index update (last — cites all above)
```
