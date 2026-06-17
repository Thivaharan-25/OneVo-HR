# Employee Promotion

**Area:** Employee Management  
**Trigger:** Authorized employee-management user initiates promotion (user action)  
**Required Permission(s):** `employees:write`  
**Related Permissions:** `payroll:write` (salary revision), `roles:manage` or `access:approve` (view/change generated access)

---

## Preconditions

- Employee is active -> [[Userflow/Employee-Management/profile-management|Profile Management]]
- Target position exists -> [[Userflow/Org-Structure/position-setup|Position Setup]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Initiate Promotion
- **UI:** Employee Profile -> Actions -> "Promote" -> form opens

### Step 2: Set New Level / Position
- **UI:** Select new job family level (for example, Mid -> Senior) -> new title auto-filled from level -> override title if needed.
- If the promotion changes position, select the target position and resolve its target department.
- **Backend:** Position access templates are evaluated only when the promotion places the employee into a new position or changes the active position assignment. Position access templates do not become active grants until confirmed or approved.

### Step 3: Salary Revision
- **UI:** Current salary shown -> enter new salary -> system shows salary band for new level -> enter effective date
- **Validation:** Warning if salary outside new level's band

### Step 4: Access Review / Approval
- **If actor has `roles:manage` or `access:approve`:** Show generated position access grants. Actor can confirm, reject, replace, or narrow them within authority.
- **If actor lacks `roles:manage` and `access:approve`:** Do not show role lists, permission details, scope controls, or access-template details. The UI may show only: "Access changes require approval."
- **Key:** Permissions do not change automatically because of the promotion label. Position-template access only becomes active after confirmation or approval.
- **Approval routing:** If a generated position access template requires approval and the actor lacks access authority, route the access approval by the target position's department:
  1. users with `roles:manage` or `access:approve` whose scope covers the target department;
  2. tenant-wide `roles:manage` or `access:approve`;
  3. Tenant Admin.
- If multiple approvers match, notify all; first approval wins.
- For pooled target positions, an authorized actor changing access must choose whether the change applies to the position template for all occupants or only to this employee as an override.

### Step 5: Submit
- **API:** `POST /api/v1/employees/{id}/promote`
- **Backend:** EmployeeLifecycleService.PromoteAsync() -> [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- **DB:** `employees` - title/level updated, `employee_compensation` - new salary record, confirmed or approved access grants stored in `user_roles`; pending access stored in `access_grant_requests`

### Step 6: Effective Date Processing
- On effective date: confirmed or approved changes become active; pending sensitive access remains inactive until approved. Employee visibility changes only from active `user_roles`, employee overrides, and memberships.

## Variations

### When user also has `roles:manage`
- Can assign a confirmed role instead of the job family suggestion
- Can add additional confirmed permissions within entitlement boundaries
- No access approval request is needed, but all role/scope decisions are audited.

### Promotion without position change
- Compensation may change. Position changes are handled through the target position assignment.
- Position-template access is not regenerated unless the active position changes or an authorized user explicitly changes access.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Same level | Validation fails | "Select a different level for promotion" |
| Lower level | Warning | "This is a demotion - proceed?" |
| No salary change | Warning | "Consider adjusting salary for new level" |
| Access approval pending | Promotion proceeds; sensitive grant inactive | "Access changes are pending approval" |

## Events Triggered

- `EmployeePromoted` -> [[backend/messaging/event-catalog|Event Catalog]]
- `RoleChanged` -> emitted only when a role change was explicitly confirmed or approved
- `AccessGrantRequested` -> emitted when generated sensitive access needs approval
- `CompensationUpdated` -> [[backend/messaging/event-catalog|Event Catalog]]
- Notification to employee -> [[backend/notification-system|Notification System]]

## Related Flows

- [[Userflow/Org-Structure/position-setup|Position Setup]] - defines reporting, capacity, and position access templates
- [[Userflow/Employee-Management/compensation-setup|Compensation Setup]] - salary details
- [[Userflow/Auth-Access/permission-assignment|Permission Assignment]] - permissions change only from confirmed or approved assignments
- [[Userflow/Auth-Access/access-policy|Access Policy Reference]]
- [[Userflow/Employee-Management/employee-transfer|Employee Transfer]] - may accompany promotion

## Module References

- [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- [[modules/core-hr/compensation/overview|Compensation]]
- [[frontend/cross-cutting/authorization|Authorization]]
