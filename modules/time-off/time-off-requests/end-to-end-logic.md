# Time Off Requests - End-to-End Logic

**Module:** Time Off
**Feature:** Time Off Requests

---

## Submit Time Off Request

### Flow

```
POST /api/v1/time-off/requests
  -> TimeOffRequestController.Submit(CreateTimeOffRequestCommand)
    -> [RequirePermission("time_off:create")]
    -> FluentValidation:
       time_off_type_id required
       start_date, end_date required, start <= end
       request_duration_minutes required, must be positive
       start >= today unless backdated request is explicitly allowed
    -> TimeOffRequestService.SubmitRequestAsync(command, ct)
      -> 1. Validate time off type exists and is active
      -> 2. Get employee from ICurrentUser
      -> 3. Resolve active time off policy for employee, time off type, and request dates
      -> 4. Validate request_duration_minutes:
           -> user enters duration in hours/minutes or selects start/end date and time
           -> system converts the requested duration to request_duration_minutes
           -> shift schedules are NOT used to calculate request duration
      -> 6. Check entitlement: available_minutes >= request_duration_minutes unless over-balance/unpaid behavior allows it
      -> 7. Check overlapping requests for same employee
      -> 8. Check max_consecutive_minutes if configured
      -> 9. Calendar conflict detection (warnings only, stored as snapshot)
      -> 10. Create TimeOffRequest entity (status = "pending", request_duration_minutes captured)
      -> 11. Persist to database
      -> 12. Resolve one Phase 1 approval owner from management coverage and required permission
      -> 13. Create a module-owned approval/action record and Notification/Inbox action for the assigned owner, or create a routing issue if none is valid
      -> 14. Publish TimeOffRequested domain event
      -> Return Result<TimeOffRequestDto> with conflict_snapshot
    -> 201 Created
```

Time Off request duration is entered directly by the user in hours/minutes or derived from the selected date/time range. Shift schedules are used for attendance expectations, calendar display, and availability context — they do not calculate Time Off request duration in Phase 1.

## Approve Time Off Request

### Flow

```
PUT /api/v1/time-off/requests/{id}/approve
  -> [RequirePermission("time_off:approve")]
  -> TimeOffRequestService.ApproveAsync(requestId, ct)
    -> 1. Load request, verify status = "pending"
    -> 2. Re-check calendar conflicts and policy validity
    -> 3. Revalidate the captured request_duration_minutes against current policy/balance rules
    -> 4. Set deduction_minutes = approved request duration minutes
    -> 5. Update status = "approved", approved_by, approved_at
    -> 6. Update entitlement: used_minutes += deduction_minutes
    -> 7. Create time_off_balances_audit (change_type = "deduction", minutes_changed = -deduction_minutes, source = "time_off")
    -> 8. Mark the module-owned approval/action record as approved
    -> 9. Publish TimeOffApproved event
    -> Return Result<TimeOffRequestDto>
```

## Cancel Time Off Request

### Flow

```
TimeOffRequestService.CancelAsync(requestId, ct)
  -> 1. Load request, verify status in (pending, approved)
  -> 2. If was approved: reverse entitlement deduction
       -> used_minutes -= deduction_minutes
  -> 3. Create audit record (change_type = "adjustment", minutes_changed = +deduction_minutes, source = "time_off")
  -> 4. Update status = "cancelled"
  -> 5. Publish TimeOffCancelled event
```

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Insufficient balance | 422 | `INSUFFICIENT_TIME_OFF_BALANCE` |
| Invalid duration | 422 | `INVALID_REQUEST_DURATION` |
| Overlapping request | 409 | `OVERLAPPING_TIME_OFF_REQUEST` |
| Exceeds maximum consecutive amount | 422 | `EXCEEDS_MAX_CONSECUTIVE_MINUTES` |
| Already processed | 409 | `REQUEST_ALREADY_PROCESSED` |
| Past start date | 422 | `PAST_TIME_OFF_REQUEST_NOT_ALLOWED` |

### Edge Cases

- Cross-period requests: split deduction across each entitlement period.
- All requests store `request_duration_minutes` directly; no schedule-based duration calculation.
- Start/end time is optional context; canonical duration is always `request_duration_minutes`.
- After approval, store deduction_minutes as the historical deduction. Later schedule changes do not automatically recalculate approved/taken Time Off.
- Overlapping schedules: resolve by assignment priority or block until corrected.
- Conflicts stored at submission are re-checked at approval.
- Phase 1 approval routing does not create or complete Workflow Engine instances. Workflow/Automation Engine approval routing is Phase 2 only.

## Related

- [[modules/time-off/time-off-requests/overview|Time Off Requests Overview]]
- [[modules/time-off/time-off-entitlements/overview|Time Off Entitlements]]
- [[modules/time-off/balance-audit/overview|Balance Audit]]
- [[modules/time-off/time-off-policies/overview|Time Off Policies]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
