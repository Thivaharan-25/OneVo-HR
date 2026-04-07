# Cost Center Setup

**Area:** Org Structure  
**Required Permission(s):** `org:manage`  
**Related Permissions:** `payroll:read` (view cost allocation)

---

## Preconditions

- Department(s) exist → [[department-hierarchy]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

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

- `CostCenterCreated` → [[event-catalog]]

## Related Flows

- [[department-hierarchy]]
- [[payroll-run-execution]]
- [[expense-claim-submission]]

## Module References

- [[cost-centers]]
- [[org-structure]]
