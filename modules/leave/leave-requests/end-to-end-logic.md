# Leave Requests — End-to-End Logic

**Module:** Leave  
**Feature:** Leave Requests

---

## Submit Leave Request

### Flow

```
POST /api/v1/leave/requests
  -> LeaveRequestController.Submit(CreateLeaveRequestCommand)
    -> [RequirePermission("leave:create")]
    -> FluentValidation: leave_type_id required, start <= end, start >= today
    -> LeaveRequestService.SubmitRequestAsync(command, ct)
      -> 1. Validate leave type exists and is active
      -> 2. Get employee from ICurrentUser
      -> 3. Calculate total_days (exclude weekends/holidays)
      -> 4. Check entitlement: remaining_days >= total_days
      -> 5. Check overlapping requests for same employee
      -> 6. Check max consecutive days if configured
      -> 7. Calendar conflict detection (warnings only, stored as snapshot)
      -> 8. Create LeaveRequest entity (status = "pending")
      -> 9. Persist to database
      -> 10. Create workflow instance for approval routing
      -> 11. Publish LeaveRequested domain event
      -> Return Result<LeaveRequestDto> with conflict_snapshot
    -> 201 Created
```

## Approve Leave Request

### Flow

```
PUT /api/v1/leave/requests/{id}/approve
  -> [RequirePermission("leave:approve")]
  -> LeaveRequestService.ApproveAsync(requestId, ct)
    -> 1. Load request, verify status = "pending"
    -> 2. Re-check calendar conflicts (live)
    -> 3. Update status = "approved", approved_by, approved_at
    -> 4. Update entitlements: used_days += total_days
    -> 5. Create leave_balances_audit (change_type = "deduction")
    -> 6. Complete workflow instance
    -> 7. Publish LeaveApproved event
    -> Return Result<LeaveRequestDto>
```

## Cancel Leave Request

### Flow

```
LeaveRequestService.CancelAsync(requestId, ct)
  -> 1. Load request, verify status in (pending, approved)
  -> 2. If was approved: reverse entitlement deduction
  -> 3. Create audit record (change_type = "adjustment")
  -> 4. Update status = "cancelled"
  -> 5. Publish LeaveCancelled event
```

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Insufficient balance | 422 | "Insufficient leave balance" |
| Overlapping request | 409 | "Overlapping leave request exists" |
| Exceeds max consecutive | 422 | "Exceeds maximum consecutive days" |
| Already processed | 409 | "Request already processed" |
| Past start date | 422 | "Cannot request leave in the past" |

### Edge Cases

- Cross-year requests: split entitlement across both years
- Half days: total_days can be 0.5
- Conflicts stored at submission, re-checked at approval

## Related

- [[leave-requests|Leave Requests Overview]]
- [[leave-entitlements]]
- [[balance-audit]]
- [[leave-policies]]
- [[event-catalog]]
- [[error-handling]]
