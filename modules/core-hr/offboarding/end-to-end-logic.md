# Offboarding — End-to-End Logic

**Module:** Core HR
**Feature:** Offboarding

---

## Start Offboarding

### Flow

```
POST /api/v1/employees/{id}/offboarding
  -> EmployeeController.StartOffboarding(id, StartOffboardingCommand)
    -> [RequirePermission("employees:write")]
    -> OffboardingService.StartAsync(employeeId, command, ct)
      -> 1. Load employee, validate status = 'active'
      -> 2. INSERT into offboarding_records
         -> reason, last_working_date, knowledge_risk_level
         -> status = 'initiated'
      -> 3. Create lifecycle event: event_type = 'terminated' or 'resigned'
      -> 4. Publish EmployeeOffboardingStarted event
         -> Consumers:
            -> leave: forfeit unused entitlements
            -> payroll: initiate final settlement
            -> agent-gateway: revoke agent access
            -> notifications: notify HR and manager
      -> 5. Calculate penalties_json (outstanding loans, notice period)
      -> Return Result.Success(offboardingDto)
```

## Complete Offboarding

### Flow

```
PUT /api/v1/offboarding/{id}/complete
  -> OffboardingController.Complete(id, CompleteOffboardingCommand)
    -> [RequirePermission("employees:write")]
    -> OffboardingService.CompleteAsync(id, command, ct)
      -> 1. Store exit_interview_notes
      -> 2. UPDATE employee: employment_status = 'terminated', termination_date
      -> 3. Deactivate user account: is_active = false
      -> 4. Revoke all sessions and refresh tokens
      -> 5. UPDATE offboarding_records: status = 'completed'
      -> 6. Publish EmployeeTerminated event
      -> Return Result.Success()
```

### Edge Cases

- **Knowledge risk assessment:** Critical employees trigger additional handover workflows.
- **Notice period tracking:** Tracked in penalties_json with expected end date.

## Related

- [[modules/core-hr/offboarding/overview|Offboarding Overview]]
- [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- [[modules/core-hr/employee-profiles/overview|Employee Profiles]]
- [[modules/core-hr/onboarding/overview|Onboarding]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
