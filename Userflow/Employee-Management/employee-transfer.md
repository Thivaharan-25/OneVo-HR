# Employee Transfer

**Area:** Employee Management  
**Trigger:** Authorized employee-management user initiates a position, department, or legal entity transfer inside the tenant  
**Required Permission(s):** `employees:write`  
**Related Permissions:** `org:manage` (department/legal entity changes), `attendance:write` (schedule reassignment), `roles:manage` or `access:approve` (view/change generated access)

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

### Step 2b: Resolve Access Impact
- **Backend:** Compare old position-template grants with the target position's access templates.
- Old grants sourced from the old position are scheduled to end on the transfer effective date.
- New grants sourced from the target position are generated using the target position's templates.
- Manual user roles and employee overrides are not removed unless an authorized access user explicitly changes them.

### Step 2c: Access UI Rules
- If the actor has `roles:manage` or `access:approve`, show the generated access diff and allow confirm/change/remove within the actor's authority.
- If the actor does not have `roles:manage` or `access:approve`, do not show role lists, permission details, scope controls, or access-template details. The UI may show only: "Access changes require approval."
- If the target position is pooled and an authorized actor changes generated access, the UI must force a choice:
  - Apply to the position template, affecting all current and future occupants.
  - Apply only to this employee, creating an employee-specific grant or override.

### Step 3: Submit Transfer
- **API:** `POST /api/v1/employees/{id}/transfer`
- **Backend:** EmployeeLifecycleService.TransferAsync() -> [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- **DB:** `employee_transfers` record created; `employees` updated on effective date

### Step 4: Access Approval (if required)
- **Rule:** If a generated position access template has `requires_approval = true` and the actor does not have `roles:manage` or `access:approve`, create an access approval request. The transfer can continue, but the sensitive grant remains pending.
- **Target department:** Approval routing uses the target position's department, not the actor's department.
- **Approver resolver:**
  1. Find users with `roles:manage` or `access:approve` whose own access scope covers the target department.
  2. If none exist, find tenant-wide users with `roles:manage` or `access:approve`.
  3. If none exist, route to Tenant Admin.
  4. If multiple users match a step, notify all; first approval wins.
- **Approver view:** Show employee, requested transfer, target position, target department, role grant, permission effect, scope, effective dates, requester, and source template.
- If the actor already has `roles:manage` or `access:approve`, no approval request is needed; generated access can be materialized immediately or scheduled for the effective date after confirmation.

### Step 5: Effective Date Processing
- **Backend:** On effective date:
  - Old `position_assignments` row closed and new row created
  - Employee primary legal entity updated when this is a legal-entity transfer
  - Department and legal-entity profile snapshots updated from the new position
  - Old `employee_assignment_history` row closed and new row created with the new `position_id`
  - Old position-template `user_roles` grants end
  - Approved new position-template `user_roles` grants activate; pending sensitive grants remain inactive until approved
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
| Access approval pending | Transfer proceeds; sensitive grant inactive | "Access changes are pending approval" |

## Events Triggered

- `EmployeeTransferred` -> [[backend/messaging/event-catalog|Event Catalog]]
- `AccessGrantRequested` -> emitted when sensitive generated access requires approval
- `UserRoleScheduled` -> emitted when generated access is approved or does not require approval
- Notification to position-resolved managers -> [[backend/notification-system|Notification System]]

## Related Flows

- [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- [[Userflow/Employee-Management/employee-promotion|Employee Promotion]]
- [[Userflow/Workforce-Presence/shift-schedule-setup|Shift Schedule Setup]]
- [[Userflow/Auth-Access/access-policy|Access Policy Reference]]

## Module References

- [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- [[modules/org-structure/departments/overview|Departments]]
- [[modules/org-structure/teams/overview|Teams]]
