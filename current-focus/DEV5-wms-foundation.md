# Task: WorkSync Foundation + Projects + OKR + Time + Resources

**Assignee:** Dev 5
**Pillar:** Pillar 3 — WorkSync
**Priority:** Critical
**Dependencies:** DEV1 Infrastructure (tenants, users, legal_entities), DEV2 Auth (roles, permissions), DEV3 Org Structure (legal_entities for workspace binding)

> DEV5 Task 1 (workspaces) is the hardest dependency for DEV6 (boards/tasks) and DEV7 (chat). Complete Task 1 before DEV6 and DEV7 can start their foundation work.

---

## Task 1: WorkSync Foundation

**Module:** `ONEVO.Modules.WorkSync.Foundation`
**Tables:** `workspaces`, `workspace_members`, `workspace_roles`
**Depends on:** DEV1 Infrastructure done (tenants, users), DEV3 Org Structure done (legal_entities)

### Acceptance Criteria

- [ ] `workspaces` table: id, tenant_id → tenants, legal_entity_id → legal_entities (nullable, binds WMS to HR topbar scope), name, slug (UNIQUE per tenant), description, owner_id → users, icon_url, is_active, timezone, created_at, updated_at
- [ ] `workspace_members` table: id, workspace_id → workspaces, user_id → users, workspace_role_id → workspace_roles, invited_by → users nullable, joined_at, created_at. UNIQUE (workspace_id, user_id)
- [ ] `workspace_roles` table: id, workspace_id → workspaces, name (Admin/Member/Viewer), is_system boolean. Seed three system roles per workspace on creation
- [ ] Tenant provisioning seeds a default workspace when a WorkSync-enabled tenant is created
- [ ] `GET /api/v1/workspaces` — list workspaces for current user (via workspace_members)
- [ ] `POST /api/v1/workspaces` — create workspace (requires `workspaces:manage` permission)
- [ ] `POST /api/v1/workspaces/{id}/members` — invite user to workspace
- [ ] `PUT /api/v1/workspaces/{id}/members/{userId}/role` — update workspace role
- [ ] Workspace switcher context: session carries active workspace_id in JWT claims or header
- [ ] Global query filter: workspace-scoped entities filter by `tenant_id` AND `workspace_id`

### Backend References
- [[onevo-unified-entity-map|Entity Map]] — Section 1 Foundation, Section 25 WMS Project Management
- [[database/schemas/wms-project-management|WMS Project Schema]]
- [[modules/work-management/foundation|WMS Foundation spec]]

---

## Task 2: Project Management

**Module:** `ONEVO.Modules.WorkSync.Projects`
**Tables:** `projects`, `project_members`, `epics`, `milestones`, `versions`, `release_calendar`, `labels`
**Depends on:** Task 1 (workspaces)

### Acceptance Criteria

- [ ] `projects` table: id, workspace_id → workspaces, name, description, status (active/archived/completed), lead_id → users nullable, start_date, target_date, icon_url, color, is_private, created_at, updated_at
- [ ] `project_members` table: id, project_id → projects, user_id → users, role (owner/member/viewer), joined_at. UNIQUE (project_id, user_id)
- [ ] `epics` table: id, project_id → projects, title, description, status, start_date, due_date, created_by → users, created_at
- [ ] `milestones` table: id, project_id → projects, name, description, due_date, status, created_at
- [ ] `versions` table: id, project_id → projects, name, description, release_date, status (planned/released), created_at
- [ ] `release_calendar` table: id, version_id → versions, workspace_id → workspaces, scheduled_date, notes
- [ ] `labels` table: id, project_id → projects, name, color, created_at. Scoped to project.
- [ ] CRUD APIs for all entities with appropriate permissions (`projects:read`, `projects:write`, `projects:manage`)
- [ ] Project member auto-added when user is assigned a task in the project
- [ ] Domain event: `ProjectCreatedEvent` → Notifications module (notify workspace Admin)

### Backend References
- [[onevo-unified-entity-map|Entity Map]] — Section 25 WMS Project Management
- [[database/schemas/wms-project-management|WMS Project Schema]]

---

## Task 3: OKR

**Module:** `ONEVO.Modules.WorkSync.OKR`
**Tables:** `objectives`, `key_results`, `okr_check_ins`
**Depends on:** Task 1 (workspaces)

### Acceptance Criteria

- [ ] `objectives` table: id, workspace_id → workspaces, owner_id → users, title, description, time_period (varchar 20 — Q1/Q2/Q3/Q4/annual), start_date, end_date, status (on_track/at_risk/off_track/done), created_at, updated_at
- [ ] `key_results` table: id, objective_id → objectives, owner_id → users, title, kr_type (numeric/percentage/boolean), current_value numeric, target_value numeric, start_value numeric, unit varchar, status, created_at, updated_at
- [ ] `okr_check_ins` table: id, key_result_id → key_results, user_id → users, value numeric, confidence_score int (1–10), notes text nullable, created_at
- [ ] Progress auto-calculated: objective progress = avg(key_result progress). Stored as computed/refreshed on check-in.
- [ ] `GET /api/v1/workspaces/{id}/objectives` — list OKRs with progress
- [ ] `POST /api/v1/objectives/{id}/key-results/{krId}/check-ins` — log a check-in
- [ ] Domain event: `OkrCheckInCreatedEvent` → Notifications (notify objective owner if kr goes at_risk)

### Backend References
- [[onevo-unified-entity-map|Entity Map]] — Section 28 WMS OKR
- [[modules/work-management/okr|WMS OKR spec]]

---

## Task 4: Time Management

**Module:** `ONEVO.Modules.WorkSync.Time`
**Tables:** `time_logs`, `timesheets`, `timesheet_entries`
**Depends on:** Task 2 (projects), DEV6 Tasks (tasks table for time log FK)

### Acceptance Criteria

- [ ] `time_logs` table: id, task_id → tasks nullable, user_id → users, workspace_id → workspaces, description text nullable, logged_minutes int, logged_date date, billable boolean, created_at
- [ ] `timesheets` table: id, user_id → users, workspace_id → workspaces, week_start date, status (draft/submitted/approved/rejected), submitted_at nullable, approved_by → users nullable, created_at
- [ ] `timesheet_entries` table: id, timesheet_id → timesheets, task_id → tasks nullable, project_id → projects nullable, monday_minutes int, tuesday_minutes int, wednesday_minutes int, thursday_minutes int, friday_minutes int, saturday_minutes int, sunday_minutes int
- [ ] `POST /api/v1/time-logs` — log time against a task
- [ ] `GET /api/v1/workspaces/{id}/timesheets/me` — own timesheets
- [ ] `POST /api/v1/timesheets/{id}/submit` — submit for approval
- [ ] Hangfire job: weekly timesheet auto-creation every Monday morning for active workspace members
- [ ] HR bridge (internal): `employees.user_id` links time logs to payroll-relevant HR records via `IEmployeeService.GetEmployeeIdAsync(userId)`

### Backend References
- [[onevo-unified-entity-map|Entity Map]] — Section 31 WMS Time Management
- [[modules/work-management/time|WMS Time spec]]

---

## Task 5: Resource Management

**Module:** `ONEVO.Modules.WorkSync.Resources`
**Tables:** `resource_plans`, `resource_allocations`, `resource_availability_overrides`
**Depends on:** Task 2 (projects), DEV6 Tasks (tasks), DEV5 Time Management

### Acceptance Criteria

- [ ] `resource_plans` table: id, project_id → projects, name, start_date, end_date, created_by → users, created_at
- [ ] `resource_allocations` table: id, plan_id → resource_plans, user_id → users, role_description varchar, allocated_hours_per_week int, start_date, end_date, notes text nullable
- [ ] `resource_availability_overrides` table: id, user_id → users, workspace_id → workspaces, date date, available_hours int, reason varchar nullable
- [ ] `GET /api/v1/workspaces/{id}/resource-plans` — list plans
- [ ] `GET /api/v1/resource-plans/{id}/allocations` — allocation detail with utilization %
- [ ] Utilization calculated as: allocated_hours / available_hours (from leave + working hours)
- [ ] Read leave data via `ILeaveService.GetBlockedDaysAsync(userId, dateRange)` for capacity planning

### Backend References
- [[onevo-unified-entity-map|Entity Map]] — Section 32 WMS Resource Management
- [[modules/work-management/resources|WMS Resources spec]]

---

## Step 2: Frontend

### Pages to Build

```
app/(dashboard)/
├── workspaces/
│   ├── page.tsx                   # Workspace switcher / list
│   └── [id]/
│       ├── layout.tsx             # Workspace layout with project sidebar
│       ├── page.tsx               # Workspace overview / activity feed
│       ├── projects/
│       │   ├── page.tsx           # Project list
│       │   └── [projectId]/
│       │       ├── page.tsx       # Project overview (epics, milestones)
│       │       └── settings/      # Project settings + members
│       ├── okr/
│       │   ├── page.tsx           # OKR dashboard (objectives list + progress rings)
│       │   └── [objectiveId]/     # Objective detail with key results
│       ├── time/
│       │   ├── page.tsx           # Timesheet list
│       │   └── [weekStart]/       # Weekly timesheet entry
│       └── resources/
│           └── page.tsx           # Resource planner (Gantt-style allocation view)
```

### Key Userflows to Reference
- [[Userflow/Work-Management/workspace-creation|Workspace Creation]]
- [[Userflow/Work-Management/project-setup|Project Setup]]
- [[Userflow/Work-Management/okr-flow|OKR Flow]]
