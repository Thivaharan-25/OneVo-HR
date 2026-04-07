# Presence Sessions — End-to-End Logic

**Module:** Workforce Presence
**Feature:** Presence Sessions (Unified)

---

## Reconcile Presence Data

### Flow

```
ReconcilePresenceSessions (Hangfire, every 5 min during work hours)
  -> PresenceReconciliationService.ReconcileAsync(tenantId, date, ct)
    -> 1. Get all employees with any presence source data today
    -> 2. For each employee:
       -> a. Get biometric events: attendance_records for today
          -> first clock_in = biometric_first_seen
          -> last clock_out = biometric_last_seen
       -> b. Get agent data: device_sessions for today
          -> first session_start = agent_first_seen
          -> last session_end = agent_last_seen
       -> c. Get manual corrections: attendance_corrections for today
       -> d. Determine unified presence:
          -> first_seen_at = MIN(biometric_first_seen, agent_first_seen)
          -> last_seen_at = MAX(biometric_last_seen, agent_last_seen)
          -> source = determine primary source (biometric/agent/mixed)
       -> e. Calculate total_present_minutes (subtract breaks)
       -> f. UPSERT into presence_sessions
          -> ON CONFLICT (tenant_id, employee_id, date) DO UPDATE
    -> 3. Determine status:
       -> 'present': has presence data
       -> 'absent': no data and not on leave
       -> 'on_leave': ILeaveService confirms approved leave
       -> 'partial': present but less than scheduled hours
```

## Get Live Workforce Status

### Flow

```
GET /api/v1/workforce/presence/live
  -> WorkforcePresenceController.GetLive()
    -> [RequirePermission("workforce:view")]
    -> WorkforcePresenceService.GetLiveWorkforceStatusAsync(ct)
      -> 1. Query today's presence_sessions
      -> 2. Query active device_sessions (session_end IS NULL)
      -> 3. Build live dashboard data:
         -> Total employees, currently active, idle, on break, absent
      -> Return Result.Success(liveStatusDto)
```

## Related

- [[presence-sessions|Presence Sessions Overview]]
- [[device-sessions]]
- [[break-tracking]]
- [[attendance-corrections]]
- [[shifts-schedules]]
- [[event-catalog]]
- [[error-handling]]
