# Permissions Reference

**Total explicitly grantable:** 106 permissions across 28 modules  
**Related flows:** [[Userflow/Auth-Access/permission-assignment|Permission Assignment]] · [[Userflow/Auth-Access/role-creation|Role Creation]]

---

## Universal Permissions (Auto-granted - never assign manually)

These are given to every active employee automatically when they enter the system. They are resolved by the auth layer, not assigned through roles, and they cannot be revoked through role permissions or employee overrides.

| Permission | What it gives |
|:-----------|:--------------|
| `inbox:read` | Access to inbox (content adapts by role) |
| `notifications:read` | Receive notifications |
| `employees:read-own` | View own employee profile |
| `leave:read-own` | View own leave balance and history |
| `attendance:read-own` | View own attendance and presence history |
| `payroll:read-own` | View own payslips and payroll history |
| `performance:read-own` | View own performance records and review tasks |
| `documents:read-own` | View documents assigned to self |
| `calendar:read` | View calendar |
| `activity:read:self` | View own activity log |
| `workforce:dashboard` | Access workforce dashboard (shows team data if manager, own data if not; manager can toggle to own view) |
| *(no code)* | Personal app account linking - connect own Teams/Slack/Google account from profile settings |

Universal permissions must not appear in the role creation permission browser, role permission save payloads, or per-employee override add/remove lists. They may still appear in API endpoint documentation to explain the access check used for self-service routes.

---

## Explicitly Grantable Permissions

### Employees
| # | Permission | Description |
|:--|:-----------|:------------|
| 1 | `employees:read` | View all employees in scope |
| 2 | `employees:read-team` | View direct reports only |
| 3 | `employees:write` | Create, update employees |
| 4 | `employees:delete` | Delete employee records |

### Organization
| # | Permission | Description |
|:--|:-----------|:------------|
| 5 | `org:read` | View org structure, departments, hierarchy |
| 6 | `org:manage` | Create and edit org structure, departments |

### Leave
| # | Permission | Description |
|:--|:-----------|:------------|
| 7 | `leave:read` | View leave records for all employees in scope |
| 8 | `leave:read-team` | View leave records for direct reports only |
| 9 | `leave:create` | Apply for leave on behalf of others |
| 10 | `leave:approve` | Approve or reject leave requests |
| 11 | `leave:manage` | Manage leave types, policies, balances |

### Attendance
| # | Permission | Description |
|:--|:-----------|:------------|
| 12 | `attendance:read` | View attendance records for all employees in scope |
| 13 | `attendance:read-team` | View attendance records for direct reports only |
| 14 | `attendance:approve` | Approve overtime and attendance corrections |
| 15 | `attendance:write` | Correct attendance records |

### Payroll
| # | Permission | Description |
|:--|:-----------|:------------|
| 16 | `payroll:read` | View payroll records and salary data |
| 17 | `payroll:write` | Edit payroll records |
| 18 | `payroll:approve` | Approve payroll runs |
| 19 | `payroll:run` | Execute payroll processing |

### Performance
| # | Permission | Description |
|:--|:-----------|:------------|
| 20 | `performance:read` | View performance records for all employees in scope |
| 21 | `performance:read-team` | View performance records for direct reports only |
| 22 | `performance:write` | Submit and edit performance reviews |
| 23 | `performance:manage` | Manage review cycles, templates, goals |

### Skills
| # | Permission | Description |
|:--|:-----------|:------------|
| 24 | `skills:read` | View skills profiles across employees |
| 25 | `skills:write` | Update own skills profile |
| 26 | `skills:write-team` | Update skills for direct reports |
| 27 | `skills:validate` | Validate or endorse skills for employees |
| 28 | `skills:manage` | Manage skill library and categories |

### Expense
| # | Permission | Description |
|:--|:-----------|:------------|
| 29 | `expense:read` | View expense records in scope |
| 30 | `expense:create` | Submit expense claims |
| 31 | `expense:approve` | Approve or reject expense claims |
| 32 | `expense:manage` | Manage expense categories, policies, limits |

### Calendar
| # | Permission | Description |
|:--|:-----------|:------------|
| 33 | `calendar:write` | Create and manage calendar events for others |
| 33a | `calendar:admin` | Manage country holiday sync, legal-entity calendar overrides, and calendar integrations |

### Notifications
| # | Permission | Description |
|:--|:-----------|:------------|
| 34 | `notifications:manage` | Manage notification templates and delivery settings |

### Settings
| # | Permission | Description |
|:--|:-----------|:------------|
| 35 | `settings:read` | View any settings section (read-only) |
| 36 | `settings:admin` | Manage core system settings — timezone, work hours, privacy mode, data retention |
| 37 | `settings:billing` | Manage subscription, plan, and payment methods |
| 38 | `settings:branding` | Manage company logo, colors, and custom domain |
| 39 | `settings:integrations` | Connect or disconnect tenant-wide app integrations via OAuth (Teams, Slack, LMS) and enter migration API keys for onboarding from existing HR systems. Google/Outlook Calendar is managed under `calendar:admin` / user-owned Calendar connections. |
| 40 | `settings:notifications` | Manage notification templates and delivery channels |
| 41 | `settings:alerts` | Configure alert thresholds and escalation rules |
| 42 | `settings:system` | Manage system-level settings — audit config, data retention policies |
| 43 | `settings:device` | View biometric device connection status |
| 44 | `settings:device:configure` | Add, remove, and configure biometric device integrations |

### Users & Roles
| # | Permission | Description |
|:--|:-----------|:------------|
| 45 | `users:read` | View user accounts |
| 46 | `users:manage` | Create, suspend, and manage user accounts |
| 47 | `roles:read` | View roles and their permission sets |
| 48 | `roles:manage` | Create and edit roles, assign permissions |

### Billing
| # | Permission | Description |
|:--|:-----------|:------------|
| 49 | `billing:read` | View billing history and invoices |
| 50 | `billing:manage` | Manage billing and subscription changes |

### Integrations
| # | Permission | Description |
|:--|:-----------|:------------|
| 51 | `integrations:read` | View configured integrations |
| 52 | `integrations:manage` | Configure and manage third-party integrations |

### Analytics
| # | Permission | Description |
|:--|:-----------|:------------|
| 53 | `analytics:read` | View analytics data |
| 54 | `analytics:view` | Access analytics dashboards |
| 55 | `analytics:export` | Export analytics reports |
| 56 | `analytics:write` | Create and save custom analytics views |

### Monitoring
| # | Permission | Description |
|:--|:-----------|:------------|
| 57 | `monitoring:view-settings` | View monitoring toggles and employee overrides |
| 58 | `monitoring:configure` | Enable/disable monitoring features, set employee overrides |

### Exceptions
| # | Permission | Description |
|:--|:-----------|:------------|
| 59 | `exceptions:view` | View exception alerts |
| 60 | `exceptions:acknowledge` | Acknowledge and resolve exception alerts |
| 61 | `exceptions:manage` | Manage exception rules and thresholds |

### Verification
| # | Permission | Description |
|:--|:-----------|:------------|
| 62 | `verification:view` | View AWS Rekognition identity verification results |
| 63 | `verification:review` | Escalate verification cases up the hierarchy, change severity level (critical, high, etc.) |
| 64 | `verification:configure` | Configure AWS Rekognition settings and verification rules |

> **Escalation rule:** Approval and alerts are sent to the person one step above in the org hierarchy. If that person does not have `verification:review` feature access, the system skips to the next person up the chain. Works in conjunction with the workflow engine.

### Workforce Intelligence
| # | Permission | Description |
|:--|:-----------|:------------|
| 65 | `workforce:view` | View workforce intelligence data and reports |
| 66 | `workforce:manage` | Manage workforce intelligence settings |

### Agent Gateway
| # | Permission | Description |
|:--|:-----------|:------------|
| 67 | `agent:command` | Send commands to agents |
| 68 | `agent:manage` | Manage agent configurations |
| 69 | `agent:register` | Register new agents |
| 70 | `agent:view-health` | View agent health and status |

### Documents
| # | Permission | Description |
|:--|:-----------|:------------|
| 71 | `documents:read` | View documents |
| 72 | `documents:write` | Upload and edit documents |
| 73 | `documents:approve` | Approve document submissions |
| 74 | `documents:manage` | Manage document categories and policies |
| 75 | `documents:admin` | Full document administration including deletion and access control |

### Grievance
| # | Permission | Description |
|:--|:-----------|:------------|
| 76 | `grievance:read` | View grievance cases |
| 77 | `grievance:write` | Submit grievance cases |
| 78 | `grievance:manage` | Manage and resolve grievance cases |

### Reports
| # | Permission | Description |
|:--|:-----------|:------------|
| 79 | `reports:read` | View reports |
| 80 | `reports:create` | Create and run reports |

### Chat
| # | Permission | Description |
|:--|:-----------|:------------|
| 81 | `chat:read` | Read chat messages |
| 82 | `chat:write` | Send chat messages |
| 83 | `chat:manage` | Manage channels, moderate messages |

### Tasks
| # | Permission | Description |
|:--|:-----------|:------------|
| 84 | `tasks:read` | View tasks |
| 85 | `tasks:write` | Create and edit tasks |
| 86 | `tasks:approve` | Approve task completions |
| 87 | `tasks:delete` | Delete tasks |

### Time Tracking
| # | Permission | Description |
|:--|:-----------|:------------|
| 88 | `time:read` | View time logs |
| 89 | `time:write` | Log and edit time entries |
| 90 | `time:approve` | Approve time submissions |

### Projects
| # | Permission | Description |
|:--|:-----------|:------------|
| 91 | `projects:read` | View projects |
| 92 | `projects:write` | Edit project details |
| 93 | `projects:create` | Create new projects |

### Work Management (WMS)
| # | Permission | Description |
|:--|:-----------|:------------|
| 94 | `okr:read` | View OKRs and goals |
| 95 | `okr:write` | Create and update OKRs |
| 96 | `wiki:read` | View wiki pages |
| 97 | `wiki:write` | Create and edit wiki pages |
| 98 | `sprints:read` | View sprints |
| 99 | `sprints:manage` | Create and manage sprints |
| 100 | `workspaces:read` | View workspaces |
| 101 | `workspaces:create` | Create new workspaces |
| 102 | `workspaces:manage` | Manage workspace settings and members |
| 103 | `resources:read` | View resource allocations |
| 104 | `resources:manage` | Manage resource planning |
| 105 | `roadmaps:read` | View roadmaps |
| 106 | `roadmaps:write` | Create and edit roadmaps |

---

## Removed from Original List

These were in the original 153 but are invalid, renamed, or redundant:

| Original | Reason |
|:---------|:-------|
| `admin:*` (11 entries) | Replaced by `settings:admin`, `roles:manage`, `users:manage`, `agent:manage`, and `settings:system` depending on route |
| `agent:read` | Renamed to `agent:view-health` |
| `agents:manage` | Renamed to `agent:manage` |
| `alerts:manage` | Covered by `settings:alerts` |
| `analytics:manage` | Covered by `analytics:write` |
| `analytics:view:self` / `analytics:view:ceo` | Covered by `analytics:view` plus server-side scope |
| `approvals:read` | Not a standalone permission - approvals are per-module |
| `attendance:manage` | Covered by `attendance:write` |
| `attendance:read-own` | Universal |
| `audit:read` | Covered by `settings:system` |
| `branding:manage` | Renamed to `settings:branding` |
| `worksync:*` module permissions | Internal WorkSync module permissions; no bridge API scopes are active |
| `calendar:sync` | Covered by `settings:integrations` |
| `compliance:manage` | Not defined |
| `departments:read` | Covered by `org:read` |
| `deployment:write` | Not defined |
| `devices:manage` | Split into `settings:device` + `settings:device:configure` |
| `docs:read` | Renamed to `documents:read` |
| `documents:read-own` | Universal |
| `employee:create` / `employees:create` / `employees:update` / `employees:bulk-update` | All covered by `employees:write` |
| `exceptions:read` | Renamed to `exceptions:view` |
| `exceptions:resolve` | Same as `exceptions:acknowledge` - removed |
| `expense:admin` | Covered by `expense:manage` |
| `goals:read` / `goals:write` | Renamed to `okr:read` / `okr:write` |
| `hr:read` | Covered by `employees:read` |
| `inbox:read` | Universal |
| `calendar:read` | Universal |
| `leave:none` | Not a permission - sentinel value |
| `leave:read-own` | Universal |
| `leave:write` | Covered by `leave:create` + `leave:manage` |
| `monitoring:update-settings` | Renamed to `monitoring:configure` |
| `notifications:configure` | Covered by `settings:notifications` |
| `notifications:read` | Universal |
| `org:write` | Covered by `org:manage` |
| `overtime:read` | Covered by `attendance:read` |
| `payroll:manage` | Renamed to `payroll:write` |
| `payroll:read-own` | Universal |
| `payroll:view` | Renamed to `payroll:read` |
| `payroll:view-salary` | Covered by `payroll:read` |
| `performance:read-own` | Universal |
| `people:read` | Covered by `employees:read` |
| `planning:read` / `planning:write` | Replaced by `sprints:*`, `roadmaps:*`, and `projects:*` |
| `platform:admin` | Renamed to `settings:admin` |
| `project:create` | Typo - correct code is `projects:create` |
| `reports:manage` | Covered by `reports:create` |
| `schedule:read` | Covered by `calendar:read` (universal) |
| `settings:manage` / `settings:write` | Redundant - covered by specific `settings:*` sub-permissions |
| `sprint:manage` | Typo - correct code is `sprints:manage` |
| `task:assign` | Covered by `tasks:write` |
| `teams:read` | Covered by `org:read` |
| `verification:read` | Renamed to `verification:view` |
| `verification:review` | Confirmed as separate - kept |
| `wms:chat` / `wms:okr` / `wms:projects` | Wrong prefix - use `chat:*`, `okr:*`, `projects:*` |
| `workforce:approve-overtime` | Same as `attendance:approve` - removed |
| `workforce:correct-attendance` | Same as `attendance:write` - removed |
| `workforce:dashboard` | Universal |
| `workforce:manage-biometric` | Renamed to `settings:device:configure` |
| `workforce:read` | Renamed to `workforce:view` |
---

## Validation Rules

- Universal permissions are auto-granted to every active employee and are never manually assigned or revoked.
- Explicitly grantable permissions are the only permissions shown in role creation, role editing, and employee override pickers.
- Any permission used by a user flow, frontend route, API endpoint, or module overview must appear either in Universal Permissions or Explicitly Grantable Permissions.
- Any legacy permission must appear in Removed from Original List with a replacement or a reason.
