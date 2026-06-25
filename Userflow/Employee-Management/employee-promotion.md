# Employee Promotion

**Area:** Employee Management  
**Trigger:** Authorized user promotes an employee  
**Required Permission(s):** `employees:write` to start a promotion; `position:approve` with valid coverage to approve/apply a position-changing promotion

---

## Phase 1 Source of Truth

Promotion is a compact modal or compact flow. It is not a five-step wizard and it does not use Workflow Engine in Phase 1.

If a target position grants access, the UI shows deterministic **Role granted** and **Can manage employees in** values from the target position.

---

## Modal Fields

| Field | Required | Notes |
|:---|:---|:---|
| Target position / level | Yes | Target position drives reporting and position-derived access |
| Effective date | Yes | Today or future |
| Reason | Yes | Audit and approver context |
| Compensation impact | Conditional | Only if compensation is in scope for the tenant/actor |

---

## Access Impact

If target position changes, load:

- Role granted
- Can manage employees in
- Requires approval

If the promotion does not change position-based access, do not regenerate access.

If direct apply is allowed and approval is not required, the actor can apply directly. If the actor lacks valid authority or the position requires approval, submit an approval request and resolve one owner through management coverage.

Bypass depends on permissions and authority grants, not hard-coded role names.

Approval routing:

1. Position coverage owners in order: Primary owner, Backup owner 1, Backup owner 2, etc.
2. Department coverage owners in the same order.
3. Company-wide coverage owners in the same order.
4. Routing issue.

If no valid owner exists, create a routing issue with: "No eligible owner could approve this request. Check position coverage and permissions."

---

## Backend Flow

1. Validate employee is active.
2. Validate target position, capacity, and legal-entity boundary.
3. Resolve access impact from the target position.
4. Create/schedule promotion and assignment changes.
5. Apply access directly only when allowed.
6. Otherwise create `access_grant_requests`.
7. On effective date, update primary assignment if the promotion changes the employment position.

---

## Multi-Position Rule

Promotion inside the same legal entity changes the employee's Primary Employment Assignment. Do not create a parallel second employment assignment in the same legal entity.

Additional Authority Assignments can grant extra authority but do not change time_off, schedule, attendance, payroll, holiday calendar, or primary legal entity.

---

## Error Scenarios

| Scenario | User sees |
|:---|:---|
| Same target position | "Employee already holds this position." |
| Position capacity exceeded | "This position has reached its capacity." |
| Actor lacks authority | "Promotion can be submitted for approval." |
| Access approval required | "Access changes are pending approval." |

---

## Events Triggered

- `EmployeePromotionRequested`
- `EmployeePromoted`
- `AccessGrantRequested`
- Notification to the single owner resolved from management coverage

---

## Related

- [[Userflow/Org-Structure/position-setup|Position Setup]]
- [[Userflow/Employee-Management/employee-transfer|Employee Transfer]]
- [[Userflow/Auth-Access/access-policy|Management Coverage Reference]]
