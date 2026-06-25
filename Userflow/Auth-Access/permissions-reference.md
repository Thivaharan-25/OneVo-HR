# Permissions Reference

**Total explicitly grantable:** 127 permissions across 31 modules  
**Related flows:** [[Userflow/Auth-Access/permission-assignment|Permission Assignment]] - [[Userflow/Auth-Access/role-creation|Role Creation]]

---

## System Permission (internal - seeded at provisioning; never shown in UI pickers)

| Permission | What it gives |
|:-----------|:--------------|
| `*` | Tenant-local Super Admin bypass - grants access to tenant endpoints regardless of permission checks inside the current tenant only; assigned only to the Super Admin role during tenant provisioning; must not appear in the role creation browser, per-employee override lists, or any assignable permission payload; does not grant platform-admin access or cross-company access without a scoped cross-company grant |

---

## Module Auto-Grant Permissions

These are given automatically to every active employee **when the tenant's subscription includes the relevant module**. They are resolved by the auth layer, never assigned through roles, and cannot be revoked through role permissions or employee overrides.

| Permission | Module Required | What it gives |
| :--------- | :-------------- | :------------ |
| `employees:read-own` | `employees` | View own employee profile |
| `time_off:read-own` | `time_off` | View own Time Off balance and history |
| `attendance:read-own` | `attendance` | View own attendance and presence history |
| `attendance:write-own` | `attendance` | Submit own attendance corrections |
| `calendar:read` | `calendar` | View calendar |
| `activity:read:self` | `monitoring` | View own activity log |
| `monitoring:dashboard` | `monitoring` | Access monitoring dashboard |

Module auto-grant permissions must not appear in the role creation permission browser, role permission save payloads, or per-employee override add/remove lists.

> **Phase 2 note:** `payroll:read-own`, `performance:read-own`, and `documents:read-own` will be added to this table when their modules (Payroll, Performance, HR Documents) are released.

## Derived Permissions

These are computed automatically by the auth layer based on the employee's effective permission set. They cannot be assigned or revoked manually.

| Permission | Derived when |
| :--------- | :----------- |
| `inbox:read` | Effective set contains any of: `time_off:approve`, `time_off:manage`, `attendance:approve`, `payroll:approve`, `payroll:run`, `performance:write`, `performance:manage`, `expense:approve`, `tasks:approve`, `documents:approve`, `grievance:manage`, `monitoring:alerts:read`, `monitoring:alerts:resolve`, `verification:review` |
| `notifications:read` | Effective set contains any of: `time_off:approve`, `time_off:manage`, `attendance:approve`, `employees:write`, `payroll:approve`, `performance:manage`, `monitoring:alerts:read`, `tasks:approve` |

Derived permissions never appear in the role creation browser or override pickers.

---

## Management Coverage

A permission answers **what action** is allowed. Management coverage answers **whose employee data** the action can reach and who owns Phase 1 approvals. The two are configured independently - the same permission (`time_off:read`) can operate over a covered position, department, or whole Company without needing separate permission codes.

Management coverage applies only to permissions that operate on employee records or employee-owned records. Tenant-wide permissions (`settings:*`, `analytics:*`, `payroll:run`, `org:*`) do not require management coverage.

| Can manage employees in | Employee set |
|:--|:--|
| Selected departments | Active employees in selected departments |
| Selected positions | Active employees assigned to selected positions |
| Entire company | Active employees in the active Company/legal entity |

Employee visibility and Phase 1 approval routing come from Org Structure management coverage. Roles and permission overrides decide what actions a user can perform; management coverage decides which employees their position can manage. The backend resolves the final employee set at query time; the frontend never sends employee ID lists.

Management coverage supports position, department, and company-wide targets only. There is no employee-specific coverage.

See [[Userflow/Auth-Access/access-policy|Management Coverage Reference]] for full details including owner ordering and the `/api/v1/me/app-context` endpoint.

---

## Explicitly Grantable Permissions

### Employees
| #   | Permission            | Description                 |
| :-- | :-------------------- | :-------------------------- |
| 1   | `employees:read`      | View employees allowed by management coverage |
| 3   | `employees:write`     | Create, update employees    |
| 4   | `employees:delete`    | Delete employee records     |
| 4a  | `employees:import`    | Import employee records in bulk |
| 4b  | `employees:export`    | Export employee data to file |

### Organization
| # | Permission | Description |
|:--|:-----------|:------------|
| 5 | `org:read` | View org structure, departments, hierarchy |
| 6 | `org:manage` | Create and edit org structure, departments |
| 6a | `position:approve` | Approve position assignment changes and generated position access when coverage is valid |

### Time Off
| # | Permission | Description |
|:--|:-----------|:------------|
| 7 | `time_off:read` | View Time Off records allowed by management coverage |
| 9 | `time_off:create` | Apply for Time Off on behalf of others |
| 10 | `time_off:approve` | Approve or reject Time Off requests |
| 11 | `time_off:manage` | Manage Time Off types, policies, balances |

### Attendance
| # | Permission | Description |
|:--|:-----------|:------------|
| 12 | `attendance:read` | View attendance records allowed by management coverage |
| 14 | `attendance:approve` | Approve overtime and attendance corrections |
| 15 | `attendance:write` | Correct attendance records for employees allowed by management coverage |

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
| 20 | `performance:read` | View performance records allowed by management coverage |
| 22 | `performance:write` | Submit and edit performance reviews allowed by management coverage |
| 23 | `performance:manage` | Manage review cycles, templates, goals |

### Skills
| # | Permission | Description |
|:--|:-----------|:------------|
| 24 | `skills:read` | View skills profiles allowed by management coverage |
| 25 | `skills:write` | Create and update skills profiles allowed by management coverage |
| 27 | `skills:validate` | Validate or endorse skills allowed by management coverage |
| 28 | `skills:manage` | Manage skill library and categories |

### Expense
| # | Permission | Description |
|:--|:-----------|:------------|
| 29 | `expense:read` | View expense records allowed by the applicable employee-data rules |
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
| 36 | `settings:admin` | Manage core system settings - timezone, work hours, privacy mode, data retention |
| 37 | `settings:billing` | Manage subscription, plan, and payment methods |
| 38 | `settings:branding` | Manage company logo and brand colors |
| 40 | `settings:notifications` | Manage notification templates and delivery channels |
| 41 | `settings:alerts` | Configure alert thresholds and escalation rules |
| 42 | `settings:system` | Manage system-level settings - audit config, data retention policies |
| 43 | `settings:device` | View attendance/biometric device connection status |
| 44 | `settings:device:configure` | Add, remove, and configure attendance/biometric device integrations |

### Users & Roles
| # | Permission | Description |
|:--|:-----------|:------------|
| 45 | `users:read` | View user accounts |
| 46 | `users:manage` | Create, suspend, and manage user accounts |
| 47 | `roles:read` | View roles and their permission sets |
| 48 | `roles:manage` | Aggregate tenant role-management permission used by Phase 1 flows; covers role create/update/delete/assignment plus permission management within scope |

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
| 61 | `exceptions:manage` | Phase 2: manage Exception Engine rules and thresholds |

### Verification
| # | Permission | Description |
|:--|:-----------|:------------|
| 62 | `verification:view` | View AWS Rekognition identity verification results |
| 63 | `verification:review` | Review or escalate verification cases (recipient resolved by Monitoring Policy), change severity level (critical, high, etc.) |
| 64 | `verification:configure` | Configure AWS Rekognition settings and verification rules |

> **Escalation rule:** Phase 1 approval and alerts are sent through management coverage routing and Notifications. Workflow Engine escalation is Phase 2.

### Monitoring
| # | Permission | Description |
|:--|:-----------|:------------|
| 65 | `monitoring:view` | View monitoring intelligence data and reports |
| 66 | `monitoring:manage` | Manage monitoring intelligence settings |

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
| 80h | `audit:read` | View audit logs - permission changes, employee updates, hierarchy changes, login/security events, and agent actions |
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
| `exceptions:resolve` | Same as `monitoring:alerts:resolve` - removed |
| `roles:manage` | Kept as the Phase 1 aggregate role-management permission; granular permissions may be used later for delegated administration |
| `expense:admin` | Covered by `expense:manage` |
| `goals:read` / `goals:write` | Renamed to `okr:read` / `okr:write` |
| `hr:read` | Covered by `employees:read` |
| `inbox:read` | Derived (computed from effective permission set) |
| `calendar:read` | Module auto-grant (calendar module) |
| `time_off:none` | Not a permission - sentinel value |
| `time_off:read-own` | Module auto-grant (Time Off module) |
| `time_off:write` | Covered by `time_off:create` + `time_off:manage` |
| `monitoring:update-settings` | Renamed to `monitoring:configure` |
| `notifications:configure` | Covered by `settings:notifications` |
| `notifications:read` | Derived (computed from effective permission set) |
| `org:write` | Covered by `org:manage` |
| `overtime:read` | Covered by `attendance:read` |
| `payroll:manage` | Renamed to `payroll:write` |
| `payroll:read-own` | Module auto-grant (Payroll module - Phase 2) |
| `payroll:view` | Renamed to `payroll:read` |
| `payroll:view-salary` | Covered by `payroll:read` |
| `performance:read-own` | Module auto-grant (Performance module - Phase 2) |
| `people:read` | Covered by `employees:read` |
| `planning:read` / `planning:write` | Replaced by `sprints:*`, `roadmaps:*`, and `projects:*` |
| `platform:admin` | Renamed to `settings:admin` |
| `project:create` | Typo - correct code is `projects:create` |
| `reports:manage` | Covered by `reports:create` |
| `schedule:read` | Covered by `calendar:read` (universal) |
| `settings:manage` / `settings:write` | Redundant - covered by specific `settings:*` sub-permissions |
| `sprint:manage` | Typo - correct code is `sprints:manage` |
| `task:assign` | Covered by `tasks:write` |
| `verification:read` | Renamed to `verification:view` |
| `verification:review` | Confirmed as separate - kept |
| `wms:chat` / `wms:okr` / `wms:projects` | Wrong prefix - use `chat:*`, `okr:*`, `projects:*` |
| `monitoring:approve-overtime` | Same as `attendance:approve` - removed |
| `monitoring:correct-attendance` | Same as `attendance:write` - removed |
| `monitoring:dashboard` | Module auto-grant (monitoring module) |
| `monitoring:manage-biometric` | Renamed to `settings:device:configure` |
| `monitoring:view` | Renamed to `monitoring:view` |
---

## Validation Rules

- Module auto-grant permissions are given to every active employee based on the tenant's active modules and are never manually assigned or revoked. Derived permissions (inbox:read, notifications:read) are computed automatically from the effective permission set.
- Explicitly grantable permissions are the only permissions shown in role creation, role editing, and employee override pickers.
- Any permission used by a user flow, frontend route, API endpoint, or module overview must appear either in Universal Permissions or Explicitly Grantable Permissions.
- Any legacy permission must appear in Removed from Original List with a replacement or a reason.
- `roles:manage` remains active as the Phase 1 aggregate role-management permission. `position:approve` is the dedicated Phase 1 approval permission for position assignment changes and generated position-template access grants. Generic employee-management permissions do not grant approval authority.
- `exceptions:view` and `exceptions:acknowledge` are retired for Phase 1 - use `monitoring:alerts:read` and `monitoring:alerts:resolve`. `exceptions:manage` is Phase 2 rule configuration only.
- The `*` permission remains tenant-local. Cross-company access requires an active company connection, explicit cross-company permission, grant scope, and audit.
