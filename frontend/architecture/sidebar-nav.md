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
