# Scheduled Report Setup

**Area:** Analytics & Reporting  
**Required Permission(s):** `reports:manage`  
**Related Permissions:** `reports:create` (create report first)

---

## Preconditions

- Saved report template exists → [[Userflow/Analytics-Reporting/report-creation|Report Creation]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Create Schedule
- **UI:** Reports → Schedules → "Create Schedule" → select saved report template
- **API:** `POST /api/v1/reports/schedules`

### Step 2: Set Frequency
- **UI:** Select: Daily (at time), Weekly (day + time), Monthly (date + time) → set timezone

### Step 3: Set Delivery
- **UI:** Delivery method: Email (enter recipients) / In-app notification / Both → set format (CSV, Excel, PDF)
- **Backend:** ScheduledReportService.CreateAsync() → [[modules/reporting-engine/report-templates/overview|Report Templates]]
- **DB:** `report_schedules` — Hangfire recurring job created

### Step 4: Activate
- **UI:** Toggle active → system runs report automatically and delivers to recipients

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Report template deleted | Schedule fails | "Source report template no longer exists" |
| Email delivery fails | Retry + alert | "Report delivery failed — will retry in 1 hour" |

## Events Triggered

- `ScheduledReportExecuted` → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Analytics-Reporting/report-creation|Report Creation]]
- [[Userflow/Notifications/notification-preference-setup|Notification Preference Setup]]

## Module References

- [[modules/reporting-engine/report-execution/overview|Report Execution]]
- [[modules/reporting-engine/report-templates/overview|Report Templates]]
- [[backend/notification-system|Notification System]]
