# Employee Transfer

**Area:** Employee Management  
**Trigger:** Authorized employee-management user initiates a position, department, or legal entity transfer inside the tenant  
**Required Permission(s):** `employees:write`  
**Related Permissions:** `org:manage` (department/legal entity changes), `attendance:write` (schedule reassignment)

---

## Transfer Types

| Type | Meaning | Boundary |
|:-----|:--------|:---------|
| Same-legal-entity transfer | Position or department change inside the employee's current legal entity | Employee primary legal entity remains unchanged |
| Legal-entity transfer | Move from one legal entity to another legal entity inside the same tenant | Employee primary legal entity and position assignment change to the target legal entity |

Separate-tenant company connections are not part of Phase 1 employee transfer. Phase 1 multi-company support is handled through legal entities inside one tenant.

## Preconditions

- Employee is active -> [[Userflow/Employee-Management/profile-management|Profile Management]]
- Target legal entity exists when changing legal entity.
- Target position exists inside the selected legal entity and department -> [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- Team membership changes are handled separately through Org Structure > Teams; employee transfers do not directly move team membership.
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Transfer Flow

### Step 1: Initiate Transfer
- **UI:** Employee Profile -> Actions -> "Transfer" -> form opens
- **API:** `GET /api/v1/org/legal-entities`, `GET /api/v1/org/departments?legalEntityId={id}`, `GET /api/v1/org/positions?legalEntityId={id}`

### Step 2: Select Transfer Details
- **UI:** Select legal entity if changing company -> select department -> select new position -> set effective date -> enter reason.
- **Validation:** Effective date must be today or future. The selected position must be active, belong to the selected legal entity, and have available occupancy. The target position's reporting position must belong to the same legal entity. If the new position reports to a vacant unique position, transfer can proceed with a warning that reporting manager will be unresolved until staffed.

### Step 2b: Confirm Access Impact
- **UI:** Show access to add/remove based on old and new position-linked roles/permissions.
- **Rule:** Remove old position-linked access, add new position-linked access, and keep manual access only if admin confirms.

### Step 3: Submit Transfer
- **API:** `POST /api/v1/employees/{id}/transfer`
- **Backend:** EmployeeLifecycleService.TransferAsync() -> [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- **DB:** `employee_transfers` record created; `employees` updated on effective date

### Step 4: Approval (if configured)
- **Backend:** Workflow triggers if approval required -> [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
- Resolver-selected approvers may include the current department owner, new department owner, position-resolved reporting manager, team lead, users with a selected permission, HR coverage resolver, or configured escalation resolver. Multiple approvers use the workflow approval mode: only one required, all required, or approve in order.

### Step 5: Effective Date Processing
- **Backend:** On effective date:
  - Old `position_assignments` row closed and new row created
  - Employee primary legal entity updated when this is a legal-entity transfer
  - Department and job title profile snapshots updated from the new position where configured
  - Old `employee_assignment_history` row closed and new row created with the new `position_id`
  - Current `employee_hierarchy_closure` rebuilt for the affected branch if the transfer is effective today; future-dated transfers rebuild when they become effective
  - Shift schedule may need reassignment -> [[Userflow/Workforce-Presence/shift-schedule-setup|Shift Schedule Setup]]
  - Notifications sent to old and new position-resolved managers where resolved from the effective-date assignment and reporting history

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Same position | Validation fails | "Employee is already assigned to this position" |
| Pending transfer exists | Blocked | "Employee has a pending transfer - cancel first" |
| Target position belongs to another legal entity | Blocked | "Position does not belong to selected legal entity" |
| Reporting position belongs to another legal entity | Blocked | "Reporting position must be inside the same legal entity" |
| Position capacity exceeded | Blocked | "This position has reached its capacity" |

## Events Triggered

- `EmployeeTransferred` -> [[backend/messaging/event-catalog|Event Catalog]]
- Notification to position-resolved managers -> [[backend/notification-system|Notification System]]

## Related Flows

- [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- [[Userflow/Employee-Management/employee-promotion|Employee Promotion]]
- [[Userflow/Workforce-Presence/shift-schedule-setup|Shift Schedule Setup]]

## Module References

- [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- [[modules/org-structure/departments/overview|Departments]]
- [[modules/org-structure/teams/overview|Teams]]
