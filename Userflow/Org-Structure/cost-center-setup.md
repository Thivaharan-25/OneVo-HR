# Cost Center Setup

**Area:** Org Structure  
**Required Permission(s):** `org:manage`  
**Related Permissions:** `payroll:read` (view cost allocation)

---

## Preconditions

- Department(s) exist → [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Cost Centers
- **UI:** Sidebar → Organization → Cost Centers → click "Add Cost Center"
- **API:** `GET /api/v1/org/cost-centers`

### Step 2: Define Cost Center
- **UI:** Enter cost center code (e.g., "CC-ENG-001") → enter name → add description → set budget amount (optional)
- **Validation:** Code unique within tenant

### Step 3: Assign to Departments
- **UI:** Select one or more departments this cost center covers
- **API:** `POST /api/v1/org/cost-centers`
- **DB:** `cost_centers` — record created with department associations

### Step 4: Confirmation
- **UI:** Cost center available in payroll reports and expense allocation

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate code | Validation fails | "Cost center code already exists" |
| Delete with transactions | Blocked | "Cannot delete — cost center has payroll allocations" |

## Events Triggered

- `CostCenterCreated` → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- [[Userflow/Payroll/payroll-run-execution|Payroll Run Execution]]
- [[Userflow/Expense/expense-claim-submission|Expense Claim Submission]]

## Module References

- [[modules/org-structure/cost-centers/overview|Cost Centers]]
- [[modules/org-structure/overview|Org Structure]]
