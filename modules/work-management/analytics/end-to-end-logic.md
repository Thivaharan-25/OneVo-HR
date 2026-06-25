# Insight & Analytics - End-to-End Logic

**Phase:** Phase 2 - deferred
**Phase 1 Status:** Not active in current Phase 1 Work implementation; retained as future design reference.

**Module:** WorkSync
**Feature:** Insight & Analytics

---

## Dashboard Visibility Check

```
GET /api/v1/workspaces/{wsId}/dashboards
  -> GetDashboardsHandler
    -> Load dashboards WHERE workspace_id = ?
      AND (
        is_shared = true                          <- workspace-wide quick toggle
        OR created_by_id = current_user           <- own dashboards
        OR EXISTS (                               <- fine-grained ACL
            SELECT 1 FROM dashboard_shares
            WHERE dashboard_id = d.id
            AND (
              (share_type = 'user' AND target_id = current_user)
              OR (share_type = 'workspace')
            )
          )
      )
    -> Return Result<List<DashboardDto>>
```

## Add Chart Widget

```
POST /api/v1/dashboards/{id}/widgets
  body: { widget_type, title, data_source, config_json, position_json }
  -> AddWidgetHandler
    -> 1. Verify caller has write access to dashboard
    -> 2. Validate: widget_type in enum, data_source in enum
    -> 3. Validate config_json structure for widget_type:
         burndown widget requires sprint_id in config_json when Phase 2 planning is enabled
         velocity widget requires project_id when Phase 2 analytics is enabled
    -> 4. INSERT chart_widgets
    -> Return Result<WidgetDto>
  -> 201 Created
```

## Async Report Export

```
POST /api/v1/workspaces/{wsId}/reports/export
  body: { report_type, format, parameters_json }
  -> QueueReportExportHandler
    -> 1. INSERT report_exports (status = "queued")
    -> 2. Enqueue Hangfire job: ProcessReportExportJob(export_id)
    -> Return 202 Accepted with { export_id, status_url }

ProcessReportExportJob (Hangfire):
    -> 1. UPDATE report_exports.status = "processing"
    -> 2. Generate report data from parameters_json
    -> 3. Render to requested format (pdf/csv/xlsx)
    -> 4. Upload to Cloudflare R2 object storage via IStorageService
    -> 5. INSERT file_assets row
    -> 6. UPDATE report_exports:
             status = "ready"
             file_asset_id = new asset id
             completed_at = now()
    -> 7. Publish ReportExportReadyEvent -> notify user with download link
    -> On failure: status = "failed"

GET /api/v1/workspaces/{wsId}/reports/exports/{id}
  -> Poll for status: returns { status, download_url? }
```

## Share Dashboard (Fine-Grained)

```
POST /api/v1/dashboards/{id}/share
  body: { share_type, target_id, can_edit }
  -> ShareDashboardHandler
    -> 1. Verify caller has manage access (owner or workspace admin)
    -> 3. UPSERT dashboard_shares (unique on dashboard_id + share_type + target_id)
    -> Return 201
```

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Export still processing | 200 | status = "processing" |
| Export failed | 200 | status = "failed" with error message |
| Widget config invalid for type | 422 | Widget config missing required field |

## Related

- [[modules/work-management/analytics/overview|Analytics Overview]]
- [[modules/work-management/analytics/testing|Analytics Testing]]
