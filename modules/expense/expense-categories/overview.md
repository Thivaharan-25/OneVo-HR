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

- [[modules/expense/overview|Expense Module]] — parent module
- [[modules/expense/expense-claims/overview|Expense Claims]] — claims that reference categories
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant-scoped category isolation
- [[security/auth-architecture|Auth Architecture]] — permission: `expense:manage`
- [[backend/messaging/event-catalog|Event Catalog]] — events emitted on category changes
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Supporting Bridges]] — implementation task
