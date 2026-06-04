# Permissions Reference

**Total explicitly grantable:** 127 permissions across 31 modules  
**Related flows:** [[Userflow/Auth-Access/permission-assignment|Permission Assignment]] Â· [[Userflow/Auth-Access/role-creation|Role Creation]]

---

## System Permission (internal â€” seeded at provisioning; never shown in UI pickers)

| Permission | What it gives |
|:-----------|:--------------|
| `*` | Tenant-local Super Admin bypass â€” grants access to tenant endpoints regardless of permission checks inside the current tenant only; assigned only to the Super Admin role during tenant provisioning; must not appear in the role creation browser, per-employee override lists, or any assignable permission payload; does not grant platform-admin access or cross-company access without a scoped cross-company grant |

---

## Module Auto-Grant Permissions

These are given automatically to every active employee **when the tenant's subscription includes the relevant module**. They are resolved by the auth layer, never assigned through roles, and cannot be revoked through role permissions or employee overrides.

| Permission | Module Required | What it gives |
| :--------- | :-------------- | :------------ |
| `employees:read-own` | `employees` | View own employee profile |
| `leave:read-own` | `leave` | View own leave balance and history |
| `attendance:read-own` | `attendance` | View own attendance and presence history |
| `attendance:write-own` | `attendance` | Submit own attendance corrections |
| `calendar:read` | `calendar` | View calendar |
| `activity:read:self` | `monitoring` | View own activity log |
| `workforce:dashboard` | `workforce` | Access workforce dashboard |

Module auto-grant permissions must not appear in the role creation permission browser, role permission save payloads, or per-employee override add/remove lists.

> **Phase 2 note:** `payroll:read-own`, `performance:read-own`, and `documents:read-own` will be added to this table when their modules (Payroll, Performance, HR Documents) are released.

## Derived Permissions

These are computed automatically by the auth layer based on the employee's effective permission set. They cannot be assigned or revoked manually.

| Permission | Derived when |
| :--------- | :----------- |
| `inbox:read` | Effective set contains any of: `leave:approve`, `leave:manage`, `attendance:approve`, `payroll:approve`, `payroll:run`, `performance:write`, `performance:manage`, `expense:approve`, `tasks:approve`, `documents:approve`, `grievance:manage`, `monitoring:alerts:read`, `monitoring:alerts:resolve`, `verification:review` |
| `notifications:read` | Effective set contains any of: `leave:approve`, `leave:manage`, `attendance:approve`, `employees:write`, `payroll:approve`, `performance:manage`, `monitoring:alerts:read`, `tasks:approve` |

Derived permissions never appear in the role creation browser or override pickers.

---

## Access Policies

A permission answers **what action** is allowed. An access policy answers **whose data** the action can reach. The two are configured independently â€” the same permission (`leave:read`) assigned with policy `direct_reports` (manager) or `organization` (HR) operates on a completely different data set without needing separate permission codes.

Access policy applies only to permissions that operate on employee records. Tenant-wide permissions (`settings:*`, `analytics:*`, `payroll:run`, `org:*`) are not scoped by access policy.

| Policy | Data Scope |
|:--|:--|
| `self` | Own employee record only (default when no policy is set) |
| `direct_reports` | Employees directly below the current employee in `employee_hierarchy_closure` (depth = 1), derived from position hierarchy |
| `reporting_tree` | All employees anywhere below this user in the org tree (depth â‰¥ 1) |
| `department` | All active employees in the same department |
| `department_tree` | All active employees in the department's full org subtree |
| `org_unit_tree` | All active employees under this user's org unit |
| `organization` | All active employees in the tenant |

Access scope is assigned when a security role is assigned to a user through `user_roles.scope_type` and `user_roles.scope_id`. Per-employee permission overrides can also carry `scope_type` and `scope_id`. The backend resolves the scope at query time; the frontend never sends employee ID lists.

See [[Userflow/Auth-Access/access-policy|Access Policy Reference]] for full details including the employee hierarchy closure table and the `/api/v1/me/app-context` endpoint.

---

## Explicitly Grantable Permissions

### Employees
| #   | Permission            | Description                 |
| :-- | :-------------------- | :-------------------------- |
| 1   | `employees:read`      | View employees within access policy scope |
| 3   | `employees:write`     | Create, update employees    |
| 4   | `employees:delete`    | Delete employee records     |
| 4a  | `employees:import`    | Import employee records in bulk |
| 4b  | `employees:export`    | Export employee data to file |

### Organization
| # | Permission | Description |
|:--|:-----------|:------------|
| 5 | `org:read` | View org structure, departments, hierarchy |
| 6 | `org:manage` | Create and edit org structure, departments |

### Leave
| # | Permission | Description |
|:--|:-----------|:------------|
| 7 | `leave:read` | View leave records within access policy scope |
| 9 | `leave:create` | Apply for leave on behalf of others |
| 10 | `leave:approve` | Approve or reject leave requests |
| 11 | `leave:manage` | Manage leave types, policies, balances |

### Attendance
| # | Permission | Description |
|:--|:-----------|:------------|
| 12 | `attendance:read` | View attendance records within access policy scope |
| 14 | `attendance:approve` | Approve overtime and attendance corrections |
| 15 | `attendance:write` | Correct attendance records for employees in scope |

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
| 20 | `performance:read` | View performance records within access policy scope |
| 22 | `performance:write` | Submit and edit performance reviews within access policy scope |
| 23 | `performance:manage` | Manage review cycles, templates, goals |

### Skills
| # | Permission | Description |
|:--|:-----------|:------------|
| 24 | `skills:read` | View skills profiles within access policy scope |
| 25 | `skills:write` | Create and update skills profiles within access policy scope |
| 27 | `skills:validate` | Validate or endorse skills within access policy scope |
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
| 33a | `calendar:admin` | Manage country holiday sync, company/location calendar overrides, and calendar integrations |

### Notifications
| # | Permission | Description |
|:--|:-----------|:------------|
| 34 | `notifications:manage` | Manage notification templates and delivery settings |

### Settings
| # | Permission | Description |
|:--|:-----------|:------------|
| 35 | `settings:read` | View any settings section (read-only) |
| 36 | `settings:admin` | Manage core system settings â€” timezone, work hours, privacy mode, data retention |
| 37 | `settings:billing` | Manage subscription, plan, and payment methods |
| 38 | `settings:branding` | Manage company logo and brand colors |
| 39 | `settings:integrations` | Connect or disconnect tenant-wide app integrations via OAuth (Teams, Slack, LMS) and enter migration API keys for onboarding from existing HR systems. Google/Outlook Calendar is managed under `calendar:admin` / user-owned Calendar connections. |
| 40 | `settings:notifications` | Manage notification templates and delivery channels |
| 41 | `settings:alerts` | Configure alert thresholds and escalation rules |
| 42 | `settings:system` | Manage system-level settings â€” audit config, data retention policies |
| 43 | `settings:device` | View biometric device connection status |
| 44 | `settings:device:configure` | Add, remove, and configure biometric device integrations |

### Users & Roles
| # | Permission | Description |
|:--|:-----------|:------------|
| 45 | `users:read` | View user accounts |
| 46 | `users:manage` | Create, suspend, and manage user accounts |
| 47 | `roles:read` | View roles and their permission sets |
| 48 | `roles:create` | Create new roles |
| 48a | `roles:update` | Edit role names, descriptions, and permission sets |
| 48b | `roles:delete` | Delete custom roles |
| 48c | `roles:assign` | Assign roles to users |
| 48d | `permissions:manage` | Grant or revoke permissions within delegation scope |

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
| 57 | `monitoring:read` | View monitoring data, insights, and activity summaries |
| 57a | `monitoring:view-settings` | View monitoring toggles and employee overrides |
| 58 | `monitoring:configure` | Enable/disable monitoring features, set employee overrides |
| 58a | `monitoring:alerts:read` | View monitoring and exception alerts |
| 58b | `monitoring:alerts:resolve` | Acknowledge and resolve monitoring alerts |
| 58c | `monitoring:recommendations:read` | View agent-generated recommendations |
| 58d | `monitoring:recommendations:apply` | Apply agent recommendations to configuration or workflows |

### Exceptions
| # | Permission | Description |
|:--|:-----------|:------------|
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
| 80g | `reports:export` | Export report data to file |

### Audit
| # | Permission | Description |
|:--|:-----------|:------------|
| 80h | `audit:read` | View audit logs â€” permission changes, employee updates, hierarchy changes, login/security events, and agent actions |
| 80i | `audit:export` | Export audit log data to file |

### Workflows
| # | Permission | Description |
|:--|:-----------|:------------|
| 80j | `workflows:read` | View workflow definitions, status, and execution history where resource access allows |
| 80k | `workflows:manage` | Create, edit, disable, and manage workflow definitions, templates, resolver rules, and SLA rules |

### Company Connections And Cross-Company Access
| # | Permission | Description |
|:--|:-----------|:------------|
| 80a | `company-connections:read` | View connected companies and connection state visible to the current tenant |
| 80b | `company-connections:manage` | Request, approve, revoke, or manage connection grants within tenant-facing permissions |
| 80c | `cross-company:employees:read` | View approved employee projections from connected companies |
| 80d | `cross-company:employees:transfer` | Start or approve cross-company employee transfer between connected tenants |
| 80e | `cross-company:reports:view` | View approved cross-company reports and dashboards |
| 80f | `cross-company:workflows:manage` | Create or manage automations that reference connected companies |

Cross-company permissions are inert without a grant scope. Scope must include selected connected tenant IDs, resource type, action, optional allowed fields or data categories, optional expiry, and the user or role receiving the grant. A matching owner email or an active connection alone never exposes data.

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
| `attendance:read-own` | Module auto-grant (attendance module) |
| `audit:read` | Restored as standalone grantable permission `audit:read` |
| `branding:manage` | Renamed to `settings:branding` |
| `worksync:*` module permissions | Internal WorkSync module permissions; no bridge API scopes are active |
| `calendar:sync` | Covered by `settings:integrations` |
| `compliance:manage` | Not defined |
| `departments:read` | Covered by `org:read` |
| `deployment:write` | Not defined |
| `devices:manage` | Split into `settings:device` + `settings:device:configure` |
| `docs:read` | Renamed to `documents:read` |
| `documents:read-own` | Module auto-grant (HR Documents module) |
| `employee:create` / `employees:create` / `employees:update` / `employees:bulk-update` | All covered by `employees:write` |
| `exceptions:read` | Renamed to `monitoring:alerts:read` |
| `exceptions:view` | Renamed to `monitoring:alerts:read` |
| `exceptions:acknowledge` | Renamed to `monitoring:alerts:resolve` |
| `exceptions:resolve` | Same as `monitoring:alerts:resolve` â€” removed |
| `roles:manage` | Split into `roles:create`, `roles:update`, `roles:delete`, `roles:assign`, `permissions:manage` |
| `expense:admin` | Covered by `expense:manage` |
| `goals:read` / `goals:write` | Renamed to `okr:read` / `okr:write` |
| `hr:read` | Covered by `employees:read` |
| `inbox:read` | Derived (computed from effective permission set) |
| `calendar:read` | Module auto-grant (calendar module) |
| `leave:none` | Not a permission - sentinel value |
| `leave:read-own` | Module auto-grant (leave module) |
| `leave:write` | Covered by `leave:create` + `leave:manage` |
| `monitoring:update-settings` | Renamed to `monitoring:configure` |
| `notifications:configure` | Covered by `settings:notifications` |
| `notifications:read` | Derived (computed from effective permission set) |
| `org:write` | Covered by `org:manage` |
| `overtime:read` | Covered by `attendance:read` |
| `payroll:manage` | Renamed to `payroll:write` |
| `payroll:read-own` | Module auto-grant (Payroll module â€” Phase 2) |
| `payroll:view` | Renamed to `payroll:read` |
| `payroll:view-salary` | Covered by `payroll:read` |
| `performance:read-own` | Module auto-grant (Performance module â€” Phase 2) |
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
| `workforce:dashboard` | Module auto-grant (workforce module) |
| `workforce:manage-biometric` | Renamed to `settings:device:configure` |
| `workforce:read` | Renamed to `workforce:view` |
| `employees:read-team` | Access policy model â€” use `employees:read` with policy `direct_reports` |
| `leave:read-team` | Access policy model â€” use `leave:read` with policy `direct_reports` |
| `attendance:read-team` | Access policy model â€” use `attendance:read` with policy `direct_reports` |
| `performance:read-team` | Access policy model â€” use `performance:read` with policy `direct_reports` |
| `skills:write-team` | Access policy model â€” use `skills:write` with policy `direct_reports` |
---

## Validation Rules

- Module auto-grant permissions are given to every active employee based on the tenant's active modules and are never manually assigned or revoked. Derived permissions (inbox:read, notifications:read) are computed automatically from the effective permission set.
- Explicitly grantable permissions are the only permissions shown in role creation, role editing, and employee override pickers.
- Any permission used by a user flow, frontend route, API endpoint, or module overview must appear either in Universal Permissions or Explicitly Grantable Permissions.
- Any legacy permission must appear in Removed from Original List with a replacement or a reason.
- `roles:manage` is retired â€” use `roles:create`, `roles:update`, `roles:delete`, `roles:assign`, and `permissions:manage` individually. Assign all five to replicate the old `roles:manage` scope.
- `exceptions:view` and `exceptions:acknowledge` are retired â€” use `monitoring:alerts:read` and `monitoring:alerts:resolve`. `exceptions:manage` remains for rule configuration.
- The `*` permission remains tenant-local. Cross-company access requires an active company connection, explicit cross-company permission, grant scope, and audit.

