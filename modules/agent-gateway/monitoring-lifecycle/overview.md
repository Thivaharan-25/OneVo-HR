# Monitoring Lifecycle

**Module:** Agent Gateway
**Feature:** Monitoring Lifecycle (Presence → Agent Control)

## Purpose

Translates workforce-presence events (clock-in, clock-out, break start, break end) into agent monitoring commands. Ensures the desktop agent only collects data when the employee is actively working — NOT during breaks, NOT before clock-in, NOT after clock-out.

## Flow

```
Employee clocks in via tray (remote/hybrid) or biometric (onsite)
  → If tray clock-in (remote): tray app triggers photo capture FIRST
      → Employee takes photo via webcam
      → Photo sent to Identity Verification for face match
      → Clock-in proceeds only after photo is accepted (or auto-skip timeout)
  → workforce-presence publishes PresenceSessionStarted
  → AgentGateway.PresenceToAgentCommandHandler
  → Finds agent by employee_id
  → Sends StartMonitoring via SignalR (or queues as pending command)
  → Agent activates all collectors
  → Data collection begins

Employee starts break
  → workforce-presence publishes BreakStarted
  → AgentGateway sends PauseMonitoring
  → Agent pauses ALL collectors (NO data captured during break)
  → Tray app shows "Break — monitoring paused"

Employee ends break
  → workforce-presence publishes BreakEnded
  → AgentGateway sends ResumeMonitoring
  → Agent resumes all collectors

Employee clocks out via tray (remote/hybrid) or biometric (onsite)
  → If tray clock-out (remote): tray app triggers photo capture FIRST
      → Employee takes photo via webcam
      → Photo sent to Identity Verification for face match
      → Clock-out proceeds after photo accepted (or auto-skip timeout)
  → workforce-presence publishes PresenceSessionEnded
  → AgentGateway sends StopMonitoring
  → Agent stops collectors, flushes remaining buffer to server
  → Agent disconnects from SignalR command hub
```

## Key Rules

1. **Agent starts in `Stopped` state.** No data collection until `StartMonitoring` received.
2. **Break = complete silence.** Zero data captured. Active/idle tracking paused. No app tracking. No screenshots. Nothing. This is a GDPR requirement for employee break time privacy.
3. **Clock-out = flush + stop.** Agent must flush any buffered data BEFORE stopping, then stop completely.
4. **Orphan protection:** If agent never receives `StopMonitoring` (server crash, network issue), agent auto-stops at midnight local time. Hangfire job `ReconcileOrphanSessionsJob` detects agents still reporting as "active" past their shift end time and sends `StopMonitoring`.
5. **Multiple devices:** If employee has multiple registered agents (e.g., desktop + laptop), `StartMonitoring` is sent to ALL agents. Only one will be actively used, but both must be ready.
6. **Photo on every tray clock-in and clock-out (remote/hybrid).** Photo capture is required each time a remote or hybrid employee clocks in or out via the tray app. This is not a one-time setup — it verifies presence at the start and end of every shift. Biometric terminal clock-in/out (onsite) does not require a webcam photo — the terminal handles identity verification itself.
7. **Device enrollment is one-time.** Employees sign in once to link their device. After that, the device credential is stored securely (DPAPI) and auto-renewed. Employees do NOT need to log in again each shift — the tray app is always connected under their enrolled identity.

## Activity-Monitoring Integration

The `activity-monitoring` module must validate that incoming snapshots fall within an active presence window:

```csharp
// When processing ingested data
var presenceSession = await _presenceService.GetActiveSessionAsync(employeeId, snapshot.Timestamp, ct);
if (presenceSession == null)
{
    // Snapshot arrived outside presence window — log warning, discard data
    _logger.LogWarning("Snapshot from {EmployeeId} at {Time} has no active presence session", employeeId, snapshot.Timestamp);
    return; // Do NOT store
}
if (presenceSession.IsOnBreak(snapshot.Timestamp))
{
    // Snapshot arrived during break — should never happen if agent respects PauseMonitoring
    _logger.LogWarning("Snapshot from {EmployeeId} at {Time} during break — discarding", employeeId, snapshot.Timestamp);
    return;
}
```

## Hangfire Jobs

| Job | Schedule | Queue | Purpose |
|:----|:---------|:------|:--------|
| `ReconcileOrphanSessionsJob` | Every 30 min | Medium | Detect agents active past shift end, send StopMonitoring |

## Related

- [[modules/agent-gateway/remote-commands/overview|Remote Commands]] — SignalR command dispatch mechanism
- [[modules/workforce-presence/overview|Workforce Presence]] — Source of presence lifecycle events
- [[modules/activity-monitoring/overview|Activity Monitoring]] — Consumer of activity data, validates presence window
- [[modules/agent-gateway/data-collection|Data Collection]] — Agent-side collectors respect lifecycle state
