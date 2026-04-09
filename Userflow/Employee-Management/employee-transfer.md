# Employee Transfer

**Area:** Employee Management  
**Required Permission(s):** `employees:write`  
**Related Permissions:** `org:manage` (cross-department), `attendance:write` (schedule reassignment)

---

## Preconditions

- Employee is active → [[Userflow/Employee-Management/profile-management|Profile Management]]
- Target department/team exists → [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Initiate Transfer
- **UI:** Employee Profile → Actions → "Transfer" → form opens
- **API:** `GET /api/v1/org/departments` + `GET /api/v1/org/teams`

### Step 2: Select Transfer Details
- **UI:** Select new department → select new team → select new reporting manager → set new location (if applicable) → set effective date → enter reason
- **Validation:** Effective date must be today or future

### Step 3: Submit Transfer
- **API:** `POST /api/v1/employees/{id}/transfer`
- **Backend:** EmployeeLifecycleService.TransferAsync() → [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- **DB:** `employee_transfers` — record created, `employees` — updated on effective date

### Step 4: Approval (if configured)
- **Backend:** Workflow triggers if approval required → [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
- Both current and new department heads may need to approve

### Step 5: Effective Date Processing
- **Backend:** On effective date:
  - Department/team updated
  - Reporting line changed
  - Shift schedule may need reassignment → [[Userflow/Workforce-Presence/shift-schedule-setup|Shift Schedule Setup]]
  - Cost center allocation updated
  - Notifications sent to old and new managers

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Same department | Validation fails | "Employee is already in this department" |
| Pending transfer exists | Blocked | "Employee has a pending transfer — cancel first" |

## Events Triggered

- `EmployeeTransferred` → [[backend/messaging/event-catalog|Event Catalog]]
- Notification to managers → [[backend/notification-system|Notification System]]

## Related Flows

- [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- [[Userflow/Employee-Management/employee-promotion|Employee Promotion]]
- [[Userflow/Workforce-Presence/shift-schedule-setup|Shift Schedule Setup]]

## Module References

- [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- [[modules/org-structure/departments/overview|Departments]]
- [[modules/org-structure/teams/overview|Teams]]
