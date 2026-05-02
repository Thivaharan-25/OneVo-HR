# WorkSync Analytics

**Area:** WorkSync -> Analytics  
**Trigger:** Workspace member opens dashboards, saves views, or exports reports  
**Required Permission(s):** `analytics:read`  
**Related Permissions:** `analytics:write`, `analytics:export`

---

## Flow Steps

### Step 1: Open Dashboard List
- **UI:** WorkSync -> Analytics
- **API:** `GET /api/v1/workspaces/{wsId}/dashboards`
- **Backend:** Applies dashboard visibility using workspace sharing and fine-grained ACL rows

### Step 2: View Dashboard
- **UI:** User opens dashboard with widgets such as velocity, burndown, cumulative flow, time, task status, or OKR progress
- **Backend:** Widget `config_json` controls filter, date range, and data source

### Step 3: Create or Edit Dashboard
- **Permission:** `analytics:write`
- **API:** `POST /api/v1/workspaces/{wsId}/dashboards`, `PATCH /api/v1/dashboards/{id}`
- **User Action:** Add widgets, change layout, set default dashboard

### Step 4: Share Dashboard
- **API:** `POST /api/v1/dashboards/{id}/share`
- **Options:** user, team, workspace, can-edit permission
- **Backend:** Writes `dashboard_shares` or updates workspace-wide `is_shared`

### Step 5: Save View
- **UI:** User saves filter/sort configuration from tasks, sprints, or projects
- **API:** `POST /api/v1/workspaces/{wsId}/saved-views`
- **Result:** Saved view is reusable and can be shared if allowed

### Step 6: Export Report
- **API:** `POST /api/v1/workspaces/{wsId}/reports/export`
- **Backend:** Queues async export job
- **UI:** User receives notification when export is ready

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Dashboard not shared | API returns 403/404 | "Dashboard not available" |
| Widget config invalid | Save rejected | Widget validation message |
| Export fails | Export job marked failed | Failure notification |
| Large report | Export remains async | Queued/processing status |

## Events Triggered

- `ReportExportReadyEvent`
- `DashboardShared`
- `SavedViewShared`

## Related Flows

- [[Userflow/Work-Management/planning-flow|Planning - Sprints and Boards]]
- [[Userflow/Work-Management/task-flow|Task Management]]
- [[Userflow/Work-Management/goals-okr-flow|Goals and OKRs]]
- [[Userflow/Analytics-Reporting/data-export|Data Export]]

## Module References

- [[modules/work-management/analytics/overview|WorkSync Analytics]]
- [[database/schemas/wms-analytics|WMS Analytics Schema]]
