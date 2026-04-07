# Expense Category Setup

**Area:** Expense  
**Required Permission(s):** `expense:manage`  
**Related Permissions:** `settings:admin` (global policy)

---

## Preconditions

- Tenant provisioned → [[tenant-provisioning]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Create Category
- **UI:** Expense → Categories → "Create Category" → enter: name (Travel, Meals, Accommodation, Equipment, Training, Other)
- **API:** `POST /api/v1/expense/categories`

### Step 2: Configure Limits
- **UI:** Set per-item limit (max per single expense) → set monthly limit per employee → set receipt required (yes/no) → set auto-approval threshold (claims below this amount auto-approved)
- **Backend:** ExpenseCategoryService.CreateAsync() → [[expense-categories]]
- **DB:** `expense_categories`

### Step 3: Save
- **Result:** Category available when employees submit claims → limits enforced at submission time

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate name | Validation fails | "Category already exists" |
| Delete with claims | Blocked | "Cannot delete — category has existing claims" |

## Events Triggered

- `ExpenseCategoryCreated` → [[event-catalog]]

## Related Flows

- [[expense-claim-submission]]
- [[expense-approval]]

## Module References

- [[expense-categories]]
- [[expense]]
