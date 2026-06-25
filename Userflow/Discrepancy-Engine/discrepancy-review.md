# Discrepancy Review

**Area:** Monitoring -> Discrepancies  
**Trigger:** Daily discrepancy job detects a meaningful mismatch  
**Required Permission(s):** `exceptions:manage`  
**Related Permissions:** `monitoring:view`, `analytics:view`

---

## Preconditions

- Activity monitoring is enabled -> [[Userflow/Monitoring/monitoring-configuration|Monitoring Configuration]]
- WorkSync time tracking is enabled when the tenant uses WorkSync -> [[Userflow/Work-Management/time-tracking-flow|Time Tracking]]
- Calendar and schedule data are available -> [[Userflow/Calendar/calendar-event-creation|Calendar Event Creation]]
- Required permissions are assigned -> [[Userflow/Auth-Access/permission-assignment|Permission Assignment]]

## Flow Steps

### Step 1: Baseline Job Runs
- **System:** `ComputeDiscrepancyBaselinesJob` runs before the discrepancy check
- **Backend:** Updates employee rolling averages and standard deviations where enough samples exist
- **DB:** `employee_discrepancy_baselines`

### Step 2: Daily Discrepancy Job Runs
- **System:** `DiscrepancyEngineJob` runs after work hours in the tenant timezone
- **Backend:** Compares HR active time, WorkSync logged time, and calendar-explained time
- **DB:** Upserts `discrepancy_events`

### Step 3: Severity Is Calculated
- **Backend:** Uses employee baseline thresholds when available; otherwise falls back to tenant absolute thresholds
- **Result:** Severity becomes `none`, `low`, `high`, or `critical`

### Step 4: Notification Is Routed
- **Low:** Employee receives a neutral unlogged-time reminder without seeing discrepancy analysis
- **Critical:** Phase 1 routes the notification to the recipient resolved by Monitoring Policy via Notifications/Inbox. Phase 2 may use Automation Center for advanced routing.
- **Rule:** Discrepancy routing must not target fixed role names. It uses resolver configuration, management coverage, and permissions.
- **Event:** `DiscrepancyCriticalDetected` for critical records

### Step 5: Reviewer Opens Discrepancy List
- **UI:** Monitoring -> Discrepancies
- **API:** `GET /api/v1/discrepancies?date={date}&severity={severity}`

### Step 6: Reviewer Opens Detail View
- **UI:** Detail page shows:
  - HR active minutes
  - WorkSync logged minutes
  - calendar-explained minutes
  - unaccounted minutes
  - threshold used
  - baseline context where available
  - links to activity, time logs, calendar, and presence records

### Step 7: Reviewer Decides Outcome
- **Allowed Actions:**
  - Mark reviewed
  - Dismiss as expected/false positive
  - Add internal note
  - Request follow-up from the configured reviewer or coverage owner
  - Open related activity or time-log screens
  - Mark review outcome and keep audit trail
  - Phase 2 only: route to Exception Engine / Automation Center if formal configurable alert workflow is enabled

### Step 8: System Records Audit Trail
- **Backend:** Stores reviewer, timestamp, resolution, and notes
- **Security Rule:** Employee never sees discrepancy analysis or gap calculation

## Variations

### WorkSync Disabled
- `wms_logged_minutes` is treated as zero or unavailable depending on tenant configuration
- Reviewer sees that WorkSync was not part of the comparison

### No Agent Data
- No discrepancy is created for that employee/date
- Reviewer can still inspect agent deployment or activity gaps through Monitoring

### Employee Has Approved Time Off or Calendar Events
- Calendar-explained time reduces the unaccounted gap
- Detail view shows the event or Time Off record that explains the time

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Reviewer lacks permission | API returns 403 | "You do not have permission to view discrepancies" |
| Activity summary missing | Job skips discrepancy | No discrepancy record for that date |
| WorkSync time unavailable | Comparison continues without WorkSync signal | "WorkSync time unavailable" badge |
| Calendar service unavailable | Job records unresolved calendar context or retries | Calendar context warning |
| Evidence retention expired | Detail opens with limited evidence | "Some evidence is no longer available" |

## Events Triggered

- `DiscrepancyCriticalDetected`
- `DiscrepancyReviewed`
- `DiscrepancyDismissed`

## Cross-Module Impact

| Module | Impact |
|:-------|:-------|
| Activity Monitoring | Provides daily active-time summary |
| WorkSync Time | Provides task/time logs through daily projection |
| Calendar | Explains meetings, Time Off, holidays, and scheduled events |
| Notifications | Routes low/high/critical notifications |
| Productivity Analytics | Uses discrepancy rate as an analytics signal |
| Exception Engine | Phase 2 only; may receive escalated cases for formal configurable alert handling |
| Audit Logs | Records review and resolution actions |

## Related Flows

- [[Userflow/Monitoring/activity-snapshot-view|Activity Snapshot View]]
- [[Userflow/Work-Management/time-tracking-flow|Time Tracking]]
- [[Userflow/Exception-Engine/alert-review|Alert Review]]
- [[Userflow/Analytics-Reporting/productivity-dashboard|Productivity Dashboard]]

## Module References

- [[modules/discrepancy-engine/overview|Discrepancy Engine]]
- [[modules/discrepancy-engine/statistical-baselines/overview|Statistical Baselines]]
- [[modules/discrepancy-engine/notification-enrichment/overview|Notification Enrichment]]
