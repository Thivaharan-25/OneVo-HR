# Data Export

**Area:** Analytics & Reporting  
**Required Permission(s):** `analytics:export`  
**Related Permissions:** `analytics:view` (view data first)

---

## Preconditions

- Data visible on any analytics page
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

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

- [[productivity-dashboard]]
- [[report-creation]]
- [[workforce-snapshot]]

## Module References

- [[productivity-analytics]]
- [[reporting-engine]]
