# Schema: Work Management - Project Management

**Module:** `Work Management.Foundation` + `Work Management.Projects`
**Phase:** 1 for Work foundation/projects; Microsoft Teams sync additions are Phase 2 unless explicitly reactivated
**Owner:** DEV3

---

## `workspaces` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK -> tenants |
| `name` | varchar(200) | |
| `slug` | varchar(100) | UNIQUE per tenant |
| `description` | text | nullable |
| `owner_id` | uuid | FK -> users |
| `icon_url` | varchar(500) | nullable |
| `is_active` | boolean | |
| `timezone` | varchar(50) | default `UTC` |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

**Indexes:** `(tenant_id)`, `(tenant_id, slug) UNIQUE`

**Scope rule:** Workspaces are tenant-local by default. Cross-company workspace/project collaboration requires an active company connection and explicit member/data-sharing scope; it is not modeled through topbar scope switching.


---

## `workspace_roles` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `workspace_id` | uuid | FK -> workspaces |
| `name` | varchar(50) | Admin / Member / Viewer |
| `is_system` | boolean | system roles cannot be deleted |

**Seeded on workspace creation:** Admin, Member, Viewer

**Rule:** Workspace roles are local access levels for a workspace. They are not tenant security roles and must not grant tenant-wide HR, payroll, security, or system administration authority.

---

## `workspace_members` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `workspace_id` | uuid | FK -> workspaces |
| `user_id` | uuid | FK -> users |
| `employee_id` | uuid | FK -> employees; required for tenant employees |
| `workspace_role_id` | uuid | FK -> workspace_roles |
| `invited_by_id` | uuid | FK -> users, nullable |
| `is_active` | boolean | false when employee is offboarded or removed |
| `joined_at` | timestamptz | |
| `removed_at` | timestamptz | nullable |
| `created_at` | timestamptz | |

**Unique:** `(workspace_id, user_id)`
**Indexes:** `(workspace_id, employee_id)`, `(employee_id, is_active)`

**Rule:** Work Management membership services must resolve `employee_id` from `employees.user_id`, verify `employees.is_deleted = false` and active employment status, then persist both `user_id` and `employee_id`. Non-employee external collaborators are not allowed in Phase 1.

---


## `workspace_teams_links` - Phase 2 Optional Integration


| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK -> tenants |
| `workspace_id` | uuid | FK -> workspaces |
| `teams_team_id` | varchar(255) | Microsoft Graph Team ID |
| `teams_group_id` | varchar(255) | Microsoft 365 Group ID |
| `link_mode` | varchar(20) | `created_from_onevo`, `linked_existing` |
| `member_match_status` | varchar(20) | `exact`, `partial`, `mismatch` |
| `sync_status` | varchar(20) | `active`, `pending`, `failed`, `paused`, `disconnected` |
| `last_member_sync_at` | timestamptz | nullable |
| `last_error` | text | nullable |
| `created_by_id` | uuid | FK -> users |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

**Unique:** `(tenant_id, workspace_id)` where `sync_status IN ('active', 'pending')`
**Index:** `(tenant_id, teams_team_id)`, `(tenant_id, sync_status)`

---

## `teams_member_sync_status` - Phase 2 Optional Integration


| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK -> tenants |
| `workspace_teams_link_id` | uuid | FK -> workspace_teams_links |
| `workspace_id` | uuid | FK -> workspaces |
| `user_id` | uuid | FK -> users |
| `teams_user_id` | varchar(255) | Nullable until user links Teams |
| `status` | varchar(20) | `linked`, `missing_link`, `added_to_team`, `failed`, `removed` |
| `last_checked_at` | timestamptz | |
| `last_error` | text | nullable |

**Unique:** `(workspace_teams_link_id, user_id)`

---

## `projects` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK -> tenants |
| `owning_legal_entity_id` | uuid | FK -> legal_entities; set from active legal entity context |
| `workspace_id` | uuid | FK -> workspaces; one owning workspace for the project in Phase 1 |
| `name` | varchar(200) | |
| `description` | text | nullable |
| `status` | varchar(20) | active / archived / completed |
| `lead_id` | uuid | FK -> users, nullable |
| `start_date` | date | nullable |
| `target_date` | date | nullable |
| `icon_url` | varchar(500) | nullable |
| `color` | varchar(20) | nullable |
| `is_private` | boolean | default false |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

**Indexes:** `(tenant_id)`, `(tenant_id, status)`, `(workspace_id)`

**Rule:** Projects are tenant-scoped business/work containers. In Phase 1, each project belongs to exactly one workspace through `projects.workspace_id`. `owning_legal_entity_id` is inferred from the creator's active legal entity context and is not a normal free-form create field.

---

## `project_workspaces` - Phase 2 Reference


| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `project_id` | uuid | FK -> projects |
| `workspace_id` | uuid | FK -> workspaces |
| `tenant_id` | uuid | FK -> tenants |
| `legal_entity_id` | uuid | FK -> legal_entities; copied from workspace/project context for reporting |
| `status` | varchar(20) | `pending`, `approved`, `active`, `rejected`, `removed` |
| `requested_by_id` | uuid | FK -> users |
| `approved_by_id` | uuid | FK -> users, nullable |
| `approved_at` | timestamptz | nullable |
| `linked_by_id` | uuid | FK -> users |
| `linked_at` | timestamptz | |
| `is_active` | boolean | false when the workspace is removed from the project context |

**Unique:** `(project_id, workspace_id)`
**Indexes:** `(workspace_id, is_active)`, `(tenant_id, project_id)`

**Rule:** This table is not active Phase 1 behavior. Phase 1 projects use `projects.workspace_id` for the owning workspace, and project access comes from accepted `project_members`. Workspace source pools, workspace participation approval, and multi-workspace project contribution reporting are Phase 2 references only.

---

## `project_member_invitations` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `project_id` | uuid | FK -> projects |
| `tenant_id` | uuid | FK -> tenants |
| `invited_user_id` | uuid | FK -> users |
| `invited_employee_id` | uuid | FK -> employees |
| `role` | varchar(20) | admin / member / viewer |
| `status` | varchar(20) | pending / accepted / declined / expired / cancelled |
| `invited_by_id` | uuid | FK -> users |
| `decided_at` | timestamptz | nullable |
| `expires_at` | timestamptz | nullable |

**Indexes:** `(project_id, status)`, `(invited_employee_id, status)`

**Rule:** Project/workspace admins invite selected employee-backed users directly. The selected member accepts or declines. An accepted invitation creates the active `project_members` row.

---

## `project_link_invitations` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `source_project_id` | uuid | FK -> projects |
| `target_project_id` | uuid | FK -> projects |
| `tenant_id` | uuid | FK -> tenants |
| `invited_project_admin_id` | uuid | FK -> users |
| `status` | varchar(20) | pending / accepted / declined / expired / cancelled |
| `invited_by_id` | uuid | FK -> users |
| `decided_at` | timestamptz | nullable |
| `expires_at` | timestamptz | nullable |

**Indexes:** `(source_project_id, status)`, `(target_project_id, status)`

**Rule:** Simple project-link invitations are sent from one project admin to another project admin. They do not create workspace source pools, employee visibility, or advanced dependency governance.

---

## `project_links` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `source_project_id` | uuid | FK -> projects |
| `target_project_id` | uuid | FK -> projects |
| `tenant_id` | uuid | FK -> tenants |
| `link_type` | varchar(30) | informational / related |
| `created_by_id` | uuid | FK -> users |
| `created_at` | timestamptz | |
| `is_active` | boolean | |

**Unique:** `(source_project_id, target_project_id, link_type)` where `is_active = true`

**Rule:** Created only after a project-link invitation is accepted. Advanced project-linking/dependency management is Phase 2.

---

## `project_members` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `project_id` | uuid | FK -> projects |
| `user_id` | uuid | FK -> users |
| `employee_id` | uuid | FK -> employees; required for tenant employees |
| `role` | varchar(20) | admin / member / viewer |
| `membership_source` | varchar(20) | `project_invite`, `system` |
| `is_active` | boolean | false when employee is offboarded or removed |
| `joined_at` | timestamptz | |
| `removed_at` | timestamptz | nullable |

**Unique:** `(project_id, user_id)`
**Indexes:** `(project_id, employee_id)`, `(employee_id, is_active)`

**Rule:** Project membership is the source of truth for project visibility and access. Except for the creator/system bootstrap, Phase 1 project membership is created after a `project_member_invitations` row is accepted. Offboarding deactivates project membership through `EmployeeOffboarded` handling.

Project visibility and dashboards must be filtered by viewer context: project admin, accepted project member, scoped tenant/project permission, or viewer/stakeholder.

---

## `epics` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `project_id` | uuid | FK -> projects |
| `title` | varchar(255) | |
| `description` | text | nullable |
| `status` | varchar(20) | open / in_progress / done |
| `start_date` | date | nullable |
| `due_date` | date | nullable |
| `created_by_id` | uuid | FK -> users |
| `created_at` | timestamptz | |

---

## `milestones` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `project_id` | uuid | FK -> projects |
| `name` | varchar(200) | |
| `description` | text | nullable |
| `due_date` | date | nullable |
| `status` | varchar(20) | planned / achieved / missed |
| `created_at` | timestamptz | |

---

## `versions` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `project_id` | uuid | FK -> projects |
| `name` | varchar(100) | |
| `description` | text | nullable |
| `release_date` | date | nullable |
| `status` | varchar(20) | planned / released / archived |
| `created_at` | timestamptz | |

---

## `release_calendar` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `version_id` | uuid | FK -> versions |
| `workspace_id` | uuid | FK -> workspaces |
| `scheduled_date` | date | |
| `notes` | text | nullable |

---

## `labels` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `project_id` | uuid | FK -> projects |
| `name` | varchar(50) | |
| `color` | varchar(20) | |
| `created_at` | timestamptz | |

**Note:** Labels are project-scoped by default. If reusable labels are needed across projects, use tenant-level label conventions or add explicit reusable label support later; do not infer label visibility from workspace membership.
