# Grievance — Schema

**Module:** [[modules/grievance/overview|Grievance]]
**Phase:** Phase 2
**Tables:** 2

---

## `disciplinary_actions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `employee_id` | `uuid` | FK → employees |
| `grievance_id` | `uuid` | FK → grievance_cases (nullable) |
| `action_type` | `varchar(30)` | `verbal_warning`, `written_warning`, `suspension`, `termination` |
| `description` | `text` |  |
| `effective_date` | `date` |  |
| `issued_by_id` | `uuid` | FK → users |
| `acknowledged_at` | `timestamptz` | Employee acknowledgement |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `grievance_id` → [[#`grievance_cases`|grievance_cases]], `issued_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `grievance_cases`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `filed_by_id` | `uuid` | FK → employees (nullable if anonymous) |
| `against_id` | `uuid` | FK → employees (nullable) |
| `category` | `varchar(30)` | `harassment`, `discrimination`, `safety`, `policy_violation`, `other` |
| `description` | `text` |  |
| `severity` | `varchar(20)` | `low`, `medium`, `high`, `critical` |
| `status` | `varchar(20)` | `filed`, `investigating`, `resolved`, `dismissed`, `escalated` |
| `resolution` | `text` |  |
| `resolved_by_id` | `uuid` | FK → users |
| `resolved_at` | `timestamptz` |  |
| `is_anonymous` | `boolean` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `filed_by_id` → [[database/schemas/core-hr#`employees`|employees]], `against_id` → [[database/schemas/core-hr#`employees`|employees]], `resolved_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## Related

- [[modules/grievance/overview|Grievance Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]