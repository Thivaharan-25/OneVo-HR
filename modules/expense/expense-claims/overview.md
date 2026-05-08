# Expense Claims

**Module:** Expense  
**Feature:** Expense Claims

---

## Purpose

Manages expense claim submission, approval workflow, and individual line items.

## Database Tables

### `expense_claims`
Fields: `employee_id`, `title`, `total_amount`, `currency_code`, `status` (`draft`, `submitted`, `approved`, `rejected`, `paid`).

### `expense_items`
Fields: `claim_id`, `category_id`, `description`, `amount`, `date`, `receipt_file_id`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/expenses/claims` | `expense:create` | Create claim |
| PUT | `/api/v1/expenses/claims/{id}` | `expense:create` | Update draft |
| POST | `/api/v1/expenses/claims/{id}/submit` | `expense:create` | Submit for approval |
| PUT | `/api/v1/expenses/claims/{id}/approve` | `expense:approve` | Approve |
| GET | `/api/v1/expenses/claims/me` | `expense:read` | Own claims |

## Related

- [[modules/expense/overview|Expense Module]] â€” parent module
- [[modules/expense/expense-categories/overview|Expense Categories]] â€” categories used in claim line items
- [[infrastructure/multi-tenancy|Multi Tenancy]] â€” tenant-scoped claim isolation
- [[security/auth-architecture|Auth Architecture]] â€” permissions: `expense:create`, `expense:approve`
- [[backend/messaging/event-catalog|Event Catalog]] â€” events emitted on claim status changes
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Supporting Bridges]] â€” implementation task

