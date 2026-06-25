# Schema: Work Management - Insight & Analytics

**Module:** `Work Management.Analytics`
**Phase:** 2 - deferred. Not part of Phase 1 Work implementation.
**Owner:** DEV6

---

## `dashboards` - Phase 2

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `workspace_id` | uuid | FK -> workspaces |
| `tenant_id` | uuid | FK -> tenants |
| `name` | varchar(200) | |
| `description` | text | nullable |
| `created_by_id` | uuid | FK -> users |
| `is_shared` | boolean | Quick flag - true means available via `dashboard_shares` to all workspace members |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

---

## `chart_widgets` - Phase 2

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `dashboard_id` | uuid | FK -> dashboards |
| `widget_type` | varchar(50) | task_status_distribution / time_report; Phase 2 may add sprint_velocity / burndown / team_workload / resource_utilization / code_activity / okr_progress |
| `title` | varchar(200) | nullable - overrides default widget title |
| `config_json` | jsonb | Filter parameters, date range, project/sprint scope |
| `position_x` | int | Grid column |
| `position_y` | int | Grid row |
| `width` | int | Grid columns spanned |
| `height` | int | Grid rows spanned |

---

## `saved_views` - Phase 2

Saved filter + sort configurations for task lists, project lists, etc.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `workspace_id` | uuid | FK -> workspaces |
| `entity_type` | varchar(30) | tasks / projects / members; Phase 2 planning may add sprints |
| `name` | varchar(200) | |
| `filter_json` | jsonb | Filter conditions |
| `sort_json` | jsonb | Sort fields and direction |
| `group_by` | varchar(50) | nullable - status / assignee / priority; Phase 2 planning may add sprint |
| `created_by_id` | uuid | FK -> users |
| `is_shared` | boolean | |
| `created_at` | timestamptz | |

---

## `report_snapshots` - Phase 2

Point-in-time report data for comparison or scheduled reporting.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `workspace_id` | uuid | FK -> workspaces |
| `report_type` | varchar(50) | sprint_velocity / time_report / resource_allocation / code_activity |
| `period_start` | date | nullable |
| `period_end` | date | nullable |
| `snapshot_json` | jsonb | Full report data at time of snapshot |
| `created_at` | timestamptz | |

---

## `report_exports` - Phase 2

Async export jobs. Generates CSV/PDF/Excel files and stores in Cloudflare R2 object storage.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `workspace_id` | uuid | FK -> workspaces |
| `requested_by_id` | uuid | FK -> users |
| `export_type` | varchar(20) | csv / pdf / excel |
| `entity_type` | varchar(30) | tasks / sprint_report / time_report / code_activity |
| `filter_json` | jsonb | What to export |
| `file_asset_id` | uuid | FK -> file_assets, nullable - set when export complete |
| `status` | varchar(20) | pending / processing / ready / failed |
| `created_at` | timestamptz | |
| `completed_at` | timestamptz | nullable |

**Hangfire job:** Processes export, uploads to object storage, sets `file_asset_id` and `status = ready`, sends notification to `requested_by_id`.

---

## `dashboard_shares` - Phase 2

Granular sharing for dashboards. Separate from `dashboards.is_shared` (which is workspace-wide).

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `dashboard_id` | uuid | FK -> dashboards |
| `can_edit` | boolean | default false - view-only sharing |
| `shared_by` | uuid | FK -> users |
| `shared_at` | timestamptz | |

**Unique:** `(dashboard_id, shared_with_type, shared_with_id)`

---

## `saved_view_shares` - Phase 2

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `saved_view_id` | uuid | FK -> saved_views |
| `shared_with_id` | uuid | |
| `shared_by` | uuid | FK -> users |
| `shared_at` | timestamptz | |

**Unique:** `(saved_view_id, shared_with_type, shared_with_id)`
