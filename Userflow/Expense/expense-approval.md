# Expense Approval

**Area:** Expense  
**Required Permission(s):** `expense:approve`  
**Related Permissions:** `expense:manage` (override limits)

---

## Preconditions

- Expense claim submitted → [[expense-claim-submission]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Receive Notification
- **UI:** Notification: "Expense claim from [Employee] — $350 — awaiting approval"
- **API:** `GET /api/v1/expense/claims?status=pending&approver=me`

### Step 2: Review Claim
- **UI:** Expense → Pending Approvals → select claim → view items, amounts, receipts, policy compliance flags
- Check: amounts reasonable, receipts match, within policy limits

### Step 3: Approve or Reject
- **UI:** "Approve" (all items) or "Partial Approve" (approve some, reject others with reason) or "Reject" (with reason)
- **API:** `PUT /api/v1/expense/claims/{id}/approve`
- **Backend:** ExpenseService.ApproveAsync() → [[expense]]
- **DB:** `expense_claims` — status updated

### Step 4: Payroll Integration
- **Backend:** Approved amount added to next payroll run as reimbursement → [[payroll-run-execution]]
- Employee notified of decision

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Approving own claim | Blocked | "Cannot approve your own expense claim" |
| Already processed | Info | "This claim has already been processed" |

## Events Triggered

- `ExpenseClaimApproved` → [[event-catalog]]
- `ExpenseClaimRejected` → [[event-catalog]]
- Notification to employee → [[notification-system]]

## Related Flows

- [[expense-claim-submission]]
- [[payroll-run-execution]]

## Module References

- [[expense]]
- [[notification-system]]
