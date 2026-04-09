# Custom Report Creation

**Area:** Analytics & Reporting  
**Required Permission(s):** `reports:create`  
**Related Permissions:** `reports:manage` (save as template, schedule)

---

## Preconditions

- Data exists in system
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Start Report Builder
- **UI:** Reports → "Create Report" → select data source: Employees, Leave, Payroll, Attendance, Performance, Activity
- **API:** `GET /api/v1/reports/data-sources`

### Step 2: Configure Columns
- **UI:** Select fields to include (drag-and-drop) → set column order → rename headers if needed

### Step 3: Apply Filters
- **UI:** Add filters: date range, department, status, etc. → combine with AND/OR

### Step 4: Group & Sort
- **UI:** Group by: department, team, month → sort by: name, value, date → add subtotals

### Step 5: Preview & Run
- **UI:** Click "Preview" → see sample data → click "Run" → full report generated
- **API:** `POST /api/v1/reports`
- **Backend:** ReportService.ExecuteAsync() → [[modules/reporting-engine/report-execution/overview|Report Execution]]
- **DB:** `report_definitions`, `report_executions`

### Step 6: Save & Export
- **UI:** Save as template for reuse → export to CSV / Excel / PDF
- Links: [[Userflow/Analytics-Reporting/scheduled-report-setup|Scheduled Report Setup]] (for automation)

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No data matches filters | Empty report | "No records match the selected criteria" |
| Too many records | Performance warning | "Report contains 50,000+ rows — consider adding filters" |

## Events Triggered

- `ReportExecuted` → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Analytics-Reporting/scheduled-report-setup|Scheduled Report Setup]]
- [[Userflow/Analytics-Reporting/data-export|Data Export]]

## Module References

- [[modules/reporting-engine/report-definitions/overview|Report Definitions]]
- [[modules/reporting-engine/report-execution/overview|Report Execution]]
- [[modules/reporting-engine/overview|Reporting Engine]]
