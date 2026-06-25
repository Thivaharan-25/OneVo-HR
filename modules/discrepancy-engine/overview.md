# Module: Discrepancy Engine

**Feature Folder:** `Application/Features/DiscrepancyEngine`
**Phase:** 1 - Build
**Pillar:** Monitoring
**Tables:** 3 (`discrepancy_events`, `wms_daily_time_logs`, `employee_discrepancy_baselines`)
**Task File:** [[current-focus/DEV3-activity-monitoring|DEV3: Activity Monitoring]] (Discrepancy Engine section)

---

## Purpose

The Discrepancy Engine is a daily end-of-day job that cross-references three data streams to detect meaningful gaps between what an employee actually did on their device and what they reported in the Work Management System (WMS). It is the core of the automated accountability layer for monitoring monitoring.

**The three streams compared:**
1. **HR Active Time** - ground truth from `activity_daily_summary.total_active_minutes` (already excludes breaks and approved Time Off intervals, since monitoring is paused during those periods)
2. **WMS Reported Time** - task/work logs from internal WorkSync `time_logs` and `wms_daily_time_logs` projections
3. **Calendar/Time Off/Meeting Time** - scheduled events from `calendar_events` and approved Time Off intervals that explain legitimate gaps

**Partial-day Time Off handling:** Approved Time Off intervals are treated as explained absence. Since monitoring is paused during approved Time Off, `total_active_minutes` already excludes that time. The expected baseline (scheduled working hours) must also be reduced by approved Time Off minutes so the gap calculation remains accurate. A full-day Time Off means no discrepancy computation for that day. (meetings, OOO, training)

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/activity-monitoring/overview\|Activity Monitoring]] | `IActivityMonitoringService` | Source of HR active time |
| **Depends on** | [[modules/calendar/overview\|Calendar]] | `ICalendarService` | Source of meeting/event time |
| **Depends on** | [[modules/work-management/time/overview|WorkSync Time]] | `IWorkSyncTimeService` | Source of WorkSync task logged time |
| **Depends on** | [[modules/configuration/monitoring-toggles/overview\|Configuration]] | `IConfigurationService` | Tenant-configured discrepancy thresholds |
| **Consumed by** | [[modules/notifications/overview\|Notifications]] | - | Phase 1 sends notifications through lightweight routing; Phase 2 may use Automation Center resolvers |
| **Consumed by** | [[modules/productivity-analytics/overview\|Productivity Analytics]] | - | Discrepancy rate as a signal |

---

## Public Interface

```csharp
// ONEVO.Application.Features.DiscrepancyEngine/Public/IDiscrepancyEngineService.cs
public interface IDiscrepancyEngineService
{
    Task<Result<DiscrepancyEventDto?>> GetDiscrepancyForDateAsync(
        Guid employeeId, DateOnly date, CancellationToken ct);

    Task<Result<IReadOnlyList<DiscrepancyEventDto>>> GetDiscrepanciesForRangeAsync(
        Guid employeeId, DateOnly from, DateOnly to, CancellationToken ct);

    Task<Result<IReadOnlyList<DiscrepancyEventDto>>> GetCoveredDiscrepanciesAsync(
        Guid reviewerEmployeeId, DateOnly date, CancellationToken ct); // resolves allowed employees through management coverage
}
```

---

## How It Works

### Phase 1 Monitoring Alerts

Phase 1 monitoring alerts do not use configurable Exception Engine rules or Workflow Engine routing.

Discrepancy Engine is a Phase 1 alert producer. It creates lightweight alert/notification records and routes them through Notifications/Inbox.

**Monitoring Policy recipient resolution:**

Monitoring Policy determines who receives monitoring/verification alerts using `monitoring_alert_recipient_resolver`.

Allowed values:
- `management_coverage_availability_chain` (default)
- `reporting_manager`

`management_coverage_availability_chain` routes to the first available responsible person from the employee's active management coverage assignments:
1. Load active date-effective coverage assignments.
2. Order responsible people by configured coverage priority / responsibility weight / effective assignment order.
3. Filter to users with the required alert permission.
4. Check availability:
   - scheduled to work now, or inside the alert routing window
   - clocked in / present
   - not on approved leave
   - not marked unavailable
5. If a responsible person is scheduled but has not reached scheduled start time + `monitoring_alert_wait_for_scheduled_recipient_grace_minutes`, wait before skipping.
6. If no eligible available person exists, follow `monitoring_alert_unresolved_routing_action`.

`reporting_manager` resolves the employee's reporting manager from position hierarchy, then applies the same permission and availability checks. If unavailable and `monitoring_alert_fallback_to_management_coverage_chain` is enabled, fall back to `management_coverage_availability_chain`.

Never silently route monitoring alerts to random HR/admin users.

### Timing

Discrepancy Engine runs after the employee's attendance day closes or during the configured daily job window. It does not live-notify managers during the workday.

### The Daily Job - `DiscrepancyEngineJob`

Runs **daily at 10:30 PM** (after work hours, before `GenerateDailyReportsJob` at 11:30 PM). The specific time is the default; tenants may configure a different job window.

```csharp
// ONEVO.Application.Features.DiscrepancyEngine/Jobs/DiscrepancyEngineJob.cs
public class DiscrepancyEngineJob
{
    public async Task RunAsync(Guid tenantId, DateOnly date, CancellationToken ct)
    {
        var employees = await _employeeService.GetActiveEmployeesAsync(tenantId, ct);

        foreach (var employee in employees)
        {
            // Stream 1: HR active time (ground truth)
            var activitySummary = await _activityService.GetDailySummaryAsync(employee.Id, date, ct);
            if (activitySummary == null) continue; // no agent data - skip

            var hrActiveMinutes = activitySummary.TotalActiveMinutes;

            // Stream 2: WMS task logged time (what they claimed)
            var wmsMinutes = await _workSyncTimeService.GetLoggedMinutesAsync(employee.Id, date, ct);

            // Stream 3: Calendar-explained time (legitimate gaps)
            var calendarMinutes = await _calendarService.GetTotalEventMinutesAsync(employee.Id, date, ct);

            // Compute unaccounted gap
            // Note: hrActiveMinutes already excludes approved Time Off intervals
            // (monitoring is paused during Time Off), so no separate Time Off subtraction
            // is needed here. Approved Time Off reduces the expected baseline, not active time.
            var unaccountedMinutes = hrActiveMinutes - wmsMinutes - calendarMinutes;

            var threshold = await _configService.GetDiscrepancyThresholdAsync(tenantId, ct);
            var severity = CalculateSeverity(unaccountedMinutes, threshold);

            await _repository.UpsertDiscrepancyEventAsync(new DiscrepancyEvent
            {
                TenantId = tenantId,
                EmployeeId = employee.Id,
                Date = date,
                HrActiveMinutes = hrActiveMinutes,
                WmsLoggedMinutes = wmsMinutes,
                CalendarMinutes = calendarMinutes,
                UnaccountedMinutes = unaccountedMinutes,
                Severity = severity,
                ThresholdMinutes = threshold.AcceptableGapMinutes
            }, ct);

            await NotifyIfRequiredAsync(employee, severity, unaccountedMinutes, ct);
        }
    }
}
```

### Severity Thresholds

Severity is calculated by `DiscrepancySeverityCalculator.Calculate()`. When a pre-computed baseline exists (>= 5 samples, stddev > 0), z-score-relative thresholds are used. New employees without enough history fall back to absolute thresholds.

**Baseline-relative (z-score) - used when baseline is available:**

| Severity | Z-Score | Description |
|:---------|:--------|:------------|
| `none` | z < 1.0 | Within normal range for this employee |
| `low` | 1.0 <= z < 1.5 | Mildly above personal baseline - automated reminder |
| `high` | 1.5 <= z < 2.5 | Significantly above baseline - configured discrepancy reviewer notified privately |
| `critical` | z >= 2.5 | Extreme anomaly - Phase 1: configured discrepancy reviewer or management coverage owner notified immediately; Phase 2: Workflow/Automation escalation |

**Absolute fallback (new employees, < 5 baseline samples):**

Severity thresholds are tenant-configured. Default values below are examples only. The computed threshold used for each event is copied into `discrepancy_events.threshold_minutes` for audit.

| Severity | Unaccounted Gap (default) | Action |
|:---------|:--------------------------|:-------|
| `none` | < 30 min | No action |
| `low` | 30-60 min | Automated reminder to employee: "You have unlogged active time today" |
| `high` | 60-180 min | Phase 1: configured discrepancy reviewer or management coverage owner notified privately (employee NOT informed) |
| `critical` | 180+ min | Phase 1: configured discrepancy reviewer or management coverage owner notified immediately; Phase 2 may use Workflow/Automation escalation |

See [[modules/discrepancy-engine/statistical-baselines/overview|Statistical Baselines]] for full details on baseline computation.

### Notification Behaviour

```csharp
private async Task NotifyIfRequiredAsync(Employee employee, DiscrepancySeverity severity,
    int unaccountedMinutes, CancellationToken ct)
{
    switch (severity)
    {
        case DiscrepancySeverity.Low:
            // Remind employee to log time - does NOT reveal discrepancy analysis
            await _notificationService.SendAsync(new Notification
            {
                RecipientId = employee.UserId,
                Type = NotificationType.UnloggedTimeReminder,
                Data = new { UnloggedMinutes = unaccountedMinutes }
            }, ct);
            break;

        case DiscrepancySeverity.High:
            // Phase 1: route to recipient resolved by Monitoring Policy via Notifications/Inbox
            var highReviewer = await _monitoringPolicyService.ResolveAlertRecipientAsync(employee.Id, ct);
            await _notificationService.SendAsync(new Notification
            {
                RecipientId = highReviewer.UserId,
                Type = NotificationType.DiscrepancyReviewRequired,
                Data = new { EmployeeId = employee.Id, Severity = "high", UnaccountedMinutes = unaccountedMinutes }
            }, ct);
            break;

        case DiscrepancySeverity.Critical:
            // Phase 1: route to recipient resolved by Monitoring Policy via Notifications/Inbox
            var criticalReviewer = await _monitoringPolicyService.ResolveAlertRecipientAsync(employee.Id, ct);
            await _notificationService.SendAsync(new Notification
            {
                RecipientId = criticalReviewer.UserId,
                Type = NotificationType.DiscrepancyReviewRequired,
                Data = new { EmployeeId = employee.Id, Severity = "critical", UnaccountedMinutes = unaccountedMinutes }
            }, ct);
            break;
    }
}
```

---

## Visibility Rules

**NON-NEGOTIABLE: Discrepancy data is never visible to the employee.**

- Resolver-assigned reviewers see discrepancy summaries for employees assigned to them by workflow or management coverage
- Users with selected permissions can see tenant or covered discrepancy views according to permission and management-coverage rules
- Employees see: their own activity timeline and productivity score ONLY - never the discrepancy analysis or gap calculation
- Enforced at the repository query level using `RequirePermission("exceptions:manage")` - not just UI-level

---

## Discrepancy Scenarios

| Scenario | HR Active | WMS Logged | Calendar | Result |
|:---------|:----------|:-----------|:---------|:-------|
| Honest high performer | 7.5h active | 7h logged | 1h meetings | `none` - 30 min gap within threshold |
| Over-reporter | 3h active | 7h claimed | 0h meetings | `critical` - 240 min gap |
| Under-reporter (forgot to log) | 7h active | 3h logged | 1h meetings | `low` - reminder sent to log time |
| Meeting-heavy day | 2h active | 2h logged | 5h meetings | `none` - calendar resolves the gap |
| Deep research day | 4h active | 3h logged | 2h meetings | `none` - 60 min gap within threshold |

---

## Code Location (Clean Architecture)

Domain entities:
  ONEVO.Domain/Features/DiscrepancyEngine/Entities/
  ONEVO.Domain/Features/DiscrepancyEngine/Events/

Application (CQRS):
  ONEVO.Application/Features/DiscrepancyEngine/Commands/
  ONEVO.Application/Features/DiscrepancyEngine/Queries/
  ONEVO.Application/Features/DiscrepancyEngine/DTOs/Requests/
  ONEVO.Application/Features/DiscrepancyEngine/DTOs/Responses/
  ONEVO.Application/Features/DiscrepancyEngine/Validators/
  ONEVO.Application/Features/DiscrepancyEngine/EventHandlers/

Infrastructure:
  ONEVO.Infrastructure/Persistence/Configurations/DiscrepancyEngine/

API endpoints:
  ONEVO.Api/Controllers/DiscrepancyEngine/DiscrepancyEngineController.cs

---

## Database Table

See [[database/schemas/discrepancy-engine|Discrepancy Engine Schema]] - `discrepancy_events`, `wms_daily_time_logs`, and `employee_discrepancy_baselines` tables.

## Features

- [[modules/discrepancy-engine/statistical-baselines/overview|Statistical Baselines]] - Per-employee rolling baseline computation and z-score severity classification
- [[modules/discrepancy-engine/notification-enrichment/overview|Notification Enrichment]] - AI-generated narrative context on critical discrepancy alerts via Claude API

---

## Hangfire Jobs

| Job | Schedule | Queue | Purpose |
|:----|:---------|:------|:--------|
| `ComputeDiscrepancyBaselinesJob` | Daily 10:00 PM | Default | Compute rolling 30-day avg+stddev per employee |
| `DiscrepancyEngineJob` | Daily 10:30 PM (per tenant timezone) | Default | Process all active employees for the day |

---

## Domain Events (intra-module - MediatR)

> These events are published and consumed within this module only. They never cross the module boundary.

| Event | Published When | Handler |
|:------|:---------------|:--------|
| _(none)_ | - | - |

## Cross-Module Events (cross-module - MediatR INotification)

### Publishes

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `DiscrepancyCriticalDetected` | Severity = `critical` | [[modules/notifications/overview\|Notifications]] (Phase 1 lightweight alert, recipient resolved by Monitoring Policy); `DiscrepancyEnrichmentHandler` (AI narrative enrichment); Phase 2 may route through Automation Center |

### Consumes

| Event | Source Module | Action Taken |
|:------|:-------------|:-------------|
| `DailySummaryAggregated` | [[modules/activity-monitoring/overview\|Activity Monitoring]] | Trigger daily discrepancy computation for all employees |

---

## Key Business Rules

1. **No agent data = no discrepancy.** If an employee has no activity data for the day (no agent installed, holiday, full-day Time Off), the job skips them. Partial-day Time Off reduces the expected baseline but does not skip the day.
2. **WorkSync is optional.** If the tenant has no WorkSync Time module enabled, `wms_logged_minutes = 0` and only the calendar cross-reference is used.
3. **Thresholds are tenant-configurable.** The default thresholds (30/60/180 min) can be adjusted per tenant via the Configuration module.
4. **Employee privacy.** The `low` severity notification to the employee says "You have unlogged hours today" - it does NOT say "we detected you worked X hours and only logged Y." The discrepancy analysis is never surfaced to the employee.

---

## Related

- [[Userflow/Discrepancy-Engine/discrepancy-review|Discrepancy Review]] - reviewer-facing flow for high/critical discrepancy records

- [[database/schemas/discrepancy-engine|Discrepancy Engine Schema]] - `discrepancy_events` and `wms_daily_time_logs` table definitions
- [[modules/activity-monitoring/overview|Activity Monitoring]] - provides `activity_daily_summary`
- [[modules/calendar/overview|Calendar]] - provides meeting/event time
- [[modules/notifications/overview|Notifications]] - delivers discrepancy alerts
- [[modules/productivity-analytics/overview|Productivity Analytics]] - aggregates discrepancy_rate as a metric
- [[backend/messaging/event-catalog|Event Catalog]] - `DiscrepancyCriticalDetected`, `DiscrepancyHighDetected`
- [[current-focus/DEV3-activity-monitoring|DEV3: Activity Monitoring]] - implementation task
