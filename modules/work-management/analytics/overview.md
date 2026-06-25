# Insight & Analytics

**Phase:** Phase 2 - deferred
**Phase 1 Status:** Not active in current Phase 1 Work implementation; retained as future design reference.

**Module:** WorkSync
**Feature:** Insight & Analytics
**Namespace:** `WorkSync.Analytics`
**Owner:** DEV6
**Tables:** 7

---

## Purpose

Phase 2 custom dashboards with configurable chart widgets, saved view filters, report snapshots, and async report exports. Sharing is controlled by two mechanisms: `dashboards.is_shared` (workspace-wide quick toggle) AND `dashboard_shares` (fine-grained ACL). Both must be checked.

---

## Database Tables

### `dashboards`
Key columns: `workspace_id`, `tenant_id`, `name`, `description`, `created_by_id`, `is_shared` (workspace-wide quick toggle - all members can view when true), `is_default`.

### `chart_widgets`
Key columns: `dashboard_id`, `widget_type` (`bar`, `line`, `pie`, `table`, `burndown`, `velocity`, `cumulative_flow`, `metric_card`), `title`, `config_json` (all filter/date-range/scope params - no separate filter tables), `position_json` (grid coordinates), `data_source` (`tasks`, `time_logs`; Phase 2 planning data may add `sprints`; Phase 2 Goals/OKR may add `okr`).

### `saved_views`
Reusable filter sets. Key columns: `workspace_id`, `user_id` (nullable - null for workspace-level views), `name`, `entity_type` (`tasks`, `projects`; Phase 2 planning may add `sprints`), `filter_json`, `sort_json`, `is_pinned`.

### `report_snapshots`
Point-in-time report captures. Key columns: `workspace_id`, `report_type`, `generated_at`, `parameters_json`, `data_json`, `generated_by_id`.

### `report_exports`
Async export jobs. Key columns: `workspace_id`, `report_type`, `format` (`pdf`, `csv`, `xlsx`), `parameters_json`, `status` (`queued`, `processing`, `ready`, `failed`), `file_asset_id` (FK -> file_assets, nullable - set when Hangfire completes), `requested_by_id`, `completed_at`.

Hangfire processes export -> uploads to Cloudflare R2 object storage -> sets `file_asset_id` -> sends notification.

### `dashboard_shares`

**Visibility check:** user can view dashboard if `dashboards.is_shared = true` OR there is a matching `dashboard_shares` row.

### `saved_view_shares`
Fine-grained ACL for saved views. Key columns: `saved_view_id`, `share_type`, `target_id`, `can_edit`, `shared_by_id`.

---

## Key Business Rules

1. **Dashboard visibility:** Check BOTH `dashboards.is_shared` (workspace-wide) AND `dashboard_shares` (ACL). A user can view if either condition is true.
2. `widget.config_json` stores all filter, date-range, and scope parameters - there are no separate filter tables.
3. Report exports are async: Hangfire job -> object storage upload -> `file_asset_id` set -> notification sent. Never block HTTP on export.
4. `saved_views` with `user_id = null` are workspace-level; with `user_id` set they are personal (My Space).
5. `is_default` dashboard: only one per user per workspace - application layer enforces uniqueness.

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `ReportExportReadyEvent` | Hangfire: export complete | Notifications (download link to user) |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/workspaces/{wsId}/dashboards` | `analytics:read` | List accessible dashboards |
| POST | `/api/v1/workspaces/{wsId}/dashboards` | `analytics:write` | Create dashboard |
| PATCH | `/api/v1/dashboards/{id}` | `analytics:write` | Update dashboard |
| POST | `/api/v1/dashboards/{id}/widgets` | `analytics:write` | Add widget |
| POST | `/api/v1/dashboards/{id}/share` | `analytics:write` | Share dashboard |
| GET | `/api/v1/workspaces/{wsId}/saved-views` | `analytics:read` | List saved views |
| POST | `/api/v1/workspaces/{wsId}/saved-views` | `analytics:write` | Save view |
| POST | `/api/v1/workspaces/{wsId}/reports/export` | `analytics:read` | Queue export |
| GET | `/api/v1/workspaces/{wsId}/reports/exports/{id}` | `analytics:read` | Check export status |

---

## Related

- [[Userflow/Work-Management/work-analytics-flow|Work Analytics]] - dashboards, saved views, and exports user flow

- [[modules/work-management/planning/overview|Planning]] - burndown/velocity widget data sources
- [[modules/work-management/tasks/overview|Task Management]] - task data source
- [[database/schemas/wms-analytics|WMS Analytics Schema]]
- [[current-focus/DEV6-tasks-boards-planning|DEV6 Task 5]]
