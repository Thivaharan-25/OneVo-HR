# Employee Offboarding

**Area:** Employee Management  
**Required Permission(s):** `employees:write`  
**Related Permissions:** `payroll:write` (final pay), `documents:manage` (exit documents)

---

## Preconditions

- Employee is active → [[profile-management]]
- Offboarding workflow template exists → [[workflow-engine]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Initiate Offboarding
- **UI:** Employee Profile → Actions → "Offboard" → form opens
- **API:** `GET /api/v1/employees/{id}`

### Step 2: Set Offboarding Details
- **UI:** Set last working day → select reason (resignation, termination, retirement, contract end, redundancy) → enter notes → set if eligible for rehire
- **Validation:** Last working day must be today or future (unless backdated with admin override)

### Step 3: Submit
- **API:** `POST /api/v1/employees/{id}/offboard`
- **Backend:** EmployeeLifecycleService.OffboardAsync() → [[employee-lifecycle]]
- **DB:** `employees.status` → "Offboarding", `employee_offboarding` — record created

### Step 4: Offboarding Checklist Triggered
- **Backend:** Workflow creates checklist → [[offboarding]]
- **Checklist items:**
  - IT: Revoke system access, collect laptop/devices
  - HR: Conduct exit interview, process final documents
  - Finance: Calculate final pay (remaining salary + unused leave payout + pending expenses)
  - Manager: Knowledge transfer, reassign tasks
  - Admin: Return badge/keys, update org chart

### Step 5: Process Each Checklist Item
- **UI:** Assigned persons complete their items → tick off → progress tracked
- **API:** `PUT /api/v1/workflows/{id}/steps/{stepId}/complete`

### Step 6: Final Day Processing
- **Backend:** On last working day (automated via Hangfire):
  - Status → "Inactive"
  - All sessions terminated → [[session-management]]
  - Desktop agent unregistered → [[agent-registration]]
  - Notifications stopped
  - Profile read-only (data retained per policy) → [[retention-policy-setup]]
  - Leave balance snapshot taken for records
  - Final payroll adjustment created → [[payroll-adjustment]]

## Variations

### Immediate termination
- Last working day = today → all steps triggered immediately
- System access revoked instantly

### When employee has pending approvals
- Pending leave/expense approvals reassigned to manager
- Pending performance reviews delegated

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Already offboarding | Blocked | "Offboarding already in progress" |
| Active payroll run | Warning | "Employee included in current payroll run — process separately" |

## Events Triggered

- `EmployeeOffboardingStarted` → [[event-catalog]]
- `EmployeeDeactivated` → [[event-catalog]]
- Notifications to checklist assignees → [[notification-system]]

## Related Flows

- [[employee-onboarding]] — reverse flow
- [[payroll-adjustment]] — final pay
- [[disciplinary-action]] — may trigger offboarding

## Module References

- [[employee-lifecycle]]
- [[offboarding]]
- [[workflow-engine]]
- [[session-management]]
- [[agent-registration]]
