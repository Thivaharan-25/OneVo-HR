# Employee Offboarding

**Area:** Employee Management  
**Trigger:** Authorized employee-management user initiates offboarding (user action)
**Required Permission(s):** `employees:write`  
**Related Permissions:** `payroll:write` (final pay), `documents:manage` (exit documents)

---

## Preconditions

- Employee is active -> [[Userflow/Employee-Management/profile-management|Profile Management]]
- Phase 1 Checklist Templates exist for offboarding tasks. Workflow Engine offboarding templates are Phase 2.
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Initiate Offboarding
- **UI:** Employee Profile -> Actions -> "Offboard" -> form opens
- **API:** `GET /api/v1/employees/{id}`

### Step 2: Set Offboarding Details
- **UI:** Set last working day -> select reason (resignation, termination, retirement, contract end, redundancy) -> enter notes -> set if eligible for rehire
- **Validation:** Last working day must be today or future (unless backdated with admin override)

### Step 3: Submit
- **API:** `POST /api/v1/employees/{id}/offboard`
- **Backend:** EmployeeLifecycleService.OffboardAsync() -> [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- **DB:** `employees.employment_status` -> `offboarding`, `offboarding_records` record created

### Step 4: Offboarding Checklist Triggered
- **Backend:** Phase 1 offboarding service creates `employee_checklist_tasks` from `checklist_templates` -> [[modules/core-hr/offboarding/overview|Offboarding]]
- **Checklist items:**
  - IT: Revoke system access, collect laptop/devices
  - HR: Conduct exit interview, process final documents
  - Finance: Calculate final pay (remaining salary + unused time off payout + pending expenses)
  - Manager: Knowledge transfer, reassign tasks
  - Admin: Return badge/keys, update org chart

### Step 4A: Knowledge Transfer and Handover
- **UI:** Offboarding detail -> Knowledge Transfer section
- **Assignee:** Configured offboarding resolver by default; authorized employee-management or asset-management users can review
- **Required when:** `knowledge_risk_level = high` or `critical`
- **Manager actions:**
  - Record handover notes
  - Confirm business-critical responsibilities transferred
  - Reassign tasks/projects
  - Attach or reference handover documents where available
  - Mark knowledge transfer complete
- **API:** `PUT /api/v1/offboarding/{id}/knowledge-transfer`
- **Backend:** OffboardingService.UpdateKnowledgeTransferAsync()
- **Validation:** High/critical risk offboarding cannot complete until knowledge transfer is completed or bypassed with approval

### Step 4B: Bypass Knowledge Transfer
- **UI:** Knowledge Transfer section -> "Bypass" action
- **Allowed for:** User with the required offboarding permission and valid management coverage for the employee
- **Required fields:**
  - Bypass reason
  - Penalty amount (optional)
  - Currency (required when amount > 0)
- **API:** `POST /api/v1/offboarding/{id}/knowledge-transfer/bypass`
- **Backend:** OffboardingService.BypassKnowledgeTransferAsync()
- **DB:** Append penalty/audit item into `offboarding_records.penalties_json`
- **Penalty behaviour:**
  - If tenant policy has a default knowledge-transfer bypass penalty, use it when no manual amount is entered
  - If manual amount is entered, store the manual amount
  - If no penalty applies, store `amount = 0` as audit-only bypass
- **Result:** Knowledge transfer checklist item is marked `bypassed`; final offboarding can continue

### Step 5: Process Each Checklist Item
- **UI:** Assigned persons complete their items -> tick off -> progress tracked
- **API:** `PUT /api/v1/offboarding/{id}/checklist/{itemId}/complete`

### Step 6: Final Day Processing
- **Backend:** On last working day (automated via Hangfire):
  - `employment_status` -> `terminated` or `resigned`
  - All sessions terminated -> [[modules/auth/session-management/overview|Session Management]]
  - Desktop agent unregistered -> [[modules/agent-gateway/agent-registration/overview|Agent Registration]]
  - Notifications stopped
  - Profile read-only (data retained per policy) -> [[Userflow/Configuration/retention-policy-setup|Retention Policy Setup]]
  - Time off balance snapshot taken for records
  - Final payroll adjustment created -> [[Userflow/Payroll/payroll-adjustment|Payroll Adjustment]]

### Step 6A: Final Settlement Penalty Review
- **Backend:** Before final settlement review, read `offboarding_records.penalties_json`
- **Includes:** outstanding loans, notice-period violations, asset recovery, and knowledge-transfer bypass penalties
- **Phase 1 behavior:** Record and expose the settlement input for review
- **Phase 2 behavior:** Payroll can consume the finalized penalty items during payroll adjustment/final pay

## Variations

### Immediate termination
- Last working day = today -> all steps triggered immediately
- System access revoked instantly

### When employee has pending approvals
- Pending time off/expense approvals are reassigned to the next eligible coverage owner. If no eligible owner exists, create a routing issue.
- Pending performance reviews are delegated to the configured reviewer or next eligible coverage owner.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Already offboarding | Blocked | "Offboarding already in progress" |
| Active payroll run | Warning | "Employee included in current payroll run - process separately" |

Additional error scenarios for knowledge transfer:

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| High/critical knowledge transfer incomplete | Blocked | "Knowledge transfer must be completed or bypassed with approval" |
| Bypass requested without reason | Blocked | "Bypass reason is required" |
| Penalty amount entered without currency | Blocked | "Currency is required for penalty amount" |

## Events Triggered

- `EmployeeOffboardingStarted` -> [[backend/messaging/event-catalog|Event Catalog]]
- `EmployeeDeactivated` -> [[backend/messaging/event-catalog|Event Catalog]]
- Notifications to checklist assignees -> [[backend/notification-system|Notification System]]

## Related Flows

- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]] - reverse flow
- [[Userflow/Payroll/payroll-adjustment|Payroll Adjustment]] - final pay
- [[Userflow/Grievance/disciplinary-action|Disciplinary Action]] - may trigger offboarding

## Module References

- [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- [[modules/core-hr/offboarding/overview|Offboarding]]
- [[modules/core-hr/offboarding/overview|Offboarding]]
- [[modules/auth/session-management/overview|Session Management]]
- [[modules/agent-gateway/agent-registration/overview|Agent Registration]]
