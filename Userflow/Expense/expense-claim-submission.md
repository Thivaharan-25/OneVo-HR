# Expense Claim Submission

**Area:** Expense  
**Trigger:** Employee submits expense claim with receipts (user action)
**Required Permission(s):** `expense:create`  
**Related Permissions:** `documents:write` (upload receipts)

---

## Preconditions

- Expense categories configured → [[Userflow/Expense/expense-category-setup|Expense Category Setup]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Create Claim
- **UI:** Sidebar → Expense → "New Claim" → enter claim title (e.g., "Business Trip - March 2026")
- **API:** `POST /api/v1/expense/claims`

### Step 2: Add Items
- **UI:** "Add Item" → select category (Travel, Meals, Accommodation, Equipment) → enter amount, date, description → upload receipt image/PDF → repeat for multiple items
- **Validation:** Receipt required if category requires it, amount within category limit

### Step 3: Review & Submit
- **UI:** Review all items → see total amount → submit for approval
- **API:** `POST /api/v1/expense/claims/{id}/submit`
- **Backend:** ExpenseService.SubmitAsync() → [[modules/expense/overview|Expense]]
- **DB:** `expense_claims` — status: "Pending", `expense_items` — individual line items

### Step 4: Track Status
- **UI:** Expense → My Claims → see status (Pending, Approved, Rejected, Paid)

## Variations

### Auto-approval
- If total below threshold (configured per category) → auto-approved without manager review

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Exceeds category limit | Blocked | "Amount exceeds limit for Travel (max $500)" |
| Missing receipt | Cannot submit | "Receipt required for Meals items" |
| Duplicate date+category | Warning | "You already have a Meals claim for March 15" |

## Events Triggered

- `ExpenseClaimSubmitted` → [[backend/messaging/event-catalog|Event Catalog]]
- Notification to approver → [[backend/notification-system|Notification System]]

## Related Flows

- [[Userflow/Expense/expense-approval|Expense Approval]]
- [[Userflow/Expense/expense-category-setup|Expense Category Setup]]
- [[Userflow/Payroll/payroll-run-execution|Payroll Run Execution]] (reimbursement)

## Module References

- [[modules/expense/overview|Expense]]
- [[modules/expense/expense-categories/overview|Expense Categories]]
