# Expense — Schema

**Module:** [[modules/expense/overview|Expense]]
**Phase:** Phase 2
**Tables:** 3

---

## `expense_categories`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `name` | `varchar(100)` | e.g., "Travel", "Meals", "Equipment" |
| `max_amount` | `decimal(15,2)` | Per-claim limit (nullable) |
| `requires_receipt` | `boolean` |  |
| `is_active` | `boolean` |  |

---

## `expense_claims`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `employee_id` | `uuid` | FK → employees |
| `title` | `varchar(200)` |  |
| `total_amount` | `decimal(15,2)` | Sum of items |
| `currency_code` | `varchar(3)` |  |
| `status` | `varchar(20)` | `draft`, `submitted`, `approved`, `rejected`, `paid` |
| `submitted_at` | `timestamptz` |  |
| `approved_by_id` | `uuid` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `employee_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## `expense_items`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `claim_id` | `uuid` | FK → expense_claims |
| `category_id` | `uuid` | FK → expense_categories |
| `description` | `varchar(255)` |  |
| `amount` | `decimal(15,2)` |  |
| `date` | `date` | Expense date |
| `receipt_file_id` | `uuid` | FK → file_records (nullable) |

**Foreign Keys:** `claim_id` → [[#`expense_claims`|expense_claims]], `category_id` → [[#`expense_categories`|expense_categories]], `receipt_file_id` → [[database/schemas/infrastructure#`file_records`|file_records]]

---

## Related

- [[modules/expense/overview|Expense Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]