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

- [[expense|Expense Module]] — parent module
- [[expense-categories]] — categories used in claim line items
- [[multi-tenancy]] — tenant-scoped claim isolation
- [[auth-architecture]] — permissions: `expense:create`, `expense:approve`
- [[event-catalog]] — events emitted on claim status changes
- [[WEEK4-supporting-bridges]] — implementation task
