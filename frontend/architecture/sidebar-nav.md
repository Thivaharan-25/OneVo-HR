# Sidebar Navigation Map

Canonical reference for the ONEVO shell navigation. Navigation components, permission gates, and cross-module links must reference this document for route paths, label names, and permission keys. Never hardcode a label or route — always verify against this file.

## Design Principles

- **Business language labels** — "Activity Trail" not "Audit Logs". "People Access" not "Users".
- **No role name checks** — all visibility is permission-key driven, never role-name driven.
- **Panels only where needed** — Home, Inbox, Automation Center, and Chat have no expansion panels.
- **Automation is first-class** — Automation Center is not hidden inside Settings because customers use it to run approvals, alerts, requests, escalations, and follow-ups.
- **WMS lives in Workforce** — all Work Management System screens route under `/workforce/`.
- **Scheduling lives in Calendar** — Schedules, Attendance, and Overtime belong in Calendar, not Workforce.

## Topbar

```
[■ Acme Malaysia Sdn Bhd  ▾]  |  [  Search...  ⌘K  ]  |  🔔  ☀  [Avatar ▾]
```

Left: Legal entity name + hierarchy switcher dropdown  
Center: Search — command palette (⌘K / Ctrl+K)  
Right: Notification bell · Theme toggle · User avatar menu

See [[frontend/architecture/topbar|Topbar Architecture]] for full legal entity switcher design.


## Responsive Navigation Mapping

The route map below is the single source of truth for both desktop sidebar navigation and mobile/tablet drawer navigation.

| Viewport | Component | Mapping rule |
|:---------|:----------|:-------------|
| Mobile `<640px` | `MobileNavDrawer` | Render visible pillars as accordion groups. Direct routes navigate immediately; panel routes expand to show sub-items. |
| Tablet `640-1023px` | `MobileNavDrawer` | Same as mobile, with optional two-column grouping if space allows. |
| Laptop `1024-1279px` | `NavRail` + flyout/collapsed `ExpansionPanel` | Show rail icons. Open sub-items as flyout or temporary panel. |
| Desktop `>=1280px` | `NavRail` + `ExpansionPanel` | Full rail and pinnable panel. |

Rules:

- Never create a separate mobile route map.
- Permission filtering, badges, active states, labels, and routes must come from the same pillar config.
- Drawer navigation must include search access, entity context, profile/settings access, and close-on-navigation behavior.

## Icon Rail — 10 Pillars

Display order (top to bottom). A separator line appears between Chat (8) and Admin (9).

| Position | Pillar | Lucide Icon | Has Panel | Default Route | Visible When |
|---|---|---|---|---|---|
| 1 | Home | `House` | No | `/` | Any authenticated user |
| 2 | Inbox | `Inbox` | No | `/inbox` | Any authenticated user |
| 3 | People | `Users` | Yes | `/people/employees` | `employees:read` OR `leave:read` |
| 4 | Workforce | `LayoutDashboard` | Yes | `/workforce` | `workforce:view` |
| 5 | Org | `Network` | Yes | `/org` | `org:read` |
| 6 | Calendar | `Calendar` | Yes | `/calendar` | `calendar:read` |
| 7 | Automation Center | `Workflow` | No | `/automation` | `automation:read` |
| 8 | Chat | `MessageCircle` | No | `/chat` | `chat:read` |
| — | *separator* | — | — | — | — |
| 9 | Admin | `Shield` | Yes | `/admin/users` | `users:read` |
| 10 | Settings | `Settings` | Yes | `/settings/general` | `settings:read` |

See [[frontend/design-system/components/nav-rail|Nav Rail]] for exact dimensions, colors, and Tailwind implementation.

## Expansion Panel Items

### People

| Label | Route | Permission Key | Notes |
|---|---|---|---|
| Employees | `/people/employees` | `employees:read` | Directory, profiles, lifecycle |
| Leave | `/people/leave` | `leave:read` | Requests, calendar, balances, policies |

### Workforce

| Label | Route | Permission Key | WMS Module(s) | Notes |
|---|---|---|---|---|
| Presence | `/workforce` | `workforce:view` | workforce-presence, productivity-analytics, exception-engine | Default — live employee card grid |
| Projects | `/workforce/projects` | `projects:read` | project | All projects in entity scope |
| My Work | `/workforce/my-work` | `tasks:read` | task | My assigned tasks across all projects |
| Planner | `/workforce/planner` | `sprints:read` | planning | Sprints, Boards, Roadmap, Releases |
| Goals | `/workforce/goals` | `okr:read` | okr | Objectives, key results, check-ins |
| Docs | `/workforce/docs` | `documents:read` | collab | Documents and Wiki |
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
| Schedules | `/calendar/schedule` | `calendar:read` | Shift schedules (was "Shifts & Schedules") |
| Attendance | `/calendar/attendance` | `attendance:read` | Attendance corrections (was "Attendance Correction") |
| Overtime | `/calendar/overtime` | `attendance:read` | Overtime requests and approvals |

### Chat (no panel)

Direct navigation to `/chat`. Full chat UI renders in the content area.  
Permission key: `chat:read`

### Automation Center (no panel)

Direct navigation to `/automation`. The page normally opens into the automation builder or the customer's existing automations. Templates appear only after the user clicks Templates.  
Permission key: `automation:read`; create/edit actions require `automation:manage`.

### Inbox (no panel)

Direct navigation to `/inbox`. Unified approvals, tasks, mentions, exception alerts.  
Permission key: any authenticated user (content filtered by their permissions).

### Admin

| Label | Route | Permission Key | Was Named |
|---|---|---|---|
| People Access | `/admin/users` | `users:manage` | Users |
| Permissions | `/admin/roles` | `roles:manage` | Roles |
| Activity Trail | `/admin/audit` | `settings:system` | Audit Logs |
| Agents | `/admin/agents` | `agent:manage` | — |
| Devices | `/admin/devices` | `settings:device` | — |
| Data & Privacy | `/admin/compliance` | `settings:system` | Compliance |

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
