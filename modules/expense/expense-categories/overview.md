# Expense Categories

**Module:** Expense  
**Feature:** Expense Categories

---

## Purpose

Defines expense categories with per-claim limits and receipt requirements.

## Database Tables

### `expense_categories`
Fields: `name`, `max_amount` (nullable), `requires_receipt`, `is_active`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/expenses/categories` | `expense:read` | List categories |

## Related

- [[expense|Expense Module]] — parent module
- [[expense-claims]] — claims that reference categories
- [[multi-tenancy]] — tenant-scoped category isolation
- [[auth-architecture]] — permission: `expense:manage`
- [[event-catalog]] — events emitted on category changes
- [[WEEK4-supporting-bridges]] — implementation task
