# Task: Activity Monitoring Module

**Assignee:** Dev 3
**Module:** ActivityMonitoring
**Priority:** Critical
**Dependencies:** [[current-focus/DEV4-shared-platform-agent-gateway|DEV4 Shared Platform Agent Gateway]] (agent gateway is data source)

---

## Step 1: Backend

### Acceptance Criteria

#### Data Pipeline
- [ ] `activity_raw_buffer` table — partitioned daily via `pg_partman`, batch INSERT via `COPY`/`unnest()`
- [ ] `ProcessRawBufferJob` Hangfire job (every 2 min) — parse raw -> snapshots + app usage + meetings
- [ ] `activity_snapshots` table — partitioned monthly, 90-day retention
- [ ] Intensity score calculation: `(keyboard + mouse) / max_expected * 100`, capped at 100
- [ ] `application_usage` table — time per app per day
- [ ] Window title hashing (SHA-256) — never store raw titles
- [ ] `meeting_sessions` table — Phase 1: process name matching (Teams.exe, zoom.exe)
- [ ] Camera/mic detection via process inspection
- [ ] `device_tracking` table — laptop active minutes, estimated mobile
- [ ] `activity_daily_summary` table — INSERT or UPDATE on conflict `(tenant_id, employee_id, date)`

#### Screenshots
- [ ] `screenshots` table — metadata only, files in blob storage via `IFileService`
- [ ] Screenshot trigger types: `scheduled`, `random`, `manual`
- [ ] `PurgeExpiredScreenshotsJob` (daily 4 AM) — per tenant retention policy
- [ ] Screenshot classified as RESTRICTED data

#### Application Categories
- [ ] `application_categories` table — tenant-configurable
- [ ] Glob pattern matching (e.g., `*chrome*`)
- [ ] `is_productive` flag (nullable — uncategorized apps)

#### Aggregation & Retention
- [ ] `AggregateDailySummaryJob` (every 30 min + EOD)
- [ ] `PurgeRawBufferJob` (daily 3 AM) — drop partitions > 48h
- [ ] `PurgeExpiredSnapshotsJob` (monthly) — drop partitions > 90 days
- [ ] `IActivityMonitoringService` public interface implementation

#### Security
- [ ] Feature toggle check before processing — `IConfigurationService`
- [ ] Never log window titles or app names — only counts
- [ ] Domain events: `ActivitySnapshotReceived`, `DailySummaryAggregated`
- [ ] Unit tests >= 80% coverage

### Backend References

- [[modules/activity-monitoring/overview|activity-monitoring]] — module architecture, data pipeline diagram
- [[modules/agent-gateway/overview|agent-gateway]] — data source (raw activity from desktop agent)
- [[modules/configuration/monitoring-toggles/overview|configuration]] — feature toggles gate processing
- [[security/data-classification|Data Classification]] — screenshots are RESTRICTED
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant-configurable application categories

---

## Step 2: Frontend

### Pages to Build

```
app/(dashboard)/workforce/activity/
├── page.tsx                      # Activity feed / team timeline
├── [employeeId]/
│   ├── loading.tsx               # Skeleton while loading
│   └── page.tsx                  # Employee activity deep-dive
├── screenshots/page.tsx          # Screenshot review queue
├── components/                   # Colocated feature components
│   ├── ActivityFeed.tsx          # Real-time activity stream
│   ├── ActivityTimeline.tsx      # Employee daily timeline (active/idle/break segments)
│   ├── ScreenshotGrid.tsx        # Screenshot review grid with zoom
│   └── AppUsageChart.tsx         # Per-app usage visualization
└── _types.ts                     # Local TypeScript definitions

app/(dashboard)/settings/
├── monitoring/page.tsx           # Application categories + screenshot settings
```

### What to Build

- [ ] Employee activity detail page:
  - ActivityHeatmap: hourly intensity grid for selected date range
  - AppUsageChart: stacked bar chart of time per application (productive vs unproductive vs uncategorized)
  - TimelineBar: minute-by-minute active/idle/meeting segments
  - Meeting sessions list with duration
  - Screenshot gallery (thumbnails, click to expand, with timestamp)
  - Date picker to navigate between days
- [ ] Application category management page (admin):
  - DataTable: category name, pattern, is_productive flag, app count
  - CRUD dialogs for categories
  - Uncategorized apps list with quick-assign
- [ ] Screenshot settings page (admin):
  - Enable/disable screenshots
  - Frequency: interval (minutes) or random
  - Retention period
- [ ] PermissionGate: `monitoring:read`, `monitoring:manage`, `monitoring:screenshots`

### Userflows

- [[Userflow/Workforce-Intelligence/activity-snapshot-view|Activity Snapshot View]] — view employee activity data and screenshots
- [[Userflow/Workforce-Intelligence/monitoring-configuration|Monitoring Configuration]] — configure monitoring settings and categories

### API Endpoints (Frontend Consumes)

| Method | Endpoint | Purpose |
|:-------|:---------|:--------|
| GET | `/api/v1/activity/summary/{employeeId}?date={date}` | Daily activity summary |
| GET | `/api/v1/activity/snapshots/{employeeId}?date={date}` | Activity snapshots (timeline) |
| GET | `/api/v1/activity/apps/{employeeId}?date={date}` | App usage breakdown |
| GET | `/api/v1/activity/meetings/{employeeId}?date={date}` | Meeting sessions |
| GET | `/api/v1/activity/screenshots/{employeeId}?date={date}` | Screenshot list |
| GET | `/api/v1/activity/screenshots/{id}/image` | Screenshot image |
| GET | `/api/v1/activity/categories` | Application categories |
| POST | `/api/v1/activity/categories` | Create category |
| PUT | `/api/v1/activity/categories/{id}` | Update category |
| GET | `/api/v1/activity/categories/uncategorized` | Uncategorized apps |

### Frontend References

- [[frontend/design-system/components/component-catalog|Component Catalog]] — TimelineBar, ActivityHeatmap, AppUsageChart
- [[frontend/design-system/patterns/data-visualization|Data Visualization]] — heatmaps, charts
- [[frontend/design-system/foundations/color-tokens|Color Tokens]] — productive/unproductive colors

---

## Related Tasks

- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4 Shared Platform Agent Gateway]] — agent gateway is the data ingestion source
- [[current-focus/DEV4-workforce-presence-biometric|DEV4 Workforce Presence Biometric]] — PresenceSessionEnded triggers activity pipeline
- [[current-focus/DEV2-exception-engine|DEV2 Exception Engine]] — reads IActivityMonitoringService for rule evaluation
- [[current-focus/DEV1-productivity-analytics|DEV1 Productivity Analytics]] — aggregates from activity_daily_summary
