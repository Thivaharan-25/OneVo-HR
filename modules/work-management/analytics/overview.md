# Insight & Analytics

**Module:** WorkSync
**Feature:** Insight & Analytics
**Namespace:** `WorkSync.Analytics`
**Owner:** DEV6
**Tables:** 7

---

## Purpose

Custom dashboards with configurable chart widgets, saved view filters, report snapshots, and async report exports. Sharing is controlled by two mechanisms: `dashboards.is_shared` (workspace-wide quick toggle) AND `dashboard_shares` (fine-grained ACL). Both must be checked.

---

## Database Tables

### `dashboards`
Key columns: `workspace_id`, `tenant_id`, `name`, `description`, `created_by_id`, `is_shared` (workspace-wide quick toggle — all members can view when true), `is_default`.

### `chart_widgets`
Key columns: `dashboard_id`, `widget_type` (`bar`, `line`, `pie`, `table`, `burndown`, `velocity`, `cumulative_flow`, `metric_card`), `title`, `config_json` (all filter/date-range/scope params — no separate filter tables), `position_json` (grid coordinates), `data_source` (`tasks`, `sprints`, `time_logs`, `okr`).

### `saved_views`
Reusable filter sets. Key columns: `workspace_id`, `user_id` (nullable — null for workspace-level views), `name`, `entity_type` (`tasks`, `sprints`, `projects`), `filter_json`, `sort_json`, `is_pinned`.

### `report_snapshots`
Point-in-time report captures. Key columns: `workspace_id`, `report_type`, `generated_at`, `parameters_json`, `data_json`, `generated_by_id`.

### `report_exports`
Async export jobs. Key columns: `workspace_id`, `report_type`, `format` (`pdf`, `csv`, `xlsx`), `parameters_json`, `status` (`queued`, `processing`, `ready`, `failed`), `file_asset_id` (FK → file_assets, nullable — set when Hangfire completes), `requested_by_id`, `completed_at`.

Hangfire processes export → uploads to Azure Blob → sets `file_asset_id` → sends notification.

### `dashboard_shares`
Fine-grained ACL for dashboard sharing. Key columns: `dashboard_id`, `share_type` (`user`, `team`, `workspace`), `target_id` (user_id or team_id — null if workspace), `can_edit`, `shared_by_id`.

**Visibility check:** user can view dashboard if `dashboards.is_shared = true` OR there is a matching `dashboard_shares` row.

### `saved_view_shares`
Fine-grained ACL for saved views. Key columns: `saved_view_id`, `share_type`, `target_id`, `can_edit`, `shared_by_id`.

---

## Key Business Rules

1. **Dashboard visibility:** Check BOTH `dashboards.is_shared` (workspace-wide) AND `dashboard_shares` (ACL). A user can view if either condition is true.
2. `widget.config_json` stores all filter, date-range, and scope parameters — there are no separate filter tables.
3. Report exports are async: Hangfire job → Azure Blob upload → `file_asset_id` set → notification sent. Never block HTTP on export.
4. `saved_views` with `user_id = null` are workspace-level; with `user_id` set they are personal (My Space).
5. `is_default` dashboard: only one per user per workspace — application layer enforces uniqueness.

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
| POST | `/api/v1/dashboards/{id}/share` | `analytics:manage` | Share dashboard |
| GET | `/api/v1/workspaces/{wsId}/saved-views` | `analytics:read` | List saved views |
| POST | `/api/v1/workspaces/{wsId}/saved-views` | `analytics:write` | Save view |
| POST | `/api/v1/workspaces/{wsId}/reports/export` | `analytics:read` | Queue export |
| GET | `/api/v1/workspaces/{wsId}/reports/exports/{id}` | `analytics:read` | Check export status |

---

## Related

- [[modules/work-management/planning/overview|Planning]] — burndown/velocity widget data sources
- [[modules/work-management/tasks/overview|Task Management]] — task data source
- [[database/schemas/wms-analytics|WMS Analytics Schema]]
- [[current-focus/DEV6-tasks-boards-planning|DEV6 Task 5]]
