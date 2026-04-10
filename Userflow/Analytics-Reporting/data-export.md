# Data Export

**Area:** Analytics & Reporting  
**Trigger:** User exports data to CSV or Excel (user action)
**Required Permission(s):** `analytics:export`  
**Related Permissions:** `analytics:view` (view data first)

---

## Preconditions

- Data visible on any analytics page
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Data
- **UI:** Any analytics/reporting page with data displayed

### Step 2: Click Export
- **UI:** Click "Export" button → select format: CSV, Excel (.xlsx), PDF
- **API:** `POST /api/v1/analytics/export`

### Step 3: Configure Export
- **UI:** Select columns to include → apply current page filters → select date range → optionally anonymize employee names (for compliance)

### Step 4: Download
- **UI:** File generated → download starts → for large exports: "Processing — you'll be notified when ready"
- **Backend:** Large exports processed async via Hangfire → notification when complete

## Variations

### Anonymized export
- With compliance requirement → employee names replaced with IDs → useful for external audits

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Export too large | Async processing | "Export queued — we'll notify you when ready" |
| No data | Empty file | "No data to export with current filters" |

## Events Triggered

- `DataExported` → audit trail

## Related Flows

- [[Userflow/Analytics-Reporting/productivity-dashboard|Productivity Dashboard]]
- [[Userflow/Analytics-Reporting/report-creation|Report Creation]]
- [[Userflow/Analytics-Reporting/workforce-snapshot|Workforce Snapshot]]

## Module References

- [[modules/productivity-analytics/overview|Productivity Analytics]]
- [[modules/reporting-engine/overview|Reporting Engine]]
