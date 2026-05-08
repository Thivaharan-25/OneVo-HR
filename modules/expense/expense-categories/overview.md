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

- [[modules/expense/overview|Expense Module]] â€” parent module
- [[modules/expense/expense-claims/overview|Expense Claims]] â€” claims that reference categories
- [[infrastructure/multi-tenancy|Multi Tenancy]] â€” tenant-scoped category isolation
- [[security/auth-architecture|Auth Architecture]] â€” permission: `expense:manage`
- [[backend/messaging/event-catalog|Event Catalog]] â€” events emitted on category changes
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Supporting Bridges]] â€” implementation task

