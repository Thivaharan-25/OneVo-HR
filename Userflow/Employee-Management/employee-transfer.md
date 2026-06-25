# Employee Transfer

**Area:** Employee Management  
**Trigger:** Authorized user transfers an employee to a new department, position, or legal entity  
**Required Permission(s):** `employees:write` to start a transfer; `position:approve` with valid coverage to approve/apply a position-changing transfer

---

## Phase 1 Source of Truth

Transfer is a compact operational modal or compact flow. It is not a five-step wizard and it does not use Workflow Engine in Phase 1.

Transfer approvals use management coverage, `position:approve`, and lightweight approval requests/notifications.

---

## Modal Fields

| Field | Required | Notes |
|:---|:---|:---|
| Target legal entity | Conditional | Required only for legal-entity transfer |
| Target department | Yes | Filtered by target legal entity |
| Target position | Yes | Must belong to target department/legal entity and have capacity |
| Effective date | Yes | Today or future |
| Reason | Yes | Audit and approver context |

Do not expose generic technical scope selectors.

---

## Access Impact

When target position is selected, load a read-only access summary:

- Role granted from target position
- Can manage employees in
- Requires approval

If the target position does not grant system access, no access section is shown.

If direct apply is allowed and the target position does not require approval, the actor may apply directly. If the actor lacks valid authority or the target position requires approval, create an approval request and resolve one owner through management coverage.

Do not use role-name bypasses. Direct apply depends on held permissions and authority grants, not labels such as CEO or HR Manager.

Approval routing:

1. Position coverage owners in order: Primary owner, Backup owner 1, Backup owner 2, etc.
2. Department coverage owners in the same order.
3. Company-wide coverage owners in the same order.
4. Routing issue.

If no valid owner exists, create a routing issue with: "No eligible owner could approve this request. Check position coverage and permissions."

---

## Primary vs Authority Assignment

If transfer changes the employee's Primary Employment Assignment:

- Close the old primary assignment.
- Create the new primary assignment.
- Re-evaluate primary legal entity, time off policy, attendance policy, work schedule, holiday calendar, and payroll/statutory context from the new primary assignment.
- Keep additional authority assignments only when business rules allow.

If transfer adds only an Additional Authority Assignment:

- Do not recalculate Time Off, schedule, attendance, payroll, holiday calendar, or primary legal entity.
- Apply only the granted role/access/approval authority from that assignment.

Hard rules:

- One employee cannot hold two active employment assignments inside the same legal entity.
- Cross-legal-entity authority assignments are allowed.
- Cross-legal-entity reporting lines are not allowed.

---

## Backend Flow

1. Validate employee is active.
2. Validate target legal entity, department, and position.
3. Validate target position capacity and same-legal-entity reporting chain.
4. Resolve access impact from target position.
5. If direct apply is allowed, create/schedule the new assignment and active role grant.
6. If approval is required, create an approval request and notify the single eligible owner resolved from management coverage.
7. On effective date, close/open `position_assignments`, update assignment history, and rebuild hierarchy closure for affected branches.

---

## Error Scenarios

| Scenario | User sees |
|:---|:---|
| Same position selected | "Employee is already assigned to this position." |
| Target position has no capacity | "This position has reached its capacity." |
| Target department belongs to another legal entity | "Department does not belong to the selected Company." |
| Reporting line crosses legal entity | "Reporting line must stay inside one Company." |
| Second active employment assignment in same legal entity | "Use transfer or promotion for another seat in the same Company." |
| Access requires approval | "Access changes are pending approval." |

---

## Events Triggered

- `EmployeeTransferRequested`
- `EmployeeTransferred`
- `AccessGrantRequested`
- Notification to the single owner resolved from management coverage

---

## Related

- [[Userflow/Org-Structure/position-setup|Position Setup]]
- [[Userflow/Employee-Management/employee-promotion|Employee Promotion]]
- [[Userflow/Auth-Access/access-policy|Management Coverage Reference]]
