# Schema: Work Management - Project Management

**Module:** `Work Management.Foundation` + `Work Management.Projects`
**Phase:** 1 + Phase 2 Teams sync additions
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
| `membership_source` | varchar(20) | `manual`, `hr_team_sync`, `project_invite`, `system` |
| `is_active` | boolean | false when employee is offboarded or removed |
| `joined_at` | timestamptz | |
| `removed_at` | timestamptz | nullable |
| `created_at` | timestamptz | |

**Unique:** `(workspace_id, user_id)`
**Indexes:** `(workspace_id, employee_id)`, `(employee_id, is_active)`

**Rule:** Work Management membership services must resolve `employee_id` from `employees.user_id`, verify `employees.is_deleted = false` and active employment status, then persist both `user_id` and `employee_id`. Non-employee external collaborators are not allowed in Phase 1.

---

## `workspace_hr_team_links` - Phase 1

Maps an HR Org Structure team to a Work Management workspace for Phase 1 membership sync. This is separate from Microsoft Teams integration.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK -> tenants |
| `workspace_id` | uuid | FK -> workspaces |
| `hr_team_id` | uuid | FK -> teams |
| `sync_enabled` | boolean | Default true |
| `last_synced_at` | timestamptz | nullable |
| `last_error` | text | nullable |
| `created_by_id` | uuid | FK -> users |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

**Unique:** `(tenant_id, workspace_id, hr_team_id)`

**Rule:** When `team_members` changes, `HrTeamWorkspaceSyncHandler` adds/removes `workspace_members` with `membership_source = hr_team_sync`. Removed HR team members are deactivated, not hard-deleted.

---

## `workspace_teams_links` - Phase 2 Integration

Maps a Work Management workspace to a Microsoft Team/group. Used when the workspace creation checkbox creates a new Team or when an admin links an existing Team with matching members.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK -> tenants |
| `workspace_id` | uuid | FK -> workspaces |
| `teams_team_id` | varchar(255) | Microsoft Graph Team ID |
| `teams_group_id` | varchar(255) | Microsoft 365 Group ID |
| `display_name` | varchar(200) | Teams display name at link time |
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

## `teams_member_sync_status` - Phase 2 Integration

Per-member Teams readiness and membership sync state for a linked workspace.

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
| `workspace_id` | uuid | FK -> workspaces |
| `tenant_id` | uuid | FK -> tenants |
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

**Indexes:** `(workspace_id)`, `(tenant_id)`

---

## `project_members` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `project_id` | uuid | FK -> projects |
| `user_id` | uuid | FK -> users |
| `employee_id` | uuid | FK -> employees; required for tenant employees |
| `role` | varchar(20) | owner / member / viewer |
| `membership_source` | varchar(20) | `manual`, `workspace_inheritance`, `hr_team_sync`, `system` |
| `is_active` | boolean | false when employee is offboarded or removed |
| `joined_at` | timestamptz | |
| `removed_at` | timestamptz | nullable |

**Unique:** `(project_id, user_id)`
**Indexes:** `(project_id, employee_id)`, `(employee_id, is_active)`

**Rule:** Project membership must be limited to active workspace members. Offboarding deactivates project membership through `EmployeeOffboarded` handling.

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

**Note:** Labels are project-scoped. For cross-project personal board label reuse, use a workspace-level label convention enforced by the team, not a separate table in Phase 1.
