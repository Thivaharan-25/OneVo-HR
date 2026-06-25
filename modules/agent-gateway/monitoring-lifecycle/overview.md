# Monitoring Lifecycle

**Module:** Agent Gateway
**Feature:** Monitoring Lifecycle (Presence -> Agent Control)

## Purpose

Translates time-attendance events (clock-in, clock-out, break start, break end) into agent monitoring commands. Ensures the desktop agent only collects data when the employee is actively working - NOT during breaks, NOT before clock-in, NOT after clock-out.

## Flow

```
Employee clocks in via tray/web or biometric/attendance terminal
  -> If verification policy requires camera photo for that work context:
      -> Employee takes photo via webcam
      -> Photo sent to Identity Verification for matching/review
      -> Clock-in proceeds only after photo is accepted or policy-defined fallback applies
  -> time-attendance publishes PresenceSessionStarted
  -> AgentGateway.PresenceToAgentCommandHandler
  -> Finds agent by employee_id
  -> Sends StartMonitoring via SignalR (or queues as pending command)
  -> Agent activates all collectors
  -> Data collection begins

Employee starts break
  -> time-attendance publishes BreakStarted
  -> AgentGateway sends PauseMonitoring
  -> Agent pauses ALL collectors (NO data captured during break)
  -> Tray app shows "Break - monitoring paused"

Employee ends break
  -> time-attendance publishes BreakEnded
  -> AgentGateway sends ResumeMonitoring
  -> Agent resumes all collectors

Approved Time Off interval starts (partial-day)
  -> time-attendance publishes TimeOffIntervalStarted
  -> AgentGateway sends PauseMonitoring(reason = approved_time_off)
  -> Agent pauses ALL collectors (same as break - NO data captured)
  -> Tray app shows "Time Off - monitoring paused"
  -> Work-location evidence is not evaluated
  -> Activity Monitoring ignores this interval
  -> Discrepancy Engine treats this interval as explained absence

Approved Time Off interval ends (or employee returns early)
  -> time-attendance publishes TimeOffIntervalEnded
  -> AgentGateway sends ResumeMonitoring
  -> Agent resumes all collectors
  -> If employee does not return after configured grace period:
     -> Create late_return_from_time_off alert (not normal idle)
     -> Route through Monitoring Policy

Employee clocks out via tray/web or biometric/attendance terminal
  -> If verification policy requires camera photo for that work context:
      -> Employee takes photo via webcam
      -> Photo sent to Identity Verification for matching/review
      -> Clock-out proceeds after photo accepted or policy-defined fallback applies
  -> time-attendance publishes PresenceSessionEnded
  -> AgentGateway sends StopMonitoring
  -> Agent stops collectors, flushes remaining buffer to server
  -> Agent disconnects from SignalR command hub
```

## Key Rules

1. **Agent starts in `Stopped` state.** No data collection until `StartMonitoring` received.
2. **Break = complete silence.** Zero data captured. Active/idle tracking paused. No app tracking. No screenshots. Nothing. This is a GDPR requirement for employee break time privacy.
3. **Approved Time Off interval = complete silence.** Same data collection pause as breaks. During approved partial-day Time Off, no idle tracking, no app tracking, no work-location evidence evaluation, no discrepancy alerts. Late return from Time Off is a separate alert type (`late_return_from_time_off`), not normal idle.
4. **Clock-out = flush + stop.** Agent must flush any buffered data BEFORE stopping, then stop completely.
5. **Orphan protection:** If agent never receives `StopMonitoring` (server crash, network issue), agent auto-stops at midnight local time. Hangfire job `ReconcileOrphanSessionsJob` detects agents still reporting as "active" past their shift end time and sends `StopMonitoring`.
6. **Multiple devices:** If employee has multiple registered agents (e.g., desktop + laptop), `StartMonitoring` is sent to ALL agents. Only one will be actively used, but both must be ready.
7. **Clock-in/out photo capture is policy-driven.** Tenant policy can require camera photo capture for remote users, onsite users, both, or neither. When required, photo capture happens on each applicable tray/web clock-in or clock-out; it is not a one-time setup. Biometric/attendance terminal events create device verification records, and any additional camera/photo evidence is created only when policy requires it.
8. **Device enrollment is one-time.** Employees sign in once to link their device. After that, the device credential is stored securely (DPAPI) and auto-renewed. Employees do NOT need to log in again each shift - the tray app is always connected under their enrolled identity.

## Activity-Monitoring Integration

The `activity-monitoring` module must validate that incoming snapshots fall within an active presence window:

```csharp
// When processing ingested data
var presenceSession = await _presenceService.GetActiveSessionAsync(employeeId, snapshot.Timestamp, ct);
if (presenceSession == null)
{
    // Snapshot arrived outside presence window - log warning, discard data
    _logger.LogWarning("Snapshot from {EmployeeId} at {Time} has no active presence session", employeeId, snapshot.Timestamp);
    return; // Do NOT store
}
if (presenceSession.IsOnBreak(snapshot.Timestamp))
{
    // Snapshot arrived during break - should never happen if agent respects PauseMonitoring
    _logger.LogWarning("Snapshot from {EmployeeId} at {Time} during break - discarding", employeeId, snapshot.Timestamp);
    return;
}
if (presenceSession.IsOnApprovedTimeOff(snapshot.Timestamp))
{
    // Snapshot arrived during approved Time Off interval - should never happen if agent respects PauseMonitoring
    _logger.LogWarning("Snapshot from {EmployeeId} at {Time} during approved time off - discarding", employeeId, snapshot.Timestamp);
    return;
}
```

## Hangfire Jobs

| Job | Schedule | Queue | Purpose |
|:----|:---------|:------|:--------|
| `ReconcileOrphanSessionsJob` | Every 30 min | Medium | Detect agents active past shift end, send StopMonitoring |

## Related

- [[modules/agent-gateway/remote-commands/overview|Remote Commands]] - SignalR command dispatch mechanism
- [[modules/time-attendance/overview|Time & Attendance]] - Source of presence lifecycle events
- [[modules/activity-monitoring/overview|Activity Monitoring]] - Consumer of activity data, validates presence window
- [[modules/agent-gateway/data-collection|Data Collection]] - Agent-side collectors respect lifecycle state
