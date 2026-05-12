# Employee Transfer

**Area:** Employee Management  
**Trigger:** HR Admin initiates within-company department/team transfer, or starts a cross-company transfer to a connected company  
**Required Permission(s):** `employees:write`; cross-company transfer also requires `cross-company:employees:transfer`  
**Related Permissions:** `org:manage` (cross-department), `attendance:write` (schedule reassignment), `company-connections:read`

---

## Transfer Types

| Type | Meaning | Boundary |
|:-----|:--------|:---------|
| Within-company transfer | Department, team, reporting manager, location, or cost center change inside the current tenant | Employee record remains in the same tenant |
| Cross-company transfer | Controlled move or secondment from source tenant to target connected tenant | Source tenant keeps history; target tenant creates or activates its own employee record |

Cross-company transfer must not be modeled as moving an employee between legal entities inside one tenant.

## Preconditions

- Employee is active -> [[Userflow/Employee-Management/profile-management|Profile Management]]
- Target department/team exists for within-company transfer -> [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]
- Cross-company transfer additionally requires an active [[modules/shared-platform/company-connections/overview|Company Connection]], target acceptance permission/scope, and configured workflow approval where applicable.

## Within-Company Flow

### Step 1: Initiate Transfer
- **UI:** Employee Profile -> Actions -> "Transfer" -> form opens
- **API:** `GET /api/v1/org/departments` + `GET /api/v1/org/teams`

### Step 2: Select Transfer Details
- **UI:** Select new department -> select new team -> select new reporting manager -> set new location (if applicable) -> set effective date -> enter reason
- **Validation:** Effective date must be today or future

### Step 3: Submit Transfer
- **API:** `POST /api/v1/employees/{id}/transfer`
- **Backend:** EmployeeLifecycleService.TransferAsync() -> [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- **DB:** `employee_transfers` record created; `employees` updated on effective date

### Step 4: Approval (if configured)
- **Backend:** Workflow triggers if approval required -> [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
- Resolver-selected approvers may include the current department owner, new department owner, reporting manager, team lead, users with a selected permission, or configured escalation owner. Multiple approvers use the workflow approval mode: only one required, all required, or approve in order.

### Step 5: Effective Date Processing
- **Backend:** On effective date:
  - Department/team updated
  - Reporting line changed
  - Shift schedule may need reassignment -> [[Userflow/Workforce-Presence/shift-schedule-setup|Shift Schedule Setup]]
  - Cost center allocation updated
  - Notifications sent to old and new managers

## Cross-Company Transfer Flow

### Step 1: Select Target Company
- **UI:** Employee Profile -> Actions -> "Transfer to connected company"
- **API:** `GET /api/v1/company-connections`
- **Validation:** Target company must be an active connected tenant included in the caller's grant scope.

### Step 2: Start Transfer Workflow
- **API:** `POST /api/v1/employees/{id}/cross-company-transfer`
- **Backend:** Workflow Engine creates a cross-company transfer case with source tenant, target tenant, subject employee, connection ID, allowed evidence package, requester, and audit context.

### Step 3: Source Approval And Target Acceptance
- Source tenant approver confirms release/secondment details.
- Target tenant approver confirms acceptance, role, department/team, start date, and onboarding tasks.
- Workflow rules decide whether approvals are sequential, all-required, or only-one-required.

### Step 4: Finalize
- Source tenant keeps historical employment, payroll, attendance, monitoring, documents, and lifecycle records.
- Target tenant creates or activates its own employee record.
- Only explicitly approved transfer evidence is shared with the target tenant.
- Payroll, leave balances, documents, device assignments, monitoring history, and user permissions do not move automatically.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Same department | Validation fails | "Employee is already in this department" |
| Pending transfer exists | Blocked | "Employee has a pending transfer - cancel first" |
| No active company connection | Blocked | "Target company is not connected" |
| Missing cross-company scope | Blocked | "You do not have permission to transfer to this company" |

## Events Triggered

- `EmployeeTransferred` -> [[backend/messaging/event-catalog|Event Catalog]]
- `CrossCompanyTransferRequested`
- `CrossCompanyTransferAccepted`
- Notification to managers -> [[backend/notification-system|Notification System]]

## Related Flows

- [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- [[Userflow/Employee-Management/employee-promotion|Employee Promotion]]
- [[Userflow/Workforce-Presence/shift-schedule-setup|Shift Schedule Setup]]

## Module References

- [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- [[modules/org-structure/departments/overview|Departments]]
- [[modules/org-structure/teams/overview|Teams]]
- [[modules/shared-platform/company-connections/overview|Company Connections]]
