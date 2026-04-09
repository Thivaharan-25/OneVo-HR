# Module: Expense

**Namespace:** `ONEVO.Modules.Expense`
**Phase:** 2 — Deferred
**Pillar:** Shared Foundation
**Owner:** Dev 2 (Week 4)
**Tables:** 3

> [!WARNING]
> **This module is deferred to Phase 2. Do not implement.** Expense claims and routing are not core to the employee monitoring product. Specs are preserved here for future reference.

---

## Purpose

Manages expense categories, claims, and individual line items. Uses the [[modules/shared-platform/overview|Shared Platform]] workflow engine for approval routing.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/core-hr/overview|Core Hr]] | `IEmployeeService` | Employee context |
| **Depends on** | [[modules/infrastructure/overview|Infrastructure]] | `IFileService` | Receipt uploads |
| **Depends on** | [[modules/shared-platform/overview|Shared Platform]] | Workflow engine | Approval routing |

---

## Database Tables (3)

### `expense_categories`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `name` | `varchar(100)` | e.g., "Travel", "Meals", "Equipment" |
| `max_amount` | `decimal(15,2)` | Per-claim limit (nullable) |
| `requires_receipt` | `boolean` | |
| `is_active` | `boolean` | |

### `expense_claims`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK → employees |
| `title` | `varchar(200)` | |
| `total_amount` | `decimal(15,2)` | Sum of items |
| `currency_code` | `varchar(3)` | |
| `status` | `varchar(20)` | `draft`, `submitted`, `approved`, `rejected`, `paid` |
| `submitted_at` | `timestamptz` | |
| `approved_by_id` | `uuid` | |
| `created_at` | `timestamptz` | |

### `expense_items`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `claim_id` | `uuid` | FK → expense_claims |
| `category_id` | `uuid` | FK → expense_categories |
| `description` | `varchar(255)` | |
| `amount` | `decimal(15,2)` | |
| `date` | `date` | Expense date |
| `receipt_file_id` | `uuid` | FK → file_records (nullable) |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/expenses/categories` | `expense:read` | List categories |
| POST | `/api/v1/expenses/claims` | `expense:create` | Create claim |
| PUT | `/api/v1/expenses/claims/{id}` | `expense:create` | Update draft claim |
| POST | `/api/v1/expenses/claims/{id}/submit` | `expense:create` | Submit for approval |
| PUT | `/api/v1/expenses/claims/{id}/approve` | `expense:approve` | Approve |
| GET | `/api/v1/expenses/claims/me` | `expense:read` | Own claims |

## Features

- [[modules/expense/expense-categories/overview|Expense Categories]] — Category definitions with per-claim limits and receipt requirements
- [[modules/expense/expense-claims/overview|Expense Claims]] — Claims with line items, approval workflow via [[modules/shared-platform/overview|Shared Platform]]

---

## Related

- [[infrastructure/multi-tenancy|Multi Tenancy]] — All expense data is tenant-scoped
- [[backend/messaging/error-handling|Error Handling]] — Workflow engine handles approval routing
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Supporting Bridges]] — Implementation task file

See also: [[backend/module-catalog|Module Catalog]], [[modules/core-hr/overview|Core Hr]], [[modules/shared-platform/overview|Shared Platform]]
