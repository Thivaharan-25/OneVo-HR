# Employee Lifecycle â€” End-to-End Logic

**Module:** Core HR
**Feature:** Employee Lifecycle

---

## Flow Overview

Employee Lifecycle tracks all significant employment events: hired, promoted, transferred, salary_change, suspended, terminated, and resigned. Each event creates an immutable audit record in `employee_lifecycle_events` and publishes a corresponding domain event consumed by notifications, leave, payroll, and agent-gateway modules.

---

## Step-by-Step Flow

### 0. Apply Approved Transfer On Effective Date

```
EmployeeTransferProcessor.ApplyDueTransfersAsync(today)
  -> Query employee_transfers
      WHERE status = "Approved"
      AND effective_date <= today
  -> For each transfer:
      - Validate employee is still active
      - Close current employee_assignment_history row by setting effective_to = effective_date - 1 day
      - Insert new employee_assignment_history row from transfer target values
      - Update employee current department/legal-entity snapshots from the new position
      - Set employee_transfers.status = "Applied"
      - Record transferred lifecycle event
      - Publish EmployeeTransferred
```

### 1. Record Lifecycle Event (Internal â€” triggered by other service actions)

```
IEmployeeLifecycleService.RecordEventAsync(employeeId, eventType, detailsJson, performedById)
  â†’ Validate: employee exists and is active
  â†’ Validate: eventType is a known enum value
  â†’ Build EmployeeLifecycleEvent entity
      - tenant_id from current tenant context
      - event_date = DateTime.UtcNow (or explicit date from caller)
      - details_json = serialized event-specific data
      - performed_by_id = user who initiated the action
  â†’ _dbContext.EmployeeLifecycleEvents.Add(event)
  â†’ _dbContext.SaveChangesAsync()
  â†’ Publish domain event based on event_type:
      - hired â†’ EmployeeCreated { EmployeeId, DepartmentId, HireDate }
      - promoted â†’ EmployeePromoted { EmployeeId, OldPositionId, NewPositionId, EffectiveDate }
      - transferred â†’ EmployeeTransferred { EmployeeId, OldDepartmentId, NewDepartmentId, OldPositionId, NewPositionId, EffectiveDate }
      - terminated/resigned â†’ EmployeeTerminated { EmployeeId, Reason, LastWorkingDate }
  â†’ Return LifecycleEventResponse
```

### 2. Query Lifecycle History

```
GET /api/v1/employees/{id}/lifecycle
  â†’ EmployeesController.GetLifecycle(id)
    â†’ IEmployeeLifecycleService.GetEventsAsync(employeeId, tenantId)
      â†’ Query employee_lifecycle_events
          WHERE employee_id = @employeeId
          AND tenant_id = @tenantId
          ORDER BY event_date DESC, created_at DESC
      â†’ Map to List<LifecycleEventResponse>
      â†’ Return 200 OK
```

### 3. Domain Event Consumers

```
EmployeeCreated â†’
  â”œâ”€ NotificationHandler: Send welcome notification to employee + position-resolved reporting manager when resolved
  â””â”€ LeaveHandler: Initialize annual leave balances (pro-rated if mid-year)

EmployeePromoted â†’
  â”œâ”€ NotificationHandler: Notify employee, old position-resolved manager, new position-resolved manager
  â””â”€ PayrollHandler: Trigger salary review workflow

EmployeeTransferred â†’
  â””â”€ NotificationHandler: Notify employee, old dept head, new dept head

EmployeeTerminated â†’
  â”œâ”€ LeaveHandler: Forfeit remaining leave balances
  â”œâ”€ PayrollHandler: Trigger final settlement calculation
  â””â”€ AgentGatewayHandler: Revoke all active agent sessions
```

---

## Sequence Diagram

```mermaid
sequenceDiagram
    participant Caller as EmployeeService / OffboardingService
    participant LCS as IEmployeeLifecycleService
    participant DB as PostgreSQL
    participant Bus as MediatR
    participant Notify as NotificationHandler
    participant Leave as LeaveHandler
    participant Payroll as PayrollHandler

    Caller->>LCS: RecordEventAsync(empId, "promoted", details)
    LCS->>DB: Validate employee exists
    LCS->>DB: INSERT INTO employee_lifecycle_events
    LCS->>Bus: Publish EmployeePromoted
    Bus->>Notify: Handle â†’ send promotion notification
    Bus->>Payroll: Handle â†’ trigger salary review
    LCS-->>Caller: LifecycleEventResponse
```

---

## Error Scenarios

| Step | Error | Handling |
|:-----|:------|:---------|
| Employee lookup | Employee not found or soft-deleted | Throw NotFoundException (404) |
| Invalid event_type | Unknown enum value | Throw ValidationException (400) |
| details_json | Invalid JSON structure for event type | Throw ValidationException (400) |
| DB write | Constraint violation | Transaction rolls back, return 500 |
| Event consumer failure | Notification service unavailable | Consumer logs error, does NOT block lifecycle record (fire-and-forget with retry) |

---

## Edge Cases

1. **Rapid successive events**: An employee promoted and transferred on the same day creates two separate lifecycle records with the same event_date. The `created_at` timestamp provides ordering within the same day.
2. **Terminated employee**: After termination, no further lifecycle events can be recorded. The service checks `employment_status` before accepting events.
3. **Back-dated events**: Events with explicit `event_date` in the past are allowed for HR corrections (e.g., recording a promotion that was effective last month). The `created_at` always reflects actual insertion time.
4. **details_json schema**: Each event type has its own expected JSON schema (e.g., promoted expects `old_position_id`, `new_position_id`). The service validates the JSON shape before persisting.

## Related

- [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle Overview]]
- [[modules/core-hr/employee-profiles/overview|Employee Profiles]]
- [[modules/core-hr/onboarding/overview|Onboarding]]
- [[modules/core-hr/offboarding/overview|Offboarding]]
- [[modules/core-hr/compensation/overview|Compensation]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]

